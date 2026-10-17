import json
from collections import Counter

INPUT_PATH = "data/manifests/lpbf_candidates_canonical.jsonl"

OUTPUT_PATH = (
    "data/manifests/"
    "lpbf_candidates_classified.jsonl"
)

TOPIC_KEYWOARDS = {

    "process_parameters": [
        "process parameter",
        "laser power",
        "scan speed",
        "scanning speed",
        "hatch spacing",
        "layer thickness",
        "energy density",
        "process optimization",
    ],

    "melt_pool_thermal": [
        "melt pool",
        "thermal history",
        "temperature field",
        "heat transfer",
        "cooling rate",
        "thermal gradient",
        "solidification",
    ],

    "defects_porosity": [
        "porosity",
        "pore formation",
        "keyhole",
        "lack of fusion",
        "defect",
        "crack formation",
        "balling",
    ],

    "microstructure": [
        "microstructure",
        "grain structure",
        "grain morphology",
        "phase transformation",
        "texture evolution",
        "crystallographic texture",
    ],

    "mechanical_properties": [
        "mechanical properties",
        "tensile strength",
        "yield strength",
        "fatigue",
        "hardness",
        "fracture",
        "ductility",
    ],

    "residual_stress": [
        "residual stress",
        "distortion",
        "warpage",
        "thermal stress",
    ],

    "monitoring_sensing": [
        "in situ monitoring",
        "in-situ monitoring",
        "process monitoring",
        "melt pool monitoring",
        "sensor",
        "thermography",
        "high-speed imaging",
        "acoustic emission",
    ],

    "simulation_modeling": [
        "finite element",
        "finite element model",
        "numerical simulation",
        "computational model",
        "simulation",
        "multiphysics",
        "computational fluid dynamics",
        "cfd",
    ],

    "materials": [
        "ti-6al-4v",
        "ti6al4v",
        "inconel 718",
        "inconel 625",
        "316l",
        "alsi10mg",
        "stainless steel",
        "nickel alloy",
        "aluminum alloy",
        "aluminium alloy",
        "titanium alloy",
    ],

    "review": [
        "review of",
        "a review",
        "systematic review",
        "state of the art",
        "state-of-the-art",
    ],
}

def classify_record(record):
    """
    This function will classify the paper based on the mentioned keywoards as a TOPIC_KEYWOARDS
    Created: 06/10/2026
    Updated: 06/10/2026
    """
    title = record.get("title") or ""
    abstract = record.get("abstract") or ""


    text = f"{title} {abstract}".lower()

    matched_topics = []

    for topic, keywoards in TOPIC_KEYWOARDS.items():

        for keywoard in keywoards:
            if keywoard in text:
                matched_topics.append(topic)
                break


    if not matched_topics:
        matched_topics.append("other_lpbf")

    return matched_topics

def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    return records

def classify_records(records):

    for record in records:

        topics = classify_record(record)

        record["boreal_topics"] = topics


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

def count_topics(records):

    counter = Counter()

    for record in records:

        for topic in record["boreal_topics"]:
            counter[topic] += 1


    return counter

def main():
    records = load_records(INPUT_PATH)
    classified_records = classify_records(records)

    topic_counts = count_topics(
        classified_records
    )

    print("=" * 60)
    print("BOREALAM LPBF TOPIC DISTRIBUTION")
    print("=" * 60)

    print("Total papers:", len(classified_records))

    for topic, count in topic_counts.most_common():

        percentage = (
            count
            / len(classified_records)
            * 100
        )

        print(
            f"{topic:25s}"
            f"{count:5d}"
            f"({percentage:5.1f}%)"
        )


    save_records(
        classified_records,
        OUTPUT_PATH,
    )

    print()
    print("Saved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
