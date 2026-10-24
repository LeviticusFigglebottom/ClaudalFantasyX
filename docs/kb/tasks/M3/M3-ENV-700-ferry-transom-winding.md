---
id: M3-ENV-700
title: "Brightwater kit: bf_common.transom is wound inward (the ferry's and drowned hulls' transoms vanish from astern)"
role: environment
status: review
owner_session: "env-art"
depends_on: [M3-ENV-08]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Found by the M3-ENV-08B worker: `assets_src/environments/kits/brightwater_ferry/bf_common.py` `transom` is wound
against its own normals (0.95 of its triangles face inward), so the ferry's transom and the derelict hulks'
transoms are invisible from astern. The Seventh Terrace builds its transom another way and is unaffected.

## Acceptance criteria
- [x] Wind `transom` outward. Rebuild `brightwater_ferry_kit`. Only the hulls that use it may change (`ferry_hull`
      and the derelict hulks), and `verify_blender_builds` is identical after the rebuild.
- [x] Add a winding test (most faces' winding agrees with their normals), like the corrow and oruvel kits have.
- [x] Re-capture the Brightwater shots and view them. No current baseline sees the stern, so none should move; if
      one does, view it and give the reason before re-approving.
- [x] Note: `bf_import_settings.py` overwrites `lut_ch04_crossing.png.import` with 2D settings. Fix the script
      so it leaves the LUT's 3D-texture import alone.

## Notes (env-art, 2026-10-24)
- Fix: one line in `bf_common.transom`. The fan triangle is now `(k, k + 1, centre)`, so its winding agrees with
  its +z (astern) normals. Before, every face was against them, at both LODs. Only `bf_hull` (ferry_hull) and
  `bf_drowned.build_hulk_a` call it. derelict_hulk_b (broken off forward of the stern), the Seventh Terrace pieces
  and no other kit use it: only the `brightwater_ferry_kit` job lists any `brightwater_ferry/*.py` source, and
  arena_derelict_deck is its own kit's code.
- Rebuilt `brightwater_ferry_kit` (Blender 5.0.1, threads 4): exactly `ferry_hull.glb` and `derelict_hulk_a.glb`
  changed (same sizes and triangle counts, manifest unchanged). `verify_blender_builds --job brightwater_ferry_kit`:
  62 identical.
- Tests: `tools/tests/test_brightwater_ferry_kit.py` `WindingTests`. The transom (FERRY, FORM_A, FORM_B, both LODs)
  agrees with its normals on every face; every piece of the 24 targets and its LOD1 agrees on > 85 % of faces and
  > 80 % of area (current minimums: ferry_cargo-lod1 0.88 by count, ferry_lantern-lod1 0.83 by area).
- `bf_import_settings.py` now patches only `.png.import` files whose importer is `texture`, so
  `lut_ch04_crossing.png.import` (`3d_texture`) is left alone. Run after `--import`, it patches nothing and the
  worktree stays unchanged.
- Shots (capture.sh, one process each; compare.py): brightwater_b02_awning rmse 0.00000, oruvel_o07_name_board
  0.00000, brightwater_b03_rail_drowned 0.00071 (PASS, limit 0.008). The B03 drift is deterministic (a second
  capture is byte-identical) and comes from the fix: 232 px of the water's glints and cyan sparkle around derelict
  hulk A move now that its transom, which reaches below the waterline, is drawn. The hulk's silhouette is unchanged
  and no stern is seen. No baseline was re-approved. battle_arena_derelict_deck_night was not captured: it holds no
  changed piece.

## Review log
