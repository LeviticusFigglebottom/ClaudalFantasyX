---
id: M3-CHR-1000
title: Act I body clips the chapter dialogue stages (Rhen, Asha, Toma, Ysolde, Kerrid, Liss)
role: character
status: review
owner_session: "claude/characters"
depends_on: []
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
The Act I chapters (Ch1–Ch9, m2-slice) stage their scenes with `@anim <hero> <clip>`. About 100 of those clips aren't in `hero_clips.CLIPS` yet. The full list, per hero, is `assets_src/characters/requested_clips.json`:

| Hero | Clips |
|---|---|
| Rhen | 46 |
| Asha | 20 |
| Toma | 12 |
| Ysolde | 9 |
| Kerrid | 7 |
| Liss | 6 |

Until a clip exists, its call is skipped at runtime (`CutsceneSequencer` checks `has_animation`), so the scenes play without that gesture. `tools/tests/test_hero_clips.py` allows the listed clips and still fails on any call that is neither built nor listed, such as a typo.

## Acceptance criteria
- [ ] Build the clips in `hero_clips.py`, in each hero's persona. The staging line in each `.dlg` is the brief, and the beat sheets in `docs/kb/story/beats/act1_ch0*.md` give the context.
- [ ] Remove each built clip from `requested_clips.json`. `TestRequestedClips` fails while a built clip is still listed.
- [ ] Priority: the clips in Ch4–Ch6's cutscenes first, because those chapters are playable now. Rhen's clips for the slice's `ch02_girl_on_the_beach` (sit_up, sit_in_shallows, turn_from_sea, stand_unsteady) are on the M2 review path.

## Notes
- Filed by m2-slice on 2026-10-24, when merging big7 brought in the clip-call tests.

- **Renumbered (Lead merge, big9, 2026-10-24):** filed as M3-CHR-01. M3-CHR-01 is the characters track's Ysolde build (named in code and docs); m2-slice filed this request under the same id. Now M3-CHR-1000, from the Lead's id block (CONSOLIDATED §4).

- 2026-10-30 (characters): claimed. The list in `requested_clips.json` now holds the Act II scripts' calls too
  (Ch10-16, merged with big27); the Act I rows were built under M3-CHR-05. Toma's `lift` (ch14_the_vows: off
  Tobin, one-armed; ch15_let_me_carry_him reuses it) is built with the Ch14 Character Art clips (Liss press_wound,
  fight_free; the Stillguard's withdraw_wounded; Merel's pull_pin and pole_push; the Tender's paint_gilt_line).
  Next: the rest of the list, hero by hero. Asha's and Rhen's libraries are near test_hero_clips' 4 MB text bound.

- 2026-10-31 (characters): every queued clip is built and the queue in `requested_clips.json` is empty. The hand
  heights were measured by FK. test_rig_integrity passes (492 tests). One allowance has a written reason: Ysolde's Body
  limit is 47.5 for remove_pin, the Level-pin taken from her hair. The 15 new shots were viewed. Follow-ups are filed
  as M4-A2P-1980: a fist on a free hand, and binary libraries for Asha and Rhen. Ready for review (cinematics).

## Review log
