---
id: M2-FP-03
title: First-playable flow - prologue, New Game routing, battle hand-off and return, end card
role: architect
status: review
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M1-ARC-06, M1-CMB-08]
milestone: M2
request-from: lead
---
## Goal
New Game → Prologue (Rhen's narration over the dead city) → Haluna beach; a field battle request that opens the CTB battle and returns to the field spawn; an end card after the Ch3 first verse that returns to the title.

## Acceptance criteria
- [x] `locations.json` new_game goes to the prologue; the prologue hands off to `ch02/haluna` at Beach.
- [x] `BattleRequest` + a field battle scene (instancing, not editing, the battle sandbox) that returns to the requesting location and spawn on victory or escape.
- [x] End card scene with a loc-keyed message; accept returns to the title.
- [x] Integration tests for each hand-off.

## Notes
- 2026-10-23 (worktree agent): built. APIs and choices in [first_playable_flow.md](../../tech/first_playable_flow.md).
  - `BattleRequest` (static start/make/submit/pending/take/clear) + `FieldBattle` (inherited `battle_sandbox.tscn`, live). Victory and escape show Return only; defeat keeps Fight again + Return (back to the field, flag unset, pre-fight vitals).
  - `ch02_tideline` (reef_crab + lantern_eel, escapable). BattleSim 500 seeds, rhen+asha / toma: 100% wins for every policy, ~10 turns, naive loses a member ~1 fight in 5.
  - Prologue scene (`game/levels/prologue/`), script `prologue_dead_city.dlg` (the SPEC §3.5 line only), `prologue` first in locations.json and `new_game` points at it. Hand-off to `ch02/haluna` / `Beach` from `game/data/flow/first_playable.json`; until that row is playable, `go_to` falls back to the default (warned).
  - End card (`game/flow/end_card.tscn`), loc keys `FLOW_END_CARD_*`.
  - Fixed `tools/validate_data.py` `scene_has_player`: a root `script = ExtResource(..)` property line (Godot's real format) now counts for place_at (was header-attribute only); test `tools/tests/test_fp_scene_place_at.py`.
  - Tests: `test_fp_field_battle.gd`, `test_fp_prologue.gd` (integration), `test_fp_end_card.gd` (unit).
  - Not done: screenshots of the prologue framing (skipped by instruction); the field trigger that calls `BattleRequest.start` belongs to the playable Haluna zone.

## Notes (handoff)
- Ready for review by **qa**. `tools/validate_data.py` (Systems-owned, shared) got a small fix so a root script defining `place_at` counts as a player (own commit + test); Systems please confirm.

## Review log
- 2026-10-23 qa (review-sweep-K, fresh reviewer): **approve with should-fixes.** No blockers. The flow can't soft-lock today, but the defeat path has no test.
  - **What I read:** the task, handoff first-playable-1, `git diff 2ddca3f^1 2ddca3f -- game/flow game/levels/prologue game/data/flow tests/integration/test_fp_* tests/unit/test_fp_end_card.gd tools/validate_data.py tools/tests/test_fp_scene_place_at.py`, scene_router.gd:80-97 and world_return.gd:61-140.
  - **Checks:** Godot `--filter=fp_` 15/0 failed, `world_return` 17/0. `validate_data` 0/0 and tool tests 400 OK.
  - **Soft-lock walk (by reading):**
    - **Loss.** Return goes to BattleReturn with the flag unset and the pre-fight vitals. Fight again reuses `request`.
    - **Escape.** It returns to the village side, and the strip fires again on the way back to the beach.
    - **Re-entry.** The victory flag blocks the trigger after a win.
    - **Save and load mid-thread.** A save is only possible at the shrine, after the strip. A load at Shrine skips Cutscene A, because `begin()` checks `ch02_met_asha` (haluna_story.gd:55). The cutscene's autosave hold covers the arrival.
    - **Data and strings.** Battle data and hand-offs are in first_playable.json. The end card and the Return labels are loc keys. The validator change (`_node_script_id`) is correct, and Systems can confirm from this entry.
  - **Should-fix:**
    - **S1: no defeat test.** test_fp_field_battle.gd covers victory (:92) and escape (:110), but not defeat. Add one for each outcome:
      - Defeat, then Return: the flag stays unset, the vitals are the pre-fight ones, and the party travels to the return spawn.
      - Defeat, then Fight again: the same encounter and seed start again, and `request` is kept.

      This is the path most likely to strand a player.
    - **S2: a hand-off is latched before it is known to go through.**
      - field_battle.gd:64 sets `returned = true` before `go_to`.
      - end_card.gd:84 sets `done = true` before `SceneRouter.change_scene`.
      - haluna_story.gd:90 sets `busy = true` and never resets it.

      `SceneRouter.change_scene` silently ignores a call while it is busy (scene_router.gd:81-83), and `WorldReturn._travel` still returns true (world_return.gd:139-140). So a Return that lands during a router swap leaves the result panel or the end card dead.

      The current timings make that unlikely: the end card's 1.5 s hold is longer than FADE_SEC 0.35 plus 4 frames. Still, wait for `not SceneRouter.is_busy()` first, as prologue_scene.gd:89 does, or un-latch when the swap is refused.
    - **S3: no test for a missing request.** No test covers `BattleRequest.submit` without a SceneRouter (battle_request.gd:72 push_error). The request stays pending and the field stays busy. Add a test, or clear `_pending` on that path.
