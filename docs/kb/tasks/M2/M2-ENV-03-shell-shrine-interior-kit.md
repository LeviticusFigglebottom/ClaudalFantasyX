---
id: M2-ENV-03
title: Shell Shrine interior kit to replace the trial's greybox (haluna.md §3.2)
role: environment
status: review
owner_session: "m2-slice subagent (M2-ENV-03)"
depends_on: [M2-FP-16]
reviewer: art (env-art compares kits), rendering
milestone: M2
request-from: cinematics
---
## Goal
Request from the m2-slice track. The Shell Shrine trial (M2-FP-16) plays in a greybox built at runtime by `ShellShrineLevel` from `game/data/trials/shell_shrine.json` `layout` and `greybox`. The slice needs the room at final quality: the fan-shell roof and oculus, the curved walls and whorl columns, the carved channels with nacre inlay, the three rotatable shell-basins (each with three spouts, a 90° turn over 1.2 s), the octagonal inner pool, the shell-valve door that sinks as the pool rises, the side pool, the net-float charm (salt-glass, 6 cm), and the west-facing exterior steps with leaf-boats (S01).

## Acceptance criteria
- [x] Kit pieces in `assets_src/environments/kits/` (reproducible, with PROVENANCE rows) and a dressed `ch03/shell_shrine` scene. The trial's moving parts are separate nodes the level can drive: each basin's turning part, the pool water, the door, the side-pool water and the charm. The level then swaps its greybox for them, keeping the same JSON positions or moving those.
- [x] Channel water uses flowmap water (SPEC §8.2.1) where Rendering has it; otherwise a documented stand-in. A lit channel shimmers (no glimmer).
- [x] LightmapGI baked per state (pre-flood and post-flood), as haluna.md's GI note recommends, or a measured alternative. Five shots S01–S05 at the brief's lenses, with lavapipe baselines.

## Notes (m2-slice subagent, M2-ENV-03)
- **Kit** (`assets_src/environments/kits/haluna/shrine_interior.py`, in the `haluna_kit` Blender job; 19 pieces, each with an authored LOD1, PROVENANCE rows): the hall (`shrine_floor`, `shrine_vault`, `shrine_roof_fan`, `shrine_steps`, `shrine_islet`), the walls (`shrine_wall_curved` R = 9 m, `shrine_wall_portal`, `shrine_wall_straight`, `shrine_column_whorl`), the channels (`shrine_channel_straight`, `_spillway`, `_sluice`, `shrine_spring`), the basins (`shrine_basin_pedestal`, `shrine_basin_bowl`: the turning part, three spouts, the open lip at -Z), `shrine_inner_pool` (octagon, 7 m), `shrine_side_pool` (3 m), `shrine_door_valve`, `shrine_charm_net_float` (salt-glass, 6 cm). Materials: `kit_shrine_stone` (tended limestone), `kit_nacre` (new `env_nacre_inlay.gdshader`: the ±40° thin-film shift at 0.3, plus the per-instance water shimmer), `kit_water_spill` (new `env_water_spill.gdshader`), `kit_leaf_boat`. No gold.
- **Level**: the trial's moving parts are separate nodes built from the JSON (`basin_pivots` turn the bowls; the pool water, the door, the side-pool water and the charm are their own nodes). The hall is `shell_shrine_dressing.tscn`. The greybox is removed; a piece that fails to load falls back to a primitive of its size (`missing_pieces`). Positions moved: `side_pool`, `side_sluice`, `door` (into the east portal), `spill_len_m`, and spill lips now take `layout.spill_bearing_deg` so no spill trough runs along another channel. `greybox` became `room`. The hall is cut for `inner_pool`, `side_pool` and the oculus targets; `tools/tests/test_shell_shrine_kit.py` fails if the JSON moves them without a rebuild.
- **Water**: flowmap water (the river `WaterSurface`) on every channel, bowl and pool. A runtime 64-texel direction wheel is the channels' `tex_flow`, and each channel's UV.x picks its direction. Lit channels show their water, shimmer their nacre (no glimmer), and the pouring lips carry a falling sheet.
- **GI**: LightmapGI has no scriptable bake in 4.6 (ClassDB lists no `bake` on `LightmapGI`), so it is not feasible headless or on lavapipe. The measured alternative: a VoxelGI (`gi_voxel` group) baked at load for both states, door up and door down, and swapped when the door sinks. It takes 4.6–5.3 s for both on lavapipe (five runs). GPU cost is unmeasured. Plus warm omnis under the three shafts and a teal bounce per pool that goes out with its water.
- **Shots**: `shrine_s01_approach`, `_s02_threshold`, `_s03_overview`, `_s04_lip`, `_s05_side_pool` (rig `shell_shrine_shots.tscn`), lavapipe baselines. Lenses and heights as the brief says, except S03: 8 m and ~33° down, not 6 m and 60°, because a 28 m hall doesn't fit at 18 mm under the vault.
- **Gates**: gdlint and gdformat clean; validate_data 0/0; taskboard --check OK; tools unittest 503 OK; `verify_blender_builds --job haluna_kit` 50 identical; Godot `--filter=shell_shrine` 13/13, `--filter=fp_` 22/22, `--filter=environment_shaders` 11/11; the full Godot suite 1448/1448; the five new shots approved, and a second capture matches them at RMSE 0.00000.
- **Costs**: about 8.5 MB of new `.glb` (the floor 2.4 MB, roof 1.4 MB, vault 1.2 MB; each under 5 MB) and about 2.9 MB of new baselines.
- **Not met / gaps (honest)**: no bend or T-junction channel modules (the runs are straight and meet at the basins). No reflection probes at the basins. Ilun's chamber isn't built (the door leads to a dark passage stub). Channels have no collision (no step-up in the controller, as in the greybox). The S02 shaft is faint on lavapipe at density 0.02. The leaf-boats don't read at S01's distance. VoxelGI shows some blotching on the vault, so its energy is low (0.3).

