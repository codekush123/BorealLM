import csv
import json
from pathlib import Path
from collections import Counter


PILOT_PATH = Path(
    "data/manifests/borealam_micro_pilot_v1.jsonl"
)

CANDIDATE_PATH = Path(
    "data/manifests/lpbf_included_themed.jsonl"
)

REVIEW_PATH = Path(
    "data/reviews/borealam_micro_review_v1.csv"
)

OUTPUT_PATH = Path(
    "data/reviews/borealam_micro_replacements_v1.csv"
)

def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def load_review(path):
    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


YEAR_GROUPS = {
    "2015-2019": (2015, 2019),
    "2020-2023": (2020, 2023),
    "2024-2026": (2024, 2026),
}


def get_year_group(year):
    if year is None:
        return "unknown"

    for group, (start, end) in YEAR_GROUPS.items():
        if start <= year <= end:
            return group

    return "unknown"

def rank_candidates(records):
    return sorted(
        records,
        key=lambda record: (
            -float(record.get("quality_score") or 0),
            record.get("openalex_id") or "",
        ),
    )

def find_replacement(
    original,
    candidates,
    excluded_ids,
):
    theme = original["boreal_primary_theme"]

    year_group = get_year_group(
        original.get("year")
    )

    eligible = [
        record
        for record in candidates
        if (
            record.get("boreal_primary_theme") == theme
            and record.get("openalex_id") not in excluded_ids
            and record.get("license") == "cc-by"
            and record.get("pdf_url")
        )
    ]

    same_period = [
        record
        for record in eligible
        if get_year_group(record.get("year")) == year_group
    ]

    if same_period:
        ranked = rank_candidates(same_period)
        selection_reason = "same_theme_same_period"
    else:
        ranked = rank_candidates(eligible)
        selection_reason = "same_theme_period_fallback"

    if not ranked:
        raise ValueError(
            f"No replacement available for {theme}"
        )

    return ranked[0], selection_reason

def build_replacements(pilot, candidates, review):
    pilot_by_id = {
        record["openalex_id"]: record
        for record in pilot
    }

    review_ids = [
        row["openalex_id"].strip()
        for row in review
    ]

    if (
        len(pilot) != 39
        or len(review) != 39
        or len(set(review_ids)) != 39
        or set(review_ids) != set(pilot_by_id)
    ):
        raise ValueError(
            "Review and pilot records do not match."
        )

    excluded_ids = set(pilot_by_id)
    proposals = []

    for row in review:
        decision = row["review_decision"].strip().upper()

        if decision not in {"APPROVE", "REPLACE"}:
            raise ValueError(
                f"Unresolved review decision: {decision!r}"
            )

        if decision != "REPLACE":
            continue

        if not row["review_notes"].strip():
            raise ValueError(
                "Replacement requires review notes."
            )

        original = pilot_by_id[row["openalex_id"].strip()]

        replacement, reason = find_replacement(
            original,
            candidates,
            excluded_ids,
        )

        excluded_ids.add(
            replacement["openalex_id"]
        )

        proposals.append({
            "original_openalex_id": original["openalex_id"],
            "original_title": original["title"],
            "original_year": original["year"],
            "original_review_notes": row["review_notes"],
            "replacement_openalex_id": replacement["openalex_id"],
            "replacement_title": replacement["title"],
            "replacement_year": replacement["year"],
            "primary_theme": replacement["boreal_primary_theme"],
            "quality_score": replacement["quality_score"],
            "selection_reason": reason,
            "replacement_doi": replacement.get("doi"),
            "replacement_pdf_url": replacement.get("pdf_url"),
            "replacement_abstract": (
                replacement.get("abstract") or ""
            )[:1000],
            "replacement_decision": "",
            "replacement_notes": "",
        })

    return proposals

def save_proposals(proposals, path):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if path.exists():
        raise FileExistsError(
            f"Replacement file already exists: {path}"
        )

    if not proposals:
        return

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(proposals[0].keys()),
        )

        writer.writeheader()
        writer.writerows(proposals)

def main():
    pilot = load_jsonl(PILOT_PATH)
    candidates = load_jsonl(CANDIDATE_PATH)
    review = load_review(REVIEW_PATH)

    decisions = Counter(
        row["review_decision"].strip().upper()
        for row in review
    )

    print("=" * 65)
    print("BOREALAM-MICRO REPLACEMENT SELECTION")
    print("=" * 65)

    print("Original pilot:", len(pilot))
    print("Candidate pool:", len(candidates))
    print("Approved:", decisions["APPROVE"])
    print("Replace:", decisions["REPLACE"])
    print("Unresolved:", decisions["REVIEW"])

    proposals = build_replacements(
        pilot,
        candidates,
        review,
    )

    print("\nReplacement proposals:", len(proposals))

    for proposal in proposals:
        print("\n" + "-" * 65)
        print("Theme:", proposal["primary_theme"])
        print("Original:", proposal["original_title"])
        print("Replacement:", proposal["replacement_title"])
        print("Year:", proposal["replacement_year"])
        print("Quality:", proposal["quality_score"])
        print("Reason:", proposal["selection_reason"])

    if proposals:
        save_proposals(proposals, OUTPUT_PATH)
        print("\nSaved:", OUTPUT_PATH)
    else:
        print("\nNo replacements required.")


if __name__ == "__main__":
    main()