# Handoff — environment — 2026-10-24 #env-art-11 (M3-ENV-700, ferry transom winding)

## Done
- **M3-ENV-700** is at `review` (reviewer: rendering). Worktree branch, not pushed; the Lead merges.
- `assets_src/environments/kits/brightwater_ferry/bf_common.py` `transom`: the fan is wound `(k, k + 1, centre)`,
  agreeing with its +z normals (it was wound against them on every face).
- Rebuilt `brightwater_ferry_kit`: only `ferry_hull.glb` and `derelict_hulk_a.glb` changed; verify: 62 identical.
  No other job sources the Brightwater kit, and derelict_hulk_b and the Seventh Terrace don't call `transom`.
- `WindingTests` in `tools/tests/test_brightwater_ferry_kit.py`: the transom agrees on every face, and every piece
  agrees on > 85 % of faces / > 80 % of area.
- `bf_import_settings.py` leaves non-`texture` PNG imports (the 3D-texture LUT `lut_ch04_crossing`) alone.
- Shots: b02 0.00000, o07 0.00000, b03 0.00071 (PASS; deterministic water-glint shift around hulk A from the newly
  drawn transom below the waterline; no stern seen; nothing re-approved).

## In progress
- Nothing.

## Exact next step
- Rendering reviews M3-ENV-700 (task file Review log); the Lead merges the branch.

## Known issues
- B03's committed baseline is 0.00071 from the new render (inside the 0.008 limit). Re-approve it the next time
  B03 is intentionally changed.
- Gotcha: kit pieces carry some lower-agreement faces (ferry_cargo-lod1 0.88 by count, ferry_lantern-lod1 0.83 by
  area), so the per-piece thresholds are guards against a whole surface flipping, not exact checks. The transom
  test is exact.

## Files touched
- `assets_src/environments/kits/brightwater_ferry/bf_common.py`, `bf_import_settings.py`
- `assets/environments/kits/brightwater_ferry/ferry_hull.glb`, `derelict_hulk_a.glb`
- `tools/tests/test_brightwater_ferry_kit.py`
- `docs/kb/tasks/M3/M3-ENV-700-ferry-transom-winding.md`, this handoff
