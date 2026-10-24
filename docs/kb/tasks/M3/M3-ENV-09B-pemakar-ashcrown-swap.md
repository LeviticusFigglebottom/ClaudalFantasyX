---
id: M3-ENV-09B
title: "Pemakar's far Ashcrown from the Ashcrown kit's LOD1 (one building at every distance)"
role: environment
status: doing
owner_session: "env-art"
depends_on: [M3-ENV-09]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Follow-up to M3-ENV-09, from its worker. The Pemakar kit draws Ashcrown as `ashcrown_silhouette`, while the new
Ashcrown kit is the same building up close; its origin is the silhouette's (0, 306.72, -682) in Pemakar's frame.
Replace the silhouette in `assets_src/environments/kits/pemakar/pemakar_layout.py` (and in the arena
`ash_terrace_lanternfall`, which places the layout's skyline) with the Ashcrown kit's LOD1 pieces, so the temple
is one building at every distance.

## Acceptance criteria
- [ ] Pemakar's preview and the Lanternfall arena place the Ashcrown kit's LOD1 at the silhouette's transform.
      The silhouette is retired or kept only as the far LOD.
- [ ] Re-capture `pemakar_p01_waterfall_of_fires`, `pemakar_p03_among_the_graves` and
      `battle_arena_ash_terrace_lanternfall`, view them, and re-approve only with a stated reason.
- [ ] `verify_blender_builds` is identical for every job touched, and `test_pemakar_kit` and `test_arenas` pass.

## Review log
