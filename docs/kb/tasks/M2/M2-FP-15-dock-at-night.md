---
id: M2-FP-15
title: B11 "The dock at night" (in-engine, after the Drownbell, before the end card)
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-13, M2-ENV-02]
milestone: M2
request-from: lead
reviewer: narrative
---
## Goal
B11 is never cut (vertical_slice.md §1). After the Drownbell, Rhen finds Asha on Haluna's dock at night (H10: oil lamps in the windows, sea-glow at 0.12, stars), asks to come as a guardian, and she says yes before Toma can object.

## Acceptance criteria
- [x] `ch03_dock_at_night.dlg`, about 90 words per §2 B11, with the `ch03_rhen_asked_after` variant. It sets `ch03_rhen_sworn_guardian`.
- [x] The thread runs the Drownbell victory → Haluna at night (the dock spawn) → B11 → the end card. `first_verse.return_scene` changes from the end card to that.
- [x] Haluna's barks switch to the night variant (guardian blessings) once `ch03_rhen_sworn_guardian` is set (§2 B03).
- [x] Uses Environment's night light (M2-ENV-02). Until then, a documented stand-in (the noon light dimmed by a data value).
- [x] Tests, including the whole thread.

## Notes (m2-slice, 2026-10-24)
- **Thread.** The Drownbell victory travels to `ch02/haluna` at `DockNight`. `HalunaStory` then plays B11 under `HalunaZone.set_night` (the stand-in) and hands off to the end card. Details: first_playable_flow.md, "The Shell Shrine trial and the dock at night".
- **Text, for narrative's review:**
  - `ch03_dock_at_night` is ~90 words. Toma's objection is "Asha. A guardian is not chosen on a dock, at night—", and her answer is "This one was, Toma.", in keeping with her very short refusals.
  - The `ch03_rhen_asked_after` branch adds three lines: Rhen almost asks; she asks about his day; he lets her.
  - Four night blessings (`ch03_bark_*_night`) are reachable only once Rhen is sworn. The slice's end card follows B11, so today you can see them only through debug.
- **Stand-in night.** The sun is at 0.12× and `#9DB2E0`, the sky ×0.12, the ambient ×0.3, plus four warm lamps (data). Replace it with M2-ENV-02's real night.
- **Asha** keeps her kneeling beach pose at the end of the dock (no clips yet; M2-FP-07).
- Tests: `tests/integration/test_haluna_night.gd` (4). Updated: the whole thread, `test_fp_first_verse` (the win travels) and `test_haluna_zone` (the DockNight spawn sits on the deck, not the terrain).

## Review log
