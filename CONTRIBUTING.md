# Contributing

Thanks for helping improve Guandan AI.

## Good First Contributions

- Add a regression test for a legal-action edge case.
- Document a regional Guandan rule variant.
- Improve the CLI demo output.
- Propose a configurable implementation for tribute and return-card rules.

## Development

Use Python 3.11 or newer:

```bash
python -m unittest discover -s tests -v
python tools/play_demo.py --seed 21
```

Keep changes small and include tests for behavior changes. If a rule differs
across regions, describe the variant and prefer an opt-in configuration flag.

## Pull Requests

Please explain:

- the rule or behavior being changed;
- why the change is needed;
- the test or reproducible example used to validate it.
