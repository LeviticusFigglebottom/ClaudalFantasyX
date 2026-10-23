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
- 2026-10-23 progression + architect (review-sweep-L, fresh reviewer): **approve, with should-fixes.** No blockers.
  - **What I read:** the task, combat-4 handoff, ADR 0023 and `git show` 9dc00f2 / 8ec75cf / da81aef / b686218 / be186bc / 4fa7363: battle_opening.gd, battle_read.gd, bestiary.gd, battle_bestiary.gd, the engine and controller hunks, game_state_data / save_shape / save_system / data_health, formulas.md § Openings and the tests.
  - **Checks:** Godot `--filter=` bestiary 18/0 failed, battle_opening 13/0, battle_read 6/0, save 168/0, formulas 26/0, battle_vitals 14/0. validate_data 0/0, tool tests 411 OK, gdlint and gdformat clean. Coverage not re-run: my review changes no code, and the author reported battle 99.93% and progression 96.52%.
  - **Trying to lose data across v4 -> v5** (a scratch test, deleted and not committed): I wrote a full v4 file (flags, both rosters, inventory, currency, play time, lattice, equipment, party_vitals with a status, attuned shrines and respawn), loaded it, logged a Read, saved and reloaded. Every v4 field came back. The log survived the write, and so did `party_vitals` HP. Nothing is lost by v5. The one way to lose the save is a v4 file that already holds a malformed `bestiary`: the migration keeps it as is (save_system.gd:673-677), and SaveShape then reads the whole save as corrupt. v4 builds never wrote the key, so only a hand edit can do that. The test pins it deliberately (test_bestiary_save.gd:65-66). Fine as frozen.
  - **Determinism:** over 200 seeds, two engines with the same seed chose the same opening and the same opening ticks. All three openings occurred. `choose` draws exactly once, before `begin()`'s tick draws (battle_bestiary.gd:44-45, then battle_engine.gd:108-111). Fixed openings draw nothing. Tests, fixtures and the simulator stay on NORMAL. OK.
  - **Formulas:** formulas.md, formulas.gd:52-59 and :213-228, and test_formulas were changed together in 9dc00f2, as required. The worked example (11% / 5% / 84%, lead 241) checks out. The doc is honest that a fast favoured combatant can act twice.
  - **Should-fix:**
    - **S1: ADR 0023:24 says "Retry replays the same opening, because the seed is the same". That is false.** Retry restarts at `seed + 1` (battle_controller.gd:605), so a live Retry rerolls the opening and the tick order. Either correct the ADR line (an append-only note) or keep the seed on Retry. A design call either way: rerolling lets a player retry out of an ambush.
    - **S2: victory credits every enemy in `engine.enemies` (battle_bestiary.gd:74-75), by the combatant id before `#`.** That is right today. But the reveal uses the enemies.json row id (`_enemy_row`, battle_read.gd:41), so one rule should be shared, or the two paths drift if combatant ids change. Also say in the docstring what happens to a foe removed mid-battle.
  - **Nits:** `Bestiary.from_saved` (bestiary.gd:66-79) normalises `defeated` but copies other keys through. That's harmless after SaveShape, but say so in the ADR next to "unknown ids are kept".
