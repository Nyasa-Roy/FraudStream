from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from .dataset import build_dataset


ANOMALY_COLUMNS = ["amount", "amount_log", "hour", "day_of_week"]


@dataclass
class AnomalyModel:
    model: IsolationForest
    version: str = "fraud-isolation-v1"

    def score(self, features: pd.DataFrame) -> list[float]:
        """Return larger values for more anomalous observations."""
        raw = -self.model.score_samples(features[ANOMALY_COLUMNS])
        low, high = float(raw.min()), float(raw.max())
        if high == low:
            return [0.0] * len(raw)
        return ((raw - low) / (high - low)).clip(0, 1).tolist()

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)


def train_anomaly_model(count: int = 10_000, seed: int = 42) -> AnomalyModel:
    features, _ = build_dataset(count, fraud_rate=0.05, seed=seed)
    model = IsolationForest(n_estimators=150, contamination="auto", random_state=seed)
    model.fit(features[ANOMALY_COLUMNS])
    return AnomalyModel(model)
