import csv
import json
from pathlib import Path


INPUT_PATH = Path(
    "data/manifests/borealam_micro_pilot_v1.jsonl"
)

OUTPUT_PATH = Path(
    "data/reviews/borealam_micro_review_v1.csv"
)

def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records

REVIEW_FIELDS = [
    "openalex_id",
    "title",
    "year",
    "primary_theme",
    "lpbf_role",
    "quality_score",
    "selection_reason",
    "doi",
    "license",
    "pdf_url",
    "abstract_preview",
    "review_decision",
    "review_notes",
]

def create_review_sheet(records, output_path):

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if output_path.exists():
        raise FileExistsError(
            f"Review sheet already exists: {output_path}"
        )

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=REVIEW_FIELDS,
        )

        writer.writeheader()

        for record in records:

            writer.writerow({
                "openalex_id": record.get("openalex_id"),
                "title": record.get("title"),
                "year": record.get("year"),
                "primary_theme": record.get("boreal_primary_theme"),
                "lpbf_role": record.get("lpbf_role"),
                "quality_score": record.get("quality_score"),
                "selection_reason": record.get("pilot_selection_reason"),
                "doi": record.get("doi"),
                "license": record.get("license"),
                "pdf_url": record.get("pdf_url"),
                "abstract_preview": (
                    record.get("abstract") or ""
                )[:1000],
                "review_decision": "",
                "review_notes": "",
            })

def main():
    records = load_records(INPUT_PATH)

    assert len(records) == 39

    create_review_sheet(
        records,
        OUTPUT_PATH,
    )

    print("Total review candidates:", len(records))
    print("Review sheet saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()