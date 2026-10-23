---
id: M1-RND-09
title: Undertow placement and character-shader contract fixes
role: rendering
status: doing
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-09-undertow-shading)
depends_on: [M1-RND-03, M1-RND-04]
milestone: M1
request-from: "environment"
---
## Goal
Review-sweep-C should-fix items on RND-03/RND-04 that are M1-sized.

## Acceptance criteria
- [ ] Undertow: explicit sea_level property decoupled from the node's Y; doc example fixed
- [ ] UndertowStorm is @tool (visible in editor)
- [ ] undertow_eye baseline: no visible test-set edge
- [ ] A daytime storm shot that reads as the bible's 'wall of dark water and cloud' (Ch1/Ch8), not a khaki cumulonimbus or sandstorm
- [ ] Cloth band-id texture uses nearest filtering and no mip-bleed; the contract states the exception
- [ ] Contract: wind weights as float colour attributes (no sRGB byte quantisation); uniform head texel density plus a pore tiling formula

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

## Review log
