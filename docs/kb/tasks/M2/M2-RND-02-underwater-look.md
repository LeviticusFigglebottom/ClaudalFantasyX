---
id: M2-RND-02
title: Underwater rendering (SPEC signature R&D): Rhen the lamp-diver's world
role: rendering
status: doing
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU, branch gpu/m2-rnd-02-underwater; took over from session_01778wbLbDFnRRLTKjnawv3T)"
depends_on: [M1-RND-08]
milestone: M2
request-from: "lead"
---
## Goal
SPEC lists underwater as signature R&D; the vertical slice opens with Rhen in the shallows and the story is about divers. Nothing exists yet.

## Acceptance criteria
- [ ] An underwater post and volume: depth-based absorption and scatter from palette.json water swatches; god rays from the surface; drifting particulate; the surface seen from below (Snell window, total internal reflection)
- [ ] Rhen's lantern as the hero light underwater (warm, falloff matching the lamp-diver fantasy); glimmer motes read correctly underwater
- [ ] A clean transition crossing the surface (no popping; camera half-submerged handled)
- [ ] Tiers in graphics_presets.json, validated; High at or under 3 ms at 1440p on the 9070 XT; Low fallback
- [ ] A test scene plus 2-3 lavapipe screenshots (the Lead approves); docs/kb/tech/underwater.md; Art sign-off requested

## Review log
