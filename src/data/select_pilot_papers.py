import json
from collections import defaultdict, Counter

INPUT_PATH = (
    "data/manifests/lpbf_included_themed.jsonl"
)

OUTPUT_PATH = (
    "data/manifests/borealam_micro_pilot_v1.jsonl"
)

PAPERS_PER_THEME = 3

EXCLUDED_THEMES = {"other_lpbf"}

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

def select_papers_for_theme(records):
    selected = []
    selected_ids = set()

    # First: one paper from each available year group
    for year_group in YEAR_GROUPS:

        candidates = [
            record
            for record in records
            if get_year_group(record.get("year")) == year_group
        ]

        if not candidates:
            continue

        best = rank_candidates(candidates)[0]

        selected.append({
            **best,
            "pilot_selection_reason": f"best_in_{year_group}",
        })

        selected_ids.add(best["openalex_id"])

    # Second: fill missing positions by quality
    for record in rank_candidates(records):

        if len(selected) >= PAPERS_PER_THEME:
            break

        if record["openalex_id"] in selected_ids:
            continue

        selected.append({
            **record,
            "pilot_selection_reason": "quality_fallback",
        })

        selected_ids.add(record["openalex_id"])

    if len(selected) != PAPERS_PER_THEME:
        raise ValueError(
            "Not enough candidates for this theme."
        )

    return selected

def group_by_theme(records):
    grouped = defaultdict(list)

    for record in records:
        theme = record.get("boreal_primary_theme")

        if not theme or theme in EXCLUDED_THEMES:
            continue

        grouped[theme].append(record)

    return grouped

def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def save_records(records, path):
    with open(path, "w", encoding="utf-8") as file:
        for record in records:
            file.write(
                json.dumps(record, ensure_ascii=False)
                + "\n"
            )

def main():
    records = load_records(INPUT_PATH)

    grouped = group_by_theme(records)

    pilot_records = []

    for theme in sorted(grouped):
        selected = select_papers_for_theme(
            grouped[theme]
        )

        pilot_records.extend(selected)

    # Important integrity checks
    unique_ids = {
        record["openalex_id"]
        for record in pilot_records
    }

    assert len(pilot_records) == 39
    assert len(unique_ids) == 39

    print("=" * 70)
    print("BOREALAM-MICRO PILOT SELECTION")
    print("=" * 70)

    print("Total candidate papers:", len(records))
    print("Selected papers:", len(pilot_records))
    print("Technical themes:", len(grouped))

    print("\nYear distribution:")

    year_counts = Counter(
        get_year_group(record.get("year"))
        for record in pilot_records
    )

    for group, count in year_counts.items():
        print(f"  {group}: {count}")

    print("\nSelected papers:")

    for record in pilot_records:
        print(
            f"\n[{record['boreal_primary_theme']}] "
            f"{record['title']}"
        )
        print(
            f"Year: {record['year']} | "
            f"Score: {record['quality_score']}"
        )
        print(
            "Selection:",
            record["pilot_selection_reason"]
        )

    save_records(pilot_records, OUTPUT_PATH)

    print("\nSaved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()