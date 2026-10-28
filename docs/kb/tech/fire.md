# Fire: the camp burnings' flame tongues (M3-RND-1315)

Owner: env-art-b, for Rendering's zone and kit looks (the Lead, 2026-10-28). Code: `game/vfx/fire/flame_tongue.gdshader`.
Used by: the Brine Shoals kit's `camp_fire_large` and `camp_fire_small` (`assets_src/environments/kits/brine_shoals/
b_fire.py`), whose `bs_fire_outer` and `bs_fire_core` slots are ShaderMaterials written by that module. They burn in the
`ch06/brine_shoals` raid camp (the Smoke block's `RAID_FIRES`) and the `salvage_camp_burning` arena.

| Part | How |
|---|---|
| **Lick** | In object space (origin at the fire bed), each vertex sways by `sway_m × h²` (h: its height over `height_m`), two sines per axis, and stretches up to ±`stretch` as a lick runs up; each placed fire takes its own phase from its world position. The bed never moves. |
| **Tear** | Two octaves of value noise rising at `rise_m_s` discard the upper part of each tongue below `tear × smoothstep(0.35, 1, h)`: the tips break and re-form. |
| **Colour** | Unshaded. The foot is `base_color` × `foot_gain`, running to `tip_color` × `tip_gain`, with a ±`flicker` slow noise per fire and the tear noise's shading. The palette swatches are dusk_gold → ember_orange for the tongues and sun_gold → dusk_gold for the heart. An ember_orange foot went flat red under the ch06 grade, and an oil_lamp one went peach. `emission` is 0, because adding it to the unshaded colour clipped the grade. Never glimmer colours (references.md §1.4 rule 10). |
| **Clock** | `hymn_wind_time` (the capture holds it), never `TIME`; `tests/unit/test_flame_tongue.gd` checks it. |

Lighting stays the zone's: the camp's `fire_lights` (shadowless omnis) light the ground around each fire.

**Open:** the cost on the PC presets is cheap by construction (two value-noise octaves per flame pixel, a few hundred
vertices per fire) but unmeasured. There are no embers or sparks rising: Rendering's particle library has none for fire yet.
