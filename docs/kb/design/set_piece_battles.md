# Set-Piece Battles (scripted entries, objectives, party locks)

Owner: Combat (M3-CMB-01). Decision: [ADR 0100](../decisions/0100-set-piece-battles-in-the-ctb.md). Design brief: [act1_ch08.md](../story/beats/act1_ch08.md) §5, §5a and §9 Combat. Code: `game/battle/battle_set_piece.gd` (`BattleSetPiece`), with hooks in `battle_engine.gd`, `boss_mechanics.gd`, `enemy_ai.gd` and `combatant.gd`. Simulator: `game/battle/sim/sim_ward_guard.gd`. Validator: `tools/validate_data.py` § Set-piece battles. Tests: `tests/unit/test_battle_set_piece.gd`, `test_battle_sim_ward_guard.gd`, `test_ch08_battles.gd`, `tools/tests/test_set_piece_validate.py`.

A set piece is an ordinary CTB battle (SPEC §6.1: time stops while the player chooses) with a few extra rows of data. There's no real-time system and no per-fight code. This page is the schema for writing one, such as Ch8's waves in M3-C08-02.

## 1. Encounter keys (`game/data/battle/encounters.json`)

| Key | Shape | What it does |
|---|---|---|
| `entries` | `[{entry row}]` (§2) | Scripted timeline entries: the Climb, the Surge, Pell. |
| `objective` | `{ward, quota, from_phase?, outcome?}` | The fight ends when the `ward` entry has taken `quota` acted turns. With `from_phase` set, only turns taken after some foe entered that phase count. `outcome` is `victory` (the default) or `scripted_escape`. **An encounter with an objective is never won by felling every foe.** At the end, the foes still standing **withdraw**. |
| `locked_active` | `[hero ids]` | A living locked hero can't be swapped out. `BattleEngine.swap_refusal(id)` returns `BattleSetPiece.FAIL_LOCKED`. A locked hero set in reserve at setup takes the last active slot held by an unlocked hero, or a free slot. A fallen locked hero may be replaced (rule 6: no stall). |
| `locked_key` | loc key | Why the swap is refused ("Holding the stair"). |
| `unavailable` | `[hero ids]` | Left out of the battle at setup, active or reserve (Kerrid in Ch8). `engine.unavailable` lists them for the formation menu. |
| `unavailable_key` | loc key | The formation menu's note ("Not with the party"). |
| `attack_override` | `{hero id: skill id}` | That hero's Attack plays this skill: it takes Attack's place in the skill list, and `BattleCombatant.attack_skill` names it for the menus. |

These work with the keys that already exist: `scripted: true` (no Escape), `opening`, `prompt_key`, `victory_key`, `party_skills` (lent skills, which now keep their `requires_flag`) and `forbidden_skills`. In Ch8, `forbidden_skills` with tag `undertow_spawn` is what keeps Toma off the offensive.

## 2. Entry rows (`entries`)

```json
{"id": "the_climb", "name_key": "ENTRY_CH08_FISHER_STAIR", "side": "party", "role": "ward",
 "agility": 4, "skills": ["climb_up"], "ai": [{"pick": [{"skill": "climb_up", "target": "self"}]}]}
```

