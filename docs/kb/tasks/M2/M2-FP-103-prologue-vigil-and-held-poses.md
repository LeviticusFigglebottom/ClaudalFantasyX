---
id: M2-FP-103
title: "FAST-TRACK: the prologue's vigil with the real cast; scripted poses hold through lines; @light"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-FP-102, M2-HER-1104]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
Two findings from viewing the slice with big9's real heroes (tools/cutscene_frames):
1. **The prologue read primitive:** seven capsules on a greybox plaza, one locked shot, nothing moving. The beat
   sheet (act_outline "The Last Time") has the party keeping a vigil apart, Rhen crossing the plaza to sit by Asha,
   and his lantern catching as the line lands (the only flame in the frame), then glimmer rising.
2. **Cutscene A stood its kneelers up:** every line plays the speaker's `talk` clip, so Asha, kneeling over Rhen,
   stood for her first line; and with the hero bodies, Rhen (the player) stood in the shallows where he should lie,
   so H06 framed two pairs of legs.

## Acceptance criteria
- [x] Prologue: Rhen, Asha and Toma on their HeroFieldActor bodies, Ysolde on her model (`vigil_book_shut`);
  Kerrid, Pell and Liss (no models yet) as cloth-coloured silhouettes moved back behind the rise. Rhen walks to
  Asha while P01 drifts into a new two-shot P02; `@light LanternLight on` as the line lands; `@vfx glimmer_lift`.
- [x] `@light <name> on|off [sec]` cue (cues.json, sequencer, docs).
- [x] Held poses: `sequencer.json` `hold_clips`; a held actor's lines don't play talk or idle over the pose, and a
  hero body holds it (`play_clip(..., hold)`), until its next `@anim` or `@mark`.
- [x] Clip stand-ins: `clip_stand_ins` plays a built clip while a requested one is missing (Rhen's beach clips
  kneel him, half risen); new requested clip `rhen/lie_in_shallows` for Character (M3-CHR-1000's list).
- [x] Tests: test_cutscene_pose (5), test_fp_prologue (7).
- [ ] Viewed: the prologue and Cutscene A rendered after the fix (see the live log).

## Notes
- Rhen's sit and trim_wicks clips (already requested) belong in the prologue once built: "he ends sitting beside
  Asha and trims his oil lantern's wick".

## Review log
