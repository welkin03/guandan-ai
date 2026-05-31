# Guandan AI

[![Tests](https://github.com/welkin03/guandan-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/welkin03/guandan-ai/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Guandan AI is a compact, testable Python rules engine and heuristic AI starter
kit for Guandan (Guan Dan), a four-player partnership card game played with two
decks. The project focuses on the parts that make Guandan interesting for game
AI research: combinatorial legal-action generation, wildcards, partnership
play, trick control, and imperfect information.

This repository is the public core of a larger research project. It is useful
on its own for rules experiments, baseline agents, and reproducible AI
prototyping. Training data, model checkpoints, private battle logs, and
machine-specific configuration are intentionally excluded.

## Why Guandan?

Guandan is widely played in China, but open and reusable AI tooling for the
game is still limited. Unlike perfect-information board games, Guandan combines:

- hidden opponent hands;
- variable-length combinatorial actions;
- two-versus-two partnership decisions;
- wildcard interpretation;
- tactical passing and trick-control choices.

That makes it a practical environment for studying imperfect-information game
AI without requiring a large framework.

## Included

- A 108-card two-deck representation and parser.
- Rule classification for singles, pairs, triples, triple-with-pair,
  straights, pair straights, plates, bombs, straight flushes, and joker bombs.
- Wildcard handling for the heart card of the level rank.
- Legal response generation and action comparison.
- Four-player game state transitions, finishing order, and partnership score.
- A lightweight heuristic policy with tactical safety guards.
- A deterministic self-play demo and unit tests.

## Quick Start

Guandan AI currently requires Python 3.11 or newer and has no runtime
dependencies.

```bash
git clone https://github.com/welkin03/guandan-ai.git
cd guandan-ai
python -m unittest discover -s tests -v
python tools/play_demo.py --seed 21
python tools/play_demo.py --seed 21 --trace demo.json
```

Use the library directly:

```python
from guandan import Rank, RuleConfig, classify, parse_cards

config = RuleConfig(level_rank=Rank.TWO)
action = classify(parse_cards("C3 D3 H2"), config)

print(action.type)       # triple
print(action.main_rank)  # 3
```

## Rule Scope

The current engine implements a commonly used competitive core:

- two decks and four players;
- the heart card of the level rank as a wildcard;
- fixed five-card straights, three consecutive pairs, and two consecutive
  triples;
- bomb ordering: four-card bomb, five-card bomb, straight flush, six-card or
  larger bomb, then joker bomb;
- partner lead inheritance after a player finishes and the trick clears.

Regional scoring, tribute, return-card, and promotion-match rules vary. They
are planned as configurable extensions.

## Project Status

This is an early open-source snapshot, released in May 2026. The core rules
engine and baseline policy are usable and covered by tests. Neural checkpoints
and experimental search stacks are not published as live defaults because they
need a cleaner release process and reproducible evaluation assets.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[docs/ROADMAP.md](docs/ROADMAP.md) for the next steps. The self-play demo can
also export a public JSON trace for the dependency-free
[replay viewer](tools/replay_viewer.html); see
[docs/REPLAY_FORMAT.md](docs/REPLAY_FORMAT.md).

## Contributing

Issues and pull requests are welcome, especially for regional rule variants,
regression cases, documentation, and evaluation tooling. Please read
[CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

MIT. See [LICENSE](LICENSE).
