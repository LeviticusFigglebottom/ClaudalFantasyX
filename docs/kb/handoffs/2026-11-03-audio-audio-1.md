# Handoff: audio, 2026-11-03 (session 1)

Lead `session_018aiGwGLGkxsnMnu8VfCu1m`; integration branch `claude/undertow-lead-handoff-ze8rrn` (merged @ e2411fb0).
Branch `claude/audio` @ 891ecd0c, everything pushed.

## Done
- **M3-AUD-865, FAST-TRACK (review):** the storm's music.
  - `battle_storm` is a composed battle variant of undertow_rising (assets_src/music/storm_battle.py →
    assets/audio/music/storm_battle.ogg). It replaces act1-chapters' interim row.
  - Battle cues are looked up as: encounter, then `battle.arenas`, then the field zone's `battle` key, then the
    default.
  - The storm zone variants (Oruvel `ch01_gulls_cried`, Corrow and Coilspire `ch08_beacon_opened`) carry
    `undertow_storm` (a new `from_loop` key: the Rising's loop, no intro) and `battle_storm`.
  - New beds `storm_gale` and `storm_wall` (assets_src/sfx/storm_ambience.py) on the storm arenas and fields.
- **M3-AUD-1254 (act1-chapters' request, review):** answered by the above. act1-chapters' M3-C01-1252 is merged
  into claude/audio.
- **M3-AUD-866, FAST-TRACK (review):** status sounds and the revive.
  - assets_src/sfx/status_sfx.py renders 21 per-status apply cues, plus cure, fade and revive.
  - `BattleAudio.play_statuses` plays them from the engine's results.
  - The Relighting Wick rings `revive`.

## In progress
Nothing.

## Exact next step
1. Merge the integration branch again when the Lead announces a merge.
2. Re-run `--filter=storm` and `--filter=status_audio`.
3. Answer any battle-presentation or combat-systems asks: per-status effect ids → the same rows; a status expiry
   signal → `status_fade`/`status_cure`; a cue for the 1 HP victory rise if they want one.
4. Otherwise resume the Act III score (M5-A3P-1951/1952; the Ch17–Ch20 cue list in the live log).

## Known issues
- In a cloud checkout without `git lfs pull`, three Godot audio tests fail on LFS pointers: test_battle_audio's
  `abl_ember`, test_music_transitions' `prologue_dusk.loop.json`, and the second of test_audio_loops' names. The
  storm and status work didn't cause them.
- `godot --import` in such a checkout rewrites about 190 LFS `.import` files. Revert them
  (`git checkout -- assets/lfs assets/audio/music/act2 assets/audio/music/act3 assets/audio/sfx/act3`) before
  committing.
- `coilspire_headland_storm` is a proposed arena id (`battle.pending_arenas`); nobody has built it.

## Files touched
- Assets: assets/audio/music/storm_battle.*, assets/audio/ambience/storm_{gale,wall}.*,
  assets/audio/sfx/battle/status_*.ogg and revive.ogg (with their .import files), assets/PROVENANCE.md.
- Sources: assets_src/music/storm_battle.py, assets_src/sfx/storm_ambience.py, assets_src/sfx/status_sfx.py.
- Game: game/audio/{audio_data,audio_director,battle_audio,music_deck}.gd.
- Data: game/data/audio/{music,ambience,battle_sfx,sfx_status}.json.
- Tools: tools/audio/{data_check,render_all}.py.
- Tests: tests/unit/{test_storm_music,test_status_audio,test_audio_loops}.gd, tools/tests/test_storm_music.py.
- Docs: docs/kb/tech/audio_runtime.md, docs/kb/tasks/M3/M3-AUD-865/866 and M3-AUD-1254,
  docs/kb/handoffs/live/audio.md.
