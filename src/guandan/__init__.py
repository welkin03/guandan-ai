"""Core Guandan rules engine and heuristic AI."""

from .cards import Card, Rank, Suit, full_deck, parse_card, parse_cards
from .deal import deal, sample_hidden_hands
from .policy import heuristic_policy
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
    "RuleConfig",
    "Suit",
    "can_play_over",
    "classify",
    "deal",
    "full_deck",
    "generate_actions",
    "heuristic_policy",
    "legal_responses",
    "parse_card",
    "parse_cards",
    "sample_hidden_hands",
]
