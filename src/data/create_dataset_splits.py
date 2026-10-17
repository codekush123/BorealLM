import json
import random
import hashlib

from pathlib import Path

INPUT_PATH = Path(
    "data/processed/pilot/borealam_pilot_extracted_v1.jsonl"
)

OUTPUT_PATH = Path(
    "data/manifests/borealam_pilot_splits_v1.json"
)

SEED = 42

def main():

    records = [
        json.loads(line)
        for line in INPUT_PATH.read_text(
            encoding="utf-8"
        ).splitlines()

        if line.strip()
    ]

    work_ids = sorted(
        record["work_id"]
        for record in records
    )

    #This ensures no documents appear twice

    if len(work_ids) != len(set(work_ids)):
        raise ValueError("Duplicate work IDs detected.")


    rng = random.Random(SEED)
    rng.shuffle(work_ids)

    n = len(work_ids)

    n_test = round(n * 0.10)
    n_val = round(n * 0.10)

    test_ids = work_ids[:n_test]

    val_ids = work_ids[
        n_test:n_test + n_val
    ]

    train_ids = work_ids[
        n_test + n_val:
    ]

    splits = {
        "seed": SEED,
        "source_sha256": hashlib.sha256(
            INPUT_PATH.read_bytes()
        ).hexdigest(),
        "train": train_ids,
        "validation": val_ids,
        "test": test_ids,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if OUTPUT_PATH.exists():
        raise FileExistsError(
            f"Split manifest already exists: {OUTPUT_PATH}"
        )

    OUTPUT_PATH.write_text(
        json.dumps(splits, indent=2),
        encoding="utf-8",
    )

    print("BOREALAM DATASET SPLITS")
    print("=" * 50)

    print("Total papers:", n)
    print("Training:", len(train_ids))
    print("Validation:", len(val_ids))
    print("Test:", len(test_ids))

    print("\nSaved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()