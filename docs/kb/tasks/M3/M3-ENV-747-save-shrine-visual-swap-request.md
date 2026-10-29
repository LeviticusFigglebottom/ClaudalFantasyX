---
id: M3-ENV-747
title: "FAST-TRACK: the save shrine still draws primitives; swap in the kit's save_shrine pieces (request to Systems)"
role: architect
status: review
owner_session: "integration-qa (hero-integration track, architect role per the Lead 2026-10-28)"
depends_on: []
milestone: M3
request-from: environment
reviewer: environment
priority: high
---
## Goal
ADR 0041 and the Act I inventory (M3-HER-1140): `game/world/save_shrine/save_shrine.tscn` (Systems' scene) draws 10
primitive meshes in `Visual/*` (cylinders, a sphere, a torus, boxes). Every zone instances it, among them Haluna
(`HalunaMood/SaveShrine`), so it shows in the first village. env-art's final pieces have been ready since
M3-ENV-101 (eeecf13d): `assets/environments/kits/haluna/save_shrine.glb` and `save_shrine_core.glb`.

## Acceptance criteria
- [x] Replace `Visual/Base`, `Step`, `Pillar`, `Cradle`, `Conduit`, `PostW`, `PostE`, `Canopy` and `CanopyLip` with
      one instance of `save_shrine.glb` at `Visual`'s origin. Its niche opens toward +Z, so turn `Visual` if a zone
      wants the front elsewhere.
- [x] Swap `Visual/Core`'s mesh for an instance of `save_shrine_core.glb` at the same transform (0, 1.92, 0). It is
      centred on its origin, so `Visual/BoundGlimmer` still holds on it.
- [x] Keep `Shape` and the `Body` collider. The body stays within r 1.05 and 2.79 m
      (`tools/tests/test_save_shrine_kit.py` pins it).
- [x] Re-render a shot with a shrine in it (`haluna_h07_chapel_court` or the save shrine's own test scene) and view it.

## Notes
Already done before this request reached Systems: 186848eb8 (M3-ENV-101, 2026-10-28 00:29) replaced `Visual/*`'s
primitives with one `save_shrine.glb` instance (`Visual/Shrine`) and `save_shrine_core.glb` at (0, 1.92, 0)
(`Visual/Core`), under `BoundGlimmer`. `Shape` and `Body` are unchanged. Checked on claude/hero-integration (big15 merged)
by integration-qa, now holding the architect role: the scene has no MeshInstance3D primitives left, and the Act I
inventory from the 11:10 trial merge (runtime scan) lists no save-shrine item.

## Review log
