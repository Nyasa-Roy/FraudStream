import pytest

from stream_processor.fraudstream_processor.risk import RiskEngine


def test_risk_engine_combines_scores_and_explains_features():
    assessment = RiskEngine().assess(0.8, 0.9, {
        "amount_ratio": 12, "new_device": True, "new_location": True,
        "new_merchant": False, "time_since_previous_transaction": 20,
    })
    assert assessment.risk_score == 0.83
    assert assessment.risk_level == "HIGH"
    assert len(assessment.reasons) == 4


def test_risk_engine_rejects_invalid_configuration_and_scores():
    with pytest.raises(ValueError):
        RiskEngine(fraud_weight=0.5, anomaly_weight=0.6)
    with pytest.raises(ValueError):
        RiskEngine().assess(1.2, 0.1)


def test_low_risk_has_no_false_explanation():
    assessment = RiskEngine().assess(0.05, 0.1, {})
    assert assessment.risk_level == "LOW"
    assert assessment.reasons == ()

