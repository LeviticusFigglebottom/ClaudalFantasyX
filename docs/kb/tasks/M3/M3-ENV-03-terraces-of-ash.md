---
id: M3-ENV-03
title: Ch5 Terraces of Ash: Pemakar town, the terrace channels and graves, the Lanternfall festival (kit at final quality)
role: environment
status: todo
owner_session: ""
depends_on: [M2-ENV-06]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The Lead's env-art standing queue (2026-10-24; the human authorised M3 work in parallel): Ch5 "Terraces of Ash" from
docs/kb/story/beats/act_outline.md, zone `ch05/pemakar`. Pemakar, a terraced town on a stair-mountain under an ash-plume: terrace channels among the graves carrying a thousand leaf-boats at Lanternfall (pillar 2: beauty in decline), copper veins in the rock (the temple trial walks a strike down them; Ashcrown temple itself is a later task), a smithy (the side scene), volcanic stone and ash palette (`volcanic_stone`, `laterite`).

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

## Notes
- 2026-10-24 (env-art): **PAUSED for the M2-review blockers (Lead), WIP committed.** Done: design notes
  `docs/kb/art/environments/pemakar.md` (committed first); kit source `assets_src/environments/kits/pemakar/`
  (25 pieces in budget: terraces, walls with copper vein, channels/inlets/spills with cross channels, paddy,
  stair, graves, open-hand gate, lamp pillar, leaf-boat, shrine-box, two houses, smithy, massif, Ashcrown
  silhouette, plume; textures, materials, import settings, layout generator writing ~940 boats / 376 lamps /
  5,000 far lights); preview scene `game/levels/_tests/pemakar_kit/` (PemakarKitPreview, dusk/night moods,
  7 cameras, shots manifest); shaders env_ash_plume, env_far_lights, env_sky_pemakar.
  **Not committed:** the generated assets under `assets/environments/kits/pemakar/` (no PROVENANCE rows yet;
  regenerate with build.py via Blender, pemakar_textures.py, pemakar_materials.py, pemakar_import_settings.py,
  then `godot --import`). No Blender job, no tests, no shots registered yet.
  **Next step:** (1) rework P01 as the view from the harbour looking north (sea-glow foreground, town lights,
  mountain far lights, Ashcrown, plume; ~50 mm, camera about (-20, 6, 130)) and update pemakar.md §5 to match;
  (2) plume: darker (fog_disabled, body_darken ~0.2), lumpier silhouette, afterglow rim; (3) far lights spread
  lower and thinner near the crest; (4) render P05-P08 and iterate; (5) add the `pemakar_kit` Blender job to
  tools/dev/blender_builds.json (sources: pemakar/*.py + haluna kit_common.py, village.py, shrine_interior.py),
  commit assets + PROVENANCE rows, Python tests (tools/tests/test_pemakar_kit.py) and a GDScript test for
  PemakarKitPreview; request a `pemakar_kit` import kind from Tools; register at most 2 shots (P01, P03).
  P03 (dusk, among the graves) already reads well on lavapipe.

## Review log
