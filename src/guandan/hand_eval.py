from __future__ import annotations

from functools import lru_cache

from .cards import Card, Rank
from .rules import Action, ActionType, RuleConfig, generate_actions
from .state import GameState


def min_play_count(
    hand: tuple[Card, ...],
    config: RuleConfig,
    *,
    exact_limit: int = 8,
) -> int:
    if not hand:
        return 0
    cards = tuple(sorted(hand))
    if len(cards) <= exact_limit:
        return _min_play_count_exact(cards, config)
    return _min_play_count_greedy(cards, config)


def team_min_play_count(state: GameState, team: int) -> int:
    total = 0
    for player, hand in enumerate(state.hands):
        if player % 2 == team and player not in state.finished:
            total += min_play_count(hand, state.config)
    return total


def team_turn_count_value(state: GameState, team: int) -> float:
    own = team_min_play_count(state, team)
    opponent = team_min_play_count(state, 1 - team)
    if own + opponent <= 0:
        return 0.0
    value = (opponent - own) / max(4.0, own + opponent)
    return max(-1.0, min(1.0, value))


@lru_cache(maxsize=200_000)
def _min_play_count_exact(cards: tuple[Card, ...], config: RuleConfig) -> int:
    if not cards:
        return 0
    best = len(cards)
    for action in _cover_actions(cards, config):
        remaining = _remove_cards(cards, action.cards)
        if len(remaining) == len(cards):
            continue
        best = min(best, 1 + _min_play_count_exact(remaining, config))
        if best == 1:
            break
    return best


def _min_play_count_greedy(cards: tuple[Card, ...], config: RuleConfig) -> int:
    remaining = tuple(cards)
    count = 0
    while remaining:
        actions = _cover_actions(remaining, config)
        if not actions:
            count += len(remaining)
            break
        action = min(actions, key=lambda item: _action_cover_cost(item))
        next_remaining = _remove_cards(remaining, action.cards)
        if len(next_remaining) == len(remaining):
            count += len(remaining)
            break
        remaining = next_remaining
        count += 1
    return count


def _cover_actions(cards: tuple[Card, ...], config: RuleConfig) -> list[Action]:
    seen: set[tuple[str, ...]] = set()
    actions: list[Action] = []
    for action in generate_actions(cards, config):
        if action.is_pass:
            continue
        key = tuple(sorted(_card_id(card) for card in action.cards))
        if key in seen:
            continue
        seen.add(key)
        actions.append(action)
    actions.sort(key=_action_cover_cost)
    return actions


def _action_cover_cost(action: Action) -> tuple[int, int, int, int]:
    bomb_penalty = 2 if action.type in {ActionType.BOMB, ActionType.JOKER_BOMB} else 0
    straight_flush_penalty = 1 if action.type == ActionType.STRAIGHT_FLUSH else 0
    return (-len(action.cards), bomb_penalty + straight_flush_penalty, _shape_order(action.type), _main_rank_order(action))


def _shape_order(action_type: ActionType) -> int:
    order = {
        ActionType.PLATE: 0,
        ActionType.PAIR_STRAIGHT: 1,
        ActionType.STRAIGHT: 2,
        ActionType.TRIPLE_WITH_PAIR: 3,
        ActionType.TRIPLE: 4,
        ActionType.PAIR: 5,
        ActionType.SINGLE: 6,
        ActionType.STRAIGHT_FLUSH: 7,
        ActionType.BOMB: 8,
        ActionType.JOKER_BOMB: 9,
    }
    return order.get(action_type, 10)


def _main_rank_order(action: Action) -> int:
    if action.main_rank is None:
        return 0
    order = {
        Rank.TWO: 2,
        Rank.THREE: 3,
        Rank.FOUR: 4,
        Rank.FIVE: 5,
        Rank.SIX: 6,
        Rank.SEVEN: 7,
        Rank.EIGHT: 8,
        Rank.NINE: 9,
        Rank.TEN: 10,
        Rank.JACK: 11,
        Rank.QUEEN: 12,
        Rank.KING: 13,
        Rank.ACE: 14,
        Rank.SMALL_JOKER: 15,
        Rank.BIG_JOKER: 16,
    }
    return order.get(action.main_rank, 0)


def _remove_cards(cards: tuple[Card, ...], used: tuple[Card, ...]) -> tuple[Card, ...]:
    remaining = list(cards)
    for card in used:
        try:
            remaining.remove(card)
        except ValueError:
            return cards
    return tuple(sorted(remaining))


def _card_id(card: Card) -> str:
    return f"{card.code()}#{card.copy}"
