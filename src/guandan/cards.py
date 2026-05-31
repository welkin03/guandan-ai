from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Suit(StrEnum):
    CLUBS = "C"
    DIAMONDS = "D"
    HEARTS = "H"
    SPADES = "S"
    JOKER = "J"


class Rank(StrEnum):
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "T"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"
    TWO = "2"
    SMALL_JOKER = "SJ"
    BIG_JOKER = "BJ"


NORMAL_RANKS: tuple[Rank, ...] = (
    Rank.THREE,
    Rank.FOUR,
    Rank.FIVE,
    Rank.SIX,
    Rank.SEVEN,
    Rank.EIGHT,
    Rank.NINE,
    Rank.TEN,
    Rank.JACK,
    Rank.QUEEN,
    Rank.KING,
    Rank.ACE,
    Rank.TWO,
)

RANK_ALIASES = {
    "3": Rank.THREE,
    "4": Rank.FOUR,
    "5": Rank.FIVE,
    "6": Rank.SIX,
    "7": Rank.SEVEN,
    "8": Rank.EIGHT,
    "9": Rank.NINE,
    "10": Rank.TEN,
    "T": Rank.TEN,
    "J": Rank.JACK,
    "Q": Rank.QUEEN,
    "K": Rank.KING,
    "A": Rank.ACE,
    "2": Rank.TWO,
    "X": Rank.SMALL_JOKER,
    "Y": Rank.BIG_JOKER,
}

SUIT_ALIASES = {
    "C": Suit.CLUBS,
    "D": Suit.DIAMONDS,
    "H": Suit.HEARTS,
    "S": Suit.SPADES,
}


@dataclass(frozen=True, order=True)
class Card:
    rank: Rank
    suit: Suit
    copy: int = 0

    @property
    def is_joker(self) -> bool:
        return self.rank in {Rank.SMALL_JOKER, Rank.BIG_JOKER}

    def code(self) -> str:
        if self.rank == Rank.SMALL_JOKER:
            return "X"
        if self.rank == Rank.BIG_JOKER:
            return "Y"
        return f"{self.suit.value}{self.rank.value}"

    def __str__(self) -> str:
        return self.code()


def full_deck(copies: int = 2) -> list[Card]:
    deck: list[Card] = []
    for copy in range(copies):
        for suit in (Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES):
            for rank in NORMAL_RANKS:
                deck.append(Card(rank=rank, suit=suit, copy=copy))
        deck.append(Card(rank=Rank.SMALL_JOKER, suit=Suit.JOKER, copy=copy))
        deck.append(Card(rank=Rank.BIG_JOKER, suit=Suit.JOKER, copy=copy))
    return deck


def parse_card(text: str, copy: int = 0) -> Card:
    token = text.strip().upper()
    if token in RANK_ALIASES and RANK_ALIASES[token] in {Rank.SMALL_JOKER, Rank.BIG_JOKER}:
        return Card(rank=RANK_ALIASES[token], suit=Suit.JOKER, copy=copy)

    if len(token) < 2:
        raise ValueError(f"Invalid card: {text!r}")
    suit = SUIT_ALIASES.get(token[0])
    rank = RANK_ALIASES.get(token[1:])
    if suit is None or rank is None or rank in {Rank.SMALL_JOKER, Rank.BIG_JOKER}:
        raise ValueError(f"Invalid card: {text!r}")
    return Card(rank=rank, suit=suit, copy=copy)


def parse_cards(text: str) -> list[Card]:
    counts: dict[str, int] = {}
    cards: list[Card] = []
    for raw in text.replace(",", " ").split():
        normalized = raw.strip().upper()
        copy = counts.get(normalized, 0)
        counts[normalized] = copy + 1
        cards.append(parse_card(normalized, copy=copy))
    return cards


def card_code_counts(cards: list[Card] | tuple[Card, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for card in cards:
        counts[card.code()] = counts.get(card.code(), 0) + 1
    return counts


def remove_by_code(deck: list[Card], cards: list[Card] | tuple[Card, ...]) -> list[Card]:
    remaining = list(deck)
    for target in cards:
        for index, card in enumerate(remaining):
            if card.code() == target.code():
                remaining.pop(index)
                break
        else:
            raise ValueError(f"Card {target.code()} is not available")
    return remaining
