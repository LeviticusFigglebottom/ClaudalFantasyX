---
id: M3-CRE-650
title: "Act I regulars: audit to final quality; weak-point marks for flue_moth, raid_hound and vein_sparker"
role: character
status: doing
owner_session: "creatures (worktree agent)"
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

**Audit (2026-10-28, creatures):** all 20 have a real mesh and rig and the full set (idle, ready, attack, cast, hit, hit_b, ko). 17 carry a spawn_wound weak point. **flue_moth** (ember glow only), **raid_hound** (no emissive) and **vein_sparker** (starlight glow, a palette point-source swatch at 2.5–4.0 over its scales) have none: each needs one small closed spawn_wound mark (ADR 0151), and vein_sparker's starlight is to be checked against palette.json's ≤0.5% usage limit.

## Review log
