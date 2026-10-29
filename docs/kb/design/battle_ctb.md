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
| `BossMechanics` | Boss rules from data (M2-FP-06): phases, telegraphed charges and weak points, summons, fields, flag-locked skills. See "The Drownbell" below. |
| `SwellInput` | Base of every Swell input (M2-CMB-01): `advance`, `press(button)`, `release(button)`, `cancel`, `result`, `buttons_used`; `create(row)` builds one by kind and `scripted_result(row, quality)` plays one at a fixed quality for the simulator. |
| `SwellChant`, `SwellBrace`, `SwellGlyph` | Asha's verse chant, Toma's tide brace and Ysolde's glyph trace (M2-CMB-01). Node-free; each has its HUD panel since M2-UI-03 (tech/ui.md). |
| `BattleOpening` | Preemptive and ambush openings (M1-CMB-03): which opening an encounter gets (`choose`, one RNG draw when rolled) and the tick shift `begin()` applies. |
| `BattleRead` | What Read reveals (M1-CMB-03). The engine puts `reveal()` on a Read hit as `hit["read"]`. |
| `Bestiary` | The bestiary log over `GameStateData.bestiary` (read flag and defeat count per enemy id; save v5). |
| `BattleHits`, `BattleItemUse`, `BattleAutoTurn`, `BattleSpoils` | Static helpers split out of `BattleEngine` in M2-CMB-03 for the line cap, with no behaviour change: one skill hit on one target (damage, heal, Read, the skill's and the gear's statuses, delay); item use, its party-defeat check and its timeline preview; the attack and target pool of a Berserk or Confused turn; and the victory rewards (XP, lume, drops). The engine keeps every public name as a one-line wrapper and still owns the turn flow, and each helper draws on `engine.rng` in the old order, so a seed plays out exactly as before. |
| `BattleVowbound` | Vowbound summons (M2-CMB-04): the call that stands the party down, the Vowbound's stats from its caller, its Swell finisher, and the party's return. The engine owns one (`engine.vowbound`) and calls it from `summon()`, `dismiss()`, `_check_outcome()` and `_finish()`. See "Vowbound" below. |

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

`TurnEntry` fields: `combatant_id`, `time`, `team`, `skipped` (Stop/Sleep will eat it), `is_preview`, `doom` (Doom countdown shown on that turn, 0 = none; the unit falls after the turn showing 1, so it has no later entries), and `intent` (the telegraphed skill this turn is committed to, &"" otherwise; see "The Drownbell").

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
- **The HUD gate.** `SwellRingView.DRAWN_KINDS` lists the input kinds the HUD can draw (the ring only, for now). A hero whose input is not drawn gets no gauge on the party panel and no Swell row (`SwellRingView.draws`, `draws_hero`), though the engine, the tests and the simulator fill and unleash it. M2-UI-03 added the three panels and listed their kinds, so every hero now has a gauge and a Swell row.
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
- **Kerrid and Liss (M3-C05-06, M3-C06-05, 2026-10-29):** Kerrid's weighted swing is a one-blow brace (hold while the cleaver coils, let go on the count) for The Long Hold (Return Tide's band). Liss's reel-stop is a three-beat ring (one press per reel) for Three-Reel Charge (every foe, power 9, a 1-rank push). Both are data rows on the existing input kinds; the HUD draws them as the brace and the ring with their own help lines. Numbers: formulas.md § Swell. **Not yet:** Pell's call-and-response tiles (Pell is a set-piece entry, not a party member).

## Read, the bestiary and openings (M1-CMB-03)

Numbers are in [formulas.md § Openings](formulas.md).

