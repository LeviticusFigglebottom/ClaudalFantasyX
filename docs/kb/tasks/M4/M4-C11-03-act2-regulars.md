---
id: M4-C11-03
title: Ch11, Ch12 and Ch16's field fights on creatures' Act II roster, with sim bands
role: cinematics
status: blocked
blocked-by: ADR 0041
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M4-C11-02, M4-C12-02, M4-C14-02, M3-CRE-620]
reviewer: combat
milestone: M4
request-from: lead
---
## Goal
The Lead's queue (2026-10-28): Act II encounter tables on creatures' Act II roster
(`docs/kb/art/creatures/act2_roster.md`), after Ch10's (M4-C10-03). Covers the walked routes with regulars: Sunken Vey's
galleries (Ch11), Keth Pass (Ch12) and the Pale Rim (Ch16). Ch13-15 are towns, a court and open sea, so they get no
random tables.

## Done (act1-chapters, 2026-10-28)
- `enemies.json` (appended): `gallery_ray` (evasive, Rhen's), `rime_urchin` (Ysolde's), `ridge_lynx` (pounces on
  the weakest every third turn, Rhen's), `cord_moth` (evasive, unravels, Ysolde's), `scree_crawler` (armoured,
  Kerrid's), `glass_skate` (Rhen's), `rim_crawler` (Toma's). No models yet (M3-CRE-620).
- `skills.json` (appended, Combat's file; flagged for review): `glide_lash`, `rime_spine`, `unravel`, `scree_slide`,
  `skate_sting`.
- `encounters.json` (appended): `ch11_vey_rays`, `ch11_vey_urchins`, `ch12_pass_lynxes`, `ch12_pass_moths`,
  `ch12_pass_scree`, `ch16_rim_skates` (an ambush), `ch16_rim_crawlers`. Tables (30-50 m, from each chapter's
  `chNN_started`) in `tools/act1/ch11_greybox.py` (1:1), `ch12_greybox.py` (2:1:1, Keth Pass only) and
  `ch15_16_greybox.py` (1:1, the Pale Rim only).
- `creature_voices.json` (appended, audio's file): all seven "silent" until audio voices them (M4-AUD-1001).
- `tools/balance/targets.json`: seven suites on the `ch08_seawall` loadout (`ch12_pass_scree` puts Kerrid in the
  active three). 1000 seeds, `--check` clean on all ten Act II suites (naive / role_answer / smart):
  rays 48.3 / report / 99.6, urchins 50.0 / 99.6 / 100, lynxes 47.7 / report / 99.3, moths 58.4 / 95.5 / 99.7,
  scree 56.1 / 93.6 / 100, skates 52.1 / report / 97.9, crawlers 42.2 / report / 97.4. The report-only role bands
  are Rhen's answers (logged exceptions, as for ch06_ridge_gulls) and the crawler swarm (the role play focuses one at
  a time); reasons are in each suite's `chapter` line.
- Loc: names, lore and skills in `game/data/loc/ch11.csv`, `ch12.csv` and `ch16.csv`.

## Next
- Act II's bosses when the beat sheets (M4-C11-01 to M4-C16-01) place them; an Act II loadout with Act II's shops.

## Review log
