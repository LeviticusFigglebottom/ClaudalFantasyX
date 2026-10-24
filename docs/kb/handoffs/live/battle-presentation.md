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

## After MERGE-READY (Lead's queue, 15:22)
- The Lead took d717cb3 into batch big7 (with ui, menus, characters, creatures, combat and the PC's rendering).
- **Mouse parity (Lead item 1): covered by the UI track.** Their M2-UI-26 `BattlePointer` gives battle mouse targeting and Swell play; the command menus took the mouse already. I removed my duplicate picker (M2-BPR-09 closed as superseded, 64a293c) so there's one mouse path.
- **summon_cinematic aligned with UI's M2-UI-23 row** (same id, options, default and text): Short (default) = full the first time, Full = always, Off = no rise. Keep one copy of that row and of the SET_BATTLE_SPEED* rows at merge.
- **Merged claude/m2-slice (MERGE-READY a30b664) into this branch** (66011333) to unblock the Act I arenas and boss intros (append-only conflicts only). Full Godot suite after the merge: **1664 run, 0 failed**.
- **Done this round (all review):**
  - **M2-BPR-10 placeholder hero clips:** a hero actor with a skeleton but no contract clip gets a generated pose clip (bone rotations in choreo.json `placeholder_clips`, MPFB2 DEF-* names); a real clip of the same name always wins, so M2-CHR-07 replaces them with no code change. Also: a hero's own `ko` clip now plays and holds. Not yet seen on a real hero (the actors aren't on this branch): reviewer character.
  - **M3-BPR-01 Act I arenas (greybox):** oruvel_raft_morning, underway_tower, causeway_route_afternoon, derelict_deck_night, ash_terrace_lanternfall, all 19 Act I encounters mapped (ch01_wickfry/oil_slug go to the Underway, per act1_ch01.md). Per-arena staging (underway: shorter, slower). 5 shots viewed and approved. Open: the derelict and Ashcrown fights are morning/day in the beats but graded night (as agreed with env-art); Art may add sub-frames.
  - **M3-BPR-02 boss intros:** Hullgnaw, Bottle Hermit, Spar Wraith, Cinder Matron, the Drownbell: the camera finds the boss, a title card (name, epithet), home; skippable; after the opening banner; once per battle. Shot battle_boss_intro_hullgnaw. Epithets are short and sincere; Narrative may want to own them. No audio sting yet.
  - battle_choreo.gd hit the 1000-line cap; the plan moved to BattleChoreoPlan (930 → 936 now).
- **M3-BPR-01 Act I battle arenas: greybox in progress (agent); env-art took M3-ENV-06** (78916415 on claude/env-art) with the same five ids; three are being built now. Starts when big7 brings m2-slice's Act I encounters.
- Hero battle clips: characters' M2-CHR-07 is in progress (reviewer: combat). I'll review and wire it when it lands.
- Review fixes from the big7 gate: none yet.

## MERGE-READY

**MERGE-READY @ d717cb3** (`claude/battle-presentation`; the integration branch at its 14:3x head merged in at 9fee881, docs-only commits after it): M2-BPR-01 choreography, -02 clip contract (with creature actors), -03 camera director + battle speed / battle animations settings, -04 specials (Swell finishers, Drownbell toll/rim/flood, Vowbound call/rise/dismiss/fall), -05 tide-line stinger + banner timing + victory/escape + lead-in bark hook, -06 freeze-frame shots, -07 per-encounter arenas, -08 C10 first-call cinematic.
- **Checks run (on 9fee881):** full Godot suite **1528 run, 0 failed**; tools/tests **511 OK (3 skipped)**; gdlint, gdformat --check, validate_data, taskboard --check clean; battle_controller.gd 995 lines. Shots captured and viewed: all 17 battle_* plus drownbell_flood (new: 11 battle_choreo_*, battle_arena_tideline, battle_arena_causeway; re-approved after viewing: drownbell_flood (sunset causeway arena + the party's flood brace), battle_choreo_vowbound_rise (help line); every other battle shot unchanged; run-to-run RMSE 0 for all new shots).
- **Skipped (Lead's gate rules):** the full screenshot manifest (only battle shots and drownbell_flood can move: no other scene or shader touched besides the stinger's new shader, which no shot captures), Blender (no Blender sources), coverage (no game/battle core or game/progression change; game/battle/scene is excluded).
- **For the Lead at merge:** (1) shared-file appends: strings.csv, flags.tres (ch03_ilun_first_call_seen), accessibility.json (3 rows), validate_data.py (check_choreo), prewarm_materials.json (the stinger shader, one row); (2) PC's game/vfx/battle files got two one-`if` hooks (BattleVfx, BattleBossVfx land on BattleChoreo.contact); (3) creatures merge: delete BattleActorMotion's action/hit calls; (4) env-art merge: repoint arenas.json and re-approve the three arena-dependent shots; (5) battle_vowbound_call sits at RMSE 0.00798 / 0.008 on lavapipe here, the same on base 499f074.

## Requests filed for other tracks
- Arena kits: env-art's own **M2-ENV-11** (docs/kb/tasks/M2/M2-ENV-11-battle-arenas.md on claude/env-art, in review); my duplicate task file was removed. Final scenes: assets/environments/arenas/{tideline_dawn,causeway_disc_sunset}/<id>.tscn (root: WorldEnvironment, Sun, Sea, dressing, CameraHints, BossAnchor, FloodAnchor; their root script is BattleArenaRoot, no name clash). **After the Lead merges both branches:** repoint the arena paths in game/data/battle/arenas.json (M2: tideline_dawn, causeway_disc_sunset; M3-ENV-06 at 437a9f64: causeway_route_afternoon, derelict_deck_night, ash_terrace_lanternfall; underway_tower and oruvel_raft_morning still being built) to assets/environments/arenas/<id>/<id>.tscn, then view and re-approve every battle_arena_* shot, drownbell_flood and battle_boss_intro_hullgnaw (raft). Env-art notes: the derelict deck's bulwarks are at x ±7.2 (runs stay within ~±4 m: fine); the terrace's plume is above the default frame (a tilted boss shot for the Cinder Matron could show it: a follow-up for the boss_tall shot). Whoever merges second (Lead or this track) does it.
- M2-NAR-01 (narrative): the tideline lead-in bark line.
- At the creatures merge: delete the action/hit calls in BattleActorMotion._on_action_resolved (agreed; whoever merges second).

## Exact next step
Merged-ready (above). Next: review fixes as they come, the creatures/env-art follow-ups after the Lead merges, then M3 battle presentation (hero clips as the characters track lands them; per-encounter arenas for Act I fights).

## Log
- 2026-10-24: merged the stinger agent (04417ea); freeze-frame capture states (b6..); BattleOutro (4e052f8). Specials agent spawned. **Two queue items remain after camera + specials: BPR-06 baselines and the pre-merge full gate.**
- 2026-10-24: branch created and pushed; tasks claimed (b-claim commit). BattleChoreo core pushed (0cfa455). Two worktree agents running (BPR-05 stinger/banner, BPR-03 camera).
