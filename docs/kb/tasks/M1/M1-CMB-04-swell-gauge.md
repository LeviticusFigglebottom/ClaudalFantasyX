---
id: M1-CMB-04
title: Swell gauge modes and Rhen's interactive Swell input
role: combat
status: review
owner_session: worktree-agent-af3aaf0993fbaba55
depends_on: [M1-CMB-01]
milestone: M1
request-from: ""
---
## Goal
SPEC §6.2: gauge fill modes plus one unique interactive input (Rhen).

## Acceptance criteria
- [x] At least 3 fill modes, data-driven, with numbers in formulas.md. There are four: Ballast (damage taken, rate 120), Wake (damage dealt, rate 50), Tether (an ally hurt, rate 60) and Salve (a healing item, flat 20). They live in `game/data/battle/swell.json`, and `check_swell` validates them (at least 3 modes, known triggers). The rules are in formulas.md § Swell, with `Formulas.swell_gain / swell_fill / swell_power` and their tests.
- [x] Rhen's input is short, cancelable, and distinct. The Lamp Ring (`SwellTimingRing`, drawn by `SwellRingView`) is 3 flares in at most 3.0 s, pressed at the brightest. Perfect, good and miss read by shape. It can be cancelled before the first grade, at no cost, back to the target pick.
- [x] Engine-side resolution is headless-testable (input result passed in). `BattleSwell.perform(technique, targets, {cancelled, grades})` goes through `BattleEngine.perform_row`, and it is tested on a fixture DB in `tests/unit/test_battle_swell.gd`.

## Notes
- **Reviewer: ui.** The HUD gauge placement and the ring panel are deviations 8 and 9 in tech/ui.md and want an art eye. The formulas.md § Swell change asks for a Progression look as well (formulas.md rule).
- **Engine:** `battle_engine.gd` was at 996 lines. The item rules moved to `BattleItemRules` (the engine keeps `item_*` wrappers), and the engine gained only `perform_row` and `apply_fixture`'s `swell`, ending at 951 lines. Gauges fill from `action_resolved`, so the core does not call Swell.
- **Controller:** `battle_controller.gd` was at 995 lines. Float feedback moved to `BattleFloats` and the victory rows to `BattleRewards`, both unchanged; it ends at 991 with the Swell flow.
- **Screenshots:** a new `battle_swell_ring` shot. `battle_hud_preview`, `battle_swap_menu` and `battle_statuses` were re-approved on purpose (Rhen's empty gauge under his name; rmse ≤ 0.0016 before re-approval). `battle_victory` is unchanged.
- **Gate:** `tools/ci_local.sh` with the five battle shots passes; coverage in game/battle is 99.79% (baseline 99.75%).
- **Follow-ups:** M2-CMB-01 (unlock rules, other heroes' inputs, Swell in the simulator), M2-ARC-01 (carry gauges and modes across battles and saves), M2-UI-01 (mode menu, timing assist).

## Review log
- 2026-10-23 ui (review-sweep-I, fresh reviewer): **approve-with-fixes.** No blockers.
  - **What I read:** the task, handoff combat-3, `git log -p` for 71d564a..2946904 (merge 32bab62), formulas.md § Swell, battle_ctb.md and tech/ui.md § Swell plus deviations 8 and 9, art/ui.md §6.2, and the `battle_swell_ring` baseline (viewed).
  - **Checks:** `validate_data` 0/0. `unittest discover -s tools/tests` 359 OK. `taskboard --check` OK. gdlint and gdformat clean. Godot `--filter=swell` 38 run, 0 failed (own `XDG_DATA_HOME`).
  - **What passes:**
    - **Formulas trio.** formulas.md, formulas.gd and test_formulas.gd changed together in b19b0aa. The worked examples (27, 20, 19, 22, 17) match the tests.
    - **Headless and deterministic.** `BattleSwell` and `SwellTimingRing` are RefCounted, use no Nodes and no RNG, and only read data. The input result is passed in. The engine core never calls Swell: gauges fill from `action_resolved`. `perform_row` keeps every `_checked` rule. The `BattleItemRules`, `BattleFloats` and `BattleRewards` extractions are behaviour-preserving moves.
    - **Tactical clarity (pillar 4).** The Swell row shows only when the technique is usable. The technique page and the target pick preview the rank-2 turn cost on the timeline, and the ghost slot stays visible while the ring is open (baseline). The result line names each grade and the bonus ("+45% power"). The bonus can only add (`swell_power` floors at the base), and canceling costs nothing. The real-time ring is the §6.2-mandated input, opened only after the player commits, so §6.1's "no real-time pressure" still holds for every decision.
    - **Reduced motion.** The full gauge holds `glow = 1` instead of pulsing (party_row.gd `_refresh_swell`), and `_process` stops. The ring drops its flicker but keeps the flare and the closing ring, which are the timing cue itself. Grades read by shape (filled diamond with a halo, filled diamond, cross). Both behaviours are tested.
  - **Should-fix:**
    - **S1 (input fairness).** battle_controller.gd:251-253: `tick()` advances the ring by the raw frame delta, and `_handle_ring_input` (:702) grades the press against the `elapsed` of the last frame. A single long frame (RND-07 measured 121-150 ms prewarm frames, plus GC or a load) can skip past a peak or turn a beat into a miss. At 30 fps, frame quantization is up to 33 ms against a ±60 ms perfect window. Clamp the per-tick delta (for example ≤ 1/20 s, so a hitch pauses the ring instead of skipping it), and ideally grade with the input event's timestamp.
    - **S2 (full-gauge cue).** hud_gauge.gd:59-60 frames a full gauge in `focus_gold` (`ui_line_gold` #D9B45A) at 1 px, around a `ui_swell` (#F2B84B) fill. Those are nearly the same hue, and in `battle_swell_ring.png` the frame cannot be seen. Deviation 8 claims this as "a shape cue, not hue alone". Use a contrasting frame (`ui_line_white`, or a 2 px gap and frame), or a small full glyph after the bar.
    - **S3 (validator).** validate_data.py:1598-1611 (`_swell_input_errors`) does not check that the grading window fits its beat: `peak_at × beat_sec + good_sec ≤ beat_sec`. Today it is 0.56 + 0.15 = 0.71 ≤ 0.8. If a tuning pushes the late window past the beat, `advance()` grades a miss before the press and the press lands on the next beat. Also bound `duration_sec` (the spec says "short").
    - **S4 (loc).** strings.csv:421 `SWELL_INPUT_TIMING_RING_HELP` hard-codes "three times", but `beats` is data. Use `{beats}`, or say "on each flare".
  - **Nits:**
    - battle_controller.gd:612 and :689: a `target: "self"` technique would open the ring without a pick, and a cancel then lands in `STATE_TARGET` (:726) with no candidates. No technique uses it yet. Guard it, or reject `self` techniques in `check_swell`.
    - battle_swell.gd:165-167: `_resolving` suppresses every gauge gain inside `perform_row`, including hits the party takes during the technique (a Reflect bounce). That matches "a technique feeds no gauge", but say so in formulas.md.
    - While the ring is open, the help line calls `swell_help(..., -1)`, so it drops "next in N". The timeline still shows the ghost slot, so this is minor.
  - **Deviations 8 and 9 (ui):** accepted. The gauge under the name is the right trade for the row width once S2 is fixed. The ring panel in the command menu's place never covers the fighters, and the timeline stays readable beside it. M2-UI-01 (timing assist) should land before the M2 slice review, because the ring is the only real-time input in the game.
  - **Formulas (Progression glance):** nothing in progression changes. § Swell is self-contained, and "Not yet specified" is updated.