- **Read** (`read`, SPEC §6.1) is a `support` skill: rank 2, no MP, single foe. Rhen and Ysolde know it. **Rhen (M2-CMB-08):** the vertical slice's party is Rhen, Asha and Toma, so without him the slice could never Read or fill a bestiary page. He is the lamp-diver who reads currents by song (taught by Dace) and appraises every piece of salvage he cuts out, so sizing up a foe is in his trade, and as the always-present protagonist he teaches the command in the first fights. It is the last row of his skills, so it never displaces his Swell or his delay tools. Ysolde keeps it too (her late skills read and exploit weaknesses, ysolde.md). A skill rather than a starting accessory: no equipment category grants a skill today, and an accessory could be unequipped and lose the slice its only Read. The balance simulator never picks Read (it deals nothing), so every band is unchanged. It always lands, rolls nothing, ignores Silence and Reflect (it is not magic) and deals nothing. The hit carries `hit["read"] = BattleRead.reveal(target, row)`: `enemy_id` (the enemies.json id; `""` for a party member), `target_id`, `name_key`, `lore_key`, `level`, `hp`/`max_hp`, `mp`/`max_mp` as they stand, `stats` (the eight battle stats before breaks), `affinities` (`weak`, `resist`, `immune`, `absorb` lists in SPEC element order), `delay_immune` and the current `statuses`.
- **The bestiary log** is `GameStateData.bestiary` (save v5): `{"<enemy id>": {"read": bool, "defeated": n}}`, wrapped in place by `Bestiary`. Only the facts are saved; a bestiary page reads the stats, weaknesses and lore from enemies.json when it is shown, so a rebalance never leaves a stale page. Ids enemies.json no longer lists are kept as saved. The data-tables gate's `bestiary` check (`BattleDB.enemies_problem`) closes saving while enemies.json is torn, missing or empty (architecture.md "Data tables gate").
- **Glue.** `BattleBestiary` (`game/battle/scene/battle_bestiary.gd`) is attached by `BattleController._build_engine` after Swell, before `begin()`. In a live battle (`persist_progress` on, no capture fixture) it rolls the opening and logs into `Game.state.bestiary`; tests and fixtures open normally and log into a scratch dictionary. It logs every Read (`last_reveal` keeps the latest for the HUD), one defeat per foe on victory, and floats two short lines: the read foe's weaknesses ("Weak to Lightning", `HUD_READ_WEAK` with `ELEMENT_*` names) and, on the first turn, the opening's caption over whoever acts first (`HUD_OPENING_PREEMPTIVE` "They have not seen you yet.", `HUD_OPENING_AMBUSH` "They saw you first."). `roll_openings = false` keeps a live battle's opening normal for tests about other rules (test_battle_vitals does this).
- **Openings.** Set `engine.opening` after `setup()` (which resets it to normal) and before `begin()`. Live play uses `BattleOpening.choose(engine)`. The timeline and every preview show the shifted order from the first turn, so the player sees who moves first (pillar 4).
- **Not yet:** a full Read panel and a bestiary menu (request M2-UI-02), openings in the balance simulator (it opens normally, so the bands are unchanged), and equipment abilities that tilt the opening odds.
- **M2-UI-02 (UI, appended):** the opening caption is now the opening banner (`OpeningBanner`, with what the opening means for the order), not a float; a Read of a foe opens the Read panel (`ReadPanel`), which holds the battle until it is closed and so costs no battle time; the out-of-battle bestiary menu is `BestiaryMenu`. Details: tech/ui.md § Read, the bestiary and openings.
- Tests: `tests/unit/test_battle_read.gd`, `test_battle_opening.gd`, `test_bestiary.gd` (log, glue, live controller) and `test_bestiary_save.gd` (v5 round trip, v4 migration, shape, gate).

## Carried vitals (M1-CMB-08)

HP, MP and the carried statuses (`game/data/world/party_rest.json`: Poison, Stone, Zombie) follow the party from one battle to the next, and a save shrine restores them (M1-ARC-06, architecture.md "Saves"). The glue is `game/battle/scene/battle_vitals.gd` (`BattleVitals`). The engine core is unchanged: it only receives a `party_modifier`.

- **In.** A live battle (`BattleController.persist_progress` on, no capture fixture) composes `progress.apply_to`, then the party's equipped gear (`BattleVitals.live_gear`, an `EquipmentEffects` over a copy of `Game.state.equipment`; M2-CMB-07), and then `Game.vitals_modifier()`, so the saved values are clamped to the battle-time maximum. A member with no saved entry starts full. Capture fixtures and tests (`persist_progress` off) never read vitals, so no baseline moves.
- **Out.** After a **victory** or an **escape**, `BattleVitals.send_back` emits `EventBus.battle_party_returned` with every party combatant (active, then reserve). `Game.record_party` saves HP, MP and the carried statuses; every other status ends with the battle. A **defeat** writes nothing back: defeat is a game over, so play resumes from the last save, and the sandbox's Retry replays the same start.
- **A KO'd or petrified member at battle start** (decided here). Fallen members stay fallen between battles until a save shrine's rest or a revive lifts them. When a battle opens:
  1. Each fallen active member trades places with the first living reserve member not already used, in active-slot order and then reserve order. The fallen member waits in the reserve in that member's place. This happens before `begin()`, so it costs no time and the incoming member rolls its opening ticks like everyone else. (Genre convention: the party you walk with is the party that is standing.)
  2. If no living reserve member is left, the fallen member keeps its slot at 0 HP. It takes no turns, and the player can revive it or swap it out on any living member's turn.
  3. If nobody in the party is standing (only possible after a victory where the last foe and the last active member fell together), the active members get up with 1 HP and their stone breaks (`BattleVitals.raise_modifier`). A fight never opens already lost (pillar 4).
