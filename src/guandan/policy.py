from __future__ import annotations

import random
from collections import Counter

from .cards import Rank
from .hand_eval import min_play_count, team_turn_count_value
from .rules import Action, ActionType, PASS, action_compare_value
from .state import GameState


def heuristic_policy(state: GameState, rng: random.Random | None = None) -> Action:
    actions = state.legal_actions()
    if not actions:
        raise ValueError("No legal actions")

    non_pass = [action for action in actions if not action.is_pass]
    if not non_pass:
        return actions[0]

    if _is_leading(state):
        return min(non_pass, key=lambda action: _lead_cost(state, action))
    return _choose_response(state, actions)


def should_guard_active_bomb_lead(state: GameState, action: Action) -> bool:
    if not _is_leading(state):
        return False
    if action.is_pass or not action.is_bomb_family:
        return False
    hand_size = len(state.hands[state.current_player])
    if len(action.cards) >= hand_size:
        return False
    if _hand_is_all_bomb_material(state):
        return False
    return any(
        not candidate.is_pass and not candidate.is_bomb_family
        for candidate in state.legal_actions()
    )


def guard_active_bomb_lead(
    state: GameState,
    action: Action,
    fallback: Action | None = None,
) -> Action:
    if not should_guard_active_bomb_lead(state, action):
        return action
    if fallback is not None and not fallback.is_pass and not fallback.is_bomb_family:
        return fallback
    non_bomb_leads = [
        candidate
        for candidate in state.legal_actions()
        if not candidate.is_pass and not candidate.is_bomb_family
    ]
    if not non_bomb_leads:
        return action
    return min(non_bomb_leads, key=lambda candidate: _lead_cost(state, candidate))


def should_guard_single_card_opponent_lead(state: GameState, action: Action) -> bool:
    if not _is_leading(state):
        return False
    if action.is_pass or action.type != ActionType.SINGLE:
        return False
    if not _opponent_has_one_card(state):
        return False
    return any(
        not candidate.is_pass and candidate.type != ActionType.SINGLE
        for candidate in state.legal_actions()
    )


def guard_single_card_opponent_lead(
    state: GameState,
    action: Action,
    fallback: Action | None = None,
) -> Action:
    if not should_guard_single_card_opponent_lead(state, action):
        return action
    if fallback is not None and not fallback.is_pass and fallback.type != ActionType.SINGLE:
        return fallback
    non_single_leads = [
        candidate
        for candidate in state.legal_actions()
        if not candidate.is_pass and candidate.type != ActionType.SINGLE
    ]
    if not non_single_leads:
        return action
    return min(non_single_leads, key=lambda candidate: _lead_cost(state, candidate))


def should_guard_single_card_opponent_response(state: GameState, action: Action) -> bool:
    if _is_leading(state):
        return False
    if state.last_action is None or state.last_action.type != ActionType.SINGLE:
        return False
    if action.is_pass or action.type != ActionType.SINGLE:
        return False
    if len(action.cards) >= len(state.hands[state.current_player]):
        return False
    guarded = _single_card_opponent_response_action(state, state.legal_actions())
    return guarded is not None and _main_value(state, guarded) > _main_value(state, action)


def guard_single_card_opponent_response(state: GameState, action: Action) -> Action:
    if not should_guard_single_card_opponent_response(state, action):
        return action
    guarded = _single_card_opponent_response_action(state, state.legal_actions())
    return guarded if guarded is not None else action


def should_guard_pre_first_pressure_response(state: GameState, action: Action) -> bool:
    if not action.is_pass or _is_leading(state) or state.finished or state.last_actor is None:
        return False
    if state.last_actor % 2 == state.current_player % 2:
        return False
    return _pre_first_pressure_response_action(state) is not None


def guard_pre_first_pressure_response(state: GameState, action: Action) -> Action:
    if not should_guard_pre_first_pressure_response(state, action):
        return action
    guarded = _pre_first_pressure_response_action(state)
    return guarded if guarded is not None else action


def should_guard_pre_first_lead_plan(
    state: GameState,
    action: Action,
    fallback: Action | None = None,
) -> bool:
    if not _is_leading(state) or state.finished or action.is_pass:
        return False
    if len(action.cards) >= len(state.hands[state.current_player]):
        return False
    guarded = _pre_first_lead_plan_action(state, action, fallback=fallback)
    return guarded is not None and guarded != action


def guard_pre_first_lead_plan(
    state: GameState,
    action: Action,
    fallback: Action | None = None,
) -> Action:
    guarded = _pre_first_lead_plan_action(state, action, fallback=fallback)
    return guarded if guarded is not None else action


