---
id: M2-RND-02
title: Underwater rendering (SPEC signature R&D): Rhen the lamp-diver's world
role: rendering
status: review
reviewer: environment
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU, branch gpu/m2-rnd-02-underwater; took over from session_01778wbLbDFnRRLTKjnawv3T)"
depends_on: [M1-RND-08]
milestone: M2
request-from: "lead"
---
## Goal
SPEC lists underwater as signature R&D; the vertical slice opens with Rhen in the shallows and the story is about divers. Nothing exists yet.

## Acceptance criteria
- [x] An underwater post and volume: depth-based absorption and scatter from palette.json water swatches; god rays from the surface; drifting particulate; the surface seen from below (Snell window, total internal reflection)
- [~] Rhen's lantern as the hero light underwater (warm, falloff matching the lamp-diver fantasy); glimmer motes read correctly underwater
- [x] A clean transition crossing the surface (no popping; camera half-submerged handled)
- [x] Tiers in graphics_presets.json, validated; High at or under 3 ms at 1440p on the 9070 XT; Low fallback
- [x] A test scene plus 2-3 lavapipe screenshots (the Lead approves); docs/kb/tech/underwater.md; Art sign-off requested

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Design, tiers, cost and gotchas: `docs/kb/tech/underwater.md`. Key frames: `docs/kb/qa/gpu/rnd02/`.
- **Done:**
  - A per-pixel post (absorption and scatter, with a lens-point waterline that follows the waves). The
    half-submerged camera gets a split with a meniscus, and crossing doesn't pop.
  - The underside: the Snell window with the refracted sun, and TIR.
  - Volumetric god rays (High and Ultra), and marine snow.
  - Rhen's oil-lamp lantern with a fog halo.
  - The light level follows the scene's sun, so a night dive is dark.
  - Tiers in graphics_presets.json (`tiers.underwater`), tested.
  - **High 1440p: the rig costs +0.32 ms; the whole frame is 1.1–1.5 ms.** Low fallback: a flat-surface post
    only, +0.14 ms.
- **Partial (criterion 2):** the glimmer motes are absorbed physically, but at noon they're faint by design and
  hidden beyond a few metres. A submerged boost is Art's call: **M2-ART-02** (sign-off requested).
- **Screenshots for lavapipe:** three pending shots in `docs/kb/qa/gpu/2026-10-24-rnd-02-pending-shots.json`
  (underwater_below, underwater_window, underwater_waterline). The Lead approves them on lavapipe.
- **Tools:** gpu_bench and capture_preset now apply every system tier (`GraphicsRuntime.apply_system_tiers`), and
  gpu_bench gained `--node-set`.
- **Not done:** caustics on characters; a splash at the crossing.

## Review log
