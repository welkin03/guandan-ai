from __future__ import annotations

import csv
import json
import re
import unittest
from pathlib import Path

from tools.summarize_gate_csv import expand_paths, summarize_gate
from guandan.learning import (
    describe_architectures,
    describe_training_milestones,
    validate_policy_value_record,
)

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

    def test_public_research_ledgers_have_expected_shape(self) -> None:
        with (ROOT / "research" / "experiment_decisions.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            decisions = list(csv.DictReader(handle))
        with (ROOT / "research" / "distributed_runs.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            distributed = list(csv.DictReader(handle))
        with (ROOT / "research" / "v45_teacher_progress.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            teacher_progress = list(csv.DictReader(handle))
        with (ROOT / "research" / "v45_student_followups.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            student_followups = list(csv.DictReader(handle))
        with (ROOT / "research" / "neural_training_milestones.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            neural_milestones = list(csv.DictReader(handle))

        self.assertGreaterEqual(len(decisions), 10)
        self.assertGreaterEqual(len(distributed), 6)
        self.assertGreaterEqual(len(teacher_progress), 20)
        self.assertGreaterEqual(len(student_followups), 5)
        self.assertGreaterEqual(len(neural_milestones), 7)
        self.assertGreaterEqual(
            {row["outcome"] for row in decisions},
            {"rejected", "correctness_fix"},
        )
        self.assertTrue(all(int(row["nodes"]) in {2, 3} for row in distributed))

    def test_recent_v45_progress_summaries_match_public_doc(self) -> None:
        with (ROOT / "research" / "v45_teacher_progress.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        total = next(
            row
            for row in rows
            if row["stage"] == "targeted_pass_refine_sweep57"
            and row["opponent"] == "total"
        )
        self.assertEqual(int(total["wins"]), 166)
        self.assertEqual(int(total["games"]), 192)
        self.assertAlmostEqual(float(total["win_rate"]), 0.8646, places=4)

        with (ROOT / "research" / "v45_student_followups.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            followups = list(csv.DictReader(handle))
        decisions = {row["decision"] for row in followups}
        self.assertIn("valid_offline_distillation_artifact", decisions)
        self.assertIn("reject_expansion_cross_opponent_veto", decisions)

    def test_learning_architecture_metadata_and_examples(self) -> None:
        architectures = describe_architectures()
        milestones = describe_training_milestones()
        self.assertGreaterEqual(len(architectures), 3)
        self.assertGreaterEqual(len(milestones), 7)
        names = {item["name"] for item in architectures}
        self.assertIn("public_policy_value_candidate_scorer", names)
        self.assertIn("full_info_outcome_oracle_teacher", names)

        records_path = ROOT / "examples" / "training" / "policy_value_records.jsonl"
        with records_path.open(encoding="utf-8") as handle:
            records = [json.loads(line) for line in handle if line.strip()]
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertEqual(validate_policy_value_record(record), [])

    def test_public_research_narrative_is_anonymized(self) -> None:
        paths = [
            ROOT / "docs" / "ENGINEERING_LESSONS.md",
            ROOT / "docs" / "DISTRIBUTED_RESEARCH.md",
            ROOT / "docs" / "RECENT_PROGRESS_2026_06.md",
            ROOT / "docs" / "NEURAL_ARCHITECTURE.md",
            ROOT / "research" / "experiment_decisions.csv",
            ROOT / "research" / "distributed_runs.csv",
            ROOT / "research" / "v45_teacher_progress.csv",
            ROOT / "research" / "v45_student_followups.csv",
            ROOT / "research" / "neural_training_milestones.csv",
            ROOT / "examples" / "training" / "README.md",
            ROOT / "examples" / "training" / "policy_value_records.jsonl",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in paths)

        prohibited = [
            r"\b" + "PI" + "NK" + r"\b",
            r"\b" + "H" + "K" + r"[_-]",
            r"[A-Za-z]:\\",
            "/" + "Users/",
            "remote" + "_jobs",
            r"\b" + "fi" + "na" + "@",
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        ]
        for pattern in prohibited:
            self.assertIsNone(re.search(pattern, text, flags=re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
