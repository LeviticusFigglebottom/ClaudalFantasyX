---
id: M3-AUD-865
title: "FAST-TRACK: the storm's battle theme, and storm music in the storm's fields and fights (Ch1 after the Rising, Ch8 after the beacon)"
role: audio
status: review
owner_session: "claude/audio (2026-11-03)"
reviewer: qa
depends_on: [M3-AUD-819, M3-AUD-861]
milestone: M3
request-from: lead
---
## Goal
The human's playtest FAST-TRACK 4 (TRACK-RULES, 11-03): in the seagull/storm sequence the fights and cutscenes play
the normal uplifting music. Provide a storm battle theme (tense, dread, the Undertow's motif, a clean loop, in the
loudness budget) and make sure the storm's cutscenes and fields use the storm and dread cues.

## What was wrong (as played)
1. **The fights.** Ch1's `ch01_scuttlers` (C1-13, right after the Rising) had no `battle.encounters` row, so it
   played `battle_standard_v2`. Any random fight in a storm zone did the same (Ch8's stormgulls on the headland
   after the beacon).
2. **The field between the fights.** The storm zones had no flag variant, so a return from a storm fight brought
   back the *calm* zone's cue: Oruvel's town bed after the scuttlers, Corrow's day bed (`corrow_seawall`) between
   the Ch8 waves. That is the "uplifting music" around the cutscenes: `ch01_net_pen`, `ch01_bridge_gone` and
   `ch01_scuttlers` name no `@music` and simply inherit what plays.

## Done
- **`battle_storm`**, the cue id act1-chapters' M3-C01-1252 chose (`assets_src/music/storm_battle.py` → `assets/audio/music/storm_battle.ogg`, plain git, 0.75 MB):
  a battle variant of our own `undertow_rising` (its brass line, clusters and run imported, nothing re-typed; G
  octatonic, the Undertow's mode), at 96 BPM, twice the Rising's tempo. A 5 s intro (the loop's own rise) and a
  70 s loop of 28 bars. Horns and violas come in at the tritone section (bar 17), and the cluster is bowed in
  tremolo. No fanfare and no major chord. −16.0 LUFS, −1.8 dBTP, all eleven buses on plan, splice residual
  −164 dB, `--determinism` byte-identical.
- **Battle cue lookup** (`AudioData.battle_cue`): the encounter's own row (a boss, the Ch8 waves) → `battle.arenas`
  (the storm arenas) → the field zone's `battle` key (a storm variant's) → `battle.default`. `AudioDirector`
  keeps `field_battle_cue` from the last zone row that has `music`, so the battle scene's own row (no music)
  doesn't lose it.
- **Storm variants** (music.json zones):
  - Oruvel on `ch01_gulls_cried`;
  - Corrow on `ch08_beacon_opened` (with `ch08_wall_fell` → `corrow_aftermath` first);
  - Coilspire on `ch08_beacon_opened`.
  Each storm variant has `music: undertow_storm` and `battle: battle_storm`.
- **`undertow_storm`**: undertow_rising's own stems with `resume` and the new `from_loop` key (MusicDeck starts it
  at its `.loop.json` loop start). After a fight the field returns to the storm's loop, not the Rising's
  town-tune intro.
- **Rows:** `battle.encounters.ch01_scuttlers` → battle_storm (act1-chapters' row). `battle.arenas` maps `seawall_stairhead_storm`,
  `wall_head_storm`, and the proposed (pending) `oruvel_raft_storm` and `coilspire_headland_storm`.
- **Validation** (`tools/audio/data_check.py`):
  - a zone's `battle` must name a cue;
  - `battle.arenas` must use arenas.json ids or `pending_arenas`, and a pending id that exists fails;
  - a `from_loop` cue needs its sidecar.

## For other tracks (the ids they wire)
- **act1-chapters (M3-C01-1252, merged into claude/audio):** their interim `battle_storm` row now plays the
  composed file, and their `oruvel_raft_storm` arena is mapped. `coilspire_headland_storm` remains proposed for
  the Ch8 headland in the storm. A new storm encounter needs no row; to give one its own cue, use
  `battle.encounters.<id>: battle_storm`. Their M3-AUD-1254 ask (the cue and the storm arenas' beds) is done.
- **slice-polish (cutscenes):** the storm's cues are:
  - `undertow_rising`: the Rising, with stem 1 the run;
  - `undertow_storm`: the storm's field loop, no intro;
  - `battle_storm`;
  - `undertow_reach`, `seawall_hold` and `hullgnaw`.
  A new vortex shot under the Rising needs no cue change. A storm script that wants the storm without the Rising's
  intro says `@music undertow_storm`. `tools/tests/test_storm_music.py` lists the storm scripts and fails if one
  names a calm cue.
- **battle-presentation:** nothing to wire. BattleAudio picks the cue itself, by encounter, then arena, then zone.

- **Storm beds:**
  - `storm_gale` and `storm_wall` (`assets_src/sfx/storm_ambience.py`) on the storm arenas;
  - the same beds in the storm variants' `ambience`.

## Tests
- `tools/tests/test_storm_music.py` (10):
  - the rows;
  - every storm fight resolves to a non-default cue;
  - the calm zones keep the default;
  - the storm scripts' `@music`;
  - the sidecar and `.import`;
  - the decoded seam and loudness against targets.py's rule;
  - data_check's new rules, both ways.
- `tests/unit/test_storm_music.gd` (5):
  - the lookup order;
  - the real table's storm fights;
  - the variants;
  - the director across the battle swap (storm field cue from its loop start);
  - `from_loop` and resume.
- `tests/unit/test_audio_loops.gd`: storm_battle.ogg added to LOOPING_CUES.

## Review log
