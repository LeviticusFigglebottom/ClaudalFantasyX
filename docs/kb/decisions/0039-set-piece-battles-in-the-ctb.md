# 0039 — Set-piece battles in the CTB: scripted entries, objectives, party locks

- **Status:** accepted (Combat; the Lead reviews it with M3-CMB-01)
- **Date:** 2026-10-24
- **Roles affected:** combat, cinematics, UI, design, narrative
- **Author role:** combat (m2-slice, M3-CMB-01)

## Context
Ch8's evacuation (act1_ch08.md §5a and §9 Combat) is three chained wave battles on the Fisher Stair plus the Undertow's Reach, which can only be survived. The brief rules out a real-time system (SPEC §6.1), and pillar 4 demands that the player always knows who acts next. The engine had no way to:
- put something on the timeline that isn't a fighter;
- win on anything but "every foe is down";
- end a fight in a way that is neither victory nor an Escape;
- make a foe untouchable for one phase;
- hold a hero in his slot, keep one out, or give him a different Attack.

These pieces cross roles. Cinematics writes the waves as data (M3-C08-02), UI draws the entries and the refusals, Design owns the bands, and Narrative owns rule 6: nobody dies of a missed turn.

## Options
1. **One long battle with reinforcements and a hand-coded script.** It allows no E beats between waves, and a defeat late on throws away everything. act1_ch08.md §5a rejects it.
2. **Special-case code per Ch8 fight** (a `Ch8Stair` class the engine knows by encounter id). It's quick, but the next set piece starts over, and Cinematics can't author a wave without code.
3. **One data-driven primitive set, read from the tables** (chosen). Encounters gain scripted timeline `entries`, an `objective`, and party rules. Skills gain ward targeting, cover, counter, withdraw and ward push. Phase rows gain `untargetable`, `damage_immune`, `spawn_bound` and `field_rules`. The rules live in a new Node-free class, `BattleSetPiece`, which the engine calls at fixed points, as it already calls `BossMechanics`.

## Decision
Option 3. The schema is in [set_piece_battles.md](../design/set_piece_battles.md). In short:
- **Scripted entries.** A non-player entry has an id, a `name_key`, a side, a fixed agility, a data AI and a role (`ward`, `tide` or `guest`). It has **no HP** and can't be KO'd, and it is never counted for victory or defeat. No skill can target it except a `target: "ward"` skill aimed at the ward. `run_enemy_turn()` plays it, on either side, and `is_party_turn()` is false for it.
- **The objective.** An encounter with an `objective` ends only on it: the ward's acted turns reach `quota`, counted from `from_phase` when one is set. Its outcome is `victory`, or the new **`scripted_escape`**: not the Escape command, and it counts as surviving the fight. Felling every foe does not end such a fight. Foes still standing at the end **withdraw**, and a withdrawn foe gives no XP, lume or drops. A `scripted_escape` awards spoils for the foes that were felled, as a victory does.
- **Party rules.**
  - `locked_active` keeps a living hero in his slot; `swap_refusal()` names the reason with `locked_key`.
  - `unavailable` leaves a hero out of the battle at setup.
  - `attack_override` replaces a hero's Attack with a skill (Toma's Stand Firm).
  - Combined with the existing `forbidden_skills`, Toma never goes on the offensive.
- **The guard.**
  - `covers: "ward"` (Hold the Stair): the next foe's ward skill lands on the coverer instead, resolved as its `on_cover` row. A Provoked foe's ward skill lands on its provoker in the same way.
  - `counter` (Stand Firm): until the hero's next turn, a landed physical hit from a foe is answered at once.
- **Lent skills keep their flag lock.** `party_skills` now runs `lock_skills` again, so the encounter can lend Haul while it still waits for `ch08_hoist_rigged`.
- **Simulator.**
  - A new `ward_guard` policy (report only) and a `guard_ward` config, which `role_answer` and `smart` set: the role answer to a grip is Toma's shield.
  - `scripted_escape` counts as a win.
  - With no foe it may strike, a policy takes a lawful non-offensive action, or sends a called Vowbound back.
  - A policy calls the Vowbound whose finisher clears the field that is up (Virel for storm_dark).

No formula changed: delay pushes, Haste, Slow, Darkness and damage all use the existing Formulas.

## Consequences
- **Easier:** any later set piece (a convoy, a siege, a ritual to protect) is data: an entry, an objective, a few skill keys. Cinematics can write M3-C08-02's waves without engine work.
- **Harder:** an objective fight can run with no foe standing, so every party needs a lawful non-offensive action. The Ch8 encounters lend Stand Fast to everyone.
- **Wired in the battle scene:**
  - the Attack row plays the hero's `attack_skill`;
  - a `ward` skill targets the ward;
  - `FieldBattle` takes `scripted_escape` as a win: Return only, and the request's victory flag is set.
- **Still a UI request:**
  - draw entries on the timeline;
  - grey the Swap row with `locked_key` and show unavailable heroes with `unavailable_key`;
  - show intercepts, counters and withdrawals, and the stair meter.
- **Watch:**
  - XP from an objective fight depends on how many foes the party fells, so it varies more than a normal fight's.
  - The carried stair meter (`ch08_stair_groups_up`) is the flow's job. It reads `engine.objective_count` after each wave and restores the meter on "Fight again". The engine never reads or writes flags.
  - The beat sheet's fire weakness on the Tide Crawler is dropped. Ysolde's fire made the waves trivial for the role answer (100%). The creatures track should know.
