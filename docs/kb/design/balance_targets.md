# Balance Targets

Owner: Combat. SPEC §6.9: every encounter is simulated over thousands of seeds, and any boss whose expected party-loss rate falls outside its band is rebalanced before release. The machine-readable copy of the bands is [`tools/balance/targets.json`](../../../tools/balance/targets.json); change both together. Results are in [balance_report.md](balance_report.md).

## How to run

```bash
python3 tools/balance/sim.py                 # every suite, 1000 seeds, rewrites balance_report.md
python3 tools/balance/sim.py --seeds 200 --suite sandbox_reef --check   # quick, exit 1 on a miss
```

`sim.py` calls `godot --headless -s res://tools/balance/sim_main.gd` (a thin wrapper around the GDScript runner `BattleSim`, whose `run_cli()` holds the logic), writes per-seed and summary CSVs to `tools/balance/out/` (gitignored), and rewrites the table at the top of the report, keeping the hand-written tuning log below the `<!-- tuning-log -->` marker. Seeds are `1..N`, so every number is reproducible. `tests/integration/test_sandbox_battle.gd` asserts the sandbox bands at 200 seeds on every CI run.

## Party policies (`game/battle/sim/`)

Each policy is a `SimPolicy` subclass. Policies use only the engine's public API and never touch `engine.rng`, and every turn ends (a fallback basic attack guarantees it). Tunables are in `game/data/battle/sim_policies.json`.

| Policy | What it models | Rule |
|---|---|---|
| `naive` | A player mashing Attack | `attack` on the first living foe. Never swaps, and never opens Swell (mashing confirm picks the top row). |
| `lowest_hp` | Focus fire, no swaps | `attack` on the living foe with the least HP. |
| `role_answer` | The elegant answer (SPEC §6.1) | If the actor answers a living foe (`enemies.json` `role_answer`), it takes the weakest such foe. Otherwise the focus is the weakest foe, and if that foe's answer is in reserve it swaps in for the actor (free) and takes the turn. An answerer opens with a Break skill its foe lacks, then uses its best expected damage per rank (MP permitting). |
| `smart` | A careful player | `role_answer`, plus: replace a KO'd or petrified active member at once (preferring a reserve who answers a living foe); a healer heals the most hurt ally below `heal_below_pct` (45%) of max HP; a healer won't swap out while an ally is below `keep_healer_below_pct` (70%). |

"Expected damage" is the real formula at mean variance (100%), without crits, times the hit chance, and 0 for magic the target would Reflect. It is deterministic.

**Swell (M2-CMB-01).** A suite's `swell` (targets.json; `--swell` overrides it) is the quality each hero's Swell input is played at: `off`, `miss`, `good` or `perfect` (`SwellInput.scripted_result`). Every policy but `naive` unleashes a full gauge before anything else: a damage technique on the weakest foe (the provoker when Provoked) or every foe, a healing one once an active ally is below `swell_heal_below_pct` (60%, `sim_policies.json`). Heroes fill in the default mode (Ballast) and start every fight empty. The sandbox suites assume `good`: a player who has learned the inputs but does not nail them.

## Party assumptions (gear and consumables)

Every suite names a **loadout** in `game/data/battle/sim_policies.json` (`loadouts`): the equipment each character wears (`EquipmentEffects` is applied as a `party_modifier`, so stats, edges, wards and Full Net count) and the consumables the party carries. Bands only hold for their loadout.

| Chapter | Loadout | Gear | Consumables |
|---|---|---|---|
| M1 sandbox (early Ch2) | `m1_starting` | Starting gear (`equipment.json` `starting`) | 2 Salt Tonic |
| M1 sandbox, geared (measured, its own bands) | `m1_tier1` | Every hero's tier-1 piece, weapon and armor, with their pre-filled ability | 4 Salt Tonic, 1 Relighting Wick |
| Ch3 boss (Drownbell) | `ch03_drownbell` | A slice player can afford one or two tier-1 pieces; we assume all of them, the generous case. Plus the story flag `ch03_ilun_bound` (Call Ilun). | as above |
| Later chapters | add one loadout per chapter: the gear that chapter's shops sell, and about one consumable per expected fight | | |

Only `smart` uses items. Its rule: a heal item on the most hurt ally below `heal_below_pct` when the actor can't heal by skill, and a revive item on a fallen active member when no reserve is left to swap in. Gear moves `naive` by about 14 points in the sandbox (10.9% → 25.1%), which is the point of buying it; the showcase bands are defined for starting gear.

**Lock check.** `tests/unit/test_battle_turn_events.gd` runs a Drag-Net-only party (99 nets) against the sandbox and asserts that the slowest foe (the crab) still acts at least once per 10 party turns. With rank-2 nets and unbounded stacking, it never acted.

## Metrics

| Column | Meaning |
|---|---|
| Win % | Victories ÷ seeds. Loss rate = 100 − win %. Timeouts (more than `max_actions` = 2000 actions) count as misses. |
| Band | The win band, plus the ease ceiling (`mean_turns_min`) where the suite sets one. A row is OK only if it meets both and p90 turns. |
| Mean / p90 turns | Actions taken by both sides, automatic (Berserk/Confuse) turns included, lost Stop/Sleep turns excluded. p90 is nearest-rank. |
| Party KO | Mean party members down (KO or stone) at the end. |
| Items | Mean consumables used (the `smart` item rule). |
| Lume | Mean battle lume (`currency_award()`, × Full Net when worn). Validates economy.md's "about 60 lume per early fight". |
| Swell / Swells | The quality the suite's Swell inputs are played at, and the mean techniques unleashed per fight (M2-CMB-01). |

