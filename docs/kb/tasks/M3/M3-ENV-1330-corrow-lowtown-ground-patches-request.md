---
id: M3-ENV-1330
title: "Corrow's low town ground: hard-edged cobble triangles and a flat dark plain from the wall"
role: environment
status: todo
owner_session: ""
depends_on: []
reviewer: environment
milestone: M3
request-from: environment (env-art-b)
---
## Goal
env-art-b's player-height walk of Ch8 Corrow (on big21 merged) shows two problems with the low town's ground,
`lowtown_ground` (`assets_src/environments/kits/corrow/cw_town.py` `build_ground`, env-art's kit code):
- **At street level** (the `bark_netmender` trigger, about (−35, −21)): the ground breaks into hard-edged patches.
  Light textured cobble triangles sit against dark earth, with straight jagged borders, and there are dark smooth
  hollows. The cobble is chosen **per triangle** (`f > 0.6` → `M_COBBLE`), so every patch edge follows the
  41 × 41 grid's triangles. The noise is in the tile's local frame, and the zone rotates the 24 m tiles, so
  patches also stop dead at tile edges.
- **From the wall-walk** (every stop on the walk looking north): the town's floor reads as one flat dark grey-brown
  plain between the houses.

## Proposed
- Blend cobble into earth through a vertex mask (a weight in a spare vertex-colour channel, or a second UV), not
  per-triangle material. Or drop the cobble patches and let the earth material carry a worn-path tint.
- Sample the noise in world space, or fade the cobble out toward the tile edges as the heights already do (`edge_fade`).
- A bit more value variation in the earth at 20–60 m (tracks, drying salt) so the plain doesn't read flat from the
  wall.

## Acceptance criteria
- [ ] No triangle-edged cobble patches and no patch edges along tile borders in env-art-b's walk stills.
- [ ] `lowtown_ground` is rebuilt; env-art-b re-renders `ch08_corrow_arrival` and `ch08_corrow_flood` and the walk.

## Review log
