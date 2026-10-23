# 0023 — Save v5: the bestiary log, and rolled battle openings

- **Status:** proposed (the Lead accepts it on merge)
- **Date:** 2026-10-23
- **Roles affected:** Combat, Systems Architect (saves), UI, Progression (review pair), QA
- **Author role:** Combat (M1-CMB-03)

## Context
SPEC §6.1 asks for a Read ability that logs into a bestiary, and for preemptive and ambush openings. The bestiary is persistent state, so it touches the save format that the Architect owns (docs/kb/tech/architecture.md "Saves", "Data tables gate"). Openings add a battle-RNG draw, which would move every seeded turn order that tests, capture fixtures and the balance simulator rely on.

## Options
1. Add `bestiary` as an optional v4 field with no version bump.
2. Bump to save v5 with a frozen v4→v5 migration, a SaveShape rule and a data-tables gate check.
3. For openings: roll inside `BattleEngine.begin()` for every battle.
4. For openings: roll only when the caller asks (`BattleOpening.choose`), and have `begin()` apply whatever `engine.opening` holds.

## Decision
Options 2 and 4.
- **Save v5.** `GameStateData.bestiary` = `{"<enemy id>": {"read": bool, "defeated": whole}}`. Only the facts are saved, never copied stats, so a rebalance cannot leave a stale page. The version bump means a v4 build refuses a v5 save ("saved by a newer build") instead of loading it and dropping the log on its next write. SaveShape checks the field. The data-tables gate has a `bestiary` check on enemies.json. Unknown ids are kept, never pruned.
- **Openings.** Encounters may fix the opening (`"opening"` in encounters.json). Otherwise scripted fights open normally and others roll once on the battle RNG. Only live battles roll (`BattleBestiary`, `persist_progress` on and no fixture). Tests, capture fixtures and the simulator open normally, so no seed, baseline or balance band moves.

## Consequences
- Another branch that also bumps `SAVE_VERSION` (for example M2-ARC-01, which carries Swell gauges) must take v6 and chain after `_migrate_v4_to_v5`.
- A live battle's turn order now depends on one extra draw. Retry replays the same opening, because the seed is the same. Tests that check vitals or HP at the start of a live battle set `BattleBestiary.roll_openings = false`.
- The balance simulator does not model openings yet. When it does, report both bands, since an 11% preemptive chance can shift a close boss fight.
