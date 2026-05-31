# Engineering Lessons

This project did not advance in a straight line. The retained private archive
contains many experiments that were useful precisely because they failed. This
page publishes a selected, sanitized record of those decisions. It intentionally
omits private logs, model weights, machine details, and unreleased configuration.

## Evaluation Discipline

Three rules became non-negotiable:

1. Use paired, seat-swapped gameplay gates. Guandan team-seat effects can make a
   promising model look much stronger than it is.
2. Split value-model validation by whole game or session. Adjacent states from
   one game are too closely related for row-level random splits.
3. Keep older policies in the regression pool. A narrow improvement against one
   opponent style is not a release result.

## Shortcuts That Did Not Survive Gameplay

| Date | Attempt | Evidence | Decision |
| --- | --- | --- | --- |
| 2026-04-28 | Promote an early direct policy from offline metrics | A 100-game self-play gate produced an 85/15 team-seat skew. | Reject. Require paired seat-swapped gates. |
| 2026-04-29 | Validate a value model with random row splits | Adjacent states from the same game leaked across the split and made error metrics look too optimistic. | Reject. Split by whole game or session. |
| 2026-04-29 | Prune candidate actions before search | A larger paired gate reached only 21/40 wins, while the same setup without pruning reached 26/40. | Reject. Tiny smoke checks and offline recall are not enough. |
| 2026-05-03 | Fine-tune narrowly on a small human-loss correction set | The correction regressed against retained older opponents. | Reject. Keep old-pool regression gates. |
| 2026-05-09 | Use Team-Q estimates for direct candidate reranking | The ranking signal was real offline but brittle in gameplay gates. | Keep as diagnostic evidence, not runtime control. |
| 2026-05-12 | Learn one global safety threshold | Among 120 shadow configurations, none passed the combined gate. | Reject. Safety decisions need state-class context. |
| 2026-05-16 | Turn an action-shape pattern into a hard veto | A refined counterfactual slice contained 9 negative, 3 neutral, and 6 positive examples. | Use the slice for mining, not a blunt runtime rule. |
| 2026-05-16 | Treat a remote stability run as a reusable training dataset | A 960-game smoke run was stable, but it had no per-decision traces. | Emit progress and trace rows at the source. |
| 2026-05-17 | Import external replay rows without a replay audit | In a 1,000-episode audit, 134,202 rows were replay-ready and 182 failed due to rule differences. | Replay-audit external data before relabeling. |
| 2026-05-29 | Train a direct policy from game return alone | On 1,200 self-play games, one old exact-retention metric fell from 1.000 to 0.460. | Reject. More volume does not repair noisy credit assignment by itself. |
| 2026-05-29 | Deploy a small all-legal direct neural model | It scored 0/8 against two retained opponents in smoke gates. | Reject. Improve the search teacher before distillation. |
| 2026-05-31 | Apply one action cap to both root and internal search nodes | Removing the accidental root top-28 cap changed one paired smoke gate from 3/6 to 6/6. | Fix. Root and internal-node widths need separate semantics. |
| 2026-05-31 | Treat exact ties as changed counterfactual labels | Three apparent label changes became 3 stable / 0 changed after tie handling was repaired. | Fix. Exact ties must not manufacture labels. |
| 2026-05-31 | Replace root decisions globally with Q-based rules | Larger paired gates showed cross-opponent regressions. | Reject. Use disagreement rows for mining first. |

## What Stayed

The failed routes shaped the public core:

- Rules are explicit and tested separately from policy code.
- Example replays expose only public information.
- Research snapshots include seat-balance fields.
- Experimental signals remain research-only until they pass paired gameplay and
  old-pool regression gates.
- Search traces are treated as first-class evidence, not an afterthought.

The compact decision ledger is available in
[`research/experiment_decisions.csv`](../research/experiment_decisions.csv).
