---
id: M3-RND-27
title: "Request: Act I's two story VFX still drawn as glowing boxes: Ch7's weeping column, Ch8's storm wall"
role: rendering
status: review
reviewer: cinematics (the requester)
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC, claude/env-art-b; rendering's zone looks, Lead 2026-10-28)"
depends_on: [M3-C07-1211, M3-C08-1210]
milestone: M3
request-from: cinematics
---
## Goal
ADR 0041 (Act I at final quality): the last two greybox blocks on Act I's path that are effects, not props. Each is an
emissive box in its zone's `greybox.keep` until a VFX replaces it (act1-chapters then drops the id and parents the
effect to the block so the story's show/hide drives it):

| Zone | Block | What |
|---|---|---|
| ch07/tamsule_bell_galleries | `Column` (0.5 x 31.5 m, pale cyan, from the pool up to the drop) | the Bell's weeping column: a thin unbroken fall of water from the drop to the pool, lit from within, its spray where it lands |
| ch07/tamsule | `BellColumn` (0.5 x 22 m, the same fall seen from the port, z -40) | the same weeping column at the port's distance (the Bell kit now hangs there too) |
| ch08/coilspire | `StormWall` (shown from `ch08_virel_bound`) | the storm seen from the gallery after the binding: a wall of rain and cloud on the sea |

## Acceptance criteria
- [x] Each effect as a scene under `game/vfx/` (or a shader on a mesh), reproducible, with PROVENANCE rows where assets.
- [x] act1-chapters places them and drops the blocks from `greybox.keep`
      (`tools/act1/ch07_tamsule_bell_dressing.py`, `tools/act1/ch07_tamsule_port_dressing.py`,
      `tools/act1/ch08_coilspire_dressing.py`).

## Notes (env-art-b, 2026-10-28)
Both are in place on `claude/env-art-b` and no zone keeps a box (`greybox.keep` is empty in all three; the Lead gave
the Ch5–Ch9 dressing generators to env-art-b alone, so env-art-b placed them):
- **Ch7's weeping column** (galleries and port): the kit piece `weep_column` (`assets_src/environments/kits/tamsule_bell/
  b_column.py`, PROVENANCE row; M3-ENV-1321), now the contract's 0.8 → 0.6 m fall, in the zones' turquoise, lit-from-
  within `weep_column_water_material`, with its spray crown and ripples. It follows the `Column` block in the galleries
  and stands under the port's Bell on the Bell's axis (the port's `BellColumn` block is the old greybox's z -40). Over
  it, the held drop itself is now Rendering's `WaterSphereRig` "tamsule_drop" (M3-RND-26, ce10e96a).
- **Ch8's StormWall:** Rendering's Undertow (`UndertowStorm`, a ZoneKitDressing `storms` row) following the
  `StormWall` block, so `ch08_virel_bound`'s state shows it; hidden, it stops processing (M3-ENV-1308, with the
  camera's far plane past it). The VFX is under `game/vfx/undertow/`.
Viewed: `ch07_bell_galleries`, `ch07_bell_moorings`, `ch07_tamsule_gantry`, `ch08_coilspire_storm`.

## Review log
