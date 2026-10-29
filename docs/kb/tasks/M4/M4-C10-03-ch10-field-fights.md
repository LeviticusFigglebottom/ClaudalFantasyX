---
id: M4-C10-03
title: Ch10's field fights on creatures' Act II roster (tannin archer, root crab, fen leech), with sim bands
role: cinematics
status: blocked
blocked-by: ADR 0041
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M4-C10-02, M3-CRE-620]
reviewer: combat
milestone: M4
request-from: lead
---
## Goal
The Lead's queue (2026-10-28): Act II encounter tables on creatures' Act II roster (`docs/kb/art/creatures/act2_roster.md`,
which leaves stats, skills and AI to the chapter track). Ch10's regulars on Ossa Fen's root-walks, none in Reedhollow
(the roster's proposal).

## Done (act1-chapters, 2026-10-28)
- `enemies.json` (appended): `tannin_archer` (every other turn its jet delays; lightning-weak), `root_crab` (the reef
  crab's mangrove cousin: a shell, Toma's; Root Drag every third turn), `fen_leech` (a poisoning bite: the roster's
  drain waits on M4-CMB-1001). No models yet (M3-CRE-620 builds the regulars after the bosses).
- `skills.json` (appended, Combat's file; flagged for review): `tannin_jet`, `root_drag`, `leech_bite`.
- `encounters.json` (appended): `ch10_fen_archers`, `ch10_fen_roots`, `ch10_fen_leeches`; Ossa Fen's table (2:1:1,
  30-50 m, from `ch10_started`) in `tools/act1/ch10_greybox.py`.
- `creature_voices.json` (appended, audio's file): the three as "silent" until audio voices them (M4-AUD-1001).
- `tools/balance/targets.json`: three suites on the `ch08_seawall` loadout (the last chapter loadout; a Ch10 loadout
  comes with Act II's shops). 1000 seeds, `--check` clean: archers 54.0/97.3 naive/smart (role_answer report only:
  lightning is Kahre's, no hero's role answers them, as for ch06_ridge_gulls), roots 33.8/93.9/99.9, leeches
  48.5/99.9 (role_answer report only: the role play focuses and never heals, and the leeches' poison is a healing
  lesson).
- Loc: names, lore and skills in `game/data/loc/ch10.csv`.

## Next
- The Mangrove Drowner (two phases) when the beat sheet places it (M4-C10-01); Ch11-16's regulars the same way.

## Review log
