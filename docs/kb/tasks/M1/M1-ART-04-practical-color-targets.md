---
id: M1-ART-04
title: Make the art numbers renderable: on-screen targets, absorption, exposure units
role: character
status: doing
owner_session: art-stream-3
depends_on: [M1-RND-01, M1-ART-03]
milestone: M1
request-from: "rendering"
---
## Goal
Rendering's reviews found four art-direction numbers that fail in practice.

## Acceptance criteria
- [ ] Hexes split into input albedo/emission values vs. on-screen (post-tonemap) targets
- [ ] Water absorption numbers replaced with values validated in the water test scene
- [ ] Exposure: an ADR on physical light units vs. Godot's default exposure, with the color script converted accordingly
- [ ] Sea-glow brightness rule made reachable against moonlit stone values
- [ ] Define the ch03_steps grade (needed by ch03_the_first_verse.dlg node `steps`)

## Notes
Sources: M1-ART-01 review log (rendering-stream-2), docs/kb/tech/water.md, the M1-NAR-04 report (ch03_steps grade).

## Review log
