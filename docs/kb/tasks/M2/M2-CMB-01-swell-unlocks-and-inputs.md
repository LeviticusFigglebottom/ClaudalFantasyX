---
id: M2-CMB-01
title: Swell mode unlocks through play, and the other heroes' Swell inputs
role: combat
status: done
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
- 2026-10-23 progression, fresh reviewer (review-sweep-M): **approve.** No blockers.
  - **Checks run** (worktree at 449f856, own `XDG_DATA_HOME`):
    - Godot `--filter=swell` 93/0 failed (inputs, unlocks, save, HUD and sim_swell), `--filter=battle_sim` 30/0 and `--filter=formulas` 26/0.
    - validate_data 0/0, tools unittest 431 OK (test_swell_validate, test_balance_sim), gdlint and gdformat clean.
    - **I re-ran the simulator:** `tools/balance/sim.py --suite sandbox_reef --seeds 300`, report to scratch. naive 10.7%, lowest_hp 89.7%, role_answer 94.3%, smart 100%. Every band is ok, which matches the committed 1000-seed table within noise.
  - **Determinism: OK.**
    - The new inputs and BattleSwell read no clock, RNG or Node, and time moves only through `advance()`. `scripted_result` is pure.
    - Damage still goes through the engine's seeded rng.
    - test_battle_sim_swell.gd:67-69 replays seed 9 with Swell on and asserts identical results.
    - The policy reset (`swells_used`) and the per-run BattleSwell keep runs independent.
  - **Formulas trio: no breach, one gap.** formulas.gd is unchanged: the new inputs feed the existing `swell_power` and `bonus_pct` paths, and the new tables are data. So editing formulas.md alone does not break the rule. **Gap:** the new worked numbers in formulas.md § Swell are not pinned in tests/unit/test_formulas.gd: Shallows Verse 17/22, Return Tide 20/26, Written Light 14/19. test_every_live_input_earns_the_same_bonus_at_each_quality pins +45/+90, but not these powers. Add the three `swell_power` cases (should-fix 1).
  - **Judgement on "naive never uses Swell": true by construction, and fair as a model of the masher, but the band hides the risk rather than measuring it.**
    - The construction matches the game. In battle_menus.gd:60-76, Attack is row 0 and Swell is appended after it, and the menus have no cursor memory, so mashing confirm really does pick Attack every turn.
    - It is still an assertion (sim_policy_naive.gd:11 returns false), not a measured behaviour. The balance report's own number shows the risk. A masher who opens Swell even once a fight wins 37.5% against a 5–15% band, and Shallows Verse alone takes them to 31.5%. The Swell row is drawn in the swell colour on a pulsing, framed gauge, so the HUD invites exactly that press.
    - Shallows Verse (skills.json:79) is power 12, every ally, no MP. That is twice Chorus Mend's power, for free, so it is the outlier to watch.
    - I accept the claim for the naive band. Should-fix 2 keeps the masher-with-Swell number visible.
  - **Should-fix:**
    1. tests/unit/test_formulas.gd: pin the three technique powers at good and perfect from formulas.md § Swell. Edit the trio together.
    2. tools/balance/targets.json and game/battle/sim/: add a report-only `naive_swell` policy (naive plus `unleashes_swell() == true`), so every report shows the masher-with-Swell rate next to the naive band. A rate that drifts past about 30% then needs a deliberate decision instead of going unseen.
    3. sim_policy.gd:63-99. A ready technique always goes first and aims at the lowest-HP foe, ignoring `role_answer`'s focus. That is why role_answer loses about 3 points at miss and good. It is a sim-policy artefact, not a balance fact. Let role_answer and smart pass their focus foe into `_swell_targets`, or record the artefact in balance_targets.md.
    4. swell.json:39 (`tether_from_ballast`, count 12). Every hero now has a Swell and every hit on any of them counts, so Tether will unlock in the first one or two sandbox fights. Note in formulas.md that the 12 was chosen for one Swell hero, or raise it.
    5. Brace UX for M2-UI-03 (swell_brace.gd:81-96). The technique is chosen with ui_accept, so the brace opens on a press the menu has already consumed. The first blow can land before the player re-presses. Make the lead-in long enough to re-press, or treat a held accept at open as `holding`.
- 2026-10-23 lead: closing on review-sweep-M approve; the should-fixes are in M2-NIT-03.
