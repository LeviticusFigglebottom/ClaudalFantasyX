# 0018 — New Game asks before a new run can replace the autosave; the chapter autosave waits for a safe point

- **Status:** accepted (Lead sign-off 2026-10-23; renumbered from 0017 on merge)
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

## Amendment 1 — 2026-10-23: an older record never overwrites a further-along autosave (M1-ARC-08 review-sweep-E S4)
- **Context.** QA's review-sweep-E found the New Game loss in another form: load an *older* manual record, cross its next chapter boundary, and the chapter autosave silently replaces a slot 0 that had got further. If the player had no manual record of the further point, that run was gone.
- **Options.** (1) Ask on load when slot 0 is further along than the record. This needs a new prompt in the load menu, and the question comes before the player knows whether they will cross a boundary. (2) **Keep the further-along autosave (chosen).** In the spirit of this ADR: no silent loss, and no extra question on the common path.
- **Decision.** When the deferred chapter autosave comes due, `SaveSystem.autosave_is_further_along(Game.state)` compares the live state with slot 0. Slot 0 is further along when it has a later chapter, the same chapter with more play time, or comes from a newer build. Then the write is skipped: `autosave_finished(reason, ERR_ALREADY_EXISTS)` and a warning, and slot 0 is untouched. Once the live run overtakes slot 0, its boundaries autosave again. **Exception:** a run started by New Game (where the player already confirmed "Begin anew") may replace slot 0 until its first autosave is written. Loading a save ends the exception. A downward `Game.set_chapter` (debug only) requests no autosave at all unless `SaveSystem.autosave_on_chapter_regress` is set (M1-ARC-10).
- **Consequences.** While a replayed older branch is behind slot 0, its progress is kept only in manual records (shrines). Continue still offers slot 0, the further-along run. A UI may later show a toast on `ERR_ALREADY_EXISTS` ("the autosave keeps a journey further along"). That needs a loc key and a UI task, not a policy change. Direct `autosave()` calls (debug keys, tests) are unaffected.

- **Also (review-sweep-E S3, M1-ARC-07 S2).** The director's backstop hold now follows the scripted shot rather than the tree. Leaving the tree drops it, and re-entering a tree with the shot still held takes it back, so a re-parented director keeps the autosave waiting.

## Amendment 2 — 2026-10-23: what Continue picks, and the director hold on a reparent (M1-ARC-11, review-sweep-F)
Append-only note; Amendment 1 is left as written. Where they differ, this note is what the code does.
- **Continue (correcting Amendment 1, Consequences).** Amendment 1 says "Continue still offers slot 0, the further-along run". That is true only until the player makes a manual record. `TitleSaveEntry.continue_slot` offers the readable slot with the **newest save time** (`saved_at`), autosave included. So while a replayed older branch is behind slot 0, Continue offers slot 0 until the player shrine-saves the branch; from then on it offers that manual record, the latest thing the player chose to save. Slot 0 still holds the further-along run, and the load menu lists it. This is the intended behaviour, not a bug: Continue means "where I last saved", and the further-along rule is about never *losing* slot 0, not about what Continue opens. The `ERR_ALREADY_EXISTS` toast is filed as a UI request (M1-UI-09) so the skipped autosave is not silent (pillar 4).
- **The director's backstop hold on a reparent (M1-ARC-07 review-sweep-F F1).** "Re-entering a tree with the shot still held takes it back" now applies only to a *settled* scripted shot. When the director leaves the tree with a move still owed, `_exit_tree` pays `blend_finished` and **drops the scripted shot**: the sequencer it wakes stops on `is_leaving()` and would never `release()`, so taking the hold back would block every chapter autosave until the zone was freed. A reparent mid-move therefore ends the cutscene (field_camera.md).

## Amendment 3 — 2026-10-23: no save path destroys an unreadable slot; table drift is repaired (M1-ARC-11, review-sweep-G)
Append-only note; Amendments 1 and 2 are left as written. Where they differ, this note is what the code does.
- **Context.** QA's review-sweep-G (B1) found that Amendment 1's "an empty or damaged slot 0 is never further along" turns a save this build *wrongly* reads as corrupt into a lost run. Sweep F had made a loadout that no longer fits the current item tables (a weapon renamed, removed or re-assigned by a later `equipment.json`) read as corrupt. The next chapter autosave, or `recover_temp`, then replaced that slot with no copy: a chapter 7 run became a chapter 2 autosave.
- **Decision, part 1 (repair, not reject).** Whether a worn piece fits its wearer and slot depends on tables a later build may change, so it is no longer a load check. After every load `EquipmentBag.repair_loadout()` takes a misfitting piece off into the bag, drops a piece whose base the tables no longer know, and warns for each. `grant_starting` then refills the weapon. Only what no table change can cause stays corrupt: a piece worn twice, a loadout uid that is not owned, and every other `SaveShape` problem.
- **Decision, part 2 (keep a copy).** Amendment 1's rule stands (a damaged slot 0 is not further along, so the autosave may replace it), but **no write replaces a non-empty slot that reads as corrupt without first moving it aside** to the next free `slot_NN.json.corrupt`, `.corrupt.2`, … (`MAX_CORRUPT` copies). This applies to `save_to_slot` (manual saves and the autosave) and `recover_temp`. If the copy cannot be made, the write is refused and the slot is kept. An empty (0-byte) file has nothing to keep.
- **Leftover temps (S2).** A temp file that is not provably older than its slot is set aside as `.recovered` before the next write and logged at startup: a recoverable temp as before, a newer build's temp, and a readable temp beside a newer build's slot. Only a torn temp and one older than a readable slot are overwritten.
- **Legacy counts (S1).** A negative whole count in a v0-v2 inventory is dropped (with a warning), as the frozen v2 → v3 step always did; from v3 on it is corrupt.
- **Nit: the system clock.** Continue offers the newest `saved_at` (Amendment 2), so a save made while the system clock was wrong (far in the future) stays the Continue slot until a later save passes it. Every slot is still listed in the load menu, so nothing is lost; a clock check is not worth a prompt.
- **Consequences.** A balance patch can never brick a save; at worst a hero's piece comes off and a warning names it. A truly damaged slot is always recoverable by hand from its `.corrupt` copy. Copies are never cleaned up automatically (each is a whole save, bounded by `MAX_CORRUPT`).
