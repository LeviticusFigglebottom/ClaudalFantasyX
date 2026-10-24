---
id: M1-UI-11
title: A preset change in the Graphics menu runs the resident shader warm-up in view (hold it behind a fade)
role: ui
status: todo
owner_session: ""
reviewer: architect
depends_on: [M1-UI-10, M1-RND-22]
milestone: M1
request-from: "lead"
---
## Goal
Review-sweep-Q on M1-UI-10. Criterion 2 there said "apply behind a short fade if a change hitches". The task skipped the fade because "the page lives on the 2D title, so a change can't visibly hitch". That stopped being true when M1-RND-22 merged. `GraphicsRuntime.select_preset` now calls `warm_resident_shaders(viewport)` once boot has armed it. That is the boot warm-up the PC measured at a 0.53–1.66 s worst frame (docs/kb/qa/gpu/2026-10-24-rnd-22-prewarm.md), and here it runs in full view on the title. Pressing confirm on a preset can freeze the menu for over a second.

## Acceptance criteria
- [ ] Choosing a preset fades the screen (or shows a held "Applying" card, through a loc key) and waits until the resident warm-up's `ShaderPrewarm` node is done (or its `finished` signal fires) before it fades back. The cursor and input are blocked meanwhile.
- [ ] A setting override that changes a tier (the character, water, vegetation, weathering, Undertow or underwater tiers) does the same if it spawns a warm-up. If it doesn't spawn one, say so in graphics_settings.md.
- [ ] Test: select a preset with GraphicsRuntime armed. The menu is inert until the warm-up node frees, and the fade then lifts.
- [ ] The `boot_title` shot doesn't move.

## Review log
