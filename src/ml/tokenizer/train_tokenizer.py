import json
import hashlib
from pathlib import Path
from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders

DATASET_PATH = Path(
    "data/processed/pilot/borealam_pilot_extracted_v1.jsonl"
)

SPLITS_PATH = Path(
    "data/manifests/borealam_pilot_splits_v1.json"
)

OUTPUT_PATH = Path(
    "artifacts/tokenizer/borealam_bpe_v1.json"
)

VOCAB_SIZE = 4096

def main():
    splits = json.loads(
        SPLITS_PATH.read_text(encoding="utf-8")
    )

    dataset_hash = hashlib.sha256(
        DATASET_PATH.read_bytes()
    ).hexdigest()

    if dataset_hash != splits["source_sha256"]:
        raise ValueError("Dataset changed since splitting.")

    records = [
        json.loads(line)
        for line in DATASET_PATH.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    train_ids = set(splits["train"])

    train_texts = [
        record["body_text"]
        for record in records
        if record["work_id"] in train_ids
    ]

    if len(train_texts) != len(train_ids):
        raise ValueError("Training document count mismatch.")

    print("Training documents:", len(train_texts))
    print("Training characters:", sum(map(len, train_texts)))

    tokenizer = Tokenizer(
        models.BPE(unk_token="[UNK]")
    )


    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(
        add_prefix_space=False
    )

    tokenizer.decoder = decoders.ByteLevel()

    trainer = trainers.BpeTrainer(
        vocab_size=VOCAB_SIZE,
        min_frequency=2,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        special_tokens=["[UNK]", "[BOS]", "[EOS]", "[PAD]"]
    )

    tokenizer.train_from_iterator(
        train_texts, trainer=trainer,
    )

    if OUTPUT_PATH.exists():
        raise FileExistsError(OUTPUT_PATH)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    tokenizer.save(str(OUTPUT_PATH))

    sample = "Laser powder bed fusion of Ti-6Al-4V."
    encoding = tokenizer.encode(sample)

    print("\nBOREALAM TOKENIZER RESULTS")
    print("=" * 50)
    print("Vocabulary size:", tokenizer.get_vocab_size())
    print("Sample:", sample)
    print("Tokens:", encoding.tokens)
    print("Token IDs:", encoding.ids)
    print("Decoded:", tokenizer.decode(encoding.ids))
    print("Round-trip correct:",
          tokenizer.decode(encoding.ids) == sample)
    print("Saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()

