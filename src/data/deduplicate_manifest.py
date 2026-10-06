import json


INPUT_PATH = "src/data/manifests/lpbf_candidates.jsonl"
OUTPUT_PATH = "src/data/manifests/lpbf_candidates_dedup_exact.jsonl"


def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    return records


def remove_exact_duplicates(records):
    unique_records = []
    seen_openalex_ids = set()

    for record in records:
        openalex_id = record.get("openalex_id")

        if openalex_id in seen_openalex_ids:
            continue

        seen_openalex_ids.add(openalex_id)
        unique_records.append(record)

    return unique_records


def save_records(records, path):
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

    deduplicated_records = remove_exact_duplicates(records)

    removed = len(records) - len(deduplicated_records)

    print("Original records:", len(records))
    print("Unique records:", len(deduplicated_records))
    print("Exact duplicates removed:", removed)

    save_records(
        deduplicated_records,
        OUTPUT_PATH,
    )

    print("Saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()