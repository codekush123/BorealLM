import json
import random


INPUT_PATH = (
    "src/data/manifests/"
    "lpbf_included_themed.jsonl"
)

RANDOM_SEED = 42
SAMPLE_SIZE = 30

def load_records(path):
    records = []


    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            records.append(
                json.loads(line)
            )

    return records

def main():
    records = load_records(INPUT_PATH)

    other_records = [
        record
        for record in records
        if record.get("boreal_primary_theme") == "other_lpbf"
    ]

    print("=" * 80)
    print("BOREALAM OTHER_LPBF AUDIT")
    print("=" * 80)

    print("Total other_lpbf papers:", len(other_records))

    random.seed(RANDOM_SEED)

    sample_size = min(
        SAMPLE_SIZE,
        len(other_records),
    )

    samples = random.sample(
        other_records,
        sample_size,
    )

    for index, record in enumerate(samples, start=1):

        print()
        print("=" * 80)
        print(f"[{index}] {record.get('title')}")
        print("=" * 80)

        print("Year:", record.get("year"))
        print("Role:", record.get("lpbf_role"))
        print("Quality score:", record.get("quality_score"))

        print(
            "Existing topics:",
            record.get("boreal_topics")
        )

        abstract = record.get("abstract") or ""

        print()
        print("Abstract preview:")
        print(
            abstract[:800]
        )

if __name__ == "__main__":
    main()
