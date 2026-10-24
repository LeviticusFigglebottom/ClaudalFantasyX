# Underwater look (M2-RND-02)

SPEC signature R&D: Rhen the lamp-diver's world. An `UnderwaterRig` beside a zone's `WaterSurface` gives every
camera below the surface the underwater look, and a half-submerged one a clean waterline.

- **Code:** `game/world/water/underwater/underwater_rig.gd`.
- **Data:** `game/data/vfx/underwater.json` (palette swatches, optics, god rays, particulate, the lantern,
  tiers).
- **Shaders:** `game/shaders/water/underwater_post*.gdshader*`, `water_underside.gdshader` and
  `underwater_shafts.gdshader`.
- **Test scene:** `game/levels/_tests/underwater/underwater_test.tscn`. It instances the water test lagoon, plus
  Rhen with his lamp, a held glimmer field, and four cameras: Below, Deep, Waterline and UpWindow.

## The parts

| Part | How |
|---|---|
| **Absorption and scatter** | Two full-screen passes drawn after everything (render priorities 126 and 127). The *multiply* pass multiplies the frame by the per-channel transmittance `exp(-sigma x path)`, where `sigma = -ln(transmit) / transmit_distance_m`: red goes first. The *add* pass adds the in-scattered light: the scatter colour, darkening toward the deep colour with depth and when looking down, times (1 - transmittance) and the scene's light level. Neither reads the screen texture, so everything drawn before them (the underside, motes, glass) is absorbed like the rest. |
| **Where the water is** | Per pixel. A ray starts underwater when its *lens point* (`lens_m` 0.25 along it, not the near plane, which is only a few cm tall) is below the surface. The surface is the water's own Gerstner sum (`water_waves.gdshaderinc`, the same time base), so the waterline moves with the waves. A rising ray stops at the surface; a ray starting above water is left to the water shader. |
| **The surface from below** | `water_underside.gdshader` on a copy of the water's surface mesh (a child of it, so it follows), back faces only, with the water's exact vertex stage. Inside the Snell window (`asin(1/ior)`, 48.6°) it's mostly clear, with a sky tint and the refracted sun (a disc and a halo); outside it, total internal reflection in `sea_glow`. |
| **God rays** | A FogVolume under the surface with a fog shader whose density is a noise on the plane perpendicular to the sun: constant along the light, so the volumetric fog draws shafts. They fade with depth and drift on `hymn_wind_time`. Presets only *gate* volumetric fog, so the rig authors it on (`GraphicsSettings.set_authored`) in a zone that didn't, with no global density, and only on tiers with `god_rays`. |
| **Particulate** | Marine snow: GPUParticles3D in a 14 m box around the camera, shown only below the surface. |
| **Rhen's lantern** | An `OmniLight3D` on `lantern_target`: `oil_lamp`, energy 9, range 9 m, a volumetric halo (`fog_energy`). Oil light, not glimmer (decisions_log N-02). |
| **Light level** | The scene's visible directional lights (energy × colour luminance) over `light_reference` (a noon sun, 3.0). It scales the in-scatter and the underside, so a night dive is dark and the lantern carries the frame. |

Key frames (RX 9070 XT, High, 2×), in `docs/kb/qa/gpu/rnd02/`:
- `below_high.png`: shafts, the lantern, the reef floor;
- `window_high.png`: the Snell window with the sun;
- `waterline_high.png`: the half-submerged split;
- `below_night_high.png`: a night dive, lit by the lantern;
- `below_low.png`: the Low fallback.

## Tiers

`graphics_presets.json` `presets[].tiers.underwater` picks a row of the data's `quality`, and
`GraphicsRuntime.apply_system_tiers` sets it as it does the water's.

| Tier | Post | God rays | Snow | Lantern shadows |
|---|---|---|---|---|
| low | simple: a flat surface, no wave sum per pixel | – | – | – |
| medium | full | – (no fog pass) | 120 | – |
| high | full | yes | 300 | yes |
| ultra | full | yes | 500 | yes |

`active = false` switches every part off (the A/B, or a zone dropping the look), along with the fog it authored.

## Cost (RX 9070 XT, 2560×1440, GPU median; the frame with the rig against `Underwater:active=false`)

| Camera | Preset | With | Without | The rig |
|---|---|---:|---:|---:|
| Below | Low | 0.798 ms | 0.660 ms | +0.14 |
| Below | Medium | 0.967 ms | 0.805 ms | +0.16 |
| Below | High | 1.271 ms | 0.954 ms | **+0.32** |
| Deep | High | 1.457 ms | 1.176 ms | +0.28 |
| UpWindow | High | 1.141 ms | 0.842 ms | +0.30 |
| Below | Ultra | 1.827 ms | 1.108 ms | +0.72 |

The whole underwater frame at High 1440p is 1.1–1.5 ms, inside the 3 ms criterion with room left. Most of
Ultra's extra is its larger volumetric-fog grid and 500 snow particles.

## Using it in a zone

1. Add an `UnderwaterRig` node. Set `water` to the zone's WaterSurface and `lantern_target` to Rhen's lamp node.
2. Add the zone's scene path to the five underwater entries of `prewarm_materials.json`.
3. Nothing else: the rig follows the current camera and the preset.

## Gotchas

- **`gpu_bench` and `capture_preset` now apply every system tier** through `GraphicsRuntime.apply_system_tiers`.
  Before, they set a hand list (or character materials only), so a non-default preset left water, weathering
  and the rig on their defaults. GPU captures at Low, Medium or Ultra can change for that reason alone.
- **Volumetric fog is a gate.** A preset can't turn it on where a scene didn't author it. The rig authors it only
  when it needs the shafts.
- **The rig finds its zone** as the nearest ancestor holding a WorldEnvironment, for the environment and the
  lights. Keep the rig inside the zone's scene.

## Open (Art sign-off: M2-ART-02)

- **Glimmer motes underwater.** They're absorbed with everything else. At noon, held motes are faint by design
  and the in-scatter haze hides them beyond a few metres. At night they survive the dark water, but at this test
  range they're 2–3 px. An "underwater glimmer" boost (compensating the motes' emission for the path's
  transmittance) is Art's call, and probably wanted for Act III's abyss of glimmer.
- **The lantern's halo** reads greenish at night: water strips the oil lamp's red over a few metres (physical).
  `albedo_white_mix` and the `turquoise_shallow` transmittance already warm it; Art may want it warmer.
- **No caustics on characters yet** (a projected caustic light is the obvious next step), and no splash or
  droplets at the crossing.
