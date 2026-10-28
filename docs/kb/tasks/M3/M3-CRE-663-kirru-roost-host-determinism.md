---
id: M3-CRE-663
title: "Request to env-art: kirru_roost.glb (haluna_kit) does not rebuild byte for byte on the AVX2 host (big14 Blender gate)"
role: environment
status: todo
owner_session: ""
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

## Review log
