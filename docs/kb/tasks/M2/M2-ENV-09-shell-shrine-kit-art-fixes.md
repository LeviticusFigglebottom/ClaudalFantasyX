---
id: M2-ENV-09
title: Shell Shrine kit art fixes (fan-shell roof, coral walls, a cool interior, S01 exterior, channel bends)
role: environment
status: doing
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
- [ ] `shrine_roof_fan` reads as tiers of overlapping ribbed stone fan-shells rising to the oculus, with white
      mortar ribs (haluna.md §3.2), not a lumpy dome: S01 viewed.
- [ ] The hall walls are coral-limestone courses (the Haluna pass-1 stone), fresher than the causeway.
- [ ] The interior is cool after the glare (`ch03_shrine_int`: shafts `#FFF1E4`, `#3FD0C9`-tinted bounce at 0.4,
      exposure 0.75): S02's shaft reads, the floor lifts about a stop, measured against the colour script.
- [ ] S01 exterior: leaf-boats on the steps and an offering shelf that read at S01's distance; sea stones and a
      wet algae band at the islet's waterline. (env-art's superseded WIP kit has `leaf_boat`, `offering_shelf`
      and `sea_stones` to salvage.)
- [ ] Channel bend and T-junction modules (salvage `channel_bend`, `channel_t` from the WIP).
- [ ] S01–S05 re-captured and viewed; drift listed with RMSE for re-approval; `verify_blender_builds` identical.

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
- **Remaining:** S01 leaf-boats and offering shelf, sea stones and algae at the islet's waterline; channel
  bends and T-junctions (salvage). **S01–S05 baselines: re-approval pending** (the merged tree's capture is
  running; they drift from ENV-06's stone and these fixes).

## Review log
