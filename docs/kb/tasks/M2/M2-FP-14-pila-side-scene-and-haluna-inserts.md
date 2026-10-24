---
id: M2-FP-14
title: B04 "Pila's Granddaughter" (optional side scene) at the wake-shell wall, plus Haluna's small inserts
role: cinematics
status: doing
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-13]
milestone: M2
request-from: lead
reviewer: narrative
---
## Goal
The vertical-slice beat sheet's optional side scene, B04 (docs/kb/story/beats/vertical_slice.md §4), and the two small Haluna touches that M2-FP-13 left out.

## Acceptance criteria
- [ ] A new `osu` speaker. Grandmother Osu at the wake-shell wall by the causeway head (H08), interactable any time between `ch02_met_asha` and B05.
- [ ] `ch02_pila_granddaughter.dlg`, about 150 words, following §4's five beats and its rules (Osu speaks no more than four lines in a row; plain, wry voice). It sets `ch02_heard_pila`. In engine, framed on H08 if a shot exists, else the field camera.
- [ ] B02 insert: Asha's packed bag by Neme's door gets a short camera insert (needs a shot and a bag prop or stand-in).
- [ ] H03: the lintel-gulls look-at prompt in the lane.
- [ ] Tests (the scene plays and sets the flag; B09's Teyo branch reads it).

## Notes
- 2026-10-24 m2-slice: **the wake-shell wall is out of reach.** `haluna_layout.json` puts `wakeshell_wall` at (30, −196), but the playable zone's walk rect stops at z −130 (`HalunaCollision.walk_rect`), so Rhen can't get to it. Either Environment moves the wall nearer the causeway head (around the trigger at (7, −125)) or the zone opens a walkable strip out to it. Decide before staging the scene. Deferred behind the Shell Shrine trial, which the slice can't ship without; B04 is optional.

- 2026-10-24 m2-slice, **decision on the wall:** stage Osu at the causeway head, inside `walk_rect` near the trigger at (7, −125), facing out to the wake-shell wall at (30, −196) so H08 frames the wall behind her. I'm not widening the zone (the strip past z −130 is the causeway's own level) and not moving the wall: the layout is Environment's (ownership.md, `haluna_mood/**`). If Environment later adds a wall piece at the head, Osu's spawn is a single data row to move.

## Review log
