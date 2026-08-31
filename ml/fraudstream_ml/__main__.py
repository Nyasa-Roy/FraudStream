import argparse

from .training import train_baseline


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the FraudStream logistic baseline")
    parser.add_argument("--count", type=int, default=10_000)
    parser.add_argument("--fraud-rate", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="ml/models/fraud-logistic-v1.joblib")
    args = parser.parse_args()
    model = train_baseline(args.count, args.fraud_rate, args.seed)
    model.save(args.output)
    print(model.metrics)


if __name__ == "__main__":
    main()

