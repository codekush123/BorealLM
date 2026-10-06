import json
from collections import Counter


INPUT_PATH = (
    "src/data/manifests/"
    "lpbf_candidates_role_classified.jsonl"
)

DECISION_OUTPUT_PATH = (
    "src/data/manifests/"
    "lpbf_corpus_decisions.jsonl"
)

INCLUDED_OUTPUT_PATH = (
    "src/data/manifests/"
    "lpbf_included.jsonl"
)

INCLUDED_ROLES = {
    "core_lpbf",
    "lpbf_application",
}

def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    return records

def assign_corpus_decision(record):
    role = record.get("lpbf_role")

    if role in INCLUDED_ROLES:
        record["corpus_decision"] = "include"
        record["exclusion_reason"] = None

    else:
        record["corpus_decision"] = "exclude"
        record["exclusion_reason"] = "peripheral_lpbf"

    return record

def assign_decisions(records):
    decided_records = []

    for record in records:
        decided_record = assign_corpus_decision(record)

        decided_records.append(decided_record)

    return decided_records

def get_included_records(records):
    return [
        record
        for record in records
        if record.get("corpus_decision") == "include"
    ]

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

    decided_records = assign_decisions(records)

    included_records = get_included_records(
        decided_records
    )

    decision_counts = Counter(
        record["corpus_decision"]
        for record in decided_records
    )

    print("=" * 60)
    print("BOREALAM CORPUS INCLUSION")
    print("=" * 60)

    print("Total candidates:", len(decided_records))
    print("Included:", decision_counts["include"])
    print("Excluded:", decision_counts["exclude"])

    save_records(
        decided_records,
        DECISION_OUTPUT_PATH,
    )

    save_records(
        included_records,
        INCLUDED_OUTPUT_PATH,
    )

    print()
    print("Decision manifest:")
    print(DECISION_OUTPUT_PATH)

    print()
    print("Included manifest:")
    print(INCLUDED_OUTPUT_PATH)


if __name__ == "__main__":
    main()