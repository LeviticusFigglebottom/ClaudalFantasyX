# Live log: creatures environment

Feature track for the battle creatures (cloud session_01CYks9e592YBEfygyTawcJD), branch `claude/creatures`, started from `origin/claude/undertow-lead-handoff-423ixt` aeb0875. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE.

## Now
- **Review:** M2-CRE-01 (design sheets); M2-CRE-05 lantern eel and M2-CRE-07 spawn-polyp (worktree agents, merged); M3-CRE-02 (the Ch1 models: Hullgnaw, wickfry, tower limpet, oil slug; first passes, waiting on m2-slice's enemy rows for the `model` line).
- **Pushed, in progress:** M2-CRE-02 pipeline, M2-CRE-03 battle hook, M2-CRE-04 reef crab, M2-CRE-08 Drownbell, M2-CRE-09 shots (baselines pending), M2-CRE-10 `CreaturePortrait` (request **M2-UI-16** filed).
  - The hook rides on the UI track's M2-UI-07: I cherry-picked its three commits (ef3937c, bf37755, 08c872c from `claude/ui`), so the two branches carry identical `fighter_stand_in.gd` hook content. My additions on top are small delegations and `BattleStage.settle_actors()`.
  - `enemies.json` now has `model` on reef_crab, lantern_eel, drownbell and spawn_polyp. battle_controller.gd is untouched.
  - **For the PC GPU session:** `game/levels/_tests/drownbell/drownbell_flood_shot.gd` (your file) gained one line after `boss.settle()`: `ctl.stage.settle_actors()`. It jumps the bell model's 2.4 s flood sink to its end, as your settle does for the water.
  - **Do not merge yet:** the 11 battle baselines that show the creatures (battle_* fixtures and drownbell_flood) are not re-approved, and the creature shots have no baselines. That waits on the gull harrier (the last worktree agent) so every battle shot is re-approved once.
- **In progress:** M2-CRE-06 gull harrier (worktree agent).
- **Coverage** (full suite under instrumentation, 1467 tests): battle 99.95%, progression 96.52%, within the baseline.
- **Act I (M3, the Lead's queue tail):** M3-CRE-01 roster proposal and 15 design sheets (`docs/kb/art/creatures/act1_roster.md`, `act1/`), sent to m2-slice for their encounters (send_message 12:20). M3-CRE-02 Ch1 models pushed.
- **Two queue items remain** for the slice: the shots and re-approvals (M2-CRE-09), and the polish passes. Then Act I continues with Ch4 (Spar-Wraith, bottle hermit, sail leech).
- **Un-pushed state:** none.
- **Integration merge:** merged `origin/claude/undertow-lead-handoff-423ixt` at d62f524 (clean).

## Decisions so far
- **Hook:** the UI track's M2-UI-07 (on `claude/ui`, 08c872c1) already makes `FighterStandIn` instance a spec's `"scene"`. The creatures build on that hook rather than a parallel one: the enemies.json `model` field becomes the stand-in spec's `scene`.
- **Materials:** one creature shader (`game/shaders/creature/creature.gdshader`) reading vertex data (albedo, wetness, cavity, wound mask), not the texture-based character families. Why: pipeline.md §2.
- **Import:** a new `creatures` category. Clip loop modes are set at runtime from `game/data/creatures/creatures.json`, so the shared `AssetImportRules` (which the characters track is also changing) is not touched.
- **Task ids:** M2-CRE-* (free on every branch at the claim).

## Exact next step
Merge the three creature worktrees as they finish (they append to creatures.json, enemies.json, the import rule, blender_builds.json and PROVENANCE.md: union the rows). Then capture every battle shot and the creature shots, view each, approve the creature baselines, and re-approve the battle shots whose change is the models (list each RMSE in M2-CRE-09).

## Queue
1. ~~M2-CRE-01 design sheets~~ (review)
2. M2-CRE-02 pipeline, M2-CRE-03 battle integration, M2-CRE-04 reef crab (pushed; crab polish and shots pending)
3. M2-CRE-05..07 lantern eel, gull harrier, spawn-polyp (worktree agents running)
4. ~~M2-CRE-08 the Drownbell~~ (first pass pushed)
5. M2-CRE-09 shots and re-approvals
6. ~~M2-CRE-10 bestiary portrait hook~~ (CreaturePortrait pushed; M2-UI-16 filed)
7. **Queue tail (Lead, 2026-10-24 12:00, M3 in parallel):** the Act I bestiary (act_outline.md Ch1 and Ch4–9: the Ch1 dive's sea-floor creatures, the Terraces of Ash and Brine Shoals foes, the Seawall). Design sheets first; rosters coordinated with m2-slice, which designs the Act I encounters.

## Setup notes
- `fetch_blender.py` failed twice on truncated debs from the proxy (`dpkg-deb ... unexpected end of file`). Delete the named `.deb` under `~/.cache/hymn/blender-*/debs/` and rerun; it finished on the third pass.
- `ln -s ~/.cache/hymn/godot-4.6.3+ds-2/godot ~/.local/bin/godot` (and `godot-render`, and `~/.cache/hymn/blender-5.0.1+dfsg-5/blender`).
