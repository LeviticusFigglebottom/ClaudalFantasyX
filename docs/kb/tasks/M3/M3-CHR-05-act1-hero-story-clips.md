---
id: M3-CHR-05
title: "Hero story clips the Act I chapters past the slice call (Ch4-Ch9: Asha, Toma, Rhen)"
role: character
status: review
owner_session: "characters (new account, branch claude/characters)"
depends_on: []
milestone: M3
request-from: lead
reviewer: cinematics
---
## Goal
m2-slice's Ch4-Ch9 greybox scripts call hero clips that `assets_src/characters/asha/hero_clips.py` does not build
yet, so those `@anim` lines do nothing today. At the big8 Lead merge `tools/tests/test_hero_clips.py` checked every
dialogue file, so it failed; its clip-exists checks are now scoped to the first playable (prologue, Ch1-Ch3), and
this task tracks the rest. Some are also listed in the chapter character tasks (M3-C06-06, M3-C07-07, M3-C09-08).

## Acceptance criteria
- [x] Clips built (or the calls renamed with Cinematics) for:
  - Asha: touch_shell, look_at_fingertip, sit_beside, hold_out_cake, look_out_to_sea, touch_arm, hold_out_forearm
    (ch04); face_crown_sing, touch_forearm, float_boat (ch05); sit, bow_palms_flat (ch06); hand_jacket,
    kneel_touch_ring (ch07); raise_staff, turn_on_raft, lower_staff, pole_out, pole_in, stand_gilt (ch09).
  - Toma: stack_bowls, sit_post, follow, unroll_ink_kit (ch04); laugh (ch05); shield_up, sit, stop,
    kneel_palms_flat (ch06); wipe_face, fold_cloth, hand_on_spear (ch09).
  - Rhen (no clip-exists test yet): his Ch1-Ch7 calls past `CLIPS["rhen"]`, for example sit_steps and offer_item
    (ch03), sit_up and sit_in_shallows (ch02), touch_cord and roof_dive (ch01). Run the test's helper for the list.
- [x] Then widen `SLICE_DIALOGUE` in `tools/tests/test_hero_clips.py` back to every chapter, and add the same check
      for Rhen.

## Notes
- Filed by the Lead's big8 merge agent (2026-10-24). Note that some Rhen calls are in the slice chapters (ch01-ch03)
  and are not checked today: Rhen has never had a clip-exists test.

- **2026-10-27, built (characters).** Every `@anim` call in game/data/dialogue now has a clip: Asha 20, Toma 12,
  Rhen 46, Ysolde 9 and Sefir 1 (`bow_from_barge`, called by ch06_barge.dlg and failing TestSefirClips on the
  integration branch).
  - **Data, not code:** `assets_src/characters/requested_clips.json`. Each clip is a base posture (stand = the idle's
    first frame, sit, kneel, both knees, seated on the ground) or a change between two, plus keyed gestures (reach,
    look, turn, lean, crouch, shrug, raw bone or hips deltas) eased between; or an alias of a clip the hero has
    (`follow`, `walk_past` = walk; `walk_backwards` = walk reversed; `procession_walk` = walk_to_chamber). Shared
    specs cover the clips several heroes call (sit, look_out_to_sea, float_boat, the standing laugh, the palms-flat
    kneel, lift and set down, give and take). act1-chapters can add a clip by adding a spec (a request task).
  - **Joins:** a gesture clip that starts standing starts exactly on the idle's first frame (test_story_clips); the
    gestures mostly settle back, and the posture changes (sit, kneel, ground) hold their last frame.
  - **Size:** the story clips keep only the keys a straight line between neighbours does not give (0.1 deg, 0.5 mm);
    the cap in test_hero_clips rises 2 -> 3 MB (Asha 2.66, Rhen 2.51 MB with 66 new clips between them).
  - **Tests:** SLICE_DIALOGUE now covers every chapter; Rhen and Ysolde have the clip-exists check.
  - **Not seen yet:** these are greybox-grade blocking poses, judged by numbers and the rig probe only (no cloud
    renders since 2026-10-27). Cinematics should flag any that read wrong in the chapters; each is a few lines of
    data to retune.

## Review log
