---
id: M4-C14-02
title: Ch14-16 greybox, the end of Act II (the Lacquer Court, the open sea, Hollowmere's first visit, the Pale Rim, the Drowned Choir) before the beat sheets
role: cinematics
status: todo
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M4-C13-02]
reviewer: environment
milestone: M4
request-from: lead
---
## Goal
The rest of Act II's geography from act_outline.md (Ch14-16) and the colour script (`ch14` .. `ch16`), so the stories
slot in when the beat sheets (M4-C14-01 .. M4-C16-01) land. One task for the three chapters (they're small).

## Done (act1-chapters, 2026-10-27)
- `tools/act1/ch14_greybox.py`: **the Lacquer Court** (`ch13/ansedra_lacquer_court`, Ch13Zone): the red-lacquered
  colonnade, the dais (`vows`, `tobin_falls`), the galleries, the Conclave's gallery, the water-steps (a ramp,
  `kerrid_steps`) down to the bridal barge (`barge_deck`; the `barge` trigger runs the escape), the water-gate
  (`merel_gate`).
- `tools/act1/ch15_16_greybox.py`: **the open sea** (`ch15/open_sea`): the barge's deck, the bier, the stern, the
  shoal of held dead below, the bow (`dawn`); **Hollowmere** (`ch17/hollowmere`, Act III's zone, first visit): the
  dock, jetties and hull-houses, the pyre-raft, the supper, the ship (`ship`); **the Pale Rim** (`ch16/pale_rim`):
  the ship, the white wade by the cairns, the Choir's edge; **the Drowned Choir** (`ch16/drowned_choir`): the ring of
  mouths, `kesh`, `sefir`, `kerrid_line`.
- `Ch15Zone`, `Ch16Zone`, `Ch17Zone`; five scenes; `locations.json` rows; `chapters/ch14.json` .. `ch16.json` (each
  arrival sets its chapter; the hand-offs court → sea → Hollowmere → Rim → Choir); five flags; `loc/ch14.csv` ..
  `ch16.csv` (names, two prompts) imported.
- `tests/integration/act2_greybox_case.gd` (the shared visit-and-hand-off base), `test_ch14_16_thread.gd`,
  `test_ch14_16_walkable.gd`.

## Next
- The beat sheets' stories; Warden Malcor Venn, the Wakefin, the Abiding guard (creatures, encounters, sim bands).
- `ch17/hollowmere` is Act III's zone too: its later visits join ch17.json's block (the zone key moves there).

## Review log
