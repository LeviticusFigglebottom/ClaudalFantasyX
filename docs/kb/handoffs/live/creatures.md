# Live log: creatures environment

Feature track for the battle creatures (cloud session_01CYks9e592YBEfygyTawcJD), branch `claude/creatures`, started from `origin/claude/undertow-lead-handoff-423ixt` aeb0875. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE.

## Now
- **Review:** M2-CRE-01, the design sheets (`docs/kb/art/creatures/`), at 4b343db.
- **Pushed, in progress:** M2-CRE-02 (pipeline), M2-CRE-03 (battle hook), M2-CRE-04 (the reef crab, first pass) at 5a873a0.
  - The hook rides on the UI track's M2-UI-07: I cherry-picked its three commits (ef3937c, bf37755, 08c872c from `claude/ui`), so the two branches carry identical `fighter_stand_in.gd` hook content. My additions on top are small delegations (`play_action`, `play_hit`, `enter_phase`, `set_part_broken`, KO and Petrify hand-off).
  - `enemies.json` gains `model` on reef_crab only so far. battle_controller.gd is untouched: `BattleStage.spawn` attaches `BattleActorMotion`.
  - **Do not merge yet:** the battle baselines that show the reef crab are not re-approved (M2-CRE-09). The gate's screenshot step fails on them until then.
- **In progress (worktree agents):** M2-CRE-05 lantern eel, M2-CRE-06 gull harrier, M2-CRE-07 spawn-polyp.
- **In progress (me):** M2-CRE-08 the Drownbell; the crab's second pass.
- **Un-pushed state:** none.

## Decisions so far
- **Hook:** the UI track's M2-UI-07 (on `claude/ui`, 08c872c1) already makes `FighterStandIn` instance a spec's `"scene"`. The creatures build on that hook rather than a parallel one: the enemies.json `model` field becomes the stand-in spec's `scene`.
- **Materials:** one creature shader (`game/shaders/creature/creature.gdshader`) reading vertex data (albedo, wetness, cavity, wound mask), not the texture-based character families. Why: pipeline.md §2.
- **Import:** a new `creatures` category. Clip loop modes are set at runtime from `game/data/creatures/creatures.json`, so the shared `AssetImportRules` (which the characters track is also changing) is not touched.
- **Task ids:** M2-CRE-* (free on every branch at the claim).

## Exact next step
Merge the three creature worktrees as they finish, build the Drownbell, polish the crab, then the shots (M2-CRE-09) with every changed battle baseline viewed and re-approved.

## Queue
1. ~~M2-CRE-01 design sheets~~ (review)
2. M2-CRE-02 pipeline, M2-CRE-03 battle integration, M2-CRE-04 reef crab (pushed; crab polish and shots pending)
3. M2-CRE-05..07 lantern eel, gull harrier, spawn-polyp (worktree agents running)
4. M2-CRE-08 the Drownbell (me, now)
5. M2-CRE-09 shots and re-approvals
6. M2-CRE-10 bestiary portrait hook

## Setup notes
- `fetch_blender.py` failed twice on truncated debs from the proxy (`dpkg-deb ... unexpected end of file`). Delete the named `.deb` under `~/.cache/hymn/blender-*/debs/` and rerun; it finished on the third pass.
- `ln -s ~/.cache/hymn/godot-4.6.3+ds-2/godot ~/.local/bin/godot` (and `godot-render`, and `~/.cache/hymn/blender-5.0.1+dfsg-5/blender`).
