---
id: M2-RND-03
title: Battle VFX library, first set for the vertical slice
role: rendering
status: review
reviewer: environment
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU, branch gpu/m2-rnd-03-battle-vfx; took over from session_01778wbLbDFnRRLTKjnawv3T)"
depends_on: [M2-CMB-01]
milestone: M2
request-from: "lead"
---
## Goal
SPEC signature R&D: a battle VFX library. The slice needs its effects.

## Acceptance criteria
- [x] Data-driven VFX definitions (game/data/vfx/battle/*.json) mapped from skill and item ids; a Node-based player kept outside the headless engine (hooked on the engine's action-resolved signal like BattleSwell)
- [x] First set: a hit per element (none, fire, ice, lightning, water, holy); Lamp Dive (Rhen's Swell); Shallows Verse (Asha's Swell heal); Read; heal and status apply; KO dissolving into released glimmer; the ambush and preemptive flash
- [x] Reduced-motion and photosensitivity-safe variants (no full-screen flashes above the safe threshold); the effects never hide the timeline (pillar 4)
- [x] Per-effect GPU cost measured; worst case within budget in a 3v3 battle
- [x] Screenshots of 3-4 key frames; docs/kb/tech/battle_vfx.md

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Design, data, safety and cost: `docs/kb/tech/battle_vfx.md`. Key frames: `docs/kb/qa/gpu/rnd03/`.
- **Player.** `BattleVfx` is listen-only (one line in `BattleController._build_engine`).
- **Data.** `game/data/vfx/battle/effects.json`: 14 effects, palette swatches, a map from skills, items, elements
  and events.
- **Rendering.** Built-in GPUParticles3D with one shared billboard material (registered for prewarm on the battle
  scenes).
- **Safety.** Flashes are capped at alpha 0.3, at least 0.5 s apart, and below the HUD. Reduced motion follows
  UiSettings.
- **Cost, High 1440p:** the worst 3v3 burst is +0.04 ms; each effect on 3 foes is +0.03-0.04 ms.
- **Tests.** `tests/unit/test_battle_vfx.gd` (7). The battle suite (362) passes with the view attached.
- **Not done here:**
  - holy has no skill in data yet (the effect is mapped and ready);
  - effects play on resolve, not on an animation contact frame (no body clips yet);
  - an art pass for the pale effects on bright scenes.

## Review log
