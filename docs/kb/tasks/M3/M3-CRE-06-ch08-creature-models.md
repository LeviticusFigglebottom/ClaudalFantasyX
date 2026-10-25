---
id: M3-CRE-06
title: "Ch8 creature models: tide crawler, squall wing, the wall-polyp variant, the Undertow's Reach"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M3-CRE-01]
milestone: M3
request-from: lead
---
## Goal
The Ch8 seawall creatures. `model` on m2-slice's rows (M3-C08-02). Waves of 3 / 3 / 4; the Reach with 2.

## Acceptance criteria
- [x] tide_crawler (first pass: 2.7k triangles)
- [x] squall_wing (gull harrier's rig, a spawn body; first pass 5.5k triangles, a steep stoop for the hoist)
- [x] wall_polyp (variant of spawn_polyp, on a Watcher's carved block; first pass 7.8k triangles)
- [x] undertows_reach (first pass: 10.9k triangles, six-fingered grip, the three states as phases `dark` and `breach`; the water look is the PC GPU session's)
- [x] flue_moth (m2-slice act1_ch08 §9: a soot-moth with wings folded like a roof, ember hindwings on the flare; 3.1k triangles)
- [x] stormgull and wallcrab (m2-slice's headland-path variants: imports of the gull harrier and reef crab builds with a palette override; jobs list the base folders)

## Notes
- 2026-10-24 (polish, review notes): squall_wing's tears now read as holes. The wing membranes have ragged lens-shaped rents cut clean through (5 on the camera-side right wing, 3 on the left): grid vertices inside a rent are pushed onto its jagged outline and the triangles inside dropped, the lips lifted apart and left black (no glow), so the ground and sky show through. The body's fbm tears (which had grown into flank-wide openings filled by a big bright core, so they read as cyan patches) are replaced by five explicit rents cut the same way, each with a two-band lip wall (a 3.5 mm lit spawn_wound rim, then dark) dropping into a dark inner hollow (an inward-wound inner wall), with a smaller, mostly dark core with a few hot seams hanging inside. 5,618 triangles (budget 6k). Screenshot creature_squall_wing re-approved after viewing.

## Review log
