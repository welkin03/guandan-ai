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
prototyping. Large training datasets, model checkpoints, private battle logs, and
machine-specific configuration are intentionally excluded.

The repository also exposes a sanitized learning track: candidate-action
policy/value architecture metadata, synthetic training-record examples, and
milestone ledgers for the policy/value, full-information teacher, and student
distillation routes. See
[docs/NEURAL_ARCHITECTURE.md](docs/NEURAL_ARCHITECTURE.md).

The public snapshot also includes a sanitized research archive: selected
paired-gate records from the pre-public development history, aggregate results,
and shareable replay examples. See [docs/RESEARCH_HISTORY.md](docs/RESEARCH_HISTORY.md)
and [research/README.md](research/README.md). The selected failed routes and the
anonymized three-computer workflow are documented in
[docs/ENGINEERING_LESSONS.md](docs/ENGINEERING_LESSONS.md) and
[docs/DISTRIBUTED_RESEARCH.md](docs/DISTRIBUTED_RESEARCH.md). A June 2026
update is available at
[docs/RECENT_PROGRESS_2026_06.md](docs/RECENT_PROGRESS_2026_06.md).

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
- Public neural-learning architecture metadata and training-record schema
  examples.
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
python tools/summarize_gate_csv.py research/gates/*.csv
python tools/inspect_learning_schema.py
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
