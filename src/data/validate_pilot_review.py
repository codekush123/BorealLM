import csv
import json
from collections import Counter


PILOT_PATH = (
    "data/manifests/borealam_micro_pilot_v1.jsonl"
)

REVIEW_PATH = (
    "data/reviews/borealam_micro_review_v1.csv"
)

VALID_DECISIONS = {
    "APPROVE",
    "REPLACE",
    "REVIEW",
}

def load_pilot_ids(path):
    ids = set()

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                record = json.loads(line)
                ids.add(record["openalex_id"])

    return ids


def load_review(path):
    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def validate_review(rows, pilot_ids):
    errors = []
    decision_counts = Counter()

    review_ids = [
        row["openalex_id"]
        for row in rows
    ]

    if len(rows) != 39:
        errors.append(
            f"Expected 39 rows, found {len(rows)}"
        )

    if len(set(review_ids)) != len(review_ids):
        errors.append("Duplicate OpenAlex IDs in review")

    if set(review_ids) != pilot_ids:
        errors.append(
            "Review IDs do not match the pilot manifest"
        )

    for row in rows:
        decision = (
            row["review_decision"].strip().upper()
        )

        notes = (
            row["review_notes"].strip()
        )

        if decision not in VALID_DECISIONS:
            errors.append(
                f"Invalid decision for {row['openalex_id']}"
            )
            continue

        decision_counts[decision] += 1

        if decision in {"REPLACE", "REVIEW"} and not notes:
            errors.append(
                f"Missing review notes for {row['openalex_id']}"
            )

    return decision_counts, errors

def main():
    pilot_ids = load_pilot_ids(PILOT_PATH)
    rows = load_review(REVIEW_PATH)

    counts, errors = validate_review(
        rows,
        pilot_ids,
    )

    print("=" * 60)
    print("BOREALAM-MICRO REVIEW VALIDATION")
    print("=" * 60)

    print("Total reviewed:", len(rows))
    print("Approved:", counts["APPROVE"])
    print("Replace:", counts["REPLACE"])
    print("Needs review:", counts["REVIEW"])

    print("\nFlagged papers:")

    for row in rows:
        decision = (
            row["review_decision"].strip().upper()
        )

        if decision in {"REPLACE", "REVIEW"}:
            print()
            print("Decision:", decision)
            print("Title:", row["title"])
            print("Theme:", row["primary_theme"])
            print("Reason:", row["review_notes"])

    print("\nValidation errors:", len(errors))

    for error in errors:
        print("ERROR:", error)

    if errors:
        raise SystemExit("Review validation failed.")

    print("\nReview file is structurally valid.")


if __name__ == "__main__":
    main()