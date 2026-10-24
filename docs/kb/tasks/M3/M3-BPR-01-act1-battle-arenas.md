---
id: M3-BPR-01
title: Act I battle arenas and their presentation (encounter arena ids, greybox fallbacks, per-arena staging)
role: combat
status: todo
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-07]
milestone: M3
request-from: lead
---
## Goal
Every Act I fight gets an arena (the M2-BPR-07 / M2-ENV-11 contract: docs/kb/tech/battle_presentation.md "Arenas",
docs/kb/tech/battle_arenas.md). The encounters are m2-slice's (game/data/battle/encounters.json on claude/m2-slice:
ch01_*, ch03_causeway_*, ch04_*, ch05_*). Proposed arenas, graded from the color script, each from env-art's zone
kit for that place:

| Arena id | Encounters | Place and grade (color_script.md) | Env-art kit |
|---|---|---|---|
| `oruvel_raft_morning` | ch01_wickfry, ch01_oil_slug, ch01_scuttlers, ch01_hullgnaw | Oruvel raft-town deck, Ch1 10:30 (sun 58°, key #FFEFE1 3.0, exposure 0.65) | M3-ENV-05 / raft-town |
| `underway_tower` | ch01_shaft_limpet, ch01_underway_shoals, ch01_underway_limpet | the drowned tower, underwater: only Rhen's oil lamp and held cyan motes (Ch1 note; underwater.md) | M3-ENV-05 lamp-diver seafloor |
| `causeway_route_afternoon` | ch03_causeway_shore, ch03_causeway_harrier | the Saltgrass Causeway route at 14:30 (lut_ch02_noon, haluna.md) | M2-ENV-10 causeway route |
| `derelict_deck_night` | ch04_sail_leeches, ch04_bottle_hermit, ch04_spar_wraith, ch04_derelict_* | a derelict's deck under the Ch4 night sky (key #FFB16E lamp 1.2, sea-glow, exposure 1.10) | M3-ENV-02 Brine Shoals |
| `ash_terrace_lanternfall` | ch05_stair_*, ch05_cinder_matron | Terraces of Ash, Ch5 festival night (key #FFA757 1.6, fog #5A3A2E, exposure 1.05) | M3-ENV-03 Terraces of Ash |

## Acceptance criteria
- [ ] Arena ids agreed with env-art (request M3-ENV-06) and m2-slice (the encounter rows' `arena` fields)
- [ ] Greybox fallbacks graded from the color script until each kit lands; arenas.json rows; shots viewed
- [ ] Per-arena staging where the place asks for it (underwater: shorter runs, slower falls; a deck: no run past its rail)
- [ ] Tests (the arena data test covers every arena; the loader keeps capture fixtures on the sandbox)

## Notes
- Lead queue 2026-10-24 item 4. Starts when big7 (with m2-slice's Act I encounters) lands on the integration branch.

## Review log