- **2026-10-24 m2-slice, the Lead's decision:**
  - **Merged here:** the kit pieces, shaders, materials and PROVENANCE rows, as commit f38edea, "M2-ENV-03 (m2-slice kit, for env-art review)". Every file is under 5 MB and every asset has a PROVENANCE row; `verify_blender_builds.py --job haluna_kit` checks the rebuild.
  - **Reverted on purpose: the level side** (the 98e65e4 dressing and the 3313bac S01–S05 shots and baselines). The shrine level stays on its greybox until env-art has compared this kit with its own and the Lead names which to swap in.
  - **To swap this kit in:** `git revert` the revert commit (the one after f38edea). That brings back `ShellShrineLevel`'s room build, `shell_shrine_dressing.tscn`, the `room` JSON block and the five shots.
  - The notes above describe the full branch, including the level side.

## Review log
- **2026-10-24, Art Director (env-art), the Lead's kit comparison: ADOPT m2-slice's kit as the base (approve-with-fixes); env-art's parallel kit stops and is kept only for salvage.**
  Compared shot for shot: m2-slice's lavapipe baselines from 3313bac against env-art's in-progress lavapipe captures at the same lenses.
  - **Why m2-slice's kit wins:** it is complete and already wired into `ShellShrineLevel` (the drivable parts, the dressing, collision, missing-piece fallbacks, JSON tests), with flowmap water on every channel and pool, the thin-film nacre shader (the brief's optional request), a measured GI alternative (VoxelGI per state, 4.6–5.3 s), and five shots. Above all it **reads**: S03's overview shows the whole channel network like a diagram (pillar 4), and S04's pour and S05's drained pool with the charm in a light pool are good. env-art's kit was unfinished, and its interior was far too dark: S03 failed tactical clarity outright.
  - **Swap-in:** m2-slice, revert your revert of the level side (the commit after f38edea), as your notes say, and land the shots.
  - **Fixes, filed as M2-ENV-09** (env-art builds them on this kit; none blocks the swap-in):
    1. **The roof doesn't read as fan-shells.** S01 shows a lumpy dome, a yurt silhouette. The brief's idea is overlapping stone fan-shells in tiers rising to an oculus. Rebuild `shrine_roof_fan` from three tiers of ribbed fans (the existing Haluna `roof_fan_shell` tiers, sized to the hall), with white mortar ribs.
    2. **The walls are regular beige ashlar.** Make them coral-limestone courses (the Haluna pass-1 stone: holes, two tones), still fresher than the causeway (tended).
    3. **The interior is brown and murky** (S02, and the S03 vault). The brief: "cool after the glare outside, lit by three oculus shafts falling on water". Cool the fill (`#3FD0C9`-tinted bounce, as `ch03_shrine_int` says), lift the floor value a stop, and make the S02 shaft read (fog density, or a shaft card if lavapipe can't show it). Measure it against the colour script, not by eye.
    4. **The exterior at S01:** add leaf-boats on the steps and an offering shelf (they don't read at S01's distance now), and give the islet some sea stones and wet algae at the waterline.
    5. **Channel bends and T-junctions** (the brief's list; the runs are straight now). env-art's WIP has `channel_bend` and `channel_t` to salvage.
    6. Later, not blocking: reflection probes at the basins; Ilun's chamber (S08) is its own task when Cutscene B needs it.
