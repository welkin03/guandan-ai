from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations

from .cards import Card, NORMAL_RANKS, Rank, Suit


class ActionType(StrEnum):
    PASS = "pass"
    SINGLE = "single"
    PAIR = "pair"
    TRIPLE = "triple"
    TRIPLE_WITH_PAIR = "triple_with_pair"
    STRAIGHT = "straight"
    PAIR_STRAIGHT = "pair_straight"
    PLATE = "plate"
    BOMB = "bomb"
    STRAIGHT_FLUSH = "straight_flush"
    JOKER_BOMB = "joker_bomb"


@dataclass(frozen=True)
class RuleConfig:
    level_rank: Rank = Rank.TWO
    wild_suit: Suit = Suit.HEARTS
    straight_len: int = 5
    pair_straight_len: int = 3
    plate_len: int = 2
    min_bomb_size: int = 4
    straight_flush_between_five_and_six_bomb: bool = True


@dataclass(frozen=True)
class Action:
    type: ActionType
    cards: tuple[Card, ...]
    main_rank: Rank | None = None
    length: int = 0
    suit: Suit | None = None

    @property
    def is_pass(self) -> bool:
        return self.type == ActionType.PASS

    @property
    def is_bomb_family(self) -> bool:
        return self.type in {ActionType.BOMB, ActionType.STRAIGHT_FLUSH, ActionType.JOKER_BOMB}


PASS = Action(type=ActionType.PASS, cards=())


COMPARISON_RANKS: tuple[Rank, ...] = (
    Rank.TWO,
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
)

SEQUENCE_TYPES = {
    ActionType.STRAIGHT,
    ActionType.PAIR_STRAIGHT,
    ActionType.PLATE,
    ActionType.STRAIGHT_FLUSH,
}


def rank_value(rank: Rank, config: RuleConfig) -> int:
    if rank == Rank.SMALL_JOKER:
        return 100
    if rank == Rank.BIG_JOKER:
        return 101
    base = [r for r in COMPARISON_RANKS if r != config.level_rank]
    base.append(config.level_rank)
    return base.index(rank)


def sequence_value(rank: Rank) -> int:
    return COMPARISON_RANKS.index(rank)


def action_compare_value(action: Action, config: RuleConfig) -> int:
    if action.main_rank is None:
        return -1
    if action.type in SEQUENCE_TYPES:
        return sequence_value(action.main_rank)
    return rank_value(action.main_rank, config)


def is_wild(card: Card, config: RuleConfig) -> bool:
    return card.rank == config.level_rank and card.suit == config.wild_suit


def classify(cards: list[Card] | tuple[Card, ...], config: RuleConfig | None = None) -> Action | None:
    config = config or RuleConfig()
    cards_tuple = tuple(cards)
    if not cards_tuple:
        return PASS

    joker_bomb = _classify_joker_bomb(cards_tuple)
    if joker_bomb:
        return joker_bomb

    wild_count, natural_counts = _split_wilds(cards_tuple, config)
    candidates: list[Action] = []

    candidates.extend(_classify_same_rank(cards_tuple, wild_count, natural_counts, config))
    candidates.extend(_classify_composites(cards_tuple, wild_count, natural_counts, config))
    candidates.extend(_classify_sequences(cards_tuple, wild_count, natural_counts, config))

    if not candidates:
        return None
    return max(candidates, key=lambda action: _class_priority(action, config))


def can_play_over(challenger: Action | None, incumbent: Action | None, config: RuleConfig | None = None) -> bool:
    config = config or RuleConfig()
    if challenger is None:
        return False
    if challenger.is_pass:
        return incumbent is not None and not incumbent.is_pass
    if incumbent is None or incumbent.is_pass:
        return True

    if challenger.is_bomb_family or incumbent.is_bomb_family:
        if not challenger.is_bomb_family:
            return False
        if not incumbent.is_bomb_family:
            return True
        return _bomb_strength(challenger, config) > _bomb_strength(incumbent, config)

    if challenger.type != incumbent.type or len(challenger.cards) != len(incumbent.cards):
        return False
    if challenger.main_rank is None or incumbent.main_rank is None:
        return False
    return action_compare_value(challenger, config) > action_compare_value(incumbent, config)


