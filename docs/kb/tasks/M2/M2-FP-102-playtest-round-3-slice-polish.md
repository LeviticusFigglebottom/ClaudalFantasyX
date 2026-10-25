---
id: M2-FP-102
title: "Playtest round 3 (slice-polish): no rigid motion, no grey frames, live villagers, no primitive moments"
role: cinematics
status: doing
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-FP-28, M2-HER-1104, M3-CRE-610, M2-CHR-03]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
FAST-TRACK. The human's open playtest complaints about the M2 slice (title → prologue → Haluna beach → playable
Haluna → B06 Saltgrass Causeway → Shell Shrine trial → Drownbell → B12 end card), after big9 brings the real heroes:
rigid or snapping animation, greyscale or flat frames, placeholder villagers, and "parts look primitive".

## Acceptance criteria
- [x] **Motion: the cutscenes drive HeroMotion.** hero-integration's `docs/kb/tech/hero_motion_sequencer.patch`
  (M2-HER-1104) applied: clips go through `HeroMotion.play` (a hero body's AnimationTree, else its AnimationPlayer),
  walks report their speed (`set_locomotion_speed`, so the gait blend follows the ramps and the feet stop sliding),
  and every cast member gets `HeroIdleMicro` (breathing, weight shift, head-led turns). `walk_mps` 1.3 → 1.0 (the
  walk clip's planted-foot speed), and a `@mark ... run` sets off at `run_mps`.
- [x] **Motion: no linear pops.** `@fade` and the letterbox ease in and out (`fade_ease`, `letterbox_ease`).
- [x] **Viewing tool.** `tools/cutscene_frames/cutscene_frames.tscn` renders any slice location's arrival beat or
  cutscene to PNG frames with dialogue auto-advanced (docs/kb/tech/cutscenes.md "Viewing a cutscene").
- [ ] **Colour:** every slice cutscene and zone beat rendered and viewed; any grey, unlit or flat frame fixed with
  lighting and grade data.
- [x] **Villagers (Haluna):** FieldNpc (M3-CRE-610) and the M2-CHR-03 villager actors replace Haluna's ten capsule
  NPCs (`HalunaVillagers`, `game/data/flow/haluna_villagers.json`, `test_haluna_villagers`). The shopkeeper, smith
  and innkeeper wear other villagers' models until M2-CHR-100.
- [ ] **Villagers (the other slice zones)** and creatures' WildlifeLayer (M3-CRE-611) once it lands.
- [ ] **Primitive moments:** the slice walked from the scripts; each one fixed here or routed as a request task.
- [ ] **Hullgnaw intro framing** (M3-BPR-404, battle-presentation): verified in the slice once it lands.

## Notes
- FieldNpc came over from claude/creatures as cherry-picks of ac7ea5b9, a846b42e and bada52a9 (without the
  `npc_stage_field` shot rows, which stay with creatures' own merge so the manifest never carries the id twice).

## Review log
