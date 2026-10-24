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
| `naive_swell` | The masher who finds the Swell row (M2-NIT-03) | `naive`, plus it unleashes a full gauge: a single-foe technique on the first living foe (where the cursor starts), a healing one under the shared rule below. With a Vowbound bound, it calls it at once (below). **Report only, in every suite but the Vowbound stress suite.** See "When the masher's Swell needs a decision" below. |
| `lowest_hp` | Focus fire, no swaps | `attack` on the living foe with the least HP. |
| `role_answer` | The elegant answer (SPEC §6.1) | If the actor answers a living foe (`enemies.json` `role_answer`), it takes the weakest such foe. Otherwise the focus is the weakest foe, and if that foe's answer is in reserve it swaps in for the actor (free) and takes the turn. An answerer opens with a Break skill its foe lacks, then uses its best expected damage per rank (MP permitting). |
| `smart` | A careful player | `role_answer`, plus: replace a KO'd or petrified active member at once (preferring a reserve who answers a living foe); a healer heals the most hurt ally below `heal_below_pct` (45%) of max HP; a healer won't swap out while an ally is below `keep_healer_below_pct` (70%). |

"Expected damage" is the real formula at mean variance (100%), without crits, times the hit chance, and 0 for magic the target would Reflect. It is deterministic.

**Swell (M2-CMB-01).** A suite's `swell` (targets.json; `--swell` overrides it) is the quality each hero's Swell input is played at: `off`, `miss`, `good` or `perfect` (`SwellInput.scripted_result`). Every policy but `naive` unleashes a full gauge before anything else. A single-foe technique goes to the policy's focus foe (`SimPolicy.swell_focus`, or the provoker when Provoked): the weakest foe by default, the first foe for `naive_swell`, and the foe the actor answers for `role_answer` and `smart`. A group technique goes to every foe. A healing one waits until an active ally is below `swell_heal_below_pct` (60%, `sim_policies.json`); for Shallows Verse, a song for the others (`all_other_allies`, M2-CMB-02), that ally must be someone other than the singer. `role_answer` and `smart` make the free swap to the focus foe's answer first, and the gauge waits in reserve (M2-NIT-03). Before that change, the technique took the answer's turn and cost `role_answer` about 3 points. That was an artefact of the policy, not a balance fact. Heroes fill in the default mode (Ballast) and start every fight empty. The sandbox suites assume `good`: a player who has learned the inputs but does not nail them.

**When the masher's Swell needs a decision (M2-NIT-03).** `naive_swell` has no band, because nothing in the game should be tuned to make mashing win. It exists so that every report shows how much Swell lifts a masher, and so that a change which raises it gets a deliberate decision. The lines are **25% on starting gear** and **45% on tier-1 gear**, measured at `good` (M2-CMB-02; they were 35% and 50% under M2-NIT-03). A rate above either needs a tuning-log entry that accepts it or fixes it. Today the rates are 23.8% and 39.1%. For comparison, a masher whose only Swell is Lamp Dive wins 19.8% and 32.2%. That lift of about 9 points is the intended comeback. Since the Verse became a song for the others, it adds about 4 points on starting gear and 7 on tier-1, down from 12 and 15 (balance_report.md, 2026-10-23 M2-CMB-02). Played perfectly, a masher's Swell reaches 26.1% and 41.4%, which needs no decision: perfect inputs are not mashing.

