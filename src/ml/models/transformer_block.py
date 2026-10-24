import torch
import torch.nn as nn

from attention import CausalSelfAttention
from feed_forward import FeedForward

class TransformerBlock(nn.Module):

    def __init__(
        self,
        embedding_dim,
        num_heads,
        context_length,
        hidden_dim,
        dropout=0.1,
    ):

        super().__init__()

        self.norm1 = nn.LayerNorm(
            embedding_dim
        )

        self.attention = CausalSelfAttention(
            embedding_dim=embedding_dim,
            num_heads=num_heads,
            context_length=context_length,
            dropout=dropout,
        )

        self.norm2 = nn.LayerNorm(
            embedding_dim
        )

        self.feed_forward = FeedForward(
            embedding_dim=embedding_dim,
            hidden_dim=hidden_dim,
            dropout=dropout,
        )

    def forward(self, x):

        x = x + self.attention(
            self.norm1(x)
        )

        x = x + self.feed_forward(
            self.norm2(x)
        )

        return x


def main():

    embedding_dim = 256
    num_heads = 8
    context_length = 256
    hidden_dim = 1024

    block = TransformerBlock(
        embedding_dim=embedding_dim,
        num_heads=num_heads,
        context_length=context_length,
        hidden_dim=hidden_dim,
        dropout=0.1,
    )

    x = torch.randn(
        8,
        context_length,
        embedding_dim,
    )

    output = block(x)

    print("BOREALLM TRANSFORMER BLOCK TEST")
    print("=" * 50)

    print(
        "Input shape:",
        x.shape,
    )

    print(
        "Output shape:",
        output.shape,
    )

    parameter_count = sum(
        parameter.numel()
        for parameter in block.parameters()
    )

    print(
        "Transformer block parameters:",
        parameter_count,
    )

    loss = output.mean()

    loss.backward()

    gradients_exist = all(
        parameter.grad is not None
        for parameter in block.parameters()
        if parameter.requires_grad
    )

    print(
        "Gradients working:",
        gradients_exist,
    )

if __name__ == "__main__":
    main()