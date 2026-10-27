---
id: M2-CHR-12
title: Field locomotion clips for Asha, Rhen and Toma (idle variants, walk and run with starts and stops, turns in place)
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
reviewer: lead
depends_on: [M2-FP-07, M2-CHR-07]
milestone: M2
request-from: lead
priority: top
---
## Goal
In the human's playtest the slice heroes walked the field as placeholders, and the prologue's motion read as rigid. The hero-integration track (claude/hero-integration) will put the models and clips into the field. They need grounded, smooth, loopable locomotion for Asha, Rhen and Toma:
- idle, plus idle variants (breathing, weight shift);
- walk and run, in place, with known stride lengths for the field controller;
- walk start and walk stop, run start and run stop;
- turn in place, left and right.

## Acceptance criteria
- [ ] The clips exist for all three heroes, in each hero's idiom:
  - loops are seamless;
  - feet plant without sliding: in-place clips with a documented stride per cycle, so the controller can match the speed;
  - starts and stops blend from and into idle.
- [ ] Stride and speed metadata for the controller, as data or Animation markers, with a test.
- [ ] Rig guards: the ratchets don't rise.
- [ ] Clip libraries regenerate deterministically, and the existing clips are unchanged.
- [ ] Clip shots viewed, and a handoff that lists names, lengths and strides for the hero-integration track.

## Notes

## Review log
