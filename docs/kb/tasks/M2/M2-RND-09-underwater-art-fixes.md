---
id: M2-RND-09
title: "Underwater look: Art's changes from M2-ART-02 (swatches, warm lantern halo, glimmer compensation, sea-glow at night)"
role: rendering
status: review
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
depends_on: [M2-ART-02]
milestone: M2
reviewer: character
request-from: character
---
## Goal
M2-ART-02 approved the underwater look (M2-RND-02) with changes. The Snell window and the Low fallback pass as built. This task makes the changes. The measurements and the reasons are in M2-ART-02's Review log. All numbers are Oklab, on the 960×540 GPU key frames in `docs/kb/qa/gpu/rnd02/`. On-screen targets are palette.json `onscreen_hex`.

## Acceptance criteria
- [x] **1. Swatches in `game/data/vfx/underwater.json` match the lagoon's water look** (color_script.md `lagoon_clear`: scatter `lagoon_teal`, deep `deep_teal_shadow`).
  - `scatter`: `turquoise_shallow` → **`lagoon_teal`** (`#1FA3A6`).
  - `transmit`: `turquoise_shallow` → **`lagoon_teal`**, with `transmit_distance_m` 20 → **40**. Green visibility stays about where it is (σ_G 0.023 → 0.025 m⁻¹). Blue now carries slightly further than green, and red is absorbed less (σ_R 0.150 → 0.107 m⁻¹, which also warms the lantern).
  - `deep`: `abyss_navy` → **`deep_teal_shadow`** as the default (Act I lagoons). A zone on the `night_sea` look (ch20, ch21, night dives) overrides it with `abyss_navy`. Add a per-zone or per-look override on the rig, so one file does not force one deep colour on every chapter.
  - **Pass:** in `below_high`, the lower water, the floor and the sun-side water read Oklab hue ≥ 195°. They are now 192°, 183° and 184°, drifting green. The mid-water stays within ΔE_ok 0.05 of `deep_teal_shadow` +1 `#106776` (now 0.020).
- [x] **2. Total internal reflection is not `sea_glow` by day.** `tir` → **`deep_teal_shadow`**, scaled so the day TIR keeps about its current on-screen value. It now measures `#196775`, ΔE 0.012 to `sea_glow` 0, which is the right *value*. `sea_glow` is "emission only, never a lit surface colour", and it is the anchored-dead signal whose absence ends the game. It must not stand in for a day reflection.
- [x] **3. Night: sea-glow in the water column** (colour script rule 3: "on the sea surface and in the water column"). Add `sea_glow` emission at the zone's sea-glow energy (0.04–0.15, from the WaterSurface) to the in-scatter and the underside. It must be independent of the light level, so a night dive is dark but teal, not black-navy. **Pass:** in `below_night_high`, the open water away from the lamp reads Oklab hue 190–230° with C ≥ 0.05 (now `#002233`, h 235°, C 0.050), and on/off ≥ 1.5×, as rule 3(a) asks on the surface.
- [x] **4. Rhen's lantern halo reads warm** (rule 4: oil flame is the only warm practical, and the last light in the game). It is now green: `#005D33` (h 155°, C 0.10) beside the lamp, `#035536` (h 160°) above it at night, and `#26907C` (h 177°) by day. `albedo_white_mix` 0.5 → **1.0** for the lantern's light, plus item 1's lower red absorption, should be enough (the arithmetic is in M2-ART-02). Use a separate lantern fog volume if the day shafts must keep a 0.5 mix.
  - **Pass:** in `below_night_high`, the halo within 0.5 m of the lamp (about 60 px) reads Oklab hue 45–95° with C ≥ 0.04, in the `oil_lamp` family (on-screen 0 `#CFA67C`, h 67°). Out to 2–3 m it may cool through neutral into the water's teal (h ≥ 190°). No halo pixel sits in the green band (h 120–175° with C > 0.04).
- [x] **5. Glimmer motes underwater: compensate the path, but only for cameras underwater.** The motes' emission is divided by the path transmittance, so they read through the water. The in-scatter haze still hides far motes, so depth stays legible.
  - **Released (`glimmer_lift`, rising): full compensation (1.0).** Rising light must read through the water: the Ch20 Vowbound releases, the Ch21 Letting, and the Ending's motes still rising through the sea.
  - **Held (`glimmer_held`): 0.6** (60% of the lost light restored). Held light is fainter and is meant to fade as it sinks.
  - Clamp so no mote core reads above its swatch's on-screen +1 (`#E2DBCC` lift, `#B2D1D8` held). The frame-fraction limits stand (day 3%, night 12%, set piece 35%).
  - A per-field opt-out (`underwater_compensation = 0`) exists. Ch2's nine sinking motes are seen from above the surface (the water shader, not the rig), so they are unaffected and keep fading by absorption, as the colour script requires.
  - The Act III "abyss of glimmer" gets its brightness from this plus ch20/ch21's emission energies (3.0, 6.0). No extra boost.
