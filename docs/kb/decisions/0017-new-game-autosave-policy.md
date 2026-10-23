# 0017 — New Game asks before a new run can replace the autosave; the chapter autosave waits for a safe point

- **Status:** proposed (Architect, M1-ARC-08; the Lead accepts or overturns it on merge)
- **Date:** 2026-10-23
- **Roles affected:** UI (title screen), Narrative and Cinematics (the cutscene sequencer), QA
- **Author role:** Systems Architect

## Context
QA's review-sweep-C (M1-ARC-03 Review log) found two save-timing problems:
1. **Slot 0 is shared across playthroughs.** New Game starts at chapter 0, so the new run's first `Game.set_chapter` silently writes over the previous run's autosave, and `TitleSaveEntry.continue_slot` then picks the new one. If the player has no manual record, the old run is gone.
2. **The autosave ran synchronously inside `Game.set_chapter`.** The natural callers are a `<<set>>` or event at a cutscene's start or end, so the save would hold half-set flags and the previous zone's `location_id`.

SPEC §5.2 says to save only at shrines plus a chapter-boundary autosave. SPEC §6.6 leaves the slot count open, and pillar 4 (tactical clarity: the player knows what an action costs) applies to menus too.

## Options
1. **One autosave per run.** Give `GameStateData` a run id and keep an autosave slot per run, or rotate the old autosave into an "earlier journey" slot. This needs a save v5 field, a slot-naming scheme, load-menu rows for the extra slots, and a rule for how many old runs to keep.
2. **Ask on New Game when slot 0 holds a run (chosen).** If slot 0 is readable, or is from a newer build, New Game asks first: "A new journey writes over the autosave when its first chapter ends. Records are kept." The choices are **Go back** (first, and the default) and **Begin anew**. An empty or damaged slot 0 has nothing to lose, so New Game starts at once.
3. **Document it as accepted.** Rejected: it loses a run silently.

For the timing problem:
1. `call_deferred` from `set_chapter`. Rejected on its own: a cutscene spans many frames, and the end of the frame is still mid-cutscene.
2. **A request written at the next safe point, with explicit holds (chosen).**

## Decision
- **Option 2: the confirm.** `TitleMenuModel` gains a confirm phase (rows `confirm_back` and `confirm_begin`, help line `TITLE_CONFIRM_NEW_GAME`). `ui_cancel` also goes back. `TitleSaveEntry.new_game_overwrites_autosave()` decides when to ask. A new run never touches manual records. New Game itself writes nothing: the old autosave stays until the new run's first chapter boundary is actually saved.
- **The autosave is deferred.** `Game.set_chapter` → `chapter_changed` → `SaveSystem.request_autosave(reason)`. It is written on a **later frame**, at the first **safe point**:
  - nothing holds the autosave (`SaveSystem.hold_autosave(holder)` / `release_autosave(holder)`; holders are weak, so a freed holder never blocks);
  - `SceneRouter` is not changing scene;
  - the tree is not paused (a menu is open).

  Several requests before the write become one write, made with the state as it is at that point. `Game.new_game()` (through `EventBus.new_game_started`) and `SaveSystem.load_into_game()` drop a pending request.
- **The sequencer rule.** A cutscene **holds the autosave from its first beat to its last** (`hold_autosave(self)` at the start, `release_autosave(self)` at the end). As a backstop, `FieldCameraDirector` holds it while a scripted shot has the camera, from `play_shot` to `release` or leaving the tree.

## Consequences
- The player is never surprised by a lost run. The cost is one extra press for players who really do want a new run.
- If players later want to keep several runs side by side, Option 1 can still be built on top of this, behind a new ADR and a save v5.
- Code that needs an immediate autosave (a debug key, a test) calls `SaveSystem.autosave()` directly. `poll_pending_autosave()` lets tests drive the deferred path without frames.
- Watch: a cutscene that forgets to release its hold blocks every chapter autosave until the holder is freed. The sequencer's review checklist must include "hold and release the autosave".
