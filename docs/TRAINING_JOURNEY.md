# Training Journey

This page summarizes the month-long training path behind the public Guandan AI
snapshot. It is intentionally a research history, not a claim that every
experiment became a release. Many branches were rejected because they improved
one opponent style while regressing another, or because they depended on
full-information inputs that are not fair for public play.

## Public Boundary

The public repository includes sanitized ledgers, architecture metadata,
synthetic record examples, and aggregate evaluation results. It does not
include private battle logs, raw human-game records, trained weights, local
paths, machine configuration, or remote job scripts.

The most useful public evidence is therefore not a checkpoint file. It is the
sequence of decisions: what was tried, what signal it trained from, what gate
accepted or rejected it, and what the next route learned.

## Route Map

| Period | Route | What Changed | Public Decision |
| --- | --- | --- | --- |
| Apr 28-29 | Public policy/value bootstrap | Paired direct gates, search labels, guard-aligned policy training, whole-game value calibration. | v7-v11 formed the first stable public-information line. |
| May 2-5 | Portfolio, loss mining, exact-race labels | Multi-model candidate pools, human-loss repairs, exact short-race supervision. | Useful research signal, but several direct checkpoints were rejected. |
| May 5-8 | Full-state and human-hard training | Full-information teacher/sparring models, pre-first-finish guards, pass specialist probes. | Kept as diagnosis or research-only where gates were too narrow. |
| May 9-17 | Team-Q, rejection safety, belief-PUCT | Role/risk heads, rejection-first sweeps, three-computer trace collection, replay counterfactuals. | Stable infrastructure and useful labels, but no runtime promotion. |
| May 29-31 | Full-information teacher search | Return-only RL and all-legal full-info search uncovered root-action and trajectory bugs. | Direct argmax routes were rejected; search/teacher route continued. |
| Jun 1-3 | Outcome-oracle teacher and students | V45 outcome teacher, policy-only student checks, V46 public belief distillation. | Teacher data became useful; student routes still require retention gates. |

## Early Public Policy/Value Route

The first retained line used candidate-action scoring because Guandan has a
variable legal-action set. A state can have only a forced pass or dozens of
candidate combinations, so the model scores each legal action against the
public state rather than using a fixed output class.

The early sequence produced several important process rules:

- A v4-style branch was rejected after a 100-game self-play seat-skew check.
- v7 passed paired gates against older baselines and became an early public
  policy baseline.
- v8 used search-mix labels and beat v7 on a 200-game paired gate.
- v9-v11 added broader hard states, self-play search labels, and guard-aligned
  labels.
- Two offline-strong v11 attempts were rejected before the guard-aligned v11
  branch passed gameplay.
- Value validation moved to whole-game/session splits because row-level splits
  leaked adjacent states from the same deal.

That is why the repository emphasizes paired swapped-seat gates and whole-game
splits instead of presenting training loss as release evidence.

## Portfolio And Loss-Mining Route

The next route tried to use older policies as an ensemble of candidate
advisors. This was valuable because v5, v6, v7, v11, and v18 exposed different
counterplay styles. It also revealed a recurring failure mode: a candidate could
look better against one opponent family while losing strength against another.

Examples from this branch:

- v18, rooted in v5-style hard states, passed several direct gates but regressed
  when combined with the older live-search/value stack.
- v19 overfit a tiny human-loss correction and was rejected.
- v20 portfolio search improved some small matched seeds but still had
  sample-size and seat-gap concerns.
- v23 strengthened old-pool matchups, but only tied v18 on the larger combined
  check.
- v24 and v24light showed that fine-tuning on v18 losses could make the old-pool
  balance worse.

The lesson was not "ensembles do not work." The lesson was that portfolio
coverage must be judged across the old opponent pool, not only on the newest
failure case.

## Exact-Race And Full-State Route

Exact short-race labels fixed a narrow but costly endgame class. They were good
as a tactical/search module, but not always compressible into the current
public-policy feature set. Some decisions require information about hidden
remaining hands.

The full-state route made that separation explicit. Full-information teachers
can see all four hands, which makes them useful for supervision and sparring,
but unfair as live public-information agents. The public project therefore
documents them as teacher artifacts rather than released runtime models.

## Human-Hard, Risk, And Pass-Specialist Route

Human battle losses produced a useful hard-state stream. Those records led to
pre-first-finish pressure guards, human-hard policy attempts, stage-risk
diagnostics, and pass-specialist probes.

Several results were promising offline but not clean enough for default use:

- v32 improved agreement with human-hard labels but regressed against v6.
- v32b repaired part of that regression but stayed baseline-level rather than
  dominant.
- v36 improved the combined small old-pool score versus v32b, but its v18 and
  human-hard diagnostics were not good enough.
- A pass guard improved bad pass-with-response labels, but standalone runtime
  override gates regressed older styles.
- The later pass-intervene stack was safer, yet the gain was still too small for
  promotion.

This is one of the most important histories to show publicly: the project did
not simply add rules after a loss. It kept the older opponent pool in the loop
so narrow repairs could not silently become broad regressions.

## Team-Q And Rejection-Safety Route

Team-Q and risk heads tested whether role, pressure, and pass danger could be
learned as auxiliary signals. The role/risk model produced useful diagnostics,
but pass danger was not safe as a hard gate. Later Phase3 rejection-safety
sweeps tested many hand-built and model-assisted gate configurations. Most
hand-built variants failed, which pushed the project toward counterfactual
labeling rather than broad handcrafted overrides.

That route is useful public evidence because it explains why the project now
separates:

- diagnostic heads;
- proposal-only guards;
- counterfactual audit queues;
- runtime/default promotion.

## Belief-PUCT And Replay Counterfactuals

The belief-PUCT route was a distributed systems and data-quality milestone more
than a strength breakthrough. A three-computer smoke completed 960 games and
52,352 decisions without crashes. A larger head-to-head night run completed
5,400 games and produced 236,802 decision trace rows, but the win rates failed
the strength target.

The failed strength result still became useful training infrastructure:

- trace mining identified loss rows, PUCT disagreements, selected-action
  disagreements, and guard rewrites;
- replay-CF queues separated weak final-outcome labels from usable
  counterfactual evidence;
- the first replay method exposed determinism gaps, so later traces stored a
  public-belief payload directly;
- public-payload CF8 and CF32 ran with zero skips and became a cleaner
  supervision source.

This branch is included publicly because it shows a real research loop:
distributed run, failed strength gate, trace mining, counterfactual audit,
schema repair, then cleaner labels.

## Full-Information Teacher And Public Distillation

The V43 and V44 routes showed two things that were easy to miss:

- return-only full-information RL can improve training loss while destroying
  retention on exact older labels;
- direct all-legal full-information argmax can have good offline prior metrics
  while failing head-to-head smoke gates.

The V45 outcome-oracle route then used bounded outcome search and paired gates
to produce a stronger teacher. The first policy-only student fit teacher labels
better but shifted gameplay trajectories, so it stayed an offline artifact.

V46 began the public-information conversion: sample hidden hands, ask the V45
teacher to score public candidate sets, then retain a public-policy anchor so
the student does not drift away from older styles. Pure V45 labels drifted too
much; anchor labels were necessary.

## Why Rejections Are Published

For this project, a rejected route is not wasted work. Rejections define the
release boundary:

- no promotion from offline accuracy alone;
- no full-information model as a fair public runtime model;
- no broad pass/pressure override without old-pool retention;
- no default change from a small same-seed smoke;
- no distillation route without public-information conversion and anchor checks.

The compact public ledger for this page is
[`research/training_attempts.csv`](../research/training_attempts.csv).