def _split_wilds(cards: tuple[Card, ...], config: RuleConfig) -> tuple[int, Counter[Rank]]:
    wild_count = 0
    counts: Counter[Rank] = Counter()
    for card in cards:
        if is_wild(card, config):
            wild_count += 1
        else:
            counts[card.rank] += 1
    return wild_count, counts


def _classify_joker_bomb(cards: tuple[Card, ...]) -> Action | None:
    if len(cards) == 4 and all(card.is_joker for card in cards):
        return Action(type=ActionType.JOKER_BOMB, cards=cards, length=4)
    return None


def _classify_same_rank(
    cards: tuple[Card, ...],
    wild_count: int,
    natural_counts: Counter[Rank],
    config: RuleConfig,
) -> list[Action]:
    size = len(cards)
    if any(rank in {Rank.SMALL_JOKER, Rank.BIG_JOKER} for rank in natural_counts):
        if size == 1:
            rank = cards[0].rank
            return [Action(type=ActionType.SINGLE, cards=cards, main_rank=rank, length=1)]
        if size == 2 and wild_count == 0:
            for joker_rank in (Rank.SMALL_JOKER, Rank.BIG_JOKER):
                if natural_counts[joker_rank] == 2:
                    return [Action(type=ActionType.PAIR, cards=cards, main_rank=joker_rank, length=2)]
        return []

    actions: list[Action] = []
    possible = list(NORMAL_RANKS)
    for rank in possible:
        if natural_counts[rank] + wild_count != size:
            continue
        if size == 1:
            actions.append(Action(type=ActionType.SINGLE, cards=cards, main_rank=rank, length=1))
        elif size == 2:
            actions.append(Action(type=ActionType.PAIR, cards=cards, main_rank=rank, length=2))
        elif size == 3:
            actions.append(Action(type=ActionType.TRIPLE, cards=cards, main_rank=rank, length=3))
        elif size >= config.min_bomb_size:
            actions.append(Action(type=ActionType.BOMB, cards=cards, main_rank=rank, length=size))
    return actions


def _classify_composites(
    cards: tuple[Card, ...],
    wild_count: int,
    natural_counts: Counter[Rank],
    config: RuleConfig,
) -> list[Action]:
    size = len(cards)
    actions: list[Action] = []
    ranks = list(NORMAL_RANKS)
    pair_ranks = ranks + [Rank.SMALL_JOKER, Rank.BIG_JOKER]

    if size == 5:
        for triple_rank in ranks:
            for pair_rank in pair_ranks:
                if pair_rank == triple_rank:
                    continue
                if pair_rank in {Rank.SMALL_JOKER, Rank.BIG_JOKER} and natural_counts[pair_rank] != 2:
                    continue
                pair_wild_need = 0 if pair_rank in {Rank.SMALL_JOKER, Rank.BIG_JOKER} else max(0, 2 - natural_counts[pair_rank])
                need = max(0, 3 - natural_counts[triple_rank]) + pair_wild_need
                extras = sum(
                    count
                    for rank, count in natural_counts.items()
                    if rank not in {triple_rank, pair_rank}
                )
                if need == wild_count and extras == 0:
                    actions.append(
                        Action(
                            type=ActionType.TRIPLE_WITH_PAIR,
                            cards=cards,
                            main_rank=triple_rank,
                            length=5,
                        )
                    )

    if any(rank in {Rank.SMALL_JOKER, Rank.BIG_JOKER} for rank in natural_counts):
        return actions

    if size == config.plate_len * 3:
        for sequence in _normal_sequences(config.plate_len):
            need = sum(max(0, 3 - natural_counts[rank]) for rank in sequence)
            extras = sum(count for rank, count in natural_counts.items() if rank not in sequence)
            if need == wild_count and extras == 0:
                actions.append(
                    Action(
                        type=ActionType.PLATE,
                        cards=cards,
                        main_rank=sequence[-1],
                        length=size,
                    )
                )
    return actions


