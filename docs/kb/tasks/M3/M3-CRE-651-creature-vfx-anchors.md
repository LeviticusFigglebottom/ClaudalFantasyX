---
id: M3-CRE-651
title: "Creature spawn/death VFX hooks: CreatureActor.vfx_anchor() with per-creature anchors (wound, core) for the Act I regulars"
role: character
status: doing
owner_session: "creatures (session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: []
milestone: M3
request-from: lead
---
## Goal
ADR 0041 (Act I at final quality first; the Lead's refocus, 2026-10-28): every **regular** enemy a player fights in
Act I gets its real mesh, rig, full animation set (idle, hit, act, death), weak-point readout and spawn/death VFX hooks,
self-rendered and viewed at battle distance and in the bestiary portrait. The bosses and the Vowbound are creatures-b's.

The 20 regulars (encounters.json, Ch1–Ch8 plus the slice): ashwing, flue_moth, gull_harrier, lantern_eel, oil_slug,
raid_hound, reef_crab, sail_leech, scuttler, shoal_skipper, slag_tortoise, squall_wing, stormgull, tide_crawler,
tower_limpet, vein_sparker, wall_polyp, wallcrab, wickfry (glassfry's model), wreck_crab.

**The gap (audit):** effects.json maps a KO to `ko_release` (with per-creature `ko_overrides`), played at the stand-in's anchor heights; no creature exposes where its body actually is: the wound, the core. Add `CreatureActor.vfx_anchor(name)` (a world position from a bone named in creatures.json `vfx_anchors`, falling back to the stand-in's heights) for every regular, and request battle VFX to spawn and KO effects there.

## Review log
