import json

CANONICAL_MAP = {
    "https://openalex.org/W2995063234":
        "https://openalex.org/W4241591685",

    "https://openalex.org/W7118374631":
        "https://openalex.org/W7117484271",

    "https://openalex.org/W4294560239":
        "https://openalex.org/W3217390568",

    "https://openalex.org/W7128618997":
        "https://openalex.org/W7125923664",
}

INPUT_PATH = (
    "src/data/manifests/"
    "lpbf_candidates_dedup_exact.jsonl"
)

OUTPUT_PATH = (
    "src/data/manifests/"
    "lpbf_candidates_canonical.jsonl"
)

def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    return records

def resolve_duplicate_versions(records):
    records_by_id = {
        record["openalex_id"]: record
        for record in records
    }

    removed_ids = set()

    for duplicate_id, canonical_id in CANONICAL_MAP.items():

        duplicate = records_by_id.get(duplicate_id)
        canonical = records_by_id.get(canonical_id)

        if duplicate is None:
            print(
                "Duplicate record not found:",
                duplicate_id
            )
            continue

        if canonical is None:
            print(
                "Canonical record not found:",
                canonical_id
            )
            continue

        alternate = {
            "openalex_id": duplicate.get("openalex_id"),
            "doi": duplicate.get("doi"),
            "journal": duplicate.get("journal"),
            "year": duplicate.get("year"),
            "pdf_url": duplicate.get("pdf_url"),
            "landing_page_url":
                duplicate.get("landing_page_url"),
        }

        if "alternate_versions" not in canonical:
            canonical["alternate_versions"] = []

        canonical["alternate_versions"].append(
            alternate
        )

        removed_ids.add(duplicate_id)

    resolved_records = [
        record
        for record in records
        if record["openalex_id"] not in removed_ids
    ]

    return resolved_records

def save_record(records, path):
    with open(path, "w", encoding="utf-8") as file:

        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

def main():
    records = load_records(INPUT_PATH)

    resolved_records = resolve_duplicate_versions(
        records
    )

    removed = len(records) - len(resolved_records)

    print("Before resolution:", len(records))
    print("After resolution:", len(resolved_records))
    print("Alternative versions merged:", removed)

    save_record(
        resolved_records,
        OUTPUT_PATH,
    )

    print("\nSaved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()