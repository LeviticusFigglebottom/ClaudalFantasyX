---
id: M3-AUD-1254
title: "FAST-TRACK request: the storm battle cue (battle_storm) and storm battle beds"
role: audio
status: review
owner_session: "claude/audio (2026-11-03)"
depends_on: []
milestone: M3
reviewer: narrative
request-from: cinematics
---
## Goal
The human's playtest (11-03): the storm's fights play the uplifting standard battle theme. act1-chapters wired every
storm fight to a storm cue (M3-C01-1252; music.json battle `storm_cues`). Ch1's Scuttlers play `battle_storm`, an
INTERIM row that reuses `undertow_rising` with its run pulse.

## Acceptance criteria
- [x] A composed `battle_storm` cue (original; dread and effort, never heroic: act1_ch01.md's "a pulse added, never
      a heroic one"), replacing the interim row's files in music.json. Any later storm regular names it.
- [x] Storm battle beds (wind, rain, the wall's roar) in ambience.json `arenas` for `oruvel_raft_storm` and the
      seawall storm arenas (`seawall_stairhead_storm`, `_hoist`, `_surge`), so the battle doesn't carry the field's
      day beds.
- [x] Optional: confirm `hullgnaw` reads as storm music (it is in `storm_cues`).

## Done (audio, with M3-AUD-865)
- **`battle_storm`** now plays the composed cue (assets/audio/music/storm_battle.ogg, from
  assets_src/music/storm_battle.py; plain git). It is a battle variant of undertow_rising: the Rising's brass line,
  clusters and minor-second run, in the Undertow's G octatonic, at 96 BPM (twice the Rising's tempo). A 5 s intro
  (the rise), then a 70 s loop, at −16 LUFS. Dread and effort, with no fanfare and no major chord. The interim stems
  row is gone. audio's own id for it, `storm_battle`, was retired so there is one id.
- **Storm beds** (assets_src/sfx/storm_ambience.py, assets/audio/ambience/; plain git; −26 LUFS):
  - `storm_gale` (the gale, driven rain, the swell on hulls, the roar) on `oruvel_raft_storm`;
  - `storm_wall` (the same, with the sea booming on the stone and the spray) on `seawall_stairhead_storm`,
    `_hoist`, `_surge` and `wall_head_storm`.
  - The storm zone variants carry the same beds into the field.
- **hullgnaw** reads as storm music: G minor, a 6/8 heave, the eel's crawling chromatic bass, and the raft breaking
  in bars 33–40. It is a boss theme built for the breaking raft, so it stays in `storm_cues`.
- **Beyond the ask (M3-AUD-865):**
  - fights with no row of their own, started in a storm zone (the Ch8 headland's stormgulls after the beacon),
    play `battle_storm` through the zone variant's `battle` key, after `battle.arenas`;
  - between the fights, the field plays `undertow_storm` (the Rising's loop without its town-tune intro) instead of
    the town's day bed.
  - tools/tests/test_storm_music.py also checks that every `storm: true` encounter resolves into `storm_cues`.

## Review log
