---
id: M3-C05-02
title: Ch5 "Terraces of Ash" playable (dialogue, flow, greybox levels, encounters, cutscenes)
role: cinematics
status: review
owner_session: "m2-slice subagent (C05 build)"
depends_on: [M3-C05-01, M3-ARC-01]
reviewer: narrative
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Build Ch5 from its beat sheet (`docs/kb/story/beats/act1_ch05.md`):
- the `.dlg` scripts under `game/data/dialogue/ch05/`;
- the chapter's flow in the M3-ARC-01 chapter data;
- greybox levels under `game/levels/ch05/` (or the night variant named in the sheet), built for env-art's kit to swap in later;
- the encounters, with combat data and `sim.py` bands;
- the cutscenes.

Use env-art, audio and creature swap-in notes as they land.

## Acceptance criteria
- [x] The chapter plays headless from its entry to its exit in an integration test, like `test_fp_thread` (`tests/integration/test_ch05_thread.gd`).
- [x] Every line goes through a loc key or a `#line:` tag; flags are declared in `flags.tres`; `validate_data` and `dlgc --check` are clean.
- [ ] Each boss and encounter has a `sim.py --check` band, and the combat reviewer has seen it. The bands are in; the Matron's `smart` is report only (below), and combat review is pending.
- [x] Each greybox level has a `place_at` root and its spawns, and an entry in `locations.json`.
- [x] PLAYTEST notes for the chapter.

## Notes
2026-10-24, m2-slice subagent (C05 build). Ready for review: **narrative** for the scripts and staging, **combat** for the bands. The handoff is `docs/kb/handoffs/2026-10-24-cinematics-15.md`.
- **Zones:** `ch05/pemakar` (Ch05Zone) and `ch05/ashcrown` (Ch05AshcrownZone). Entry is `ch05/pemakar` at `Harbour`, which Ch4 should hand off to. Exit is the end card, standing in for Ch6's `ch06/brine_shoals`.
- **The flow:** `game/data/flow/chapters/ch05.json`, with 24 `.dlg` scripts in `game/data/dialogue/ch05/`.
- **Watches** (asserted in the test):
  - Kerrid has three lines, none to Rhen, and no `@vfx` at him (ADR 0020 and 0022 (g)).
  - Asha has no rite lines at Lanternfall (ADR 0017).
  - Exactly one boat flag is set, and `kell_wick` is untouched.
- **The Ashcrown trial:** `AshcrownTrial` and `game/data/trials/ashcrown.json`. It is no-fail, and the "before it fades" budget is metres walked.
- **Combat** (provisional; request M3-C05-06):
  - Kerrid's row and gear, and Kahre's vowbound row.
  - Four foes and five encounters.
  - The BossMechanics hooks `cleanses` and `reactions` for the Matron's re-crust and quench.
  - Bands come from the Ch4–Ch9 rows. The Matron's `smart` is report only, with an ease floor of ≥ 40 mean turns: a healing five-hero party wins every seed without a time-pressure mechanic (M3-C05-06).
- **Requests filed:** M3-C05-03 (environment), M3-C05-04 (audio), M3-C05-05 (character, for creatures), M3-C05-06 (combat).

## Review log
