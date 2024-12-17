"""Demo loss-per-learning-rate."""

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import nn

from examples.common import set_seed
from examples.fully_connected.fully_connected import FullyConnected
from learning_rate_utils import loss_per_learning_rate


def run_demo() -> None:
    """Run demo for a fully-connected neural network."""
    learning_rates = np.linspace(0.0, 5.0, 100)
    num_plots = 10
    losses = np.ndarray((len(learning_rates), num_plots))

    batch_size = 16
    input_dim = 8
    hidden_layer_dims = [64, 32, 16, 8]
    output_dim = 4
    negative_slope = 0.01

    # Make fully-connected model
    model = FullyConnected(input_dim, hidden_layer_dims, output_dim, negative_slope)

    # Make MSE criterion
    criterion = nn.MSELoss()

    # Make standard gradient descent optimizer
    optimizer = torch.optim.SGD(model.parameters())

    # Model parameters are fixed; make new dummy data for each plot
    for i in range(num_plots):
        x = 10.0 * torch.randn(batch_size, input_dim)  # Constant factor for larger errors
        y = torch.randn(batch_size, output_dim)
        losses[:, i] = loss_per_learning_rate(model, criterion, optimizer, x, y, learning_rates)

    # Plot losses
    fig, ax = plt.subplots()
    ax.plot(learning_rates, losses)
    ax.set_xlabel("learning rate")
    ax.set_ylabel("loss")
    ax.set_title("Loss per learning rate (fully-connected, untrained)")

    fig.tight_layout()

    plt.show()


if __name__ == "__main__":
    set_seed(11)
    plt.rcParams["text.usetex"] = True
    run_demo()