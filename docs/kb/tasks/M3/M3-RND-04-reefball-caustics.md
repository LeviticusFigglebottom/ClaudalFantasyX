---
id: M3-RND-04
title: "Reefball: caustic light on the players inside the water sphere"
role: rendering
status: review
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: character
depends_on: [M3-RND-01]
milestone: M3
request-from: "lead"
---
## Goal
SPEC §8.2 item 2, for the Reefball: caustic light on the players inside the suspended ball (M3-RND-01's open item).

## Acceptance criteria
- [x] The players inside the ball show a moving caustic web on the faces turned to the sun, and none on faces
      turned away.
- [x] The web redistributes light (around its mean), fades with depth along the sun and toward the wall, and
      follows the scene's light level.
- [x] It's data-driven (`water_sphere.json` "caustics", one switch per tier) and tested (shader uniforms, rig wiring,
      tiers).
- [x] Cost measured on every view.

## Notes (PC GPU, 2026-10-24)
- `game/shaders/water/sphere/water_sphere_caustics.gdshaderinc`, in the multiply pass. It reuses the ocean's caustic
  web (`water_caustics.gdshaderinc`, two layers) rather than a new pattern, projected on the plane across the sun.
  The sun direction comes from `WaterSphereRig` every frame.
- Tuned for the ball's depth: the players hang about 15 m under its top, so blur is 0.004/m, falloff 30 m, strength 2.2
  and scale 1.3/m. At the ocean's settings (blur 0.01, falloff 12 m) the web was a faint smear.
- Cost: ≤ 0.013 ms at 1440p (Medium and High, all three views), unmeasurable on Low at 1080p. So it's on every tier.
- Known limit: no shadow test. A shadowed point still gets the (proportionally faint) web. See
  docs/kb/tech/water_sphere.md.
- Key frames: `docs/kb/qa/gpu/reefball/caustics_inside_high.png` and `caustics_inside_low.png`. The four reefball
  shots in `2026-10-24-reefball-pending-shots.json` change (Inside and LookUp most), so they need re-approving on
  lavapipe with M3-RND-01's.

## Review log
