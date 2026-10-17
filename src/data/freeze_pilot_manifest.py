import csv
import json
from pathlib import Path
from collections import Counter


PILOT_PATH = Path(
    "src/data/manifests/borealam_micro_pilot_v1.jsonl"
)

CANDIDATE_PATH = Path(
    "src/data/manifests/lpbf_included_themed.jsonl"
)

REVIEW_PATH = Path(
    "src/data/reviews/borealam_micro_review_v1.csv"
)

REPLACEMENT_PATH = Path(
    "src/data/reviews/borealam_micro_replacements_v1.csv"
)

OUTPUT_PATH = Path(
    "src/data/manifests/borealam_micro_acquisition_v1.jsonl"
)
def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def load_csv(path):
    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def get_approved_originals(pilot, reviews):

    pilot_by_id = {
        record["openalex_id"]: record
        for record in pilot
    }

    approved = []
    replaced_ids = set()

    for row in reviews:
        openalex_id = row["openalex_id"].strip()
        decision = row["review_decision"].strip().upper()

        if openalex_id not in pilot_by_id:
            raise ValueError(
                f"Unknown pilot ID: {openalex_id}"
            )

        if decision == "REVIEW":
            raise ValueError(
                f"Unresolved review: {openalex_id}"
            )

        if decision == "APPROVE":
            record = pilot_by_id[openalex_id].copy()

            record["pilot_review_status"] = "approved_original"
            record["pilot_review_notes"] = row["review_notes"]

            approved.append(record)

        elif decision == "REPLACE":
            replaced_ids.add(openalex_id)

        else:
            raise ValueError(
                f"Invalid decision: {decision}"
            )

    return approved, replaced_ids

def get_approved_replacements(
    candidates,
    replacement_rows,
    replaced_ids,
):

    candidates_by_id = {
        record["openalex_id"]: record
        for record in candidates
    }

    replacements = []
    handled_ids = set()

    for row in replacement_rows:
        original_id = row["original_openalex_id"].strip()
        replacement_id = row["replacement_openalex_id"].strip()
        decision = row["replacement_decision"].strip().upper()

        if original_id not in replaced_ids:
            raise ValueError(
                f"Unexpected replacement for: {original_id}"
            )

        if original_id in handled_ids:
            raise ValueError(
                f"Multiple proposals for: {original_id}"
            )

        if decision != "APPROVE":
            raise ValueError(
                f"Replacement not approved: {replacement_id}"
            )

        if replacement_id not in candidates_by_id:
            raise ValueError(
                f"Replacement not in candidate pool: {replacement_id}"
            )

        record = candidates_by_id[replacement_id].copy()

        if record["boreal_primary_theme"] != row["primary_theme"]:
            raise ValueError(
                f"Theme mismatch for: {replacement_id}"
            )

        record["pilot_review_status"] = "approved_replacement"
        record["replaces_openalex_id"] = original_id
        record["pilot_review_notes"] = row["replacement_notes"]
        record["pilot_selection_reason"] = row["selection_reason"]

        replacements.append(record)
        handled_ids.add(original_id)

    if handled_ids != replaced_ids:
        raise ValueError(
            "Some rejected originals have no approved replacement."
        )

    return replacements

def validate_final_manifest(records, original_count):

    if len(records) != original_count:
        raise ValueError(
            f"Expected {original_count} papers, found {len(records)}"
        )

    ids = [record["openalex_id"] for record in records]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate OpenAlex IDs found")

    theme_counts = Counter(
        record["boreal_primary_theme"]
        for record in records
    )

    if len(theme_counts) != 13:
        raise ValueError("Incorrect number of technical themes")

    for theme, count in theme_counts.items():
        if count != 3:
            raise ValueError(
                f"Theme {theme} has {count} papers instead of 3"
            )

    for record in records:
        if record.get("license") != "cc-by":
            raise ValueError(
                f"License requires review: {record['openalex_id']}"
            )

        if not record.get("pdf_url"):
            raise ValueError(
                f"Missing PDF URL: {record['openalex_id']}"
            )

def save_jsonl(records, path):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if path.exists():
        raise FileExistsError(
            f"Frozen manifest already exists: {path}"
        )

    with open(path, "w", encoding="utf-8") as file:
        for record in records:
            file.write(
                json.dumps(record, ensure_ascii=False)
                + "\n"
            )

def main():

    pilot = load_jsonl(PILOT_PATH)
    candidates = load_jsonl(CANDIDATE_PATH)
    reviews = load_csv(REVIEW_PATH)
    replacement_rows = load_csv(REPLACEMENT_PATH)

    if len(pilot) != 39 or len(reviews) != 39:
        raise ValueError("Expected 39 pilot and review records")

    pilot_ids = {record["openalex_id"] for record in pilot}
    review_ids = [row["openalex_id"].strip() for row in reviews]

    if len(set(review_ids)) != 39 or set(review_ids) != pilot_ids:
        raise ValueError("Pilot and review IDs do not match")

    originals, replaced_ids = get_approved_originals(
        pilot,
        reviews,
    )

    replacements = get_approved_replacements(
        candidates,
        replacement_rows,
        replaced_ids,
    )

    final_records = originals + replacements

    final_records.sort(
        key=lambda record: (
            record["boreal_primary_theme"],
            record.get("year") or 0,
            record["openalex_id"],
        )
    )

    validate_final_manifest(
        final_records,
        original_count=len(pilot),
    )

    print("=" * 60)
    print("BOREALAM-MICRO FINAL ACQUISITION MANIFEST")
    print("=" * 60)

    print("Approved original papers:", len(originals))
    print("Approved replacements:", len(replacements))
    print("Total final papers:", len(final_records))

    counts = Counter(
        record["boreal_primary_theme"]
        for record in final_records
    )

    print("\nTechnical theme distribution:")

    for theme, count in sorted(counts.items()):
        print(f"{theme:28s}: {count}")

    save_jsonl(
        final_records,
        OUTPUT_PATH,
    )

    print("\nManifest frozen at:", OUTPUT_PATH)


if __name__ == "__main__":
    main()