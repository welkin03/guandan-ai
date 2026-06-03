# Neural Architecture

The public repository now includes the learning route used by the larger
Guandan AI project, without publishing private checkpoints or raw logs. The
goal is to make the deep-learning work inspectable while keeping the release
boundary honest.

## Candidate-Action Scoring

Guandan has a variable legal-action set: one state may have only a forced pass,
while another may have dozens or hundreds of legal combinations. The project
therefore uses candidate-action scoring instead of a fixed softmax over every
possible card subset.

The public policy/value architecture has:

- a public-state feature vector;
- one feature vector per legal candidate action;
- a state trunk;
- a state-action policy scorer;
- value heads for team win probability and single-game utility.

The public module [`src/guandan/learning.py`](../src/guandan/learning.py)
contains inspectable architecture metadata and an optional PyTorch factory. The
package still has no required neural dependency; PyTorch is only needed if a
caller explicitly builds the optional network.

## Training Signals

The historical training route used several label families:

| Signal | Purpose | Release boundary |
| --- | --- | --- |
| Behavior/self-play labels | Bootstrap a direct public policy. | Must pass paired gameplay gates. |
| Search labels | Teach the policy to imitate stronger lookahead. | Offline accuracy is not enough. |
| Whole-game value labels | Calibrate win and utility heads. | Split by whole game/session, not by adjacent rows. |
| Human-loss hard states | Repair repeated tactical failures. | Must not regress old-pool opponents. |
| Full-information teacher labels | Distill slow search into smaller students. | Teacher-only until public-information conversion is validated. |

The example schema lives under
[`examples/training/`](../examples/training/). It can be inspected with:

```bash
python tools/inspect_learning_schema.py
```

## Historical Route

The project moved through several learning approaches:

| Date | Route | Outcome |
| --- | --- | --- |
| 2026-04-28 | Early public policy checkpoints | Seat-swapped evaluation became mandatory after seat-bias failures. |
| 2026-04-29 | v8-v11 policy/value route | v11 guard-aligned branch retained; two offline-strong v11 attempts were rejected by gameplay. |
| 2026-05-03 | Portfolio and loss distillation | Mixed opponent-style tradeoffs; kept research-only. |
| 2026-05-05 | Full-state exact-race distillation | Useful as teacher/sparring, but not fair public-information play. |
| 2026-06-02 | V45 outcome-oracle teacher | Cleared the internal research target for policy-only student data. |
| 2026-06-03 | V45 policy-only student | Fit teacher labels better, but gameplay checks had opponent regressions. |
| 2026-06-03 | V46 public belief distillation | Viable first pass; anchor labels are necessary to avoid drift. |

The compact ledger is available at
[`research/neural_training_milestones.csv`](../research/neural_training_milestones.csv).
A fuller month-long route ledger is documented in
[`docs/TRAINING_JOURNEY.md`](TRAINING_JOURNEY.md) and
[`research/training_attempts.csv`](../research/training_attempts.csv).

## Why Full-Information Teachers Are Separate

Full-information teachers can see all four hands. That makes them useful for
offline supervision and diagnosis, but unfair as a public-information runtime
agent. The route is:

1. Build a slow teacher that clears paired outcome gates.
2. Export policy-only teacher records.
3. Train a smaller student without changing the value head unless explicitly
   authorized.
4. Test the student by fresh paired swapped-seat outcomes.
5. Convert teacher knowledge into public-information play through hidden-hand
   sampling and retention anchors.

This is why some models are described as "valid offline artifacts" while still
being rejected for runtime or default use.

## What Is Public Now

This repository includes:

- neural architecture metadata;
- a runnable schema inspector;
- synthetic training-record examples;
- public milestone ledgers;
- sanitized outcome evidence and rejected-experiment records.

It does not include:

- trained neural weights;
- raw private battle logs;
- local machine paths or remote job scripts;
- hidden-hand private records from human games.