- Tests: `tests/unit/test_battle_vitals.gd` (the lineup rule, in and out on a bare engine, and the live controller: carried HP and Poison, a carried KO swapped out, victory write-back with Retry starting from it and a shrine heal clearing it, defeat recording nothing, and fixtures and tests ignoring vitals).

## The Drownbell (M2-FP-06)

The slice boss (vertical_slice.md §5): encounter `drownbell` (scripted, no escape), the id Cutscene B's `<<event start_battle drownbell>>` names. Party Rhen, Asha and Toma, no reserve. Phase 1 is **the Toll**; at 40% HP it becomes **the Flood**. Everything below is data on generic engine rules in `game/battle/boss_mechanics.gd` (`BossMechanics`, static helpers the engine calls at fixed points; headless, all randomness on `engine.rng`), so later bosses reuse them.

**Data shape.**

| Where | Field | Meaning |
|---|---|---|
| `enemies.json` | `phases: [{id, at_hp_pct, name_key?, prompt_key?, skills?, ai?, affinities?, stats?, delay_immune?, field?, spawn?: [enemy ids], remove?: [enemy ids]}]` | Applied in order, once each, at the end of any turn that leaves the enemy alive at or below `at_hp_pct` of max HP (a killing blow skips it). `skills`, `ai` and `affinities` replace; `stats` overrides combat stats (never HP, MP or level); `field` raises a field; `spawn` adds fresh enemies; `remove` fells living ones. Any charge in progress ends. `turn_mod` in the AI counts from the phase's start (`ai_turn_base`). |
| `enemies.json` | `weak_point: {hits, max_delay, name_key}` | While the enemy is charging, every landed **physical** hit from an attacker whose action delay for that skill (`action_delay(agi, rank, speed)`) is at most `max_delay` ticks counts. `hits` of them break the charge. |
| `enemies.json` | `field: "flood"` | This combatant is bound to the field and falls when it clears. |
| `skills.json` | `charge: {skill, turns}` | Telegraph: the user commits to `skill`, which fires on its own acted turn `turns` turns from now (the firing one counted), in place of its AI. Turns lost to Stop/Sleep do not count down. |
| `skills.json` | `summon: enemy id` | Adds one enemy (it first acts a default-rank delay from now; ids keep counting, e.g. `spawn_polyp#4`). |
| `skills.json` | `clears_field: field id` | After the hits, ends that field; every combatant bound to it falls. Refused at no cost (`no_field`) while the field is down. |
| `skills.json` | `requires_flag: story flag` | A party member only knows the skill when the flag is in `BattleEngine.story_flags`. |
| AI | condition `field_active: "flood"`, selector `largest_ally` | The living ally with the highest max HP (adds tending their boss). |

**Engine API.** `BattleEngine.story_flags` (set before `setup()`; the engine never reads `Game`) and `fields` (fields in force). Signals: `phase_changed(enemy, phase_id)`, `combatants_joined(added)`, `charge_started(actor, skill_id, turns)`, `charge_broken(enemy, skill_id)`, `field_cleared(field_id, fallen)`. Hits carry `weak_point_hits` (the count so far) and `charge_broken` (the silenced skill). `rebuild_roster()` is public for spawns.

**Phase 1, the Toll.** The bell (3000 HP, delay-immune, agility 12) opens with *Gathering Toll* (rank 2, `charge: {toll, 2}`) on its first turn and every third turn after. *The Toll* is an all-foes physical hit (power 8) with a 3-rank delay push: when it lands, the whole party slides back and the bell gets its next turns sooner. Its rim is the weak point: 3 hits at 200 ticks or less. In practice that is Rhen (Attack 174 ticks, Quick Hit 116); Toma (300) and Asha (240) only qualify under Haste. Toll is physical, so Toma's Shield Wall (Protect, from the Lattice) halves it, and Challenge (Provoke) pulls the *Hood Slam*s off Asha while Rhen works the rim.