def _classify_sequences(
    cards: tuple[Card, ...],
    wild_count: int,
    natural_counts: Counter[Rank],
    config: RuleConfig,
) -> list[Action]:
    if any(rank in {Rank.SMALL_JOKER, Rank.BIG_JOKER} for rank in natural_counts):
        return []

    actions: list[Action] = []
    size = len(cards)

    if size == config.straight_len:
        for sequence in _normal_sequences(config.straight_len, config):
            if _can_fill_sequence(sequence, 1, wild_count, natural_counts):
                suit = _straight_flush_suit(cards, sequence, wild_count, config)
                action_type = ActionType.STRAIGHT_FLUSH if suit else ActionType.STRAIGHT
                actions.append(
                    Action(type=action_type, cards=cards, main_rank=sequence[-1], length=size, suit=suit)
                )

    if size == config.pair_straight_len * 2:
        for sequence in _normal_sequences(config.pair_straight_len, config):
            if _can_fill_sequence(sequence, 2, wild_count, natural_counts):
                actions.append(
                    Action(
                        type=ActionType.PAIR_STRAIGHT,
                        cards=cards,
                        main_rank=sequence[-1],
                        length=size,
                    )
                )
    return actions


def _normal_sequences(length: int, config: RuleConfig | None = None) -> list[tuple[Rank, ...]]:
    ranks = [
        Rank.ACE,
        Rank.TWO,
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
    ]
    return [tuple(ranks[index : index + length]) for index in range(0, len(ranks) - length + 1)]


def _can_fill_sequence(
    sequence: tuple[Rank, ...],
    copies_per_rank: int,
    wild_count: int,
    natural_counts: Counter[Rank],
) -> bool:
    need = sum(max(0, copies_per_rank - natural_counts[rank]) for rank in sequence)
    extras = sum(count for rank, count in natural_counts.items() if rank not in sequence)
    overfilled = any(natural_counts[rank] > copies_per_rank for rank in sequence)
    return need == wild_count and extras == 0 and not overfilled


def _straight_flush_suit(
    cards: tuple[Card, ...],
    sequence: tuple[Rank, ...],
    wild_count: int,
    config: RuleConfig,
) -> Suit | None:
    natural = [card for card in cards if not is_wild(card, config)]
    normal_suits = [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES]
    for suit in normal_suits:
        if all(card.suit == suit for card in natural):
            missing = sum(1 for rank in sequence if not any(card.rank == rank and card.suit == suit for card in natural))
            if missing == wild_count:
                return suit
    return None


def _class_priority(action: Action, config: RuleConfig) -> tuple[int, int, int]:
    if action.main_rank is None:
        rank = -1
    else:
        rank = action_compare_value(action, config)
    return (_type_priority(action.type), action.length, rank)


def _type_priority(action_type: ActionType) -> int:
    order = {
        ActionType.PASS: 0,
        ActionType.SINGLE: 1,
        ActionType.PAIR: 2,
        ActionType.TRIPLE: 3,
        ActionType.TRIPLE_WITH_PAIR: 4,
        ActionType.STRAIGHT: 5,
        ActionType.PAIR_STRAIGHT: 6,
        ActionType.PLATE: 7,
        ActionType.BOMB: 8,
        ActionType.STRAIGHT_FLUSH: 9,
        ActionType.JOKER_BOMB: 10,
    }
    return order[action_type]


def _bomb_strength(action: Action, config: RuleConfig) -> tuple[int, int]:
    if action.type == ActionType.JOKER_BOMB:
        return (100, 0)
    rank = -1 if action.main_rank is None else action_compare_value(action, config)
    if action.type == ActionType.STRAIGHT_FLUSH:
        if config.straight_flush_between_five_and_six_bomb:
            return (5, 100 + rank)
        return (action.length, rank)
    if action.type == ActionType.BOMB:
        return (action.length, rank)
    return (0, rank)


