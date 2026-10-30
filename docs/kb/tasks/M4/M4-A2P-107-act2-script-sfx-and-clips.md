---
id: M4-A2P-107
title: "The Act II scripts' pending cues: 11 cutscene SFX, two music cues, and the hero clips they call"
role: audio
status: todo
owner_session: ""
depends_on: [M4-A2P-001, M4-A2P-007]
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
The Act II scripts (M4-A2P-001..009) name cues and clips that nobody has made yet. To fix big20's tools-suite red (the Lead's FAST-TRACK, 2026-10-30), they now sit on the tests' pending lists. Each list may only shrink, and each item plays silent or still until it lands.

- **Audio, `@sfx`** (`tools/tests/test_cutscene_sfx_files.py` `SFX_TODO`, files under `assets/audio/sfx/`):
  - `egret_lift` (Ch10, the dead channel)
  - `lamp_seat` (Ch11, the lamp bench)
  - `engine_tick` (Ch11, the engine)
  - `stirring_bells` (Ch14, the first ripple and left standing)
  - `water_gate_drop` (Ch14)
  - `level_pin_ring` (Ch14, the vows)
  - `lamp_housing_close` and `lamp_crack` (Ch15, the pyre-raft)
  - `fin_cut` (Ch15, the fin; battle_sfx.json maps it to `hit_none`, but the cutscene needs a file)
  - `kerrid_sits` (Ch15, the shoal)
  - `kesh_rise` (Ch16, the choir)
- **Audio, `@music`** (`MUSIC_TODO`; `abiding_guard` landed in big21 and now plays through a stand-in row):
  - `abiding_guard` (M4-A2P-092)
  - `kesh_memory` (act2_cue_sheet.md proposes `drowned_choir`; if that's the answer, add a `music_stand_ins` row and take it off the list)
- **Characters, `@anim`** (`assets_src/characters/requested_clips.json` `clips`, the M3-CHR-1000 pending list): 73 clips across Asha, Rhen, Toma, Ysolde, Sefir, Liss, Kerrid and Pell. The file lists each one. Build them through hero_clips.py's story specs, then drop each built clip from the list (`TestRequestedClips` enforces that).

## What the story track already resolved, with sounds that exist
- `pole_stroke`, `pole_no_wake` and `barge_no_wake` became `barge_pole`.
- `pyre_crackle` became `hearth_crackle`.
- `storm_wall` became `undertow_wall_roar`.
- `current_song_hum` became `current_song`.
- `sequencer.json` `music_stand_ins` now names the delivered Act II files for 15 cues. Most of those files live under `assets/audio/act2/music/`, outside `music_dir`, so their rows are written `../act2/music/<id>`. If audio would rather move the files, the rows go away.

## Acceptance criteria
- [ ] Each SFX file is rendered from source with a PROVENANCE row, and its id is off `SFX_TODO`.
- [ ] Each music cue has a row in music.json and resolves in the sequencer, and its id is off `MUSIC_TODO`.
- [ ] Each clip is built, and its id is off `requested_clips.json` `clips` (characters).

## Review log
