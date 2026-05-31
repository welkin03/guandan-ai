from __future__ import annotations

import unittest

from guandan import (
    PASS,
    ActionType,
    GameState,
    Rank,
    RuleConfig,
    can_play_over,
    classify,
    deal,
    full_deck,
    heuristic_policy,
    parse_cards,
)


class CardAndRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = RuleConfig(level_rank=Rank.TWO)

    def test_full_deck_has_108_cards(self) -> None:
        self.assertEqual(len(full_deck()), 108)

    def test_pair_and_straight(self) -> None:
        pair = classify(parse_cards("C3 D3"), self.config)
        straight = classify(parse_cards("CA C2 C3 C4 C5"), self.config)
        self.assertEqual(pair.type, ActionType.PAIR)
        self.assertEqual(straight.type, ActionType.STRAIGHT_FLUSH)

    def test_level_heart_is_wild(self) -> None:
        action = classify(parse_cards("C3 D3 H2"), self.config)
        self.assertEqual(action.type, ActionType.TRIPLE)
        self.assertEqual(action.main_rank, Rank.THREE)

    def test_bomb_beats_regular_action(self) -> None:
        pair = classify(parse_cards("C3 D3"), self.config)
        bomb = classify(parse_cards("C4 D4 H4 S4"), self.config)
        self.assertTrue(can_play_over(bomb, pair, self.config))
        self.assertFalse(can_play_over(pair, bomb, self.config))

    def test_joker_bomb(self) -> None:
        action = classify(parse_cards("X X Y Y"), self.config)
        self.assertEqual(action.type, ActionType.JOKER_BOMB)


class StateAndPolicyTests(unittest.TestCase):
    def test_deal_has_four_hands_of_27_cards(self) -> None:
        hands = deal(seed=21)
        self.assertEqual([len(hand) for hand in hands], [27, 27, 27, 27])

    def test_trick_returns_to_leader_after_three_passes(self) -> None:
        state = GameState(
            hands=(
                tuple(parse_cards("C3 C4")),
                tuple(parse_cards("C5")),
                tuple(parse_cards("C6")),
                tuple(parse_cards("C7")),
            ),
            current_player=0,
        )
        state = state.play(parse_cards("C3"))
        state = state.play_action(PASS)
        state = state.play_action(PASS)
        state = state.play_action(PASS)
        self.assertEqual(state.current_player, 0)
        self.assertIsNone(state.last_action)

    def test_heuristic_policy_returns_legal_action(self) -> None:
        state = GameState(hands=deal(seed=21), current_player=0)
        action = heuristic_policy(state)
        self.assertIn(action, state.legal_actions())


if __name__ == "__main__":
    unittest.main()