def should_guard_partner_bomb_overplay(state: GameState, action: Action) -> bool:
    if not _partner_is_winning_trick(state):
        return False
    if action.is_pass or not action.is_bomb_family:
        return False
    hand_size = len(state.hands[state.current_player])
    if len(action.cards) >= hand_size:
        return False
    if _opponents_near_finish(state):
        return False
    if _hand_is_all_bomb_material(state):
        return False
    return any(candidate.is_pass for candidate in state.legal_actions())


def guard_partner_bomb_overplay(state: GameState, action: Action) -> Action:
    if not should_guard_partner_bomb_overplay(state, action):
        return action
    return next((candidate for candidate in state.legal_actions() if candidate.is_pass), PASS)


def _is_leading(state: GameState) -> bool:
    return state.last_action is None or state.last_actor == state.current_player


def _choose_response(state: GameState, actions: list[Action]) -> Action:
    non_pass = [action for action in actions if not action.is_pass]
    pass_action = next((action for action in actions if action.is_pass), PASS)
    finishing = _finishing_actions(state, non_pass)
    if finishing:
        return min(finishing, key=lambda action: _response_cost(state, action))

    single_card_lock = _single_card_opponent_response_action(state, non_pass)
    if single_card_lock is not None:
        return single_card_lock

    if _partner_is_winning_trick(state):
        urgent = _opponents_near_finish(state)
        takeover = _partner_takeover_action(state, non_pass)
        if takeover is not None:
            return takeover
        if not urgent:
            return pass_action

    non_bombs = [action for action in non_pass if not action.is_bomb_family]
    if non_bombs:
        return min(non_bombs, key=lambda action: _response_cost(state, action))

    if _should_spend_bomb(state):
        return min(non_pass, key=lambda action: _response_cost(state, action))
    return pass_action


def guard_partner_pass(state: GameState, action: Action) -> Action:
    if not action.is_pass or not _partner_is_winning_trick(state):
        return action
    legal_actions = state.legal_actions()
    non_pass = [candidate for candidate in legal_actions if not candidate.is_pass]
    finishing = _finishing_actions(state, non_pass)
    if finishing:
        return min(finishing, key=lambda candidate: _response_cost(state, candidate))
    single_card_lock = _single_card_opponent_response_action(state, non_pass)
    if single_card_lock is not None:
        return single_card_lock
    takeover = _partner_takeover_action(state, non_pass)
    if takeover is not None:
        return takeover
    if _opponents_near_finish(state) and non_pass:
        return min(non_pass, key=lambda candidate: _response_cost(state, candidate))
    return action


def _pre_first_pressure_response_action(state: GameState) -> Action | None:
    legal_actions = state.legal_actions()
    non_pass = [candidate for candidate in legal_actions if not candidate.is_pass]
    if not non_pass:
        return None

    current_turns = _safe_min_play_count(state.hands[state.current_player], state.config)
    opponent_min_cards = min(
        (
            len(state.hands[player])
            for player in range(4)
            if player % 2 != state.current_player % 2 and player not in state.finished
        ),
        default=99,
    )
    team_pressure = team_turn_count_value(state, state.current_player % 2) <= -0.08
    shape_pressure = bool(
        state.last_action is not None
        and (state.last_action.is_bomb_family or state.last_action.length >= 5)
    )
    urgent = opponent_min_cards <= 8 or _opponents_near_finish(state) or team_pressure

    def improves_plan(candidate: Action) -> bool:
        after_turns = _safe_min_play_count(_remaining_after_action(state, candidate), state.config)
        if after_turns < current_turns:
            return True
        return (
            candidate.type in {ActionType.STRAIGHT_FLUSH, ActionType.PAIR_STRAIGHT, ActionType.PLATE}
            and candidate.length >= 5
            and after_turns <= current_turns
        )

    efficient = [candidate for candidate in non_pass if improves_plan(candidate)]
    if not efficient:
        return None

    straight_flushes = [candidate for candidate in efficient if candidate.type == ActionType.STRAIGHT_FLUSH]
    if straight_flushes and (shape_pressure or urgent):
        return min(straight_flushes, key=lambda candidate: _response_cost(state, candidate))

    non_bomb_pressure = [
        candidate
        for candidate in efficient
        if not candidate.is_bomb_family and candidate.length >= 2
    ]
    if non_bomb_pressure:
        return min(non_bomb_pressure, key=lambda candidate: _response_cost(state, candidate))

    bombs = [
        candidate
        for candidate in efficient
        if candidate.type in {ActionType.BOMB, ActionType.JOKER_BOMB}
    ]
    if bombs and (urgent or (shape_pressure and len(state.hands[state.current_player]) <= 16)):
        return min(bombs, key=lambda candidate: _response_cost(state, candidate))
    return None


