from __future__ import annotations

import argparse

from guandan import GameState, Rank, RuleConfig, deal, heuristic_policy


def run_demo(seed: int, max_turns: int) -> GameState:
    state = GameState(
        hands=deal(seed=seed),
        current_player=0,
        config=RuleConfig(level_rank=Rank.TWO),
    )

    for turn in range(1, max_turns + 1):
        if state.is_terminal():
            return state
        action = heuristic_policy(state)
        print(
            f"{turn:03d} P{state.current_player}: "
            f"{action.type.value:<16} {' '.join(card.code() for card in action.cards) or 'PASS'}"
        )
        state = state.play_action(action)

    raise RuntimeError(f"Demo exceeded {max_turns} turns")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic Guandan heuristic self-play.")
    parser.add_argument("--seed", type=int, default=21)
    parser.add_argument("--max-turns", type=int, default=600)
    args = parser.parse_args()

    state = run_demo(seed=args.seed, max_turns=args.max_turns)
    print(f"finish order: {state.finish_order()}")
    print(f"team 0 score: {state.team_score(0)}")
    print(f"team 1 score: {state.team_score(1)}")


if __name__ == "__main__":
    main()
