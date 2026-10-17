"""This will give you 5 randomly selected papers from every category.
manual validation of the classifier
Created:06/10/2026
Updated:06/10/2026
"""
import json
import random

INPUT_PATH = "data/manifests/lpbf_candidates_classified.jsonl"


SAMPLES_PER_TOPICS = 5

RANDOM_SEED = 42

def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))


    return records

def get_records_for_topic(records, topic):
    return [
        record
        for record in records
        if topic in record.get("boreal_topics", [])
    ]

def main():
    records = load_records(INPUT_PATH)

    random.seed(RANDOM_SEED)

    all_topics = set()

    for record in records:
        for topic in record.get("boreal_topics", []):
            all_topics.add(topic)


    for topic in sorted(all_topics):

        matching_records = get_records_for_topic(
            records,
            topic,
        )

        sample_size = min(
            SAMPLES_PER_TOPICS,
            len(matching_records),
        )

        samples = random.sample(
            matching_records,
            sample_size,
        )

        print()
        print("=" * 80)
        print(topic.upper())
        print("=" * 80)

        for index, record in enumerate(samples, start=1):
            print()
            print(f"[{index}] {record.get('title')}")
            print("Year:", record.get("year"))
            print("Topics:", record.get("boreal_topics"))

            abstract = record.get("abstract") or ""

            print()
            print("Abstract preview:")
            print(abstract[:500])

            print("-" * 80)


if __name__ == "__main__":
    main()