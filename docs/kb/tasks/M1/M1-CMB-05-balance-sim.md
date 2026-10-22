---
id: M1-CMB-05
title: Headless balancing simulator
role: combat
status: review
owner_session: combat-stream-2
reviewer: progression
depends_on: [M1-CMB-00]
milestone: M1
request-from: ""
---
## Goal
SPEC §6.9: thousands of seeded fights per encounter, reporting win rate, average turns, and item use.

## Acceptance criteria
- [x] A GDScript runner scene runs N seeds with a pluggable party policy
- [x] tools/balance/sim.py invokes Godot headless and writes a Markdown/CSV report
- [x] Target bands per chapter documented in docs/kb/design/balance_targets.md

## Notes
Sandbox note: a naive all-attack policy probably loses to sandbox_reef by design (the elegant answer is swapping). Report it.

Delivered:
- `game/battle/sim/`: `BattleSim` (`run_one`, `run_many`, `summarize`) plus `SimPolicy` subclasses (naive, lowest_hp, role_answer, smart), and `sim_main.gd` for `godot --headless -s`. Policy tunables are in `game/data/battle/sim_policies.json`.
- `tools/balance/sim.py`: runs the suites in `tools/balance/targets.json`, writes `docs/kb/design/balance_report.md` (keeping the tuning log) and CSVs in `tools/balance/out/` (gitignored, `.gdignore`d). `--check` exits 1 on a miss.
- `balance_targets.md`: the chapter curve, the M1 sandbox suite, and Drownbell (Ch3 boss; pending until its encounter data exists).
- Sandbox tuning in `enemies.json`. 1000 seeds, before → after: naive 0.0 → 8.7%, lowest_hp 58.8 → 82.8%, role_answer 86.5 → 96.8%, smart 98.9 → 99.7%. The integration test asserts the bands at 200 seeds.
- **Known gate issue:** the tuning changes the `battle_victory` capture (Rhen now survives; RMSE 0.016 against 0.008). It needs a QA-approved baseline refresh (`python3 tools/screenshots/compare.py --update-baselines battle_victory`). Every other gate passes. See the M1-CMB-01 review, item 6.
Follow-ups: a full-Lattice-petal run (`run_one(..., party_modifier)`), per-skill usage in the report (Kick Off tempo), and a Drownbell encounter once boss phases and summons exist.

## Review log
