---
id: M3-ENV-719
title: "Request (character): stamp the Saltwright housing-mark on Rhen's lantern, to match Lowlight's conduit housing"
role: character
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: environment
---
## Goal
In Ch11, Liss reads a Saltwright housing-mark on a Lowlight conduit, "the same make as Rhen's lantern", and Rhen
admits he is Dace's son (act_outline Ch11). Env-art's `conduit_housing` (the Haluna kit's `lowlight.py`; shot L03)
now carries the mark. Dace's diving lantern (rhen.md §3) has no mark yet, so the two can't be compared on screen.

**The mark** (lowlight.md §1; `lowlight._mark`), stamped in relief, about 3 mm proud:
- a circle 15 cm across on the housing, crossed by three fine parallel lines slanted 30° (the Saltwrights'
  camp-sign, as on Ch6's chalk marks);
- two small round seats, side by side under the circle ("pair-built": Liss's word in Ch6).

On the lantern, scale it to the brass collar or base (about 3–4 cm across), in brass.

## Acceptance criteria
- [ ] Rhen's lantern carries the mark (normal map or geometry), legible in a close insert.
- [ ] Its proportions match `conduit_housing`'s (the test `tools/tests/test_lowlight_housing.py` pins the
      housing's).

## Notes
- The Ch6 tideline rule still holds there: no insert that could read the buried lamp's collar (act1_ch06.md §7).

## Review log
