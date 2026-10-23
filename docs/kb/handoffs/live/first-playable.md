# Live log: first-playable environment

Seeded by the Lead on 2026-10-23. **This environment owns this file** (CLAUDE.md §7a).

## FINAL HANDOFF (2026-10-23, session_01ELR13ohWMPrprcpcgLa7UR, for the account move)

**Branch `claude/first-playable` is pushed. Nothing is WIP, and there's no un-pushed or local-only state.** The last code commit was gated at 76397e4: `tools/ci_local.sh` with `HYMN_SHOTS=battle_hud_preview,battle_swap_menu,battle_victory,battle_statuses,battle_swell_ring,boot_title` and `HYMN_SKIP_BLENDER=1` gave 1244 tests green, game/battle 99.95% and progression 96.52% (both within the ratchet), shots unchanged, and `tools/balance/sim.py --check` passing every suite at 5000 seeds. Only this file changed after that.

### Already merged into the integration branch (at 2ddca3f)
- M2-FP-01 cutscene sequencer, M2-FP-02 playable Haluna, M2-FP-03 flow (prologue, BattleRequest/FieldBattle, end card) and M2-FP-04 integration with PLAYTEST.md. Sweep K approved all four; they are closed on the integration branch at 7f4c76b.

### On `claude/first-playable` but NOT merged yet: all `review`, merge as one batch
The branch already contains every integration change through origin/claude/new-session-mj8c3c at the M2-CMB-02 merge, so it merges back cleanly as of then.
1. **M2-FP-05 polish** (`docs/kb/tasks/M2/M2-FP-05-playable-polish.md`):
   - Cutscene skip: hold ui_cancel for 1 s; it fast-forwards to the next choice or the end.
   - Haluna prebuild on SceneRouter's worker thread: the swap frame went from 1684 to 33 ms.
   - After a defeat: Fight again, or Return to last save (the title when there is none).
   - An escape returns to `BeforeBattle`.
2. **M2-FP-06 the Drownbell** (`M2-FP-06-drownbell-boss.md`):
   - `game/battle/boss_mechanics.gd`; data in `encounters.json`, `enemies.json` and `skills.json`.
   - ADR **0024** is the Ilun stand-in.
   - Wired as Cutscene B → `BattleRequest(drownbell, return_scene=end card)` → end card.
   - Battle docs: battle_ctb.md, "The Drownbell", which includes the **VFX hook points** table for M2-RND-04.
   - Balance: Floodtide power 14. At 5000 seeds: naive 0%, role_answer 77.7%, smart 85.5%.
3. **M2-FP-08:** `@face` and line emotions drive Asha's shape keys (`CutsceneFace`), with viseme lip-flap; idle, talk, walk and run clips play when they exist.
4. **M2-FP-09 thread hardening** (renumbered from a duplicate M2-FP-05; `M2-FP-09-thread-hardening.md`):
   - `FlowRouting` keeps hand-offs from being lost while the router is busy.
   - The whole-thread test drives the real trigger, with defeat, save and load legs, plus a strip test.
   - The intro flag comes from JSON, and the zone suns use the close-up shadow bias.
   - A sequencer that leaves the tree releases `play()`.
5. **M1-ARC-15:** `game/core/graphics_runtime.gd` applies GraphicsSettings at boot and on each zone load through `SceneRouter.attach_graphics_hook` (a minimal, additive change to a Systems-owned file). M1-UI-10 (the graphics menu) is filed for UI. The RND-12 S2 finding is in graphics_settings.md.
6. Smaller items:
   - The `BattleIds` helper keeps `battle_controller.gd` under the cap.
   - `"opening": "normal"` on both story fights.
   - Handoffs renumbered on merges: combat-8 is the Drownbell, architect-17 is ARC-15.

### WIP
None.

### Remaining queue, in order
1. **Merge** `claude/first-playable` into the integration branch. On conflicts:
   - `strings.csv`: `python3 tools/dev/merge_union.py`.
   - `dialogue.csv`: rerun `python3 tools/dlgc.py`.
   - `balance_report.md`: take theirs and rerun `sim.py`.
   - Rerun `sim.py --check` after any merge that touches skills or Swell.
2. **Dialogue key light**, filed by the Lead as `docs/kb/tasks/M2/M2-FP-06-dialogue-key-light.md` on the integration branch. **That id clashes with M2-FP-06 (the Drownbell), so renumber it M2-FP-10 when claiming.**
   - The problem: the 400 m sun cascades can't resolve face self-shadows at dialogue range.
   - The fix: a character key light with a short shadow range, `shadow_normal_bias` 4.5, aligned to the zone sun. Add it to the cutscene sequencer or shot data, e.g. a `CameraShot`/`CutsceneShotNode` field or a per-stage `KeyLight` that the sequencer enables on close-ups.
   - When it's done, ask the PC GPU session (session_01778wbLbDFnRRLTKjnawv3T, or its successor) for a GPU check of Cutscene A.
