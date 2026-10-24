---
id: M2-UI-14
title: Accessibility audit (5/5): a "hold to confirm" alternative for timed Swell inputs
role: ui
status: review
owner_session: "claude/ui"
reviewer: combat
depends_on: [M2-UI-03]
milestone: M2
request-from: lead
---
## Goal
Timed inputs (Rhen's ring, Asha's chant, Toma's brace, Ysolde's glyph) ask for presses at moments. A player who cannot time presses can already widen the window or count misses as Good (timing assist, M2-UI-01). The audit asks for a "hold to confirm" way to play them: holding Confirm plays the input for you.

## Acceptance criteria
- [x] A new `timing_assist` option, `hold`: while Confirm is held, each step is played at the assist floor's grade (good) when it comes up, so the input finishes on its own. Release pauses that, and the player may play steps by hand.
- [x] It works through `SwellInput` and `UiSettings` like the other assist options (no engine rule changes). Swift (glyph) is never earned by the assist, as with "auto".
- [x] The panel shows the assist tag, and the hint says "Hold Confirm".
- [x] Tests for each kind.

## Implementation notes (claude/ui, 2026-10-24)
- **The setting.** `timing_assist` gains `hold` (accessibility.json: `assist_floor` good plus `assist_hold`; loc `SET_TIMING_ASSIST_HOLD`, tag `HUD_SWELL_ASSIST_HOLD` "Assist: hold Confirm to play"). The panel shows the tag at its top left, as for the other options; that tag is the "hint", and the per-kind hint lines are unchanged.
- **The rule.** `SwellInput.assist_hold` and `held`: `_record` applies `assist_floor` to a miss only while `held`. Holding Confirm therefore lets every step run out at Good, and the input finishes by itself. Letting go hands the steps back, so an unpressed step is a miss again and a hand-played step is graded as played. Swift still reads `raw_misses`, so the hold never earns it. No grade table or engine rule changed: only the condition in `_record`.
- **Input.**
  - `SwellInputKeys.feed` tracks Confirm for every kind while the hold assist is on: the chant and glyph take Confirm only then.
  - `SwellRingClock.hold()` catches time up before it flips `held`, so a step that ran out earlier is graded with the old state.
  - For the brace, letting go clears `held` before the release is graded, so an early release is played by hand.
  - `carry_held` also starts the hold for any kind when Confirm is still held from the menu.
- **Tests:** `tests/unit/test_swell_hold_assist.gd` (6) covers all four kinds at Good, letting go, no Swift, the menu carry, and Confirm passing a direction input when the assist is off. Updated: `test_swell_mode_menu.gd` (the options list).
- **Reviewer combat,** because `swell_input.gd` is under game/battle.

## Review log
