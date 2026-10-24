---
id: M2-FP-14
title: B04 "Pila's Granddaughter" (optional side scene) at the wake-shell wall, plus Haluna's small inserts
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-13]
milestone: M2
request-from: lead
reviewer: narrative
---
## Goal
The vertical-slice beat sheet's optional side scene, B04 (docs/kb/story/beats/vertical_slice.md §4), and the two small Haluna touches that M2-FP-13 left out.

## Acceptance criteria
- [x] A new `osu` speaker. Grandmother Osu at the wake-shell wall by the causeway head (H08), interactable any time between `ch02_met_asha` and B05.
- [x] `ch02_pila_granddaughter.dlg`, about 150 words, following §4's five beats and its rules (Osu speaks no more than four lines in a row; plain, wry voice). It sets `ch02_heard_pila`. In engine, framed on H08 if a shot exists, else the field camera.
- [x] B02 insert: Asha's packed bag by Neme's door gets a short camera insert (needs a shot and a bag prop or stand-in).
- [x] H03: the lintel-gulls look-at prompt in the lane.
- [x] Tests (the scene plays and sets the flag; B09's Teyo branch reads it).

## Notes
- 2026-10-24 m2-slice: **the wake-shell wall is out of reach.** `haluna_layout.json` puts `wakeshell_wall` at (30, −196), but the playable zone's walk rect stops at z −130 (`HalunaCollision.walk_rect`), so Rhen can't get to it. Either Environment moves the wall nearer the causeway head (around the trigger at (7, −125)) or the zone opens a walkable strip out to it. Decide before staging the scene. Deferred behind the Shell Shrine trial, which the slice can't ship without; B04 is optional.

- 2026-10-24 m2-slice, **decision on the wall:** stage Osu at the causeway head, inside `walk_rect` near the trigger at (7, −125), facing out to the wake-shell wall at (30, −196) so H08 frames the wall behind her. I'm not widening the zone (the strip past z −130 is the causeway's own level) and not moving the wall: the layout is Environment's (ownership.md, `haluna_mood/**`). If Environment later adds a wall piece at the head, Osu's spawn is a single data row to move.

- 2026-10-24 m2-slice, **done, for review by narrative:**
  - **B04:** `ch02_pila_granddaughter.dlg` is about 150 words: §4's five beats, Osu never more than three lines in a row. It sets `ch02_heard_pila`. A second visit gets one short line (`_015`).
  - **Osu:** a new speaker `osu` (`CHAR_OSU`), with a Talk prompt from `ch02_met_asha`. At night she is removed through `night_hide`.
  - **Shots:** H08 is a locked three-quarter on Osu against the wall; H08_hand is the insert on Teyo's shell.
  - **Staging:** the beat calls for the wake-shell wall and the playable zone can't reach it, so a greybox stand-in wall (shells and the new gap) stands behind her at the causeway head. **M2-ENV-04** asks Environment for the real piece there; this supersedes the earlier "facing out to the wall" note, because the coral tide-wall hides the far piece.
  - **B02:** a bag stand-in by Neme (`NPCs/Neme/Bag`, removed at night) and the `B02_bag` insert after her last line, then `@camera release`.
  - **H03:** a "Look" prompt in the lane at the doorway gap in front of house_tile_b (`FIELD_PROMPT_LOOK`). `ch02_look_lintel_gull` holds a raised camera on that house's ridge gull, with one Rhen line.
  - **Tests:** `tests/integration/test_haluna_b04.gd` (8), including the chain into B09's Teyo line (`ch03_verse_034`). `test_haluna_zone.gd` lists the new shots.
  - **Checked by eye** on lavapipe: H08, H08_hand, H03, B02_bag. No manifest shot renders this scene (they use `haluna_mood.tscn`).

## Review log
