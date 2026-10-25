---
id: M3-C09-07
title: "Pell's battle kit and his place in the party (joins in Ch9, fights from Ch10)"
role: combat
status: todo
owner_session: ""
depends_on: [M3-C09-02]
milestone: M3
request-from: cinematics
---
## Goal
Pell joins at the end of Ch9's B08 (act1_ch09.md; pell.md). Ch9 has no fight, and he has no `characters.json` row, so M3-C09-02 records his joining by flag only: `ch09_pell_joined` (and `ch09_pell_named` at B09). He is in no party list and no sim suite.

From Ch10 he is in the party: three active plus four in reserve (act1_ch09.md §10), and he is new to the formation menu. Give him a battle kit before Ch10's first fight.

## Acceptance criteria
- [ ] A `characters.json` row for `pell` (stats, skills, Swell, Lattice start, gear) from pell.md and the combat design docs.
- [ ] Ch10's chapter flow seats him from `ch09_pell_joined`. The Ch9 flow needs no change: Ch9 never fights.
- [ ] His `sim.py` suites and bands come with Ch10's encounters, not Ch9's. Ch9 adds no suite.
- [ ] **Liss.** She also has no battle row, though she is one of the seven at the act's end. Check that her row is planned (Ch6, M3-C06-*).

## Notes

## Review log
