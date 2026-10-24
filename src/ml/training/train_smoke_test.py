import sys
from pathlib import Path

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

TRAIN_PATH = PROJECT_ROOT / (
    "artifacts/dataset/train_tokens.npy"
)

CONTEXT_LENGTH = 256
BATCH_SIZE = 4

LEARNING_RATE = 3e-4
MAX_GRAD_NORM = 1.0

def main():

    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    print("BOREALLM TRAINING SMOKE TEST")
    print("=" * 60)

    print("Device:", device)

    model = BorealLM().to(device)

    _, train_loader = create_loader(
        TRAIN_PATH,
        CONTEXT_LENGTH,
        BATCH_SIZE,
        shuffle=True,
    )

    optimizer = AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=0.1,
    )

    x, y = next(iter(train_loader))

    x = x.to(device)
    y = y.to(device)

    print("Input shape:", x.shape)
    print("Target shape:", y.shape)

    model.train()

    optimizer.zero_grad(
        set_to_none=True
    )

    logits = model(x)

    print("Logits shape:", logits.shape)

    loss = F.cross_entropy(
        logits.reshape(
            -1,
            model.vocab_size,
        ),
        y.reshape(-1),
    )

    print(
        "Initial loss:",
        loss.item(),
    )

    if not torch.isfinite(loss):
        raise ValueError(
            "Loss is not finite."
        )

    loss.backward()

    gradient_norm = torch.nn.utils.clip_grad_norm_(
        model.parameters(),
        MAX_GRAD_NORM,
    )

    print(
        "Gradient norm before clipping:",
        gradient_norm.item(),
    )

    optimizer.step()

    print("Optimizer step: SUCCESS")

    optimizer.zero_grad(
        set_to_none=True
    )

    logits_after = model(x)

    loss_after = F.cross_entropy(
        logits_after.reshape(
            -1,
            model.vocab_size,
        ),
        y.reshape(-1),
    )

    print(
        "Loss after one update:",
        loss_after.item(),
    )

    print("\nTRAINING PIPELINE WORKING")

if __name__ == "__main__":
    main()