**Phase 2, the Flood** (40% HP). The phase raises the field `flood`, spawns two Spawn-Polyps (180 HP, bound to the field) and swaps the bell's kit: while the field is up it rouses a new polyp whenever fewer than two stand, otherwise it casts *Floodtide* (all foes, magical, power 14; retuned twice after the Swell merges, balance_report.md). The bell's magic is 11 since M2-CMB-07's affordable-party loadout (balance_report.md, 2026-10-24). Each polyp's *Feeding Tide* heals the bell (power 20) each of its turns, more than the party deals, and a killed polyp is replaced. Once the field is gone the bell falls back to *Hood Slam* and an *Undertow Surge* (power 5) every third turn.

**The Ilun stand-in** ([ADR 0026](../decisions/0026-drownbell-ilun-stand-in.md)). The full Vowbound system (SPEC §6.3: the summon replaces the party, with its own HP and Swell) is out of scope for the first playable. Asha gets **Call Ilun** (`call_ilun`, 12 MP, rank 4, magical power 8 to all foes) with `requires_flag: ch03_ilun_bound` (Cutscene B sets it) and `clears_field: flood`: Ilun's *Floodnet* washes the polyps away and ends the field for good. The command is greyed out (and refused at no cost) while no field is up. When Vowbound land, replace the skill with the real summon and keep the field rule as Floodnet's effect. **Done (M2-FP-17):** the stand-in is removed, and Asha calls the real Ilun with M2-UI-05's Call row. His Floodnet carries the field rule.