3. **M2-FP-07:** Character's clip request (idle, walk, run, talk, the beach rise, take_hand and the others listed). The sequencer already plays same-named clips, so there's no code to do here; just follow up.
4. **Keep docs/PLAYTEST.md current** after each item.
5. **Known issue:** 8 `p_elem->_root != this` engine errors at exit after `haluna.tscn` has been loaded. They are present on the base too (ARC-15's finding), are exit-only, and don't affect play. Bisect the mood scene vs our zone.

### Coordination notes
- **Save v6 belongs to the integration branch (M2-ARC-01).** This branch never bumps SAVE_VERSION and needs no new save fields.
- **`battle_engine.gd` is at exactly 1000 lines and `battle_controller.gd` at about 990, the lint cap.** Put new logic in helper classes (BossMechanics, BattleBossHud, BattleBestiary, BattleIds). Combat should split the engine before it grows.
- **The PC GPU session builds the Drownbell VFX and flood rig as M2-RND-04.** Hooks: battle_ctb.md, "VFX hook points". It should be a listen-only view attached next to `BattleBossHud.attached`, and the flood height goes through `hymn_water_level` with one publisher.
- **ADR numbers:** 0023 is save v5 (CMB-03) and 0024 is the Drownbell stand-in.
- Cross-session messages from this session to the Lead were refused (the session needs a trusted device). This file is the report.

### Exact next step
For a new session: check out `claude/first-playable` and run `python3 tools/dev/fetch_godot.py && python3 tools/dev/fetch_render_deps.py`, then `godot --headless --path . --import` twice. Merge it into the integration branch (step 1 of the queue), then claim the dialogue key light as M2-FP-10.

### How to resume (tests for this area)
`godot --headless --path . res://tests/run_tests.tscn -- --filter=<x>` for x in `fp_`, `test_cutscene`, `haluna`, `flow_routing`, `graphics`, `boss`, `drownbell`. The coverage step applies because this branch touches game/battle.

## History
- 2026-10-23: ci_local green after the CMB-02 merge: 1244 tests; game/battle 99.95%, progression 96.52%; battle and title shots unchanged. The Drownbell is mergeable now.
- 2026-10-23: merged integration (M2-CMB-02 Shallows Verse, M2-NIT-03, the M2 UI). I kept the `_show_pick` target-kind line in battle_controller.gd as merged (no conflict there).
  - My Drownbell handoff is now **combat-8**, because theirs took 6 and 7.
  - In the validator, the AI vocabulary (field_active, largest_ally) and SKILL_ONLY_TARGETS are both kept.
  - Drownbell rebalance: with the Verse covering only two allies, smart fell to 77.3%, so Floodtide went from 15 to 14.
  - `sim.py --check` at 5000 seeds passes every suite. Drownbell: naive 0%, role_answer 77.7%, smart 85.5%.
- 2026-10-23: merged integration (SPEC v1.2, M2-CMB-01 Swell inputs, M2-ARC-01 save v6).
  - Handoff renumbering: theirs took combat-5 and architect-16, so mine are now **combat-8** (Drownbell) and **architect-17** (ARC-15).
  - Drownbell rebalance after Swell: with Swell, smart reached 95.5%, so Floodtide went from power 13 to 15 (since superseded: it is now 14, see above).
  - Added the VFX hook docs for M2-RND-04.
- 2026-10-23: merged integration (the coverage ratchet 4c462ee, M1-NIT-02 enemy_id, ADR 0023 Amendment 1); clean merge. ci_local green: 1125 tests; game/battle 99.94% (baseline 99.93%), progression 96.52%.
- 2026-10-23: merged integration c21dce5 (M1-CMB-03: save v5, Read, openings).
  - The Drownbell's ADR is now **0024**, because CMB-03 took 0023. My combat handoff is now combat-8.
  - ch02_tideline and drownbell have `"opening": "normal"`.
  - The two id helpers moved out of BattleController into `BattleIds`, keeping it at 989 lines (under the cap).
  - ci_local green: 1094 tests, battle coverage 99.94%, battle and title shots unchanged.
- 2026-10-23: merged M1-ARC-15 (GraphicsRuntime). Area tests green: graphics, fp_, haluna, scene_router.
- 2026-10-23: M2-FP-09 done. Merged integration 7f4c76b+ (sweep K). M1-ARC-15 with an agent.
- 2026-10-23: merged FP-05 (prebuild, defeat retry) and FP-06 (Drownbell), wired the boss into the thread. ci_local green: 1043 tests, battle shots unchanged.
- 2026-10-23: M2-FP-08 done (face shape keys, lip-flap, clip defaults); 16 cutscene tests.
- 2026-10-23: merged integration 9508ade; claimed M2-FP-05..08; cutscene skip done (13 sequencer tests).
- 2026-10-23: claimed M2-FP-01..04; CutsceneStage contract and sequencer API stub.
- 2026-10-23: pushed the sequencer, the flow (prologue, battle hand-off, end card), the Cutscene B set and a PLAYTEST draft. ci_local green with 967 tests.
- 2026-10-23: merged playable Haluna, wired the whole thread, added test_fp_thread.gd plus the runtime smoke run. ci_local green with 974 tests. Merged the integration branch for the §3 and §7a directives. The old `first-playable-progress.md` is folded into this file.
