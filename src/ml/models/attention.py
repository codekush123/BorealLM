import math

import torch
import torch.nn as nn
import torch.nn.functional as F

class CausalSelfAttention(nn.Module):
    def __init__(
        self,
        embedding_dim,
        num_heads,
        context_length,
        dropout=0.1,
    ):

        super().__init__()

        if embedding_dim % num_heads != 0:
            raise ValueError(
                "embedding_dim must be divisible by num_heads."
            )

        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.head_dim = embedding_dim // num_heads

        self.qkv_projection = nn.Linear(
            embedding_dim,
            3 * embedding_dim,
        )

        self.output_projection = nn.Linear(
            embedding_dim,
            embedding_dim,
        )

        self.attention_dropout = nn.Dropout(
            dropout
        )

        self.output_dropout = nn.Dropout(
            dropout
        )

        causal_mask = torch.triu(
            torch.ones(
                context_length,
                context_length,
                dtype=torch.bool,
            ),
            diagonal=1,
        )

        self.register_buffer(
            "causal_mask",
            causal_mask,
            persistent=False,
        )

    def forward(self, x):

        batch_size, sequence_length, embedding_dim = x.shape

        if sequence_length > self.causal_mask.size(0):
            raise ValueError(
                "Sequence length exceeds configured context length."
            )

        qkv = self.qkv_projection(x)

        query, key, value = qkv.chunk(
            3,
            dim=-1,
        )

        query = query.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim,
        ).transpose(1, 2)

        key = key.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim,
        ).transpose(1, 2)

        value = value.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim,
        ).transpose(1, 2)

        attention_scores = (
            query @ key.transpose(-2, -1)
        ) / math.sqrt(self.head_dim)

        mask = self.causal_mask[
            :sequence_length,
            :sequence_length,
        ]

        attention_scores = attention_scores.masked_fill(
            mask,
            float("-inf"),
        )

        attention_weights = F.softmax(
            attention_scores,
            dim=-1,
        )

        attention_weights = self.attention_dropout(
            attention_weights
        )

        output = attention_weights @ value


        output = output.transpose(
            1,
            2,
        ).contiguous()

        output = output.view(
            batch_size,
            sequence_length,
            embedding_dim,
        )

        output = self.output_projection(
            output
        )

        output = self.output_dropout(
            output
        )

        return output

def main():

    embedding_dim = 256
    num_heads = 8
    context_length = 256

    attention = CausalSelfAttention(
        embedding_dim=embedding_dim,
        num_heads=num_heads,
        context_length=context_length,
        dropout=0.1,
    )

    x = torch.randn(
        8,
        context_length,
        embedding_dim,
    )

    output = attention(x)

    print("BOREALLM ATTENTION TEST")
    print("=" * 50)

    print("Input shape:", x.shape)
    print("Output shape:", output.shape)

    parameters = sum(
        parameter.numel()
        for parameter in attention.parameters()
    )

    print(
        "Attention parameters:",
        parameters,
    )

    attention.eval()

    test_a = torch.randn(
        1,
        8,
        embedding_dim,
    )

    test_b = test_a.clone()

    test_b[:, 4:, :] = torch.randn_like(
        test_b[:, 4:, :]
    )

    with torch.no_grad():

        output_a = attention(test_a)
        output_b = attention(test_b)

    causal_test = torch.allclose(
        output_a[:, :4, :],
        output_b[:, :4, :],
        atol=1e-6,
    )

    print(
        "Causal mask working:",
        causal_test,
    )

if __name__ == "__main__":
    main()