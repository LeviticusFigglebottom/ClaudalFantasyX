# 0014 — Light units and exposure: stay on Godot's default units, with a practical exposure per frame

- **Status:** accepted
- **Date:** 2026-10-23
- **Roles affected:** Rendering, Environment, Character, Cinematics, VFX (glimmer), UI (none: UI is post-tonemap)
- **Author role:** Art Director (art-stream-3, M1-ART-04), answering item 3 of Rendering's M1-ART-01 review

## Context
The color script gave every frame an **EV100** (6.0 to 15.0) "for `CameraAttributesPhysical`". Rendering's review (M1-ART-01 review log, item 3) found it isn't actionable: `CameraAttributesPhysical` exposure only means anything with `rendering/lights_and_shadows/use_physical_light_units` on, and the project has it **off** (the default). So the water stream picked `Environment.tonemap_exposure` by eye: 0.65 by day and 1.1 at night.

Every light already in the repo is authored in default units, at the color script's energies (sun 2.0–3.2, moon 0.25, oil lamp 1.2, mote emission 0.6–6.0, sea-glow 0.04–0.15):
- the water test scene and its rig (4 baselines), plus the water bench;
- the three glimmer scenes and `GlimmerField`'s per-mode energies in `glimmer.json` (3 baselines);
- the vegetation test scene (3 baselines);
- the base-body character stage (11 baselines);
- the field-camera test scenes (3 baselines), the battle sandbox, the shader-prewarm scene, and the lighting probe (2 baselines);
- the shaders that add their own light: the water's sun glint, sea-glow (`hymn_sea_glow()`, clamped to 0.04–0.15) and SSS, and the additive HDR mote draw passes.

That's 26 approved baselines and 41 authored energy values in scenes, scripts and data, plus the shader constants. SPEC §8.4 reviews shots against the color script, so the exposure has to be a number Rendering can type in.

## Options
1. **Switch to physical light units.** Set the project setting, give every `Camera3D` (or the `WorldEnvironment`) a `CameraAttributesPhysical` with aperture, shutter and ISO to match each frame's EV100, and restate every light in lux (sun ~100,000, moon ~0.1–0.3), lumens (lamps ~600–800 lm), and nits (emission, sky).
   - *For:* real-world reference values. EV100 becomes literal. Depth of field comes from the lens (`frustum_focal_length` in mm, which matches our lens-in-mm shot specs).
   - *Against:* every light and emissive above must be retuned, and that's not a mechanical ×k. Godot multiplies emissive and sky values by the exposure normalisation, but our shaders write their own `EMISSION` and light terms (sea-glow's 0.04–0.15 clamp, the glint, the mote cores' HDR 2–5), so each one needs re-deriving and re-reviewing. All 26 baselines must be re-approved. The color script's energies become 6–8 orders of magnitude apart, and the narrative rules (sea-glow 0.04–0.15, mote energies) would have to be restated in nits. The art direction gains nothing visible: the AgX curve and the LUT decide the look, not the unit.
2. **Default units, plus a practical exposure multiplier per frame.** Keep every light as it is. Give each color-script frame a `tonemap_exposure` and treat EV100 as an intent label only.
   - *For:* zero retune. Every existing scene and baseline stays valid. The swatch card's measured on-screen values (palette.json `onscreen_hex`) are directly usable because they're stated as `exposure × light`.
   - *Against:* light values have no physical meaning, so energies have to be kept consistent by convention. That's what the color script is for. Lens DOF must be set by hand on `CameraAttributesPractical` (blur distances), not from mm and f-stop.
3. **Default units now, physical later.** That's the same as 2 today, with a planned migration. It was rejected as a stated plan, because a planned migration invites half-converted scenes. If a real need appears (option 1's DOF), a new ADR can supersede this one.

## Decision
**Option 2.** `use_physical_light_units` stays **off**. No Lead action is needed, and `project.godot` doesn't change.

1. **One exposure control: `Environment.tonemap_exposure`**, set per color-script frame in the frame's environment (`game/levels/_mood/<frame_id>.tres`). The color script's "Exposure" column is this value.
   - Measured with the swatch card (`swatch_measure.tscn`): `tonemap_exposure = e` on a value `v` is pixel-identical to exposure 1 on `e·v`. For example, coral_stone at level 2 and at exposure 2 both read `#DBD7CF`.
   - Don't use `CameraAttributesPractical.exposure_multiplier` for frames. With physical units off it **had no effect** on the swatch card (identical output at 1.0 and 2.0). Its effect on lit surfaces wasn't measured, so it isn't a reliable second knob. Cinematic exposure trims (the Ch8 lightning "2.0× exposure for 2 frames") animate `tonemap_exposure` too.
2. **Conversion of the color script's EV100:** `tonemap_exposure = 0.65 × 2^((15 − EV100) / 10)`, rounded to 0.05. That's one stop of practical exposure per 10 EV of intent. It passes through both of Rendering's validated settings: `ch02_noon` EV 15 → **0.65**, and the night water (`ch02_night`/`ch04`, EV 7.5) → **1.09 ≈ 1.1**. The light energies already carry most of the day-to-night drop (sun 3.2 vs moon 0.25 is 3.7 stops), so exposure only trims. The full range is 0.65 (noon) to 1.2 (`ending_dock`). The EV100 numbers stay in the color script in parentheses as intent and are never typed into the engine.
3. **Key product.** A front-lit surface's on-screen value is set by `k = tonemap_exposure × (key energy × N·L + fill)`. The palette's `onscreen_hex` gives each swatch at k = 0.5, 1 and 2. So a frame's exposure and key energy together tell an artist which column of the palette to check against (README.md, "How to pick a value").
4. **No auto-exposure** in gameplay or cinematics. A grade is authored, and the sea-glow's absence in `ending_dock` must not be "corrected" by adaptation.

## Consequences
- Nothing in the repo needs retuning. The 26 baselines stand. The color script's energies remain the authoring source, now with an exposure that can be typed in.
- Exposure and energies are coupled by convention, not physics. A frame that raises its key must lower its exposure, or it moves up a palette column. The review checks `k`, not either number alone.
- Emissive brightness (motes, sea-glow, flames) scales with `tonemap_exposure` like everything else. So the night value rules (color script rule 3: glow on/off ≥ 1.5×, moonlit stone ≤ 2.5× the glowing sea) are stated as ratios that hold at any exposure.
- Lens DOF is set on `CameraAttributesPractical` by blur distance. If Cinematics needs DOF tied to lens mm and f-stop, or a lighting pipeline needs photometric data, reopen this with a new ADR. The migration cost recorded above (every energy, every self-lit shader term, 26+ baselines) is the price to weigh.
- `docs/kb/art/color_script.md` (conventions, strip summary, every frame's exposure row) and `docs/kb/art/environments/haluna.md` are converted in the same change.
