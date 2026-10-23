# Live log: first-playable environment

Seeded by the Lead on 2026-10-23. **This environment owns this file** (CLAUDE.md §7a). Update it on your own branch after every finished item: what's done, what's in progress, the exact next step, and any un-pushed state.

## Current state (2026-10-23, session_01ELR13ohWMPrprcpcgLa7UR)

**The first playable thread works end to end** on `claude/first-playable`, and everything is pushed:
title → New Game → prologue → Cutscene A on Haluna's beach → walk the village (3 villagers) → tideline battle → back to the field → save at the shrine → causeway head → Cutscene B (the first verse) on a placeholder Shell Shrine set → end card → title.

How the human plays it: [docs/PLAYTEST.md](../../../PLAYTEST.md) (Godot 4.6.3, open project.godot, press F5).

### Done (all four tasks are in `review`)
| Task | What | Where |
|---|---|---|
| M2-FP-01 | Cutscene sequencer: `.dlg` cues on a `CutsceneStage`, the camera contract, autosave hold, choices | `game/cutscene/`, `docs/kb/tech/cutscenes.md` |
| M2-FP-02 | Playable Haluna: the mood scene instanced, collision, Rhen, camera volumes, villagers, triggers, Cutscene A stage | `game/levels/ch02/haluna/` |
| M2-FP-03 | Prologue, New Game routing, `BattleRequest`/`FieldBattle`, the `ch02_tideline` encounter, end card | `game/flow/`, `game/levels/prologue/`, `docs/kb/tech/first_playable_flow.md` |
| M2-FP-04 | `HalunaStory` driver, Cutscene B set, whole-thread test, PLAYTEST.md | `game/flow/haluna_story.gd`, `game/levels/ch03/first_verse/`, `tests/integration/test_fp_thread.gd` |

### Verification
- `tools/ci_local.sh` green before the integration merge: 974 tests, `HYMN_SHOTS=boot_title`, Blender skipped (no asset sources touched).
- After merging the integration branch (e9ae43a), I ran scoped checks per §3 "Gate scope": lint, format, data, and the filtered tests `fp_`, `cutscene`, `haluna`.
- A real-runtime smoke run (throwaway script, not committed) went through the actual SceneRouter from New Game to the title with Enter mashed. No script errors.

### In progress
Nothing. The Lead's queue of 2026-10-23 (M2-FP-05..08) is done and pushed:
- **M2-FP-05 polish (review):**
  - Cutscene skip: hold Escape/B for 1 s; it stops at choices.
  - Haluna entry: prebuilt on the router's worker thread, so the swap frame went from a median of 1684 ms to 33 ms.
  - After a defeat: Fight again, or Return to last save (the title when there is no save). An escape returns to `BeforeBattle`, on the near side of the trigger.
- **M2-FP-06 Drownbell (review):**
  - The engine gains a phase mechanism (`game/battle/boss_mechanics.gd`).
  - Phase 1, the Toll: a timeline push, telegraphed in the preview, that breaking the rim silences.
  - Phase 2, the Flood: polyps heal the bell; Asha's Call Ilun clears the water. Call Ilun stands in for the Vowbound summon (ADR 0023).
  - In balance: naive 0%, role_answer 80%, smart 90%.
  - Wired into the thread: Cutscene B → `BattleRequest(drownbell)` with `return_scene` → end card.
- **M2-FP-07:** a request task for Character (Asha's clips), still `todo`.
- **M2-FP-08 (review):** `@face` and line emotions blend Asha's shape keys, with lip-flap; idle, talk, walk and run clips play when they exist.

### Exact next step
Wait for the Lead's review and the human's playtest notes, and turn the notes into M2-FP-09+ tasks. The open follow-up on this branch is the shutdown-only engine errors described below.

### Known issues (candidate follow-ups)
- **New since FP-05:** quitting the game after Haluna has been loaded logs 8 engine errors, `Condition "p_elem->_root != this"` (self_list.h). They come from resources built during the worker-thread prebuild. They appear only at process exit, and scene swaps stay clean. Before the prebuild there were none. The likely culprit is a material or mesh created off the main thread; next, try creating those resources on the main thread in `_ready` while keeping the heavy mesh build threaded.
- `battle_controller.gd` sits at exactly the 1000-line lint cap after FP-06. Split it before growing it.
- The balance sim doesn't model Toma's Lattice skills.
- Placeholders: stand-in music (`game/data/cutscene/sequencer.json` `music_stand_ins`); `@face` is recorded only; `@anim` uses `CutsceneStage.clip_marks`; motes are simple spheres; everyone except Asha is a capsule, and Asha holds her rest pose.
- `tools/validate_data.py` (Systems-owned) got a small `place_at` player-detection fix from FP-03. It's in its own commit with a test, and Systems should confirm it.

### Local-only state
None that matters. `.scratch/` (excluded through `.git/info/exclude`) holds the throwaway smoke and preview scripts; regenerate them if needed.
- The first-verse `.tscn` was emitted by a scratch Python generator. The `.tscn` is the source now, so edit it directly.

### How to resume
1. Check out `claude/first-playable`.
2. Run `python3 tools/dev/fetch_godot.py && python3 tools/dev/fetch_render_deps.py`.
3. Run `godot --headless --path . --import` twice.
4. Run the area tests: `godot --headless --path . res://tests/run_tests.tscn -- --filter=fp_`, then `--filter=cutscene` and `--filter=haluna`.
5. Read the M2-FP task files and `docs/kb/handoffs/2026-10-23-first-playable-1.md`.

## History
- 2026-10-23: merged FP-05 (prebuild, defeat retry) and FP-06 (Drownbell), wired the boss into the thread. ci_local green: 1043 tests, battle shots unchanged.
- 2026-10-23: M2-FP-08 done (face shape keys, lip-flap, clip defaults); 16 cutscene tests.
- 2026-10-23: merged integration 9508ade; claimed M2-FP-05..08; cutscene skip done (13 sequencer tests).
- 2026-10-23: claimed M2-FP-01..04; CutsceneStage contract and sequencer API stub.
- 2026-10-23: pushed the sequencer, the flow (prologue, battle hand-off, end card), the Cutscene B set and a PLAYTEST draft. ci_local green with 967 tests.
- 2026-10-23: merged playable Haluna, wired the whole thread, added test_fp_thread.gd plus the runtime smoke run. ci_local green with 974 tests. Merged the integration branch for the §3 and §7a directives. The old `first-playable-progress.md` is folded into this file.
