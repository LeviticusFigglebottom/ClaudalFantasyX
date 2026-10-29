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
| **Night sea-glow** (M3-RND-05) | Colour script rule 3: the add pass carries the shared sea-glow (`glimmer.gdshaderinc`: `sea_glow` with its slow ±25% noise, building up along the ray's water) at the zone's `hymn_zone_sea_glow`, or the rig's own `sea_glow_energy`, × `sea_glow_strength` 1.8 (as the underwater look's), times (1 − transmittance), independent of the light level. A night ball is dark teal, not black. |
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
- **Snow and the lantern:** UnderwaterRig's particulate and Rhen's lantern halo aren't wired to the sphere. The night
  match (M3-RND-05) is lamp-keyed from outside the ball; the arena's lamps don't scatter in its water.
- Art's review of the look (character), against the colour script's Act I festival match.

## Caustics cost (M3-RND-04; RX 9070 XT, GPU median, on against off)

| Camera | Low 1080p | Medium 1440p | High 1440p |
|---|---:|---:|---:|
| Inside | 0.417 / 0.417 | 0.826 / 0.815 | 1.027 / 1.014 |
| Outside | | 0.683 / 0.678 | 0.867 / 0.863 |
| LookUp | | 0.763 / 0.754 | 0.966 / 0.958 |

Key frames: `docs/kb/qa/gpu/reefball/caustics_inside_high.png` and `caustics_inside_low.png`.

## The night match (M3-RND-05)
Test scene: `game/levels/_tests/reefball/reefball_night_test.tscn`, the day scene with a moon (`moon_blue`, 0.25),
the water test's night sky and exposure 1.1, four oil-lamp spots on the pillars aimed at the ball (energy 20), and
the ball's sea-glow at 0.12. Key frames: `docs/kb/qa/gpu/reefball/night_inside_high.png` and
`night_outside_high.png`. Shots `reefball_night_inside` and `reefball_night_outside` are pending a lavapipe baseline.

**Rule for arena lamps: `light_volumetric_fog_energy = 0`.** The ball's god rays are a dense FogVolume (0.3), and a
lamp lights it as fog: four lamps turned the whole inside view a bright green, in bands along their cones. It's the
same trap as Rhen's lantern (tech/underwater.md), and the night test checks it.

Colour script rule 3, measured in linear luminance (High, 960×540):

| | Glow on / off | Rule |
|---|---|---|
| Inside, open water | 0.0333 / 0.0066 (5.0×) and 0.0397 / 0.0132 (3.0×) | ≥ 1.5× |
| Outside, the ball | 0.0205 / 0.0131 (1.56×) and 0.0404 / 0.0215 (1.87×) | ≥ 1.5× |
| Moonlit stone against the glowing sea (outside) | ground 2.36× / 1.53×, pillar 2.10× | ≤ 2.5× |

Before the column build-up (the glow at its surface value), the outside view was 1.27–1.42×: under the rule.

Glow cost (GPU median, on against off): Inside High 1440p 1.423 / 1.341 ms (+0.08); Outside High 1440p
1.129 / 1.119 (+0.01); Inside Low 1080p 0.595 / 0.564 (+0.03). Rule 3 never cuts it for performance.


## The Tamsule Bell's held drop (M3-RND-26, env-art-b for Rendering, 2026-10-28)

The same rig holds the Ch7 drop through a **profile**: `WaterSphereRig.profile = "tamsule_drop"` lays the data's
`profiles.tamsule_drop` row over the sections above, key by key (`WaterSphereRig.profile_data`). The empty profile is
the Reefball arena's ball, unchanged: at `sphere_flatten` 1 and `under.strength` 0 every pass computes what it did.

| Part | How |
|---|---|
| **The contract's shape** | `sphere.semi_axis_y_m` (11.5) under `radius_m` (14.0): the passes take `sphere_flatten` = 0.82 and solve the ray in the space where the drop is a unit ball (`sphere_hit`, so the distances stay metres); the wall's normal is `(p − c) / axes²`; the inside distance (`sphere_inside_m`) is exact for a ball and scaled by the short axis for the drop. The mesh is a SphereMesh of the same proportions, grown by the facets' sag; the shafts' FogVolume is 28 × 23 × 28 m. |
| **Still** (N-12) | `swell_m` 0 and `caustics.speed` 0: the bound drop has no swell, and its web holds. |
| **Pushed cyan** (colour script ch07) | Transmit and scatter `turquoise_shallow`, deep `lagoon_teal`, over 18 m (the drop reads as a body of water from every side, not clear glass), in-scatter 0.9. |
| **Its bound light** | The add pass's `bound_glow_*`: `glimmer_bound` × 0.25 × (1 − transmittance), steady (colour rule 2: no sea-glow noise; `sea_glow_strength` 0). |
| **Light under it** (the shade disc, tamsule_bell.md §0) | `sphere_under_light` in the add pass: an opaque point outside the drop whose ray to the sun crosses it gets the web, in `glimmer_lift_hi` × `under.strength` 2.4, strongest where the ray crossed `lens_m` or more of water, fading over `reach_m` below it; vertical faces (the posts, the pool's coping) take half, faces turned from the sun none. Faces turned down within `reflect_radius_m` of the axis between `floor_m` and `top_m` (the bell's inside, under the gantry head) take the pool's reflected web × `reflect`. It may clip to white (ch07). It's added after the multiply, times the drop's transmittance in front of it. |
| **God rays** | As the ball's (High and Ultra). |

The weep column is env-art-b's kit piece (`b_column.py`, M3-ENV-1321): the contract's 0.8 → 0.6 m fall from the pool's
surface 0.3 m up into the drop, in the zones' turquoise `weep_column_water_material`. Placements: the preview
(`SphereAnchor/Drop`, `SphereAnchor/WeepColumn`), and both Ch7 zones through ZoneKitDressing's `drops` rows.

**Open:** the cost on the PC presets (it adds one web evaluation per pixel in the add pass where `under.strength` > 0;
the ball's own cost is above). A weep cusp at the drop's foot (the contract allows one) isn't modelled: the column
enters the drop's lowest point.
