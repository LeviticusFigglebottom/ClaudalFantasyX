---
id: M3-C09-02
title: Ch9 "The Ebbing" playable (dialogue, flow, greybox levels, encounters, cutscenes)
role: cinematics
status: review
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
- [x] The chapter plays headless from its entry to its exit in an integration test, like `test_fp_thread`.
- [x] Every line goes through a loc key or a `#line:` tag; flags are declared in `flags.tres`; `validate_data` and `dlgc --check` are clean.
- [x] Each boss and encounter has a `sim.py --check` band, and the combat reviewer has seen it. **N/A: Ch9 has no fight of any kind** (act1_ch09.md rule 5, §5). No encounter, no `battle` step, no suite.
- [x] Each greybox level has a `place_at` root and its spawns, and an entry in `locations.json`.
- [x] PLAYTEST notes for the chapter.

## Notes
- 2026-10-24, m2-slice subagent (C09 build). Ready for review (reviewer: **narrative**, SPEC §12.3). Handoff: `docs/kb/handoffs/2026-10-24-cinematics-18.md`.
- **The zone is a stand-in, `ch09/corrow_night`.** The sheet's `ch08/corrow` night variant can't be used because Ch8 isn't built. It has its own `locations.json` row (spawn `Strand`) and an F5 teleport. When Ch8 lands, it either hosts the zone block as its night variant or hands off here at `Strand` (chapter_flow.md "Ch9").
- **What was built:**
  - eight `.dlg` scripts in `game/data/dialogue/ch09/`;
  - `ch09.json`;
  - `Ch09Zone` (Ch05Zone plus variant `place` and `clip_marks`);
  - `CutsceneHoldGate`, the no-fail held input, with the `hold_input` / `hold_input_end` events;
  - the layout, with shots N01–N19, N05A/B, D01–D03, D02B and P02–P04;
  - `test_ch09_thread.gd` (seven tests);
  - the chapter_flow.md and cutscenes.md sections, and PLAYTEST.
- **The watches, and how each is held:**
  - **Motes:** every `@vfx` is `glimmer_held drift=down_seaward`, with no `motion=` and no release. Tested.
  - **Kerrid's cutaway** is one node with one shot (N13), cut in and cut out. Only `kerrid_stair` acts in it, no `@vfx` is aimed at him, and the motes start seaward of him and drift away. Tested.
  - **"Somebody's still below."** plays on D02 with Asha off frame (a frustum check in the test). Kerrid walks last in D03. Tested.
  - **Pell's first line** is exactly "Beautiful. And pointing the wrong way.", and no earlier chapter gives him a line. Tested.
  - **The act break:** the vigil VO is the sheet's recommended line, with no fire (only the burner).
  - **The side scene** "Shield-Mate", with both choices. Tested.
- **Decisions for review:**
  1. **Pell's mandated words are one line.** The sheet's ≥ 1.5 s gap between "Beautiful." and the rest can't sit inside a line, so it is a translator and VO note on the line. Split it into two lines if Narrative prefers.
  2. **B03–B08 and B09–B11 are one scene each, a node per beat.** Separate `play` steps hand the camera back to the field between scenes, so a cut could not stay a cut.
  3. **The Iskarra vigil is a stand-in plaza in the same zone** (x 300). The prologue scene is hard-wired to its own hand-off, and a scene change fades, so this keeps D03 → P02 a hard cut.
  4. **The act card is a caption on black** until UI's widget (M3-C09-05). The slice's end card then follows, as Act II's stand-in.
  5. **The held input is `field_interact`.** Each movement is gated by events, not by a new ZoneStory step, so `zone_story.gd` is unchanged.
  6. **Toma has one talk prompt**, `ch09_toma.dlg`. It plays the side scene while `ch08_met_ivo` is set and the scene hasn't played, else "Not since the stair."
- **Gaps:**
  - **The sheet's side scene puts the gilt line "fresh" on Asha's face**, but B03 is its first appearance. The scene is staged without it (a note in `ch09_toma.dlg`); Narrative to rule.
  - **No save shrine and no chandler** (B01): see M3-C09-04.
  - **The vigil is lit by the dawn variant:** see M3-C09-10.
  - **Music and SFX:** see M3-C09-06.
- **Ch8 must set three flags Ch9 reads:** `ch08_met_ivo`, `ch08_fed_the_beacon` and `ch08_hoist_cut_down`. Ch9 adds the Corrow speakers `marra`, `hobb`, `fenn` and `stillguard`, which Ch8 reuses. Ch9 doesn't read `ch08_stair_groups_up`, so it isn't declared.
- **Pell** has no battle row, so he joins by flag (`ch09_pell_joined`); see M3-C09-07. He is in no party list and no sim suite.
- **Follow-up requests:**
  - M3-C09-03 rendering: the Ebbing's motes (§9 Rendering, copied);
  - M3-C09-04 environment;
  - M3-C09-05 ui;
  - M3-C09-06 audio;
  - M3-C09-07 combat (Pell);
  - M3-C09-08 character;
  - M3-C09-09 architect (systems);
  - M3-C09-10 rendering (the color script).

## Review log
