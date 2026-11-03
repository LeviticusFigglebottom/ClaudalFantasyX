---
id: M3-C01-1252
title: "FAST-TRACK (human playtest 11-03): the storm's fights on storm arenas with storm music"
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: []
milestone: M3
reviewer: qa
request-from: lead
---
## Goal
The human's playtest: the seagull/storm scene's fights used the normal backdrop and the uplifting music. Find every
fight that happens while the Undertow is up, point it at a storm arena (storm sky, rain, the vortex visible) and at
storm battle music, and lock it with a test.

## Acceptance criteria
- [x] The storm fights found and flagged `storm: true` in encounters.json: Ch1 `ch01_scuttlers` (C1-13) and
      `ch01_hullgnaw` (C1-14), both on the sunny `oruvel_raft_morning`; Ch8 `ch08_stair_hold_1/2/3` and
      `undertows_reach` (already on the seawall storm arenas, which carry the Undertow node, and already on storm
      cues); Ch16 `ch16_storm_wakes` (B09, on the moonlit `drowned_choir_ring` with `battle.default`).
- [x] Not storm fights: `ch08_headland_gulls`/`_crabs` (B04, 13:00: the table stops at `ch08_entered_coilspire`,
      before B07's storm; B08's run back is a cutscene to the wall-gate) and Ch1's Underway fights (before the gulls).
- [x] arenas.json `storm`: `arenas` (scenes with the vortex) and `pending` (`oruvel_raft_storm`,
      `drowned_choir_storm`: their `scenes` rows point at the base arena until env-art-b's M3-ENV-1253 lands).
- [x] music.json battle `storm_cues` and `battle_storm` (interim: `undertow_rising` with the run pulse, the C1-13
      run's own cue, until audio's M3-AUD-1254) for `ch01_scuttlers`; `abiding_guard_storm` (stem 2, the storm, in
      from the start) for `ch16_storm_wakes`. ambience.json: `ch16_storm_wakes` plays the Choir's storm beds (the
      row was keyed to the planned id `ch16_holding_the_line`).
- [x] `tests/unit/test_storm_encounters.gd`: every storm fight flagged, on a storm arena, playing a storm cue (never
      the default); every storm arena shows the Undertow; a pending arena has its request and fails once its own
      scene lands (so the swap can't be forgotten).
- [ ] When M3-ENV-1253 lands: repoint the two `scenes` rows, move the ids to `storm.arenas`, render and view the
      two fights. When M3-AUD-1254 lands: nothing (audio replaces `battle_storm`'s files).

## Notes
- Requests: M3-ENV-1253 (env-art-b, the two storm arenas), M3-AUD-1254 (audio, the composed storm battle cue and
  storm battle beds for the raft and the wall-head), M3-BPR-1255 (battle-presentation, rain and sky in battle).
- Combat-systems is tuning Hullgnaw (the solo boss): this change touches only `ch01_hullgnaw`'s `arena` and `storm`.

## Review log
