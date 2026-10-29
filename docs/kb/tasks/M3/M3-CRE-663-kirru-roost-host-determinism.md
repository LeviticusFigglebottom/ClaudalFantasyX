---
id: M3-CRE-663
title: "Request to env-art: kirru_roost.glb (haluna_kit) does not rebuild byte for byte on the AVX2 host (big14 Blender gate)"
role: environment
status: review
owner_session: "env-art (claude/env-art, 2026-10-29)"
depends_on: []
milestone: M3
request-from: creatures
---
## Goal
The big14 gate's Blender step (docs/kb/qa/gate-runs/big14/blender_diffs.txt on `gpu/gate-big14-shots`) fails
`haluna_kit` on one file: `assets/environments/kits/haluna/kirru_roost.glb` (M3-ENV-718, yours). The rebuild's
`kirru_roost-lod1.POSITION` differs from the committed file.

## Likely cause and fix (what fixed the Avalanche Ram, the same gate)
numpy picks its SIMD path per host (AVX-512 on the cloud, AVX2 on the PC). On the ram, the head's midline came out at
x = 0 on one host and x = ±1e-17 on the other. Snapping coordinates under 1e-9 to 0 (and adding 0.0 to clear -0.0)
before export made it identical on all three paths. See `finish()` in
`assets_src/creatures/avalanche_ram/build_avalanche_ram.py` and docs/kb/qa/blender_builds.md §"Host determinism".
The roost's LOD1 decimate input may need the same snap, or a 1 µm grid, as the character builds use.

To reproduce in the cloud:
`NPY_DISABLE_CPU_FEATURES="X86_V4" python3 tools/dev/verify_blender_builds.py --job haluna_kit` (the AVX2 path),
then rebuild and commit the GLB once it is identical natively, under `"X86_V4"`, and under `"X86_V3 X86_V4"`.

## Fix (env-art, 2026-10-29)
- Reproduced in the cloud with `NPY_DISABLE_CPU_FEATURES="X86_V4"`: only `kirru_roost-lod1.POSITION` differed.
- Cause: the lodge's arches sample `cos(t * pi)`, whose crown (t 0.5) is ~6e-17, not 0, and differs by SIMD path.
- Fix: `ossa_fen.build_roost` snaps coordinates under `SNAP_EPS` (1e-9) to 0 and clears -0.0 before returning, as the
  Avalanche Ram's `finish()`. Only `kirru_roost.glb` changed.
- `verify_blender_builds --job haluna_kit`: 199 identical natively, under `"X86_V4"` and under `"X86_V3 X86_V4"`.
  `test_haluna_kit`, `test_ossa_fen` OK.

## Review log
