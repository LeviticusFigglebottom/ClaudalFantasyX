---
id: M2-RND-09
title: "Underwater look: Art's changes from M2-ART-02 (swatches, warm lantern halo, glimmer compensation, sea-glow at night)"
role: rendering
status: todo
owner_session: ""
depends_on: [M2-ART-02]
milestone: M2
request-from: character
---
## Goal
M2-ART-02 approved the underwater look (M2-RND-02) with changes. The Snell window and the Low fallback pass as built. This task makes the changes. The measurements and the reasons are in M2-ART-02's Review log. All numbers are Oklab, on the 960×540 GPU key frames in `docs/kb/qa/gpu/rnd02/`. On-screen targets are palette.json `onscreen_hex`.

## Acceptance criteria
- [ ] **1. Swatches in `game/data/vfx/underwater.json` match the lagoon's water look** (color_script.md `lagoon_clear`: scatter `lagoon_teal`, deep `deep_teal_shadow`).
  - `scatter`: `turquoise_shallow` → **`lagoon_teal`** (`#1FA3A6`).
  - `transmit`: `turquoise_shallow` → **`lagoon_teal`**, with `transmit_distance_m` 20 → **40**. Green visibility stays about where it is (σ_G 0.023 → 0.025 m⁻¹). Blue now carries slightly further than green, and red is absorbed less (σ_R 0.150 → 0.107 m⁻¹, which also warms the lantern).
  - `deep`: `abyss_navy` → **`deep_teal_shadow`** as the default (Act I lagoons). A zone on the `night_sea` look (ch20, ch21, night dives) overrides it with `abyss_navy`. Add a per-zone or per-look override on the rig, so one file does not force one deep colour on every chapter.
  - **Pass:** in `below_high`, the lower water, the floor and the sun-side water read Oklab hue ≥ 195°. They are now 192°, 183° and 184°, drifting green. The mid-water stays within ΔE_ok 0.05 of `deep_teal_shadow` +1 `#106776` (now 0.020).
- [ ] **2. Total internal reflection is not `sea_glow` by day.** `tir` → **`deep_teal_shadow`**, scaled so the day TIR keeps about its current on-screen value. It now measures `#196775`, ΔE 0.012 to `sea_glow` 0, which is the right *value*. `sea_glow` is "emission only, never a lit surface colour", and it is the anchored-dead signal whose absence ends the game. It must not stand in for a day reflection.
- [ ] **3. Night: sea-glow in the water column** (colour script rule 3: "on the sea surface and in the water column"). Add `sea_glow` emission at the zone's sea-glow energy (0.04–0.15, from the WaterSurface) to the in-scatter and the underside. It must be independent of the light level, so a night dive is dark but teal, not black-navy. **Pass:** in `below_night_high`, the open water away from the lamp reads Oklab hue 190–230° with C ≥ 0.05 (now `#002233`, h 235°, C 0.050), and on/off ≥ 1.5×, as rule 3(a) asks on the surface.
- [ ] **4. Rhen's lantern halo reads warm** (rule 4: oil flame is the only warm practical, and the last light in the game). It is now green: `#005D33` (h 155°, C 0.10) beside the lamp, `#035536` (h 160°) above it at night, and `#26907C` (h 177°) by day. `albedo_white_mix` 0.5 → **1.0** for the lantern's light, plus item 1's lower red absorption, should be enough (the arithmetic is in M2-ART-02). Use a separate lantern fog volume if the day shafts must keep a 0.5 mix.
  - **Pass:** in `below_night_high`, the halo within 0.5 m of the lamp (about 60 px) reads Oklab hue 45–95° with C ≥ 0.04, in the `oil_lamp` family (on-screen 0 `#CFA67C`, h 67°). Out to 2–3 m it may cool through neutral into the water's teal (h ≥ 190°). No halo pixel sits in the green band (h 120–175° with C > 0.04).
- [ ] **5. Glimmer motes underwater: compensate the path, but only for cameras underwater.** The motes' emission is divided by the path transmittance, so they read through the water. The in-scatter haze still hides far motes, so depth stays legible.
  - **Released (`glimmer_lift`, rising): full compensation (1.0).** Rising light must read through the water: the Ch20 Vowbound releases, the Ch21 Letting, and the Ending's motes still rising through the sea.
  - **Held (`glimmer_held`): 0.6** (60% of the lost light restored). Held light is fainter and is meant to fade as it sinks.
  - Clamp so no mote core reads above its swatch's on-screen +1 (`#E2DBCC` lift, `#B2D1D8` held). The frame-fraction limits stand (day 3%, night 12%, set piece 35%).
  - A per-field opt-out (`underwater_compensation = 0`) exists. Ch2's nine sinking motes are seen from above the surface (the water shader, not the rig), so they are unaffected and keep fading by absorption, as the colour script requires.
  - The Act III "abyss of glimmer" gets its brightness from this plus ch20/ch21's emission energies (3.0, 6.0). No extra boost.
- [ ] **6. `waterline_high` shows the split.** The GPU frame's upper half is TIR (`#156074`, ΔE 0.034 to `sea_glow`), not air, while the lavapipe baseline `underwater_waterline` shows sky, sea and the underwater half. Recapture with the lens on the waterline (or explain the difference). On that frame, the meniscus reads as one continuous thin line. It is now a broken, aliased white streak.
- [ ] Recapture the five key frames (and re-approve the `underwater_*` lavapipe baselines if they move). Name Art (character) as the reviewer.

## Notes
- Not part of this task: caustic light on characters (SPEC §8.2 item 2) is still open in tech/underwater.md. It is needed before the first underwater zone ships.
- Item 1 also moves `below_low`. That frame already reads h 210–212° in the water and will stay inside the pass band.

## Review log
