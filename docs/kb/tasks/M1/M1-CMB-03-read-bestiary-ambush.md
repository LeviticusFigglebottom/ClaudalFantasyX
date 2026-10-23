---
id: M1-CMB-03
title: Read ability, bestiary log, preemptive/ambush openings
role: combat
status: review
owner_session: worktree-agent-ac6e2c29473e13d13
depends_on: [M1-CMB-00]
milestone: M1
request-from: ""
---
## Goal
SPEC §6.1 Read/Scan plus opening-tick modifiers.

## Acceptance criteria
- [x] Read reveals stats, weaknesses, and lore_key, and logs to a bestiary in GameStateData. `read` is a rank-2, 0 MP single-foe support skill that Ysolde knows. The hit carries `BattleRead.reveal()`: stats, HP/MP, affinity lists, lore_key, delay immunity and statuses. `BattleBestiary` logs it into `GameStateData.bestiary` (save v5, wrapped by `Bestiary`), plus one defeat per foe on victory.
- [x] Preemptive and ambush adjust initial ticks (documented in formulas.md § Openings). `BattleOpening.choose` makes one RNG draw (an 11% / 5% split in the sandbox), or uses the encounter's fixed `opening`. `begin()` pushes the side caught out past the favored side's latest opening tick. Only live battles roll.

## Notes
- **Reviewer: progression** (SPEC §12.3 Combat ↔ Progression; formulas.md § Openings is new). **Architect, please also look:** the save went to v5 (`_migrate_v4_to_v5`, SaveShape `_bestiary`, the DataHealth `bestiary` check) in `game/core`, which the Architect owns. ADR 0023 (proposed) records the decision.
- **Engine:** goes from 951 to 957 lines. Rules live in the new Node-free `BattleOpening`, `BattleRead` and `Bestiary` classes. The controller goes from 994 to 997 lines, with the glue in `BattleBestiary`.
- **Determinism:** tests, capture fixtures and the simulator open normally, so no seed, screenshot or balance band moved. The five battle shots are at rmse 0. `test_battle_vitals` sets `bestiary.roll_openings = false`, because a rolled ambush plays enemy turns before its HP checks.
- **Data:** an appended `read` skills.json row, `read` at the end of Ysolde's skills, loc keys appended, `check_read_openings` appended to validate_data.py. encounters.json is untouched, because the default (roll, or normal when scripted) covers today's rows. That leaves room for the Drownbell work.
- **Gate:** `HYMN_SHOTS=battle_hud_preview,battle_swap_menu,battle_victory,battle_statuses,battle_swell_ring tools/ci_local.sh` rc 0. 1040 Godot tests, 0 failed. Coverage: battle 99.93%, progression 96.52%.
- **Follow-up:** M2-UI-02 (Read panel, bestiary menu, opening banner).

## Review log
