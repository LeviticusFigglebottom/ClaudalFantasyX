---
id: M3-CHR-540
title: "Request: Ivo Brannick (Ch8-9) as a Stillguard variant with his face uncovered"
role: character
status: review
owner_session: "chr-ivo-wip"
depends_on: [M3-CHR-507]
milestone: M3
request-from: character
reviewer: rendering
---
## Goal
`ivo` is a capsule in `game/levels/ch08/corrow/corrow.tscn` (inventory). act1_ch08.md B02: Ivo Brannick is a Stillguard,
Toma's shield-mate for seven years: he drops his shield to hug Toma (`@anim ivo hug_lift toma`), kneels to Asha
(`kneel_palms_flat`), stands in the W10 shield-line, and in Ch9 his is the only uncovered face among the shrouds. He needs
the Stillguard kit (red-lacquered shell armour, the shield), which the villager pipeline cannot build, so he belongs with
the Stillguard builds (the stillguard_a/b/c work, another agent's) as a named variant with his own face, no helmet.

## Acceptance criteria
- [x] A Stillguard build variant `ivo` with his own face and params (thirties, broad, warm), the shield on the left arm.
- [x] Clips `hug_lift`, `kneel_palms_flat` (shared spec), talk/idle; a lying-in-shroud pose for Ch9 if the Ch9 owner wants one.
- [x] The usual wiring (job verified on three numpy paths, PROVENANCE, import rule, tests, a stage scene and shots).

## Notes
- Filed 2026-10-28 by chr-npc-wip (the named-NPC pass): not built on the villager pipeline on purpose (no armour there).

- 2026-10-28 (chr-ivo-wip): **built, status review (reviewer: rendering).**
  - Build: `named.ivo` in `assets_src/characters/stillguard/stillguard_variants.json`, `build_stillguard.py --variant ivo`
    to `assets/characters/ivo/` (the speaker id; `sg_table.named()`/`builds()`, `variants()` stays the six). 1.81 m,
    broad (shoulders 1.9 heads as stillguard_b: at 1.94 the jack left the shoulder's body edge uncovered), muscle 0.74,
    mass 0.36, his own face sliders and skin (#A86F52, age 0.25, stubble 0.55, warm brown iris), a dark crop, no helm,
    the weathered kit, the shield on the left forearm and **no spear** (`build_moll` `no_prop`, default path unchanged:
    the moll and stillguard jobs re-verified identical, 40 and 178 files). The broken front tooth: the upper central
    incisor's edge chipped on a slant (`_variant.broken_tooth`, about 2 mm; it barely shows, as the sheet asks).
    LOD0 40,256 tris, LOD1 17,602 (budget 45k/22k); ivo.glb 2.50 MB, ivo_lod1.glb 0.91 MB.
  - Clips (`anim/ivo_clips.tres`): idle and walk (the squad's), run (shared) and talk (mirrored onto his free right hand),
    and the story specs `requested_clips.json` `heroes.ivo`: `hug_lift` (3.2 s: arms open, wrap, dip, lift leaning back,
    held) and `kneel_palms_flat` (his own spec: both knees, the bow, the palms face down and level before his knees; the
    shared spec put his arms out at his sides). `look_at` is the sequencer's turn. No Ch9 lying-in-shroud pose (open).
  - Wiring: job `ivo` (three numpy paths identical, 27 files), PROVENANCE rows, import rule and `.glb.import` script,
    rig_checks entry with ratchets (`_allowances`), `TestRigIntegrityIvo`, `test_stillguard.TestIvo`, test_hero_clips'
    dialogue check, stages `game/levels/_tests/characters/stillguard/ivo_*.tscn`, shots `ivo_front`, `ivo_three_quarter`,
    `ivo_face`, `ivo_face_laugh`, `ivo_clip_hug_lift`, `ivo_clip_kneel_palms_flat`, `ivo_clip_talk` (viewed; no baselines).
  - For the level owners (also in M3-CHR-519): hide the GLB's `Shield` node at `@sfx shield_dropped` and lay a dropped
    shield; Toma's lift in the hug is the scene's placement.
  - Known: the stage shots show the shield on his arm in the hug and kneel (in the scene it is dropped); the crop is the
    squad's card hair (blocky at face distance); the laugh uses Asha's face poses and reads a little lopsided.

## Review log
