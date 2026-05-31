from __future__ import annotations

import argparse
import csv
import glob
from pathlib import Path
from typing import Any


def summarize_gate(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Gate file is empty: {path}")

    team_wins: dict[int, list[bool]] = {0: [], 1: []}
    scores: list[float] = []
    for row in rows:
        team = int(row["candidate_team"])
        if team not in team_wins:
            raise ValueError(f"Unexpected candidate_team {team!r} in {path}")
        won = row["candidate_win"].lower() == "true"
        team_wins[team].append(won)
        scores.append(float(row["candidate_score"]))

    if not team_wins[0] or not team_wins[1]:
        raise ValueError(f"Gate file must contain both candidate teams: {path}")
    wins = sum(won for values in team_wins.values() for won in values)
    team_rates = [
        sum(values) / len(values)
        for values in (team_wins[0], team_wins[1])
    ]
    return {
        "games": len(rows),
        "wins": wins,
        "win_rate": wins / len(rows),
        "seat_gap": abs(team_rates[0] - team_rates[1]),
        "average_score": sum(scores) / len(scores),
    }


def expand_paths(patterns: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        matches = [Path(match) for match in sorted(glob.glob(str(pattern)))]
        paths.extend(matches or [pattern])
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize sanitized paired-gate CSV files.")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    for path in expand_paths(args.paths):
        summary = summarize_gate(path)
        print(
            f"{path}: games={summary['games']} wins={summary['wins']} "
            f"win_rate={summary['win_rate']:.3f} seat_gap={summary['seat_gap']:.3f} "
            f"average_score={summary['average_score']:.3f}"
        )


if __name__ == "__main__":
    main()
