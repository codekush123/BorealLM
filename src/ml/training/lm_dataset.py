from pathlib import Path

import numpy as np
import torch

from torch.utils.data import Dataset, DataLoader

TRAIN_PATH = Path(
    "artifacts/dataset/train_tokens.npy"
)

VALIDATION_PATH = Path(
    "artifacts/dataset/validation_tokens.npy"
)

CONTEXT_LENGTH = 256
BATCH_SIZE = 8

class CausalTokenDataset(Dataset):

    def __init__(
        self,
        token_path,
        context_length,
    ):

        self.tokens = np.load(
            token_path,
            mmap_mode="r",
        )

        self.context_length = context_length

        if len(self.tokens) <= context_length:
            raise ValueError(
                "Token stream is shorter than context length."
            )

        self.num_sequences = (
            (len(self.tokens) - 1)
            // context_length
        )

    def __len__(self):

        return self.num_sequences

    def __getitem__(self, index):

        start = index * self.context_length
        end = start + self.context_length + 1

        chunk = np.asarray(
            self.tokens[start:end],
            dtype=np.int64,
        )

        x = torch.from_numpy(
            chunk[:-1].copy()
        )

        y = torch.from_numpy(
            chunk[1:].copy()
        )

        return x, y

def create_loader(
    token_path,
    context_length,
    batch_size,
    shuffle,
):

    dataset = CausalTokenDataset(
        token_path,
        context_length,
    )

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=True,
    )

    return dataset, loader

def main():

    train_dataset, train_loader = create_loader(
        TRAIN_PATH,
        CONTEXT_LENGTH,
        BATCH_SIZE,
        shuffle=True,
    )

    validation_dataset, validation_loader = create_loader(
        VALIDATION_PATH,
        CONTEXT_LENGTH,
        BATCH_SIZE,
        shuffle=False,
    )

    print("BOREALLM CAUSAL DATASET")
    print("=" * 50)

    print("Context length:", CONTEXT_LENGTH)

    print(
        "Training sequences:",
        len(train_dataset),
    )

    print(
        "Validation sequences:",
        len(validation_dataset),
    )

    x, y = next(iter(train_loader))

    print("\nFIRST TRAINING BATCH")
    print("-" * 50)

    print("Input shape:", x.shape)
    print("Target shape:", y.shape)

    print("Input dtype:", x.dtype)
    print("Target dtype:", y.dtype)

    print("\nFirst 12 input IDs:")
    print(x[0, :12])

    print("\nFirst 12 target IDs:")
    print(y[0, :12])

    shifted_correct = torch.equal(
        x[0, 1:],
        y[0, :-1],
    )

    print(
        "\nTarget shift correct:",
        shifted_correct,
    )


if __name__ == "__main__":
    main()