def legal_responses(
    hand: list[Card] | tuple[Card, ...],
    incumbent: Action | None,
    config: RuleConfig | None = None,
) -> list[Action]:
    config = config or RuleConfig()
    responses: list[Action] = []
    if incumbent is not None and not incumbent.is_pass:
        responses.append(PASS)

    seen_actions: set[tuple[ActionType, Rank | None, int, Suit | None, tuple[str, ...]]] = set()
    for action in generate_actions(hand, config):
        key = (
            action.type,
            action.main_rank,
            action.length,
            action.suit,
            tuple(sorted(card.code() for card in action.cards)),
        )
        if key in seen_actions:
            continue
        seen_actions.add(key)
        if can_play_over(action, incumbent, config):
            responses.append(action)
    return responses


def generate_actions(hand: list[Card] | tuple[Card, ...], config: RuleConfig | None = None) -> list[Action]:
    config = config or RuleConfig()
    hand_tuple = tuple(hand)
    actions: list[Action] = []
    actions.extend(_generate_same_rank_actions(hand_tuple, config))
    actions.extend(_generate_triple_with_pair_actions(hand_tuple, config))
    actions.extend(_generate_sequence_actions(hand_tuple, config))
    actions.extend(_generate_joker_bomb_actions(hand_tuple))
    return actions


def _cards_by_rank(hand: tuple[Card, ...], config: RuleConfig) -> tuple[list[Card], dict[Rank, list[Card]]]:
    wilds: list[Card] = []
    by_rank: dict[Rank, list[Card]] = {rank: [] for rank in NORMAL_RANKS}
    for card in hand:
        if is_wild(card, config):
            wilds.append(card)
        elif card.rank in by_rank:
            by_rank[card.rank].append(card)
    return wilds, by_rank


def _take(cards: list[Card], count: int) -> tuple[Card, ...] | None:
    if len(cards) < count:
        return None
    return tuple(cards[:count])


def _fill_rank(rank: Rank, size: int, wilds: list[Card], by_rank: dict[Rank, list[Card]]) -> tuple[Card, ...] | None:
    natural = by_rank.get(rank, [])
    use_natural = min(len(natural), size)
    need_wild = size - use_natural
    if need_wild > len(wilds):
        return None
    return tuple(natural[:use_natural] + wilds[:need_wild])


def _generate_same_rank_actions(hand: tuple[Card, ...], config: RuleConfig) -> list[Action]:
    wilds, by_rank = _cards_by_rank(hand, config)
    actions: list[Action] = []

    for card in hand:
        actions.append(Action(type=ActionType.SINGLE, cards=(card,), main_rank=card.rank, length=1))

    for joker_rank in (Rank.SMALL_JOKER, Rank.BIG_JOKER):
        joker_pair = tuple(card for card in hand if card.rank == joker_rank)
        if len(joker_pair) >= 2:
            actions.append(Action(type=ActionType.PAIR, cards=joker_pair[:2], main_rank=joker_rank, length=2))

    for rank in NORMAL_RANKS:
        for size, action_type in ((2, ActionType.PAIR), (3, ActionType.TRIPLE)):
            cards = _fill_rank(rank, size, wilds, by_rank)
            if cards:
                actions.append(Action(type=action_type, cards=cards, main_rank=rank, length=size))

        max_size = min(len(by_rank[rank]) + len(wilds), 8)
        for size in range(config.min_bomb_size, max_size + 1):
            cards = _fill_rank(rank, size, wilds, by_rank)
            if cards:
                actions.append(Action(type=ActionType.BOMB, cards=cards, main_rank=rank, length=size))
    return actions


