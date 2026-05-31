from __future__ import annotations

from typing import Any

from .rules import Action
from .state import GameState

REPLAY_SCHEMA_VERSION = 1


def action_record(action: Action | None) -> dict[str, Any] | None:
    if action is None:
        return None
    return {
        "type": action.type.value,
        "cards": [card.code() for card in action.cards],
        "main_rank": None if action.main_rank is None else action.main_rank.value,
        "length": action.length,
        "suit": None if action.suit is None else action.suit.value,
    }


def public_state_record(state: GameState) -> dict[str, Any]:
    return {
        "current_player": state.current_player,
        "last_actor": state.last_actor,
        "last_action": action_record(state.last_action),
        "consecutive_passes": state.consecutive_passes,
        "hand_sizes": [len(hand) for hand in state.hands],
        "finished": list(state.finished),
    }


def turn_record(turn: int, state: GameState, action: Action, next_state: GameState) -> dict[str, Any]:
    return {
        "turn": turn,
        "player": state.current_player,
        "action": action_record(action),
        "before": public_state_record(state),
        "after": public_state_record(next_state),
    }


def replay_record(seed: int, initial_state: GameState, turns: list[dict[str, Any]], final_state: GameState) -> dict[str, Any]:
    return {
        "schema_version": REPLAY_SCHEMA_VERSION,
        "game": "guandan",
        "seed": seed,
        "rule_config": {
            "level_rank": initial_state.config.level_rank.value,
            "wild_suit": initial_state.config.wild_suit.value,
        },
        "initial": public_state_record(initial_state),
        "turns": turns,
        "result": {
            "finish_order": list(final_state.finish_order()),
            "team_scores": {
                "0": final_state.team_score(0),
                "1": final_state.team_score(1),
            },
        },
    }
