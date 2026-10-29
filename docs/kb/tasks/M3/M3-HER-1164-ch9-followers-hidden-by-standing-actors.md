---
id: M3-HER-1164
title: "Ch9: Rhen walks the strand alone because Asha's and Toma's stage actors stand visible all chapter (GPU QA row 39)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: qa
---
## Goal
PC GPU QA row 39 (`docs/kb/qa/act1_gpu_qa.md` on gpu/act1-qa-2): "In Ch9 Rhen walks alone though Asha and Toma are
in the chapter's party."

**Cause (integration-qa's probe, 2026-10-29):** `ch09/corrow_night`'s CutsceneStage has `Actors/asha` and
`Actors/toma` visible from the moment the zone loads (and ysolde, liss, pell, the mourners, ...). HeroFieldParty
hides a follower while a stage shows the same hero (`staged()`, so the player never sees two Ashas). On the strand,
with party `[rhen, asha, toma]` and both followers spawned, the probe gives `asha visible=false staged=true` and
`toma visible=false staged=true`. The follower code works as designed. What the player sees comes from the staging:
Asha and Toma stand at their marks and Rhen walks alone.

## Options (act1-chapters' call)
1. **They follow** (row 39's expectation): hide `Actors/asha` and `Actors/toma` until a scene cues them. The
   sequencer's `@mark` / `@show` brings an actor on, and the follower hides as the stage shows the hero. Toma's
   Shield-Mate prompt (B02) moves to a talk spot, or onto the follower: the stage `Talk` area, re-parented or
   following.
2. **They wait on purpose** (Toma at his talk point, Asha somewhere fitting the beat): keep the actors and give each
   a clear standing beat (an idle or look pose and a place in the frame), so it reads as a choice. Then close row 39
   as by design, with a line in act1_ch09.md.

## Acceptance criteria
- [ ] One of the two, checked in play: the strand walk from Strand to the landing.
- [ ] Row 39 updated (or a line for pc-gpu to update it).

## Notes
- Filed by integration-qa (hero/follower owner), 2026-10-29. The followers themselves need no change. If option 1
  wants them to appear only after a scene, `HeroFieldParty.staged()` already handles the hand-over both ways.

- Row 39 also says "no Toma in Ch4's field and battles". ch04.json seats Rhen, Asha and Toma in every step, so the
  field half is likely the same cause on the wake's stage (an `Actors/toma` standing visible). The battle half was
  seen on big15, before M3-HER-1149's reserve and party fixes. Re-check both on big17 when picking this up.

## Review log
