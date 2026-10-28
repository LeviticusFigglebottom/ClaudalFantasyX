---
id: M3-CRE-661
title: "Request to characters: four small villager-pipeline options the crowd needs (line-marks and brand, LOD1-only, path constants, hand props)"
role: character
status: todo
owner_session: ""
depends_on: [M3-CRE-659]
milestone: M3
request-from: creatures
---
## Goal
ADR 0152. The crowd villagers (M3-CRE-659: 22 bodies, 56 Act I people) are built through your villager modules,
imported and unedited (assets_src/crowd/build_crowd.py). Four things need a change on your side; the details are in
docs/kb/tasks/M3/M3-CRE-659-crowd-villagers.md, "Requests to characters".
1. **Saltwright line-marks and the brine-brand.** villager_textures paints only Low Reaches reach-bands, so the Brine
   Shoals wrights' forearms are bare. That is the visible story beat at act1_ch06 W06. The ask is `_skin.line_marks`
   and `_skin.brand` blocks.
2. **`_build.lod1_only`.** The crowd ships LOD1 only, and LOD0's build is a third of each Blender run.
3. **`OUT_ROOT` / `TEX_ROOT` constants** in write_materials and villager_clips, so a caller sets them instead of
   monkey-patching.
4. **Hand props** for the work clips (broom, basket, net section, leaf-boats), M3-CRE-614, on a hand bone any
   villager-schema body can carry.

Item 1 blocks the wrights' final read; 2–4 are cleanups. Tell creatures when they land, and the crowd regenerates.

## Review log
