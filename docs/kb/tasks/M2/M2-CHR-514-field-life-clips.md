---
id: M2-CHR-514
title: "Field life: idle and talk variants, a listening nod and look-at poses, so heroes never stand rigid in cutscenes"
role: character
status: review
reviewer: cinematics
owner_session: "characters (new account, branch claude/characters)"
depends_on: [M2-CHR-12]
milestone: M2
request-from: lead
---
## Goal
The human's playtest: the heroes stand rigid in cutscenes. Hero-integration's HeroIdleMicro (M2-HER-1104) layers
breathing, a weight shift and a head that leads turns at runtime; this task gives the sequencer and that layer
clips to play and blend, for Asha, Rhen, Toma and Ysolde.

## Acceptance criteria
- [x] Idle variants: `idle_look_around` (8 s loop) and `idle_fidget` in each hero's idiom (Asha smooths the verse
      sleeve; Rhen bounces, rolls his neck and checks his tin; Toma rolls his shoulders; Ysolde touches the book).
- [x] Talk gestures: `talk_explain` and `talk_emphatic` (loops; two-handed for Rhen, the free hand for the others),
      and `listen_nod` (a 6 s loop of small nods).
- [x] Look-at key poses: `look_left`, `look_right`, `look_up`, `look_down` (two frames each, head and neck only on the
      idle's first frame), for a runtime blend toward a target.
- [x] Rig probe clean at the existing ratchets; libraries regenerate byte-identical.
- [ ] Hero-integration wires them: idle variants into HeroIdleMicro's rotation, talk and listen into the sequencer's
      dialogue beats, and the look poses into a look-at blend (request: this file's Notes).

## Notes
- Data: the `field` section of `assets_src/characters/requested_clips.json` (M3-CHR-05's gesture engine; loops via
  `"loop": true`). Asha's head turns stay smaller (look poses 18 deg at the neck, look-around with the hips
  carrying part of it): a bigger neck twist opens her halter edge at the shoulder (rig probe).
- **For hero-integration:** the look poses differ from the idle's first frame only in DEF-spine.004-.006 (Asha's in
  .005 and .006), so a look-at can blend them as additive layers against idle frame 0, or set the neck bones from
  them directly. Toma's `look_up` is shallower (12 deg) because his spear shaft sits by his head.
- Not seen rendered yet (renders are on the PC since 2026-10-27).

## Review log
