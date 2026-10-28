---
id: M3-ENV-749
title: "Ch4 ferry: place the landing and boarding pieces on the four greybox blocks the dressing still keeps (request to act1-chapters)"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
request-from: environment
reviewer: cinematics
priority: high
---
## Goal
ADR 0041 and the Act I inventory (M3-HER-1140, Ch4 row). `brightwater_ferry_dressing.json`
(`tools/act1/ch04_ferry_dressing.py`) keeps four greybox blocks visible: `IsletRock`, `Gangplank`, `SternGate` and
`NameBoardWrapped`. env-art's ferry kit now has a piece for each (M3-ENV-746, `bf_landing.py`).

## Acceptance criteria
- [x] Add these four rows to the dressing's pieces (all ferry kit, yaw 0, each following its block):

  | Piece | At (x, z) | y | Block |
  |---|---|---|---|
  | `islet_landing` | (12.0, 7.9) | 0.0 | `IsletRock` |
  | `gangplank` | (7.0, 7.9) | 0.0 | `Gangplank` |
  | `stern_gate` | (3.45, 7.9) | 0.0 | `SternGate` |
  | `terrace_name_board_wrapped` | (-2.125, 15.7) | 0.0 | `NameBoardWrapped` |

  - The islet landing is the IsletRock's 10 x 18 m top at y 0; its edges break down to the sea.
  - The gangplank runs from the islet's edge to the rail along -X, with its rope rails on the GangplankRail blocks.
  - The stern gate stands on the deck at the gangway, spanning z.
  - The wrapped name-board lies on the deck.
- [x] Empty `greybox.keep`.
- [ ] Optional: the islet is in pre-dawn dark (F01's foreground reads black). A warm fire light (about 0.8, range 6)
      at the mooring posts (10.6, 1.0, 7.9) would give the landing a lamp.
- [x] Re-render the zone's shots and view them (10-28: ch04_ferry_deck/derelict pass; brightwater_landing_f01/f06
      viewed).

## Notes
- env-art's preview of exactly this is `game/levels/_tests/brightwater_landing/` (`bf_landing_preview.py`; shots
  `brightwater_landing_f01/f06`).

- 2026-10-28 (env-art): done by env-art in `tools/act1/ch04_ferry_dressing.py` (`landing()`), under the Lead's
  10-28 02:40 split, which gives the Prologue–Ch4 dressing and its tools/act1 scripts to env-art. The collision JSON
  is unchanged; `test_ch04_validate` passes.

## Review log
