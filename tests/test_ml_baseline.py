from fraudstream_ml import build_dataset, train_baseline
from fraudstream_ml.training import benchmark_inference


def test_dataset_is_reproducible_and_labelled():
    first = build_dataset(100, seed=9)
    second = build_dataset(100, seed=9)
    assert first[0].equals(second[0])
    assert first[1].equals(second[1])
    assert set(first[1].unique()) == {0, 1}


def test_baseline_trains_and_reports_imbalanced_metrics():
    model = train_baseline(500, fraud_rate=0.2, seed=9)
    assert set(model.metrics) == {"precision", "recall", "f1", "pr_auc", "roc_auc"}
    assert all(0 <= value <= 1 for value in model.metrics.values())
    features, _ = build_dataset(10, seed=10)
    assert benchmark_inference(model, features)["rows"] == 10

