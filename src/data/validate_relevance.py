"""
test whether the labels actually correspond to human judgment.
Created: 06/10/2026
Updated: 06/10/2026
"""
import json
import random


INPUT_PATH = (
    "src/data/manifests/"
    "lpbf_candidates_scored.jsonl"
)

RANDOM_SEED = 42

SAMPLE_SIZES = {
    "high": 10,
    "medium": 10,
    "low": 20,
}


def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    return records


def records_by_relevance(records, label):
    return [
        record
        for record in records
        if record.get("lpbf_relevance") == label
    ]


def main():
    records = load_records(INPUT_PATH)

    random.seed(RANDOM_SEED)

    for label in ["high", "medium", "low"]:

        candidates = records_by_relevance(
            records,
            label,
        )

        sample_size = min(
            SAMPLE_SIZES[label],
            len(candidates),
        )

        samples = random.sample(
            candidates,
            sample_size,
        )

        print()
        print("=" * 80)
        print(f"{label.upper()} RELEVANCE")
        print("=" * 80)

        for index, record in enumerate(samples, start=1):

            print()
            print(f"[{index}] {record.get('title')}")

            print(
                "Score:",
                record.get("lpbf_relevance_score")
            )

            print(
                "Topics:",
                record.get("boreal_topics")
            )

            details = (
                record.get("lpbf_relevance_details")
                or {}
            )

            print(
                "Title LPBF mentions:",
                details.get("title_lpbf_mentions")
            )

            print(
                "Abstract LPBF mentions:",
                details.get("abstract_lpbf_mentions")
            )

            print(
                "Other process in title:",
                details.get("other_process_in_title")
            )

            abstract = record.get("abstract") or ""

            print("\nAbstract preview:")
            print(abstract[:700])

            print("-" * 80)


if __name__ == "__main__":
    main()