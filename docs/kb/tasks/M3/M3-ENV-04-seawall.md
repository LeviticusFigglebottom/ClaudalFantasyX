---
id: M3-ENV-04
title: Ch8 the Seawall: Corrow Bastion, the Fisher Stair and the Watchers (kit at final quality)
role: environment
status: todo
owner_session: ""
depends_on: [M2-ENV-06]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The Lead's env-art standing queue (2026-10-24; the human authorised M3 work in parallel): Ch8 "The Seawall" from
docs/kb/story/beats/act_outline.md, zone `ch08/corrow`. Corrow's nine-hundred-year seawall: the wall-head, the Fisher Stair up from the low town (wide enough to matter, not wide enough), the carved Watchers' faces (Liss bolts a hoist into them), the low town at the stair foot, the Coilspire beacon on the skyline (the temple is a later task). Storm-lit: the Undertow set-piece; a destroyed state (the wall falls) as a variant or follow-up.

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
