---
id: M3-ENV-1331
title: "Corrow kit: laterite_blocks albedo and normal at a higher resolution (Coilspire's gate reads blocky up close)"
role: environment
status: todo
owner_session: ""
depends_on: []
reviewer: environment
milestone: M3
request-from: environment (env-art-b)
---
## Goal
The PC's pass 7, row 84: up close at the Coilspire gate the laterite's speckle is blocky and low resolution.
- **The cause:** `cs_laterite` and `cs_laterite_inner` map `assets/environments/kits/corrow/textures/laterite_blocks_albedo.png`
  (512 px) over `tile_m` (6, 1), about 85 px a metre. The pores are a few texels each, so at the gate's close view
  they read as square blots.
- **What env-art-b did in its own zone copy** (`coilspire_inner_material.tres`, the inner laterite): calmer pores
  (cavity 0.3, normal 0.9) and a finer detail grain (0.15 m). This softens the blots but doesn't remove them.

## Ask (env-art's kit textures)
Bake `laterite_blocks_albedo.png` and `_normal.png` at 2048 px, or at 1024 with a finer pore pass, from the kit's
texture generator, and re-import. The tiling stays (6, 1), because the courses are mapped to the geometry.

## Acceptance criteria
- [ ] `ch08_coilspire_gate` and a 1 m close view of the gate wall show round pores, not square blots.

## Review log
