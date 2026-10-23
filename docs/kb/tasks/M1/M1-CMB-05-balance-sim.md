---
id: M1-CMB-05
title: Headless balancing simulator
role: combat
status: done
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
- 2026-10-23 progression (review-sweep-A): **approve with fixes**. The simulator is sound and reproduces exactly. `python3 tools/balance/sim.py --seeds 1000 --check` (report written to /tmp) gave naive 8.7%, lowest_hp 82.8%, role_answer 96.8% and smart 99.7%, the same as the committed `balance_report.md` table. 200 seeds gave 9.5, 85.0, 96.0 and 99.5. Runs are deterministic, policies never touch `engine.rng`, `take_turn` always ends the turn, and timeouts are counted as misses. The `battle_victory` baseline was already re-approved in cf6b820, so the "known gate issue" note is stale.
  - **should-fix** (band assumptions): the bands are written for a party with every Lattice point spent but no gear and no items. PRG-02 has now landed both. A probe running `run_many` with `party_modifier = EquipmentEffects.apply_to` moved the sandbox to naive 10.9% with starting gear and naive 18.7% with the slice's tier-1 forge gear, which is outside the 5–15% band. role_answer went 96.8 → 98.4 and smart → 100.0. Before Drownbell is tuned, `balance_targets.md` must state which gear (the shop stock under that chapter's flags) and which consumables the "chapter party" carries. `smart` also needs an item rule (Salt Tonic or Relighting Wick), or a boss band like smart 80–95% will be tuned against a player who never uses items. I can supply a party-goods fixture per chapter from `economy.md`.
  - **nit**: `lowest_hp` is report-only, and the swap lesson is the 14 pp gap between it and `role_answer`. Consider a gap band, such as `role_answer − lowest_hp ≥ 10 pp`, so a tuning change can't quietly erase the reason the sandbox exists.
  - **nit**: in CI the naive band is asserted at a fixed 200 seeds (9.5% against a 5% floor). That is deterministic, so it won't flake, but any change to RNG call order will move it. Expect to re-tune rather than treat a miss as a bug.
- 2026-10-23 lead: closing on review-sweep-A approve-with-fixes; the run was reproduced exactly. Gear-aware bands were forwarded into M1-CMB-06.
