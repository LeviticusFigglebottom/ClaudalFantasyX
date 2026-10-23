# QA & Tools

| Check | Command | Where it runs |
|---|---|---|
| Data validator | `python3 tools/validate_data.py` | CI `tools` job |
| Validator tests | `python3 -m unittest discover -s tools/tests` | CI `tools` job |
| Task board | `python3 tools/taskboard.py --check` | CI `tools` job |
| GDScript lint/format | `gdlint game tests` / `gdformat -l 120 --check game tests` | CI `tools` job |
| Godot tests | `godot --headless --path . res://tests/run_tests.tscn` | CI `godot` job |
| Coverage (battle/, progression/) | `python3 tools/coverage/run_coverage.py` (ADR 0013, [coverage.md](coverage.md)) | `tools/ci_local.sh`; CI `godot` job |
| Audio synth tests | `python3 -m unittest discover -s tools/audio/tests -p "test_*.py"` | `tools/ci_local.sh` |
| Screenshot manifest | `python3 tools/screenshots/compare.py --manifest-only` | CI `tools` job |
| Screenshot regression | `tools/screenshots/capture.sh && python3 tools/screenshots/compare.py` ([screenshots.md](screenshots.md)) | `tools/ci_local.sh`; CI `screenshots` job (non-gating) |
| Blender asset rebuild | `python3 tools/dev/verify_blender_builds.py [--all]` ([blender_builds.md](blender_builds.md)) | `tools/ci_local.sh` (`HYMN_SKIP_BLENDER=1` skips); CI `blender` job (non-gating) |

Banned terms: `tools/banned_terms.txt`. Matching is whole-word; the `i:` prefix makes a term case-insensitive. The scan covers `game/`, `assets_src/`, `docs/kb/story/`, and `docs/kb/glossary.md`. When a doc needs to talk *about* a banned term, point at the list instead of quoting the term.
