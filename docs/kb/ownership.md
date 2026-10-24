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
| UI + Combat (stream) | `game/ui/**`, `game/battle/scene/**`, `game/data/ui/**`, `assets/fonts/**` | 2026-10-22 | ui-combat-stream-1 |
| Rendering (glimmer) | `game/vfx/glimmer/**`, `game/shaders/glimmer/**`, `game/data/vfx/**`, `game/levels/_tests/glimmer/**` | 2026-10-22 | rendering-stream-3 |
| Rendering (water) | `game/shaders/water/**`, `game/world/water/**`, `game/levels/_tests/water/**` | 2026-10-22 | rendering-stream-2 |
| Character | `assets_src/characters/**`, `assets/characters/**`, `game/levels/_tests/characters/**` | 2026-10-22 | character-stream-1 |
| Environment | `assets_src/environments/**`, `assets/environments/**`, `game/shaders/vegetation/**`, `game/levels/_tests/vegetation/**` | 2026-10-22 | environment-stream-1 |
| Progression (economy) | `game/data/items/**`, `game/progression/{item_db,inventory,equipment_bag,customize,wallet,shop,flag_reader,party_goods,equipment_effects,item_battle_action}.gd` | 2026-10-23 | progression-stream-2 |
| Systems (field/debug/saves) | `game/world/**`, `game/core/debug/**`, `game/data/world/**`, `game/data/debug/**` | 2026-10-23 | architect-stream-2/4 |
| Rendering (storm) | `game/shaders/undertow/**`, `game/vfx/undertow/**`, `game/levels/_tests/undertow/**` | 2026-10-23 | rendering-stream-5 |
| Rendering (storm perf, M1-RND-10) | `assets_src/vfx/undertow/**`, `assets/vfx/undertow/**`, `tools/gpu_bench/**` | 2026-10-23 | session_01778wbLbDFnRRLTKjnawv3T (PC GPU) |
| Rendering (storm events, M2-RND-05) | `game/vfx/undertow/undertow_events.gd`, `game/shaders/undertow/undertow_{streamer,bolt,rain}.gdshader` (inside the storm stream's `game/shaders/undertow/**` and `game/vfx/undertow/**`), the storm group of `game/shaders/water/water_surface_body.gdshaderinc` | 2026-10-24 | session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU) |
| Environment (kits) | `assets_src/environments/kits/**`, `assets/environments/kits/**`, `game/shaders/environment/**`, `game/levels/_tests/haluna_mood/**` | 2026-10-23 | environment-stream-2 |
| Systems (saves) | `game/world/save_shrine/**`, `game/ui/save/**`, `game/levels/_tests/save_shrine/**` | 2026-10-23 | architect-stream-4 |
| Art (swatches) | `game/levels/_tests/swatches/**` | 2026-10-23 | art-stream-3 |
| Rendering (sky perf, M1-RND-12) | `assets_src/vfx/sky/**`, `assets/vfx/sky/**` (plus the sky-quality edits to `game/shaders/environment/env_sky_cumulus.gdshader` and `haluna_noon_environment.tres`, routed by the Lead from review-sweep-H; Environment reviews) | 2026-10-23 | session_01778wbLbDFnRRLTKjnawv3T (PC GPU) |
| First Playable (lead request) | `game/cutscene/**`, `game/flow/**`, `game/levels/ch02/**`, `game/levels/ch03/**`, `game/levels/prologue/**`, `docs/PLAYTEST.md` | 2026-10-23 | session_01ELR13ohWMPrprcpcgLa7UR |
| Character + Tools (import, M1-ART-02) | `game/core/import/**`, `game/data/import/**`, `tests/fixtures/import/**`, `docs/kb/tech/asset_import.md` (plus the one `import_script/path` line in the Environment-owned kit and vegetation `.glb.import` files, Lead-assigned; Environment owns those files otherwise) | 2026-10-23 | worktree-agent-a21af6e9e71ccbfda |
| M2 slice (continues First Playable; Lead-assigned standing queue) | `game/cutscene/**`, `game/flow/**`, `game/levels/ch02/**`, `game/levels/ch03/**`, `game/levels/prologue/**`, `docs/PLAYTEST.md` | 2026-10-23 | m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC) |
| M2 slice (trials data, M2-FP-16) | `game/data/trials/**` | 2026-10-24 | m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC) |
| Rendering (underwater, M2-RND-02) | `game/world/water/underwater/**`, `game/levels/_tests/underwater/**` (shaders under the water stream's `game/shaders/water/**`) | 2026-10-24 | session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU) |