def _pre_first_lead_plan_action(
    state: GameState,
    action: Action,
    fallback: Action | None = None,
) -> Action | None:
    legal_actions = state.legal_actions()
    hand_size = len(state.hands[state.current_player])
    if action.is_pass or hand_size <= 1:
        return None
    non_bomb_leads = [
        candidate
        for candidate in legal_actions
        if not candidate.is_pass and not candidate.is_bomb_family
    ]
    if not non_bomb_leads:
        return None

    selected_turns = _safe_min_play_count(_remaining_after_action(state, action), state.config)
    candidates = list(non_bomb_leads)
    if fallback is not None and not fallback.is_pass and not fallback.is_bomb_family:
        candidates.append(fallback)
    best = min(candidates, key=lambda candidate: _lead_cost(state, candidate))
    best_turns = _safe_min_play_count(_remaining_after_action(state, best), state.config)
    team_pressure = team_turn_count_value(state, state.current_player % 2)
    if best_turns + 2 <= selected_turns:
        return best
    if (
        action.type == ActionType.TRIPLE_WITH_PAIR
        and best.type in {ActionType.PAIR_STRAIGHT, ActionType.PLATE}
        and best_turns + 1 <= selected_turns
    ):
        return best
    if (
        action.type == ActionType.SINGLE
        and best.type != ActionType.SINGLE
        and best_turns <= selected_turns
        and len(best.cards) >= 2
        and team_pressure <= -0.10
    ):
        return best
    return None


def guard_dangerous_opponent_pass(state: GameState, action: Action) -> Action:
    if not action.is_pass or _is_leading(state) or state.last_actor is None:
        return action
    if state.last_actor % 2 == state.current_player % 2:
        return action
    legal_actions = state.legal_actions()
    non_pass = [candidate for candidate in legal_actions if not candidate.is_pass]
    if not non_pass:
        return action

    if _pass_would_clear_to_opponent(state):
        current_turns = _safe_min_play_count(state.hands[state.current_player], state.config)
        non_bombs = [candidate for candidate in non_pass if not candidate.is_bomb_family]
        efficient_non_bombs = [
            candidate
            for candidate in non_bombs
            if _safe_min_play_count(_remaining_after_action(state, candidate), state.config) <= current_turns
        ]
        if efficient_non_bombs:
            return min(efficient_non_bombs, key=lambda candidate: _response_cost(state, candidate))
        if non_bombs and _opponents_near_finish(state):
            return min(non_bombs, key=lambda candidate: _response_cost(state, candidate))

    last_actor_finished = state.last_actor in state.finished
    last_actor_short = len(state.hands[state.last_actor]) <= 3
    if not (last_actor_finished or last_actor_short or _opponents_near_finish(state)):
        return action

    non_bombs = [candidate for candidate in non_pass if not candidate.is_bomb_family]
    if non_bombs:
        return min(non_bombs, key=lambda candidate: _response_cost(state, candidate))
    if last_actor_finished or last_actor_short or _opponent_has_one_card(state):
        return min(non_pass, key=lambda candidate: _response_cost(state, candidate))
    return action


def _pass_would_clear_to_opponent(state: GameState) -> bool:
    try:
        next_state = state.play_action(PASS)
    except Exception:
        return False
    if next_state.last_action is not None:
        return False
    return next_state.current_player % 2 != state.current_player % 2


def _lead_cost(state: GameState, action: Action) -> tuple[int, int, int, int, int]:
    hand_size = len(state.hands[state.current_player])
    main = _main_value(state, action)
    bomb_penalty = 1000 if action.is_bomb_family and hand_size > len(action.cards) else 0
    finish_bonus = -1000 if hand_size == len(action.cards) else 0
    single_lock_penalty = 900 if _opponent_has_one_card(state) and action.type == ActionType.SINGLE and hand_size > 1 else 0
    turn_count = _safe_min_play_count(_remaining_after_action(state, action), state.config)
    combo_bonus = -_combo_priority(action)
    return (finish_bonus + bomb_penalty + single_lock_penalty, turn_count, -action.length, combo_bonus, main + _wild_usage(state, action))


