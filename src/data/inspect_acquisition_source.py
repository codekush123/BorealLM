import json
from pathlib import Path


MANIFEST_PATH = Path(
    "data/manifests/borealam_micro_acquisition_v1.jsonl"
)


def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records

def inspect_paper(record):
    print("=" * 70)
    print("BOREALAM SINGLE-PAPER ACQUISITION TEST")
    print("=" * 70)

    print("Title:", record.get("title"))
    print("OpenAlex ID:", record.get("openalex_id"))
    print("DOI:", record.get("doi"))
    print("Year:", record.get("year"))

    print("\nSOURCE INFORMATION")
    print("Journal:", record.get("journal"))
    print("License:", record.get("license"))
    print("Version:", record.get("version"))

    print("\nFULL-TEXT LOCATIONS")
    print("Landing page:", record.get("landing_page_url"))
    print("PDF URL:", record.get("pdf_url"))
    print("OpenAlex PDF:", record.get("openalex_pdf_url"))
    print("GROBID XML:", record.get("grobid_xml_url"))

def main():
    records = load_records(MANIFEST_PATH)

    if len(records) != 39:
        raise ValueError(
            f"Expected 39 papers, found {len(records)}"
        )

    first_paper = records[0]

    inspect_paper(first_paper)


if __name__ == "__main__":
    main()