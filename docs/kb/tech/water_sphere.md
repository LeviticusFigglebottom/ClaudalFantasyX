# The Reefball water sphere (M3-RND-01)

SPEC §6.10: Reefball is played inside a suspended sphere of water. This is the sphere's look. It's R&D on the PC GPU,
ahead of a Reefball zone.

- **Code:** `game/world/water/sphere/water_sphere_rig.gd` (`WaterSphereRig`); shaders in `game/shaders/water/sphere/`.
- **Data:** `game/data/vfx/water_sphere.json`. The colours are palette swatches, the underwater look's lagoon set
  (M2-RND-09).
- **Test scene:** `game/levels/_tests/reefball/reefball_test.tscn`. A stadium blockout, a 16 m ball 22 m up, and six
  players inside it.
- **Shots:** the Outside, Inside, LookUp and Crossing cameras. They're pending a lavapipe baseline
  (`docs/kb/qa/gpu/2026-10-24-reefball-pending-shots.json`). GPU key frames are in `docs/kb/qa/gpu/reefball/`.

## How it works

One rule covers every camera position: **a view ray's water is the part of it inside the ball, from
max(entry, the lens point) to min(exit, the opaque scene).**

| Part | How |
|---|---|
| **Absorption and in-scatter** | Two full-screen passes drawn after everything else (priorities 126 and 127), as the UnderwaterRig's. The multiply pass applies `exp(-sigma × path)` per channel. The add pass adds the in-scatter: the scatter colour near the ball's top, darkening with depth below it and when looking down, times the scene's light level. From outside, the ball absorbs what's behind and inside it; from inside, the water runs up to the wall. |
| **The wall from outside** | Front faces of the sphere mesh. What's behind is refracted (the screen, offset by the view-space normal, scaled by 1/depth, and faded out toward the silhouette), and the sky reflects through Godot's specular (roughness 0.04): a Fresnel rim and the sun's glint. |
| **The wall from inside** | Back faces. Inside the Snell window (`asin(1/ior)` from the outward normal) the stadium shows through, refracted. Outside it, total internal reflection in `deep_teal_shadow` × `tir_gain`. |
| **Refraction ghosts** | A screen-space offset would drag the pixels of anything in front of the wall (a player) into the water as a ghost copy. Where the offset sample lands on something nearer than the surface, the unrefracted pixel is used instead. |
| **One mesh, both faces** | `cull_disabled` with no depth write: from outside, the far wall's back faces (dark TIR) painted over the near face wherever their triangles came later in the draw (wedges along the rings). So a back face is discarded whenever the camera is outside the ball. The mesh is grown by the swell and the facets' sag, so its silhouette always encloses the exact sphere the full-screen passes use. |
| **The crossing** | A camera at the wall gets the split along its lens line, with a `meniscus_px` dark line, antialiased in screen space (as M2-RND-09's waterline). |
| **The swell** | Three sines on the sphere's direction displace the surface `swell_m` along its normal, on the weather clock. The normal follows their slope. The ball stays a ball. |
| **Caustics on the players** (M3-RND-04) | In the multiply pass (`water_sphere_caustics.gdshaderinc`): the opaque point behind each pixel, from the depth buffer, if it's inside the ball, is scaled by the shared caustic web (`water_caustics.gdshaderinc`, as the ocean's floor) around its mean, so it redistributes light without adding any. The web lies on the plane across the sun's direction (the rig's first visible DirectionalLight3D), so it falls on bodies and floor alike and slides over a moving player. A face turned from the sun (normal from the depth's derivatives) gets none. It fades with the water above the point along the sun (`falloff_m`), with view distance, and over `wall_soft_m` inside the wall, and scales with the light level (a night match's water has almost none). It's on every tier: it costs ≤ 0.013 ms at 1440p. |
| **God rays** | An ellipsoid FogVolume filling the ball with the underwater shafts shader (constant along the sun). Only on tiers with `god_rays`, under volumetric fog the rig authors (as UnderwaterRig does). |

Tiers come from the data's `quality`. Low has no refraction (a tinted Fresnel shell) and no god rays. Medium
refracts. High and Ultra add the god rays. Every tier has the caustics.

## Cost (RX 9070 XT, GPU median; the frame against the same view with the ball hidden)

| Camera | Low 1080p | Medium 1080p | High 1080p | Ultra 1080p | Low 1440p | High 1440p | Ultra 1440p |
|---|---:|---:|---:|---:|---:|---:|---:|
| Outside | +0.08 | +0.11 | +0.09 | +0.11 | +0.14 | +0.19 | +0.24 |
| Inside | +0.13 | +0.19 | +0.18 | +0.36 | +0.23 | +0.32 | +0.48 |
| LookUp (inside, toward the sun) | +0.17 | +0.20 | +0.19 | +0.39 | +0.20 | +0.33 | +0.50 |

The whole test frame is at most 1.3 ms at 1440p Ultra. The ball is cheap: two full-screen passes, a sphere mesh
and a small FogVolume.

## Open
- **Caustics in shadow.** The multiply pass can't tell sun from shadow, so a player in another's shadow still gets
  the web (faint, since it scales what's lit there). A shadow-aware version would sample the sun's shadow map in
  the body's own shader; it doesn't read at this size.
- The underwater look (tech/underwater.md) can reuse `water_sphere_caustics.gdshaderinc`'s approach for SPEC §8.2
  item 2.
- **Reflections of the absorbing water.** The front face's sky reflection is absorbed by the multiply pass along
  with what's behind it, which is slightly too dark at the rim. A per-pixel "reflection before water" split would
  fix it; it doesn't read at this size.
- **Snow, the lantern and a night match:** UnderwaterRig's particulate and Rhen's lantern halo aren't wired to the
  sphere yet.
- Art's review of the look (character), against the colour script's Act I festival match.

## Caustics cost (M3-RND-04; RX 9070 XT, GPU median, on against off)

| Camera | Low 1080p | Medium 1440p | High 1440p |
|---|---:|---:|---:|
| Inside | 0.417 / 0.417 | 0.826 / 0.815 | 1.027 / 1.014 |
| Outside | | 0.683 / 0.678 | 0.867 / 0.863 |
| LookUp | | 0.763 / 0.754 | 0.966 / 0.958 |

Key frames: `docs/kb/qa/gpu/reefball/caustics_inside_high.png` and `caustics_inside_low.png`.
