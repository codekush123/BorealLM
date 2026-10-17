import json
from collections import Counter

INPUT_PATH = (
    "data/manifests/"
    "lpbf_included_quality_scored.jsonl"
)

OUTPUT_PATH = (
    "data/manifests/"
    "lpbf_included_themed.jsonl"
)

THEME_KEYWORDS = {
    "process_parameters": [
        "process parameter",
        "process parameters",
        "processing parameter",
        "processing parameters",
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
        "microstructural",
        "grain structure",
        "grain morphology",
        "phase transformation",
        "phase evolution",
        "texture evolution",
        "crystallographic texture",
        "cellular substructure",
    ],

    "mechanical_properties": [
        "mechanical properties",
        "mechanical behavior",
        "mechanical behaviour",
        "tensile strength",
        "yield strength",
        "compressive strength",
        "compressive behavior",
        "compressive behaviour",
        "fatigue",
        "hardness",
        "fracture",
        "ductility",
        "stiffness",
        "energy absorption",
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

    "design_geometry": [
        "lattice structure",
        "lattice structures",
        "topology optimization",
        "topological design",
        "build orientation",
        "cellular structure",
        "porous structure",
        "triply periodic minimal surface",
        "tpms",
        "metamaterial",
        "lightweight structure",
        "geometry optimization",
        "geometric design",
    ],

    "powder_feedstock": [
        "powder recycling",
        "recycled powder",
        "powder reuse",
        "powder rejuvenation",
        "powder characteristic",
        "powder characteristics",
        "powder morphology",
        "particle size",
        "powder flowability",
        "flowability",
        "spreadability",
        "powder packing",
        "feedstock",
        "gas atomization",
    ],

    "surface_post_processing": [
        "surface roughness",
        "surface finish",
        "surface quality",
        "surface state",
        "polishing",
        "grinding",
        "machining",
        "post-processing",
        "post processing",
        "heat treatment",
        "heat-treated",
        "annealing",
        "welding",
        "surface modification",
    ],

    "functional_properties": [
        "electrical conductivity",
        "thermal conductivity",
        "thermal expansion",
        "magnetic properties",
        "magnetic",
        "electrochemical",
        "electrode",
        "tribological",
        "tribology",
        "corrosion resistance",
        "corrosion behavior",
        "corrosion behaviour",
        "oxidation resistance",
        "wear resistance",
    ],

    "manufacturability": [
        "manufacturability",
        "printability",
        "processability",
        "cracking susceptibility",
        "processing window",
        "process window",
        "fabrication feasibility",
        "manufacturing limitation",
        "manufacturing limitations",
    ],
}

def count_keyword_matches(text, keywords):
    text = text.lower()

    count = 0

    for keyword in keywords:
        if keyword.lower() in text:
            count += 1

    return count

def calculate_theme_scores(record):
    title = record.get("title") or ""
    abstract = record.get("abstract") or ""

    scores = {}

    for theme, keywords in THEME_KEYWORDS.items():

        title_matches = count_keyword_matches(
            title,
            keywords,
        )

        abstract_matches = count_keyword_matches(
            abstract,
            keywords,
        )

        score = (
            title_matches * 3
            + abstract_matches
        )

        scores[theme] = score

    return scores

def assign_themes(record):
    scores = calculate_theme_scores(record)

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    positive_themes = [
        (theme, score)
        for theme, score in ranked
        if score > 0
    ]

    if not positive_themes:
        record["boreal_primary_theme"] = "other_lpbf"
        record["boreal_secondary_themes"] = []
        record["boreal_theme_scores"] = scores

        return record

    primary_theme = positive_themes[0][0]

    secondary_themes = [
        theme
        for theme, score in positive_themes[1:]
    ]

    record["boreal_primary_theme"] = primary_theme
    record["boreal_secondary_themes"] = secondary_themes
    record["boreal_theme_scores"] = scores

    return record

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

    themed_records = []

    for record in records:
        themed_records.append(
            assign_themes(record)
        )

    counts = Counter(
        record["boreal_primary_theme"]
        for record in themed_records
    )

    print("=" * 60)
    print("BOREALAM PRIMARY THEME DISTRIBUTION")
    print("=" * 60)

    print("Total papers:", len(themed_records))
    print()

    for theme, count in counts.most_common():

        percentage = (
            count
            / len(themed_records)
            * 100
        )

        print(
            f"{theme:25s}"
            f"{count:5d} "
            f"({percentage:5.1f}%)"
        )

    save_records(
        themed_records,
        OUTPUT_PATH,
    )

    print()
    print("Saved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()