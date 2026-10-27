# Handoff — environment (env-art worker, M3-ENV-09B) — 2026-10-24

## Done
- **M3-ENV-09B**, now `status: review` (reviewer: rendering). Pemakar's far Ashcrown is the Ashcrown kit's
  building: `assets_src/environments/kits/pemakar/pemakar_layout.py` places `ashcrown_tiers`, `flying_stair`,
  `crown_pavilion`, `forecourt`, `pilgrim_causeway` at the rim point (0, 306.72, −682), yaw 0, with per-placement
  `kit_dir`, `materials_dir` and `lod1_from_m` 600; `pemakar_kit_preview.gd` honours them. The Lanternfall arena
  (`arena_scenes.py` → `ash_terrace_lanternfall.tscn`) places the same five pieces through `town_to_arena`.
- `ashcrown_silhouette` retired from both layouts; the asset and PROVENANCE row stay (still built, read by
  `test_ashcrown_kit`).
- Baseline `pemakar_p01_waterfall_of_fires` re-approved (rmse 0.00164, the temple only). P03 unchanged.
- Test: `test_ashcrown_is_the_ashcrown_kits_building_at_the_rim` in `tools/tests/test_pemakar_kit.py`.

## In progress
- Nothing. Commits on the worktree branch only (not pushed).

## Exact next step
- Rendering reviews M3-ENV-09B. The Lead merges and notes it in `docs/kb/handoffs/live/env-art.md`.
- `battle_arena_ash_terrace_lanternfall` fails compare (rmse 0.018) at HEAD as well as with this change:
  creature-pose drift (gull, crab, eel), not the skyline (out of frame). Needs whoever owns the creature models or
  the arena shot to look; not re-approved here.

## Known issues
- In the arena the Ashcrown pieces use the import's LOD distances (LOD0 to 70 m); fine at 650 m, but a camera
  closer to the temple in an arena would need per-placement ranges.
- The forecourt's LOD1 substructure stops at y −30 (LOD0 at −60); at the town's distance the massif covers it.

## Files touched
- `assets_src/environments/kits/pemakar/pemakar_layout.py`, `game/levels/_tests/pemakar_kit/pemakar_preview_layout.json`,
  `game/levels/_tests/pemakar_kit/pemakar_kit_preview.gd`
- `assets_src/environments/kits/haluna/arena_scenes.py`, `assets/environments/arenas/ash_terrace_lanternfall/ash_terrace_lanternfall.tscn`
- `tools/tests/test_pemakar_kit.py`, `tests/screenshots/baselines/pemakar_p01_waterfall_of_fires.png`
- `docs/kb/art/environments/pemakar.md`, `docs/kb/art/environments/ashcrown.md` (Revisions), the task file, this handoff.
