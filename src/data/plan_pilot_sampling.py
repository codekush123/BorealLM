import json
from collections import Counter
from inspect_other_theme import load_records

INPUT_PATH = (
    "data/manifests/lpbf_included_themed.jsonl"
)

def get_year_group(year):
    if year is None:
        return "unknown"

    if 2015 <= year <= 2019:
        return "2015-2019"

    if 2020 <= year <= 2023:
        return "2020-2023"

    if 2024 <= year <= 2026:
        return "2024-2026"

    return "unknown"

def main():
    records = load_records(INPUT_PATH)

    counts = Counter()

    for record in records:
        theme = record.get("boreal_primary_theme")

        year = record.get("year")

        year_group = get_year_group(year)

        counts[(theme, year_group)] += 1


    themes = sorted(
        {
            record["boreal_primary_theme"]
            for record in records
        }
    )

    print("=" * 85)
    print("BOREALAM PILOT SAMPLING AVAILABILITY")
    print("=" * 85)


    print(
        f"{'Theme':28s}"
        f"{'2015-19':>10s}"
        f"{'2020-23':>10s}"
        f"{'2024-26':>10s}"
        f"{'Total':>10s}"
    )

    for theme in themes:
        old = counts[(theme, "2015-2019")]
        middle = counts[(theme, "2020-2023")]
        recent = counts[(theme, "2024-2026")]

        total = old + middle + recent


        print(
            f"{theme:28s}"
            f"{old:10d}"
            f"{middle:10d}"
            f"{recent:10d}"
            f"{total:10d}"
        )

    print()
    print("Total records:", len(records))
    print(
        "Outside year groups:",
        sum(
            count
            for (theme, group), count in counts.items()
            if group == "unknown"
        ),
    )

if __name__ == "__main__":
    main()