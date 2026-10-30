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
| Ch3 boss (Drownbell) | `ch03_drownbell` | Starting gear plus the two most likely tier-1 buys, Rhen's Coral-Bitten Hooks and Toma's Chiselled Shield (720 lume of the slice's 800–900; M2-CMB-07 follow-up, balance_report.md 2026-10-24). Plus the story flag `ch03_ilun_bound` (Call Ilun). | as above |
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

### Ch3 route: `ch03_causeway_harrier` and `ch03_causeway_shore` (regular, M2-FP-25)

These are the Saltgrass Causeway's two fights (B06): the scripted flier lesson at C07, and the random shallows fight after it. Both put a Gull Harrier, a Reef Crab and a Lantern Eel against Rhen and Asha, with Toma in reserve, on loadout `m1_starting`. They take the Ch1–Ch3 **regular** band from the curve above.

| Policy | Band | Measured (1000 seeds), harrier / shore |
|---|---|---|
| `naive` | 40–80% | 65.8% / 71.3% |
| `role_answer` | ≥ 95% | 95.3% / 95.3% |
| `smart` | ≥ 98% | 100% / 99.9% |
| p90 turns | ≤ 30 | 18 / 19 |

**Notes:**
- **Foe order matters.** The naive policy strikes the first foe, so the harrier-first lesson and the eel-first shallows land in band. The same three foes with the crab first fall to 10.9% for naive, and that's out of band.
- **Two foes are too easy.** Every pair tried gave naive 96–100%.
- **The other three-foe mixes miss.** With two crabs, or two harriers, the role answer falls short, because the crab's answer (Toma) starts in reserve and the eel's (Ysolde) hasn't joined yet.
- Leave the order as authored, and re-measure if a foe moves.

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

From [act_outline.md](../story/beats/act_outline.md): two phases on the causeway. Phase 1's toll delays the whole party on the timeline, and breaking its rim (Rhen's precise strikes) silences the toll. In phase 2 the polyps heal it and summoning Ilun clears the water field. Party: Rhen, Asha, Toma, with no reserve. Loadout `ch03_drownbell`: starting gear plus two tier-1 pieces (the table above), the `m1_tier1` consumables, and the story flag `ch03_ilun_bound` (a loadout's `flags` become `BattleEngine.story_flags`), so Asha knows Call Ilun. Mechanics and data: [battle_ctb.md § The Drownbell](battle_ctb.md#the-drownbell-m2-fp-06).

| Policy | Band | Why |
|---|---|---|
| `naive` | 0–10% | A boss is never beaten by mashing. |
| `role_answer` | 70–90% | Rhen on the rim is enough to win most of the time, but not without risk. |
| `smart` | 80–95% | Healing and replacement close most of the gap; a 5% or greater loss rate keeps it a boss. |
| p90 turns | ≤ 66 | Two phases, still a slice-length fight. Raised from 60 (Lead, 2026-10-24, big7): Ilun's real call adds his own actions to the count, and the affordable party (M2-CMB-07) fights longer. Smart's p90 is 65 at 1000 seeds, and no stat change got it below 61. |

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
- **Tempo (M3-CMB-02):** no Ch1 regular should routinely double-turn a solo Rhen. A foe's rank × base delay should be no shorter than about 0.85 of Rhen's Attack (174 ticks): the Wickfry is 150, and every other regular is slower. Only Hullgnaw's second phase out-tempos him, by design. The timeline shows each foe at its AI's rank (ADR 0038).

Numbers are in the 2026-10-24 tuning log entry in balance_report.md.

### Ch5: the pilgrim stair and the Cinder Matron (M3-C05-02)

The story party from the end of B05: active Rhen, Asha and Kerrid, with Toma and Ysolde in reserve. The Matron fight starts Kerrid, Rhen and Asha. Swell is `good`.

Loadouts are `ch05_ashcrown` (2 Salt Tonic) and `ch05_matron` (4 Salt Tonic, 1 Relighting Wick, Ilun bound). Both carry the best gear a Ch5 player can own. Pemakar's shop tier doesn't exist yet, so that's Haluna's post-Drownbell weapons (Tidewalker Hooks, Dawnwick Staff, Saltgrass Pike), the tier-1 armour, Ysolde's tier-1 pieces and Kerrid's starting pieces.
- **The Coral Hooks are left out on purpose.** Their Ember Edge makes Rhen's attacks fire, which the Matron absorbs. The policies can't change gear, and with them equipped every policy loses.

| Suite | Kind | `naive` | `role_answer` | `smart` | p90 turns |
|---|---|---|---|---|---|
| `ch05_stair_tortoises` (scripted: two slag tortoises, Kerrid's lesson) | Ch4–Ch9 regular | 20–60% | ≥ 92% | ≥ 97% | ≤ 35 |
| `ch05_stair_ashwings`, `ch05_stair_tortoise_sparker`, `ch05_stair_tortoise_ashwing` (the random stair table) | Ch4–Ch9 regular | 20–60% | ≥ 92% | ≥ 97% | ≤ 35 |
| `ch05_cinder_matron` | Ch4–Ch9 boss | ≤ 5% | 65–85% | **report only**, ≥ 40 mean turns | ≤ 70 |
| `ch05_cinder_matron_ilun` (`naive_swell`: Ilun called at once, the water mistake) | report only | | | | ≤ 70 |

- **The Matron's `smart` band is report only.** With two reserves, Asha's Mend and the items, `smart` won every seed of every tuning tried: 100% even where `role_answer` won 0%. A boss with no time pressure can't push a healing five-hero party below 92%.
  - The table's 75–92% needs a mechanic that punishes a long fight, such as an escalation by turn count. That's the combat request M3-C05-06.
  - Until then, `mean_turns_min` (`smart` ≥ 40 actions) is the ease ceiling, as in the M1 sandbox.
- **Foe order matters.** `naive` hits the first foe:
  - both mixed groups put the slag tortoise first;
  - `[vein_sparker, slag_tortoise]` gave a masher 78%, and `[ashwing, slag_tortoise]` 64%.
- **The cut 3-foe group.** The sheet's "2 ashwings + 1 vein sparker" was cut from the table. All three foes are answered by Ysolde, who starts in reserve, so `role_answer` won only 48%. The stair stays at two foes for now (sheet §9 Creatures 15; M3-C05-05).
- **Ashwings name Ysolde as their answer** (fire weak), not Rhen. The sheet allows either, and only Ysolde gives `role_answer` a swap to make.

Numbers are in the 2026-10-24 tuning-log entry in balance_report.md.

### Ch4: the first four-member party (M3-C04-02)

The derelict's fights (act1_ch04.md C4-12, C4-13, §5, §9 Combat). Rhen, Asha and Toma are active and Ysolde is in reserve (she joins at the gangplank), at Swell `good`. Loadouts: `ch04_derelict` (every Haluna tier-1 piece for Rhen, Asha and Toma, Ysolde's starting gear, 4 Salt Tonic, 1 Brine Eyewash, 1 Relighting Wick) and `ch04_spar_wraith` (the same, plus Ilun bound). The Spar-Wraith suite seats Ysolde active and Toma in reserve: the formation a player brings once the bottle-hermit has taught the swap (with Ysolde in reserve, `role_answer` swaps out whoever acts first, usually Rhen and his ember-edged hooks, and measures that rather than the answer).

| Suite | Kind | `naive` | `role_answer` | `smart` | p90 turns |
|---|---|---|---|---|---|
| `ch04_bottle_hermit`, and the random `ch04_derelict_glass` | Ch4–Ch9 regular | 20–60% | ≥ 92% | ≥ 97% | ≤ 35 |
| `ch04_sail_leeches`, and the random `ch04_derelict_leeches` | Ch4–Ch9 regular, `role_answer` report only (logged exception) | 20–60% | report only | ≥ 97% | ≤ 35 |
| `ch04_spar_wraith` | Ch4–Ch9 boss, `smart` ceiling lifted (logged exception) | 0–5% | 65–85% | 75–100%, ≥ 30 mean turns | ≤ 70 |

- **The leeches' `role_answer`.** The leech's answer is Rhen, and he is already on the field with nothing a masher lacks but Quick Hit, so the policy plays almost exactly like `naive` (62.9% against 48.2%). Asking it for 92% would need a leech the masher also beats. Report only, as Ch1's Hullgnaw, until Combat rules (M3-C04-06).
- **The Spar-Wraith's `smart` ceiling.** With four heroes and Asha's Mend, `smart` out-heals any damage that `role_answer` (which never heals) survives: every tuning that put `role_answer` in 65–85% left `smart` at 99–100%. No field mechanic like the Drownbell's flood is in the sheet. The ceiling is lifted to 100% and the ease ceiling is `smart` ≥ 30 mean turns (measured 33.3) until Combat rules (M3-C04-06).
- **The sim plays every opening as normal.** BattleSim never sets `engine.opening`, so the scripted leech ambush and its random twin measure the same. The ambush makes the live fight a little harder than measured.
- **Ysolde's lesson.** The hermit's glass resists blows and is immune to fire (the sheet's "reflects fire": the engine has no reflect), and ice cracks it. Rhen's ember-edged Coral Hooks turn his Attack to fire, so a masher's Rhen does nothing to it. The masher wins about half the time on Toma and Asha alone; Ysolde's Frost ends it in about eight actions.

Numbers are in the 2026-10-24 tuning log entry in balance_report.md.

### Ch6: the Brine Shoals and the Stillguard Inquisitor (M3-C06-02)

The road's fights use Ch5's party: active Rhen, Asha and Kerrid, with Toma and Ysolde in reserve. The Inquisitor starts Toma, Rhen and Asha (Toma steps in front of Asha), with Kerrid and Ysolde in reserve. Liss joins after the fight and is in no suite. Swell is `good`.

Loadouts are `ch06_shoals` (3 Salt Tonic, 1 Brine Eyewash) and `ch06_inquisitor` (4 Salt Tonic, 2 Brine Eyewash, 1 Relighting Wick, Ilun bound, flags `ch03_ilun_bound` and `ch05_kahre_bound`). Both carry Ch5's gear (`ch05_ashcrown`'s pieces), since Pemakar's shop tier doesn't exist yet.

| Suite | Kind | `naive` | `role_answer` | `smart` | p90 turns |
|---|---|---|---|---|---|
| `ch06_ridge_skippers` (two shoal skippers) | Ch4–Ch9 regular, `role_answer` report only (logged exception) | 20–60% | report only | ≥ 97% | ≤ 35 |
| `ch06_ridge_crab` (a wreck crab and a shoal skipper) | the same | 20–60% | report only | ≥ 97% | ≤ 35 |
| `ch06_ridge_gulls` (two gull harriers and a shoal skipper) | the same | 20–60% | report only | ≥ 97% | ≤ 35 |
| `ch06_flats_crabs` (the mud-flats: two wreck crabs and a gull harrier) | Ch4–Ch9 regular | 20–60% | ≥ 92% | ≥ 97% | ≤ 35 |
| `ch06_inquisitor` | Ch4–Ch9 boss, `smart` ceiling lifted (logged exception) | ≤ 5% | 65–85% | 75–100%, ≥ 25 mean turns | ≤ 70 |

- **The skipper suites' `role_answer`** is the Ch4 leech exception again. The skipper's answer is Rhen, who is already on the field, so the policy plays like the masher. Report only until Combat rules (M3-C06-05).
- **The Inquisitor's `smart` ceiling** is the Ch4 Spar-Wraith exception again. With Asha's Mend, `smart` out-heals anything `role_answer` survives (100% wherever `role_answer` was in 65–85%). The ease ceiling is `smart` ≥ 25 mean turns (measured 29.0).
- **Toma will not strike the Stillguard** (`forbidden_skills`), so `naive` fights with two blades and a guard, and loses. `role_answer` swaps Toma for a reserve striker (battle_ctb.md "Encounter rules"); that is how it reaches 65–85%.
- **The flats are cut to three foes.** The sheet's 3–4 foe groups are too much for this party: three skippers gave `smart` 53–85%, and four foes pushed `smart`'s p90 to 43–51. The flats keep one 3-foe group (two crabs, whom Kerrid answers, and a gull), and `ch06_ridge_gulls` (three foes) is in their table too. The cut groups are `ch06_flats_skippers` and `ch06_flats_mixed` (M3-C06-05).

Numbers are in the 2026-10-24 tuning-log entry in balance_report.md.

### Ch8: the Fisher Stair set piece and the Undertow's Reach (M3-CMB-01)

The set piece (act1_ch08.md §5a; schema in [set_piece_battles.md](set_piece_battles.md), ADR 0100) is won on its **objective**: a quota of the Climb's turns, or `scripted_escape` for the Reach, which the simulator counts as a win. `kind: set_piece`. Every suite uses the loadout `ch08_seawall`: Ch6's gear without Kerrid's, 4 Salt Tonic, 2 Brine Eyewash and 1 Relighting Wick, the flags `ch03_ilun_bound`, `ch05_kahre_bound`, `ch08_virel_bound` and `ch08_hoist_rigged`, and Ilun, Kahre and Virel bound. Swell is `good`. Toma is locked active in every fight and Kerrid is in none.

**The guard.** `role_answer` and `smart` play `sim_policies.json` `guard_ward` (SimWardGuard): Toma holds the stair when a grip comes before his next turn, Provokes a second one, and Liss hauls a bare Climb. This is the set piece's role answer; the crawlers' `role_answer` is Toma. `ward_guard` (`naive` plus the guard) is report only. It shows that guarding alone doesn't carry a wave. The killing still matters.

| Suite | Party (active / reserve) | `naive` | `role_answer` | `smart` | p90 turns |
|---|---|---|---|---|---|
| `ch08_stair_hold_1` "Hold" | Toma, Ysolde, Liss / Rhen, Asha | 10–60% | 85–95% | 97–100% | ≤ 100 |
| `ch08_stair_hold_2` "The Rope" | Toma, Rhen, Liss / Asha, Ysolde | 10–60% | 85–95% | 97–100% | ≤ 100 |
| `ch08_stair_hold_3` "The Last of the Low Town" | Toma, Liss, Ysolde / Rhen, Asha | 10–60% | 85–95% | 97–100% | ≤ 100 |
| `ch08_undertows_reach` | Toma, Asha, Liss / Rhen, Ysolde | ≤ 10% | 75–85% | 75–95% (the Act I boss range) | ≤ 90 |

- **The waves' `naive` floor is 10%, not the sheet's proposed 40%.** In Wave 1 the Climb is slowest and its grips land unguarded, so a masher who never holds the stair loses most of the time. It measures about 15%, against 53% and 33% in Waves 2 and 3. Lifting it would have needed the role answer pushed past 95%.
- **Wave 1's party is Toma, Ysolde and Liss.** With Asha active, the role answer, which neither heals nor guards with her, fell to about 20%. With Rhen and Ysolde it won every fight. The bands hold for this party, and the player may choose another.
- **Waves are long for a masher** (p90 up to about 90 actions, against about 55 for the role answer), which is why the p90 ceiling is 100.
- **The Reach:** the masher never lights the dark (no Virel), so storm_dark's Darkness, which lasts to the hero's next turn, kills its blows and its counters. The role answer calls Virel the moment the field rises; Flare Line clears it and the bound Squall Wings fall. Losses are the fights where Asha falls before her first turn in the Dark.

Measured at 1000 seeds (balance_report.md, 2026-10-24 M3-CMB-01):

| Suite | `naive` | `naive_swell` | `role_answer` | `smart` | `ward_guard` |
|---|---|---|---|---|---|
| Wave 1 | 15.4 | 29.6 | 89.8 | 100.0 | 2.5 |
| Wave 2 | 53.2 | 54.1 | 87.8 | 100.0 | 44.9 |
| Wave 3 | 33.2 | 37.3 | 93.0 | 100.0 | 8.4 |
| The Reach | 0.3 | 12.8 | 80.7 | 86.2 | 0.3 |

### Ch10: the Mangrove Drowner (M4-A2P-010, chapters' combat seat)

The suite runs on the `ch08_seawall` loadout until M4-A2P-019's Ch10 loadout lands; re-run it then. Active Rhen, Asha and
Toma; Ysolde and Kerrid in reserve. Swell is `good`. Toma's Shell Breaker is the role answer (phase 1 is armoured roots,
defence 120). The Drowner is level 9, 3,600 HP, strength 14. Phase 2 (`uprooted`) comes at 55%: defence 30, agility 16,
Root Stomp and a two-turn charged Drowning Grasp.

