# 0110 — The bestiary shows the baked creature portraits, not a live viewport

- **Status:** accepted
- **Date:** 2026-10-25
- **Roles affected:** ui, character (creatures), rendering
- **Author role:** ui (ui-menus track)

## Context
Two tracks built a bestiary portrait on the same day (2026-10-24). The UI track's `BestiaryPortraitSlot` (M2-UI-1000, then numbered M2-UI-26) showed the creatures track's live `CreaturePortrait`: a SubViewport rendering the creature's battle model. The menus track's M2-MNU-302 baked one PNG per creature with `tools/portraits/render.sh` under ADR 0120, which chose baked portraits for every menu. The merge kept the live one in use and the PNGs unused, and the menus track's handover asked the Lead which to keep.

## Options
1. **Keep the live viewport.** Model changes show at once, but every step through the book loads a creature model (meshes, skeletons, shaders) and renders it in a second world. On a weak machine that is a hitch per step (ADR 0029's 50 ms visible-frame budget) and a constant render cost while the page is open.
2. **Use the baked PNGs** through the same slot: the same layout, the same silhouette for unread foes, a small texture per step.
3. Keep both, chosen by a setting.

## Decision
Option 2. `BestiaryPortraitSlot` keeps its fit (square in the page's leftover corner, `min_px` to `max_px`) and its silhouette shader, and draws `CreaturePortraits.texture(enemy_id)` in a TextureRect. ADR 0120 already chose baked portraits for every menu for the same reasons; a setting would double the paths to test for no player-facing gain.

## Consequences
- The bestiary costs one small texture per step on every machine, and shows the same picture everywhere.
- A creature model change needs a re-render (`tools/portraits/render.sh --only <creature>`) and a commit, as ADR 0120 says for heroes. The glossy black creatures get a stronger light in that render (`light_scale` and `stage_environment` in `tools/portraits/portraits.json`).
- `CreaturePortrait` (live) stays available to any screen that wants a turning creature. The bestiary no longer instances it.
- The `bestiary_menu` shot changes once, from the live render to the baked picture.
