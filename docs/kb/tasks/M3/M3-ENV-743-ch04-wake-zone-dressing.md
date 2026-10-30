---
id: M3-ENV-743
title: "Ch4 wake night: a ZoneKitDressing for the haluna_wake greybox, with its ground, lane houses and short dock"
role: environment
status: done
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-709]
milestone: M3
reviewer: cinematics
---
## Goal
ADR 0041: Act I at final quality. `game/levels/ch04/haluna_wake/haluna_wake.tscn` is the 41-block greybox stand-in
for Haluna's wake night. It stays a zone of its own until Haluna moves to ZoneStory (ADR 0035), so dress it in its
own frame from the Haluna kit and M3-ENV-709's wake set (the M3-C04-03 wake-night half).

## Acceptance criteria
- [x] New kit pieces (Haluna kit, `build.py`): `wake_ground` (the terrace level at y 0 inside the rails, the beach
      and the flats past them, the island rising behind; lane, turf, seagrass and rubble masks for kit_ground);
      `house_lane_a/b/c` (the houses with no shade deck, at the greybox's 6 x 6, 8 x 5 and 6 x 8);
      `dock_haluna_short` (the dock at 14.4 m); `wake_shell_set` (a named shell for the wall, no stand). The
      existing houses, dock and single shell rebuild byte-identical.
- [x] `assets_src/environments/kits/haluna/wake_zone_dressing.py` writes the zone's JSON, its night Environment
      (Haluna's ch02_night) and its night sea material (HalunaMood's ch02_night settings).
- [x] The wake set on the blocks: the wake-shell arc with its gap on `AshaShell`, tidewall runs to the block's ends
      (both colliding on their own mesh, the arc bowing to the village), Imra's faded shell and Asha's inked one,
      the ink kit on `InkLamp`, the lamps on `WallLamps`/`WallLampsLow`/`GrassLamps` with their warm lights, the
      feast mats at the tables, the window lights on `WindowLit1`–`4`; the causeway's slabs under the tide.
- [x] `tools/tests/test_zone_dressing_ch01.py`.
- [x] Self-rendered and viewed (`zone_wake_h02/h04/h07/h09/h12/h13/h08/c01`, 10-28): the moonlit lane and
      houses, the shut market and inn, the chapel door, the dark dock from the shore and from under it, the feast
      and the lamp-lit wall, Asha's and Imra's shells in the wall. H08 first showed the shells on stands in front
      of the wall; they are now set in it (`wake_shell_set`).
- [ ] Mounted by act1-chapters (M3-ENV-744).

## Notes
- 2026-10-28 (env-art): two shot notes for act1-chapters (in M3-ENV-744's spirit, not blocking): H02's camera
  stands 0.5 m from Neme's house front, so the house fills the left half (as in the greybox); C01's camera is
  1.5 m south of the 2 m wall and below its top, so the frame is the wall's coping, not the causeway.

- 2026-10-28 (env-art): **DROPPED, superseded** (the Lead's word, 10-28). Ch4's wake no longer stands on a greybox
  zone: act1-chapters' M3-C04-1226 put it on the real Haluna at night (ADR 0041). This dressing's frame (the
  greybox blocks) is gone, and its preview cameras landed inside walls (the GPU QA's row 24). Removed:
  `wake_zone_dressing.py`, `assets/environments/zones/ch04/**`, the preview `game/levels/_tests/haluna_wake_dressing/`,
  the eight `zone_wake_*` shots and their PROVENANCE rows. The kit pieces it made (`wake_ground`, `wake_shell_set`,
  the lane houses, `dock_haluna_short`) stay in the Haluna kit.

## Review log
- 2026-10-28 Lead (relayed by env-art from the Lead's message: "Drop M3-ENV-743/744 if they're dead (superseded); say so in their task files"): dropped, superseded by M3-C04-1226. No cinematics review is owed; nothing was mounted.
