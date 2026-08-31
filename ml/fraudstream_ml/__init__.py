"""Training and evaluation utilities for FraudStream models."""

from .dataset import build_dataset
from .training import BaselineModel, train_baseline

__all__ = ["BaselineModel", "build_dataset", "train_baseline"]

