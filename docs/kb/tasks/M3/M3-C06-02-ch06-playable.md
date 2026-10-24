---
id: M3-C06-02
title: Ch6 "Salt Edict" playable (dialogue, flow, greybox levels, encounters, cutscenes)
role: cinematics
status: review
owner_session: "m2-slice subagent (C06 build)"
depends_on: [M3-C06-01, M3-ARC-01]
reviewer: narrative (scripts and staging); combat (the bands)
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Build Ch6 from its beat sheet (`docs/kb/story/beats/act1_ch06.md`):
- the `.dlg` scripts under `game/data/dialogue/ch06/`;
- the chapter's flow in the M3-ARC-01 chapter data;
- greybox levels under `game/levels/ch06/` (or the night variant named in the sheet), built for env-art's kit to swap in later;
- the encounters, with combat data and `sim.py` bands;
- the cutscenes.

Use env-art, audio and creature swap-in notes as they land.

## Acceptance criteria
- [x] The chapter plays headless from its entry to its exit in an integration test, like `test_fp_thread`.
- [x] Every line goes through a loc key or a `#line:` tag; flags are declared in `flags.tres`; `validate_data` and `dlgc --check` are clean.
- [x] Each boss and encounter has a `sim.py --check` band (the combat reviewer hasn't seen it yet: review).
- [x] Each greybox level has a `place_at` root and its spawns, and an entry in `locations.json`.
- [x] PLAYTEST notes for the chapter.

## Notes
2026-10-24 (m2-slice subagent, C06 build). Handoff: docs/kb/handoffs/2026-10-24-cinematics-17.md.
- **Built:** one greybox zone, `ch06/brine_shoals` (Ch06Zone: Ch04Zone's flag-driven states, plus layout `lights` and `checkpoint`); 14 scripts in `game/data/dialogue/ch06/`; `game/data/flow/chapters/ch06.json`; `game/data/loc/ch06.csv`; `tests/integration/test_ch06_thread.gd` (5 tests).
- **Seams:** Ch5's dawn now hands off to `ch06/brine_shoals` at `Entry` (ch05.json and test_ch05_thread updated); B10 hands off to `ch07/tamsule` at `RiverMouth`.
- **B05 (Sefir) against ADR 0017 (a):** his lines are the sheet's, verbatim, item by item, with every staging rule kept and the §5a tells played flat. The test checks his line set, no contraction, no mark (he never steps onto the mud), only wide shots before his first line, his theme after it, no @vfx and no sound but the poles and the iron, no Liss line or glare, half a beat on Kerrid's back and 1.5 s on the crate, and "once it had finished" after he has gone. Asha has no line in B07, and no Ch6 line names the lamp.
- **The fight:** encounter rules `forbidden_skills` (Toma's offensive skills greyed and refused against foes tagged `stillguard`; both foes are) and `yield_at_hp_pct` (both yield at 0 HP; nobody dies), plus `victory_key` for "The Inquisitor yields." (battle_ctb.md; `tests/unit/test_battle_forbidden_yield.gd`, 12 tests). `party_skills` lends Toma his guard and a no-cost Stand Fast. The sim's `role_answer` steps a forbidden hero back for a reserve striker.
- **Liss:** a PROVISIONAL `characters.json` row and placeholder gear, in no sim suite; she joins in reserve after B06.
- **Bands (1000 seeds):** five suites, all in band; two logged exceptions (skipper suites' `role_answer` report only; the Inquisitor's `smart` ceiling lifted with a 25-mean-turn floor). Two of the sheet's flats groups were cut. balance_targets.md "Ch6", balance_report.md tuning log.
- **Stand-ins for the reviewers:** Ysolde's field bark closes B03 and the Inquisitor's yield bark opens B05; Toma's "No. Not them." is his first-turn prompt. The B08 vendor reuses `brightwater_purser`.
- **Requests:** M3-C06-03 (environment), M3-C06-04 (audio), M3-C06-05 (combat), M3-C06-06 (character), M3-C06-07 (narrative: canon lines, glossary, the burned lamp's design truth).

## Review log
