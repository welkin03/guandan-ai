from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from .cards import Card
from .rules import Action, PASS, RuleConfig, can_play_over, classify, legal_responses

PlayerId: TypeAlias = int


@dataclass(frozen=True)
class GameState:
    hands: tuple[tuple[Card, ...], tuple[Card, ...], tuple[Card, ...], tuple[Card, ...]]
    current_player: PlayerId
    last_action: Action | None = None
    last_actor: PlayerId | None = None
    consecutive_passes: int = 0
    finished: tuple[PlayerId, ...] = ()
    config: RuleConfig = RuleConfig()

    def legal_actions(self) -> list[Action]:
        if self.current_player in self.finished:
            return []
        incumbent = None if self.last_actor == self.current_player else self.last_action
        return legal_responses(self.hands[self.current_player], incumbent, self.config)

    def play(self, cards: list[Card] | tuple[Card, ...]) -> "GameState":
        action = classify(cards, self.config)
        if not can_play_over(action, None if self.last_actor == self.current_player else self.last_action, self.config):
            raise ValueError("Illegal action")
        return self.play_action(action)

    def play_action(self, action: Action) -> "GameState":
        if self.current_player in self.finished:
            raise ValueError("Illegal action")
        incumbent = None if self.last_actor == self.current_player else self.last_action
        if action.is_pass:
            if not can_play_over(action, incumbent, self.config):
                raise ValueError("Illegal action")
        else:
            if not _hand_contains_cards(self.hands[self.current_player], action.cards):
                raise ValueError("Illegal action")
            classified = classify(action.cards, self.config)
            if not can_play_over(classified, incumbent, self.config):
                raise ValueError("Illegal action")
            action = classified
        if action is None:
            raise ValueError("Illegal action")

        hands = [list(hand) for hand in self.hands]
        last_action = self.last_action
        last_actor = self.last_actor
        consecutive_passes = self.consecutive_passes
        finished = list(self.finished)

        if action.is_pass:
            consecutive_passes += 1
        else:
            for card in action.cards:
                hands[self.current_player].remove(card)
            last_action = action
            last_actor = self.current_player
            consecutive_passes = 0
            if not hands[self.current_player] and self.current_player not in finished:
                finished.append(self.current_player)

        next_player = _next_player(self.current_player, tuple(finished))
        if consecutive_passes >= _passes_required_to_clear(last_actor, tuple(finished)):
            next_player = _next_leader_after_clear(last_actor, tuple(finished))
            last_action = None
            last_actor = None
            consecutive_passes = 0

        return GameState(
            hands=tuple(tuple(hand) for hand in hands),  # type: ignore[arg-type]
            current_player=next_player,
            last_action=last_action,
            last_actor=last_actor,
            consecutive_passes=consecutive_passes,
            finished=tuple(finished),
            config=self.config,
        )

    def skip_finished_player(self) -> "GameState":
        if self.current_player not in self.finished:
            return self
        return GameState(
            hands=self.hands,
            current_player=_next_player(self.current_player, self.finished),
            last_action=self.last_action,
            last_actor=self.last_actor,
            consecutive_passes=self.consecutive_passes,
            finished=self.finished,
            config=self.config,
        )

    def is_terminal(self) -> bool:
        if len(self.finished) >= 3:
            return True
        return len(self.finished) >= 2 and self.finished[0] % 2 == self.finished[1] % 2

    def finish_order(self) -> tuple[PlayerId, ...]:
        if len(self.finished) == 4:
            return self.finished
        remaining = tuple(player for player in range(4) if player not in self.finished)
        return self.finished + remaining

    def team_score(self, team: int) -> int:
        order = self.finish_order()
        first_player = order[0]
        first_team = first_player % 2
        partner = (first_player + 2) % 4
        partner_place = order.index(partner) + 1
        upgrade = {2: 3, 3: 2, 4: 1}[partner_place]
        return upgrade if team == first_team else -upgrade

    def team_win(self, team: int) -> int:
        return 1 if self.team_score(team) > 0 else -1

    def team_single_game_utility(self, team: int) -> float:
        score = self.team_score(team)
        if score > 0:
            return 1.0 + 0.1 * (score - 1)
        return -1.0 + 0.1 * (score + 1)


def _hand_contains_cards(hand: tuple[Card, ...], cards: tuple[Card, ...]) -> bool:
    remaining = list(hand)
    for card in cards:
        try:
            remaining.remove(card)
        except ValueError:
            return False
    return True


def _active_player_count(finished: tuple[PlayerId, ...]) -> int:
    return 4 - len(finished)


def _passes_required_to_clear(last_actor: PlayerId | None, finished: tuple[PlayerId, ...]) -> int:
    active_count = _active_player_count(finished)
    if last_actor is None:
        return active_count
    return active_count if last_actor in finished else active_count - 1


def _next_player(current: PlayerId, finished: tuple[PlayerId, ...]) -> PlayerId:
    player = (current + 1) % 4
    while player in finished:
        player = (player + 1) % 4
    return player


def _partner(player: PlayerId) -> PlayerId:
    return (player + 2) % 4


def _next_leader_after_clear(last_actor: PlayerId | None, finished: tuple[PlayerId, ...]) -> PlayerId:
    if last_actor is None:
        return _next_player(0, finished)
    if last_actor not in finished:
        return last_actor
    partner = _partner(last_actor)
    if partner not in finished:
        return partner
    return _next_player(last_actor, finished)
