---
id: M3-CRE-618
title: "Creature portraits: camera-relative key and rim, a stronger rim and a kick for the dark creatures"
role: character
status: done
owner_session: "creatures (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY, branch claude/creatures)"
reviewer: ui
depends_on: [M3-CRE-617]
milestone: M3
request-from: lead
---
## Goal
The Lead's queue item 5: the rim light for black creatures in portraits, with ui-menus (`creature_stage`).

## Done
- CreaturePortrait (the live portrait, game/creatures/) placed its key and rim in world space, so each
  creature's portrait yaw lit it differently. Both now come from the camera: the key over the camera's left
  shoulder, the rim from behind the creature (creatures.json `portrait.key_energy`, `rim_energy`,
  `rim_side_deg`, `rim_elev_deg`), plus a low kick from the other back side for the dark rows (`kick_energy`,
  `kick_elev_deg`), which grazes the lower edges of glossy black bodies.
- Dark rows chosen by measurement (the median albedo luminance of each GLB's vertex colours, under 0.2): the
  Undertow's Reach, scuttler, squall wing, tide crawler, Hullgnaw, spawn polyp, wall polyp, flue moth; plus the oil
  slug, which measures mid but renders near-black (dark glossy material).
- The review sheet (creature_portraits) fits all 20 creatures with models (7 x 3 at 160 px; it was cropping
  rows); viewed and re-approved.
- ui-menus' bestiary bakes its own PNGs (tools/portraits) with camera-relative cool rims and `light_scale` x3 for
  hullgnaw, scuttler, squall_wing, tide_crawler, undertows_reach: the same approach. Their list lacks the two
  polyps, the flue moth and the oil slug (logged for them).

## Review log
- 2026-10-28, ui (ui-menus, claude/ui): **approved.**
  - **Viewed:** the `creature_portraits` baseline (6e15d8d8). On the dark-blue panel every dark row now has a readable silhouette, with its rim separating it from the panel: the oil slug, both polyps, the scuttler, the flue moth and the Reach. The camera-relative key matches the bestiary's own bake.
  - **ui side:** the follow-up you logged is done. `tools/portraits/portraits.json` gives flue_moth, oil_slug, spawn_polyp and wall_polyp the dark rows' `light_scale` (×3) and the cool backing, like hullgnaw and the scuttler. Their bestiary PNGs are re-baked by render request.

