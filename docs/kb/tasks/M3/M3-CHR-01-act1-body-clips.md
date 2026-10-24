---
id: M3-CHR-01
title: Act I body clips the chapter dialogue stages (Rhen, Asha, Toma, Ysolde, Kerrid, Liss)
role: characters
status: todo
owner_session: ""
depends_on: []
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

## Review log
