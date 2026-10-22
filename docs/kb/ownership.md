# Scene and Asset Ownership

Claim a path glob before editing `.tscn` or `.tres` files or assets (SPEC §5.3). Release a claim by deleting its row. Never edit another role's claimed paths: open a request task instead.

| Role | Path glob | Since | Session |
|---|---|---|---|
| Lead | `SPEC.md`, `CLAUDE.md`, `docs/kb/STATUS.md`, `docs/kb/decisions/**` | 2026-10-22 | lead-bootstrap |
| Systems Architect | `game/core/**`, `project.godot`, `.github/**`, `tools/validate_data.py` | 2026-10-22 | lead-bootstrap (acting) |
| Combat | `game/battle/**`, `game/data/battle/**` | 2026-10-22 | lead-bootstrap (acting) |
| Narrative | `docs/kb/story/**`, `game/data/dialogue/**` | 2026-10-22 | narrative-stream-1 |
| Audio | `tools/audio/**`, `assets_src/music/**`, `assets_src/sfx/**`, `assets/audio/**`, `docs/kb/audio/**` | 2026-10-22 | audio-stream-1 |
| QA & Tools | `tests/test_case.gd`, `tests/run_tests.*`, `tests/error_counter.gd`, `tools/taskboard.py`, `tools/screenshots/**` | 2026-10-22 | lead-bootstrap (acting) |
