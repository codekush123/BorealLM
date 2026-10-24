import torch
import torch.nn as nn


class FeedForward(nn.Module):

    def __init__(
        self,
        embedding_dim,
        hidden_dim,
        dropout=0.1,
    ):

        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(
                embedding_dim,
                hidden_dim,
            ),

            nn.GELU(),

            nn.Linear(
                hidden_dim,
                embedding_dim,
            ),

            nn.Dropout(
                dropout
            ),
        )

    def forward(self, x):

        return self.network(x)

def main():

    embedding_dim = 256
    hidden_dim = 1024

    model = FeedForward(
        embedding_dim=embedding_dim,
        hidden_dim=hidden_dim,
        dropout=0.1,
    )

    x = torch.randn(
        8,
        256,
        embedding_dim,
    )

    output = model(x)

    print("BOREALLM FEED-FORWARD TEST")
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
        for parameter in model.parameters()
    )

    print(
        "Feed-forward parameters:",
        parameter_count,
    )


if __name__ == "__main__":
    main()