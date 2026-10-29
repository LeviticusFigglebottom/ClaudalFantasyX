---
id: M3-CRE-651
title: "Creature spawn/death VFX hooks: CreatureActor.vfx_anchor() with per-creature anchors (wound, core) for the Act I regulars"
role: character
status: review
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

## Done (2026-10-28)
- `CreatureActor.vfx_anchor(name)`, with `ANCHOR_WOUND`/`ANCHOR_CORE`. It reads the named bone's posed world
  position (forcing the skeleton's update first); a missing wound falls back to the core; no anchors gives INF.
- creatures.json `vfx_anchors` for the 20 Act I regulars. The wound is the bone with the most weak-point-masked
  vertices, the core the body bone. flue_moth, raid_hound and vein_sparker get their wound once M3-CRE-650 adds
  their marks.
- validate_creatures.py checks the shape. Tests: tools/tests/test_creatures.py (each bone exists in the GLB; every
  regular has a core) and tests/unit/test_creature_vfx_anchors.gd (on the body; the fallback; follows the clip).
- The request to battle VFX is M3-CRE-653.

## Review log
