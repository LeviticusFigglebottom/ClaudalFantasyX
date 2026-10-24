---
id: M2-FP-15
title: B11 "The dock at night" (in-engine, after the Drownbell, before the end card)
role: cinematics
status: todo
owner_session: ""
depends_on: [M2-FP-13, M2-ENV-02]
milestone: M2
request-from: lead
reviewer: narrative
---
## Goal
B11 is never cut (vertical_slice.md §1). After the Drownbell, Rhen finds Asha on Haluna's dock at night (H10: oil lamps in the windows, sea-glow at 0.12, stars), asks to come as a guardian, and she says yes before Toma can object.

## Acceptance criteria
- [ ] `ch03_dock_at_night.dlg`, about 90 words per §2 B11, with the `ch03_rhen_asked_after` variant. It sets `ch03_rhen_sworn_guardian`.
- [ ] The thread runs the Drownbell victory → Haluna at night (the dock spawn) → B11 → the end card. `first_verse.return_scene` changes from the end card to that.
- [ ] Haluna's barks switch to the night variant (guardian blessings) once `ch03_rhen_sworn_guardian` is set (§2 B03).
- [ ] Uses Environment's night light (M2-ENV-02). Until then, a documented stand-in (the noon light dimmed by a data value).
- [ ] Tests, including the whole thread.

## Review log
