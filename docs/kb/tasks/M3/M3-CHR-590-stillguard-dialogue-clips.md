---
id: M3-CHR-590
title: "Stillguard dialogue clips: walk_torch, hold_arm, kneel_palms_flat, let_go (Ch6), shake_head (Ch8)"
role: character
status: review
owner_session: "characters (claude/characters)"
depends_on: [M3-CHR-508]
milestone: M3
request-from: ""
reviewer: cinematics
---
## Goal
The Stillguard models (M3-CHR-508) have idle, walk, stand_watch_seaward, shield_up and level_spear. The Act I dialogue
also calls on them for these, which they don't have yet:
- Ch6 raid: `walk_torch`, `hold_arm` (the girl's arm held over the brazier), `kneel_palms_flat` (the Stilling posture)
  and `let_go`.
- Ch8: `shake_head`.

## Acceptance criteria
- [x] Each clip is built as a story spec (requested_clips.json, the shared ones where they exist) on the Stillguard
      personas, with the spear and shield held or set down sensibly. The rig probe is clean.
- [x] `hold_arm` is staged with the Ch6 wright girl; the contact point is noted for Cinematics.
- [x] Self-rendered and viewed.

## Notes
- 2026-10-29 (characters): **built for all six variants** (the squad shares one clip set; the dialogue calls a, b, c).
  - `walk_torch` (hero_clips `sg_pose_at`, a loop at the walk's length): the walk with the shield arm carried low and
    forward, the arm nearly straight, the left hand closed in a fist (HAND_SHAPE "fist" on the FLAT_HAND solve). The
    torch is the scene's prop on `DEF-hand.L`. A raised, bent torch arm brought the strapped shield's rim into the
    shoulder (prop_in_body 18-36 mm), so the torch is carried, not raised.
  - `hold_arm` (requested_clips.json `heroes.stillguard_<v>`, 1.6 s, holds): a slight lean and a look down, the shield
    hand forward at about a metre and 0.45-0.5 m in front of his root, closing to a fist: **the contact point for
    Cinematics** is the left fist (`DEF-hand.L`) at the clip's last frame; stage the wright girl's forearm there.
    `let_go` (1.2 s) is hold_arm played back, the fist opening early.
  - `kneel_palms_flat` (the shared spec, Ivo's) with the spear set down over the posture change and taken up when he
    rises (PROP_DOWN); `shake_head` (Kerrid's spec, now in `shared`).
  - Rig probe clean for all six with pinned allowances (rig_checks.json `_allowances`: the kneel's knee fold as Ivo's,
    the sleeve in the armpit crease, two edge vertices more of the underarm cut on b and e).
  - Shots (new, no baselines): `stillguard_a_clip_walk_torch`, `stillguard_c_clip_hold_arm`,
    `stillguard_a_clip_kneel_palms_flat`.

## Review log
