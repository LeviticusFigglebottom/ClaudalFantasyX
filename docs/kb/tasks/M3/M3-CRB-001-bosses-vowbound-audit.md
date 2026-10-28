---
id: M3-CRB-001
title: "Audit the Act I bosses and Vowbound against ADR 0041 (mesh, clips, weak point, VFX hooks)"
role: character
status: doing
owner_session: "creatures-b"
reviewer: art
depends_on: []
milestone: M3
request-from: lead
---
## Goal
ADR 0041 (Act I at final quality first). Final means: a real mesh that does not read as primitives up close or at battle distance (no plain tubes, lathes or spheres left bare: surface relief, broken edges, wear, the sheet's details), the full clip set (idle, ready, intro, attack, cast, hit, hit_b, idle_b, every phase clip, ko), one readable weak point in `spawn_wound` (ADR 0151: open wound seams on Undertow-spawn, one small closed mark on a beast or construct), and unweighted VFX anchor bones `vfx_wound` (the weak point), `vfx_core` (the body's centre of mass) and `vfx_phase` (where the phase change bursts from) for battle-presentation's intro and phase effects. Bone, node and clip names the data uses stay. Self-rendered and viewed at battle distance (creature_<id> and the boss intro shot). Audit of hullgnaw, drownbell, bottle_hermit, spar_wraith, cinder_matron, undertows_reach, ilun, kahre, virel; the findings become M3-CRB-002..008.

## Review log
