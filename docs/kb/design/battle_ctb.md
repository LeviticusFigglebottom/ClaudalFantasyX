# Battle System (CTB): Architecture and How to Extend

Owner: Combat Designer-Engineer. Formulas: [formulas.md](formulas.md).

## Pieces (`game/battle/`)

| Class | Role |
|---|---|
| `Formulas` | Static, pure formula functions plus constants. |
| `BattleCombatant` | Runtime state of one fighter: stats, HP/MP, statuses, `next_time`. |
| `CtbTimeline` | Picks the next actor; `predict()` returns `TurnEntry[]` for the timeline UI, optionally previewing a candidate action's rank or delay. |
| `BattleEngine` | Orchestrates a battle: `setup → begin → perform/swap/escape/run_enemy_turn` until `outcome`. Signals: `turn_started`, `action_resolved`, `battle_finished`. |
| `EnemyAI` | Data-driven rule evaluation (conditions → weighted picks → target selectors). |
| `BattleDB` | Loads and indexes `game/data/battle/*.json`; `from_tables()` for test fixtures. |
| `ActionResult`, `TurnEntry` | Value objects for UI and VFX glue. |

**Headless and deterministic:** no Nodes, no scene access, and all randomness through `engine.rng` (seeded in `setup`). The battle *scene* (UI, cameras, VFX) listens to the engine's signals and never mutates combat state directly.

## Data

- `skills.json`: `kind` (physical|magical|heal|support), `power`, `rank` 1–8, `accuracy`, `element`, `target`, `mp_cost`, `magic` (Silence blocks it), optional `statuses: [{id, chance, duration}]`, and `delay_ranks`.
- `statuses.json`: all 21 statuses from SPEC §6.8. `implemented: false` marks the ones the engine doesn't handle yet.
- `enemies.json`: stats, `affinities`, `skills`, `ai` rules, `xp`, `lore_key`, and **`role_answer`**: which party member's niche is the "elegant answer" (SPEC §6.1). QA can audit encounter variety from this.
- `characters.json`: base stats and skills (the Lattice will layer on top in M1-PRG-01).
- `encounters.json`: enemy lineup, `scripted` (no escape).

## Rules worth knowing

- **Swap** costs no time. The incoming member inherits the outgoing member's `next_time`, and the current turn if it was theirs. Reserve members don't occupy the timeline.
- Defeat means every *active* member is KO'd. Reserves don't prevent a game over (genre convention). Revisit in M1-CMB-01 review.
- Enemy actions that fail on bad data (for example, not enough MP) burn the enemy's turn instead of stalling the battle.

## Adding a status
1. Add it to `statuses.json` (it must be in the SPEC set; the validator enforces this).
2. Implement its effect in `BattleCombatant` (stat modifier) or `BattleEngine` (behaviour), and set `implemented: true`.
3. If it changes time, teach `CtbTimeline.predict()` so previews stay honest (pillar 4).
4. Add tests, and update formulas.md if a number is involved.

## Adding an AI condition or target selector
Extend `EnemyAI._conditions_hold` / `select_targets`, add the name to `AI_CONDITIONS` / `AI_TARGETS` in `tools/validate_data.py`, and add a test.
