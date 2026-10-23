# Balance Targets

Owner: Combat. SPEC §6.9: every encounter is simulated over thousands of seeds, and any boss whose expected party-loss rate falls outside its band is rebalanced before release. The machine-readable copy of the bands is [`tools/balance/targets.json`](../../../tools/balance/targets.json); change both together. Results are in [balance_report.md](balance_report.md).

## How to run

```bash
python3 tools/balance/sim.py                 # every suite, 1000 seeds, rewrites balance_report.md
python3 tools/balance/sim.py --seeds 200 --suite sandbox_reef --check   # quick, exit 1 on a miss
```

`sim.py` calls `godot --headless -s res://game/battle/sim/sim_main.gd` (the GDScript runner, `BattleSim`), writes per-seed and summary CSVs to `tools/balance/out/` (gitignored), and rewrites the table at the top of the report, keeping the hand-written tuning log below the `<!-- tuning-log -->` marker. Seeds are `1..N`, so every number is reproducible. `tests/integration/test_sandbox_battle.gd` asserts the sandbox bands at 200 seeds on every CI run.

## Party policies (`game/battle/sim/`)

Each policy is a `SimPolicy` subclass. Policies use only the engine's public API and never touch `engine.rng`, and every turn ends (a fallback basic attack guarantees it). Tunables are in `game/data/battle/sim_policies.json`.

| Policy | What it models | Rule |
|---|---|---|
| `naive` | A player mashing Attack | `attack` on the first living foe. Never swaps. |
| `lowest_hp` | Focus fire, no swaps | `attack` on the living foe with the least HP. |
| `role_answer` | The elegant answer (SPEC §6.1) | If the actor answers a living foe (`enemies.json` `role_answer`), it takes the weakest such foe. Otherwise the focus is the weakest foe, and if that foe's answer is in reserve it swaps in for the actor (free) and takes the turn. An answerer opens with a Break skill its foe lacks, then uses its best expected damage per rank (MP permitting). |
| `smart` | A careful player | `role_answer`, plus: replace a KO'd or petrified active member at once (preferring a reserve who answers a living foe); a healer heals the most hurt ally below `heal_below_pct` (45%) of max HP; a healer won't swap out while an ally is below `keep_healer_below_pct` (70%). |

"Expected damage" is the real formula at mean variance (100%), without crits, times the hit chance, and 0 for magic the target would Reflect. It is deterministic.

## Metrics

| Column | Meaning |
|---|---|
| Win % | Victories ÷ seeds. Loss rate = 100 − win %. Timeouts (more than `max_actions` = 2000 actions) count as misses. |
| Mean / p90 turns | Actions taken by both sides, automatic (Berserk/Confuse) turns included, lost Stop/Sleep turns excluded. p90 is nearest-rank. |
| Party KO | Mean party members down (KO or stone) at the end. |
| Items | Mean items used. Items don't exist yet (Progression), so this is 0; `SimPolicy.items_used` is the hook. |

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

Rhen and Asha active, Toma and Ysolde in reserve, against Reef Crab (answer: Toma's Shell Breaker), Lantern Eel (answer: Ysolde's fire) and Gull Harrier (answer: Rhen's accuracy). The sandbox exists to teach swapping, so it is deliberately harsher than a Ch1 regular fight.

| Policy | Band | Why |
|---|---|---|
| `naive` | 5–15% | Mashing should usually lose, but not always: hopeless fights read as unfair. |
| `lowest_hp` | report only | Focus fire is a real tactic and lands near 80% whenever naive sits in its band (the two are tied by the lineup). The swap reward is the gap to `role_answer`. |
| `role_answer` | ≥ 85% | The elegant answer must reliably work. |
| `smart` | ≥ 85% | Never worse than `role_answer` in practice. |
| p90 turns | ≤ 40 | A showcase fight stays short. |

### Ch3 boss: Drownbell (vertical slice), `boss_drownbell` (pending data)

From [act_outline.md](../story/beats/act_outline.md): two phases on the causeway. Phase 1's toll delays the whole party on the timeline, and breaking its rim (Rhen's precise strikes) silences the toll. In phase 2 the polyps heal it and summoning Ilun clears the water field. Party: Rhen, Asha, Toma, with no reserve.

| Policy | Band | Why |
|---|---|---|
| `naive` | 0–10% | A boss is never beaten by mashing. |
| `role_answer` | 70–90% | Rhen on the rim is enough to win most of the time, but not without risk. |
| `smart` | 80–95% | Healing and replacement close most of the gap; a 5% or greater loss rate keeps it a boss. |
| p90 turns | ≤ 60 | Two phases, still a slice-length fight. |

`sim.py` lists Drownbell as pending until the encounter is in `encounters.json`. Two things are needed first: the boss phase mechanism (M2) and Vowbound summons (`smart` will need a "summon when the water field is up" rule). Until then the bands are the design target that the boss data is tuned toward.
