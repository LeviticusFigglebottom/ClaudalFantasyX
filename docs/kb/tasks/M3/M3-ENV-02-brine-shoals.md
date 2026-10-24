---
id: M3-ENV-02
title: Ch6 Brine Shoals: the route of wrecks and mud-flats, and the burning Saltwright camp (kit at final quality)
role: environment
status: doing
owner_session: "env-art"
depends_on: [M2-ENV-06]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The Lead's env-art standing queue (2026-10-24; the human authorised M3 work in parallel): Ch6 "Salt Edict" from
docs/kb/story/beats/act_outline.md, zone `ch06/brine_shoals`. A route of wrecks and mud-flats with a shoal channel deep enough for Sefir's white barge (poled, no wake). The Saltwright salvage camp the Order raid burns: tents, racks, crates, salvage piles, brine-branding gear, and its burned state (smoke, char, embers) as a variant. The tideline where Liss buries a lamp.

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
