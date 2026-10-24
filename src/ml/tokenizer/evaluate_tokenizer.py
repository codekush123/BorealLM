import json
from pathlib import Path
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

def load_dataset(path):

    return [
        json.loads(line)
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

def evaluate_split(
        tokenizer,
        records,
        work_ids,
):

    work_ids = set(work_ids)

    total_characters = 0
    total_words = 0
    total_tokens = 0
    document_count = 0

    for record in records:
        if record["work_id"] not in work_ids:
            continue

        text = record["body_text"]

        encoding = tokenizer.encode(text)

        total_characters += len(text)

        total_words += len(text.split())

        total_tokens += len(encoding.ids)

        document_count += 1

    if document_count == 0:
        raise ValueError(
            "No documents found for split."
        )

    tokens_per_character = (
        total_tokens / total_characters
    )

    characters_per_token = (
        total_characters / total_tokens
    )

    tokens_per_word = (
        total_tokens / total_words
    )

    return {
        "documents": document_count,
        "characters": total_characters,
        "words": total_words,
        "tokens": total_tokens,
        "tokens_per_character": tokens_per_character,
        "characters_per_token": characters_per_token,
        "tokens_per_word": tokens_per_word,
    }

def inspect_terms(tokenizer):

    terms = [
        "laser powder bed fusion",
        "LPBF",
        "Ti-6Al-4V",
        "SS316L",
        "melt pool",
        "keyhole porosity",
        "microstructure",
        "residual stress",
        "powder feedstock",
        "additive manufacturing",
    ]

    print("\nTECHNICAL TERM TOKENIZATION")
    print("=" * 60)

    for term in terms:

        encoding = tokenizer.encode(term)

        print(f"\nTerm: {term}")
        print("Tokens:", encoding.tokens)
        print("Token IDs:", encoding.ids)
        print("Token count:", len(encoding.ids))

def main():

    tokenizer = Tokenizer.from_file(
        str(TOKENIZER_PATH)
    )

    records = load_dataset(
        DATASET_PATH
    )

    splits = json.loads(
        SPLITS_PATH.read_text(
            encoding="utf-8"
        )
    )

    print("BOREALAM TOKENIZER EVALUATION")
    print("=" * 60)

    print(
        "Vocabulary size:",
        tokenizer.get_vocab_size(),
    )

    for split_name in [
        "train",
        "validation",
        "test",
    ]:

        metrics = evaluate_split(
            tokenizer,
            records,
            splits[split_name],
        )

        print(
            f"\n{split_name.upper()}"
        )
        print("-" * 40)

        print(
            "Documents:",
            metrics["documents"],
        )

        print(
            "Characters:",
            metrics["characters"],
        )

        print(
            "Words:",
            metrics["words"],
        )

        print(
            "Tokens:",
            metrics["tokens"],
        )

        print(
            "Tokens / character:",
            round(
                metrics[
                    "tokens_per_character"
                ],
                4,
            ),
        )

        print(
            "Characters / token:",
            round(
                metrics[
                    "characters_per_token"
                ],
                3,
            ),
        )

        print(
            "Tokens / word:",
            round(
                metrics[
                    "tokens_per_word"
                ],
                3,
            ),
        )

    inspect_terms(tokenizer)


if __name__ == "__main__":
    main()