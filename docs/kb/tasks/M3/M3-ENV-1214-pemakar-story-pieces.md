---
id: M3-ENV-1214
title: Pemakar's story pieces the kit lacks (the sea-cut weir, the wake-wall, the crown bell, a harbour quay) and a day grade
role: environment
status: todo
owner_session: ""
depends_on: [M3-C05-1213]
milestone: M3
request-from: cinematics
---
## Goal
act1-chapters dressed `ch05/pemakar` with the Pemakar kit (M3-C05-1213). act1_ch05.md §10 item 1 lists pieces the
kit doesn't have yet; the zone uses greybox stand-ins or kit modules for them:
- **The sea-cut weir** (the hero mesh: "the last stone lip where the channels spill into the sea"; B05's P11/P12).
  Stand-in: the greybox block `SeaCutWeir` in the water off the quay's east end (x 10, z 27.7).
- **The wake-wall** for name-boards at the harbour (greybox `WakeWall`, x 8, z 22.7, at the quay's back).
- **The crown bell** at the top tier (greybox `CrownBell`).
- **A harbour quay**: today a row of `terrace_wall_4m` / `terrace_tread_4m` modules at the shore (front z 27, top
  y 1.2), the slope behind meeting it at z 22.7.
- **A day grade** for B11 (the day after the binding): the zone uses `pemakar_dusk_environment.tres` as a stand-in.

Each piece can be dropped in by naming it in `tools/act1/ch05_pemakar_dressing.py` (the greybox block it replaces
is named above; give it `"block": <id>` so it follows the story).

## Acceptance criteria
- [ ] The pieces exist in the Pemakar kit with PROVENANCE rows; the day grade exists.

## Review log
