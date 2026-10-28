---
id: M3-ENV-747
title: "FAST-TRACK: the save shrine still draws primitives; swap in the kit's save_shrine pieces (request to Systems)"
role: architect
status: todo
owner_session: ""
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
- [ ] Replace `Visual/Base`, `Step`, `Pillar`, `Cradle`, `Conduit`, `PostW`, `PostE`, `Canopy` and `CanopyLip` with
      one instance of `save_shrine.glb` at `Visual`'s origin. Its niche opens toward +Z, so turn `Visual` if a zone
      wants the front elsewhere.
- [ ] Swap `Visual/Core`'s mesh for an instance of `save_shrine_core.glb` at the same transform (0, 1.92, 0). It is
      centred on its origin, so `Visual/BoundGlimmer` still holds on it.
- [ ] Keep `Shape` and the `Body` collider. The body stays within r 1.05 and 2.79 m
      (`tools/tests/test_save_shrine_kit.py` pins it).
- [ ] Re-render a shot with a shrine in it (`haluna_h07_chapel_court` or the save shrine's own test scene) and view it.

## Review log
