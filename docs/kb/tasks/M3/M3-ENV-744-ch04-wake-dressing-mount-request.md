---
id: M3-ENV-744
title: "Mount env-art's wake-night dressing in ch04/haluna_wake.tscn (request to act1-chapters)"
role: cinematics
status: done
owner_session: ""
depends_on: [M3-ENV-743]
milestone: M3
request-from: environment
reviewer: environment
priority: high
---
## Goal
ADR 0041: no greybox in Act I. `game/levels/ch04/haluna_wake/haluna_wake.tscn` shows its 41 greybox blocks.
env-art's dressing is ready (M3-ENV-743). The preview
`game/levels/_tests/haluna_wake_dressing/haluna_wake_dressed.tscn` is the reference.

## Acceptance criteria
- [ ] Add a `Dressing` child (`game/levels/act1/zone_kit_dressing.gd`) with
      `layout_path = "res://assets/environments/zones/ch04/haluna_wake_dressing.json"`.
- [ ] A `Water` WaterSurface at y -0.9 (the night's high water: the causeway's top, -1.1, lies under it) on
      `assets/environments/zones/ch04/haluna_wake_water_material.tres`, `sea_glow_energy = 0.12`; and
      `hymn_glimmer` at HalunaMood's night value (0.2122, 0.5647, 0.6939, 0.6), which opens the sea-glow.
- [ ] Optional: the four `Table*` blocks are 0.8 m tall, the feast mats 0.47; lower the blocks to 0.5 so the
      table's edge is where the mat's is.
- [ ] Optional: ImraShell has one state (faded); the re-inked one (`kit_wake_shell_inked`) can follow a block
      shown from `ch04_saw_ysolde_ink` if you add one.
- [ ] The actors with no `model` are capsules (Osu, the vendor, the fisher, the child, the netmender, Reed, Ysolde):
      VillagerLayer bodies, or characters.
- [ ] For slice-polish (HalunaDresser's owner), not blocking: `instance_piece` treats a `-lod2` mesh as LOD0, so the
      palms placed through `kit_dir` (vegetation, three LODs) draw LOD0 and LOD2 together up close. A `-lodN` rule
      there (or `plants` support in ZoneKitDressing) fixes it.
- [ ] Shots: H02's camera is 0.5 m from Neme's house front (the house fills the left half); C01's camera is 1.5 m
      south of the 2 m wall and below its top (the frame is the wall). Both are so in the greybox too.
- [ ] Re-render the zone's shots and view them.

- 2026-10-28 (env-art): **DROPPED, superseded** (the Lead's word, 10-28). Ch4's wake no longer stands on a greybox
  zone: act1-chapters' M3-C04-1226 put it on the real Haluna at night (ADR 0041). This dressing's frame (the
  greybox blocks) is gone, and its preview cameras landed inside walls (the GPU QA's row 24). Removed:
  `wake_zone_dressing.py`, `assets/environments/zones/ch04/**`, the preview `game/levels/_tests/haluna_wake_dressing/`,
  the eight `zone_wake_*` shots and their PROVENANCE rows. The kit pieces it made (`wake_ground`, `wake_shell_set`,
  the lane houses, `dock_haluna_short`) stay in the Haluna kit.

## Review log
- 2026-10-28 environment (env-art, the request's reviewer): closed as superseded at the Lead's word. The wake now stands on the real Haluna (M3-C04-1226), so there is nothing to mount.
