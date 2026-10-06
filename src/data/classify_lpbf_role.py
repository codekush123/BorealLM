import json
import re
from collections import Counter


INPUT_PATH = (
    "src/data/manifests/"
    "lpbf_candidates_classified.jsonl"
)

OUTPUT_PATH = (
    "src/data/manifests/"
    "lpbf_candidates_role_classified.jsonl"
)


LPBF_PATTERNS = [
    r"\blaser powder bed fusion\b",
    r"\blaser powder-bed fusion\b",
    r"\blaser-powder bed fusion\b",
    r"\blpbf\b",
    r"\bl-pbf\b",
    r"\bl-pbfam\b",
    r"\bpbf-lb\b",
    r"\bpbf-lb/m\b",
    r"\bselective laser melting\b",
]

CORE_PROCESS_PATTERNS = [
    r"process parameter",
    r"scan speed",
    r"scanning speed",
    r"laser power",
    r"hatch spacing",
    r"layer thickness",
    r"energy density",
    r"scan strategy",
    r"scanning strategy",
    r"melt pool",
    r"keyhole",
    r"lack of fusion",
    r"powder spreading",
    r"in[- ]situ monitoring",
    r"process monitoring",
    r"thermal history",
    r"build parameter",
]

def contains_pattern(text, patterns):

    for pattern in patterns:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            return True

    return False

def classify_lpbf_role(record):

    title = record.get("title") or ""
    abstract = record.get("abstract") or ""

    full_text = f"{title} {abstract}"

    lpbf_in_title = contains_pattern(
        title,
        LPBF_PATTERNS,
    )

    lpbf_in_abstract = contains_pattern(
        abstract,
        LPBF_PATTERNS,
    )

    process_focus = contains_pattern(
        full_text,
        CORE_PROCESS_PATTERNS,
    )

    if lpbf_in_title and process_focus:
        return "core_lpbf"

    if lpbf_in_abstract and process_focus:
        return "core_lpbf"

    if lpbf_in_title or lpbf_in_abstract:
        return "lpbf_application"

    return "peripheral"

def load_records(path):

    records = []

    with open(path, "r", encoding="utf-8") as file:

        for line in file:
            records.append(
                json.loads(line)
            )

    return records

def classify_records(records):

    for record in records:

        record["lpbf_role"] = (
            classify_lpbf_role(record)
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

    records = classify_records(records)

    counts = Counter(
        record["lpbf_role"]
        for record in records
    )

    print("=" * 60)
    print("BOREALAM LPBF ROLE CLASSIFICATION")
    print("=" * 60)

    print("Total:", len(records))

    for role in [
        "core_lpbf",
        "lpbf_application",
        "peripheral",
    ]:

        count = counts[role]

        percentage = (
            count
            / len(records)
            * 100
        )

        print(
            f"{role:20s}"
            f"{count:5d} "
            f"({percentage:5.1f}%)"
        )

    save_records(
        records,
        OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()