| Suite | Kind | `naive` | `role_answer` | `smart` | p90 turns |
|---|---|---|---|---|---|
| `ch10_mangrove_drowner` | Ch10–Ch16 boss | ≤ 3% (2.5) | 55–80% (71.9) | **report only**, ≥ 30 mean turns (100%, 34.4 turns, 0.75 KOs) | ≤ 80 (46) |

- **`smart` is report only, as for `ch05_cinder_matron`.** With healing, two reserves and items, `smart` won every
  seed of every tuning tried (1,000 seeds):
  - lowering steady damage (strength 22 → 11) didn't move it;
  - nor did raising the charged burst (Drowning Grasp power 20 → 40).
  - It still costs a careful player about one KO a fight.
- **The Act II curve's 70–90%** needs the same escalation mechanic the Matron's note asks for (M3-C05-06).
- **The tuning that mattered:** the fight's length. At 4,800 HP, `role_answer` (which never heals) lost by attrition at
  every damage level. At 3,600 HP behind defence 120, Shell Breaker's answer carries it.

### Ch10: the Mangrove Drowner on its record row (big20; the Lead 10-30 05:28: one definition, the chapters seat owns the numbers)
- **Superseded above:** my own row's tune (role answer Toma, Root Lash, Drowning Grasp). There's one row now:
  battle-presentation's.
  - Role answer: Ysolde (fire on a fire-weak boss).
  - Skills: Root Haul (`drowner_drag`), Rising Water, Root Stamp.
  - Phase `uprooted` at 50%.
