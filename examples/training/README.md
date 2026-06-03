# Training Record Examples

This directory contains tiny synthetic examples of the public policy/value
record schema. They are not training data and are not derived from private
battle logs.

Validate them with:

```bash
python tools/inspect_learning_schema.py
python tools/inspect_learning_schema.py --json
```

The schema mirrors the research route:

- `state`: public or known-team state information;
- `legal_actions`: all legal candidate actions considered for the decision;
- `candidate_scores`: teacher or search scores aligned with the candidates;
- `selected_index`: the chosen candidate;
- `target_win` and `target_utility`: optional value targets.
