# Recent Progress: June 2026

This page summarizes selected project progress from June 1-3, 2026. It is a
sanitized public snapshot of a larger private research archive. Model weights,
private logs, machine names, network details, local paths, and credentials are
not published here.

## Current Route

The active research route is V45: build a slow but strong full-information
teacher before distilling a smaller student. This is intentionally separate from
the public-information runtime problem. The teacher sees complete game state and
is used for offline research, not fair live play.

The release discipline stayed the same:

- judge progress by paired same-deal swapped-seat games;
- compare against multiple retained old-pool opponents;
- require no opponent-style regression;
- keep counterfactual and frontier metrics diagnostic until confirmed by game
  outcomes;
- do not promote a student just because it fits teacher labels better.

## Outcome-Oracle Teacher

The slow teacher route moved from "promising" to "ready for student-data
preparation" after targeted outcome-gated sweeps.

The retained teacher configuration is a bounded full-information outcome oracle:

- all legal root actions are available;
- expensive continuation checks are only used on small enough branches;
- the per-game oracle decision budget is capped;
- overrides require a score margin and non-decreasing continuation win rate;
- ambiguous low-margin pass overrides get extra refinement;
- broad hard pass or bomb-pass rules remain disabled.

Fresh paired swapped-seat evidence after the June 2 sweep57 package:

| Opponent | Wins | Win rate |
| --- | ---: | ---: |
| v5 | 41/44 | 0.9318 |
| v6 | 50/60 | 0.8333 |
| v7 | 37/44 | 0.8409 |
| v18 | 38/44 | 0.8636 |
| total | 166/192 | 0.8646 |

Decision: the slow full-information teacher cleared the internal research
target for preparing policy-only student data. This is still an offline teacher
result, not a public runtime release.

## Three-Computer Evidence

A June 1 three-node holdout produced 176 paired swapped-seat games for a
consensus-veto teacher candidate. The aggregate crossed 80% overall, but v6 and
v18 were still below the per-opponent target:

| Opponent | Baseline | Candidate | Candidate rate |
| --- | ---: | ---: | ---: |
| v5 | 24/44 | 40/44 | 0.9091 |
| v6 | 19/44 | 35/44 | 0.7955 |
| v7 | 22/44 | 36/44 | 0.8182 |
| v18 | 21/44 | 32/44 | 0.7273 |
| total | 86/176 | 143/176 | 0.8125 |

Decision: useful evidence, but not enough for student training at that point.
The later June 2 work repaired this by focusing on the weaker opponent styles.

## Semantics-Preserving Optimization

The rules and hand-evaluation code was optimized without changing legal
behavior:

| Check | Result |
| --- | --- |
| Full unit suite | 106 tests passed |
| Random legacy hand-turn equivalence | 2,880 small hands matched |
| Recorded legal-action regression | 5,445 retained states matched |
| Real-trace hand-turn digest | unchanged |

Microbenchmarks on the same 5,445 retained states:

| Benchmark | Before | After cold | After warm |
| --- | ---: | ---: | ---: |
| Action generation | 10.67s | 9.09s | 2.06s |
| Exact hand-turn estimate | 40.96s | 20.40s | 6.89s |

Decision: keep the optimization. Do not globally collapse suit-aware actions;
natural suits can still affect future straight-flush material and replay state.

## Student Distillation

After the teacher gate cleared, a policy-only student was trained from 1,041
teacher records across 48 game groups. The data uses policy targets only:
`value_target_weight = 0.0`.

Freeze audit:

- the state encoder stayed unchanged;
- the value head stayed unchanged;
- only action-scoring and policy-head parameters changed.

Teacher-label fit improved on the full package:

| Model | Top1 | Top3 | Policy CE |
| --- | ---: | ---: | ---: |
| base iter2 | 0.7128 | 0.9289 | 1.1420 |
| policy-only student | 0.7416 | 0.9395 | 0.9402 |

Fresh direct gameplay smokes were mixed:

| Opponent | Base direct | Student direct |
| --- | ---: | ---: |
| v5 | 4/8 | 6/8 |
| v6 | 6/8 | 4/8 |
| v7 | 1/8 | 3/8 |
| v18 | 3/8 | 1/8 |

The student was then tested as the oracle baseline/prior. That also failed the
cross-opponent veto:

| Opponent | Base oracle | Student oracle |
| --- | ---: | ---: |
| v5 | 4/4 | 3/4 |
| v6 | 4/4 | 4/4 |
| v7 | 4/4 | 3/4 |
| v18 | 3/4 | 4/4 |
| total | 15/16 | 14/16 |

Decision: the student is a valid offline distillation artifact, but it is not a
retained direct gameplay checkpoint and not a retained oracle baseline.

## Public Ledgers

The compact CSV snapshots for this page are:

- [`research/v45_teacher_progress.csv`](../research/v45_teacher_progress.csv)
- [`research/v45_student_followups.csv`](../research/v45_student_followups.csv)
