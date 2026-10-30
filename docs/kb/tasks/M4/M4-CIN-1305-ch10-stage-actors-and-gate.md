---
id: M4-CIN-1305
title: "Request (cinematics track → the chapters track): Ch10's stage actors, the hold gate and its two prompts, for the staged scenes"
role: cinematics
status: todo
owner_session: ""
depends_on: [M4-A2P-010]
milestone: M4
request-from: cinematics
---
## Goal
Ch10's cutscene shots and marks are staged (cinematics' `game/data/cutscene/ch10/*.json`, M4-CIN-1304). The scenes
also `@mark` and `@anim` people the layouts don't have yet, and the farewell-tide needs a hold gate. These are the
chapter's (layout actors, the zone's host wiring).

## Acceptance criteria
- [ ] **ossa_fen** stage actors (hero bodies or casts): `asha`, `toma`, `ysolde`, `liss`, `kerrid`, standing on the
      bank behind FenEdge in the Ch9 line (ch10_fen_edge walks them to `fen_line_*`, then onto the root-walk), and
      `mangrove_drowner` at the dead tree (`"cast": "creature:mangrove_drowner"` once creatures-b has the model;
      ch10_dead_channel's `@anim mangrove_drowner stir`).
- [ ] **reedhollow** stage actors: `owa` (the eldest; a Kirru cast, M4-A2P-053), inside the ring near the causeway's
      east end (she walks to `causeway_gate`); `asha`, `toma`, `ysolde`, `liss`, `kerrid` (the gate scenes and the
      shore). For the farewell-tide, the party stands on the shore behind the clutch: Asha at `shore_front`
      (66.6, 0, 0), the others 0.8–1.2 m behind her. The clutch (`clutch_0..7`) is shown by the beat (`show_block`), as
      Ch1's Hullgnaw is; `@anim clutch turn_back` plays on every `clutch_*` actor (CutsceneGroup).
- [ ] **The hold gate on Reedhollow's story sequencer** (as Ch09Zone's `hold_gate`), with prompts
      `hold_to_watch` ("Hold to watch") and `release_tide` ("Release") as loc keys: ch10_farewell_tide opens
      `<<event hold_input hold_to_watch>>`, then `<<event release_input release_tide>>` (the release gate,
      M4-CIN-1302).
- [ ] Optional, for the staging to read as written: the clutch nearer the waterline (x ≈ 61–62, not 64–65), so the
      party has room behind it on the shore; the T-shots are framed for either.

## Notes
- Cinematics' staging review (M4-C10-01) and M4-A2P-070. The stills wait on these actors.

## Review log
