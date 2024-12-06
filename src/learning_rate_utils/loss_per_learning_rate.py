"""Compute loss per learning rate."""

import copy
from typing import Union

import torch
from jaxtyping import Float, Integer, jaxtyped
from torch import Tensor, nn
from typeguard import typechecked as typechecker

_OutputDataType = Union[Float[Tensor, "b ..."], Integer[Tensor, "b ..."]]


@jaxtyped(typechecker=typechecker)
def loss_per_learning_rate(
    model: nn.Module,
    x: Float[Tensor, "b ..."],
    y: _OutputDataType,
    criterion: torch.nn.modules.loss._Loss,
    optimizer: torch.optim.Optimizer,
    learning_rates: list[float],
    init_gradients: bool = True,
) -> list[float]:
    """Compute loss per learning rate.

    This function computes the loss values which would result from using
    each learning rate in specified set of learning rates, at a single step
    of gradient descent.

    Args:
        model: Network model.
        x: Input tensor.
        y: Output tensor.
        criterion: Loss criterion.
        optimizer: Optimizer for each trainable parameter in `model`.  The
            only constraint on `optimizer` is that each of its parameter groups
            uses the `lr` key for the learning rate.
        learning_rates: List of learning rates (must be non-empty).
        init_gradients: Run initial gradient computation (default = `True`).

    Returns:
        The loss values for each learning rate in `learning_rates`.

    Raises:
        ValueError: If any arguments are invalid.

    Note:
        No modification is made to the state of `model` unless `init_gradients`
        is `True`.  In this case, we set the parameter gradients of `model`.

    Note:
        No modification is made to the state of `optimizer`.
    """
    # Sanity check on `learning_rates` argument
    if not learning_rates:
        raise ValueError("learning_rates is empty")

    # Sanity check on `optimizer` argument
    for param_group in optimizer.param_groups:
        if "lr" not in param_group:
            raise ValueError("optimizer is missing lr key")

    losses = [None] * len(learning_rates)

    # Compute initial parameter gradients, if required
    if init_gradients:
        y_hat = model(x)
        loss = criterion(y_hat, y)
        loss.backward()

    # Save model and optimizer states
    model_state_dict = copy.deepcopy(model.state_dict())
    optimizer_state_dict = copy.deepcopy(optimizer.state_dict())

    for i, learning_rate in enumerate(learning_rates):
        # Update learning rate in each parameter group
        for param_group in optimizer.param_groups:
            param_group["lr"] = learning_rate

        # Update parameters
        optimizer.step()

        # Compute loss with updated parameters
        with torch.no_grad():
            new_y_hat = model(x)
            new_loss = criterion(new_y_hat, y)
            losses[i] = new_loss.item()

        # Restore model and optimizer states
        # - In particular, this restores parameter gradients computed earlier
        model.load_state_dict(model_state_dict)
        optimizer.load_state_dict(optimizer_state_dict)

    return losses
