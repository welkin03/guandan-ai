# Distributed Research Workflow

Some Guandan experiments are naturally shardable: multi-seed evaluation,
counterfactual labeling, search traces, and grid sweeps. The private research
environment used three computers to run these jobs without changing the live
battle stack.

This page describes the workflow in anonymized form. It does not publish host
names, usernames, network addresses, credential locations, or remote scripts.

## Roles

| Role | Responsibility |
| --- | --- |
| Coordinator node | Stores canonical artifacts, prepares small job manifests, merges pulled results, and runs final validation. |
| Worker node A | Runs long evaluation and trace shards when available. |
| Worker node B | Runs supplemental shards, medium grids, and independent checks. |

The three-node setup is reserved for workloads that are easy to divide and
likely to take at least 30 to 60 minutes. Short smoke tests stay local unless an
independent environment check is part of the experiment.

## Selected Runs

| Date | Workload | Nodes | Scale | Result |
| --- | --- | ---: | --- | --- |
| 2026-05-11 | Conservative adapter multi-seed sweep | 3 | 17 final-config seeds | 8 seeds passed offline gates. Matching dataset digests were checked across all nodes. The result remained proposal-only. |
| 2026-05-12 | Safety-head follow-up | 2 | 12 seeds and 120 shadow configurations | 7 seeds passed internal hard-label gates, but 0 shadow configurations passed the combined gate. The head stayed diagnostic-only. |
| 2026-05-16 | Belief-search stability smoke | 3 | 960 games and 52,352 search decisions | Completed without crashes. This established stability, not strength. |
| 2026-05-17 | Belief-search night evaluation | 3 | 5,400 games and 236,802 decision-trace rows | The candidate lost its strength gates, but the traces became useful mining data. |
| 2026-05-17 | Concurrent trace and counterfactual collection | 3 | Parallel trace shards plus coordinator-side validation | Kept offline-only. The orchestration was useful for diagnostics without affecting runtime defaults. |

The night evaluation compared the belief-search candidate with three retained
opponents. Its win rates were 0.423, 0.432, and 0.408. Publishing a negative
result matters here: distributed compute increased the amount of evidence, but
did not justify promotion.

## Operational Lessons

The distributed experiments also exposed engineering mistakes that local runs
did not:

- Stop after bounded remote-authentication attempts and fix configuration before
  retrying.
- Treat optional diagnostic dependencies as fail-open when they are not
  authorized to affect actions.
- Redirect background-process output so launchers do not inherit handles and
  appear to hang.
- Emit progress and per-decision traces at the worker source.
- Verify pulled packages with checksums before aggregation.
- Tie keep-awake behavior to the worker process so completed jobs leave no stale
  blockers.
- Do not wait for the slowest worker unless the decision genuinely requires its
  shard.

The aggregate ledger is available in
[`research/distributed_runs.csv`](../research/distributed_runs.csv).
