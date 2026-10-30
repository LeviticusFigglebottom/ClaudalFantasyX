---
id: M4-C13-02
title: Ch13 "Gold and Lacquer" greybox (ch13/ansedra, ch13/sanctum, ch13/lamp_archive) before the beat sheet
role: cinematics
status: todo
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M4-C12-02]
reviewer: environment
milestone: M4
request-from: lead
---
## Goal
Ch13's geography from act_outline.md (Ch13) and the colour script's `ch13` (an overcast 16:30, still air, gold domes
doubled in a mirror lagoon; gold that must feel cold), so the story slots in when the beat sheet (M4-C13-01) lands.

## Done (act1-chapters, 2026-10-27)
- `tools/act1/ch13_greybox.py`: **Ansedra**, the outer moorings and their lacquered barges (`kerrid_moorings`), the
  causeways with gold lamp-posts to the central island and Sefir's house (`sefir_door`), Corran's old house
  (`corran_house`), the archive's isle and the Sanctum's, gold bowl-domes; **the Sanctum**, the vestibule, the nave
  round the still basin (lit from beneath, ringed by a kneeling ledge), `ethren`, `corran`, `pilgrims`; **the Lamp
  Archive**, the reading room between stacks, `ledgers`, `cantor_roll`.
- `Ch13Zone`; three scenes; `locations.json` rows; `chapters/ch13.json` (the chapter becomes 13; the city to each and
  back; Kerrid out of the Sanctum by party steps); three flags; `loc/ch13.csv` imported.
- `tests/integration/test_ch13_thread.gd`, `test_ch13_walkable.gd`.

## Next
- The beat sheet's story (no boss in Ch13's outline).

## Review log
