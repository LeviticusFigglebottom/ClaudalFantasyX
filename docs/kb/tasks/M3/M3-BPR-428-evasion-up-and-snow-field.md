---
id: M3-BPR-428
title: "Request (the chapters' combat seat): an evasion-up status for the Wakefin's Sound Dive, and the Ram's snow field"
role: combat
status: todo
owner_session:
depends_on: []
milestone: M4
request-from: combat
---
## Goal
battle-presentation wrote PROVISIONAL rows for the four Act II creature bosses (the Lead, 10-30) so their staging
goes live. Two of their sheet mechanics have no engine rule yet, and the rows stand in for them:

1. **The Wakefin's Sound Dive (ADR 0204 #3): evasion up, with a clear telegraph.** `statuses.json` has no
   evasion-up status. Today `sound_dive` is a one-turn telegraphed charge into `wake_breach`, with no evasion change.
   - Asked for: a beneficial status, for example `evasion_up` ("Evasion +N"), applied by `sound_dive` to the
     Wakefin while the dive is held. Its numbers go in formulas.md, formulas.gd and test_formulas.gd, in one commit.
   - The timeline shows it (pillar 4). battle-presentation then adds its status tick.
2. **The Avalanche Ram's snow (act2_roster.md: "a charging boss whose charge brings down the snow, a field hazard
   round by round").** Today `ram_bellow` is a one-off blow on every hero, with Slow at 30%.
   - Asked for: a field (as the Drownbell's flood and Ch8's storm_dark) that the bellow raises and that hurts or
     slows each round, with the field HUD row.
   - ADR 0204: it is snow and grit, never ice.

## Acceptance criteria
- [ ] Both exist in data and the engine, with tests, and the two skill rows' `_note` "PROVISIONAL" lines are updated.
- [ ] Each is banded in its boss suite (balance_targets.md, Act II boss).

## Notes
- The rows are in skills.json, enemies.json and encounters.json, each marked `"provisional": true`.

## Review log
