---
id: M2-RND-01
title: Undertow storm to production cost and quality
role: rendering
status: doing
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/m2-rnd-01-undertow; start: sweep-G ch08 findings)"
depends_on: [M1-RND-03]
milestone: M2
request-from: ""
---
## Goal
The M1 prototype reads (horizon and eye shots) but its raymarched tiers are an estimated 5-15× over a storm shot's 2-3 ms GPU budget, and the agent self-assesses it at about a third of the bar for "the most important visual" (SPEC §8.2.9). See docs/kb/tech/undertow.md.

## Acceptance criteria
- [ ] Body at half/quarter resolution with temporal reprojection; baked 3D noise textures instead of hash noise; <= 2-3 ms estimated on the recommended tier
- [ ] Billow surface detail and multiple scattering (no uniform khaki lit tone, less regular striations)
- [ ] Wounds as real torn rents; storm-scale mote streamers
- [ ] Storm in sky and reflections, shadowing the zone, rain
- [ ] Lightning bolts plus exposure flash
- [ ] Per-chapter presets, including the Ch21 turn to rising gold
- [ ] Art confirms spawn_wound usage for storm rents (palette.json currently limits it to creature weak points)

## Notes
Needs a real GPU for final cost; the CPU-render ratios are the guide until then.

## Review log
