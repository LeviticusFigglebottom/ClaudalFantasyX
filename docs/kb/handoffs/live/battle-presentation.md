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
  - **M3-BPR-03 Ch6 (review, b1db8fa):** greybox brine_shoals_afternoon (ridges/flats) and salvage_camp_burning (the Inquisitor), Ch6 haze grade, fog-safe lamps; the Inquisitor's intro ("Inquisitor Hadric Moll / A tired officer who still believes the Edict"; Narrative may refine); shots battle_arena_shoals, battle_arena_camp, battle_boss_intro_inquisitor viewed and approved. Toma's first-turn bark still shows after the intro (tested). Known quirk (BattleBossHud, not this track's): one pending prompt slot, so if Toma ever had the first turn his bark would replace TUT_CH06_HOUND.
  - **Follow-ups (17:3x):** BattleBossHud's turn prompt no longer replaces an unshown opening prompt (m2-slice's file, one condition; test_battle_boss_prompts). The Cinder Matron's intro has its own `boss_skyward` shot (she was small behind a party fighter; now clear above the card with the terraces and Ashcrown's cone). Every boss intro has a viewed shot: battle_boss_intro_{hullgnaw,inquisitor,matron,hermit,wraith,drownbell}.
  - **Hero clips (characters' M2-CHR-07):** strikes now land on each clip's `contact` marker (BattleClips.contact_sec); a revive returns a hero to idle. Answered characters.
  - battle_choreo.gd hit the 1000-line cap; the plan moved to BattleChoreoPlan (930 → 936 now).
- **M3-BPR-01 Act I battle arenas: greybox in progress (agent); env-art took M3-ENV-06** (78916415 on claude/env-art) with the same five ids; three are being built now. Starts when big7 brings m2-slice's Act I encounters.
- Hero battle clips: characters' M2-CHR-07 is in progress (reviewer: combat). I'll review and wire it when it lands.
- Review fixes from the big7 gate: none yet.

## MERGE-READY

**MERGE-READY @ HEAD (batch 2 for big8; big7 d6a0886d merged in at 046e8409, latest 9531191c):** M2-BPR-10 placeholder hero clips, M3-BPR-01 Act I arenas + staging, M3-BPR-02 boss intros (all six with viewed shots), M3-BPR-03 Ch6 arenas + the Inquisitor, the BattleBossHud prompt fix, the audio hooks.
- **big7 merge resolutions:** C10 follows `UiSettings.summon_cinematic_cut` (Lead's call); Off's `none` cut still plays `off_entry` (no rise; tested). Seven new arena shot fixtures moved to `game/levels/_tests/battle_arenas/` with their script path. strings/flags/shots/provenance/docs unioned; 19 duplicate loc keys dropped. My handoff renumbered combat-18. **17 m2-slice speakers** (boatman … wright) got placeholder voice rows like the Lead's six (noted on M3-AUD-13) so validate_data stays 0/0.
- **Checks run:** full Godot suite **2032 run, 0 failed**; validate_data 0/0, taskboard --check, gdlint, gdformat clean. tools/tests **704 run, 2 failed (7 skipped)**: both `test_hero_clips` (below). Shots: 9 arenas, 11 choreo, 6 boss intros compared. Re-approved after viewing: battle_arena_{raft,underway,route,derelict,terrace,shoals,camp} and battle_boss_intro_drownbell (only changes: the creatures track's models in place of stand-ins and UI's new panel corners); all others PASS.
- **Known red, not this track's:** `test_hero_clips` (characters' test from big7) fails because m2-slice's Ch4–Ch9 dialogue calls 32 Asha/Toma clips hero_clips.py lacks. Same on any branch with both. Request **M3-CHR-01** lists every clip and its scene. No test was skipped or loosened.
- **env-art's report (19:5x):** (1) `AudioDirector.attach_battle` assigned freed listener keys to an `Object` loop var: now `Variant` like the prune loop above it (audio's file, one token; **audio track please note**). (2) The WorldEnvironment owner warning: `BattleArena.apply` already clears the owner of every moved node (battle_arena.gd:63); not reproduced here on the greybox (single run nor the 10-shot capture). Env-art: send the exact log line and shot if it persists.
- **Skipped:** full screenshot manifest (only battle shots can move), Blender (none touched), coverage (no game/battle core change).

