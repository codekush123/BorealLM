import torch
import torch.nn as nn

from embeddings import TokenAndPositionEmbedding
from transformer_block import TransformerBlock


class BorealLM(nn.Module):

    def __init__(
        self,
        vocab_size=4096,
        context_length=256,
        embedding_dim=256,
        num_heads=8,
        num_layers=10,
        hidden_dim=1024,
        dropout=0.1,
    ):

        super().__init__()

        self.vocab_size = vocab_size
        self.context_length = context_length

        self.embeddings = TokenAndPositionEmbedding(
            vocab_size=vocab_size,
            context_length=context_length,
            embedding_dim=embedding_dim,
        )

        self.blocks = nn.ModuleList([
            TransformerBlock(
                embedding_dim=embedding_dim,
                num_heads=num_heads,
                context_length=context_length,
                hidden_dim=hidden_dim,
                dropout=dropout,
            )
            for _ in range(num_layers)
        ])

        self.final_norm = nn.LayerNorm(
            embedding_dim
        )

        self.lm_head = nn.Linear(
            embedding_dim,
            vocab_size,
        )

    def forward(self, token_ids):

        x = self.embeddings(token_ids)

        for block in self.blocks:
            x = block(x)

        x = self.final_norm(x)

        logits = self.lm_head(x)

        return logits


def count_parameters(model):

    total = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    trainable = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    return total, trainable


def main():

    model = BorealLM()

    total, trainable = count_parameters(
        model
    )

    print("BOREALLM MODEL")
    print("=" * 60)

    print("Vocabulary size:", model.vocab_size)
    print("Context length:", model.context_length)

    print(
        "Total parameters:",
        f"{total:,}",
    )

    print(
        "Trainable parameters:",
        f"{trainable:,}",
    )

    print(
        "Model size:",
        f"{total / 1_000_000:.2f}M parameters",
    )

    token_ids = torch.randint(
        low=0,
        high=model.vocab_size,
        size=(2, 256),
    )

    model.eval()

    with torch.no_grad():
        logits = model(token_ids)

    print("\nFORWARD PASS")
    print("-" * 60)

    print(
        "Input shape:",
        token_ids.shape,
    )

    print(
        "Logits shape:",
        logits.shape,
    )


if __name__ == "__main__":
    main()