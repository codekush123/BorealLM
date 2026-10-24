import torch
import torch.nn as nn

class TokenAndPositionEmbedding(nn.Module):
    def __init__(self, vocab_size, context_length, embedding_dim):
        super().__init__()

        self.token_embedding = nn.Embedding(
            vocab_size, embedding_dim
        )

        self.position_embedding = nn.Embedding(
            context_length,
            embedding_dim,
        )

    def forward(self, token_ids):
        batch_size, sequence_length = token_ids.shape

        if sequence_length > self.position_embedding.num_embeddings:
            raise ValueError(
                "Sequence length exceeds configured contex length."
            )

        token_vectors = self.token_embedding(
            token_ids
        )

        positions = torch.arange(
            sequence_length,
            device=token_ids.device,
        )

        position_vectors = self.position_embedding(
            positions
        )

        x = token_vectors + position_vectors

        return x


def main():

    vocab_size = 4096
    context_length = 256
    embedding_dim = 256

    model = TokenAndPositionEmbedding(
        vocab_size=vocab_size,
        context_length=context_length,
        embedding_dim=embedding_dim,
    )

    token_ids = torch.randint(
        low=0,
        high=vocab_size,
        size=(8, 256),
    )

    output = model(token_ids)

    print("BOREALLM EMBEDDING TEST")
    print("=" * 50)

    print("Input shape:", token_ids.shape)
    print("Output shape:", output.shape)

    print(
        "Embedding parameters:",
        sum(
            parameter.numel()
            for parameter in model.parameters()
        ),
    )


if __name__ == "__main__":
    main()