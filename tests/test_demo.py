from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tools.play_demo import run_demo


class DemoTests(unittest.TestCase):
    def test_demo_finishes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            state = run_demo(seed=21, max_turns=600)
        self.assertTrue(state.is_terminal())
        self.assertGreaterEqual(len(state.finished), 2)

    def test_demo_writes_public_replay_trace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace_path = Path(directory) / "demo.json"
            with contextlib.redirect_stdout(io.StringIO()):
                state = run_demo(seed=21, max_turns=600, trace_path=trace_path)

            replay = json.loads(trace_path.read_text(encoding="utf-8"))
            self.assertEqual(replay["schema_version"], 1)
            self.assertEqual(replay["game"], "guandan")
            self.assertEqual(replay["seed"], 21)
            self.assertEqual(replay["initial"]["hand_sizes"], [27, 27, 27, 27])
            self.assertEqual(replay["result"]["finish_order"], list(state.finish_order()))
            self.assertEqual(replay["result"]["team_scores"]["0"], state.team_score(0))
            self.assertGreater(len(replay["turns"]), 0)

            first_turn = replay["turns"][0]
            self.assertEqual(first_turn["turn"], 1)
            self.assertEqual(first_turn["player"], 0)
            self.assertIn("action", first_turn)
            self.assertIn("before", first_turn)
            self.assertIn("after", first_turn)


if __name__ == "__main__":
    unittest.main()
