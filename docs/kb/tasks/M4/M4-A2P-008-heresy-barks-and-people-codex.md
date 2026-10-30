---
id: M4-A2P-008
title: "Act II state lines: heresy barks, Kerrid's revealed barks, and the people's codex pages"
role: narrative
status: doing
owner_session: "claude/ui (ui-menus, narrative seat for the codex)"
depends_on: [M4-A2P-005, M4-A2P-006]
reviewer: ui
milestone: M4
request-from: lead
---
## Goal
The lines that change by state across Act II: every town NPC's heretic-state line from `ch14_declared_heretics` on, Kerrid's party barks before and after the reveal, and codex pages for Tobin, Merel, the Conclave (as the public knows it), Ressa, Ama Quillo, Corran and Kesh, plus Kerrid's page rewritten after Ch15 in the bible's own words (unrisen, held).

## Acceptance criteria
- [ ] Loc rows and codex.json rows (with ui-menus), each behind its flag.
- [ ] validate_data and banned-terms clean (the inspiring game's words for the lingering dead are banned).
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.2, §4.3, §4.5.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30 ui-menus: Act II started per track (ADR 0205). Ch10 codex entries in: the farewell-tide (`ch10_farewell_tide_seen`, declared here for the Ch10 dialogue to set), name-shells and the Eldest of Reedhollow (`ch10_reached_reedhollow`). The heresy barks and Kerrid's barks wait on the Ch14/Ch15 dialogue (M4-A2P-005/006).
- 2026-10-30 ui-menus: **four more entries whose flags are declared:** `keth` (World, `ch12_reached_quellan`), `conclave` (World, `ch13_started`, the public "Conclave of Elders" only, no truth and no "revenant", ADR 0016), `malcor_venn` (People, `ch14_started`, a man and nothing stranger, ch14 rule 2) and `heresy` (World, `ch14_declared_heretics`, titled "Outside the Level", ADR 0204). Read flags declared; test_codex totals 14 to 17; validate_data (banned terms) clean.
  - The rest of codex_bestiary.md's list waits on their beats' flags (ch11 to ch16: Tobin, Merel, Wenna, Ama, Corran, the Vowbound, the Hush, Liss's father; Kerrid, Sefir and Pell's second bodies). Each lands as soon as its flag is declared.

## Review log
