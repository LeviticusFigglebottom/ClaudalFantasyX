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

## Review log
