# 0120 — Menu portraits are baked PNGs from a reproducible lavapipe renderer

- **Status:** accepted
- **Date:** 2026-10-24
- **Roles affected:** ui, art (characters, creatures), tech
- **Author role:** ui (menus track)

## Context
The human's playtest note says parts of the menus "look primitive": party pages show initials in boxes, and the bestiary shows no creature at all. The Lead asked for real portrait renders of Rhen, Asha and Toma in every menu, and creature portraits in the bestiary. These must come from the characters and creatures tracks' own models, through a lavapipe portrait renderer under `tools/`, with PROVENANCE rows (SPEC §2: every asset reproducible from source).

The creatures track already has `CreaturePortrait`, a live SubViewport that renders a creature in its own small world (M2-CRE-10). It stores no image.

## Options
1. **Live 3D portraits everywhere.** Each menu slot renders its model in a SubViewport. Model changes show up at once. But hero meshes, skeletons and hero shaders cost seconds to load and render on a weak machine for every page open, and a 4-row Formation page would hold four of them.
2. **Baked PNG portraits.** A Godot scene under `tools/portraits/`, run on the lavapipe render wrapper (as screenshot capture is), renders each hero × expression and each creature to a PNG under `assets/ui/portraits/`. Menus load a small texture.
3. A mix: bake the heroes and keep live creatures.

## Decision
Option 2. One renderer and one manifest (`tools/portraits/portraits.json`) cover heroes and creatures. The renderer reuses the characters track's stage logic (hero materials, shader tier, face poses from the emotions table) and the creatures track's `CreatureFraming` with each creature's `portrait` block, so the framing data stays with its owner. The PNGs are committed with PROVENANCE rows that name the source model and the command, and the renderer is deterministic (pinned wind, fixed frame count). `CreaturePortrait` stays available for any screen that wants a live creature.

## Consequences
- Menus open fast and show the same picture on every machine.
- A model change does not update a portrait by itself. The owning track, or whoever changes the model, reruns `tools/portraits/render.sh` and commits the new PNGs. A unit test checks that every hero, emotion and creature in the manifest has its PNG and its PROVENANCE row.
- PNGs are small (256 px heroes, 256 px creatures), far under the 5 MB limit (ADR 0005).
