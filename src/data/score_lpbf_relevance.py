"""
inspect a few high, medium, and especially low papers.
Created: 06/10/2026
Updated: 06/10/2026
"""

import json
import re
from collections import Counter


INPUT_PATH = (
    "src/data/manifests/"
    "lpbf_candidates_classified.jsonl"
)

OUTPUT_PATH = (
    "src/data/manifests/"
    "lpbf_candidates_scored.jsonl"
)

LPBF_PATTERNS = [
    r"\blaser powder bed fusion\b",
    r"\blaser powder-bed fusion\b",
    r"\blpbf\b",
    r"\bl-pbf\b",
    r"\bpbf-lb\b",
    r"\bpbf-lb/m\b",
    r"\bselective laser melting\b",
]

OTHER_PROCESS_PATTERNS = [
    r"\bwire arc additive manufacturing\b",
    r"\bwaam\b",
    r"\belectron beam melting\b",
    r"\bdirected energy deposition\b",
    r"\bded\b",
    r"\bbinder jetting\b",
    r"\bfused deposition modeling\b",
    r"\bfused filament fabrication\b",
    r"\bmaterial extrusion\b",
    r"\bcold metal transfer\b",
]

def count_matches(text, patterns):
    count = 0

    for pattern in patterns:
        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        count += len(matches)


    return count

def score_relevance(record):
    title = record.get("title") or ""
    abstract = record.get("abstract") or ""

    title_lpbf = count_matches(
        title,
        LPBF_PATTERNS,
    )

    abstract_lpbf = count_matches(
        abstract,
        LPBF_PATTERNS,
    )

    title_other_process = count_matches(
        title,
        OTHER_PROCESS_PATTERNS,
    )

    score = 0

    if title_lpbf > 0:
        score += 5

    score += min(
        abstract_lpbf,
        5,
    )

    if title_other_process > 0 and title_lpbf == 0:
        score -= 4

    return {
        "score": score,
        "title_lpbf_mentions": title_lpbf,
        "abstract_lpbf_mentions": abstract_lpbf,
        "other_process_in_title": title_other_process,
    }

def relevance_label(score):
    if score >= 6:
        return "high"

    if score >= 3:
        return "medium"

    return "low"

def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            records.append(
                json.loads(line)
            )

    return records

def score_records(records):
    for record in records:

        relevance = score_relevance(record)

        record["lpbf_relevance_score"] = (
            relevance["score"]
        )

        record["lpbf_relevance"] = (
            relevance_label(
                relevance["score"]
            )
        )

        record["lpbf_relevance_details"] = relevance

    return records

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

    scored_records = score_records(records)

    counts = Counter(
        record["lpbf_relevance"]
        for record in scored_records
    )

    print("=" * 60)
    print("BOREALAM LPBF RELEVANCE")
    print("=" * 60)

    print("Total:", len(scored_records))

    for label in ["high", "medium", "low"]:

        count = counts[label]

        percentage = (
            count
            / len(scored_records)
            * 100
        )

        print(
            f"{label:10s}"
            f"{count:5d} "
            f"({percentage:5.1f}%)"
        )

    save_records(
        scored_records,
        OUTPUT_PATH,
    )

    print()
    print("Saved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()