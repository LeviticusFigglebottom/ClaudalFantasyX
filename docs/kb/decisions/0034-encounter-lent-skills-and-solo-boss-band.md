# 0034 — Encounter-lent skills, and the solo-boss band for Hullgnaw

- **Status:** accepted (Combat to confirm in the M3-C01-02 review)
- **Date:** 2026-10-24
- **Roles affected:** combat, design, cinematics, narrative
- **Author role:** cinematics (m2-slice, M3-C01-02)

## Context
Ch1's boss, Hullgnaw (act1_ch01.md §5), is fought by Rhen alone, and its second phase teaches **Kick Off the Wall** (`kick_off`). But Rhen doesn't start with Kick Off. It's the first ability node on his Lattice petal (`rh_03`), and a new game reaches Hullgnaw about 30 minutes in, with no Lattice use guaranteed. A phase prompt naming a skill the player may not have breaks pillar 4.

The balance policies also assume a party. `role_answer` is "the answer swaps in and takes its foe, without items". In a one-hero fight there is nobody to swap, so `role_answer` is just the masher plus MP skills and the Swell. Rhen's answer to Hullgnaw is tempo **plus a Salt Tonic when the Gnaw is coming**, and only `smart` plays that.

## Options
1. **Give Rhen Kick Off in `characters.json`.** That moves every existing suite (sandbox, Drownbell): the policies would spend his MP on it at 5 power per rank.
2. **Make Kick Off flag-locked (`requires_flag`) and give it to Rhen's base kit.** `lock_skills` runs after the Lattice, so a slice player who learned `rh_03` without the Ch1 flag would lose it. It also breaks the existing Lattice tests.
3. **Have the story grant the Lattice node.** That needs a Lattice write from the field and a Design call on where the first node goes. The sheet leaves the Lattice's first use to Design (§9 Design 4).
4. **Let the encounter lend it.** Add an encounter field, `party_skills: {hero id: [skill ids]}`, which adds those skills for that fight only, after the Lattice and the flag locks, and never twice.

## Decision
Option 4.
- `BossMechanics.lend_skills` runs from `BattleEngine.setup`.
- `validate_data` checks the field, and `tests/unit/test_ch01_battles.gd` covers it.
- `ch01_hullgnaw` lends Rhen `kick_off`. Its phase-2 prompt (`TUT_HULLGNAW_KICK_OFF`) describes what the skill really does: it costs almost no time, so Rhen takes his turns before Hullgnaw's. The skill adds no delay to the foe, so the sheet's line "pushes a foe back down the order" is reworded.

**The band:** `ch01_hullgnaw` keeps the Ch1–Ch3 boss band for `naive` (≤ 10%) and `smart` (80–95%), and p90 ≤ 60. `role_answer` is **report only** for this one suite: the logged tutorial exception the sheet allows (§5). The other Ch1 fights:
- `ch01_scuttlers` is on the Ch1–Ch3 regular band.
- The three Underway tutorial fights (`ch01_wickfry`, `ch01_oil_slug`, `ch01_shaft_limpet`) and the Underway's two random lineups (`ch01_underway_shoals`, `ch01_underway_limpet`) are a logged **tutorial** exception: `naive` 80–100%, so a first-time masher doesn't lose a tutorial fight. `role_answer` and `smart` stay on the regular band.

## Consequences
- **Easier:** any later tutorial fight can lend the skill it teaches without touching the hero's base kit or the Lattice.
- **Harder:** a lent skill doesn't persist. After Ch1, Rhen has Kick Off only once he learns `rh_03`. That's a Design call (M3-C01-03 asks it): should Ch1 grant the node outright?
- **Watch:**
  - Hullgnaw is tuned for a full-HP Rhen. The chapter flow rests him before the fight (a `rest` zone step, Ch01Zone). If Design drops that rest, re-tune with the scuttlers' carried damage.
  - `role_answer` is weak in every solo fight by construction, and that's why it's report only here.
