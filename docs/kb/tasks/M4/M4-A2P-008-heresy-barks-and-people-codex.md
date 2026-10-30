---
id: M4-A2P-008
title: "Act II state lines: heresy barks, Kerrid's revealed barks, and the people's codex pages"
role: narrative
status: review
owner_session: "act2 story track (claude/act2-plan, ADR 0205)"
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

## Done (story track, 2026-10-30)
- **Codex (people), 12 entries:** `owa`, `tobin`, `merel`, `ressa`, `ama_quillo`, `corran`, `malcor_venn`, `conclave`, `brannoc_hale`, `aldous_varrow`, `kesh`, `kerrid_stair`.
  - Each unlocks on its chapter's flag and uses the bible's own words (unrisen, held).
  - The rows are appended to `codex.json`, `loc/codex.csv` and `flags.tres` (`codex_<id>_read`).
  - The Kerrid entry is a second page, `kerrid_stair`, unlocked by `ch15_kerrid_told`, because the codex has no conditional body.
  - The Archive's records stay in the `ch13_archive_*` scripts for the document reader: a `records` or `world` entry would break `test_codex.gd`'s pinned counts, which are ui-menus'.
- **Heresy barks:** `ch14_bark_purveyor_refuses`, `ch14_bark_dark_shrine` and `ch15_bark_outside_the_level`.
- **Kerrid's post-reveal barks:** `ch15_bark_kerrid_night` and `ch15_bark_kerrid_floors`, plus the Ch16 wade bark.
- **Checks:** validate_data, dlgc, Godot `--filter=act2_dialogue` and `--filter=codex` 15/0. Reviewer: ui-menus.

## Review log
