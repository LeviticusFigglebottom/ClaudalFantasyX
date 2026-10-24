---
id: M3-RND-05
title: "Reefball: the night match (the ball's sea-glow, lamp-keyed players, rule 3)"
role: rendering
status: review
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: art
depends_on: [M3-RND-04]
milestone: M3
request-from: "lead"
---
## Goal
A night Reefball match that reads: the ball dark but teal (colour script rule 3), players readable under the arena's
lamps, no daytime look leaking in.

## Acceptance criteria
- [x] The water column carries the night sea-glow (the shared `glimmer.gdshaderinc` term, at the zone's energy or the
      rig's `sea_glow_energy`), independent of the light level.
- [x] Rule 3, measured: glow on/off ≥ 1.5× inside and outside the ball; moonlit stone ≤ 2.5× the glowing sea.
- [x] A night test scene and two pending shots; the arena-lamp fog rule is documented and tested.
- [x] Cost measured.

## Notes (PC GPU, 2026-10-24)
- `water_sphere_post_add.gdshader`: `hymn_sea_glow(mid, hymn_wind_time, energy × sea_glow_strength, path_m)` ×
  (1 − transmittance). The column build-up (`path_m`) took the outside view from 1.27–1.42× to 1.56–1.87×.
- `WaterSphereRig.sea_glow_energy` is exported (0 = the zone's) and pushed to the material when set.
- **The finding:** the arena's lamps lit the god-ray FogVolume into bright green bands, which read as daytime. Arena
  lamps need `light_volumetric_fog_energy = 0`, as Rhen's lantern does. The test checks the night scene's lamps;
  a real arena (Environment) must do the same.
- Numbers, cost and key frames: docs/kb/tech/water_sphere.md, "The night match".
- Not in scope: snow and Rhen's lantern inside the ball (still open in the tech doc).

## Review log
