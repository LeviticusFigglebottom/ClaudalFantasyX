---
id: M2-CHR-11
title: Host-independent builds for base_body, Rhen, Toma and the villagers (M1-CHR-14's snaps)
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
reviewer: lead
depends_on: [M1-CHR-14]
milestone: M2
request-from: lead
priority: top
---
## Goal
The PC's Blender gate showed 10 diffs on its AVX2 host for base_body, rhen, toma and the villager jobs. Asha is already host-independent (M1-CHR-14). Opt every other character job into the same snaps and rebuild once:
- MIDLINE_SNAP on head coordinates;
- snap_shape_noise (shape deltas on a 1 µm grid);
- quantize_uvs (UVs on a 2^-16 grid);
- asha_textures.PRE_ROUND in the texture runs.

## Acceptance criteria
- [ ] rhen and toma opted in (carried by M1-CHR-15, which rebuilds them anyway).
- [ ] base_body and the seven M2 villagers opted in. Tavi and Kell already are, through their params.
- [ ] `verify_blender_builds.py` identical for every character job, both natively and with NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4" (the AVX2-only numpy paths).
- [ ] Changed shots viewed. The changes should be invisible, at RMSE ~1e-4.

## Notes

## Review log
