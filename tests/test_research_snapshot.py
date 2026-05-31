from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from tools.summarize_gate_csv import expand_paths, summarize_gate

ROOT = Path(__file__).resolve().parents[1]


class ResearchSnapshotTests(unittest.TestCase):
    def test_selected_gate_rows_match_published_summaries(self) -> None:
        summary_path = ROOT / "research" / "selected_gate_results.csv"
        with summary_path.open(encoding="utf-8", newline="") as handle:
            published = list(csv.DictReader(handle))

        self.assertEqual(len(published), 8)
        self.assertEqual(sum(int(row["games"]) for row in published), 1280)
        for row in published:
            summary = summarize_gate(ROOT / "research" / row["file"])
            self.assertEqual(summary["games"], int(row["games"]))
            self.assertEqual(summary["wins"], int(row["wins"]))
            self.assertAlmostEqual(summary["win_rate"], float(row["win_rate"]), places=3)
            self.assertAlmostEqual(summary["seat_gap"], float(row["seat_gap"]), places=3)
            self.assertAlmostEqual(summary["average_score"], float(row["average_score"]), places=3)

    def test_gate_rows_are_sanitized(self) -> None:
        for path in (ROOT / "research" / "gates").glob("*.csv"):
            with path.open(encoding="utf-8", newline="") as handle:
                fields = csv.DictReader(handle).fieldnames
            self.assertNotIn("seed", fields)
            self.assertNotIn("path", fields)

    def test_gate_summary_tool_expands_wildcards(self) -> None:
        paths = expand_paths([ROOT / "research" / "gates" / "*.csv"])
        self.assertEqual(len(paths), 8)

    def test_example_replays_omit_private_hands(self) -> None:
        replay_paths = sorted((ROOT / "examples" / "replays").glob("*.json"))
        self.assertEqual(len(replay_paths), 3)
        for path in replay_paths:
            replay = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(replay["schema_version"], 1)
            self.assertGreater(len(replay["turns"]), 0)
            self.assertNotIn("hands", json.dumps(replay))


if __name__ == "__main__":
    unittest.main()
