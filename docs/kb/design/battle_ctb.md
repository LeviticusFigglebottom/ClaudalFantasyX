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
| `BattleItemRules` | Static item rules shared by play and previews (who an item may target, fells, downs). `BattleEngine` keeps its `item_*` names as wrappers. Split out in M1-CMB-04 for the line cap. |
| `BattleSwell` | Swell gauges (M1-CMB-04): fill modes from `swell.json`, filled from `action_resolved`, and techniques resolved with their input's result passed in. |
| `SwellTimingRing` | Rhen's Swell input logic (lantern-flicker timing ring). It is Node-free, and the HUD's `SwellRingView` draws it. |
| `SwellInput` | Base of every Swell input (M2-CMB-01): `advance`, `press(button)`, `release(button)`, `cancel`, `result`, `buttons_used`; `create(row)` builds one by kind and `scripted_result(row, quality)` plays one at a fixed quality for the simulator. |
| `SwellChant`, `SwellBrace`, `SwellGlyph` | Asha's verse chant, Toma's tide brace and Ysolde's glyph trace (M2-CMB-01). Node-free; no HUD panel yet (M2-UI-03). |
| `BattleOpening` | Preemptive and ambush openings (M1-CMB-03): which opening an encounter gets (`choose`, one RNG draw when rolled) and the tick shift `begin()` applies. |
| `BattleRead` | What Read reveals (M1-CMB-03). The engine puts `reveal()` on a Read hit as `hit["read"]`. |
| `Bestiary` | The bestiary log over `GameStateData.bestiary` (read flag and defeat count per enemy id; save v5). |

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

| `preview_item(item_id, target, items, count = 16)` | `Array[TurnEntry]` | The order if `current` used that item on `target` (rank, delay push, time statuses, revive rejoin, Zombie felled). |

**Turn reports (M1-CMB-06, for the HUD):**
- `turn_ended(actor, changes)` fires after every acted turn, and the same list is on `ActionResult.end_of_turn`. `changes` is `[{target_id, cause, amount, doom}]`: `poison`, `regen` (negative heals, positive under Zombie), `doom_tick` (`doom` = turns left) or `doom` (fell; `amount` = HP lost). Stop diffing HP.
- `turn_lost(actor, reason, changes)` fires for each Stop/Sleep turn (`reason` &"stop" or &"sleep"), and `changes` carries Doom's tick or fall on that turn.
- `apply_fixture(state)` sets an opening state after `setup()` and before `begin()`: `{id or base id: {hp?, statuses?: [{id, duration}], provoked_by?}}`. HP is clamped to 1..max, and statuses go through `add_status`. **UI switch:** replace the body of `BattleFixture.prepare(engine)` with `engine.apply_fixture(opening)`, and give a provoked combatant a `provoke` status entry as well as `provoked_by` (Provoke needs both).
- **Lifetime gotcha:** a `Callable` does not keep its `RefCounted` object alive. Hold the `EquipmentEffects` (and `LatticeProgress`) instance for the whole battle when you pass `fx.apply_to` / `fx.currency_multiplier`, or the hook silently does nothing.

**Items and rewards (M1-CMB-06):** `use_item(item_id, targets, items: BattleItemSource) -> ActionResult` (hits carry `amount`, `mp_amount`, `revived`, `statuses_removed`, `delay_ticks`, and `ActionResult.item_id` is set). For play, pass `InventoryItemSource.new(item_db, inventory)`; its `usable()` lists the Items menu. Use `item_can_target(action, c)` to filter the cursor. After victory, call `currency_award()` (set `currency_multiplier = equipment_effects.currency_multiplier` first) and `drop_awards()`. For equipment, compose `engine.party_modifier = EquipmentEffects.compose([progress.apply_to, fx.apply_to])`; skill hits then report `element`. Rules: formulas.md § Items, § Equipment in battle, § Rewards.

