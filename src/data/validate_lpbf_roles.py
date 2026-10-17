import json
import random


INPUT_PATH = (
    "data/manifests/"
    "lpbf_candidates_role_classified.jsonl"
)

RANDOM_SEED = 42

SAMPLE_SIZES = {
    "core_lpbf": 10,
    "lpbf_application": 10,
    "peripheral": 9,
}


def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    return records


def get_records_by_role(records, role):
    return [
        record
        for record in records
        if record.get("lpbf_role") == role
    ]


def main():
    records = load_records(INPUT_PATH)

    random.seed(RANDOM_SEED)

    for role in [
        "core_lpbf",
        "lpbf_application",
        "peripheral",
    ]:

        matching_records = get_records_by_role(
            records,
            role,
        )

        sample_size = min(
            SAMPLE_SIZES[role],
            len(matching_records),
        )

        samples = random.sample(
            matching_records,
            sample_size,
        )

        print()
        print("=" * 80)
        print(role.upper())
        print("=" * 80)

        for index, record in enumerate(samples, start=1):

            print()
            print(f"[{index}] {record.get('title')}")
            print("Year:", record.get("year"))
            print("Topics:", record.get("boreal_topics"))

            abstract = record.get("abstract") or ""

            print()
            print("Abstract preview:")
            print(abstract[:700])

            print("-" * 80)


if __name__ == "__main__":
    main()