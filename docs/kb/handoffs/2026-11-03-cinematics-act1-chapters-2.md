# Handoff 2026-11-03 (2): cinematics (act1-chapters), FAST-TRACK follow-ups and the Lead's answers

## Done (all pushed to claude/act1-chapters)
- **Storm wiring** (M3-C01-1252): checked against env-art-b's storm arenas and audio's storm cues. After the big47
  merge, `oruvel_raft_storm` is in `storm.arenas`; `drowned_choir_storm` stays pending (no Choir variant built).
  The storm table is the single source of truth (the Lead's decision). Ch8's storm fights are only the three stair
  holds and the Reach; the headland and flue-moth fights come before the storm.
- **FAST-TRACK, W20's kites** (a0e7ae974): the new flag `ch08_kites_down` is set after `ch08_run_back`, and Corrow's
  states hide Kites and KitesHigh from then on (and from `ch08_reach_survived`). `test_ch08_thread` covers it.
  `ch08_wall_falls_w20` was rendered and viewed.
- **Rows 82 and 86 (act1_gpu_qa.md):** nothing left in my lane; they are queued for the PC re-check.
- **Act II sweep:** the Ch10–16 thread tests are green and the Act II audit has no act1-chapters items. The sim is in
  band except `ch15_wakefin` naive_swell's p90 (91 > 80), which is FYI for combat-systems, who own balance now.
- **LEAD-ANSWERED 1:** `end_card.act2_playable` (false) is the switch to Ossa Fen FenEdge (`EndCard.next_of`,
  `test_end_card_act2`).
- **LEAD-ANSWERED 2:** M4-A2P-071–075 are now act1-chapters'.
- **LEAD-ANSWERED 3:** the Act II break plays at the Prologue's plaza (`ch16_act_break.dlg`, PrologueScene
  `visits`), then hands on to `ch17/hollowmere` Dock. Shot `ch16_act_break_vigil` (pending baseline) was viewed.
  Request M4-UI-1256 asks for the two-line act card.

## In progress
- None. No uncommitted or WIP work.

## Exact next step
1. Merge the integration branch after the Lead's next batch. Re-run `--filter=storm_`, `ch08`, `ch14_16_thread` and
   `fp_prologue`.
2. When env-art-b builds `drowned_choir_storm`: point `scenes.drowned_choir_storm` at its own scene, move it to
   `storm.arenas`, then render and view `ch16_storm_wakes`.
3. When M4-UI-1256 lands: swap `ch16_act_break.dlg`'s `#card` line for `<<event act_card 3>>`.
4. M4-A2P-074's stills: give the act-break vigil a deeper grade with the burner lower (the sheet's B11 note), then
   do the M4-A2P-071–075 stills once the bodies land (M4-CIN-1305).

## Known issues (not from this branch's changes)
- On the integration branch, `test_storm_arenas` fails 2/12 on `oruvel_raft_storm` (env-art's scene against
  env-art-b's test).
- shots.json has a duplicate id, `battle_arena_oruvel_raft_storm`, which fails `test_screenshots`.
- `test_cutscene_sfx_files` has 19 music cues without stand-ins.
- `test_dialogue_box`: `ullari_woman` has a model but no portrait.

## Files touched this session
game/data/battle/{encounters,arenas}.json, game/data/audio/{music,ambience}.json, game/data/flags.tres,
game/data/flow/chapters/{ch08,ch16}.json, game/data/flow/first_playable.json, game/levels/ch08/corrow/corrow_layout.json,
game/data/dialogue/ch16/{ch16_swept_away,ch16_act_break}.dlg (+ compiled, dialogue.csv, translator_notes.tsv),
game/flow/end_card.gd, game/levels/prologue/prologue_scene.gd, tests/unit/{test_storm_encounters,test_end_card_act2,
test_battle_arena}.gd, tests/integration/{test_ch08_thread,test_ch14_16_thread}.gd, tests/screenshots/shots.json,
docs/kb/tasks (M3-C01-1252, M3-ENV-1253, M3-AUD-1254, M3-BPR-1255, M4-UI-1256, M4-A2P-071..075),
docs/kb/handoffs/live/act1-chapters.md.
