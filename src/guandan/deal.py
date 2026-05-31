from __future__ import annotations

import random
from collections.abc import Sequence

from .cards import Card, full_deck, remove_by_code
from .state import PlayerId


def deal(seed: int | None = None) -> tuple[tuple[Card, ...], tuple[Card, ...], tuple[Card, ...], tuple[Card, ...]]:
    rng = random.Random(seed)
    cards = full_deck()
    rng.shuffle(cards)
    return tuple(tuple(cards[index * 27 : (index + 1) * 27]) for index in range(4))  # type: ignore[return-value]


def sample_hidden_hands(
    known_hands: dict[PlayerId, Sequence[Card]],
    played_cards: Sequence[Card] = (),
    hand_sizes: dict[PlayerId, int] | None = None,
    seed: int | None = None,
) -> tuple[tuple[Card, ...], tuple[Card, ...], tuple[Card, ...], tuple[Card, ...]]:
    rng = random.Random(seed)
    hand_sizes = hand_sizes or {player: 27 for player in range(4)}

    remaining = full_deck()
    for cards in known_hands.values():
        remaining = remove_by_code(remaining, list(cards))
    remaining = remove_by_code(remaining, list(played_cards))
    rng.shuffle(remaining)

    result: list[tuple[Card, ...] | None] = [None, None, None, None]
    for player, cards in known_hands.items():
        result[player] = tuple(cards)

    cursor = 0
    for player in range(4):
        if result[player] is not None:
            continue
        size = hand_sizes[player]
        result[player] = tuple(remaining[cursor : cursor + size])
        cursor += size

    if cursor != len(remaining):
        raise ValueError("Known cards, played cards, and hand sizes do not match a full deck")
    return tuple(result)  # type: ignore[return-value]
