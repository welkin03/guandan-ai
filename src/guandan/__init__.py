"""Core Guandan rules engine and heuristic AI."""

from .cards import Card, Rank, Suit, full_deck, parse_card, parse_cards
from .deal import deal, sample_hidden_hands
from .learning import describe_architectures, describe_training_milestones, validate_policy_value_record
from .policy import heuristic_policy
from .replay import REPLAY_SCHEMA_VERSION, action_record, public_state_record, replay_record, turn_record
from .rules import (
    PASS,
    Action,
    ActionType,
    RuleConfig,
    can_play_over,
    classify,
    generate_actions,
    legal_responses,
)
from .state import GameState, PlayerId

__all__ = [
    "PASS",
    "Action",
    "ActionType",
    "Card",
    "GameState",
    "PlayerId",
    "Rank",
    "REPLAY_SCHEMA_VERSION",
    "RuleConfig",
    "Suit",
    "can_play_over",
    "classify",
    "deal",
    "describe_architectures",
    "describe_training_milestones",
    "action_record",
    "full_deck",
    "generate_actions",
    "heuristic_policy",
    "public_state_record",
    "replay_record",
    "turn_record",
    "legal_responses",
    "parse_card",
    "parse_cards",
    "sample_hidden_hands",
    "validate_policy_value_record",
]
