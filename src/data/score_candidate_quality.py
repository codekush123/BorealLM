import json
from collections import Counter
from statistics import mean, median


INPUT_PATH = (
    "src/data/manifests/"
    "lpbf_included.jsonl"
)

OUTPUT_PATH = (
    "src/data/manifests/"
    "lpbf_included_quality_scored.jsonl"
)

REFERENCE_YEAR = 2026

def calculate_citation_rate(record):
    citations = record.get("citations") or 0
    year = record.get("year")

    if not year:
        return 0.0

    years_active = max(
        1,
        REFERENCE_YEAR - year + 1,
    )

    return citations / years_active

def citation_score(citation_rate):
    if citation_rate >= 10:
        return 3.0

    if citation_rate >= 3:
        return 2.0

    if citation_rate >= 1:
        return 1.0

    if citation_rate > 0:
        return 0.5

    return 0.0

def metadata_score(record):
    score = 0.0

    if record.get("abstract"):
        score += 1.0

    if record.get("doi"):
        score += 0.5

    if record.get("journal"):
        score += 0.5

    if record.get("year"):
        score += 0.5

    if record.get("pdf_url"):
        score += 0.5

    return score

def role_score(record):
    role = record.get("lpbf_role")

    if role == "core_lpbf":
        return 2.0

    if role == "lpbf_application":
        return 1.0

    return 0.0

def extraction_score(record):
    if record.get("grobid_xml_url"):
        return 1.0

    if record.get("openalex_pdf_url"):
        return 0.5

    if record.get("pdf_url"):
        return 0.25

    return 0.0

def score_record(record):
    citation_rate = calculate_citation_rate(record)

    components = {
        "metadata": metadata_score(record),
        "citation_evidence": citation_score(
            citation_rate
        ),
        "lpbf_role": role_score(record),
        "extraction_readiness":
            extraction_score(record),
    }

    total_score = sum(components.values())

    record["quality_score"] = round(
        total_score,
        2,
    )

    record["quality_priority"] = (
        priority_label(total_score)
    )

    return record

def priority_label(score):
    if score >= 7:
        return "high"

    if score >= 5:
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

    scored_records = []

    for record in records:
        scored_records.append(
            score_record(record)
        )

    scores = [
        record["quality_score"]
        for record in scored_records
    ]

    priorities = Counter(
        record["quality_priority"]
        for record in scored_records
    )

    print("=" * 60)
    print("BOREALAM CANDIDATE QUALITY REPORT")
    print("=" * 60)

    print("Total papers:", len(scored_records))

    print(
        "Minimum score:",
        min(scores),
    )

    print(
        "Maximum score:",
        max(scores),
    )

    print(
        "Mean score:",
        round(mean(scores), 2),
    )

    print(
        "Median score:",
        round(median(scores), 2),
    )

    print()

    for priority in [
        "high",
        "medium",
        "low",
    ]:
        count = priorities[priority]

        percentage = (
            count
            / len(scored_records)
            * 100
        )

        print(
            f"{priority:10s}"
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