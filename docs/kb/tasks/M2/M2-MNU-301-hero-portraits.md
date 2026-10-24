---
id: M2-MNU-301
title: Hero portraits in every menu, rendered from the characters track's models
role: ui
status: review
owner_session: "menus (claude/menus)"
reviewer: art
depends_on: [M2-MNU-05]
milestone: M2
request-from: lead
---
## Goal
The human's playtest note: "parts look primitive". Replace every placeholder initial or box in the menus (Status, Equip, Lattice, Formation, Shop) with real portrait renders of Rhen, Asha and Toma, made from the characters track's models by a reproducible lavapipe portrait renderer under `tools/`, with a PROVENANCE row for each image. Add expression variants where the face shapes allow. See ADR 0120.

## Acceptance criteria
- [x] `tools/portraits/` renders every portrait from source (the hero `.glb`, hero materials, face poses) on lavapipe; one command rebuilds them all.
- [x] Portrait PNGs under `assets/ui/portraits/heroes/`, each with a PROVENANCE row.
- [x] Expression variants (neutral plus those the face poses allow).
- [x] A small `HeroPortraits` lookup (id + emotion → texture, falling back to neutral, then to the old initial).
- [x] Status, Equip, Lattice, Formation and Shop show them; tests; shots re-approved after viewing.

## Notes
- **Renderer.** `tools/portraits/render.sh` (one lavapipe Godot process per manifest entry, as `capture.sh`) runs `tools/portraits/portrait_renderer.tscn` over `tools/portraits/portraits.json`. Each hero's own review stage (`game/levels/_tests/characters/<hero>/..._stage.tscn`, an `AshaStage`: glb, hero materials, shader tier, face pose from the emotion tag, pinned wind, Face camera on the eye midpoint) is instanced unchanged into a transparent SubViewport at 2x, with the manifest's framing (distance 1.0 m, yaw 18°, pitch 4°, aim 6 cm under the eyes, fov 24°), the floor and cyclorama hidden and the sky background off, and Lanczos-reduced to 256 x 256 RGBA after 24 frames. Byte-identical on a rerun. Options: `--only rhen`, `--emotions neutral,grief`, `--out DIR` (previews). The manifest has an empty `creatures` list and the renderer a `_render_creature` hook for M2-MNU-302.
- **Expressions.** neutral, smile, determined, worried, grief for each of Rhen, Asha and Toma (15 PNGs; every hero's pose table defines all fifteen tags; these five read best at menu size). Pages use them through `game/data/ui/hero_portraits.json` `pages`: Status and Formation neutral (worried for a fallen hero), Equip and Lattice determined.
- **Game side.** `HeroPortraits` (game/ui/menus/hero_portraits.gd, Node-free): `texture(hero, emotion)` falls back to neutral, then null; `face()` is the head crop (`face_region`). `HeroPortraitFrame` (game/ui/menus/hero_portrait_frame.gd): a PanelSmall frame with the picture (cover-cropped) or, without one, the hero's initial (Ysolde today).
- **Pages.** Status: a 171 px portrait left of the name and gauges (vitals narrowed to 315). Equip: the heroes page narrowed to 222 (names only) with a 138 px portrait beside it. Formation: a 150 px portrait at the top left of the detail, the detail's lines indented by it. Lattice: an 84 px head crop right of the "< Rhen > 1 of 3" line. Rects in each page's layout JSON.
- **Shop:** it shows no hero anywhere (Buy / Sell / Leave, goods, purse), so nothing to replace there. The Lattice overview's woken-by letters (M3-MNU-04 "R", "A", "T" beside nodes) are board marks, not portraits; left as they are.
- **Shots re-approved after viewing:** status_menu, equip_menu, equip_customize, formation_menu, lattice_menu, lattice_menu_activate, lattice_overview (diffs only in the portrait areas and the shifted vitals / hero line).
- **Tests:** tests/unit/test_hero_portraits.gd (manifest ↔ PNG ↔ PROVENANCE ↔ stage sources, fallbacks, frame initial, each page's TextureRect follows the cursor; the Status portrait clears every detail control).
- A model change does not update the portraits by itself: rerun `tools/portraits/render.sh` and commit the PNGs (ADR 0120).

## Review log
