-- FraudStream persistence contract. Safe to run once on a fresh database.
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(32) PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL REFERENCES users(id),
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    merchant_id VARCHAR(32) NOT NULL,
    merchant_category VARCHAR(64) NOT NULL,
    location VARCHAR(128) NOT NULL,
    device_id VARCHAR(32) NOT NULL,
    payment_method VARCHAR(32) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_time
    ON transactions (user_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_occurred_at
    ON transactions (occurred_at DESC);

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id VARCHAR(32) PRIMARY KEY REFERENCES users(id),
    avg_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    usual_location VARCHAR(128),
    usual_device VARCHAR(32),
    transaction_count INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fraud_predictions (
    id BIGSERIAL PRIMARY KEY,
    transaction_id VARCHAR(32) NOT NULL UNIQUE REFERENCES transactions(id),
    model_version VARCHAR(64) NOT NULL,
    fraud_probability DOUBLE PRECISION NOT NULL CHECK (fraud_probability BETWEEN 0 AND 1),
    anomaly_score DOUBLE PRECISION NOT NULL CHECK (anomaly_score BETWEEN 0 AND 1),
    risk_score DOUBLE PRECISION NOT NULL CHECK (risk_score BETWEEN 0 AND 1),
    risk_level VARCHAR(16) NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fraud_alerts (
    id BIGSERIAL PRIMARY KEY,
    transaction_id VARCHAR(32) NOT NULL UNIQUE REFERENCES transactions(id),
    risk_score DOUBLE PRECISION NOT NULL CHECK (risk_score BETWEEN 0 AND 1),
    status VARCHAR(16) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'RESOLVED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS model_versions (
    id BIGSERIAL PRIMARY KEY,
    version VARCHAR(64) NOT NULL UNIQUE,
    model_type VARCHAR(64) NOT NULL,
    dataset_version VARCHAR(64) NOT NULL,
    precision_score DOUBLE PRECISION,
    recall_score DOUBLE PRECISION,
    f1_score DOUBLE PRECISION,
    pr_auc DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

