"""Fully-connected neural network."""

from jaxtyping import Float, jaxtyped
from torch import Tensor, nn
from typeguard import typechecked as typechecker


class FullyConnected(nn.Module):
    """Fully-connected neural network.

    Args:
        input_dim: Input dimension.
        hidden_layer_dims: Hidden layer dimensions.
        output_dim: Output dimension.
        negative_slope: Negative slope for leaky ReLU (default = 0.0).
    """

    def __init__(  # noqa: DCO010
        self,
        input_dim: int,
        hidden_layer_dims: list[int],
        output_dim: int,
        negative_slope: float = 0.0,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_layer_dims = hidden_layer_dims
        self.output_dim = output_dim
        self.negative_slope = negative_slope

        layers = []

        if not hidden_layer_dims:
            # Edge case: No hidden layers
            layers.append(nn.Linear(input_dim, output_dim))
            layers.append(nn.LeakyReLU(negative_slope))
        else:
            # Generic case: At least one hidden layer
            layers = []
            layers.append(nn.Linear(input_dim, hidden_layer_dims[0]))
            layers.append(nn.LeakyReLU(negative_slope))

            for i in range(1, len(hidden_layer_dims)):
                layers.append(nn.Linear(hidden_layer_dims[i - 1], hidden_layer_dims[i]))
                layers.append(nn.LeakyReLU(negative_slope))

            layers.append(nn.Linear(hidden_layer_dims[-1], output_dim))
            layers.append(nn.LeakyReLU(negative_slope))

        self.layers = nn.Sequential(*layers)

    @jaxtyped(typechecker=typechecker)
    def forward(self, x: Float[Tensor, "b input_dim"]) -> Float[Tensor, "b output_dim"]:
        """Compute network output.

        Args:
            x: Input tensor.

        Returns:
            Output tensor.
        """
        return self.layers(x)