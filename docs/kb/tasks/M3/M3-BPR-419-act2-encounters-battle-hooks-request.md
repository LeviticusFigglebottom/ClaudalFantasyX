---
id: M3-BPR-419
title: "Request: Act II boss encounters, use the staged ids (arena, enemy and phase), so their battle presentation is live on day one"
role: combat
status: todo
owner_session: ""
depends_on: [M3-BPR-418]
milestone: M4
request-from: combat
---
## Goal
To act1-chapters (or whoever writes the Act II enemies and encounters; M4-C10..C15 "Next: … its encounter with sim
bands"). Battle-presentation has staged the Act II bosses ahead of their data (M3-BPR-408, 418), keyed by ids. The
encounters only need to use those ids, and every intro, moment, telegraph and arena works with no change on this
side.

## What to keep
| Boss (creatures' scene) | Enemy id | Phase id | Arena id (encounters.json `arena`) | Staged |
|---|---|---|---|---|
| The Mangrove Drowner (Ch10) | `mangrove_drowner` | `uprooted` (its creatures.json phase) | `ossa_fen_roots` (env-art M3-ENV-718) | intro (boss_tall), tearing-free moment |
| The Lamp Engine (Ch11) | `lamp_engine` | `opened` | `lowlight_engine_hall` (env-art) | intro (boss_tall), the opening moment |
| The Avalanche Ram (Ch12) | `avalanche_ram` | any | `keth_seep_terrace` (env-art M3-ENV-717; your Keth Pass RamArena: the shelf under the seeping wall) | intro, side-on framing, charge gather plus camera pressure |
| The Wakefin (Ch15) | `wakefin` | any | `bridal_barge_night` (env-art) | intro, blade-under gather plus camera pressure (no light) |

- A charged skill (a skill row's `charge`) reads on stage automatically (BattleTelegraph or the boss row).
- The Ch10–12 regulars need nothing: the model fit, spacing and line-up work from their creature models.
- The arenas are env-art's final kits (claude/env-art, rendered on the Lead's gate). If a story place needs a
  different one, ask env-art.

## Acceptance criteria
- [ ] The Act II boss encounters use the enemy, phase and arena ids above (or a reply here naming the new ones).
- [ ] Battle-presentation then adds the boss-intro and charge shots (M3-BPR-408/418's open items) and requests renders.

## Review log
