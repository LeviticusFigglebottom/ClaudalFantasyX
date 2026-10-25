---
id: M3-C08-02
title: Ch8 "The Seawall" playable (dialogue, flow, greybox levels, encounters, cutscenes)
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M3-C08-01, M3-ARC-01, M3-CMB-01]
reviewer: narrative
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Build Ch8 from its beat sheet (`docs/kb/story/beats/act1_ch08.md`):
- the `.dlg` scripts under `game/data/dialogue/ch08/`;
- the chapter's flow in the M3-ARC-01 chapter data;
- greybox levels under `game/levels/ch08/` (or the night variant named in the sheet), built for env-art's kit to swap in later;
- the encounters, with combat data and `sim.py` bands;
- the cutscenes.

Use env-art, audio and creature swap-in notes as they land.

## Acceptance criteria
- [x] The chapter plays headless from its entry to its exit in an integration test, like `test_fp_thread`.
- [x] Every line goes through a loc key or a `#line:` tag; flags are declared in `flags.tres`; `validate_data` and `dlgc --check` are clean.
- [ ] Each boss and encounter has a `sim.py --check` band, and the combat reviewer has seen it. The set piece's four are M3-CMB-01's. The three field fights are new here; the combat reviewer has **not** seen them yet (M3-C08-100).
- [x] Each greybox level has a `place_at` root and its spawns, and an entry in `locations.json`.
- [x] PLAYTEST notes for the chapter.

## Notes
- 2026-10-24, m2-slice worktree agent (C08 build). Ready for review (reviewer: **narrative**, SPEC §12.3). Handoff: `docs/kb/handoffs/2026-10-24-cinematics-m2-slice-1.md`.
- **What was built:**
  - 23 `.dlg` scripts in `game/data/dialogue/ch08/` (B01-B18, B03's side scene, four barks and the trial's hint), about 620 words;
  - `ch08.json`, with two zones: `ch08/corrow` (`Ch08Zone`) and `ch08/coilspire` (`Ch08CoilspireZone` with `CoilspireTrial`);
  - `ch08_field.json`;
  - the flow's stair meter: a battle step's `objective_flag`, carried by `BattleRequest` and written by `FieldBattle`, and put back on "Fight again";
  - three field enemies (`stormgull`, `wallcrab`, `flue_moth`) and three encounters, each with a `sim.py` suite;
  - the speaker `ivo`; 22 Ch8 flags;
  - `test_ch08_thread.gd` (six tests) and `tools/tests/test_ch08_flow.py` (seven tests).
- **Hand-offs:** Ch7's `leave` now goes to `ch08/corrow` at `Mole`. Ch8's B18 goes to `ch09/corrow_night` at `Strand`, so Ch9's zone stays a location of its own (M3-C09-04 can still fold it into `ch08/corrow`).
- **The rules, and how each is held:**
  - **Nothing bound against the storm:** the beacon is the player's one input, and the hoist is rope and iron. No `@vfx` names Kerrid anywhere in Ch8 (tested).
  - **B15:** all cuts, no `@vfx`, and `@music silence` before "Captain?" (tested). W10_below is the far wall-head only. Kerrid looks, goes down a step, and gets no close-up after it.
  - **No return for Kerrid:** his only Ch8 line is "Later." (tested). There's no Corrow line for him, and nobody tells the 1001 story.
  - **The freeze:** Rhen has no line from the figure's first shot to its exit. The figure turns away (`figure_gone`, off frame) before Kerrid's first cue (tested). W24 is aimed away from it.
  - **Asha only hums** (an `@sfx`, no verse). Pell has no line in Ch8 (tested).
  - **No death by playing badly:** a lost wave is "Fight again" with the meter as the wave began (tested), and a scripted escape is a win.
- **Decisions for review:**
  1. **The set piece uses the sim suites' parties** (Wave 1: Toma, Ysolde, Liss; Wave 2: Toma, Rhen, Liss; Wave 3: Toma, Liss, Ysolde; the Reach: Toma, Asha, Liss), so the bands describe what the player plays. The player can still swap anyone but Toma.
  2. **B17 and B18 run as one sequence** after the Reach. The zone refreshes to the aftermath light between them, then hands off to Ch9 on black.
  3. **The flue trial is trial and error in the greybox:** four rooms in a row, each with its key set in `ch08_field.json`. There's no telltale yet (env-art's kit; M3-C08-102).
  4. **B04's gatekeeper and B02's stair insert are wordless.** The sheet budgets 40 words for B04, which went to the Tender's line.
  5. **Ivo's greeting is on the critical path:** the wall-gate needs `ch08_met_ivo`, and the Ivo trigger spans the top of the mole.
  6. **The word count is about 620, under the sheet's ~1,150.** The barks, the hoist and the cut rope are lean. Narrative may want more town barks.
- **Gaps (filed):**
  - the sailmaker's needle item and the battle barks: M3-C08-100;
  - music and SFX: M3-C08-101, with three music stand-ins today;
  - the kits: M3-C08-102;
  - the stair meter on screen, and timeline chips for the entries: M3-UI-100 (already filed);
  - the body clips the staging calls: appended to `requested_clips.json` (M3-CHR-01).
- **Not filed:** Ch8's four grade ids (`ch08_day`, `ch08_storm`, `ch08_coilspire_int`, `ch08_aftermath`). The scripts don't use `grade=` yet; the zones' `lights` carry the looks.

## Review log
