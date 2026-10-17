
import os
import re
import json
import hashlib
import requests
import xml.etree.ElementTree as ET

from pathlib import Path
from datetime import datetime, timezone


MANIFEST_PATH = Path(
    "data/manifests/borealam_micro_acquisition_v1.jsonl"
)

XML_DIR = Path("data/raw/xml")
PROVENANCE_DIR = Path("data/provenance/xml")

REPORT_PATH = Path(
    "data/reviews/pilot_xml_download_status.jsonl"
)

MAX_XML_BYTES = 25 * 1024 * 1024
MAX_NEW_DOWNLOADS = None


def validate_xml(data):
    root = ET.fromstring(data)

    has_tei = any(
        element.tag.split("}")[-1].lower() == "tei"
        for element in root.iter()
    )

    if not has_tei:
        raise ValueError("No TEI element found.")


def download_xml(paper, session):
    work_id = paper["openalex_id"].split("/")[-1]

    if not re.fullmatch(r"W\d+", work_id):
        raise ValueError("Invalid OpenAlex work ID.")

    output_path = XML_DIR / f"{work_id}.tei.xml"

    url = (
        f"https://content.openalex.org/works/"
        f"{work_id}.grobid-xml"
    )

    if output_path.exists():
        data = output_path.read_bytes()

        if len(data) > MAX_XML_BYTES:
            raise ValueError("Existing XML exceeds size limit.")

        validate_xml(data)

        return {
            "work_id": work_id,
            "status": "already_exists",
        }

    temporary_path = output_path.with_suffix(".xml.part")

    try:
        with session.get(
            url,
            stream=True,
            timeout=(15, 60),
        ) as response:

            if response.status_code == 404:
                return {
                    "work_id": work_id,
                    "status": "unavailable",
                }

            if response.status_code in (401, 403, 429):
                return {
                    "work_id": work_id,
                    "status": "stop",
                    "http_status": response.status_code,
                }

            response.raise_for_status()

            data = bytearray()

            for chunk in response.iter_content(65536):
                if not chunk:
                    continue

                data.extend(chunk)

                if len(data) > MAX_XML_BYTES:
                    raise ValueError("XML exceeds size limit.")

        validate_xml(data)

        temporary_path.write_bytes(data)
        temporary_path.replace(output_path)

        checksum = hashlib.sha256(data).hexdigest()

        provenance = {
            "work_id": work_id,
            "source_url": url,
            "metadata_license": paper.get("license"),
            "license_verified": False,
            "sha256": checksum,
            "size_bytes": len(data),
            "downloaded_at_utc": (
                datetime.now(timezone.utc).isoformat()
            ),
        }

        provenance_path = (
            PROVENANCE_DIR / f"{work_id}.json"
        )

        if provenance_path.exists():
            raise FileExistsError(
                f"Provenance already exists: {provenance_path}"
            )

        provenance_path.write_text(
            json.dumps(provenance, indent=2),
            encoding="utf-8",
        )

        return {
            "work_id": work_id,
            "status": "downloaded",
            "size_bytes": len(data),
        }

    finally:
        temporary_path.unlink(missing_ok=True)


def main():
    api_key = os.getenv("OPENALEX_API_KEY")

    if not api_key:
        raise RuntimeError("OPENALEX_API_KEY is not set.")

    papers = [
        json.loads(line)
        for line in MANIFEST_PATH.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    XML_DIR.mkdir(parents=True, exist_ok=True)
    PROVENANCE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    results = []
    attempted_new = 0

    with requests.Session() as session:
        session.headers.update({
            "Authorization": f"Bearer {api_key}"
        })

        for paper in papers:

            work_id = paper["openalex_id"].split("/")[-1]
            existing = XML_DIR / f"{work_id}.tei.xml"

            if (
                not existing.exists()
                and MAX_NEW_DOWNLOADS is not None
                and attempted_new >= MAX_NEW_DOWNLOADS
            ):
                break

            if paper.get("license", "").lower() != "cc-by":
                result = {
                    "work_id": work_id,
                    "status": "license_review_required",
                }
            else:
                if not existing.exists():
                    attempted_new += 1

                try:
                    result = download_xml(paper, session)

                except Exception as error:
                    result = {
                        "work_id": work_id,
                        "status": "error",
                        "error": str(error),
                    }

            results.append(result)

            print(
                f"[{result['status'].upper()}] {work_id}"
            )

            if result["status"] == "stop":
                print("Stopping: check API authentication or quota.")
                break

    REPORT_PATH.write_text(
        "".join(
            json.dumps(item) + "\n"
            for item in results
        ),
        encoding="utf-8",
    )

    print("\nPILOT XML ACQUISITION")
    print("=" * 50)
    print("Manifest papers:", len(papers))
    print("Checked this run:", len(results))
    print(
        "New downloads:",
        sum(r["status"] == "downloaded" for r in results),
    )
    print(
        "Unavailable:",
        sum(r["status"] == "unavailable" for r in results),
    )
    print(
        "Errors:",
        sum(r["status"] == "error" for r in results),
    )
    print("Status report:", REPORT_PATH)


if __name__ == "__main__":
    main()