- **Stats changed:**
  - HP 5200 → 2200, strength 30 → 11, magic 20 → 8, defence 60 → 200.
  - `uprooted` defence 36 → 160.
- **Why:**
  - Ysolde's Ember costs 4 MP, and the role play never uses items, so her fire must finish it inside her MP.
  - The physical wall (defence 200, then 160) keeps a naive basic-attack party out.
- **The ease floor** drops to 20 turns: the record row is the shorter fight.
- **Results** (1,000 seeds, `ch08_seawall`):
  - naive 1.1, role_answer 62.1, smart 100 (about 24 turns, report only).
  - **naive_swell 100** (report only): a player who fills the Swell overpowers it. Watch this once the Ch10 loadout
    lands.

### Act II creature bosses: the combat seat's tune for battle-presentation's PROVISIONAL rows (1dbfed6d5)

- **Status: applied** on the record rows (big20), with suites `ch11_lamp_engine`, `ch12_avalanche_ram` and
  `ch15_wakefin` added. The same 1,000-seed numbers as below.
- **History:** battle-presentation wrote the rows so the staging (M3-BPR-419) could go live. I tuned them first in a
  scratch worktree of their branch.
- **Common to all three:**
  - Loadout `ch08_seawall` until M4-A2P-019.
  - Swell `good`.
  - Smart is report only (≥ 30 mean turns), on the Drowner's grounds: smart won 100% at every tune.

