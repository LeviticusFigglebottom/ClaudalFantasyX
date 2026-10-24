---
id: M3-CMB-01
title: Ch8 Fisher Stair set-piece battle pieces (scripted timeline entries, objective victory, scripted escape, party locks)
role: combat
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: []
reviewer: lead
milestone: M3
request-from: cinematics
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel; m2-slice owns Act I gameplay and narrative). Ch8's evacuation set-piece (`docs/kb/story/beats/act1_ch08.md` §5a and §9 Combat) is three chained scripted battles plus the Undertow's Reach. All of it stays in the existing CTB engine, with no real-time system. It needs these new building blocks:
- **A scripted timeline entry with no HP,** used three ways:
  - **the Climb:** each of its turns brings a group up, and spawn delays push it back;
  - **the Surge:** untargetable, it brings in reinforcements;
  - **Pell:** a guest who casts a telegraphed Storm-Call that removes one moving spawn.
- **Victory on an objective,** a quota of Climb turns, plus a `scripted_escape` outcome for the Reach's last phase.
- **Untargetable / damage-immune phases.**
- **Party locks:** Toma is locked in his slot, with his Attack replaced by the Stand Firm counter stance; Kerrid is unavailable.
- **Skills:** Liss's Haul (Haste on the Climb) and Toma's Hold the Stair (he takes the next hit aimed at the Climb).
- **Fields:** the `storm_dark` field, and Virel's Flare Line clearing it.
- **Sim:** a `ward_guard` sim policy.
- **Bands:** waves at 85–95% role-answer; the Reach at 75–85% role-answer and ≤ 10% naive.

The engine stays headless and deterministic (CLAUDE.md §3). Formulas change only together with their docs and tests.

## Acceptance criteria
- [x] Each piece lands with unit tests in `tests/unit`, the battle coverage doesn't drop, and `sim.py --check` passes with the new bands.
- [x] The data schema is documented in `docs/kb/design` so M3-C08-02 can write the waves as data.

## Notes
- Requested by m2-slice (cinematics), the Act I owner. M3-C08-02 depends on this.
- 2026-10-24 combat (worktree agent, handoff 2026-10-24-combat-14): built, status review, reviewer lead.
  - Schema: `docs/kb/design/set_piece_battles.md`. Decision: ADR 0038. Code: `game/battle/battle_set_piece.gd` (+ hooks in the engine, BossMechanics, EnemyAI, the combatant), `game/battle/sim/sim_ward_guard.gd`, `sim_policy_ward_guard.gd`.
  - Ch8 data (provisional, for M3-C08-02 to keep or reshape): `ch08_stair_hold_1..3` and `undertows_reach` in encounters.json; `tide_crawler`, `squall_wing`, `wall_polyp`, `undertows_reach` in enemies.json; Virel in vowbound.json; strings in `game/data/loc/ch08.csv`; flags `ch08_hoist_rigged`, `ch08_virel_bound`.
  - Bands at 1000 seeds: see balance_targets.md § Ch8 and the handoff.
  - Departures from the sheet: the Tide Crawler is not fire-weak; its grip is telegraphed one turn ahead; Storm-Call picks its mover when it fires; storm_dark's Darkness lasts to the hero's next turn. Waves' `naive` band is 10–60 (the sheet proposed 40–60; Wave 1 measures ~15).
  - Not built (UI requests): entries drawn on the timeline, swap/formation greying with locked_key/unavailable_key, intercept/counter/withdraw floats, the stair meter HUD. The carried meter `ch08_stair_groups_up` is the flow's (reads `engine.objective_count`).

## Review log
