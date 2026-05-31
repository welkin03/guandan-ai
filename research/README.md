# Sanitized Research Snapshot

This directory publishes a small, inspectable subset of the project's
pre-public evaluation history.

## Contents

- `selected_gate_results.csv`: one aggregate row per selected historical gate.
- `gates/*.csv`: sanitized per-game records for eight paired gates.

The snapshot contains 1,280 game rows from April 28-29, 2026. It covers direct
policy comparisons and two early public-information search gates.

## Privacy Boundary

The original private records were reduced to:

| Column | Meaning |
| --- | --- |
| `deal_id` | Pair identifier within one gate |
| `level_rank` | Level rank used for the game |
| `candidate_team` | Candidate seat group, `0` or `1` |
| `finish_order` | Player order at game end |
| `candidate_score` | Partnership score from the candidate perspective |
| `candidate_win` | Whether the candidate partnership won |
| `candidate_utility` | Single-game candidate utility |
| `steps` | Number of actions in the game |
| `search_decisions` | Search decisions made, when applicable |

Random seeds, machine paths, model checkpoints, private battle logs, and
machine-specific configuration are not included.

## Summaries

Recompute metrics from the included CSV files:

```bash
python tools/summarize_gate_csv.py research/gates/*.csv
```

The historical neural checkpoints are intentionally not published in this
initial snapshot, so these CSV files document earlier evaluation evidence
rather than a fully reproducible neural benchmark.