| Boss (suite) | Party (reserve) | Stats changed from the provisional row | `naive` | `role_answer` | `smart` (turns) |
|---|---|---|---|---|---|
| Lamp Engine (`ch11_lamp_engine`) | Rhen, Asha, Liss (Toma, Ysolde) | HP 5600 → 4000, strength 28 → 22, magic 26 → 20, defence 110 → 140, magic defence 40 → 60; `opened` defence 30 → 80, magic defence 20 → 40 | 2.7 | **report only** (9.7) | 100 (68) |
| Avalanche Ram (`ch12_avalanche_ram`) | Rhen, Asha, Kerrid (Toma, Ysolde) | HP 6200 → 4000, strength 36 → 22, defence 44 → 120; `torn_fleece` defence 22 → 40 | 2.2 | 61.3 | 100 (43) |
| Wakefin (`ch15_wakefin`) | Rhen, Asha, Toma (Ysolde, Kerrid) | HP 7000 → 5000, strength 38 → 30, magic 18 → 16, agility 22 → 16, evasion 8 → 4, defence 36 → 120 | 0.0 | 70.3 | 100 (43) |

- **Why the defence wall:** the sim's `role_answer` opens with a Break skill the foe lacks: Kerrid's Fluke Cleave on
  the Ram, Toma's Shell Breaker on the Wakefin. At the rows' low defence, nothing separated a naive player from the
  answer. As provisional, every policy lost by attrition (role 0–5%).
- **The Lamp Engine's answer is Liss's part repair (M4-A2P-022), which is not data yet.**
  - Liss has no Break skill, so `role_answer` can't beat naive, and her row stays report only until the mechanic lands.
  - Re-tune it then.
