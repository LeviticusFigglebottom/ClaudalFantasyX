---
id: M2-UI-02
title: Read result panel, bestiary menu and opening banner
role: ui
status: todo
owner_session: ""
depends_on: [M1-CMB-03]
milestone: M2
request-from: combat
---
## Goal
SPEC §6.1 and §6.11. M1-CMB-03 ships Read, the bestiary log and preemptive/ambush openings with only two float lines for feedback. Give them real HUD and menu views.

## Acceptance criteria
- [ ] After a Read, a short panel shows the foe from `BattleController.bestiary.last_reveal` (`BattleRead.reveal`): name, HP and MP as they stand, the eight stats, the four affinity lists, delay immunity, current statuses, and the lore text (`lore_key`). It closes on confirm and costs no battle time.
- [ ] A bestiary menu (out of battle) lists `Bestiary.known_ids()` from `Game.state.bestiary`. A Read entry shows the page from enemies.json (stats, weaknesses, lore) and the defeat count. An entry that was defeated but never Read shows its name and count only. Ids enemies.json no longer lists are skipped on screen, never removed from the save.
- [ ] A clear banner for a preemptive or ambush opening (`BattleOpening.CAPTION_KEYS`, `engine.opening`), replacing or joining the float that `BattleBestiary` shows today. Keep it within the HUD build budget (M1-UI-03), and add screenshot fixtures if it is visible in a capture.
- [ ] New strings go through loc keys appended to strings.csv. Element names are already there as `ELEMENT_*`.

## Notes
- Rules and data: docs/kb/design/battle_ctb.md "Read, the bestiary and openings", formulas.md § Openings.

## Review log
