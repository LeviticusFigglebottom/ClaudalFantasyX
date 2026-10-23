---
id: M1-UI-05
title: Swell HUD and validator fixes (review-sweep-I on CMB-04)
role: ui
status: review
owner_session: "worktree-agent-ae77f8e225d2b48a3"
depends_on: [M1-CMB-04]
milestone: M1
request-from: "combat"
---
## Goal
From the review-sweep-I entries (file:line references there).

## Acceptance criteria
- [x] The Lamp Ring advances on clamped or fixed-step time so one long frame cannot skip a beat (battle_controller.gd ~:251-253, ~:702)
- [x] The full-gauge gold frame is distinguishable from the fill (contrast check; hud_gauge.gd ~:59-60)
- [x] validate_data checks that each timing window fits inside its beat (~:1598)
- [x] The ring help text does not hard-code the beat count (strings.csv ~:421)

## Notes
- **Reviewer: combat** (CMB-04's owner; the ring and swell.json are combat's).
- **S1, input fairness.** New `SwellRingClock` (`game/battle/scene/swell_ring_clock.gd`, RefCounted) is the only code that reads the wall clock. `SwellTimingRing` stays node-free and deterministic: it gains `max_step_sec` (data) and `clamp_step()`.
  - `_process` calls `tick(delta, true)`: a rendered frame moves the ring by at most `max_step_sec` = **0.05 s** (swell.json), so a long frame pauses the ring instead of skipping a peak. `tick(delta)` without `frame` is exact simulated time, so tests and the capture script are unchanged.
  - A press first catches the ring up from the last frame to the moment the event is handled (clamped too), and the next frame subtracts it. That removes the one-frame lag (33 ms at 30 fps). Godot 4 input events carry no timestamp, so this is as close to "the event's time" as the engine allows.
  - The validator keeps `max_step_sec` in (0, `perfect_sec`], so neither a hitch nor a catch-up can move a press across a whole grade. That also makes the capture deterministic: its press grades perfect whatever the wall clock does.
  - battle_controller.gd is at 994 lines (lint cap 1000).
- **S2, full frame.** `HudGauge` draws a 2 px `outline` (night) gap, then a 2 px `text` (white) line, outside a full gauge, as filled whole-pixel bands under the bar. 1 px bands were tried first and vanished in the 1280x720 capture: it draws the 1080p layout at 2/3 scale, so 1 px is 0.67 px (also part of why the old 1 px gold frame was invisible) (`swell_full_gap_px` and `swell_full_frame_px` in battle_hud.json; `full_frame_rects()`). The old `focus_gold` frame is ~1.1:1 against `ui_swell`. Fill vs gap, the brightened fill vs gap, and frame vs gap all clear 3:1 (WCAG 1.4.11), checked on the real theme colours in `tests/unit/test_hud_gauge.gd`.
- **S3, validator.** `_ring_timing_errors` in validate_data.py: the good window must sit inside its beat on both sides (`peak_at x beat_sec ± good_sec` within `[0, beat_sec]`; today 0.41..0.71 in 0.8), the whole input must be ≤ `RING_MAX_DURATION_SEC` = 5 s (today 3.0 s), and `max_step_sec` must be in (0, `perfect_sec`]. Tests: `tools/tests/test_swell_validate.py`.
- **S4, loc.** `SWELL_INPUT_TIMING_RING_HELP` is "Press as each flare burns brightest. Flares: {beats}." (one line in the help panel, as before) `BattleMenus.swell_help` fills `{beats}` from the input row. (No plural form is needed, because the count stands alone.)
- **Nits not done** (no AC; noted for M2-UI-01 or CMB): a `target: "self"` technique would open the ring with no pick; the `_resolving` gauge suppression wants a line in formulas.md; the open ring's help line drops "next in N".
- **Screenshots:** `battle_swell_ring` changes on purpose (the frame on Rhen's full gauge, and the help line's new text). `battle_hud_preview` has an empty gauge, so it doesn't change. See the gate results below.
- **Docs:** tech/ui.md § Swell (deviation 8, input fairness, help text).
- Tests: `tests/unit/test_swell_ring_clock.gd` (7), `tests/unit/test_hud_gauge.gd` (3), and 1 new + 2 extended in `tests/unit/test_battle_swell_hud.gd`.

## Review log
- 2026-10-23 combat (review-sweep-J, fresh reviewer): **approve with should-fixes.** No blockers.
  - **What I read:**
    - the task and handoff qa-2;
    - the commits dcaca56, 9e76295 and 6a43b1f: `SwellRingClock`, `SwellTimingRing.clamp_step`, battle_controller `tick`/`_handle_ring_input`, `HudGauge.full_frame_rects`, party_row, battle_menus `swell_help`, the validator, swell.json and battle_hud.json.
  - **I viewed tests/screenshots/baselines/battle_swell_ring.png:**
    - The white frame with its dark gap is plainly visible round Rhen's full gauge, and it overlaps nothing.
    - The help line fits on one line.
  - **Checks:** Godot `--filter=swell` 46/0 and `hud_gauge` 3/0 failed. Tool tests 382 OK, including test_swell_validate. `validate_data` 0/0.
  - **What passes:**
    - The clamp (`max_step_sec` 0.05 ≤ `perfect_sec` 0.06, validated).
    - The press catch-up, with the next frame subtracting it.
    - The validator conditions, which match `SwellTimingRing.press/advance` exactly: a press before `beat_start` is ignored, and one after the next beat start lands on the next beat.
    - The 3:1 contrast test on the real theme colours.
  - **Should-fix:**
    - **S1 (two clocks under `Engine.time_scale`).** swell_ring_clock.gd:35 steps by the engine `delta`, which `Engine.time_scale` scales. :47 catches up by wall-clock µs, which it does not. battle_controller.gd:255 says "input timing is real time: never scaled", but that only holds for pacing, not for `time_scale` (used by CaptureSetup today, and by any later slow-mo). Pick one: step frames by wall-clock µs too, or divide the catch-up by `Engine.time_scale`.
    - **S2 (help text reads oddly).**
      - battle_menus.gd:126-128 joins with " · ", so the line becomes "Press as each flare burns brightest. Flares: 3. · Physical, one foe" (visible in the baseline). Drop the trailing period in strings.csv:421.
      - That line also says "as each flare burns brightest", while the ring's own hint (strings.csv:424) says "strike as the ring meets the lamp". Two different instructions for one input go against pillar 4 (tactical clarity). Narrative or UI should pick one metaphor.
    - **S3 (Art spec).** docs/kb/art/ui.md:135 still specifies only "glows with a 1.6 s sine pulse" for a full gauge. The night-gap-plus-white-frame is documented as deviation 8 in tech/ui.md:126 only. Ask Art to append the frame to art/ui.md §6.2, or approve it there.
  - **Nits:**
    - Below 20 fps (frame time > 0.05 s) the ring now runs slower than real time. That is fair, and the ring draws its own `elapsed`, but say so in tech/ui.md.
    - The author's open nits stand: `target: "self"`, the `_resolving` line in formulas.md, and "next in N".
