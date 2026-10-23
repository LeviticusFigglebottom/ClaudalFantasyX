---
id: M2-CMB-01
title: Swell mode unlocks through play, and the other heroes' Swell inputs
role: combat
status: review
reviewer: progression
owner_session: worktree-agent-a670939c5cb593976
depends_on: [M1-CMB-04]
milestone: M2
request-from: ""
---
## Goal
SPEC §6.2 follow-up to M1-CMB-04: players unlock new fill modes through play, and every hero's Swell has its own short, cancelable input.

## Acceptance criteria
- [x] Unlock rules are data in `game/data/battle/swell.json` (for example "take N hits in Ballast unlocks Tether"), counted by `BattleSwell` and calling `unlock_mode()`. The numbers go in formulas.md § Swell.
- [x] At least one more input kind is Node-free and headless-testable like `SwellTimingRing`. Candidates from the character sheets: Asha's chant sequence, Liss's reel-stop, and Pell's call-and-response tiles. It is validated in `check_swell` (`SWELL_INPUT_KINDS`).
- [x] The balance simulator can unleash techniques with a fixed input result (for example all `good`), and balance_report.md records the effect on the sandbox bands.

## Notes
- Rhen's ring, the four modes and their rates are in formulas.md § Swell. The engine takes only `{cancelled, grades}`, so a new input needs only its own grade table.

- 2026-10-23 combat (worktree-agent-a670939c5cb593976): ready for review (reviewer **progression**, Combat ↔ Progression; UI glances at the HUD gate).
  - Unlocks: `swell.json` `unlocks` (Tether after 12 hits taken in Ballast, Salve after 5 healing items), counted in `BattleSwell._count`; `mode_unlocked` signal; record via `load_saved`/`to_saved`.
  - Inputs: `SwellInput` base plus `SwellChant` (Asha), `SwellBrace` (Toma), `SwellGlyph` (Ysolde), all Node-free; each earns +45% at good and +90% perfect. Techniques Shallows Verse, Return Tide, Written Light. `SWELL_INPUT_KINDS` = ring, chant, brace, glyph, with per-kind checks.
  - The HUD draws only the ring, so `SwellRingView.DRAWN_KINDS` hides the other heroes' gauges and Swell rows until M2-UI-03 (request filed). No baseline moved.
  - Sim: `--swell` / targets.json `swell` (suites at good); naive never unleashes. All bands hold at every quality (balance_report.md 2026-10-23).
  - Gate: `HYMN_SKIP_BLENDER=1 HYMN_SHOTS=battle_hud_preview,battle_swap_menu,battle_victory,battle_statuses,battle_swell_ring tools/ci_local.sh` rc 0 (Blender step run separately in the first pass: identical). 1116 Godot tests, 0 failed; coverage battle 99.94% (1763/1764), progression 96.52%; five battle shots rmse 0; tool tests 421 OK; validate_data 0/0.

## Review log