- [x] **6. `waterline_high` shows the split.** The GPU frame's upper half is TIR (`#156074`, ΔE 0.034 to `sea_glow`), not air, while the lavapipe baseline `underwater_waterline` shows sky, sea and the underwater half. Recapture with the lens on the waterline (or explain the difference). On that frame, the meniscus reads as one continuous thin line. It is now a broken, aliased white streak.
- [x] Recapture the five key frames (and re-approve the `underwater_*` lavapipe baselines if they move). Name Art (character) as the reviewer.

## Notes
- Not part of this task: caustic light on characters (SPEC §8.2 item 2) is still open in tech/underwater.md. It is needed before the first underwater zone ships.
- Item 1 also moves `below_low`. That frame already reads h 210–212° in the water and will stay inside the pass band.

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Key frames: `docs/kb/qa/gpu/rnd09/` (RX 9070 XT, High, 960×540): `below_high`, `window_high`, `waterline_high`,
`below_night_high`, `below_low`, plus `below_night_motes_high` (released motes) and `tir_day_high` (the camera 8 cm
under, for the TIR). All numbers are Oklab, region means. Reviewer: **Art (character)**.

1. **Swatches.** scatter and transmit are `lagoon_teal` (transmit_distance_m 40). deep is `deep_teal_shadow`, and a
   new `looks.night_sea` (UnderwaterRig.look) keeps `abyss_navy` for ch20, ch21 and night dives.
   - `below_high`: lower water h 199.3°, floor 196.8°, sun-side 201.9° (all ≥ 195°; they were 191–192°, 183°,
     188° on my regions).
   - The mid-water is ΔE 0.022 from `deep_teal_shadow` +1.
   - `below_low`: water h 214°, lower water 199°.
2. **TIR.** `deep_teal_shadow` × `tir_gain` 2.2. Day TIR now `#1B6681` (L 0.48), against `#145F73` (L 0.45)
   before: about the same value, and no longer `sea_glow`.
3. **Night sea-glow** in the column and the underside, at the WaterSurface's `sea_glow_energy` × 1.8, independent
   of the light level.
   - `below_night_high`: open water `#003243`, h 228.2°, C 0.058 (it was `#002131`, h 232°, C 0.048).
   - Sea-glow on/off is 2.2× (the bar is 1.5×).
4. **The lantern halo is now the post's own** single scattering of the lamp. Why: the volumetric fog's halo was
   absorbed over the whole path to the background, 60+ m, so its red went to zero and it turned green. A white fog
   albedo couldn't fix that.
   - Settings: absorbed lamp → point → camera at `halo_absorption` 0.35 ("physics yields"), inside
     `halo_range_m` 4 m. `fog_energy` is 0, and the shafts keep `albedo_white_mix` 0.5.
   - Within 60 px (0.5 m): h 71.9–75.4°, C 0.064–0.070 (it was h 155–159°).
   - At 120–250 px (1–2 m) it's h 214.5°, the water's teal.
   - Green-band pixels (h 120–175°, C > 0.04): **0** (it was 54,049).
   - It shows on every tier now, Low and Medium included.
5. **Glimmer.** While the camera is underwater, the motes' core and halo are divided by the path transmittance:
   released 1.0, held 0.6, capped at `max_gain` 8. `GlimmerField.underwater_compensation = 0` opts out.
   - **Found:** a field underwater was invisible before this. Its own above-water sinking model (`exp(-2.2 ×
     depth)`) killed every mote below the surface, which is e⁻¹⁰ at the test's 4.6 m. So the rig now also zeroes
     the field's absorption while the camera is underwater, and restores it when the camera is above water or the
     field opts out. Ch2, with no rig, is unchanged.
   - Night test field (`below_night_motes_high`): held motes cover 1.24% of the frame and released 1.75% (the
     night cap is 12%). Peak luminance 0.52, under `glimmer_held` +1 (0.60) and `glimmer_lift` +1 (0.71).
6. **Waterline.** The GPU frame differed from lavapipe because the test rig drives its own wave clock, and on the
   GPU capture the fixed camera sat under a crest. Physically that's right (TIR above 48.6° from vertical), but it
   wasn't the shot.
   - The Waterline camera now rides the surface (`WaterlineCamera`, `offset_m` 0.03).
   - The underside is discarded nearer than `lens_m`, consistent with the post.
   - The split is antialiased in screen space, with a 1.5 px meniscus: one continuous thin line. `waterline_high`
     shows sky (h 243°), the sea surface and the water (h 204°).
- **Cost (1440p, GPU):** the rig is High +0.37 ms (was +0.32), Low +0.17 (was +0.14), Ultra +0.72 (same).
- **Lavapipe baselines that will drift** (for the Lead to re-approve on lavapipe; I didn't touch them):
  `underwater_below`, `underwater_window`, `underwater_waterline`. The waterline one changes most: its camera now
  rides the surface.
- **Checks:** gdlint and gdformat, validate_data, taskboard, the tools unittests, and the full Godot suite
  (1454/0; underwater 8/0).

## Review log
