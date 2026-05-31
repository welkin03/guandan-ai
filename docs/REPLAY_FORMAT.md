# Replay Format

`tools/play_demo.py` can export a dependency-free, public JSON replay:

```bash
python tools/play_demo.py --seed 21 --trace demo.json
```

Open `tools/replay_viewer.html` in a browser and select the generated file to
step through the game locally.

## Schema

The top-level object contains:

| Field | Description |
| --- | --- |
| `schema_version` | Integer format version, currently `1` |
| `game` | Always `guandan` |
| `seed` | Deterministic deal seed |
| `rule_config` | Public rule settings used for the game |
| `initial` | Public state before the first action |
| `turns` | Ordered action records with `before` and `after` public states |
| `result` | Finish order and partnership scores |

Public states record the current player, current trick, pass count, remaining
hand sizes, and finish order. Traces intentionally omit full player hands so
they remain suitable for sharing as debugging artifacts.
