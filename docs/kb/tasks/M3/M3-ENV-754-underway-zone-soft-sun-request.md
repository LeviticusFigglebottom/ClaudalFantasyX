---
id: M3-ENV-754
title: "The Underway zone's sun casts hard-edged lit panes on the floor (request to slice-polish)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
env-art's Prologue–Ch4 audit (2026-10-29, `lead/gate-big18`, player-eye stills) shows hard-edged, bright rectangles of
sun on the Underway's floor under every window and breach (the gallery, the gauge room, the bell-rest). It is the same
defect the PC's GPU QA found in the Underway battle arenas (rows 15, 40), fixed there in M3-ENV-1323: under 21 m of water
the light comes through the surface, so a window's shadow can't be crisp.

The zone's sun is built by `GreyboxZone._build_lighting()` (`game/world/zone/greybox_zone.gd`) from the layout's `sun`
row (`game/levels/ch01/oruvel_underway/oruvel_underway_layout.json`, slice-polish's), and it sets no angular size or
blur. env-art doesn't own either file.

## Ask
- [ ] Let a layout's `sun` row carry `angular_deg` and `shadow_blur` (applied only when present, so other zones are
      unchanged), and set the Underway's to **9.0** and **4.0**, the arenas' values (M3-ENV-1323).
- [ ] Re-render `ch01_underway_crown`, `ch01_underway_gallery` and `ch01_bell_room`: soft pools, no panes.

## Review log
