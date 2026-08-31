import argparse
import json
import sys

from .generator import TransactionGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic FraudStream transactions")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--fraud-rate", type=float, default=0.05)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--output", help="Write JSONL to a file instead of stdout")
    args = parser.parse_args()
    output = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    try:
        generator = TransactionGenerator(fraud_rate=args.fraud_rate, seed=args.seed)
        for transaction in generator.generate(args.count):
            output.write(json.dumps(transaction.as_event()) + "\n")
    finally:
        if args.output:
            output.close()


if __name__ == "__main__":
    main()

