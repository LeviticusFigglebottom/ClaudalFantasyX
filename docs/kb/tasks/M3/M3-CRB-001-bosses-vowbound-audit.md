---
id: M3-CRB-001
title: "Audit the Act I bosses and Vowbound against ADR 0041 (mesh, clips, weak point, VFX hooks)"
role: character
status: review
owner_session: "creatures-b"
reviewer: art
depends_on: []
milestone: M3
request-from: lead
---
## Goal
ADR 0041 (Act I at final quality first). Final means: a real mesh that does not read as primitives up close or at battle distance (no plain tubes, lathes or spheres left bare: surface relief, broken edges, wear, the sheet's details), the full clip set (idle, ready, intro, attack, cast, hit, hit_b, idle_b, every phase clip, ko), one readable weak point in `spawn_wound` (ADR 0151: open wound seams on Undertow-spawn, one small closed mark on a beast or construct), and unweighted VFX anchor bones `vfx_wound` (the weak point), `vfx_core` (the body's centre of mass) and `vfx_phase` (where the phase change bursts from) for battle-presentation's intro and phase effects. Bone, node and clip names the data uses stay. Self-rendered and viewed at battle distance (creature_<id> and the boss intro shot). Audit of hullgnaw, drownbell, bottle_hermit, spar_wraith, cinder_matron, undertows_reach, ilun, kahre, virel; the findings become M3-CRB-002..008.

## Audit (2026-10-28, creatures-b; creature_<id> review shots self-rendered at 4c tree 339557e6+, viewed)
| id | tris | clips missing (vs final set) | weak point | verdict |
|---|---|---|---|---|
| hullgnaw | 5.4k | ready, intro | wound bands between ribs (ok) | **primitive**: a smooth tube with torus rings; round ribs, not squared frames; bare head |
| drownbell | 19.4k | ready, intro | crack seams (ok) | light pass: cone legs, rope |
| bottle_hermit | 3.4k | ready, intro | none visible | **primitive**: toy crab of tubes and spheres, clean glass |
| spar_wraith | 7.1k | ready, intro | knots (ok) | medium: plain cylinder spars, lumpy shroud, bare lines |
| cinder_matron | 23.9k | ready, intro | heart port (glimmer_bound; no spawn_wound mark) | light pass: even hex crust, smooth limbs; needs one small closed spawn_wound mark (ADR 0151) |
| undertows_reach | 10.9k | ready, intro | door wounds (ok) | **primitive**: smooth tube forearm, cylinder spars, sphere shells |
| ilun | 13.7k | intro (rise exists) | n/a (ally) | **primitive**: a flat sheet with a tick-mark grid, not a vast spectral manta |
| kahre | 14.1k | intro (rise exists) | n/a (ally) | **primitive**: cylinder limbs, a box anvil, comb mane |
| virel | 12.2k | intro (rise exists) | n/a (ally) | **primitive**: a closed ring of panels (reads as a tyre) |
No model has `vfx_*` anchor bones yet. Moll is the characters track's (M3-CHR-507).

## Review log
