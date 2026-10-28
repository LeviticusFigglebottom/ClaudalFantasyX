---
id: M3-ENV-101
title: "Request: a save-shrine model (Haluna's save shrine is the last primitive the slice's field shows)"
role: environment
status: review
owner_session: "session_01YbaV2c8yquRHqj6afQYg89 (env-art)"
depends_on: []
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
In the M2 slice's field, the only primitives still visible at runtime are Haluna's save shrine
(`game/world/save_shrine/save_shrine.tscn` `Visual/*`): cylinders for the base, step, pillar, cradle and canopy,
a sphere for the salt-glass core, a torus conduit and two box posts. That came out of slice-polish's runtime audit
for the human's "primitive moments": a headless walk of every slice scene listing visible PrimitiveMesh instances.
- **Clean:** the causeway, the shrine, and the First Verse (now in the real shrine, M2-FP-116).
- **Still primitive:** the Prologue's whole set (M3-ENV-100) and this shrine.
- Neme's bag (a box) is a prop for creatures.

## The look (already decided)
- **haluna.md §2:** "a shell-niche in a coral pillar with a perpetual oil flame", styled to Haluna.
- **save_shrine.gd and the art color script, rule 2:** the core is bound light: a salt-glass core in
  `glimmer_bound`, with a GlimmerField in MACHINE mode that holds perfectly still.
- **Per region:** the shrine appears in every zone with one (ShrineNetwork). A base model plus per-region trim
  (Haluna's coral, later kits' stone) would serve them all.

## Acceptance criteria
- [x] A kit piece (or a small set) under `assets_src/`, with PROVENANCE rows, sized to the current `Visual`:
  - the Interactable's shape and the GlimmerField's placement stay valid;
  - the core sits where `Visual/Core` is, because the glimmer holds there.
- [x] A swap-in note for the save shrine's owner. Systems owns it; in this account that work goes to ui-menus,
  per CONSOLIDATED.md. Cinematics can do the swap if the Lead prefers.

## Notes (slice-polish, 2026-10-28)
- Swapped in on claude/m2-slice per env-art's note (eeecf13d). `save_shrine.tscn`'s `Visual` is now one
  `save_shrine.glb` and the `save_shrine_core.glb` at (0, 1.92, 0); BoundGlimmer, `Shape` and `Body` are unchanged.
  The kit's import puts `kit_bound_core` on the core as a surface override, so it glows `glimmer_bound`.
  `test_save_shrine` reads it with `get_active_material`.
- `test_slice_primitives` no longer allows the shrine.
- **Still to view:** the niche opens toward +Z, and Haluna's `SaveShrine` (env-art's `haluna_dressing.tscn`)
  keeps its yaw. Check the field shot `save_shrine_field` and Haluna in the next render.

- 2026-10-28 (env-art): viewed `save_shrine_field` on the current tree. The final shrine reads: the coral-stone
  plinth, the scallop hood and the salt-glass core with its glow, on the field test stage. Haluna's SaveShrine was
  seen in the walk-through (`ch02_haluna_touch`), its niche toward the lane. To review. (The shot drifts from its
  baseline: re-approve.)

## Review log
