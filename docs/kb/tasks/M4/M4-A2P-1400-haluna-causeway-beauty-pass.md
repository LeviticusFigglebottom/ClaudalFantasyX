---
id: M4-A2P-1400
title: "Ch2 Haluna and Ch3 causeway beauty pass at eye height along the slice path (the Lead, 10-30)"
role: environment
status: review
owner_session: "claude/env-art"
depends_on: []
reviewer: art
milestone: M4
request-from: lead
---
## Goal
Haluna is the third thing the player sees, after the Prologue and the Ch1 Underway, so it should read
beautiful-and-doomed (pillar 2): a living town, sea light, and the Shell Shrine's approach. The Lead's 10-30 order.

## Acceptance criteria
- [x] Eye-height stills along tools/act1/walkthrough.py's legs are viewed: ch02_haluna (22), ch03_causeway (12) and
      ch03_shell_shrine (8).
- [x] Every defect found is fixed or noted below.
- [x] Haluna kit tests and the Godot vegetation and haluna filters pass.

## Notes
- **Found and fixed:** Haluna's 49 windbreak trees rendered as black blots from every side. Their sprays use the leaf
  atlas's darkest blue-green cluster, and the crown's baked occlusion plus a dim tint left no green. `materials.py`
  now gives `kit_windbreak_leaf` a tint over 1, half the baked darkening, more transmission and a softer wrap.
- **Viewed and left as is:**
  - The beach, the lanes and the stilt pier at Haluna; the sea light is strong.
  - The causeway's stepping stones, guide posts and tide pools.
  - The Shell Shrine's sunlit approach and cool interior.

## Review log
