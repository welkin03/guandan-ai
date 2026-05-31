from __future__ import annotations

import contextlib
import io
import unittest

from tools.play_demo import run_demo


class DemoTests(unittest.TestCase):
    def test_demo_finishes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            state = run_demo(seed=21, max_turns=600)
        self.assertTrue(state.is_terminal())
        self.assertGreaterEqual(len(state.finished), 2)


if __name__ == "__main__":
    unittest.main()