## Target curve by chapter

The bands get harder as the player gains tools. **Regular** encounters should forgive a naive player early and stop forgiving them by Act II. **Bosses** should never be beaten by mashing, should be reliably beaten by the intended answer, and should still cost a careful player some KOs.

| Chapters | Kind | `naive` | `role_answer` | `smart` | p90 turns |
|---|---|---|---|---|---|
| Ch1–Ch3 (Act I start) | regular | 40–80% | ≥ 95% | ≥ 98% | ≤ 30 |
| Ch1–Ch3 | boss | ≤ 10% | 70–90% | 80–95% | ≤ 60 |
| Ch4–Ch9 (Act I) | regular | 20–60% | ≥ 92% | ≥ 97% | ≤ 35 |
| Ch4–Ch9 | boss | ≤ 5% | 65–85% | 75–92% | ≤ 70 |
| Ch10–Ch16 (Act II) | regular | 5–35% | ≥ 90% | ≥ 95% | ≤ 40 |
| Ch10–Ch16 | boss | ≤ 3% | 55–80% | 70–90% | ≤ 80 |
| Ch17–Ch21 (Act III) | regular | ≤ 25% | ≥ 88% | ≥ 95% | ≤ 45 |
| Ch17–Ch21 | boss | ≤ 2% | 50–75% | 65–88% | ≤ 90 |

The simulated party for a chapter is the party the story gives you there, with the Lattice progress of a player who has spent every movement point the preceding fights award (to be scripted with `run_one(..., party_modifier)` once those fights exist).

## Suites in force

### M1 sandbox: `sandbox_reef` (showcase)

Loadout `m1_starting`. Rhen and Asha active, Toma and Ysolde in reserve, against Reef Crab (answer: Toma's Shell Breaker), Lantern Eel (answer: Ysolde's fire) and Gull Harrier (answer: Rhen's accuracy). The sandbox exists to teach swapping, so it is deliberately harsher than a Ch1 regular fight.

| Policy | Band | Why |
|---|---|---|
| `naive` | 5–15% | Mashing should usually lose, but not always: hopeless fights read as unfair. |
| `lowest_hp` | report only | Focus fire is a real tactic and lands near 80% whenever naive sits in its band (the two are tied by the lineup). The swap reward is the gap to `role_answer`. |
| `role_answer` | ≥ 85% | The elegant answer must reliably work. |
| `smart` | ≥ 85%, and ≥ 16 mean turns | Never worse than `role_answer` in practice. The turns floor is the ease ceiling (below). |
| p90 turns | ≤ 40 | A showcase fight stays short. |

**Ease ceiling (M1-CMB-07).** `smart` wins every seed (100.0%), so a win band can't see a regression that makes the sandbox *easier*. A win ceiling below 100% would fail today's numbers. The suite sets `mean_turns_min` in targets.json instead: `smart` must still average at least 16 actions per fight (measured 17.9 at 1000 seeds and 18.1 at the 200 seeds CI uses, so the floor allows about a 10% shorter fight). The geared suite `sandbox_reef_tier1` floors `smart` at 14.5 (measured 16.1 and 16.3). `sim.py` marks a row out of band when it misses the floor, and `test_sandbox_battle.gd` asserts the starting-gear floor at 200 seeds. Mean turns is used rather than party KOs because KOs are rare for `smart` (0.07 to 0.12 per fight) and too noisy at 200 seeds. If a deliberate change makes the fight shorter, re-measure and move the floor with a tuning-log note.

### Ch3 boss: Drownbell (vertical slice), `drownbell`

From [act_outline.md](../story/beats/act_outline.md): two phases on the causeway. Phase 1's toll delays the whole party on the timeline, and breaking its rim (Rhen's precise strikes) silences the toll. In phase 2 the polyps heal it and summoning Ilun clears the water field. Party: Rhen, Asha, Toma, with no reserve. Loadout `ch03_drownbell`: the `m1_tier1` gear and consumables plus the story flag `ch03_ilun_bound` (a loadout's `flags` become `BattleEngine.story_flags`), so Asha knows Call Ilun. Mechanics and data: [battle_ctb.md § The Drownbell](battle_ctb.md#the-drownbell-m2-fp-06).

| Policy | Band | Why |
|---|---|---|
| `naive` | 0–10% | A boss is never beaten by mashing. |
| `role_answer` | 70–90% | Rhen on the rim is enough to win most of the time, but not without risk. |
| `smart` | 80–95% | Healing and replacement close most of the gap; a 5% or greater loss rate keeps it a boss. |
| p90 turns | ≤ 60 | Two phases, still a slice-length fight. |

The encounter landed in M2-FP-06 with a first-playable stand-in for the Vowbound summon (ADR 0024). Both `role_answer` and `smart` carry the "clear the field" rule: `sim_policies.json` `clear_field_skill: call_ilun`, so whoever can use it does so as soon as a field is up (`smart` heals first if someone is below 45%). Measured at 1000 seeds: naive 0.0%, role answer 79.7%, smart 89.6%, p90 51 actions (balance_report.md). `tests/integration/test_drownbell_battle.gd` asserts loose bands at 200 seeds on every run.
