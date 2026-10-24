---
id: M3-ENV-05
title: Ch1 the lamp-diver's sea floor: Oruvel Underway, the drowned tower (kit at final quality)
role: environment
status: todo
owner_session: ""
depends_on: [M2-ENV-06]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The Lead's env-art standing queue (2026-10-24; the human authorised M3 work in parallel): Ch1 "Lamp-Diver" from
docs/kb/story/beats/act_outline.md, zone `ch01/oruvel_underway`. Rhen's tutorial dive: a drowned tower and the sea floor around it, lit by his lantern, under the underwater look from M2-RND-02 (docs/kb/tech/underwater.md, the M2-ART-02 sign-off and its M2-RND-09 fixes). Salvage, collapsed floors, seagrass and coral growth, Lit Age fragments, the Hullgnaw's ship's ribs as a landmark.

Gameplay placement (spawns, triggers, NPCs, collision tuning) is m2-slice's: hand it over as swap-in notes in
docs/kb/handoffs/live/env-art.md.

## Acceptance criteria
- [ ] **Design notes first:** `docs/kb/art/environments/<zone>.md` in the haluna.md format (mood in one line,
      layout and orientation, lighting sub-frame and grade from color_script.md, kit table with dimensions,
      materials against palette.json, composed shot list with lenses), reviewed against the act outline and the
      story bible before any geometry; references in words only (references.md).
- [ ] A procedural kit in `assets_src/environments/kits/<zone>/` with its own Blender job, LOD0/LOD1 within
      budgets and chained per vegetation.md "One LOD at every distance", vertex-colour weathering per haluna.md
      §4, materials written by script, PROVENANCE rows, `verify_blender_builds` byte-identical, every file under
      5 MB, no reference images, packs or AI generation.
- [ ] An Environment-owned preview scene with composed views of the design notes' key shots, viewed on lavapipe
      and iterated to final quality (pillar 2, the palette, the colour script). Register at most the two most
      telling shots as screenshot baselines (the repo's binary budget).
- [ ] Tests for anything with runtime code; a swap-in note for m2-slice.

## Review log
