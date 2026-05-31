from __future__ import annotations

import argparse
import json
from pathlib import Path

from guandan import GameState, Rank, RuleConfig, deal, heuristic_policy, replay_record, turn_record


def run_demo(seed: int, max_turns: int, trace_path: str | Path | None = None) -> GameState:
    state = GameState(
        hands=deal(seed=seed),
        current_player=0,
        config=RuleConfig(level_rank=Rank.TWO),
    )
    initial_state = state
    turns = []

    for turn in range(1, max_turns + 1):
        if state.is_terminal():
            if trace_path is not None:
                trace = replay_record(seed=seed, initial_state=initial_state, turns=turns, final_state=state)
                Path(trace_path).write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
            return state
        action = heuristic_policy(state)
        print(
            f"{turn:03d} P{state.current_player}: "
            f"{action.type.value:<16} {' '.join(card.code() for card in action.cards) or 'PASS'}"
        )
        next_state = state.play_action(action)
        turns.append(turn_record(turn=turn, state=state, action=action, next_state=next_state))
        state = next_state

    raise RuntimeError(f"Demo exceeded {max_turns} turns")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic Guandan heuristic self-play.")
    parser.add_argument("--seed", type=int, default=21)
    parser.add_argument("--max-turns", type=int, default=600)
    parser.add_argument("--trace", type=Path, help="Write a public JSON replay trace.")
    args = parser.parse_args()

    state = run_demo(seed=args.seed, max_turns=args.max_turns, trace_path=args.trace)
    print(f"finish order: {state.finish_order()}")
    print(f"team 0 score: {state.team_score(0)}")
    print(f"team 1 score: {state.team_score(1)}")


if __name__ == "__main__":
    main()
