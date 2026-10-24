import sys
from pathlib import Path
import torch
from tokenizers import Tokenizer
PROJECT_ROOT = Path(__file__).resolve().parents[3]


MODEL_DIR = (
    PROJECT_ROOT
    / "src"
    / "ml"
    / "models"
)

sys.path.insert(
    0,
    str(MODEL_DIR),
)
from boreallm import BorealLM

CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "checkpoints"
    / "boreallm_v1_3epoch_best.pt"
)

TOKENIZER_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "tokenizer"
    / "borealam_bpe_v1.json"
)

PROMPT = "Laser powder bed fusion"

MAX_NEW_TOKENS = 80

TEMPERATURE = 0.8

TOP_K = 50

def get_device():

    if torch.cuda.is_available():
        return torch.device("cuda")

    if (
        hasattr(torch.backends, "mps")
        and torch.backends.mps.is_available()
    ):
        return torch.device("mps")

    return torch.device("cpu")


def load_model(
        checkpoint_path,
        device,
):

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
    )

    config = checkpoint[
        "model_config"
    ]

    model = BorealLM(
        **config
    )

    model.load_state_dict(
        checkpoint[
            "model_state_dict"
        ]
    )

    model.to(device)

    model.eval()

    return model, checkpoint

def sample_next_token(
        logits,
        temperature,
        top_k,
):
    if temperature <= 0:
        raise ValueError(
            "temperature must be greater than zero."
        )

    logits = logits / temperature

    if top_k is not None:

        top_k = min(
            top_k,
            logits.size(-1),
        )

        values, _ = torch.topk(
            logits,
            top_k,
        )

        threshold = values[
            :, -1
        ].unsqueeze(-1)

        logits = logits.masked_fill(
            logits < threshold,
            float("-inf"),
        )

    probabilities = torch.softmax(
        logits,
        dim=-1,
    )

    next_token = torch.multinomial(
        probabilities,
        num_samples=1,
    )

    return next_token

@torch.no_grad()
def generate(
    model,
    tokenizer,
    prompt,
    device,
    max_new_tokens,
    temperature,
    top_k,
):

    encoding = tokenizer.encode(
        prompt
    )

    token_ids = encoding.ids

    if not token_ids:
        raise ValueError(
            "Prompt produced no tokens."
        )

    generated = torch.tensor(
        [token_ids],
        dtype=torch.long,
        device=device,
    )

    eos_id = tokenizer.token_to_id(
        "[EOS]"
    )

    for _ in range(
        max_new_tokens
    ):

        context = generated[
            :,
            -model.context_length:,
        ]

        logits = model(
            context
        )

        next_token_logits = logits[
            :,
            -1,
            :
        ]

        next_token = sample_next_token(
            next_token_logits,
            temperature,
            top_k,
        )

        generated = torch.cat(
            [
                generated,
                next_token
            ],
            dim=1,
        )

        if (
            eos_id is not None
            and next_token.item() == eos_id
        ):
            break


    output_ids = (
        generated[0]
        .detach()
        .cpu()
        .tolist()
    )

    text = tokenizer.decode(
        output_ids,
        skip_special_tokens = True,
    )

    return text, output_ids

def main():
    device = get_device()

    tokenizer = Tokenizer.from_file(
        str(TOKENIZER_PATH)
    )

    model, checkpoint = load_model(
        CHECKPOINT_PATH,
        device,
    )

    print("BOREALLM GENERATION")
    print("=" * 60)

    print("Device:", device)

    print(
        "Checkpoint epoch:",
        checkpoint["epoch"],
    )

    print(
        "Validation loss:",
        round(
            checkpoint[
                "validation_loss"
            ],
            4,
        ),
    )

    print(
        "Prompt:",
        PROMPT,
    )

    print(
        "Temperature:",
        TEMPERATURE,
    )

    print(
        "Top-k:",
        TOP_K,
    )

    generated_text, token_ids = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=PROMPT,
        device=device,
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        top_k=TOP_K,
    )

    print("\nGENERATED TEXT")
    print("-" * 60)

    print(
        generated_text
    )

    print("\nGENERATION STATS")
    print("-" * 60)

    print(
        "Total tokens:",
        len(token_ids),
    )


if __name__ == "__main__":
    main()
    