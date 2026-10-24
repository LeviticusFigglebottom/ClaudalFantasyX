---
id: M2-ENV-1000
title: "Haluna lintel-gulls render dark: village.lintel_gull builds its body inside-out"
role: environment
status: review
owner_session: "env-art"
depends_on: [M2-ENV-06]
milestone: M2
request-from: environment
reviewer: rendering
---
## Goal
Found by the M3-ENV-07 (Oruvel) worker: `assets_src/environments/kits/haluna/village.py` `lintel_gull` winds its
body's faces inward, so every Haluna gull shades dark. The Oruvel kit fixed its own copy only. Fix the Haluna
generator.

## Acceptance criteria
- [x] Wind the gull body's faces outward in `village.lintel_gull`. Rebuild the `haluna_kit` job and check
      `verify_blender_builds` is identical apart from the gull pieces.
- [x] Re-capture every Haluna shot that shows a gull (the lintel-gulls at H03 and others), view them, and
      re-approve only the drifted ones.
- [x] Check the Brightwater ferry's "stem-gull" (it reuses the Haluna gull, M3-ENV-08) and re-approve its shots
      if they move.

## Notes (env-art, 2026-10-24)
- **Cause:** `village._loft` took its outward hint at grid column `sides // 4` while `_orient_grid` measures the
  winding at the middle column `(sides + 1) // 2`, on the far side of the section, so every loft was flipped
  inside-out. The hint now comes from the measured point. The LOD lofts also get smooth normals: `smooth=False`
  had left them all +Y (the full mesh is re-faceted by `_facet`, so it doesn't use them). `_loft` is used only
  by `lintel_gull`. Oruvel's `ov_cabins._turn_lofts_outward` is now a no-op guard (docstring updated).
- **Outputs changed** (verify_blender_builds before the rebuild: exactly these, everything else identical):
  `haluna/lintel_gull_a.glb`, `lintel_gull_b.glb`, `lintel_gull_c.glb`; `brightwater_ferry/ferry_hull.glb` (the
  stem-gull); `oruvel/lintel_gull_open.glb` (full mesh geometrically the same, vertex order changed; LOD normals
  were −Y and are now smooth outward). No kit_manifest changed. After the rebuild, verify is identical for
  haluna_kit (75), oruvel_kit (42), brightwater_ferry_kit (40), pemakar_kit (62), corrow_kit (44) and
  ashcrown_kit (40), the jobs that list village.py as a source.
- **Re-approved:** `haluna_h03_lintel_gull`, rmse 0.04675 against the old baseline (the drift is confined to the
  gull, which now shows its lit outer faces; the old glbs captured at 0.00400).
- **Within threshold, not re-approved:** h01 0.00513, h02 0.00199, h04 0.0, h07 0.00073, h10 0.00545,
  dialogue_backlog 0.00175, brightwater_b02 0.0, b03 0.0, oruvel_o01 0.0, o19 0.00081.
- **Drift that is not this change, left alone:** `battle_arena_oruvel_raft_morning` (0.05175; the placeholder
  enemies are now creature models) and `field_objective_line` / `field_interact_prompt` / `field_area_title` /
  `field_tip_card` (0.068) and `dialogue_continue` (0.057) (the Haluna tidewalls render wetter and darker). A
  control capture with the old gull glbs drifts the same (raft 0.05177, area_title 0.06861), so these baselines
  were already stale on main. Their owners need to re-approve them. The gull change in them is a few pixels.

- **Renumbered (Lead merge, big9, 2026-10-24):** filed as M2-ENV-12. M2-ENV-12 was already the shell shrine's off-tree prebuild on big9 (code and tests name it). The comments in assets_src/environments/kits/haluna/village.py and oruvel/ov_cabins.py still say M2-ENV-12; they are left alone so the haluna and oruvel Blender jobs need no rebuild, and env-art updates them when it next touches those files. Now M2-ENV-1000, from the Lead's id block (CONSOLIDATED §4).

## Review log
