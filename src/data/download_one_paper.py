import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import requests
MANIFEST_PATH = Path(
    "data/manifests/borealam_micro_acquisition_v1.jsonl"
)

PDF_DIR = Path("data/raw/pdf")

PROVENANCE_DIR = Path("data/provenance")

TARGET_ID = "https://openalex.org/W2942539847"

MAX_PDF_BYTES = 50 * 1024 * 1024

def download_pdf(paper):

    pdf_url = paper["pdf_url"]

    paper_id = paper["openalex_id"].split("/")[-1]

    PDF_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    pdf_path = PDF_DIR / f"{paper_id}.pdf"

    temporary_path = PDF_DIR / f"{paper_id}.pdf.part"

    if pdf_path.exists():
        raise FileExistsError(
            f"PDF already exists: {pdf_path}"
        )

    sha256 = hashlib.sha256()
    total_bytes = 0

    try:
        with requests.get(
            pdf_url,
            stream=True,
            timeout=(15, 60),
        ) as response:

            response.raise_for_status()

            with open(temporary_path, "wb") as file:

                for chunk in response.iter_content(
                    chunk_size=65536
                ):

                    if not chunk:
                        continue

                    total_bytes += len(chunk)

                    if total_bytes > MAX_PDF_BYTES:
                        raise ValueError(
                            "PDF exceeds 50 MiB limit."
                        )

                    sha256.update(chunk)

                    file.write(chunk)

        with open(temporary_path, "rb") as file:
            signature = file.read(5)

        if signature != b"%PDF-":
            raise ValueError(
                "Downloaded content is not a PDF."
            )

        temporary_path.rename(pdf_path)

    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    return (
        pdf_path,
        total_bytes,
        sha256.hexdigest(),
    )

def find_paper(path, target_id):

    with open(path, "r", encoding="utf-8") as file:

        for line in file:

            if not line.strip():
                continue

            record = json.loads(line)

            if record.get("openalex_id") == target_id:
                return record

    raise ValueError(
        f"Paper not found: {target_id}"
    )

def save_provenance(paper, pdf_path, size, checksum):

    PROVENANCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    paper_id = paper["openalex_id"].split("/")[-1]

    provenance_path = (
        PROVENANCE_DIR / f"{paper_id}.json"
    )

    if provenance_path.exists():
        raise FileExistsError(
            f"Provenance already exists: {provenance_path}"
        )

    provenance = {
        "openalex_id": paper["openalex_id"],
        "title": paper["title"],
        "doi": paper.get("doi"),
        "authors": paper.get("authors"),
        "year": paper.get("year"),
        "journal": paper.get("journal"),

        "source_url": paper["pdf_url"],

        "publisher_page": (
            "https://www.nature.com/articles/"
            "s41467-019-10009-2"
        ),

        "license_openalex": paper.get("license"),
        "verified_license": "CC-BY-4.0",
        "license_url": (
            "https://creativecommons.org/licenses/by/4.0/"
        ),

        "version": paper.get("version"),

        "local_file": str(pdf_path),
        "file_size_bytes": size,
        "sha256": checksum,

        "provenance_recorded_at_utc": (
            datetime.now(timezone.utc).isoformat()
        ),
    }

    with open(
        provenance_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            provenance,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return provenance_path

def inspect_existing_pdf(pdf_path):

    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)

    sha256 = hashlib.sha256()

    with open(pdf_path, "rb") as file:

        if file.read(5) != b"%PDF-":
            raise ValueError("Invalid PDF header.")

        file.seek(0)

        while True:
            chunk = file.read(65536)

            if not chunk:
                break

            sha256.update(chunk)

    size = pdf_path.stat().st_size

    return size, sha256.hexdigest()

def main():

    paper = find_paper(
        MANIFEST_PATH,
        TARGET_ID,
    )

    paper_id = TARGET_ID.split("/")[-1]

    pdf_path = PDF_DIR / f"{paper_id}.pdf"

    print("Inspecting existing PDF...")

    size, checksum = inspect_existing_pdf(
        pdf_path
    )

    provenance_path = save_provenance(
        paper,
        pdf_path,
        size,
        checksum,
    )

    print("\nPROVENANCE SAVED SUCCESSFULLY")
    print("Paper:", paper["title"])
    print("PDF:", pdf_path)
    print("Size:", size, "bytes")
    print("SHA-256:", checksum)
    print("Provenance:", provenance_path)


if __name__ == "__main__":
    main()