**MERGE-READY @ HEAD (see `git log -1 origin/claude/battle-presentation`; the integration branch merged in at 35d3a35, m2-slice MERGE-READY a30b664 merged in at 6601133):** M2-BPR-10 placeholder hero clips, M3-BPR-01 Act I greybox arenas + staging, M3-BPR-02 Act I boss intros, the audio hooks (battle_stinger / battle_bark / boss_intro), M2-BPR-08's alignment with UI's summon_cinematic row, M2-BPR-09 closed (superseded by UI's BattlePointer).
- **Checks run (on 35d3a35 + the two small fixes after):** full Godot suite **1707 run, 1 failed** (below); tools/tests **561 OK (3 skipped)**; validate_data, taskboard --check, gdlint, gdformat clean; battle_controller.gd 995, battle_choreo.gd 936 lines. Shots: all 30 battle_* plus drownbell_flood captured and compared: all PASS after the drownbell rig fix (new and viewed: battle_arena_raft/underway/route/derelict/terrace, battle_boss_intro_hullgnaw).
- **RESOLVED 16:5x:** m2-slice reverted its 17 resident flags (dc044b48) and I merged it again; `test_scene_router_swap` passes here (16/0, twice). **Full Godot suite on 1311c99: 1739 run, 0 failed.** Since then only 0f-level additions: the hero contact-marker fix (choreo 40/0, placeholder 7/0, specials 13/0) and task files. Background, kept for the record: **`test_scene_router_swap` (boot.tscn and battle_sandbox swap frames 160–190 ms ≥ 40 ms).** It passes on the integration branch alone and on this branch before the 35d3a35 merge; it fails once **m2-slice's M2-ENV-05 `"resident": true` flags in prewarm_materials.json** meet **the integration branch's new boot card / shader_prewarm / scene_router (M2-ARC-05/08)**. Removing the resident flags makes it pass (verified). The Lead will hit the same when merging m2-slice: needs the m2-slice / architect owners (resident warm-up has to stay out of the swap frames). I didn't change either.
- **Skipped (Lead's rules):** full screenshot manifest (only battle shots and drownbell_flood can move), Blender (none touched), coverage (game/battle/scene excluded; no core change).


**MERGE-READY @ d717cb3** (`claude/battle-presentation`; the integration branch at its 14:3x head merged in at 9fee881, docs-only commits after it): M2-BPR-01 choreography, -02 clip contract (with creature actors), -03 camera director + battle speed / battle animations settings, -04 specials (Swell finishers, Drownbell toll/rim/flood, Vowbound call/rise/dismiss/fall), -05 tide-line stinger + banner timing + victory/escape + lead-in bark hook, -06 freeze-frame shots, -07 per-encounter arenas, -08 C10 first-call cinematic.
- **Checks run (on 9fee881):** full Godot suite **1528 run, 0 failed**; tools/tests **511 OK (3 skipped)**; gdlint, gdformat --check, validate_data, taskboard --check clean; battle_controller.gd 995 lines. Shots captured and viewed: all 17 battle_* plus drownbell_flood (new: 11 battle_choreo_*, battle_arena_tideline, battle_arena_causeway; re-approved after viewing: drownbell_flood (sunset causeway arena + the party's flood brace), battle_choreo_vowbound_rise (help line); every other battle shot unchanged; run-to-run RMSE 0 for all new shots).
- **Skipped (Lead's gate rules):** the full screenshot manifest (only battle shots and drownbell_flood can move: no other scene or shader touched besides the stinger's new shader, which no shot captures), Blender (no Blender sources), coverage (no game/battle core or game/progression change; game/battle/scene is excluded).
- **For the Lead at merge:** (1) shared-file appends: strings.csv, flags.tres (ch03_ilun_first_call_seen), accessibility.json (3 rows), validate_data.py (check_choreo), prewarm_materials.json (the stinger shader, one row); (2) PC's game/vfx/battle files got two one-`if` hooks (BattleVfx, BattleBossVfx land on BattleChoreo.contact); (3) creatures merge: delete BattleActorMotion's action/hit calls; (4) env-art merge: repoint arenas.json and re-approve the three arena-dependent shots; (5) battle_vowbound_call sits at RMSE 0.00798 / 0.008 on lavapipe here, the same on base 499f074.

## Notes from env-art (17:10)
- The raft's rope rails are at x ±6.3 and the derelict's bulwarks at ±7.2: runs stay within ~±4 m (fine; underway travel is 0.6x anyway).
- underway_tower's `Underwater` child (ArenaUnderwater over the UnderwaterRig) must come after the moved WorldEnvironment and Sun: BattleArena already moves those first. **Follow-up:** when Rhen's fighter carries a lamp node (hero actor), re-target `Arena/Underwater.lantern_target` to it (today a bare marker at party slot 0's hand). Its look under the battle camera: Rendering's M3-RND-25.
- **Lead rule:** lights near a dense FogVolume set `light_volumetric_fog_energy = 0`. Done for every OmniLight in this track's greybox arenas and the C10 summon light (shots unchanged, RMSE 0). **PC GPU:** BattleBossVfx's glow and net_light OmniLights need the same (your file).

## Requests filed for other tracks
- Arena kits: env-art's own **M2-ENV-11** (docs/kb/tasks/M2/M2-ENV-11-battle-arenas.md on claude/env-art, in review); my duplicate task file was removed. Final scenes: assets/environments/arenas/{tideline_dawn,causeway_disc_sunset}/<id>.tscn (root: WorldEnvironment, Sun, Sea, dressing, CameraHints, BossAnchor, FloodAnchor; their root script is BattleArenaRoot, no name clash). **After the Lead merges both branches:** repoint the arena paths in game/data/battle/arenas.json (M2: tideline_dawn, causeway_disc_sunset; M3-ENV-06, all five at 169445e9: causeway_route_afternoon, derelict_deck_night, ash_terrace_lanternfall, oruvel_raft_morning, underway_tower) to assets/environments/arenas/<id>/<id>.tscn, then view and re-approve every battle_arena_* shot, drownbell_flood and battle_boss_intro_hullgnaw (raft). Env-art notes: the derelict deck's bulwarks are at x ±7.2 (runs stay within ~±4 m: fine); the terrace's plume is above the default frame (a tilted boss shot for the Cinder Matron could show it: a follow-up for the boss_tall shot). Whoever merges second (Lead or this track) does it.
- M2-NAR-01 (narrative): the tideline lead-in bark line.
- At the creatures merge: delete the action/hit calls in BattleActorMotion._on_action_resolved (agreed; whoever merges second).

## Exact next step
MERGE-READY for big8 (above). After big8: take env-art's arenas.json repoint (74c6dc0e on claude/env-art) if the Lead hasn't, re-view arena shots. Then: review fixes; M3-CHR-01 clips when characters land them.

Older: Next: review fixes as they come, the creatures/env-art follow-ups after the Lead merges, then M3 battle presentation (hero clips as the characters track lands them; per-encounter arenas for Act I fights).

## Log
- 2026-10-24: merged the stinger agent (04417ea); freeze-frame capture states (b6..); BattleOutro (4e052f8). Specials agent spawned. **Two queue items remain after camera + specials: BPR-06 baselines and the pre-merge full gate.**
- 2026-10-24: branch created and pushed; tasks claimed (b-claim commit). BattleChoreo core pushed (0cfa455). Two worktree agents running (BPR-05 stinger/banner, BPR-03 camera).