| Key | Meaning |
|---|---|
| `id` | Unique in the encounter. Not a hero or enemy id, and no `#` in it. It is also the combatant id (`engine.find("the_climb")`). |
| `name_key` | Its label on the timeline. |
| `side` | `party` or `enemy`: the team whose foes its skills face. |
| `role` | `ward` (at most one per encounter: the target of `ward` skills and the objective's counter), `tide` (an enemy-side spawner) or `guest` (an ally the player reads but doesn't command). |
| `agility` | Its fixed pace (≥ 1). The player can always count how many turns away its next turn is (pillar 4). |
| `skills`, `ai` | Its kit and data AI, as for an enemy (EnemyAI rules and `charge` telegraphs, on either side). |
| `delay_immune` | Optional, as for enemies (the Surge). |
| `summon_cap` | Optional. Its `summon` skills add nothing while this many **targetable** foes stand. |
| `joins_at_phase` | Optional. Off the field until a foe enters that phase id; then it acts a default-rank delay from now (the Reach's Surge). |

An entry **has no HP** and can't be KO'd: hits, Doom and field falls do nothing to it. It is never in `living_foes_of` / `living_allies_of`. It is never a target except for a `ward` skill aimed at the ward, and it never counts for victory or defeat. `is_party_turn()` and `is_player_side_turn()` are false on its turns, and `run_enemy_turn()` plays it. It appears in `preview()`, `preview_swap()` and the Vowbound previews like anyone else. Statuses work on it: Haste, Slow, and a telegraph's intent.

## 3. Skill keys (`skills.json`)

| Key | Meaning |
|---|---|
| `"target": "ward"` | Aims at the battle's ward entry, on either side: a foe's grip, or Liss's Haul. The AI selector is `"target": "ward"`. |
| `covers: "ward"` | The user covers the ward until its next turn. The next ward skill from a foe lands on the user instead and spends the cover (Hold the Stair). |
| `on_cover: skill id` | On a ward skill: the row it resolves as when a coverer, or the actor's provoker, takes it. It's a physical blow for a grip. Without it, the skill's own row lands on the guard. `ActionResult.intercepted_by` names the guard. |
| `counter: skill id` | Until the user's next turn, each landed **physical** hit from a foe is answered at once with this skill on the attacker. The answer hit carries `counter_by` (Stand Firm → `stand_firm_riposte`). |
| `withdraws: true` | A landed foe target leaves the field, not felled (`BattleCombatant.withdrawn`: no XP, lume or drops). Pell's Storm-Call. |
| `spares_tag: tag` | Never lands on a foe carrying the tag. Storm-Call spares `rooted`. A telegraphed skill picks its random target from the others. |
| `pushes_ward: ranks` | After the hits, the opposing ward is pushed back by that many ranks (Breach). |

Existing keys carry the rest: `charge` (telegraph), `summon`, `delay_ranks`, `cleanses` (a Rope Dive strips Haste), `statuses` (Haul's Haste), `clears_field` and `requires_flag`.

## 4. Enemy and phase keys (`enemies.json`)

| Key | Where | Meaning |
|---|---|---|
| `hp_floor_pct` | enemy row | Hits never take it below this share of max HP. The Reach can't fall before its last phase, which begins at that same share. A heal still heals. |
| `untargetable` | phase row | No skill may target it from then on. It still acts, and still counts as standing. |
| `damage_immune` | phase row | No hit takes HP from it. |
| `spawn_bound` | phase row | The phase's `spawn` are bound to its `field`, so they fall when it clears (the Dark's Squall Wings). |
| `field_rules` | phase row | `[{on: party/enemy/ward, status, duration?}]`. While the phase's `field` is up, each such combatant gains the status at the **start of its turn**. storm_dark gives Darkness for 2 turns, so it lasts until the hero's next turn and also covers counters, and Slow for 1 on the Climb. Clearing the field ends its rules. |

AI: the condition `ward_has_status: status` (a Squall Wing dives only a hauled rope) and the target `ward`. `EnemyAI.likely_skills` (what the first rule that holds would pick) is for the simulator.

## 5. Outcomes, spoils and the flow

- `BattleEngine.OUTCOME_SCRIPTED_ESCAPE` (`"scripted_escape"`) is not the Escape command, and it is never offered as one. It is the Reach survived.
  - `BattleSpoils.SPOILS_OUTCOMES` gives it spoils for the felled foes, as a victory does.
  - `BattleVitals` records the party's vitals.
  - `FieldBattle` treats it as a win: Return only, the request's `victory_flag` set, and the encounter's `victory_key` as the title over `HUD_SCRIPTED_ESCAPE_SUB`.
- **The carried stair meter** (`ch08_stair_groups_up`) belongs to the flow, M3-C08-02. The engine never reads or writes flags. After each wave, add `engine.objective_count` to the meter. On "Fight again", restore the meter to its value at the wave's start.
- A defeat is the party KO'd, as ever. The Climb can't die (rule 6).

## 6. The simulator

- **`ward_guard`** (report only): `naive`, plus the guard. `role_answer` and `smart` play the guard too, through `sim_policies.json` `"guard_ward": true`, because the role answer to a grip is Toma's shield. `SimWardGuard.act` runs only while the objective counts:
  1. A foe will use a ward skill before the actor's next turn (a telegraphed intent, or `EnemyAI.likely_skills`). The actor covers the ward if nobody covers it, or Provokes a second threat.
  2. The Climb has no Haste, and no field rule touches it (storm_dark's Slow would erase the Haste at once). The actor hauls.
- `scripted_escape` counts as a win (`BattleSim.WIN_OUTCOMES`).
- **When there's no foe to strike**, a policy takes its first lawful non-offensive skill on itself, an ally or the ward, or dismisses a called Vowbound.
- **A policy calls the Vowbound whose finisher clears the field that is up** (`SimPolicy.field_answer`): Virel for storm_dark, Ilun for the flood.

## 7. Ch8 as shipped (provisional numbers; the bands are in balance_targets.md)

| Encounter | Climb agility | Quota | Opening foes | Surge (agility, cadence, cap) | Other |
|---|---|---|---|---|---|
| `ch08_stair_hold_1` "Hold" | 3 | 3 | 2 `tide_crawler` | 8, every 2nd turn, 3 | — |
| `ch08_stair_hold_2` "The Rope" | 4 | 4 | `tide_crawler`, 2 `squall_wing` | 10, every 2nd, 3, crawler or wing | Haul lent |
| `ch08_stair_hold_3` "The Last of the Low Town" | 3 | 4 | 2 `tide_crawler`, `squall_wing`, `wall_polyp` | 14, every 2nd, 4 | Haul; Pell (`the_kirru`, agility 9) |
| `undertows_reach` | 6 | 2 from `breach`, `scripted_escape` | `undertows_reach` | joins at `breach`: 10, every 2nd, 2, crawlers | phases `dark` 60% and `breach` 30% |

Every Ch8 encounter has these rules:
- Toma: `locked_active`, his Attack becomes `stand_firm`, and `forbidden_skills` on `undertow_spawn`. He is lent `hold_the_stair` and `challenge`.
- Kerrid is `unavailable`.
- Everyone is lent `stand_fast`, so there is always a lawful action when no foe stands.

The new skills are:
- Party: `stand_firm`, `stand_firm_riposte`, `hold_the_stair` and `hoist_haul` (`requires_flag: ch08_hoist_rigged`).
- Virel: `kite_flare` and the finisher `flare_line` (`clears_field: storm_dark`).
- Spawn: `tide_claw`, `reach_for_stair` (a 1-turn telegraph of `grip_the_stair`, whose cover row is `grip_blow`), `wing_peck` and `rope_dive` (`dive_strike`).
- Entries: `climb_up`, `surge_crawler`, `surge_wing`, `surge_ebb`, and `storm_call_sound` (a telegraph of `storm_call`).
- The Reach: `close_the_hand` (a 2-turn telegraph of `hand_closes`, whose cover row is `hand_closes_blow`), `undertow_pull`, `crust_slam`, and `breach_gather` (a 4-turn telegraph of `breach`, with `pushes_ward: 3`).

Virel's row is in `vowbound.json` (caller Asha, `bound_flag: ch08_virel_bound`). Strings are in `game/data/loc/ch08.csv`.

**Where the data departs from the sheet** (each one for the bands, or for pillar 4):
1. **The Tide Crawler is not fire-weak.** With Ysolde's fire, the waves were trivial for the role answer (100%).
2. **A crawler's grip is telegraphed one turn ahead** (Reach for the Stair). The player sees it coming, and the guard has a turn to answer.
3. **Storm-Call picks its mover when it fires, not when it is telegraphed.** The timeline shows "Storm-Call" without naming the foe.
4. **The Kirru keeps that name.** Renaming him at `ch09_pell_named` is a UI or data follow-up.
5. **storm_dark's Darkness lasts until the hero's next turn,** so it also covers the party's counters.
6. **Haul lasts 2 of the Climb's turns, at rank 4.**
7. **If the wall is never lit, the dark stays through the Breach.**

## 8. The battle scene

**Wired here:**
- The Attack row plays and names the hero's `attack_skill` (Toma's Stand Firm), and the Skills page doesn't list it twice.
- A `ward` skill's only candidate and default target is the ward (`BattleMenus.skill_candidates` / `default_targets`).
- `scripted_escape` gets its result panel (§5).

**Still a UI request** (not built here):
1. Draw entries on the timeline with their `name_key` and a glyph (the stair, the tide, the kite), and draw no fighter for them on stage.
2. Grey the Swap row for a locked hero with `locked_key`. Show `unavailable` heroes greyed with `unavailable_key` in the formation menu.
3. Show an intercepted ward skill (`ActionResult.intercepted_by`), a counter (`counter_by`) and a withdrawal (`withdrawn`) in the battle log and floats.
4. Show the objective's count against its quota on the HUD (the stair meter).