def _response_cost(state: GameState, action: Action) -> tuple[int, int, int, int]:
    finish_bonus = -1000 if len(state.hands[state.current_player]) == len(action.cards) else 0
    bomb_penalty = 1000 if action.is_bomb_family else 0
    turn_count = _safe_min_play_count(_remaining_after_action(state, action), state.config)
    return (finish_bonus + bomb_penalty, turn_count, action.length, _main_value(state, action) + _wild_usage(state, action))


def _remaining_after_action(state: GameState, action: Action) -> tuple:
    remaining = list(state.hands[state.current_player])
    for card in action.cards:
        try:
            remaining.remove(card)
        except ValueError:
            return tuple(state.hands[state.current_player])
    return tuple(remaining)


def _safe_min_play_count(hand: tuple, config) -> int:
    try:
        return min_play_count(hand, config)
    except (MemoryError, RecursionError):
        try:
            return min_play_count(hand, config, exact_limit=6)
        except (MemoryError, RecursionError):
            return len(hand)


def _combo_priority(action: Action) -> int:
    priorities = {
        ActionType.PAIR_STRAIGHT: 6,
        ActionType.PLATE: 6,
        ActionType.STRAIGHT: 5,
        ActionType.TRIPLE_WITH_PAIR: 5,
        ActionType.TRIPLE: 3,
        ActionType.PAIR: 2,
        ActionType.SINGLE: 1,
    }
    return priorities.get(action.type, 0)


def _main_value(state: GameState, action: Action) -> int:
    return action_compare_value(action, state.config)


def _wild_usage(state: GameState, action: Action) -> int:
    return sum(1 for card in action.cards if card.rank == state.config.level_rank and card.suit == state.config.wild_suit)


def _finishing_actions(state: GameState, actions: list[Action]) -> list[Action]:
    hand_size = len(state.hands[state.current_player])
    return [action for action in actions if len(action.cards) == hand_size]


def _partner_takeover_action(state: GameState, actions: list[Action]) -> Action | None:
    hand_size = len(state.hands[state.current_player])
    if hand_size > 5 and not _opponents_near_finish(state):
        return None
    single_card_lock = _single_card_opponent_response_action(state, actions)
    if single_card_lock is not None:
        return single_card_lock
    non_bombs = [action for action in actions if not action.is_bomb_family]
    if not non_bombs:
        return None
    return min(non_bombs, key=lambda action: _response_cost(state, action))


def _single_card_opponent_response_action(state: GameState, actions: list[Action]) -> Action | None:
    if _is_leading(state):
        return None
    if state.last_action is None or state.last_action.type != ActionType.SINGLE:
        return None
    if not _opponent_has_one_card(state):
        return None
    hand_size = len(state.hands[state.current_player])
    singles = [
        action
        for action in actions
        if not action.is_pass and action.type == ActionType.SINGLE and len(action.cards) < hand_size
    ]
    if not singles:
        return None
    non_jokers = [
        action
        for action in singles
        if action.main_rank not in {Rank.SMALL_JOKER, Rank.BIG_JOKER}
    ]
    pool = non_jokers or singles
    return max(pool, key=lambda action: _main_value(state, action))


def _partner_is_winning_trick(state: GameState) -> bool:
    return state.last_actor is not None and state.last_actor % 2 == state.current_player % 2


def _hand_is_all_bomb_material(state: GameState) -> bool:
    hand = state.hands[state.current_player]
    if not hand:
        return False
    jokers = sum(1 for card in hand if card.is_joker)
    if jokers not in {0, 4}:
        return False
    rank_counts = Counter(card.rank for card in hand if not card.is_joker)
    return all(count >= state.config.min_bomb_size for count in rank_counts.values())


def _opponents_near_finish(state: GameState) -> bool:
    return any(
        len(state.hands[player]) <= 4
        for player in range(4)
        if player % 2 != state.current_player % 2 and player not in state.finished
    )


def _opponent_has_one_card(state: GameState) -> bool:
    return any(
        len(state.hands[player]) == 1
        for player in range(4)
        if player % 2 != state.current_player % 2 and player not in state.finished
    )


def _should_spend_bomb(state: GameState) -> bool:
    hand_size = len(state.hands[state.current_player])
    if hand_size <= 4:
        return True
    return _opponents_near_finish(state)


def hand_shape_score(state: GameState, player: int) -> int:
    ranks = Counter(card.rank for card in state.hands[player] if not card.is_joker)
    pairs_or_better = sum(1 for count in ranks.values() if count >= 2)
    bombs = sum(1 for count in ranks.values() if count >= 4)
    jokers = sum(1 for card in state.hands[player] if card.rank in {Rank.SMALL_JOKER, Rank.BIG_JOKER})
    return pairs_or_better + bombs * 3 + jokers
