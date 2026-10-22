# Engine

| Item | Value |
|---|---|
| Engine | **Godot 4.6.3-stable** (ADR 0001) |
| Renderer | Forward+ (ADR 0002) |
| Language | Typed GDScript (ADR 0003); Python 3.13 tooling |
| Lint/format | gdtoolkit 4.5.0: `gdlint`, `gdformat -l 120` |
| CI download | `https://github.com/godotengine/godot-builds/releases/download/4.6.3-stable/Godot_v4.6.3-stable_linux.x86_64.zip` |

**No network path to GitHub releases (cloud sandbox)?** Run `python3 tools/dev/fetch_godot.py` and put `~/.cache/hymn/godot-4.6.3+ds-2/godot` on PATH as `godot` (ADR 0008). Then `tools/ci_local.sh` runs every CI gate.

Change the version only through a new ADR, updating `project.godot` (`config/features`), `.github/workflows/ci.yml` (`GODOT_RELEASE`), and this file together.

## Headless gotchas
- `--headless` uses the dummy renderer: shaders compile and scenes load, but nothing draws. Visual tests need a GPU runner (M1-QA-01).
- Run `--import` once on a fresh checkout before running scenes, or `class_name` lookups fail (the global class cache lives in `.godot/`, which is gitignored).
- The test runner is a *scene* (not `--script`), so autoloads exist during tests.
