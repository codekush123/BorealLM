import sys
import json
import math
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from torch.optim import AdamW


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_DIR = PROJECT_ROOT / "src" / "ml" / "models"
TRAINING_DIR = PROJECT_ROOT / "src" / "ml" / "training"

sys.path.insert(0, str(MODEL_DIR))
sys.path.insert(0, str(TRAINING_DIR))

from boreallm import BorealLM
from lm_dataset import create_loader


TRAIN_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "dataset"
    / "train_tokens.npy"
)

VALIDATION_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "dataset"
    / "validation_tokens.npy"
)

CHECKPOINT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "checkpoints"
)

HISTORY_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "training"
    / "boreallm_v1_3epoch_history.json"
)


SEED = 42

CONTEXT_LENGTH = 256
BATCH_SIZE = 4

EPOCHS = 3

LEARNING_RATE = 3e-4
WEIGHT_DECAY = 0.1
MAX_GRAD_NORM = 1.0

LOG_EVERY = 25

def set_seed(seed):

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def get_device():

    if torch.cuda.is_available():
        return torch.device("cuda")

    if (
        hasattr(torch.backends, "mps")
        and torch.backends.mps.is_available()
    ):
        return torch.device("mps")

    return torch.device("cpu")

def language_model_loss(
    logits,
    targets,
    vocab_size,
):

    return F.cross_entropy(
        logits.reshape(
            -1,
            vocab_size,
        ),
        targets.reshape(-1),
    )

@torch.no_grad()
def evaluate(
    model,
    loader,
    device,
):

    model.eval()

    total_loss = 0.0
    total_batches = 0

    for x, y in loader:

        x = x.to(device)
        y = y.to(device)

        logits = model(x)

        loss = language_model_loss(
            logits,
            y,
            model.vocab_size,
        )

        total_loss += loss.item()
        total_batches += 1

    if total_batches == 0:
        raise ValueError(
            "Validation loader contains no batches."
        )

    average_loss = (
        total_loss / total_batches
    )

    return average_loss

def save_checkpoint(
    model,
    optimizer,
    epoch,
    validation_loss,
    path,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    checkpoint = {
        "epoch": epoch,
        "validation_loss": validation_loss,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),

        "model_config": {
            "vocab_size": 4096,
            "context_length": 256,
            "embedding_dim": 256,
            "num_heads": 8,
            "num_layers": 10,
            "hidden_dim": 1024,
            "dropout": 0.1,
        },
    }

    torch.save(
        checkpoint,
        path,
    )

def main():

    set_seed(SEED)

    device = get_device()

    print("BOREALLM TRAINING")
    print("=" * 60)

    print("Device:", device)
    print("Epochs:", EPOCHS)
    print("Batch size:", BATCH_SIZE)
    print("Context length:", CONTEXT_LENGTH)
    print("Learning rate:", LEARNING_RATE)

    model = BorealLM().to(device)

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

    print("\nDATA")
    print("-" * 60)

    print(
        "Training sequences:",
        len(train_dataset),
    )

    print(
        "Validation sequences:",
        len(validation_dataset),
    )

    optimizer = AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    history = []

    best_validation_loss = float("inf")

    global_step = 0

    for epoch in range(1, EPOCHS + 1):

        model.train()

        running_loss = 0.0

        print(
            f"\nEPOCH {epoch}/{EPOCHS}"
        )

        print("-" * 60)

        for batch_index, (x, y) in enumerate(
            train_loader,
            start=1,
        ):

            x = x.to(device)
            y = y.to(device)

            optimizer.zero_grad(
                set_to_none=True
            )

            logits = model(x)

            loss = language_model_loss(
                logits,
                y,
                model.vocab_size,
            )

            if not torch.isfinite(loss):
                raise ValueError(
                    "Training loss became non-finite."
                )

            loss.backward()

            gradient_norm = (
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    MAX_GRAD_NORM,
                )
            )

            optimizer.step()

            running_loss += loss.item()

            global_step += 1

            if batch_index % LOG_EVERY == 0:

                average_loss = (
                    running_loss
                    / LOG_EVERY
                )

                print(
                    f"Step {global_step:5d} | "
                    f"batch {batch_index:4d}/"
                    f"{len(train_loader):4d} | "
                    f"loss {average_loss:.4f} | "
                    f"grad {gradient_norm.item():.3f}"
                )

                running_loss = 0.0

            validation_loss = evaluate(
                model,
                validation_loader,
                device,
            )

            validation_perplexity = math.exp(
                min(validation_loss, 20)
            )

            print("\nVALIDATION")
            print("-" * 60)

            print(
                "Validation loss:",
                f"{validation_loss:.4f}",
            )

            print(
                "Validation perplexity:",
                f"{validation_perplexity:.2f}",
            )

            epoch_record = {
                "epoch": epoch,
                "global_step": global_step,
                "validation_loss": validation_loss,
                "validation_perplexity": (
                    validation_perplexity
                ),
            }

            history.append(
                epoch_record
            )

        if validation_loss < best_validation_loss:

            best_validation_loss = (
                validation_loss
            )

            checkpoint_path = (
                CHECKPOINT_DIR
                / "boreallm_v1_3epoch_best.pt"
            )

            save_checkpoint(
                model=model,
                optimizer=optimizer,
                epoch=epoch,
                validation_loss=validation_loss,
                path=checkpoint_path,
            )

            print(
                "Best checkpoint saved:",
                checkpoint_path,
            )

    HISTORY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    HISTORY_PATH.write_text(
        json.dumps(
            {
                "seed": SEED,
                "epochs": EPOCHS,
                "batch_size": BATCH_SIZE,
                "context_length": CONTEXT_LENGTH,
                "learning_rate": LEARNING_RATE,
                "weight_decay": WEIGHT_DECAY,
                "history": history,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nTRAINING COMPLETE")
    print("=" * 60)

    print(
        "Best validation loss:",
        f"{best_validation_loss:.4f}",
    )

    print(
        "History:",
        HISTORY_PATH,
    )


if __name__ == "__main__":
    main()