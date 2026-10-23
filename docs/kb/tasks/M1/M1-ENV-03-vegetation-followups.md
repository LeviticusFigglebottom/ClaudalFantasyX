---
id: M1-ENV-03
title: Vegetation follow-ups (review-sweep-B)
role: environment
status: doing
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/env-03-vegetation; routed by the Lead)"
depends_on: [M1-ENV-02, M1-ENV-01]
milestone: M1
request-from: "rendering"
---
## Goal
Rendering-side findings on vegetation, scheduled after the mood test (which uses the vegetation) merges.

## Acceptance criteria
- [ ] translucency_shadow_floor no longer lets plants under eaves glow
- [ ] Capture under FXAA (as water does) and restore threshold 0.008
- [ ] LOD fade (no palm pop against sky)
- [ ] Overdraw measured (debug_draw OVERDRAW capture) with a budget
- [ ] Assets tagged PLACEHOLDER until Art Director sign-off
- [ ] Wind flutter cap noted for GPU TAA motion test

## Notes
-

## Review log
