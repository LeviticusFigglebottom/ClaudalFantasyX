---
id: M2-ENV-10
title: The Shell Shrine ships its baked GI instead of baking both states at entry (ADR 0029 breach)
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-ENV-03]
reviewer: rendering
milestone: M2
request-from: lead
---
## Goal
The Lead's decision on 2026-10-24 at 14:40. The PC's probe (gpu/shrine-gi-hang-probe, `docs/kb/qa/gpu/2026-10-24-shrine-gi-hang-probe.md`) found that ShellShrineLevel baked both VoxelGI states in one main-thread frame at entry: 3.5–3.8 s on an RX 9070 XT. That makes the worst hidden frame 4.2–5.6 s and the entry 4.9–6.5 s, against ADR 0029's limits of ≤ 1 s and ≤ 3 s. One state alone is about 1.8 s, which is over 1 s, so per the Lead the baked VoxelGIData ships instead, made reproducibly by a tools/ script with PROVENANCE rows.

## Acceptance criteria
- [x] `tools/shrine/bake_shrine_gi.tscn` bakes both states under godot-render (lavapipe) or a GPU. Two runs give byte-identical files. The command is in PROVENANCE.md.
- [x] The data is `assets/levels/ch03/shell_shrine/shrine_gi_{open,closed}.res` (about 0.8 MB each, compressed), named by `shell_shrine.json` `room.gi_data`.
- [x] At entry the level only loads both states. The bake is an opt-in development fallback (`bake_at_load`, off).
- [x] **A staleness guard:** `tools/shrine/gi_inputs.py` hashes the bake's inputs into `shrine_gi_inputs.json`. `tools/tests/test_shrine_gi_bake.py` fails when they change without a rebake, and also checks that the files exist, are under 5 MB and have PROVENANCE rows.
- [x] **A frame-time test:** `test_shell_shrine_level.gd::test_the_lighting_ships_baked_and_entry_never_bakes` asserts no bake at entry, the GI load under 250 ms, and the whole headless entry frame under 1 s.
- [ ] The PC re-measures the shrine entry on hardware.

## Notes
- 2026-10-24 m2-slice:
  - **Lavapipe:** the bake takes about 2.5 s per state, so it's offline now.
  - **Rebaking:** any change to the shrine's scenes, its level script, the trial data or the kit's shrine pieces needs a rebake. The guard test says so. Env-art's M2-ENV-09 kit fixes will trip it, which is intended: rebake with the PROVENANCE command.
  - **First run:** only the very first bake after a fresh import differed in bytes. Every later run is identical, so bake twice if in doubt.
  - **Shots:** shrine_s01–s05 captured on lavapipe with the shipped GI. All pass against their baselines (rmse ≤ 0.00007), and none hung.
  - **The lavapipe deadlock:** it was seen right after "GI baked (2 states)". Entry no longer bakes, so that path is gone on this branch.

## Review log
