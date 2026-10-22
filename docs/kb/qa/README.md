# QA & Tools

| Check | Command | Where it runs |
|---|---|---|
| Data validator | `python3 tools/validate_data.py` | CI `tools` job |
| Validator tests | `python3 -m unittest discover -s tools/tests` | CI `tools` job |
| Task board | `python3 tools/taskboard.py --check` | CI `tools` job |
| GDScript lint/format | `gdlint game tests` / `gdformat -l 120 --check game tests` | CI `tools` job |
| Godot tests | `godot --headless --path . res://tests/run_tests.tscn` | CI `godot` job |
| Screenshots | `python3 tools/screenshots/compare.py` (stub) | CI `tools` job |

Banned terms: `tools/banned_terms.txt`. Matching is whole-word; the `i:` prefix makes a term case-insensitive. The scan covers `game/`, `assets_src/`, `docs/kb/story/`, and `docs/kb/glossary.md`. When a doc needs to talk *about* a banned term, point at the list instead of quoting the term.