**Vowbound (M2-CMB-05, ADR 0027).** A loadout's `vowbound` list is the Vowbound the party has bound (the game builds it from story flags; the simulator takes it from the loadout so a suite opts in). `sim_policies.json` `call_vowbound` is each policy's call rule: `naive_swell` calls **at once** (`at_once`: the masher who finds every new row), and `role_answer` and `smart` call **while a field is up** (`on_field`: the Drownbell's `clear_field_skill` is the model, so they call Ilun when the flood rises). `naive` and `lowest_hp` never call. A called Vowbound is played by the same policy: its full gauge goes first (`SimPolicy.unleash_vowbound`, aimed like a technique; Floodnet hits every foe), then the policy's usual choice. Under `at_once` it stays out until it falls or the battle ends. Under `on_field` it stays out while the field holds and is dismissed on its first turn after the field is gone: a careful player sends Ilun back when he no longer answers anything. Only policies that open the Swell row unleash it.

## Party assumptions (gear and consumables)

Every suite names a **loadout** in `game/data/battle/sim_policies.json` (`loadouts`): the equipment each character wears (`EquipmentEffects` is applied as a `party_modifier`, so stats, edges, wards and Full Net count) and the consumables the party carries. Bands only hold for their loadout.

| Chapter | Loadout | Gear | Consumables |
|---|---|---|---|
| M1 sandbox (early Ch2) | `m1_starting` | Starting gear (`equipment.json` `starting`) | 2 Salt Tonic |
| M1 sandbox, geared (measured, its own bands) | `m1_tier1` | Every hero's tier-1 piece, weapon and armor, with their pre-filled ability | 4 Salt Tonic, 1 Relighting Wick |
| M1 sandbox, Ilun called (stress test) | `sandbox_vowbound` | None | None; `vowbound: [ilun]` |
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

### Vowbound masher line: `sandbox_reef_vowbound` (stress test, M2-CMB-05)

ADR 0027 accepted a **provisional ceiling of 40%** for a masher who calls the Vowbound at once, on the sandbox with no gear. It is a ceiling, not a band to aim at, and the sandbox is pre-Ilun content. Suite: `sandbox_reef`, Rhen and Asha active and Toma in reserve (the probe's lineup), loadout `sandbox_vowbound` (no gear, no items, Ilun bound), `kind: vowbound`.

| Policy | Band | Why |
|---|---|---|
| `naive` | report only | Never opens the Vowbound row: the plain masher with no gear (8.7%). |
| `naive_swell` | **0–40%** | The masher calling Ilun on Asha's first turn. Measured 38.9% (Floodnet 0.22 times a fight, Ilun falls in nearly every run), exactly the probe's number. A1–A3 move nothing here: the only water Ilun meets is the crab's Brine Spit (power 4, every third crab turn), and it seldom comes while he is out. |
| p90 turns | ≤ 40 | As the sandbox. |

**The suite plays the heroes' Swell `off`**, unlike every other suite (`good`). The 40% line was accepted on the probe, which had no hero Swell, so the suite measures what was accepted. **With the heroes' Swell at `good`, the same masher wins 46.2%**: above the line. That number needs a decision from Design or the Lead (the levers are Ilun's HP scale and `call_rank`, battle_ctb.md § Vowbound). The binding per-encounter line is set on the Drownbell (M2-FP-17).

**The Swell-on line: `sandbox_reef_vowbound_good` (M2-CMB-06, review-sweep-Q design verdict).** It's the same suite with the heroes' Swell at `good`, as play has it: a player can't turn hero Swell off, and the masher who finds the Vowbound row unleashes the heroes' gauges too. The ceiling for `naive_swell` is **50%**, set just above the measured **46.2%** (1000 seeds), and is accepted as is. Both suites are engine regression ceilings on pre-Ilun content, not player experiences. The Swell-off line isolates the Vowbound's own lift; the Swell-on line would catch a change in how hero Swell and the Vowbound interact (a technique that feeds Ilun's gauge, say). The binding per-encounter check stays on the Drownbell, with the heroes' Swell at `good`.

**The Drownbell with the real call (scratch probe, M2-CMB-05; not a suite yet).** The `drownbell` suite with Asha's `call_ilun` stand-in removed (no `ch03_ilun_bound` flag) and `"vowbound": ["ilun"]` in the loadout, 300 seeds: naive 0.0%, naive_swell 1.0%, **role_answer 72.0%** (p90 46 actions), **smart 87.0%** (p90 60), and no timeouts. Both sit in the boss bands, but smart's p90 is at the 60 ceiling. Two engine and policy choices got it there. The first is A1 counting the rolled absorb: with only the HP actually restored, a called Ilun at full HP filled nothing in the flood, so Floodnet never came and the flood never cleared (role_answer 0.0% and smart 0.0%, about 80% of fights timed out). The second is the `on_field` dismissal. M2-FP-17 owns the suite and its bands.

**The Drownbell suite plays the real call (M2-FP-17, m2-slice).** `ch03_drownbell` binds Ilun (`"vowbound": ["ilun"]`). The `call_ilun` stand-in is gone from the game, and so are the policies' `clear_field_skill` rule and the loadout's story flag: M2-UI-05's Call row is the only way. The bands are unchanged. Measured at 1000 seeds on the canonical CMB-05 mechanics: naive 0.0%, naive_swell 0.7%, **role_answer 71.0%** (p90 47), **smart 85.3%** (p90 60, at the ceiling), and no timeouts. A new policy, **`flood_call`**, is the masher who calls Ilun the moment the flood rises and leaves him out until he falls or the bell dies (`call_vowbound: field_up`). It wins **38.8%** (p90 38). Its band is [0, 95], the suite's `smart` ceiling: calling into the flood must never beat the careful player, and the fight must never stall.

### Ch3 boss: Drownbell (vertical slice), `drownbell`

From [act_outline.md](../story/beats/act_outline.md): two phases on the causeway. Phase 1's toll delays the whole party on the timeline, and breaking its rim (Rhen's precise strikes) silences the toll. In phase 2 the polyps heal it and summoning Ilun clears the water field. Party: Rhen, Asha, Toma, with no reserve. Loadout `ch03_drownbell`: the `m1_tier1` gear and consumables plus the story flag `ch03_ilun_bound` (a loadout's `flags` become `BattleEngine.story_flags`), so Asha knows Call Ilun. Mechanics and data: [battle_ctb.md § The Drownbell](battle_ctb.md#the-drownbell-m2-fp-06).

| Policy | Band | Why |
|---|---|---|
| `naive` | 0–10% | A boss is never beaten by mashing. |
| `role_answer` | 70–90% | Rhen on the rim is enough to win most of the time, but not without risk. |
| `smart` | 80–95% | Healing and replacement close most of the gap; a 5% or greater loss rate keeps it a boss. |
| p90 turns | ≤ 60 | Two phases, still a slice-length fight. |

The encounter landed in M2-FP-06 with a first-playable stand-in for the Vowbound summon (ADR 0026). Both `role_answer` and `smart` carry the "clear the field" rule: `sim_policies.json` `clear_field_skill: call_ilun`, so whoever can use it does so as soon as a field is up (`smart` heals first if someone is below 45%). Measured at 1000 seeds: naive 0.0%, role answer 79.7%, smart 89.6%, p90 51 actions (balance_report.md). `tests/integration/test_drownbell_battle.gd` asserts loose bands at 200 seeds on every run.

### Ch1: solo Rhen (M3-C01-02, ADR 0034)

Rhen fights alone all chapter (act1_ch01.md §9 Combat), with `active: [rhen]` and no reserve. The loadouts are `ch01_underway` (starting gear, 2 Salt Tonic, 1 Brine Eyewash) and `ch01_hullgnaw` (the same). Swell is `good`.

| Suite | Kind | `naive` | `role_answer` | `smart` | p90 turns |
|---|---|---|---|---|---|
| `ch01_wickfry`, `ch01_oil_slug`, `ch01_shaft_limpet`, and the random `ch01_underway_shoals` and `ch01_underway_limpet` | tutorial (logged exception) | 80–100% | ≥ 95% | ≥ 98% | ≤ 30 |
| `ch01_scuttlers` | Ch1–Ch3 regular | 40–80% | ≥ 95% | ≥ 98% | ≤ 30 |
| `ch01_hullgnaw` | Ch1–Ch3 boss | 0–10% | report only | 80–95% | ≤ 60 |

- **Tutorial fights:** each teaches one thing (the command menu, items, escape), and a first-time masher shouldn't lose one.
- **Hullgnaw's `role_answer`:** the policy never uses items, and in a one-hero fight nobody can swap in, so it measures only the masher plus MP skills and the Swell. Rhen's answer is tempo plus a Salt Tonic when the Coil telegraphs the Gnaw, and only `smart` plays that.
- **Kick Off:** the encounter lends it (`party_skills`), because the second phase teaches it.

Numbers are in the 2026-10-24 tuning log entry in balance_report.md.
