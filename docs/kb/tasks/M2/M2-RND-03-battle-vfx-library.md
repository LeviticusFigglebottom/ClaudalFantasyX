---
id: M2-RND-03
title: Battle VFX library, first set for the vertical slice
role: rendering
status: doing
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU, branch gpu/m2-rnd-03-battle-vfx; took over from session_01778wbLbDFnRRLTKjnawv3T)"
depends_on: [M2-CMB-01]
milestone: M2
request-from: "lead"
---
## Goal
SPEC signature R&D: a battle VFX library. The slice needs its effects.

## Acceptance criteria
- [ ] Data-driven VFX definitions (game/data/vfx/battle/*.json) mapped from skill and item ids; a Node-based player kept outside the headless engine (hooked on the engine's action-resolved signal like BattleSwell)
- [ ] First set: a hit per element (none, fire, ice, lightning, water, holy); Lamp Dive (Rhen's Swell); Shallows Verse (Asha's Swell heal); Read; heal and status apply; KO dissolving into released glimmer; the ambush and preemptive flash
- [ ] Reduced-motion and photosensitivity-safe variants (no full-screen flashes above the safe threshold); the effects never hide the timeline (pillar 4)
- [ ] Per-effect GPU cost measured; worst case within budget in a 3v3 battle
- [ ] Screenshots of 3-4 key frames; docs/kb/tech/battle_vfx.md

## Review log