`TurnEntry` fields: `combatant_id`, `time`, `team`, `skipped` (Stop/Sleep will eat it), `is_preview`, and `doom` (Doom countdown shown on that turn, 0 = none; the unit falls after the turn showing 1, so it has no later entries).

## Data

- `skills.json`: `kind` (physical|magical|heal|support), `power`, `rank` 1–8, `accuracy`, `element`, `target`, `mp_cost`, `magic` (Silence blocks it), optional `statuses: [{id, chance, duration}]`, and `delay_ranks`.
- `statuses.json`: all 21 statuses from SPEC §6.8. `implemented: false` marks the ones the engine doesn't handle yet.
- `enemies.json`: stats, `affinities`, `skills`, `ai` rules, `xp`, `currency`, `drops` (`[{item, chance}]`), optional `delay_immune` (bosses), `lore_key`, and **`role_answer`**: which party member's niche is the "elegant answer" (SPEC §6.1). QA can audit encounter variety from this.
- `characters.json`: base stats and skills (the Lattice will layer on top in M1-PRG-01).
- `encounters.json`: enemy lineup, `scripted` (no escape), optional `opening` (`normal`, `preemptive`, `ambush` or `roll`; § Openings).
- `skills.json` `target`: `single_foe`, `all_foes`, `single_ally`, `all_allies`, `self`, or `all_other_allies` (M2-CMB-02: every living active ally but the user; skills only, never items). `BattleEngine.living_other_allies_of(c)` is its reach, and the target pick, its "All other allies" label and the preview follow it.
- `skills.json` `"read": true` marks a Read skill: kind `support`, target `single_foe` (the validator's `check_read_openings` enforces both, and that every enemy has a `name_key` and `lore_key`).

## Rules worth knowing

- **Swap** costs no time. Replacing a *living* member, the incoming one inherits its slot (`max(slot, now)`), and the current turn if it was theirs. Replacing a *KO'd* member, the incoming one acts `action_delay(agi, DEFAULT_RANK)` after `now`. **Time never runs backwards** (a test asserts it). Reserve members don't occupy the timeline.
- **Targets are validated** against the skill's `target` field: alive, deduplicated, on the right side, and exactly one for single-target skills. An action with no valid target fails with `no_valid_target` and costs nothing (no MP, no turn).
- Defeat means every *active* member is KO'd. Reserves don't prevent a game over (genre convention). Revisit in M1-CMB-01 review.
- Enemy actions that fail on bad data (for example, not enough MP) burn the enemy's turn instead of stalling the battle.
- **Auto turns.** Berserk and Confuse take control away on either side. `is_party_turn()` is false for such a turn and `is_auto_turn()` is true; the UI loop treats it like an enemy turn and calls `run_enemy_turn()`, which plays it and returns an `ActionResult` with `auto_reason` set (`berserk` or `confuse`). `perform()` refuses with `auto_turn`. Use `is_player_side_turn()` for "is the actor one of ours".
- **Provoke** forces single-foe targets. `forced_target(actor, skill_id)` returns the provoker (or null), so the target cursor can lock onto it; `perform()` rejects other targets with `provoked` at no cost.
- **Reflect** is deterministic: `reflect_recipient(actor, target, skill_row)` tells the UI where a spell will land, and `preview()` already uses it. Hits that bounced carry `reflected_from`.
- **Petrify** counts as KO everywhere (`is_alive()` is false). `BattleCombatant.is_petrified()` lets the UI draw stone instead of a KO.

## Swell (M1-CMB-04)

The rules and numbers are in [formulas.md § Swell](formulas.md); the data is in `game/data/battle/swell.json`, which `check_swell` in validate_data.py checks.

- **State and rules.** The gauge state lives on `BattleCombatant` (`swell` 0..100, `swell_mode`). `BattleSwell` holds the rules. Create it with `BattleSwell.new(BattleSwell.load_config())` and call `attach(engine)` after `setup()` and `apply_fixture()`. Hold the instance for the whole battle, because a signal connection does not keep it alive. Only heroes with a `heroes` row get a mode, and only they get a gauge on the HUD.
- **Filling.** Gauges fill only from `action_resolved` hits, so nothing in the engine core calls into Swell. A technique feeds no gauge.
- **Engine hook.** `BattleEngine.perform_row(skill_id, row, targets)` plays a skill row the actor has not learned and pays no MP for. Otherwise it applies `perform()`'s checks: turn, Silence, targets, Provoke, Reflect, rank. `BattleSwell.perform(technique, targets, input_result)` gates the technique on a full gauge, scales the row's power by the input bonus (a copy; the table row is never changed), calls `perform_row`, and empties the gauge on success.
- **Inputs are outside the engine.** `SwellTimingRing` (Node-free, `advance` / `press` / `cancel`) produces `{cancelled, grades}`. Tests and the simulator pass that dictionary straight to `perform()`. In the scene, `BattleController` shows **Swell** on the root menu under Attack while the actor is ready. The flow is Swell page → target pick → ring (`STATE_SWELL_INPUT`, advanced by `tick()` at real time, never scaled by pacing) → `unleash()`. Cancelling the ring returns to the pick, and cancelling the pick returns to the Swell page.
- **Fixtures.** `apply_fixture` takes `swell` (clamped to 0..100). The `swell_ring` capture fixture opens with Rhen full.
- **Unlocks (M2-CMB-01).** `swell.json` `unlocks` rows count events as gauges fill (`BattleSwell._count`, from the same `_gain` calls) and call `unlock_mode()` at their count; the numbers are in formulas.md § Swell. The party-wide record (unlocked modes, counts) is plain data on `BattleSwell` (`load_saved`, `to_saved`), and ids swell.json no longer knows are kept as loaded. `attach()` keeps a carried mode only while it is unlocked, else the hero falls back to the default mode.
- **The other heroes' inputs (M2-CMB-01).** Every hero has a Swell: Rhen's `timing_ring`, Asha's `chant`, Toma's `brace`, Ysolde's `glyph` (formulas.md § Swell; each a `SwellInput` subclass with its own grade names, all worth +45% at good and +90% perfect). `BattleSwell.bonus_pct` counts at most `SwellInput.grade_count()` grades. The controller builds any kind through `SwellInput.create`, `SwellRingClock` drives any `SwellInput`, and `SwellInputKeys` feeds it ui_accept and the four directions (press and release) for the buttons it uses (`buttons_used`), so an event the input ignores keeps its usual meaning.
- **The HUD gate.** `SwellRingView.DRAWN_KINDS` lists the input kinds the HUD can draw (the ring only, for now). A hero whose input is not drawn gets no gauge on the party panel and no Swell row (`SwellRingView.draws`, `draws_hero`), though the engine, the tests and the simulator fill and unleash it. M2-UI-03 adds the three panels and lists their kinds, which turns the gauges on. No screenshot changed.
- **API for the Swell mode menu (M2-UI-01).**

  | Call | Returns | Use |
  |---|---|---|
  | `swell.mode_rows(c)` | `Array[Dictionary]` `{id, name_key, desc_key, trigger, current}` | In battle: `c`'s choosable modes in data order (empty for no Swell). |
  | `swell.set_mode(c, mode)` | `bool` | In battle: choose; refused for a locked mode or no Swell. The gauge keeps its points. |
  | `swell.unlocked` | `Array[StringName]` | Every choosable mode. |
  | `swell.progress_toward(mode)` | `{count, need}` | How far a locked mode is (`need` 0: no rule unlocks it). |
  | `swell.mode_unlocked` | signal `(mode)` | Play just unlocked a mode (a float or toast; not fired when a save is loaded). |
  | `BattleSwellCarry.mode_rows(cid, state = Game.state)` | as `mode_rows` | Out of battle: hero `cid`'s choosable modes from the saved record, `current` = its saved mode. |
  | `BattleSwellCarry.set_mode(cid, mode, state = Game.state)` | `bool` | Out of battle: saves the choice into `party_vitals` (refused for a locked mode or a hero with no Swell). |
  | `BattleSwellCarry.rules(state = Game.state)` | `BattleSwell` | The rules with the saved record loaded (`unlocked`, `progress_toward`). |

  The controller's live `BattleSwell` is `ctl.swell`; a mode chosen there is carried out of the battle with the gauge.
- **Simulator (M2-CMB-01).** `BattleSim.swell_quality` (targets.json `swell`, `--swell`) attaches a `BattleSwell`, and every policy but `naive` unleashes a full gauge first with `SwellInput.scripted_result` (balance_targets.md). The sandbox suites play at `good`, and every band holds at every quality (balance_report.md, 2026-10-23).
- **The masher's Swell (M2-NIT-03).** The report-only `naive_swell` policy (`SimPolicyNaiveSwell`) is `naive` plus the Swell row. Every report shows it next to `naive`, with decision lines at 25% and 45% (balance_targets.md; 35% and 50% before M2-CMB-02). A single-foe technique goes to the policy's focus foe (`SimPolicy.swell_focus`). `role_answer` and `smart` make the free swap to the answer before they unleash.
- **Why Shallows Verse is power 4 (M2-NIT-03; it was 12).** Ballast fills only after about 83% of max HP is lost, so a hero's gauge is full when that hero is nearly down. A party heal there is a second life for the singer, and at power 12 (391 HP per ally at good) it was the one Swell a masher could not lose with (37.9%). The fix keeps the shape, a free song for the whole party, and moves the payoff into the chant. At miss and good the Verse heals less than a Chorus Mend (92 and 115 against 138 from Asha). Only a perfect chant beats it (161), and it still saves the 14 MP and a rank. The Ballast rate was rejected as the lever: it is a cliff (at 100 nobody's gauge fills in a fight), it costs every hero's Swell, and carried gauges would undo it in play. The rest of the masher's 32% is that second-life loop, which only a structural change removes: a Verse that skips the singer, or Asha filling from her allies' hurt. Numbers and sweeps: balance_report.md, 2026-10-23 M2-NIT-03.
- **Why the Verse skips the singer (M2-CMB-02).** Shallows Verse targets `all_other_allies`: every living active ally but Asha. That ends the second-life loop at its root. Her Ballast fills when she is nearly down, and the song can no longer save her: it saves the others. The masher drops from 32.1% to 23.8% (39.1% on tier-1 gear), and every band holds at miss, good and perfect. The power stays at 4, so the chant still decides whether the song beats a Chorus Mend for each ally. We prototyped the other option, Asha's default mode filling from her allies' hurt (a per-hero Tether), and rejected it. At Tether's rate of 60 her gauge never fills in a sandbox fight, so her Swell disappears. At 100 it still never fires for a masher. At the 120 needed for it to fire, the masher is back at 25.7%, and the loop just moves to Rhen, who is the one nearly down when her gauge fills. That option also touches saves, unlocks and the mode menu. With nobody else standing, the Verse has no target: `BattleSwell.perform` refuses it at no cost, and the Swell page greys it out. A full gauge waits, and it carries into the next fight. In the sandbox's two-member party the Verse heals Rhen alone. In a three-member party it heals two. Sweeps: balance_report.md, 2026-10-23 M2-CMB-02.
- **Not yet:** HUD panels for the chant, brace and glyph, their grade words, and a float for `mode_unlocked` (M2-UI-03); a mode menu and timing assist (M2-UI-01); Swell for Kerrid, Liss and Pell (not in characters.json yet: the character sheets suggest a weighted swing, a reel-stop and call-and-response tiles).

