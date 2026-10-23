---
id: M1-CMB-01
title: CTB battle sandbox: 2 heroes vs 3 enemies with timeline preview and swap
role: combat
status: done
owner_session: ui-combat-stream-1
reviewer: progression
depends_on: [M1-CMB-00, M1-UI-01]
milestone: M1
request-from: ""
---
## Goal
SPEC §10.2 M1 exit criterion: a playable battle sandbox scene on top of the engine.

## Acceptance criteria
- [x] Scene game/battle/scene/battle_sandbox.tscn is reachable from the F-key debug menu (for now F9 on the boot screen, debug builds, until M1-ARC-02)
- [x] Timeline (right side) shows the next 16 turns; hovering a command previews the shift
- [x] Swap menu works on any party turn at no time cost
- [x] Target highlight ring shader (placeholder look is fine at M1)
- [x] Rhen + Asha vs sandbox_reef, reserves Toma + Ysolde

## Notes
Greybox visuals are acceptable; this proves tactical clarity (pillar 4).

Delivered (how it works: `docs/kb/tech/ui.md`, "Battle sandbox"):
- `battle_sandbox.tscn`: a greybox arena, primitive stand-ins (`battle_sandbox.json`), `ground_ring.gdshader`, a fixed camera, and the HUD.
- `BattleController`: the engine API and signals only. Previews follow hovered commands, skills and targets. Swap is free, Escape works, enemy turns are paced, damage numbers show, and there are victory, defeat and escape screens with retry.
- **Engine API added:** `BattleEngine.party_modifier: Callable`, run once on each party combatant after `_make_party_member`. The sandbox sets it to `LatticeProgress.apply_to`. Victory feeds `xp_awards()` into `award_battle()` and saves `Game.state.lattice`.
- Tests: `tests/unit/test_battle_controller.gd` (15 tests, simulated `ui_*` input on the real scene) and 4 new hook tests in `tests/unit/test_battle_engine.gd`.
- Capture states `player_preview`, `swap_menu` and `victory` (`game/battle/scene/shots/`). Baselines are in `tests/screenshots/baselines/`.
- Also done: the Combat review of M1-PRG-01 (approve with one fix: Shield Wall MP).

Follow-ups: `BattleEngine.preview_swap(out, in)`, so the Swap menu can move timeline chips (today the help line explains the effect). Defeat still means every *active* member is KO'd, and the sandbox makes that readable: the result screen lists fallen fighters.

Review follow-ups closed by M1-UI-02 (2026-10-23, `docs/kb/tasks/M1/M1-UI-02-battle-hud-followups.md`):
- [x] 1. Unlocalized fail reasons: every reason maps to a `HUD_FAIL_*` line (`BattleMenus.fail_text`), and a test reads the reasons from the engine.
- [x] 2. Provoke targeting: the cursor starts on and is locked to `forced_target()`, with a hook marker on the provoker.
- [x] 3. Swap preview: the swap-in and swap-out steps show `preview_swap(out, in)`; the chips move.
- [x] 4. Auto-turn copy: Berserk/Confuse turns are announced and reported from `auto_reason`, with their own pacing.
- [x] 5. New status data: the Doom count is on chips and party rows, Reflect shows a bounce arc and "Reflected", Petrify shows a stone portrait and stand-in.
- [x] 6. Victory capture encodes balance: every capture state runs on `game/data/ui/battle_fixtures.json` (frozen tables), so rebalancing no longer moves the baselines.
- [x] 7. Flaky-risk captures: the baselines were re-approved on the fixture data. Repeat captures here measure RMSE 0.00000. Text anti-aliasing determinism on other stacks is still QA's question.
- The swap follow-up above is closed by item 3.

## Review log
- **2026-10-22, Progression-side reviewer (combat-stream-2), SPEC §12.3 pair: approve with follow-ups (none blocking).**
  Read `game/battle/scene/` (controller, menus, stage, stand-ins), `docs/kb/tech/ui.md` § Battle sandbox and `tests/unit/test_battle_controller.gd`. Ran the sandbox headlessly through its tests (15/15 pass, plus the 4 `party_modifier` hook tests in `test_battle_engine.gd`) and the full `tools/ci_local.sh`.
  **Lattice hook-up is correct.** `party_modifier = progress.apply_to` is set before `setup()`, so active and reserve fighters are built once each with their gains. Victory feeds `xp_awards()` into `award_battle()` only for travellers on the board. Fallen participants get nothing ("Fell before the end"), which matches the XP credit rule. `persist_progress` gates the write to `Game.state.lattice`. The controller never writes combatant state. Note: with ADR 0012, a modifier can no longer change `level`, and the engine undoes any attempt.
  It also works with M1-CMB-02 unchanged: a Berserk/Confused party member makes `is_party_turn()` false, so `_next_turn()` routes it through `_run_enemy()` → `run_enemy_turn()`, which plays the automatic turn with normal pacing (I checked this by reading the code, not with a scene test).
  Issues (owner: UI/combat stream; I did not touch `game/battle/scene/`):
  1. **Unlocalized text on screen.** `act()` shows `hud.set_help(String(result.fail_reason))`, so the player sees raw ids (`no_mp`, `silenced`, `no_valid_target`, and now `provoked` / `auto_turn`). Map each reason to a `HUD_FAIL_*` key (CLAUDE.md §3).
  2. **Provoke targeting.** `_default_targets()` / `_candidates_for()` ignore `engine.forced_target(actor, skill)`, so a Provoked hero can pick an illegal foe and only learns why from issue 1's raw text. Start the cursor on, or lock it to, the forced target.
  3. **Swap preview.** `STATE_SWAP_OUT` shows `MODE_PREVIEW` with no shift. `BattleEngine.preview_swap(out, in, count)` now exists; the one-line hook-up is in `battle_ctb.md` § Timeline API.
  4. **Auto-turn copy.** `_run_enemy()` labels a Berserk/Confused *party* member's turn with `HUD_ENEMY_ACTS_FMT`. Use `ActionResult.auto_reason` for a "{name} is berserk / confused" line (pillar 4: say why the player had no menu).
  5. **New status data not shown yet:** `TurnEntry.doom` (the countdown chip), `hits[].reflected_from` (a bounce cue), and `BattleCombatant.is_petrified()` (stone currently renders as KO, which is acceptable for greybox).
  6. **The victory capture encodes balance.** `battle_victory` shows who fell, so any enemy tuning breaks the screenshot gate. M1-CMB-05's sandbox softening does: RMSE 0.0160 against the 0.008 limit; the same shot on the old data measures 0.00026. Now Rhen survives, so the result lists three XP rows instead of "Rhen: Fell before the end". QA needs to approve the new baseline (`compare.py --update-baselines battle_victory`). Longer term, pin the capture to a fixture encounter, or show a result that doesn't depend on tuning.
  7. **Flaky-risk captures.** `battle_hud_preview` and `battle_swap_menu` sit at 0.0078–0.0079 against a 0.008 limit even on unchanged data (0.00777 measured on the pre-tuning data). The diff concentrates on HUD text. QA should check text anti-aliasing determinism, or re-baseline.
  Fine as-is: the state machine and cancel paths, instant-pacing drain loop, the failed-escape preview (rank-3 turn), the default-target heuristics, and the capture scripts driving only the intent API.
- 2026-10-23 lead: closing on the Progression-side approval; the UI follow-ups are M1-UI-02 (in progress).
