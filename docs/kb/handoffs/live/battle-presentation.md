# Live log: battle-presentation environment

**Session:** `session_014EcW9e5tEmjDi5S2HmCECd` (cloud) · **Branch:** `claude/battle-presentation` (from `claude/undertow-lead-handoff-423ixt` 499f074) · **Role:** combat · **Lead:** `session_019iimsngAgPLEram1wcbLpE`

The gap (the human's playtest note): battles had no action animation. This track adds a listen-only presentation layer: choreography, a clip contract, a camera director, the specials, the intro and outro. Docs: `docs/kb/tech/battle_presentation.md`.

## Queue (tasks M2-BPR-01..08, role combat; all built, all `review`, reviewer lead)
| Task | State |
|---|---|
| M2-BPR-01 BattleChoreo sequencer | review. Beats from choreo.json; floats/VFX/Read panel land on contact; KO collapse; hand-off waits `BattleStage.hold_after` (controller still 995 lines). |
| M2-BPR-02 clip contract | review. `BattleClips`; creature actors (claude/creatures) strike with their own clip on their contact frame (agreed with creatures). |
| M2-BPR-03 camera director + battle_speed / battle_animations settings | review. |
| M2-BPR-04 specials | review. Swell finishers (dive/verse/brace/glyph), Drownbell toll wave + gather/rim/flood beats (BattleBossVfx lands on contact), Vowbound call/rise/dismiss/fall. |
| M2-BPR-05 stinger, banner timing, victory pose, escape, lead-in bark hook | review. Bark line: Narrative, M2-NAR-01. |
| M2-BPR-06 freeze-frame shots | review. 11 freeze-frames + 2 arenas, all viewed, run-to-run RMSE 0. |
| M2-BPR-07 per-encounter arenas | review. encounters.json `arena`; contract agreed with env-art; greybox tideline_dawn / causeway_disc_sunset; env-art M2-ENV-11 (their task). |
| M2-BPR-08 C10 Ilun first call | review. Full on first live call (flag ch03_ilun_first_call_seen), Short setting, skippable. |

## Pillar-4 fixes found in the freeze-frames
- While an action plays the order has already moved on: the timeline head now reads **"Next"** (not "Acting now") and the help line names the action ("Rhen: Attack") until the sequence ends.
- The Read panel opens on the Read's contact beat, not before the reader moves.

## Requests filed for other tracks
- Arena kits: env-art's own **M2-ENV-11** (docs/kb/tasks/M2/M2-ENV-11-battle-arenas.md on claude/env-art, in review); my duplicate task file was removed. Final scenes: assets/environments/arenas/{tideline_dawn,causeway_disc_sunset}/<id>.tscn (root: WorldEnvironment, Sun, Sea, dressing, CameraHints, BossAnchor, FloodAnchor; their root script is BattleArenaRoot, no name clash). **After the Lead merges both branches:** repoint the two paths in game/data/battle/arenas.json, then view and re-approve battle_arena_tideline, battle_arena_causeway, drownbell_flood. Whoever merges second (Lead or this track) does it.
- M2-NAR-01 (narrative): the tideline lead-in bark line.
- At the creatures merge: delete the action/hit calls in BattleActorMotion._on_action_resolved (agreed; whoever merges second).

## Exact next step
Write the MERGE-READY line when the background full Godot suite + tools/tests on 9fee881 report; then M3 battle work or review fixes.

## Log
- 2026-10-24: merged the stinger agent (04417ea); freeze-frame capture states (b6..); BattleOutro (4e052f8). Specials agent spawned. **Two queue items remain after camera + specials: BPR-06 baselines and the pre-merge full gate.**
- 2026-10-24: branch created and pushed; tasks claimed (b-claim commit). BattleChoreo core pushed (0cfa455). Two worktree agents running (BPR-05 stinger/banner, BPR-03 camera).
