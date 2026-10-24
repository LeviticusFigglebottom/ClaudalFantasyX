# Live log: creatures environment

Feature track for the battle creatures (cloud session_01CYks9e592YBEfygyTawcJD), branch `claude/creatures`, started from `origin/claude/undertow-lead-handoff-423ixt` aeb0875. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE.

## Now
- **Claimed:** M2-CRE-01..10 (task files on this branch; ownership row for `assets_src/creatures/**`, `assets/creatures/**`, `game/creatures/**`, `game/shaders/creature/**`, `docs/kb/art/creatures/**`).
- **In progress:** M2-CRE-01, the design sheets.
- **Un-pushed state:** none.

## Decisions so far
- **Hook:** the UI track's M2-UI-07 (on `claude/ui`, 08c872c1) already makes `FighterStandIn` instance a spec's `"scene"`. The creatures build on that hook rather than a parallel one: the enemies.json `model` field becomes the stand-in spec's `scene`. I take 08c872c1's `fighter_stand_in.gd` content verbatim so the two branches merge clean.
- **Task ids:** M2-CRE-* (free on every branch at the claim).

## Exact next step
Write the five design sheets (M2-CRE-01), then the pipeline on the reef crab as the pilot.

## Queue
1. M2-CRE-01 design sheets
2. M2-CRE-02 pipeline, M2-CRE-03 battle integration (pilot: reef crab, M2-CRE-04)
3. M2-CRE-05..07 lantern eel, gull harrier, spawn-polyp (parallel worktree agents)
4. M2-CRE-08 the Drownbell
5. M2-CRE-09 shots and re-approvals
6. M2-CRE-10 bestiary portrait hook

## Setup notes
- `fetch_blender.py` failed twice on truncated debs from the proxy (`dpkg-deb ... unexpected end of file`). Delete the named `.deb` under `~/.cache/hymn/blender-*/debs/` and rerun; it finished on the third pass.
- `ln -s ~/.cache/hymn/godot-4.6.3+ds-2/godot ~/.local/bin/godot` (and `godot-render`, and `~/.cache/hymn/blender-5.0.1+dfsg-5/blender`).
