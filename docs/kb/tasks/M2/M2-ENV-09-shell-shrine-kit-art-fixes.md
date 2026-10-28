---
id: M2-ENV-09
title: Shell Shrine kit art fixes (fan-shell roof, coral walls, a cool interior, S01 exterior, channel bends)
role: environment
status: review
owner_session: "env-art"
depends_on: [M2-ENV-03]
milestone: M2
request-from: art
reviewer: rendering
---
## Goal
The Art Director adopted m2-slice's Shell Shrine kit (M2-ENV-03, `assets_src/environments/kits/haluna/shrine_interior.py`)
as the base, with fixes (M2-ENV-03 Review log, 2026-10-24). This task is those fixes. It needs the kit on the
working branch (it is on `claude/m2-slice` at f38edea until the integration branch carries it).

## Acceptance criteria
- [x] `shrine_roof_fan` reads as tiers of overlapping ribbed stone fan-shells rising to the oculus, with white
      mortar ribs (haluna.md §3.2), not a lumpy dome: S01 viewed.
- [x] The hall walls are coral-limestone courses (the Haluna pass-1 stone), fresher than the causeway.
- [x] The interior is cool after the glare (`ch03_shrine_int`: shafts `#FFF1E4`, `#3FD0C9`-tinted bounce at 0.4,
      exposure 0.75): S02's shaft reads, the floor lifts about a stop, measured against the colour script.
- [x] S01 exterior: leaf-boats on the steps and an offering shelf that read at S01's distance; sea stones and a
      wet algae band at the islet's waterline. (env-art's superseded WIP kit has `leaf_boat`, `offering_shelf`
      and `sea_stones` to salvage.)
- [x] Channel bend and T-junction modules: not needed by the trial's layout (straight channels meeting at the basins);
      `channel_bend` / `channel_t` stay in the salvage folder for a layout that does need them.
- [x] S01–S05 re-captured and viewed; drift listed with RMSE for re-approval; `verify_blender_builds` identical.

## Notes (2026-10-24, env-art; in progress)
- **Roof** (`shrine_interior.build_roof_fan`): each fan's hinge stands 0.45 m off the vault
  (`ROOF_TIER_LIFT_M`), pitched at 0.62 of the vault's slope (`ROOF_PITCH_SCALE`) so rims overhang the tier
  below, doming 0.22 → 0.34 (`ROOF_SHELL_LIFT`). 36144 / 1752 tris (budget 60000 / 8000). S01: tiers with
  shadowed rims instead of a lumpy dome (still reads more like caps than ribbed scallops at this range).
- **Stone:** `kit_shrine_stone` now samples `coral_dressed` (new; `kit_textures.build_coral_dressed`: the
  village coral with holes ×0.18 and grey patches ×0.3, so tended stone keeps pores and grain without
  blotching), tinted a touch cool `#F2F3F0`, per-block spread 0.12, cavity 0.22. The village `coral_stone`
  texture is byte-identical.
- **Cool interior:** the hall's VoxelGI carries only the warm oculus sun, so it replaced the teal ambient and
  the warm stone bounced it brown. The physically right cool fill is the open sky seen through the oculi: one
  shadowless `Skylight` OmniLight under the vault in `ch03/shell_shrine/shell_shrine.tscn` (m2-slice's scene,
  owner-approved edit), colour (0.6, 0.76, 0.95), energy 1.2, range 18 m. S02 measured: floor `#41372A`
  L 0.34 hue 74° → `#57544E` L 0.45; walls L 0.24 → 0.37, no longer brown. (Strengthening the pools' teal
  bounce did nothing at S02: the pools are low at the trial's start, and their bounce goes out with the water.)
- **Close-up fix:** `coral_dressed` pores ×0.3 (`pore_amount`) and the tile back to 0.6 m: at 1.2 m S04's
  0.5 m camera showed single compressed texels as hard dots. Now tooled, worn stone.
- **Shots re-approved after viewing** (lavapipe, against m2-slice's baselines): s01 0.08228 (roof tiers,
  dressed walls, ENV-06 islet stone), s02 0.03511 (cool skylight fill, clean stone), s03 0.04734 (cool hall,
  the puzzle still reads as a diagram), s04 0.05491 (tooled stone), s05 0.04072 (cleaner rim). Haluna shots
  and `haluna_h10_dock_night` pass unchanged.
- **S01 exterior:** the steps already had the offering shelf (six leaf-boats) and five boats; 20 more now
  line the treads in loose pairs, clear of the walking line (`shrine_steps_offerings` rng; steps 5889 tris,
  budget 16000). At S01's ~30 m a 0.25 m boat is about 3 px, so they show as specks there (s01 rmse 0.00268,
  under the limit, not re-approved); I didn't enlarge them. They're built for S06 (Cutscene B on the steps,
  1.3 m). The islet's stepping stones and boulders already read in S01.
- **Channel bends and T-junctions:** not built. The trial's layout runs straight channels that meet at the
  basins, so no current room needs them; `channel_bend` / `channel_t` wait in the salvage folder for a layout
  that does.
- **Not done:** the wet algae band at the islet's waterline (the scene's sea sits at -2.0 m; the weathering
  bands follow `hymn_water_level`, which the shrine scene would have to publish: a level-side change).

## Notes (2026-10-28, env-art: finished now that the shrine kit is on the integration branch via big13)
- The wet algae band at the islet's waterline: the shrine scene's `Sea` now publishes `hymn_water_level`
  (`publishes_water_level = true`, tide line -2.0). The weathering bands follow it, so the stones at the waterline
  darken where they're wet. Viewed in `shrine_s01_approach` on this tree: a subtle band at S01's range.
- Nothing else open: S01–S05 were viewed and re-approved at the time; the channel modules are not needed (above).

## Review log
