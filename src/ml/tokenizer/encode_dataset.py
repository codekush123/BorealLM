import json
import hashlib
from pathlib import Path

import numpy as np

from tokenizers import Tokenizer

TOKENIZER_PATH = Path(
    "artifacts/tokenizer/borealam_bpe_v1.json"
)

DATASET_PATH = Path(
    "data/processed/pilot/borealam_pilot_extracted_v1.jsonl"
)

SPLITS_PATH = Path(
    "data/manifests/borealam_pilot_splits_v1.json"
)

OUTPUT_DIR = Path(
    "artifacts/dataset"
)

def load_records(path):

    return [
        json.loads(line)
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

def encode_split(
    tokenizer,
    records,
    work_ids,
):

    work_ids = set(work_ids)

    eos_id = tokenizer.token_to_id("[EOS]")

    if eos_id is None:
        raise ValueError(
            "[EOS] token not found."
        )

    token_ids = []
    document_count = 0

    for record in records:

        if record["work_id"] not in work_ids:
            continue

        encoding = tokenizer.encode(
            record["body_text"]
        )

        token_ids.extend(
            encoding.ids
        )

        token_ids.append(
            eos_id
        )

        document_count += 1

    return token_ids, document_count

def main():

    tokenizer = Tokenizer.from_file(
        str(TOKENIZER_PATH)
    )

    records = load_records(
        DATASET_PATH
    )

    splits = json.loads(
        SPLITS_PATH.read_text(
            encoding="utf-8"
        )
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = {
        "tokenizer": str(TOKENIZER_PATH),
        "tokenizer_sha256": hashlib.sha256(
            TOKENIZER_PATH.read_bytes()
        ).hexdigest(),
        "vocab_size": tokenizer.get_vocab_size(),
        "splits": {},
    }

    for split_name in [
        "train",
        "validation",
        "test",
    ]:

        token_ids, document_count = encode_split(
            tokenizer,
            records,
            splits[split_name],
        )

        array = np.asarray(
            token_ids,
            dtype=np.uint16,
        )

        output_path = (
            OUTPUT_DIR
            / f"{split_name}_tokens.npy"
        )

        np.save(
            output_path,
            array,
        )

        metadata["splits"][split_name] = {
            "documents": document_count,
            "tokens": len(token_ids),
            "file": str(output_path),
        }

        print(
            f"{split_name}: "
            f"{document_count} documents, "
            f"{len(token_ids)} tokens"
        )

    metadata_path = (
        OUTPUT_DIR
        / "tokenization_metadata.json"
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nTOKEN DATASET CREATED")
    print("=" * 50)
    print("Vocabulary:", tokenizer.get_vocab_size())
    print("Output:", OUTPUT_DIR)


if __name__ == "__main__":
    main()