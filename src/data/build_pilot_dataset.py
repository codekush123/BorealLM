import json
import hashlib

from pathlib import Path

from extract_grobid_text import extract_article


MANIFEST_PATH = Path(
    "data/manifests/borealam_micro_acquisition_v1.jsonl"
)

XML_DIR = Path("data/raw/xml")

OUTPUT_PATH = Path(
    "data/processed/pilot/borealam_pilot_extracted_v1.jsonl"
)

def load_manifest(path):

    papers = []

    with path.open("r", encoding="utf-8") as file:

        for line in file:

            if not line.strip():
                continue

            papers.append(json.loads(line))

    return papers

def build_dataset(papers):

    records = []
    missing_xml = []
    failed = []

    for paper in papers:

        work_id = paper["openalex_id"].split("/")[-1]

        xml_path = XML_DIR / f"{work_id}.tei.xml"

        if not xml_path.is_file():
            missing_xml.append(work_id)
            continue

        try:

            (
                body_text,
                figure_text,
                heading_count,
                paragraph_count,
                figure_count,
            ) = extract_article(xml_path)

            if not body_text.strip():
                raise ValueError("Empty article text")

            xml_checksum = hashlib.sha256(
                xml_path.read_bytes()
            ).hexdigest()

            record = {
                "work_id": work_id,
                "openalex_id": paper["openalex_id"],
                "doi": paper.get("doi"),
                "title": paper.get("title"),
                "year": paper.get("year"),
                "primary_theme": paper.get("primary_theme"),

                "source_xml": str(xml_path),
                "source_xml_sha256": xml_checksum,

                "body_text": body_text,
                "figure_text": figure_text,

                "heading_count": heading_count,
                "paragraph_count": paragraph_count,
                "figure_count": figure_count,

                "extraction_method": "grobid_tei_v1",
                "quality_status": "unreviewed",
            }

            records.append(record)

            print(f"[OK] {work_id}")

        except Exception as error:

            failed.append(work_id)
            print(f"[ERROR] {work_id}: {error}")

    return records, missing_xml, failed

def save_dataset(records, output_path):

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                ) + "\n"
            )

def main():

    papers = load_manifest(MANIFEST_PATH)

    print("BorealAM Pilot Dataset Builder")
    print("=" * 50)

    print("Manifest papers:", len(papers))

    if len(papers) != 39:
        raise ValueError(
            f"Expected 39 pilot papers, found {len(papers)}"
        )

    records, missing_xml, failed = build_dataset(papers)

    save_dataset(records, OUTPUT_PATH)

    print("\nBATCH EXTRACTION REPORT")
    print("=" * 50)

    print("Total candidates:", len(papers))
    print("Successfully extracted:", len(records))
    print("Missing XML:", len(missing_xml))
    print("Failed extractions:", len(failed))

    print("\nDataset:", OUTPUT_PATH)

    if missing_xml:
        print("\nMissing XML work IDs:")
        for work_id in missing_xml:
            print(" ", work_id)


if __name__ == "__main__":
    main()