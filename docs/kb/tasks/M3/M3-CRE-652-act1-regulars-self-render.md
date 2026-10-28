---
id: M3-CRE-652
title: "Self-render the 20 Act I regulars at battle distance and as bestiary portraits; view each; fix what reads unfinished"
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

**Method (TRACK-RULES, while the PC is paused):** `HYMN_SHOTS=<≤15 ids> HYMN_SKIP_BLENDER=1 tools/ci_local.sh` (one capture at a time), plus `tools/portraits/render.sh --only <ids>`; view every out, diff and portrait; never write baselines; log `SELF-RENDERED @ <sha>: …`.

## Review log
