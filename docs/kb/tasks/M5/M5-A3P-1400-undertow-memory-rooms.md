---
id: M5-A3P-1400
title: "Ch20 Undertow: the three missing memory rooms (a Pemakar terrace on lantern-night, a drowned gallery, a still gold square)"
role: environment
status: review
owner_session: "claude/env-art"
depends_on: []
reviewer: art
milestone: M5
request-from: lead
---
## Goal
ADR 0207 opens Act III per track. act3_ch20.md's six layers each stand on a remembered place. The Undertow kit
(`assets_src/environments/kits/haluna/undertow_layers.py`, M3-ENV-727) has the island, the Corrow kitchen (U03), the
Oruvel market (U01), the Reefball stands (U04) and the held pillar. Three rooms are missing:
- **U02, `memory_terrace`:** a Pemakar terrace on lantern-night (Ch5's Lanternfall). A terrace step and channel
  with small boats in it, each holding held light, cold cyan (never warm: the warm light is the Letting's, in Ch21).
- **U05, `memory_gallery`:** a Lit Age gallery like the Vey's. Lamps steady, silt-light falling, no ice (ADR 0015).
- **U06, `memory_square`:** a square of Ansedra under the Level: still water that has never moved, a Tender's broom
  on a step.

## Acceptance criteria
- [x] The three pieces built procedurally in undertow_layers.py, at r 5 to 6 and within 7k / 500 triangles each, as
      their siblings. Each stands on `memory_island`'s flat top.
- [x] glbs, imports, PROVENANCE rows and the kit manifest; the docs' piece table updated.
- [x] The Undertow kit preview shows them, viewed and approved; test_undertow (or its kit tests) extended.
- [x] No Final Fantasy terms; nothing frozen (ADR 0015); held light only (no warm practicals).

## Notes
The zone split with env-art-b is proposed in env-art.md (21:56 + ADR 0207). The ch20 zone's greybox and staging stay
the Act III chapters' track's.

**Done (env-art, 2026-10-30):**
- Built: memory_terrace 2284/364 tris, memory_gallery 3060/316, memory_square 2434/304.
- The rooms have no kit preview of their own, so they hang in the `undertow_cage` arena with the others, and that is
  where they were viewed. The gallery replaces the arena's second kitchen, a stand-in; the terrace and the square
  hang at new heights and bearings.
- test_undertow_layers gains two checks: every layer (U01..U06) has its room in the kit and in the arena, and the new
  rooms hold only held light.
- Viewed: the square's pool and flags first sat under the island's top, so they were raised. The terrace's boats
  were flat slabs, so they became pointed hulls. Under the arena's top-down key the gallery's columns read dark
  against the dark wall; Ch20's staging sets its light.

## Review log
