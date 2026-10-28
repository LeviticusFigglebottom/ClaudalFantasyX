---
id: M3-RND-27
title: "Request: Act I's two story VFX still drawn as glowing boxes: Ch7's weeping column, Ch8's storm wall"
role: rendering
status: todo
owner_session: ""
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
- [ ] Each effect as a scene under `game/vfx/` (or a shader on a mesh), reproducible, with PROVENANCE rows where assets.
- [ ] act1-chapters places them and drops the blocks from `greybox.keep`
      (`tools/act1/ch07_tamsule_bell_dressing.py`, `tools/act1/ch07_tamsule_port_dressing.py`,
      `tools/act1/ch08_coilspire_dressing.py`).

## Review log
