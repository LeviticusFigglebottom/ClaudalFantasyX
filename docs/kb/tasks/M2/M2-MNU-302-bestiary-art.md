---
id: M2-MNU-302
title: Bestiary creature portraits rendered from the creatures track's models
role: ui
status: review
owner_session: "menus (claude/menus)"
reviewer: art
depends_on: [M2-MNU-301]
milestone: M2
request-from: lead
---
## Goal
Creature portraits for the bestiary: all 27 Act I creatures plus the slice's five, rendered from `claude/creatures`' models by the same pipeline as M2-MNU-301 (ADR 0120), framed from `creatures.json`'s `portrait` block.

## Acceptance criteria
- [x] The portrait renderer covers every enemy with a model; one PNG each, with a PROVENANCE row.
- [x] The bestiary page shows the portrait of a seen creature, a silhouette of an unseen one, nothing for a creature with no model.
- [x] Tests; the bestiary shots re-approved after viewing.

## Notes
- The manifest lists every creatures.json row (27, which include the slice's five), keyed by creature id, not by enemy id: an enemy finds its PNG through its `model` scene (`CreaturePortraits`), so wickfry and glassfry share one picture and an enemy that takes any existing model already has its portrait. On this branch only 5 enemies have a `model` (reef_crab, lantern_eel, gull_harrier, drownbell, spawn_polyp); `claude/m2-slice` gives 15 more their models, and all of them are covered. `test_creature_portraits.gd` fails on a creatures.json row or a modelled enemy without a portrait.
- The bestiary lists only foes the party has Read or defeated, so "unseen" means "defeated, never Read" (its page shows only the name): that foe shows a dark silhouette (`creature_portraits.json → silhouette_unread`).
- Framing overrides in `tools/portraits/portraits.json` (creatures.json is the creatures track's, untouched): ashwing and sail_leech pitch 40 (flat, edge-on otherwise); gull_harrier, stormgull and squall_wing margin 0.75 (wingspans made them small); lantern_eel yaw 70 and margin 1.0 (its profile, lure in frame); reef_crab, wallcrab, wreck_crab, tide_crawler, spar_wraith and wall_polyp margin 0.95 (legs or frame cut at 0.85).
- The portrait is 184 px at the 1920 reference: wider pushed the page panel past its rect (the English stat row needs about 690 px).

## Merge note (menus, after the agent)
The UI track built a live bestiary portrait the same day (M2-UI-26, `BestiaryPortraitSlot` over the creatures track's `CreaturePortrait`, silhouette for an unread foe). The bestiary is the UI track's page, so the merge into claude/menus keeps their page and drops this task's page wiring and its page test. Kept: the renderer's creature support, the 27 baked PNGs with PROVENANCE rows, `CreaturePortraits` and `CreaturePortraitFrame` (tested), ready for any screen that wants a still picture without a viewport. For the Lead / UI: if the live slot costs too much on a weak machine, the baked PNGs can stand in for it (ADR 0120).

## Review log
