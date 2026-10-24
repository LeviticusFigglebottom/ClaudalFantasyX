---
id: M3-CHR-1001
title: "Hero clips the Act I dialogue calls (Ch4–Ch9 `@anim asha|toma`) that hero_clips.py lacks"
role: character
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: combat
---
## Goal
`tools/tests/test_hero_clips.py` (the characters track's, on the integration branch since big7) checks that every
`@anim asha <clip>` and `@anim toma <clip>` in `game/data/dialogue/**.dlg` names a clip in
`assets_src/characters/asha/hero_clips.py`. m2-slice's Ch4–Ch9 scripts call 32 that don't exist yet, so
`TestAshaClips.test_scripts_call_only_existing_clips` and `TestTomaClips.test_every_called_clip_exists` fail on any
branch carrying both (found at battle-presentation's big7 merge, 2026-10-24). Nobody skipped or loosened the tests.

## Acceptance criteria
- [ ] Each clip below exists in `hero_clips.CLIPS` (a real pose; a short hold of an existing one is fine where the
      script only needs the beat) and the committed libraries rebuild byte-for-byte.
- [ ] `python3 -m unittest test_hero_clips` (from `tools/tests`) passes.

## Notes
The Ch9 ones overlap M3-C09-08 (that task's art pass may replace them).
- **Asha:** `bow_palms_flat` (ch06_barge), `face_crown_sing` (ch05_kahre), `float_boat` (ch05_lanternfall_boats),
  `hand_jacket` (ch07_after_the_bell), `hold_out_cake`, `look_out_to_sea`, `sit_beside` (ch04_dock_in_the_dark),
  `hold_out_forearm` (ch04_under_way), `kneel_touch_ring` (ch07_empty_moorings), `look_at_fingertip`,
  `touch_shell` (ch04_long_way_round), `lower_staff`, `pole_in`, `pole_out`, `raise_staff`, `stand_gilt`,
  `turn_on_raft` (ch09_the_ebbing), `sit` (ch06_midday), `touch_arm` (ch04_shell_is_set), `touch_forearm`
  (ch05_ferry_comes_in).
- **Toma:** `fold_cloth`, `wipe_face` (ch09_toma), `follow` (ch04_shell_is_set), `hand_on_spear` (ch09_the_ebbing),
  `kneel_palms_flat` (ch06_barge), `laugh` (ch05_kahre), `shield_up` (ch06_barge, ch06_raid), `sit` (ch06_midday),
  `sit_post` (ch04_dock_in_the_dark), `stack_bowls` (ch04_bark_galley_bowls), `stop` (ch06_smoke),
  `unroll_ink_kit` (ch04_under_way).

- **Renumbered (Lead merge, big9, 2026-10-24):** filed as M3-CHR-01. M3-CHR-01 is the characters track's Ysolde build; battle-presentation filed this request under the same id. Now M3-CHR-1001, from the Lead's id block (CONSOLIDATED §4).

## Review log
