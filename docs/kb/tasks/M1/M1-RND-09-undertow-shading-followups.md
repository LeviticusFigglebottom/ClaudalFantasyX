---
id: M1-RND-09
title: Undertow placement and character-shader contract fixes
role: rendering
status: review
reviewer: environment
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-09-undertow-shading)
depends_on: [M1-RND-03, M1-RND-04]
milestone: M1
request-from: "environment"
---
## Goal
Review-sweep-C should-fix items on RND-03/RND-04 that are M1-sized.

## Acceptance criteria
- [x] Undertow: explicit sea_level property decoupled from the node's Y; doc example fixed
- [x] UndertowStorm is @tool (visible in editor)
- [x] undertow_eye baseline: no visible test-set edge
- [x] A daytime storm shot that reads as the bible's 'wall of dark water and cloud' (Ch1/Ch8), not a khaki cumulonimbus or sandstorm
- [x] Cloth band-id texture uses nearest filtering and no mip-bleed; the contract states the exception
- [x] Contract: wind weights as float colour attributes (no sRGB byte quantisation); uniform head texel density plus a pore tiling formula

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

## Notes (author, PC GPU session, 2026-10-23)
All six criteria done; report with GPU before/after, look metrics and the lavapipe drift list: docs/kb/qa/gpu/2026-10-23-rnd-09.md. New shot undertow_day_ch08 waits in docs/kb/qa/gpu/2026-10-23-rnd-09-pending-shots.json for a lavapipe baseline (Lead). Band-id import mips: request M1-CHR-03 (Character owns the asset). Reviewer (Environment raised these in review-sweep-C): judge the day shot against bible §9 and the Eye framing.

## Review log