**The real call (M2-FP-17).** The simulator's Drownbell suite now plays Ilun's real call, not the stand-in (balance_targets.md). The flood was checked against a lone water absorber, because Ilun absorbs water and so do the bell and polyps. Under ADR 0027 A1 as merged (the gauge fills from the *rolled* absorb, so a full-HP Ilun still fills it), the flood phase doesn't stall: Flood Surge fills Ilun's gauge, and Floodnet ends the flood (`flood_call`: 0 timeouts in 1000 fights). **The bell needs no rule that answers a lone Ilun.** One was tried on the m2-slice branch (Hood Slam when every foe absorbs the flood), but it only lowered every band (role_answer 62.7%, smart's p90 72), so it was not kept.

**Timeline honesty (pillar 4).** `TurnEntry.intent` is the skill a turn is already committed to. `CtbTimeline.predict()` marks the charge on the turn it fires, uses that skill's rank for the next delay, and applies its all-foes delay push to every predicted foe (with the diminishing returns of play). A candidate action that would land the breaking hit on the rim (`BossMechanics.would_break`) removes the toll from its preview (pseudo-status `BREAKS_CHARGE`, assumed to land like every preview). Spawns join the timeline the moment they appear. What the engine cannot predict: when a damage threshold will be crossed, and future gathers.

**Foe tempo (M3-CMB-02, ADR 0038).** The timeline predicts each foe's turns at the rank its AI will use, not at `DEFAULT_RANK` (`CtbTimeline.tempo` → `BattleEngine.tempo_rank` → `EnemyAI.predicted_skill`). It applies the predicted skill's delay push to the foe it must hit, so a quick shoal or a slow, pushing limpet sits on the reel where it will really act. `tests/integration/test_battle_timeline_honesty.gd` checks the opening order against the turns played in every Ch1 fight and the tideline, and checks the live HUD and choreography against the engine at two battle speeds.

**How the HUD shows it** (`game/battle/scene/battle_boss_hud.gd`, `BattleBossHud`, a view). The timeline chip of the toll's turn reads "The Toll" in place of the bell's name (`TurnTimeline.intent_labels`; the bell's glyph and the foe colour still say whose turn it is, and the old "The Drownbell · The Toll" ran past the chip, M2-FP-12). The encounter's `prompt_key` and each phase's `prompt_key` are the one tutorial line per phase (vertical_slice.md §5), shown on the help line when the next command menu opens. Float words over the bell: the gathered skill, "Rim 1/3" and so on for each rim hit, "The Drownbell's Rim breaks. The Toll is silenced." for a break, and "The water field clears." over each polyp Floodnet takes. New fighters take the first free enemy slot (`BattleStage.add_enemy`). Live battles pass the story flags in through `BattleBossHud.live_flags` (`Game.get_flag`); tests and capture fixtures pass none. Placeholder stand-ins: `battle_sandbox.json` `drownbell` (a large dark-bronze cylinder with a faint cyan emission) and `spawn_polyp` (small, cyan).

**Status strip (M2-FP-12).** `BattleBossStatus` (`game/battle/scene/battle_boss_status.gd`) is a standing read-out under the target info, top left (`battle_hud.json` `boss_status`). `BattleBossHud` builds it the first time a boss with mechanics is on the field (an enemy with a weak point or phases), refreshes it after every boss signal and every action, hides it at the battle's end, and reuses it on a retry. It reads combatant state and never writes it. The lines are:
- **The boss and its phase**: enemies.json `phase_name_key` for the opening phase ("The Toll"), then each phase row's `name_key` ("The Flood").
- **The telegraph**, in danger: "The Toll comes on its next turn." or "... in 2 of its turns.", from `charge_left`.
- **The weak point's progress**: "Rim 1/3".
- **The field**: enemies.json `field_name_key` and the number of living combatants bound to it ("The flood: 2 bound to it").

The floats stay as accents, but they are off with damage numbers; the strip is never off, so the telegraph reads with every setting (pillar 4). Fight again (`CHOICE_RETRY`) builds a fresh engine: the bell starts over at the Toll, with no polyps and no field, Call Ilun is still known from the live flag, and the opening prompt shows again. Tests: `tests/unit/test_battle_boss_status.gd`.

**Balance** (balance_report.md, `drownbell` suite, loadout `ch03_drownbell` = tier-1 gear, 4 Salt Tonics, 1 Relighting Wick and the flag): naive 0.0%, role answer 79.7%, smart 89.6%, p90 51 actions, 1000 seeds (5000 seeds: 0.0 / 80.3 / 90.4%). The `role_answer` and `smart` policies call Ilun as soon as the field is up (`sim_policies.json` `clear_field_skill`); `smart` heals first when someone is below 45%, which is how most of its losses happen. Tests: `tests/unit/test_battle_boss.gd` (engine, fixture DB), `tests/unit/test_battle_boss_hud.gd` (scene), `tests/integration/test_drownbell_battle.gd` (real data, bands at 200 seeds), `tools/tests/test_boss_validate.py`.
### VFX hook points (for M2-RND-04, the Drownbell's VFX and flood rig)

Everything below is presentation. The boss's logic is in data and `BossMechanics`, and a VFX node only listens; it never writes combat state, just as `BattleBossHud` doesn't. The clean way to wire in is a new view class (`BattleBossVfx`, say) built the same way as `BattleBossHud`. `BattleController._build_engine` creates the HUD with `BattleBossHud.attached(self, engine)`, after `setup()`. One added line there (or in `BattleBossHud.attached`) can attach the VFX view to the same engine. Keep the controller edit to that one line, because it sits at the lint cap and three branches touch it.

| Moment | Engine signal (`game/battle/battle_engine.gd`) | What it carries | Suggested VFX |
|---|---|---|---|
| Toll gathered (telegraph) | `charge_started(actor, skill_id, turns)` | the bell, `&"toll"`, the number of turns until it fires (the timeline marks the firing turn as `TurnEntry.intent`) | Rim glow building; held motes gathering on the hood |
| Toll fires | `action_resolved(result)` with `result.skill_id == &"toll"` | the hits on all three, plus `delay_ranks` pushed | Shockwave ring over the water; the party's stand-ins knocked back |
| Rim hit / rim breaks | `action_resolved` (a weak-point hit counts toward `weak_point.hits`), then `charge_broken(enemy, skill_id)` | the bell and the charge it lost | Cracks per hit; a cyan burst and a dull clank on the break |
| Phase change to the Flood | `phase_changed(enemy, phase_id)`, with `phase_id == &"flood"` | the bell | **Start the flood rise.** haluna.md §2.2: the water goes from −0.7 to +0.6 m over 8 s. The bell submerges. |
| Polyps appear | `combatants_joined(added)` | the new `spawn_polyp` combatants (the HUD has already seated them on the stage: `ctl.stage.fighter(id)`) | Polyps glowing `spawn_wound` cyan below the surface |
| Polyp heals the bell | `action_resolved` with `result.skill_id == &"polyp_mend"` | the heal on the bell | Held motes flowing from the polyp to the bell (**held**: sinking and cyan, never rising) |
| Call Ilun clears the water | `field_cleared(field_id, fallen)` with `field_id == &"flood"`; also `action_resolved` with `skill_id == &"call_ilun"` | the polyps that fell with the field | **Ilun's Floodnet**: **bound** light (steady teal, `glimmer_bound`). Then the water falls back. |
| The bell dies | `battle_finished(&"victory")`, or `action_resolved` with the bell's `hp` at 0 | — | Its motes **slide seaward**; they do not rise (vertical_slice.md §5) |

**Flood height.** Write it through the global `hymn_water_level` (x = water height now, y = datum; see `weathering_tide.gd` and M1-RND-15). There must be **one publisher per scene**. The battle scene (`battle_sandbox.tscn`, inherited by `game/flow/field_battle.tscn`) has no water today, so the flood rig would be that publisher. Restore the global when the battle leaves the tree; `SceneRouter` also resets the water globals before every swap.

**Data and code paths:** `game/data/battle/encounters.json` (`drownbell`), `enemies.json` (`drownbell`, `spawn_polyp`, including `phases`, `weak_point` and `field`), `skills.json` (`toll_gather`, `toll`, `hood_slam`, `flood_surge`, `undertow_surge`, `rouse_polyp`, `polyp_mend`, `call_ilun`), the placeholder stand-ins in `game/data/ui/battle_sandbox.json` (`stand_ins.drownbell` and `stand_ins.spawn_polyp`), and `game/battle/boss_mechanics.gd` and `game/battle/scene/battle_boss_hud.gd`. Tests: `tests/unit/test_battle_boss.gd`, `test_battle_boss_hud.gd` and `tests/integration/test_drownbell_battle.gd`.

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

## Vowbound (M2-CMB-04)

SPEC §6.3: a called Vowbound **replaces the whole party on the field**, with its own HP, abilities and Swell. The engine rules are in `game/battle/battle_vowbound.gd` (`BattleVowbound`; headless, with no random rolls), the rows in `game/data/battle/vowbound.json` (validated by `validate_data.py`'s `check_vowbound`), and the stats in [formulas.md § Vowbound](formulas.md). Each Vowbound's battle identity comes from [vowbound.md](../story/vowbound.md). The first is **Ilun** (caller Asha): *Brine Lash*, *Tidal Ward*, Attack, and the finisher *Floodnet*.

**Engine API.** `engine.vowbound = BattleVowbound.new(BattleVowbound.load_config(), known)` before `begin()`, where `known` is the ids the party has bound. The scene builds it from story flags (`ch03_ilun_bound` → `ilun`), since the engine never reads `Game`. The default instance has no Vowbound.
- `engine.summon(id) -> bool`, with `vowbound.refusal(engine, id)` giving the reason (`not_your_turn`, `vowbound_out`, `unknown_vowbound`, `not_bound`, `not_caller`, `silenced` (the call is a verse), `vowbound_fallen`). `vowbound.callable_ids(engine)` lists the ones the current actor may call now, for the command menu.
- `engine.dismiss() -> bool` and `vowbound.dismiss_refusal(engine)`.
- `vowbound.unleash(engine, targets) -> ActionResult` and `unleash_refusal(engine)` (`swell_not_full`); `vowbound.finisher(c)` names the technique.
- State: `vowbound.summon` (the combatant on the field, team `party`, or null), `vowbound.stood_down` (the active party, in slot order), `vowbound.is_out()`. `engine.find()` still reaches the stood-down party.
- Signals on `engine.vowbound`: `called(vowbound)` and `departed(vowbound, fell)`. `turn_started` fires for the Vowbound when it takes the caller's turn.

**Turn rules** (decided here; pillar 4: the timeline always shows them).
1. **The call.** On the caller's own turn (it must be in control of itself and not Silenced), the whole active party stands down, KO'd members included, and leaves the timeline. The Vowbound takes the current turn at once. The call is still the caller's action, so **the caller's end of turn runs at the call** (ADR 0027 A3): Poison and Regen, the status countdown, Doom, `turns_taken` and `turn_ended` (`turn_ended` for the caller comes before `turn_started` for the Vowbound; the changes are also on `vowbound.call_changes`). Only its next turn waits: when the party comes back, the caller waits a `call_rank` delay (Ilun's is 3), and every other member waits the ticks it had left. A caller that Doom or Poison fells at the call still makes it. If the Vowbound later hands back a party with nobody standing, that is a defeat. The stood-down party is out of reach, and its statuses don't count down.
2. **While it is out.** It is the only party combatant on the field, so every foe's action lands on it. It acts like any party member, with its own skills and MP. The reserve stays in reserve. **Refused while out:** Swap, Escape and items (`vowbound_out`; "a Vowbound uses no items"). Provoke from a stood-down hero ends at once, because the provoker left the field.
3. **Its Swell.** Its gauge fills from HP it loses and from the HP it drinks by absorbing a hit's element: the rolled absorb, so it counts at full HP too (ADR 0027 A1; the hit's `absorbed`; formulas.md § Vowbound). Ilun drinks the tide and turns it into the net: calling him into the flood is the answer, not a hiding place. A full gauge unleashes its finisher, which has no interactive input, needs no MP, is not a learned skill (so `perform()` refuses it) and empties the gauge. Party Swell gauges never see its hits.
4. **Leaving.** (a) **Dismissed** on its own turn: the turn is spent, the party comes back, and the next turn begins. (b) **Fallen** (KO or stone): this is **no defeat**. The party comes back at that moment, and this Vowbound cannot be called again this battle (`vowbound_fallen`). (c) **Victory while out:** the party comes back before `battle_finished`, so the XP credit, the vitals write-back and the result screen all see the party. A Vowbound earns no XP.
5. **Coming back.** A dismissed Vowbound called again in the same battle returns as it left (HP, MP, statuses, gauge). Every battle builds it fresh. Carrying it between battles is a later save task (formulas.md § Not yet specified).

**Why the call costs the caller's rank.** The sandbox probe (`sandbox_reef`, Rhen and Asha active, Toma in reserve, no gear, 1000 seeds) compared a masher who attacks the first living foe with the same masher calling Ilun on Asha's first turn. There, Ilun attacks the crab, Brine Lashes the rest and unleashes Floodnet when full. A plain masher wins 8.7%.

| Ilun (HP at Asha level 5) | Call free (first draft) | **Call at rank 3** |
|---|---|---|
| 1 HP (the mechanic alone) | 28.7% | 16.4% |
| 760 (first-draft stats) | 87.2% | 78.9% |
| 400 | | 50.1% |
| **360 (shipped)** | | **38.9%** (Ilun falls in 99.6%; 0.22 Floodnets a fight) |

A free call gave the masher a free action that soaked an enemy turn, which was worth 20 points by itself. With the rank, the 1 HP call is worth 8. The shipped stats keep a Vowbound strong, but not a second party, against an encounter that was tuned with no Vowbound: a masher lands at 38.9%. **That is above the Swell masher line on starting gear (25%), on purpose, and it is up for review** (ADR 0027): a Vowbound is **one HP pool per battle**, not a gauge that refills every fight (a dismissed Vowbound can be called again as it left; only a fallen one cannot). The Vowbound masher line, accepted as a provisional ceiling, is 40% with no gear. If Ilun needs to be weaker, the levers are his HP scale and `call_rank`. The simulator now has a call rule (M2-CMB-05) and the line is a suite, `sandbox_reef_vowbound` (balance_targets.md): it reproduces the probe exactly (38.9%, 0.22 Floodnets a fight).

**Floodnet and the flood (ADR 0027 A2).** Floodnet is non-elemental (the net binds; it is not a wave) and carries `clears_field: flood`, so it ends the Drownbell's flood through the same path as the `call_ilun` stand-in (`BossMechanics.after_action` → `clear_field`; the polyps fall with it). A Swell finisher is never refused for a missing field: with no field up, Floodnet is still Ilun's finisher and clears nothing. Brine Lash stays water, so Read teaches the player not to lash an absorber.

**Follow-ups.**
- **UI and HUD** (request task M2-UI-05): a Vowbound command on the caller's menu (`callable_ids`), its own command menu (skills, the finisher and Dismiss), the stood-down party shown off the field, and a timeline preview of the call (the caller's `call_rank` delay). Built in M2-UI-05 (tech/ui.md § The Vowbound; ADR 0030): the scene binds a Vowbound from its row's `bound_flag`.
- **The Drownbell** (claude/m2-slice, M2-FP-17): replace `call_ilun` with the real call. Floodnet already carries the field rule (M2-CMB-05). Give the `ch03_drownbell` loadout `"vowbound": ["ilun"]` and re-run the Drownbell bands with the call rule.
- **The simulator** (done, M2-CMB-05): a loadout's `vowbound` binds the Vowbound and `sim_policies.json` `call_vowbound` says when each policy calls (`naive_swell` at once and it stays out; `role_answer` and `smart` while a field is up, and they dismiss it on its first turn after the field is gone). A called Vowbound unleashes its finisher when full (`SimPolicy.call_vowbound`, `unleash_vowbound`).
- Tests: `tests/unit/test_battle_vowbound.gd` (stats, the call and the caller's end of turn, refusals, reach, dismissal and its timing, a fall that is no defeat, no swap, escape or items, the Swell (absorbed HP included) and Floodnet (the flood clear), victory handing the field back, Provoke, and a seeded replay), `test_formulas.gd` (`vowbound_stat`), `tools/tests/test_vowbound_validate.py`, and `test_battle_sim_vowbound.gd` (the sim's call rule).

## Cleanses and reactions (M3-C05-02, the Cinder Matron)
Two small boss hooks in `BossMechanics.after_action`, both data-driven:
- **A skill's `"cleanses": [status ids]`** lifts those statuses off every target the skill landed on, after its hits. The Matron's `recrust` (fired from `recrust_gather`'s two-turn charge, so the timeline shows it) ends Kerrid's armor break.
- **An enemy's `"reactions"`:** `[{elements, from_phase?, cleanses?, statuses?: [{id, duration?}]}]`. A landed hit of one of the `elements` on that enemy, while its phase is `from_phase` (or any phase when unset), lifts `cleanses` off it and adds `statuses`, and the hit records `"reacted": true`. This is the Matron's quench: in the Pour, a water or ice hit re-crusts her at once (Protect and Shell for two turns, and the break is gone).
- `BossMechanics.phase_id(enemy)` names the phase in force. Tests: `tests/unit/test_battle_boss_reactions.gd`.
- **Still to come (combat request M3-C05-06):** the HUD doesn't show a reaction yet, and the battle VFX has no quench hook.

## Encounter rules: forbidden skills and yielding foes (M3-C06-02, the Stillguard Inquisitor)
Ch6's boss is the party's first fight with the Order's own, and nobody dies in it (act1_ch06.md §5). Two data rules carry it, both in `BossMechanics` and `BattleCombatant`:
- **`encounters.json` `"forbidden_skills": {hero id: {"against_tag": tag, "fail_key": loc key}}`.** That hero's offensive skills (`BossMechanics.is_offensive`: a physical or magical skill aimed at foes) are refused on any foe whose `enemies.json` `"tags"` hold the tag. The engine fails the action with `forbidden` before it costs anything, so the turn is not lost.
  - `forbidden_now(engine, actor, skill)` greys a single-target skill while no living foe is a fair target, and a group skill while any forbidden foe stands. The menus grey Attack and the skill rows with it, and the greyed row's help (and the refusal) reads the rule's `fail_key`: "Toma will not strike the Stillguard."
  - Support skills, heals and Provoke are untouched. Ch6 lends Toma his guard with `party_skills` (Stand Fast, a no-cost guard, plus Brace, Challenge and Shield Wall), so he always has a lawful action.
  - The sim follows the same rule. `usable_skills` skips a forbidden skill, and `_basic` falls back to the actor's first lawful skill. `role_answer` (and so `smart`) swaps a hero who may strike no living foe for a reserve member who may, preferring one who answers a living foe.
- **`enemies.json` `"yield_at_hp_pct"`.** It is -1 by default, a fight to a KO. Otherwise, a hit that leaves the foe at or below that share of its max HP ends its fight on its feet: it keeps at least 1 HP, its statuses clear, and `yielded` is set. `is_alive()` is false from then on, so it counts as down for the timeline, targeting and the outcome, and it takes no more damage. Doom, or a field's fall, makes it yield too. The Inquisitor and the hound both use 0: they yield (or run) at what would have been 0 HP.
- **`encounters.json` `"victory_key"`** retitles the victory banner (`BattleMenus.victory_title_key`): "The Inquisitor yields."
- Tests: `tests/unit/test_battle_forbidden_yield.gd` (fixture DB), and the real fight in `tests/integration/test_ch06_thread.gd`.
- **Not yet (combat request M3-C06-05):** the hound's intercept and pounce, a true Smoke field (Darkness every round; played as the phase's every-third-turn Torch the Hulk), Toma's shove counter (the engine has no counters), a first-refusal bark (Toma's "No. Not them." is his first-turn prompt), and Berserk or Confuse auto-turns, which don't check the rule.
