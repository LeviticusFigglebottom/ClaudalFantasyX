---
id: M3-CRE-616
title: "Ambient insects: moths round the lamps, dragonflies over water and paddies"
role: character
status: review
owner_session: "creatures (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY, worktree agent-a179c0f36c6e5f9a8)"
reviewer: art
depends_on: [M3-CRE-611]
milestone: M3
request-from: lead
---
## Goal
A fourth ambient wildlife kind for the WildlifeLayer (M3-CRE-611): insects. Pale dusk moths looping round the lamps,
dragonflies holding hovers and darting over water and paddies (and away from the player). Same pipeline, same
cheapness, deterministic, data-placed.

## Acceptance criteria
- [x] Two insect meshes in one GLB from source (the wildlife kit), materials, a Blender job, PROVENANCE rows
- [x] A wing-flutter shader mode, pure function of the instance data (no `TIME`)
- [x] `WildlifeSwarm` (moth swarm, dragonfly patrol), zone `swarms` rows, the `insect` kind, budgets (24 insects,
  6 draw calls), validator rules and tests
- [x] Zone data for Haluna and Pemakar; moths (and dragonflies) on the review stage; shot re-approved

## Notes
- 2026-10-27 character (worktree agent-a179c0f36c6e5f9a8): design, budgets and zone table in
  `docs/kb/art/wildlife.md`.
- **Models** (`assets_src/wildlife/insect/build_insect.py`, creature-kit geometry, `export_static`):
  `assets/wildlife/insect/insect.glb` (22 KB), `insect_moth` 248 tris (3 cm span, furry body, dusty off-white and
  grey-brown banded wings, antennae) and `insect_dragonfly` 272 tris (7 cm, blue-green to bronze segmented abdomen,
  four narrow glassy wings with a darker vein edge and a tip spot; opaque, no alpha). Slots `moth` and
  `dragonfly` (`assets/wildlife/insect/materials/*.tres` by `write_materials.py --wildlife insect`). Motion mask
  `TEXCOORD_1.y` = the wing span, 0 root .. ±1 tip, sign = side. Palette only, no reserved glimmer/wound colours.
  Job `wildlife_insect`: `verify_blender_builds.py --job wildlife_insect` prints identical. PROVENANCE rows for the
  GLB and both `.tres`, at the end of the wildlife block. Import: `res://assets/wildlife/insect/` added to
  `game/data/import/wildlife.json`.
- **Shader:** mode 5, wing flutter about the body's long axis at `flutter_pivot`; the dragonfly's hind pair (behind
  `flutter_split_z`) lags `flutter_hind_lag`. `WildlifeBuffer.MODE_FLUTTER`.
- **Runtime:** `game/world/wildlife/wildlife_swarm.gd` (moths: jittery orbits and darts round a point, ignore the
  player; dragonflies: hover, dart 1-3 m, perch on optional `perches`, flee a player within 1.5 m). Seeded
  `<zone>/insect/<id>`, paused off screen and hidden past 120 m like the other groups. `WildlifeLayer` reads a zone's
  `swarms` array, two more MultiMeshes (moths, dragonflies; no shadows), budget `insects` 24, `draw_calls` 6. A kind
  may now give one material per mesh (`material: {mesh: path}`), which the insect kind does.
- **Data:** `wildlife.json` `insect` kind (`moth` and `dragonfly` tables). `ch02_haluna.json`: no marsh or reeds in
  Haluna, so one 4-dragonfly patrol over the shallows' edge by the north crabs. New `ch05_pemakar.json`: moth swarms
  (5 each) at [0, 2.2, -36] and [0, 2.2, -24], a 4-dragonfly patrol over the paddies at [22, 1.2, -31] r 5 (noted
  as the day variant's; the layout is Lanternfall night).
- **Measured** (headless debug, shared CPU, all groups simulated, 1,200 frames): Pemakar's 14 insects 0.07 ms per
  frame (worst 0.20); Haluna's 4 dragonflies 0.02 ms; whole Haluna layer 0.21 ms (worst 0.67). Budget 1.0 ms.
- **Review:** `wildlife_stage` now has a low lamp post with five moths near the camera and two dragonflies over the
  water's edge; baseline re-approved (recapture rmse 0). The insects are true to size, so they read as small pale
  flecks and a slim dark dart at this range.
- **Zone owners:** nothing new to wire for Haluna (the same WildlifeLayer node). Pemakar needs its one
  `WildlifeLayer` node with `zone_id = &"ch05/pemakar"`; not added here (the scene is theirs).

## Review log
