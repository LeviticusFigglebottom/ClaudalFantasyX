---
id: M3-CIN-01
title: "Sefir in the cutscene sequencer: a per-actor slow blink (10-14 s), his face poses and blend time"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M3-CHR-02]
reviewer: character
milestone: M3
request-from: character
---
## Goal
Sefir's tell is composure that reads as wrongness on a second look (act1_npcs.md §1.6): a fully symmetric face, no
breath, and **a slow blink, one every 10-14 s**. The sequencer's blink (`game/data/cutscene/sequencer.json` `blink`,
M2-FP-18) has one `interval_s` range (2.2-5.0 s) for every actor, so his interval needs a per-actor setting. The
sequencer file is Cinematics'; Character does not edit it (M3-CHR-02).

## Acceptance criteria
- [x] A per-actor blink interval in `sequencer.json` (for example `blink.per_actor.sefir.interval_s: [10.0, 14.0]`),
      read by CutsceneSequencer; every other actor keeps today's range. Keep `on_emotion_change` off for him if it
      would blink him faster than once in 10 s (a changed expression is not a reason for him to blink).
- [x] `face_poses.sefir` -> `res://game/levels/_tests/characters/sefir/sefir_face_poses.json` (15 symmetric rows).
- [x] His expression blend is 0.40 s with no overshoot (the table's `blend_in_s` and empty `overshoot`): honour the
      table's own value if the sequencer has a fixed blend time.
- [ ] His clips (`idle` is deliberately still: no breath, no sway; `talk`, `raise_palm`, `incline_head`, `glance`,
      `pivot`; `walk_glide` for Ch13) play from `assets/characters/sefir/anim/sefir_clips.tres` through the
      `characters` import rule, as the other heroes' do.

## Notes
- Source of the numbers: `assets_src/characters/sefir/sefir_params.json` `_face.blink_interval_s` and
  `_face.blend_in_s`; the clips are documented in `docs/kb/art/characters/sefir_review.md` §5.
- `glance` turns his head 22 degrees to his left and back; the eyes are not keyed by the body clips. If the beat
  needs the other side, mirror the facing with the `@mark` (act1_npcs.md §1.8: "two variants by the @mark").

## Done (slice-polish, 2026-10-27)
- **Per-actor blink:** `blink.per_actor.sefir` = `interval_s` [10, 14] and `on_emotion_change` false.
  `CutsceneFace.configure_blink(cfg, seed, actor_id)` merges the row; every other actor keeps 2.2–5.0 s.
- **`face_poses.sefir`:** `res://game/data/cutscene/sefir_face_poses.json`, a byte copy of Character's review
  table. Shipped data may not point into `game/levels/_tests`, which a release leaves out. A test keeps the copy
  equal: re-copy it when Character changes the source.
- **Blend:** a line's emotion already blends over the table's `blend_in_s` (0.40 s), with no overshoot.
- **Clips: not done here.** They depend on how Sefir is staged. He has no cutscene stage yet in Ch1–Ch3, and his
  `sefir_clips.tres` goes through the characters import rule, which is Character's and hero-integration's. Left
  open: when a scene first stages him, his actor needs the hero-style body hook-up.
- **Tests:** test_cutscene_face_per_actor (2); face 28, cutscene 70, all 0 failed.

## Review log
