# Handoff: environment, 2026-10-24 #4

Session: an m2-slice subagent (session_01DQ9tdk8Uatb8Jr6raAkXiC), working in its own worktree branch. Task: M2-ENV-03, the Shell Shrine interior kit that replaces the trial's greybox.

## Done
- **Kit.** `assets_src/environments/kits/haluna/shrine_interior.py` adds 19 pieces to the `haluna_kit` job. The job is byte-reproducible: `verify_blender_builds --job haluna_kit` reports 50 identical. Every piece has a LOD1 and a PROVENANCE row.
  - The hall: a stadium plan with R = 9 m half-rounds. Inside are the fluted vault with three oculi and the floor, cut for the two sunken pools. Outside are the fan-shell roof tiers, the west steps with leaf-boats, and the islet with the last tidepool.
  - The trial's modules: wall arcs and portal, straight runs, whorl columns, the trough, spillway, sluice and spring, the pedestal and the turning bowl (the open lip at -Z), the octagonal pool, the side pool, the shell-valve door, and the 6 cm salt-glass charm.
  - New materials: `kit_shrine_stone`, `kit_nacre` (`env_nacre_inlay.gdshader`: the thin-film shift plus the instance uniform `inst_shimmer`), `kit_water_spill` (`env_water_spill.gdshader`) and `kit_leaf_boat`.
- **Level.** `ShellShrineLevel` builds the working parts from the JSON as kit pieces, each as a separate node: the bowls, the channels, the pool water, the door, the side-pool water and the charm.
  - The greybox is gone. A piece that fails to load falls back to a primitive and is listed in `missing_pieces`.
  - Flowmap water runs on every channel: a runtime direction wheel serves as `tex_flow`. While the water runs, the nacre shimmers and the falling sheets show. Each pool has a teal bounce light that goes out with its water.
  - The collision proxies replace the greybox's.
  - The hall itself is `shell_shrine_dressing.tscn`.
  - In the JSON, `greybox` became `room`. The side pool, sluice and door moved, and spill lips take `layout.spill_bearing_deg`.
- **GI.** LightmapGI can't be baked from a script, so the level bakes a VoxelGI at load for both door states and swaps them when the door sinks. Both states take 4.6–5.3 s on lavapipe. The README has the details.
- **Shots.** `shrine_s01_approach`, `shrine_s02_threshold`, `shrine_s03_overview`, `shrine_s04_lip` and `shrine_s05_side_pool` were appended to `shots.json`. The rig is `shell_shrine_shots.tscn`. They have lavapipe baselines; I viewed each one and iterated on all five.
- **Tests.** The new `tools/tests/test_shell_shrine_kit.py` checks:
  - the hall is cut for the JSON;
  - the scene's sun is the one the oculi were cut for;
  - no roof shell shades a shaft or pierces the vault;
  - the bowl's lip faces -Z.

  `test_shell_shrine_level.gd` now covers the kit pieces, the water, the shimmer, the spill bearings and the fallback. `test_environment_shaders.gd` lists the two new shaders.

## In progress
- Nothing. M2-ENV-03 is in review, with Rendering as reviewer for the two shaders, the VoxelGI choice and the cost.

## Exact next step
- Rendering, or the PC GPU session: measure the hall on the reference tier. That means the VoxelGI bake time (both states) and the frame cost at S03, which shows about 20 river `WaterSurface`s when every channel runs and 4–6 in a normal state. Then decide whether to keep VoxelGI or move to editor-baked LightmapGI data committed per state.
- Optional, from the brief: bend and T-junction channel modules, reflection probes at the basins, and Ilun's chamber (the door now opens on a dark passage stub).

## Known issues
- Channels have no collision, so Rhen can walk through a trough's curbs. The controller has no step-up, and the greybox had the same gap.
- The S02 shaft is faint on lavapipe at fog density 0.02.
- VoxelGI blotches the vault a little, so its energy is 0.3.
- S03 is 8 m high and about 33° down, not 6 m and 60°: the 28 m hall doesn't fit at 18 mm under the vault.
- The leaf-boats don't read at S01's distance.
- About 8.5 MB of new `.glb` and 2.9 MB of baselines (repo-binary risk, STATUS #4).
- `game/data/settings/prewarm_materials.json` (Rendering's file) doesn't list `kit_nacre` or `kit_water_spill`. It scans scene materials, so whether they need explicit rows is Rendering's call.

## Files touched
- assets_src/environments/kits/haluna/: shrine_interior.py (new), build.py, materials.py
- assets/environments/kits/haluna/: shrine_*.glb and .import (19, new), kit_manifest.json, materials/kit_{shrine_stone,nacre,water_spill,leaf_boat}.tres (new); assets/PROVENANCE.md (rows appended)
- game/shaders/environment/env_nacre_inlay.gdshader, env_water_spill.gdshader (new)
- game/levels/ch03/shell_shrine/: shell_shrine_level.gd, shell_shrine.tscn, README.md; new: shell_shrine_dressing.tscn, shell_shrine_environment.tres, shrine_water_material.tres, shell_shrine_shots.gd/.tscn, shots/S01–S05.tres
- game/data/trials/shell_shrine.json
- tests/integration/test_shell_shrine_level.gd, tests/unit/test_environment_shaders.gd, tools/tests/test_shell_shrine_kit.py (new)
- tests/screenshots/shots.json (5 appended), baselines/shrine_s0*.png, baselines.json
- docs/kb/tasks/M2/M2-ENV-03-shell-shrine-interior-kit.md

## Gates
- gdlint and `gdformat -l 120 --check` on game and tests: clean. validate_data: 0 errors and 0 warnings. `taskboard --check`: OK.
- Tools unittest: 503 OK.
- Blender: `verify_blender_builds --job haluna_kit`: 50 identical, in 17 s.
- Godot `--filter=shell_shrine`: 13/13. `--filter=fp_`: 22/22. `--filter=environment_shaders`: 11/11.
- The full Godot suite: 1448 run, 0 failed.
- Shots: I approved only the five new ids. A second capture matches them at RMSE 0.00000.
- Skipped, because my diff can't affect them: the coverage step (no battle or progression code); the other shots (no shared shader, material or scene changed, and the kit's existing `.glb` and `.tres` files rebuild byte-identically).
