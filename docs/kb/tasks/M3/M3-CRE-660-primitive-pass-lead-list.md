---
id: M3-CRE-660
title: "Primitive pass on the Lead's list (2026-10-28 03:41): raid hound, slag tortoise, 'pumice crawler', avalanche ram"
role: character
status: review
owner_session: "creatures (session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-659]
milestone: M3
request-from: lead
---
## Goal
Read at close range, the Lead's list of creatures still primitive: raid_hound (blocky segmented legs, a box muzzle),
slag_tortoise and "pumice_crawler" (lumpy shells, stub legs), and avalanche_ram (its fleece reads as plates). Give them
real silhouettes, joint transitions and surface detail. Self-render, and view at battle distance.

## State when filed (creatures)
- **raid_hound:** re-modelled in M3-CRE-655 (merged 2026-10-28): greyhound legs with real joints and paws, a wedge
  head with a moving jaw, the harness and cage. The Lead's note predates it. Re-check at battle distance after the
  Lead's re-render; nothing more is planned unless the render says so.
- **slag_tortoise:** re-modelled in M3-CRE-654 (merged): scaled, clawed legs, a beaked head, a dripping crust.
  Same: re-check at battle distance.
- **"pumice_crawler":** there's no such creature in the repo. The likely one is **scree_crawler** (Act II, the slag
  tortoise's variant, rebuilt with it in M3-CRE-654), which is paused by ADR 0041. Lead: confirm the id.
- **avalanche_ram:** Act II (Ch12 boss), paused by ADR 0041. Lead: say if it comes back into scope.

## Lead's answer (2026-10-28 ~10:34)
pumice_crawler and avalanche_ram are in no Act I encounter: Act II, out of scope under ADR 0041, skipped. Do the pass
on raid_hound and slag_tortoise.

## Done (self-rendered creature_raid_hound and creature_slag_tortoise, and the three portraits; viewed)
- **slag_tortoise:**
  - The crust is a 44×112 lathe, up from 24×64.
  - Each plate is a slab tilted its own way (PLATE_TILT), so neighbouring plates step at narrow seams (SEAM_W, SEAM_DEPTH) instead of melting into one blob. The seams are dark cracks with a thin copper lip.
  - The glass gloss is halved and varied (no single sky hotspot). There are 12 clinker lumps, up from 7, and larger, to break the dome's silhouette.
  - The leg scales are overlapping, domed, smooth-shaded scutes (5×4 on the fore legs, 3×3 on the hind), not flat triangles.
  - The scree crawler (Act II, the same build) is rebuilt with it.
- **raid_hound:**
  - The foreleg's top sections sit back and in, inside the chest wall, and every leg has 14 segments (was 10).
  - Each leg's top blends its normals and colour into the body's nearest point (blend_into_body), so the shoulder rises out of the chest as an upper arm and elbow instead of a flat plate with a seam round it.
  - The rose ears are fuller and folded (9 stations, 12 segments).
- **Checks:**
  - Blender verify: identical for the three jobs natively, under `"X86_V4"` and under `"X86_V3 X86_V4"`.
  - Godot creature 84/0; tools test_creatures OK.

## Review log
