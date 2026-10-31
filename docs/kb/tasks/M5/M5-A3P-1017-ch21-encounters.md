---
id: M5-A3P-1017
title: "Request (combat): Ch21's fights (Kesh; Sefir's Warden, heart and Letting phases) and their fight lines"
role: combat
status: review
owner_session: "act1-chapters"
depends_on: [M5-A3P-1014, M5-A3P-1009]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
The Ch21 scripts start encounters that don't exist yet: `ch21_kesh`, `ch21_sefir_heart` and `ch21_sefir_letting`.
The flow starts phase 1, `ch21_sefir_warden`, after R1 (drafts README decision 13). Brief: act3_ending.md (H03–H08).
- **Fight lines** (`ch21_bark_sefir.dlg`, H04/H06): warm and reasonable. They need M5-A3P-1009's mid-battle hook.
- **Line order:** H04, the Warden phase: the opening, when he settles the timeline, and at 50% (to Asha). H06, the heart phase: the opening, and at 25%. Each node's comment names its trigger.

## Acceptance criteria
- [ ] The encounters exist, chained as the flow needs; each fight line plays at its trigger.

## Notes (act1-chapters, the chapters combat seat, 2026-10-31)
- **Encounters** (all scripted, PROVISIONAL), chained by the flow (M5-A3P-1015):
  - `ch21_kesh`: `kesh_held` (creatures-b's held model). Six element phases (each absorbs its own element and is
    weak to Ysolde's ice or fire); `release` at 8%.
  - `ch21_sefir_warden` (H04, the flow starts it after R1): Patience (Protect, Shell), Settle (every hero set back),
    and at 50% he turns to Asha.
  - `ch21_sefir_heart` (H06): Draw (glimmer from every hero), the storm's note; at 25% the note deepens; he absorbs
    glimmer.
  - `ch21_sefir_letting` (H07): Asha off the timeline (`unavailable`); her verse is the ward entry `the_letting`
    (objective quota 5); Toma is locked in covering it; Sefir's Reach pushes it; the Long Stillness raises the Stilled
    (a tide, two at most); Sefir can't be felled (`hp_floor_pct`).
- **Bands** (500 seeds; balance_targets.md "Act III"): Kesh 57.6, Warden 59.8, heart 63.8 (the Act III boss band);
  Letting role 89.6 (the set-piece band, its naive floor 0, with the reason).
- **Open:**
  - The fight lines (`ch21_bark_sefir.dlg`) wait on M5-A3P-1009's mid-battle hook.
  - Sefir and the Stilled have no battle model (qa_known capsules; M5-A3P-1849).
  - Audio: `ch21_sefir_warden` has no `encounter_music` row yet (the others map: kesh_first_voice, sefir_heart,
    the_letting). I took the three now-written ids off `music.json` `pending_encounters` (validate_data demanded it).

## Review log
