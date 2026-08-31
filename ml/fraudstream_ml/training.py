from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .dataset import CATEGORICAL_FEATURES, NUMERIC_FEATURES, build_dataset


@dataclass
class BaselineModel:
    pipeline: Pipeline
    metrics: dict[str, float]
    version: str = "fraud-logistic-v1"

    def predict_probability(self, features: pd.DataFrame) -> list[float]:
        return self.pipeline.predict_proba(features)[:, 1].tolist()

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        path.with_suffix(".json").write_text(json.dumps({
            "version": self.version, "model_type": "logistic_regression", "metrics": self.metrics,
        }, indent=2), encoding="utf-8")


def train_baseline(count: int = 10_000, fraud_rate: float = 0.05,
                   seed: int = 42) -> BaselineModel:
    features, labels = build_dataset(count, fraud_rate, seed)
    split = int(len(features) * 0.8)
    train_x, test_x = features.iloc[:split], features.iloc[split:]
    train_y, test_y = labels.iloc[:split], labels.iloc[split:]
    preprocess = ColumnTransformer([
        ("numeric", StandardScaler(), list(NUMERIC_FEATURES)),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), list(CATEGORICAL_FEATURES)),
    ])
    pipeline = Pipeline([("preprocess", preprocess),
                         ("classifier", LogisticRegression(max_iter=500, class_weight="balanced"))])
    pipeline.fit(train_x, train_y)
    probabilities = pipeline.predict_proba(test_x)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    metrics: dict[str, float] = {
        "precision": precision_score(test_y, predictions, zero_division=0),
        "recall": recall_score(test_y, predictions, zero_division=0),
        "f1": f1_score(test_y, predictions, zero_division=0),
        "pr_auc": average_precision_score(test_y, probabilities),
        "roc_auc": roc_auc_score(test_y, probabilities),
    }
    return BaselineModel(pipeline, metrics)


def benchmark_inference(model: BaselineModel, features: pd.DataFrame) -> dict[str, float]:
    start = time.perf_counter()
    model.predict_probability(features)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {"rows": float(len(features)), "total_ms": elapsed_ms,
            "per_row_ms": elapsed_ms / len(features) if len(features) else 0.0}

