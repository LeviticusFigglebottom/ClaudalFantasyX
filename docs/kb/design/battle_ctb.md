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

## Sandbox balance (M1 target bands)

The balancing simulator (`game/battle/sim/`, `tools/balance/sim.py`; see [balance_targets.md](balance_targets.md)) owns the bands, and [balance_report.md](balance_report.md) has the latest numbers and the tuning log. `tests/integration/test_sandbox_battle.gd` asserts them on the real `sandbox_reef` data on every run.

| Policy | Band | Measured 2026-10-22 (1000 seeds, after the M1-CMB-05 softening) |
|---|---|---|
| Naive: attack the first living foe | 5–15% wins (test: ≥ 1% and ≤ 20% at 200 seeds) | 8.7% (was 0%) |
| Attack the lowest-HP foe | report only | 82.8% (was 58.8%) |
| Role answer: swap in each foe's `role_answer` | ≥ 85% wins | 96.8% (was 86.5%) |
| Swap Toma in for Asha, then attack the lowest-HP foe (legacy test policy) | ≥ 70% wins | 95.6% (was 87.8%) |

Swapping remains the elegant answer (SPEC §6.1), but a naive party now wins about one fight in eleven instead of never.

## Timeline API for the UI

| Call | Returns | Use |
|---|---|---|
| `preview(count = 16)` | `Array[TurnEntry]` | The order as it stands, starting with the current actor. |
| `preview(skill_id, target, count)` | `Array[TurnEntry]` | The order if `current` used `skill_id` on `target` (rank, delay push, time statuses, Petrify, Reflect bounce). The previewed actor's next turn has `is_preview = true`. |
| `preview_swap(out_id, in_id, count = 16)` | `Array[TurnEntry]` | The order **exactly as `preview()` would show it right after `swap(out_id, in_id)`**, with no state change. Empty when `swap()` would refuse (not a player turn, unknown ids, or a fallen reserve). |

`preview_swap` uses the same rule as `swap()` (one shared helper, `_swap_in_time`): the entrant takes a living leaver's slot (`max(slot, now)`) or, replacing a KO'd/petrified member, waits `action_delay(agi, DEFAULT_RANK, speed)` from now. The entrant keeps any statuses it had (for example Haste from earlier field time). It sits in the leaver's party slot, so ties break the same way they will after the swap. Tests in `tests/unit/test_battle_engine.gd` check it against `preview()` after the real swap *and* against the turns actually played.

**Hook-up for the Swap menu (UI stream, not done here):** in `BattleController`, `STATE_SWAP_OUT` already knows `_swap_in_id` and the highlighted active member, so `_show_pick()` can pass `engine.preview_swap(_candidates[_target_index], _swap_in_id, CtbTimeline.PREVIEW_LENGTH - 1)` as the `preview` argument of `_show_timeline(MODE_PREVIEW, ...)` instead of an empty preview. When the leaver is the current actor, the first entry is the entrant at `now`.

`TurnEntry` fields: `combatant_id`, `time`, `team`, `skipped` (Stop/Sleep will eat it), `is_preview`, and `doom` (Doom countdown shown on that turn, 0 = none; the unit falls after the turn showing 1, so it has no later entries).

## Data

- `skills.json`: `kind` (physical|magical|heal|support), `power`, `rank` 1–8, `accuracy`, `element`, `target`, `mp_cost`, `magic` (Silence blocks it), optional `statuses: [{id, chance, duration}]`, and `delay_ranks`.
- `statuses.json`: all 21 statuses from SPEC §6.8. `implemented: false` marks the ones the engine doesn't handle yet.
- `enemies.json`: stats, `affinities`, `skills`, `ai` rules, `xp`, `lore_key`, and **`role_answer`**: which party member's niche is the "elegant answer" (SPEC §6.1). QA can audit encounter variety from this.
- `characters.json`: base stats and skills (the Lattice will layer on top in M1-PRG-01).
- `encounters.json`: enemy lineup, `scripted` (no escape).

## Rules worth knowing

- **Swap** costs no time. Replacing a *living* member, the incoming one inherits its slot (`max(slot, now)`), and the current turn if it was theirs. Replacing a *KO'd* member, the incoming one acts `action_delay(agi, DEFAULT_RANK)` after `now`. **Time never runs backwards** (a test asserts it). Reserve members don't occupy the timeline.
- **Targets are validated** against the skill's `target` field: alive, deduplicated, on the right side, and exactly one for single-target skills. An action with no valid target fails with `no_valid_target` and costs nothing (no MP, no turn).
- Defeat means every *active* member is KO'd. Reserves don't prevent a game over (genre convention). Revisit in M1-CMB-01 review.
- Enemy actions that fail on bad data (for example, not enough MP) burn the enemy's turn instead of stalling the battle.
- **Auto turns.** Berserk and Confuse take control away on either side. `is_party_turn()` is false for such a turn and `is_auto_turn()` is true; the UI loop treats it like an enemy turn and calls `run_enemy_turn()`, which plays it and returns an `ActionResult` with `auto_reason` set (`berserk` or `confuse`). `perform()` refuses with `auto_turn`. Use `is_player_side_turn()` for "is the actor one of ours".
- **Provoke** forces single-foe targets. `forced_target(actor, skill_id)` returns the provoker (or null), so the target cursor can lock onto it; `perform()` rejects other targets with `provoked` at no cost.
- **Reflect** is deterministic: `reflect_recipient(actor, target, skill_row)` tells the UI where a spell will land, and `preview()` already uses it. Hits that bounced carry `reflected_from`.
- **Petrify** counts as KO everywhere (`is_alive()` is false). `BattleCombatant.is_petrified()` lets the UI draw stone instead of a KO.

## Adding a status
1. Add it to `statuses.json` (it must be in the SPEC set; the validator enforces this).
2. Implement its effect in `BattleCombatant` (stat modifier) or `BattleEngine` (behaviour), and set `implemented: true`.
3. If it changes time, teach `CtbTimeline.predict()` so previews stay honest (pillar 4): add it to `TIMED_STATUSES` (counts down per own turn) or `PREVIEW_STATUSES` (a candidate action inflicting it changes the preview), and mirror its effect in the `_sim_*` helpers.
4. Add tests, and update formulas.md if a number is involved.

## Adding an AI condition or target selector
Extend `EnemyAI._conditions_hold` / `select_targets`, add the name to `AI_CONDITIONS` / `AI_TARGETS` in `tools/validate_data.py`, and add a test.
