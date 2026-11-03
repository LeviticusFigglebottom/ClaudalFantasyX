# Handoff 2026-11-03: cinematics (act1-chapters), FAST-TRACK storm fights

## Done
- M3-C01-1252 (review, reviewer qa): every fight fought while the Undertow is up is flagged `storm: true`. That is
  Ch1's Scuttlers and Hullgnaw, Ch8's three stair holds and the Reach, and Ch16's storm waking. Each is on a storm
  arena (arenas.json `storm`) with a storm cue (music.json battle `storm_cues`), and test_storm_encounters locks it.
  Ch8's headland fights are pre-storm (B04), so they are not flagged.
- Requests filed: M3-ENV-1253 (env-art-b), M3-AUD-1254 (audio), M3-BPR-1255 (battle-presentation).

## In progress
- None. `oruvel_raft_storm` and `drowned_choir_storm` play on their base arenas until M3-ENV-1253 lands.

## Exact next step
When M3-ENV-1253 lands: in arenas.json, point `scenes.oruvel_raft_storm` and `scenes.drowned_choir_storm` at
`assets/environments/arenas/<id>/<id>.tscn` and move both ids from `storm.pending` to `storm.arenas`. Run
`--filter=storm_encounters` (it fails until you do), then render and view the three fights.

## Known issues
- `tools.tests.test_b_arenas` fails on `ashcrown_anvil_court` reproducibility on the integration branch, with or
  without this change (env-art-b's generated scene).
- Ch8's wave stills show clouds and rain but not the storm wall in frame (noted on M3-ENV-1253 and M3-BPR-1255).

## Files touched
game/data/battle/encounters.json, game/data/battle/arenas.json, game/data/audio/music.json,
game/data/audio/ambience.json, tests/unit/test_storm_encounters.gd, tests/unit/test_battle_arena.gd,
docs/kb/tasks/M3/M3-{C01-1252,ENV-1253,AUD-1254,BPR-1255}-*.md, docs/kb/handoffs/live/act1-chapters.md.
