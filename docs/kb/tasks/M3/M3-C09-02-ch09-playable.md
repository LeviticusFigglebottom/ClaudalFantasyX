---
id: M3-C09-02
title: Ch9 "The Ebbing" playable (dialogue, flow, greybox levels, encounters, cutscenes)
role: cinematics
status: doing
owner_session: "m2-slice subagent (C09 build)"
depends_on: [M3-C09-01, M3-ARC-01]
reviewer: narrative
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Build Ch9 from its beat sheet (`docs/kb/story/beats/act1_ch09.md`):
- the `.dlg` scripts under `game/data/dialogue/ch09/`;
- the chapter's flow in the M3-ARC-01 chapter data;
- greybox levels under `game/levels/ch09/` (or the night variant named in the sheet), built for env-art's kit to swap in later;
- the encounters, with combat data and `sim.py` bands;
- the cutscenes.

Use env-art, audio and creature swap-in notes as they land.

## Acceptance criteria
- [ ] The chapter plays headless from its entry to its exit in an integration test, like `test_fp_thread`.
- [ ] Every line goes through a loc key or a `#line:` tag; flags are declared in `flags.tres`; `validate_data` and `dlgc --check` are clean.
- [ ] Each boss and encounter has a `sim.py --check` band, and the combat reviewer has seen it.
- [ ] Each greybox level has a `place_at` root and its spawns, and an entry in `locations.json`.
- [ ] PLAYTEST notes for the chapter.

## Notes

## Review log
