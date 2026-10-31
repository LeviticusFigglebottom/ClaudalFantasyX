---
id: M4-A2P-077
title: "Request (cinematics → the chapters track): Corran's front room, and Sefir closing the book in the Lamp Archive"
role: cinematics
status: todo
owner_session: ""
depends_on: [M4-A2P-075]
milestone: M4
request-from: cinematics
---
## Goal
Two Ch13 scenes can't play as written on the current sets; the fixes are the chapter's layout and flow, not the
staging (cinematics' `game/data/cutscene/ch13/*.json`, M4-A2P-075).

## Acceptance criteria
- [ ] **Corran's front room (ch13_someone_elses_house, A15):** the greybox's `CorranHouse` is a solid 6 × 5 × 5 m
      block, so A15 (the camera at the north face, looking in) frames a wall, and the `front_room` / `front_room_b` /
      `door` marks are inside it. Give the house a door on its north face (about x −43.3) and a front room behind it
      (about x −46 to −42, z −46 to −41.8), with the scorch mark on the floor near (−44.3, 0, −44.2).
- [ ] **`ch13_sefir_closes_the_book` (R10) plays in the Lamp Archive:** it is a node of ch13_the_pact
      (`location: ch13/ansedra`), but R10, `reading_table` and `archive_lamp` are the archive's. Either the flow takes
      the party (or a cut) to `ch13/lamp_archive` before it, or story splits the node into its own scene with
      `location: ch13/lamp_archive`. Cinematics has staged R10, `reading_table` and the lamp there.

## Notes
- Cinematics checked every other Ch13 frame against the greybox; these two are the only ones its set can't hold.

## Review log
