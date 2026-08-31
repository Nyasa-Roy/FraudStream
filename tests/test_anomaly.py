from fraudstream_ml import build_dataset, train_anomaly_model


def test_anomaly_model_returns_bounded_scores():
    model = train_anomaly_model(300, seed=12)
    features, _ = build_dataset(20, seed=13)
    scores = model.score(features)
    assert len(scores) == 20
    assert all(0 <= score <= 1 for score in scores)
    assert max(scores) > min(scores)