def _generate_triple_with_pair_actions(hand: tuple[Card, ...], config: RuleConfig) -> list[Action]:
    wilds, by_rank = _cards_by_rank(hand, config)
    actions: list[Action] = []
    joker_pairs = {
        joker_rank: [card for card in hand if card.rank == joker_rank]
        for joker_rank in (Rank.SMALL_JOKER, Rank.BIG_JOKER)
    }
    for triple_rank in NORMAL_RANKS:
        for pair_rank in list(NORMAL_RANKS) + [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
            if pair_rank == triple_rank:
                continue
            for wild_for_triple in range(0, len(wilds) + 1):
                triple_natural_needed = 3 - wild_for_triple
                pair_wilds = len(wilds) - wild_for_triple
                if triple_natural_needed < 0 or len(by_rank[triple_rank]) < triple_natural_needed:
                    continue
                if pair_rank in {Rank.SMALL_JOKER, Rank.BIG_JOKER}:
                    if len(joker_pairs[pair_rank]) < 2:
                        continue
                    pair_cards = joker_pairs[pair_rank][:2]
                    need_pair_wilds = 0
                else:
                    pair_natural_needed = 2 - min(2, pair_wilds)
                    if pair_natural_needed < 0:
                        pair_natural_needed = 0
                    need_pair_wilds = 2 - pair_natural_needed
                    if need_pair_wilds > pair_wilds or len(by_rank[pair_rank]) < pair_natural_needed:
                        continue
                    pair_cards = by_rank[pair_rank][:pair_natural_needed]
                cards = tuple(
                    by_rank[triple_rank][:triple_natural_needed]
                    + wilds[:wild_for_triple]
                    + pair_cards
                    + wilds[wild_for_triple : wild_for_triple + need_pair_wilds]
                )
                if len(cards) == 5:
                    action = classify(cards, config)
                    if action and action.type == ActionType.TRIPLE_WITH_PAIR:
                        actions.append(action)
    return actions


def _generate_sequence_actions(hand: tuple[Card, ...], config: RuleConfig) -> list[Action]:
    wilds, by_rank = _cards_by_rank(hand, config)
    actions: list[Action] = []
    for sequence, copies, action_type in (
        *[(seq, 1, ActionType.STRAIGHT) for seq in _normal_sequences(config.straight_len, config)],
        *[(seq, 2, ActionType.PAIR_STRAIGHT) for seq in _normal_sequences(config.pair_straight_len, config)],
        *[(seq, 3, ActionType.PLATE) for seq in _normal_sequences(config.plate_len, config)],
    ):
        cards = _fill_sequence(sequence, copies, wilds, by_rank)
        if not cards:
            continue
        action = classify(cards, config)
        if action and action.type in {action_type, ActionType.STRAIGHT_FLUSH}:
            actions.append(action)

    actions.extend(_generate_natural_straight_flushes(hand, config))
    return actions


def _fill_sequence(
    sequence: tuple[Rank, ...],
    copies: int,
    wilds: list[Card],
    by_rank: dict[Rank, list[Card]],
) -> tuple[Card, ...] | None:
    selected: list[Card] = []
    wild_index = 0
    for rank in sequence:
        natural = by_rank[rank][:copies]
        need = copies - len(natural)
        if wild_index + need > len(wilds):
            return None
        selected.extend(natural)
        selected.extend(wilds[wild_index : wild_index + need])
        wild_index += need
    return tuple(selected)


def _generate_natural_straight_flushes(hand: tuple[Card, ...], config: RuleConfig) -> list[Action]:
    actions: list[Action] = []
    wilds = [card for card in hand if is_wild(card, config)]
    for suit in (Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES):
        suited: dict[Rank, list[Card]] = {rank: [] for rank in NORMAL_RANKS}
        for card in hand:
            if not is_wild(card, config) and card.suit == suit and card.rank in suited:
                suited[card.rank].append(card)
        for sequence in _normal_sequences(config.straight_len, config):
            selected: list[Card] = []
            wild_index = 0
            for rank in sequence:
                if suited[rank]:
                    selected.append(suited[rank][0])
                elif wild_index < len(wilds):
                    selected.append(wilds[wild_index])
                    wild_index += 1
                else:
                    break
            if len(selected) == config.straight_len:
                action = classify(tuple(selected), config)
                if action and action.type == ActionType.STRAIGHT_FLUSH:
                    actions.append(action)
    return actions


def _generate_joker_bomb_actions(hand: tuple[Card, ...]) -> list[Action]:
    jokers = [card for card in hand if card.rank in {Rank.SMALL_JOKER, Rank.BIG_JOKER}]
    if len(jokers) == 4:
        return [Action(type=ActionType.JOKER_BOMB, cards=tuple(jokers), length=4)]
    return []
