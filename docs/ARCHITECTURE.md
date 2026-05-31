# Architecture

The public repository is deliberately small. It exposes a stable core that can
support several AI approaches without requiring private training artifacts.

## Modules

| Module | Responsibility |
| --- | --- |
| `cards.py` | Card types, two-deck construction, and parser |
| `rules.py` | Action classification, generation, and comparison |
| `state.py` | Four-player state transitions and scoring |
| `deal.py` | Deterministic deals and hidden-hand sampling |
| `hand_eval.py` | Lightweight hand-shape and turn-count estimates |
| `policy.py` | Heuristic baseline and tactical guards |
| `replay.py` | Public JSON replay serialization |
| `research/` | Sanitized historical gate records and aggregates |
| `examples/replays/` | Shareable public self-play traces |

## Research Direction

The long-term direction is an imperfect-information partnership AI:

1. Encode public state, known teammate cards, played cards, and hand counts.
2. Sample opponent hands consistent with public information.
3. Rank legal candidate actions with a policy model.
4. Search over sampled hidden states.
5. Evaluate candidates against deterministic regression cases and fixed-seed
   head-to-head gates before release.

The public baseline stays dependency-free so contributors can test rules and
heuristics before adding optional machine-learning components.
