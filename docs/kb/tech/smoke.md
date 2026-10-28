# Smoke: the volumetric column (M3-RND-21)

Owner: env-art-b, for Rendering's zone and kit looks (the Lead, 2026-10-28). Code: `game/vfx/smoke/smoke_column.gd`
(`SmokeColumn`) and `smoke_column.gdshader`. Data: `game/data/vfx/smoke_column.json`. Placed by ZoneKitDressing's
`smokes` rows. Its first use is the Ch6 raid camp (`tools/act1/ch06_brine_shoals_dressing.py`'s `SMOKES`, on the
Smoke block).

## How it works
The node builds a box that bounds the column and draws the shader on the box's **back faces**, with no depth test.
So a camera inside the smoke still sees it, and nothing in front of the smoke hides it wrongly. Each pixel marches
its view ray through the box in the column's own frame, up to the opaque scene (read from the depth buffer). It
composites density front to back and stops once the ray is 98 % opaque.

| Part | How |
|---|---|
| **Shape** | The kit plume's frame: up +Y to `height_m`, a spine bending downwind toward +X by `lean_m × h^1.5` (with a small wobble), and a radius from `base_radius_m` to `top_radius_m`. The column thins by `top_thin` as it rises, and fades in over `base_fade` and out over `top_fade`. |
| **Billows** | 3-octave value fBm at `noise_scale_per_m`, rising at `rise_m_s` on `hymn_wind_time` (never `TIME`), offset per column by `seed`. It breaks the edge by `edge_noise` and modulates the density. |
| **Light** | Unshaded. An outward normal per sample (radial, tipped up) against the sun mixes `col_core` and `col_lit`, so sun sides and tops are lit and the core is darker. Looking toward the sun adds `forward_scatter` (the backlit glow). `col_fire × fire_glow` warms the lowest `fire_band`. It is not lit by the zone's lamps, and it neither casts nor receives shadow. |
| **Steps** | Per preset from the data: Low 12, Medium 20, High 32, Ultra 48. The first step is offset by interleaved gradient noise, so there is no banding. The finer dither replaced a white hash's grain at the column's foot. |

The camp profile is grey to grey-brown (`#C4BCAE` lit, `#2E2C2A` core, `ember_orange` fire), density 1.2, the kit
plume's 14 m × 9 m lean. Viewed in `ch06_brine_camp` and `ch06_brine_road` (5 to 150 m).

## Open
- **Cost** on the PC presets is unmeasured (criterion: under 0.3 ms at High 1440p for four columns). The march is
  32 steps × one 3-octave fBm per sample, over the box's screen area.
- **The tier hook:** `GraphicsRuntime.apply_system_tiers` doesn't call `set_quality` yet (request M3-ARC-1324).
- **The kit preview and the camp arenas** still draw env-art's shells (request M3-ENV-1324).
- **Shadow and lamps:** the column is self-lit, so the zone's fire lights don't light it and it casts no shadow on
  the camp.
