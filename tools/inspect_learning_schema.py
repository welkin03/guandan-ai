from __future__ import annotations

import argparse
import json
from pathlib import Path

from guandan.learning import (
    describe_architectures,
    describe_training_milestones,
    validate_policy_value_record,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect public Guandan AI learning metadata.")
    parser.add_argument(
        "--records",
        type=Path,
        default=Path("examples/training/policy_value_records.jsonl"),
        help="JSONL file using the public policy/value record schema.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    records = load_records(args.records)
    errors = validate_records(records)
    summary = {
        "architectures": describe_architectures(),
        "milestones": describe_training_milestones(),
        "record_file": str(args.records),
        "records": len(records),
        "schema_errors": errors,
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return

    print("Architectures:")
    for architecture in summary["architectures"]:
        print(f"- {architecture['name']}: {architecture['visibility']}")
    print("\nTraining milestones:")
    for milestone in summary["milestones"]:
        print(f"- {milestone['date']} {milestone['route']}: {milestone['outcome']}")
    print(f"\nRecords checked: {len(records)} from {args.records}")
    if errors:
        print("Schema errors:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("Schema check: ok")


def load_records(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def validate_records(records: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(records, start=1):
        for error in validate_policy_value_record(record):
            errors.append(f"line {index}: {error}")
    return errors


if __name__ == "__main__":
    main()
