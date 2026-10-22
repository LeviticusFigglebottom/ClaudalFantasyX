# Scene and Asset Ownership

Claim a path glob before editing `.tscn` or `.tres` files or assets (SPEC §5.3). Release a claim by deleting its row. **Shared files** (loc CSVs, flags.tres, PROVENANCE.md, banned_terms.txt, validate_data.py, formulas.md, glossary.md) are append-only for non-owners; see CLAUDE.md §5. Never edit another role's claimed paths: open a request task instead.

| Role | Path glob | Since | Session |
|---|---|---|---|
| Lead | `SPEC.md`, `CLAUDE.md`, `docs/kb/STATUS.md`, `docs/kb/decisions/**` | 2026-10-22 | lead-bootstrap |
| Systems Architect | `game/core/**`, `project.godot`, `.github/**`, `tools/validate_data.py` | 2026-10-22 | lead-bootstrap (acting) |
| Combat | `game/battle/**`, `game/data/battle/**` | 2026-10-22 | lead-bootstrap (acting) |
| Narrative | `docs/kb/story/**`, `game/data/dialogue/**` | 2026-10-22 | narrative-stream-1 |
| Audio | `tools/audio/**`, `assets_src/music/**`, `assets_src/sfx/**`, `assets/audio/**`, `docs/kb/audio/**` | 2026-10-22 | audio-stream-1 |
| QA & Tools | `tests/test_case.gd`, `tests/run_tests.*`, `tests/error_counter.gd`, `tools/taskboard.py`, `tools/screenshots/**` | 2026-10-22 | lead-bootstrap (acting) |
| Architect (stream) | `tools/dlgc.py`, `game/narrative/**`, `game/ui/dialogue/**`, `game/data/dialogue/**` | 2026-10-22 | architect-stream-1 |
| Progression (stream) | `game/progression/**`, `game/data/progression/**`, `tools/lattice_editor/**` | 2026-10-22 | progression-stream-1 |
| Rendering (stream) | `game/core/graphics_settings.gd`, `game/core/shader_prewarm.*`, `game/data/settings/**`, `game/shaders/**` | 2026-10-22 | rendering-stream-1 |
| QA (stream) | `tools/dev/**`, `tools/screenshots/**`, `tests/screenshots/**`, `docs/kb/qa/**` | 2026-10-22 | qa-stream-1 |
| Art direction (stream) | `docs/kb/art/**` | 2026-10-22 | art-stream-1 |