## Read, the bestiary and openings (M1-CMB-03)

Numbers are in [formulas.md § Openings](formulas.md).

- **Read** (`read`, SPEC §6.1) is a `support` skill: rank 2, no MP, single foe. Ysolde knows it (Asha's tutor reads what she faces), so a fight Rhen and Asha open asks for a swap to read. It always lands, rolls nothing, ignores Silence and Reflect (it is not magic) and deals nothing. The hit carries `hit["read"] = BattleRead.reveal(target, row)`: `enemy_id` (the enemies.json id; `""` for a party member), `target_id`, `name_key`, `lore_key`, `level`, `hp`/`max_hp`, `mp`/`max_mp` as they stand, `stats` (the eight battle stats before breaks), `affinities` (`weak`, `resist`, `immune`, `absorb` lists in SPEC element order), `delay_immune` and the current `statuses`.
- **The bestiary log** is `GameStateData.bestiary` (save v5): `{"<enemy id>": {"read": bool, "defeated": n}}`, wrapped in place by `Bestiary`. Only the facts are saved; a bestiary page reads the stats, weaknesses and lore from enemies.json when it is shown, so a rebalance never leaves a stale page. Ids enemies.json no longer lists are kept as saved. The data-tables gate's `bestiary` check (`BattleDB.enemies_problem`) closes saving while enemies.json is torn, missing or empty (architecture.md "Data tables gate").
- **Glue.** `BattleBestiary` (`game/battle/scene/battle_bestiary.gd`) is attached by `BattleController._build_engine` after Swell, before `begin()`. In a live battle (`persist_progress` on, no capture fixture) it rolls the opening and logs into `Game.state.bestiary`; tests and fixtures open normally and log into a scratch dictionary. It logs every Read (`last_reveal` keeps the latest for the HUD), one defeat per foe on victory, and floats two short lines: the read foe's weaknesses ("Weak to Lightning", `HUD_READ_WEAK` with `ELEMENT_*` names) and, on the first turn, the opening's caption over whoever acts first (`HUD_OPENING_PREEMPTIVE` "They have not seen you yet.", `HUD_OPENING_AMBUSH` "They saw you first."). `roll_openings = false` keeps a live battle's opening normal for tests about other rules (test_battle_vitals does this).
- **Openings.** Set `engine.opening` after `setup()` (which resets it to normal) and before `begin()`. Live play uses `BattleOpening.choose(engine)`. The timeline and every preview show the shifted order from the first turn, so the player sees who moves first (pillar 4).
- **Not yet:** a full Read panel and a bestiary menu (request M2-UI-02), openings in the balance simulator (it opens normally, so the bands are unchanged), and equipment abilities that tilt the opening odds.
- **M2-UI-02 (UI, appended):** the opening caption is now the opening banner (`OpeningBanner`, with what the opening means for the order), not a float; a Read of a foe opens the Read panel (`ReadPanel`), which holds the battle until it is closed and so costs no battle time; the out-of-battle bestiary menu is `BestiaryMenu`. Details: tech/ui.md § Read, the bestiary and openings.
- Tests: `tests/unit/test_battle_read.gd`, `test_battle_opening.gd`, `test_bestiary.gd` (log, glue, live controller) and `test_bestiary_save.gd` (v5 round trip, v4 migration, shape, gate).

## Carried vitals (M1-CMB-08)

HP, MP and the carried statuses (`game/data/world/party_rest.json`: Poison, Stone, Zombie) follow the party from one battle to the next, and a save shrine restores them (M1-ARC-06, architecture.md "Saves"). The glue is `game/battle/scene/battle_vitals.gd` (`BattleVitals`). The engine core is unchanged: it only receives a `party_modifier`.

- **In.** A live battle (`BattleController.persist_progress` on, no capture fixture) composes `progress.apply_to` and then `Game.vitals_modifier()`, so the saved values are clamped to the battle-time maximum. A member with no saved entry starts full. Capture fixtures and tests (`persist_progress` off) never read vitals, so no baseline moves.
- **Out.** After a **victory** or an **escape**, `BattleVitals.send_back` emits `EventBus.battle_party_returned` with every party combatant (active, then reserve). `Game.record_party` saves HP, MP and the carried statuses; every other status ends with the battle. A **defeat** writes nothing back: defeat is a game over, so play resumes from the last save, and the sandbox's Retry replays the same start.
- **A KO'd or petrified member at battle start** (decided here). Fallen members stay fallen between battles until a save shrine's rest or a revive lifts them. When a battle opens:
  1. Each fallen active member trades places with the first living reserve member not already used, in active-slot order and then reserve order. The fallen member waits in the reserve in that member's place. This happens before `begin()`, so it costs no time and the incoming member rolls its opening ticks like everyone else. (Genre convention: the party you walk with is the party that is standing.)
  2. If no living reserve member is left, the fallen member keeps its slot at 0 HP. It takes no turns, and the player can revive it or swap it out on any living member's turn.
  3. If nobody in the party is standing (only possible after a victory where the last foe and the last active member fell together), the active members get up with 1 HP and their stone breaks (`BattleVitals.raise_modifier`). A fight never opens already lost (pillar 4).
- Tests: `tests/unit/test_battle_vitals.gd` (the lineup rule, in and out on a bare engine, and the live controller: carried HP and Poison, a carried KO swapped out, victory write-back with Retry starting from it and a shrine heal clearing it, defeat recording nothing, and fixtures and tests ignoring vitals).

## Carried Swell (M2-ARC-01)

Swell follows the party as HP and MP do (save v6; architecture.md "Save v6"). The glue is `game/battle/scene/battle_swell_carry.gd` (`BattleSwellCarry`) and `BattleVitals`; the engine core only gained the plain-data record on `BattleSwell`.

- **Gauges and modes** ride on the combatants. In: `Game.vitals_modifier()` sets the saved `swell` (clamped to 0..100) and `swell_mode` at setup. Out: after a victory or an escape, `BattleVitals.send_back(engine, swell)` emits `EventBus.battle_party_returned`, and `Game.record_party` keeps a gauge above 0 and a mode other than swell.json's default in the member's `party_vitals` entry. A **defeat writes nothing**.
- **The record** (unlocked modes and unlock counts, `GameStateData.swell`). In: `BattleSwellCarry.attach(swell, engine, carry)` loads it before `attach()`. Out: `send_back` also emits `EventBus.battle_swell_returned(swell.to_saved())`, and `Game.record_swell` keeps it (not while swell.json is broken). **Both halves refuse alike (M2-NIT-03).** While swell.json is broken, `Game.record_party` still writes HP, MP and statuses, but every member keeps its saved gauge and mode. A battle that ran without its Swell rules records no Swell at all. The DataHealth gate closes saving meanwhile. `test_swell_save.gd` covers this and the escape write-back.
- **A shrine's rest keeps gauges and modes** (decided here, the combat default): it fills HP and MP and cures, and a gauge built in battle is still there for the next one.
- Capture fixtures and tests (`persist_progress` off) read and write none of it, so no baseline moves.
- Tests: `tests/unit/test_swell_save.gd` (state, record, migration, shape, gate, field API, live controller: victory carries, defeat and tests do not).

## Adding a status
1. Add it to `statuses.json` (it must be in the SPEC set; the validator enforces this).
2. Implement its effect in `BattleCombatant` (stat modifier) or `BattleEngine` (behaviour), and set `implemented: true`.
3. If it changes time, teach `CtbTimeline.predict()` so previews stay honest (pillar 4): add it to `TIMED_STATUSES` (counts down per own turn) or `PREVIEW_STATUSES` (a candidate action inflicting it changes the preview), and mirror its effect in the `_sim_*` helpers.
4. Add tests, and update formulas.md if a number is involved.

## Adding an AI condition or target selector
Extend `EnemyAI._conditions_hold` / `select_targets`, add the name to `AI_CONDITIONS` / `AI_TARGETS` in `tools/validate_data.py`, and add a test.
