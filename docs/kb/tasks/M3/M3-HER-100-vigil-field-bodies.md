---
id: M3-HER-100
title: "Request (slice-polish, to the hero track): field bodies for Liss, then Kerrid and Pell, so the Prologue's vigils stand as people"
role: character
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
reviewer: cinematics
---
## Goal
The Prologue's vigil (P01, P02 and slice_prologue_vigil_line) still shows Kerrid, Pell and Liss as cloth-coloured
capsules (`City/Vigils`). env-art's Iskarra is approved, so they are the last greybox in the frame. Since 28b0f97a,
`PrologueScene.dress_vigils()` gives each figure its hero's `HeroFieldActor` body as soon as
`game/data/hero_motion/hero_motion.json` `field.heroes.<id>` lists one: feet on the paving, and the capsule goes.
Nothing on slice-polish's side changes when a row lands.

## Acceptance criteria
- [ ] **`field.heroes.liss`:** liss.glb and liss_lod1.glb are on claude/characters (M3-CHR-50x). Add the row (scene,
      walk_clip_mps, run_clip_mps) when they merge.
- [ ] **`field.heroes.kerrid`** when M3-CHR-505 lands, and **`field.heroes.pell`** when M3-CHR-506 lands.
- [ ] **Check:** `godot --headless --path . res://tests/run_tests.tscn -- --filter=prologue` stays green.
      `test_fp_prologue::test_a_vigil_takes_its_body_when_its_hero_has_one` already covers the swap with a
      borrowed model.

## Notes
- Each figure faces its capsule's -Z for now. Once their bodies show, slice-polish turns them to the story's poses
  (Kerrid standing, Pell with his back to the sea).

## Review log
