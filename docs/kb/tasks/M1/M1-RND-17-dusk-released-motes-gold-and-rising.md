---
id: M1-RND-17
title: Dusk released motes read gold and rising (halo chroma, streak axis)
role: rendering
status: todo
owner_session: ""
depends_on: [M1-RND-08]
milestone: M1
request-from: "character"
---
## Goal
In the M1-ART-05 sign-off (Art Director, 2026-10-23), `glimmer_dusk` got **changes needed**. Its released motes break colour-script rule 1 in two ways that a player would read:
1. **They read white, not gold.** `look.halo_chroma_gain` 1.6 has no measurable effect on lavapipe. Each halo *lowers* the chroma of the sky it sits on, and against the peach horizon it shifts the sky toward cyan.
2. **They read as scattering sparks, not a rising spiral.** Since `spiral_rate_rad_s` went 0.3 → 1.0, the streaks fan out diagonally. Sideways motion is the *held* grammar, so the still frame now mixes the two meanings.

`center_bias` 1.8 passes, and so do the held, bound and release shots. Leave them as they are.

## How to measure (lavapipe baseline, 960×540; Art used this method)
- **Background:** the per-row 30th percentile of linear sRGB over every pixel outside the figure box x 445–515, y 200–470. The sky and the mirror are uniform along each row.
- **rel:** for each pixel, (pixel luminance − background luminance) / background luminance, using Rec.709 weights.
  - **Inner halo:** 0.6 < rel ≤ 2.0.
  - **Coverage:** rel > 0.10.
- **Δab:** mean of (pixel Oklab − background Oklab) over the selected pixels, reported per region:
  - upper sky (blue-lilac): y 0–180;
  - horizon band (peach): y 250–360;
  - mirror: y 365–540.
- **Streaks:** blobs of rel > 0.35 with at least 12 px. Take the luminance-weighted PCA of each blob, and keep blobs whose elongation (√ of the eigenvalue ratio) is ≥ 2. The angle is measured from screen vertical. A blob is **heads-down** when its brightest pixel lies more than 1 px below the centroid along the streak axis.
- Please add both measurements as checks in `tests/screenshots/palette_checks.json` (a new check `kind` in `tools/screenshots/palette_check.py`, with a unit test) so the targets stay gated.

## Acceptance criteria
- [ ] **Halo hue and chroma (gold, one hue per mote).** In `glimmer_dusk`, inner-halo Δab has hue **75–95°** in all three regions. `glimmer_lift` is h 83°. Today's values are 87° / **175°** / 136°.
- [ ] **Halo chroma, blue sky.** Inner-halo |Δab| in the upper sky is **≥ 0.06** (today 0.039; before RND-08 0.040).
- [ ] **Halo chroma, horizon and mirror.** Inner-halo |Δab| in the horizon band and the mirror is **≥ 0.04** (today 0.023 and 0.021). The median pixel chroma under the inner halo is **≥ the background's** (today 0.029 against 0.043 at the horizon, and 0.029 against 0.036 on the mirror). The halo must enrich the sky, not bleach it.
- [ ] **The cores may stay pale.** A median core chroma ≤ 0.03 (`glimmer_lift_hi`, "fades into the sky") is fine. Don't tint the cores to reach the halo targets.
- [ ] **No gold bought with size.** Coverage (rel > 0.10) stays **≤ 18 %** (today 16.8 %), and the `palette_check` gold swatch mask stays 0 %.
- [ ] **Why 1.6 fails, and the expected fix.** The gain multiplies `glimmer_lift`'s own on-screen chroma, which is C 0.022–0.037 (palette.json −1 / 0 / +1). 1.6× that is still below the dusk sky's 0.04–0.06. Suggested fix: an absolute warm-halo chroma, `look.halo_chroma_min` of about 0.08 at the mote's hue (about `sun_gold` "−1", C 0.078). If you keep the multiplier, a gain of about 2.5 or more. Record the final value in glimmer.md and glimmer.json.
- [ ] **The streaks read rising.**
  - Median streak angle from vertical **≤ 25°** (today 37°; before RND-08 20°).
  - **≥ 70 %** of streaks within 30° (today 32 %).
  - **≤ 5 %** beyond 60° (today 10 %).
  - **≤ 2 %** heads-down (today 3 of 96).
- [ ] **Keep the spiral in motion.** Colour-script rule 1's spiral radius (0.2–0.6 m) and rise (0.15–0.4 m/s) are unchanged. Preferred fix: draw the streak along the rise and curl drift velocity only, leaving out the spiral's tangential term, so `spiral_rate_rad_s` 1.0 still reads as a spiral in play. If you lower the rate instead, cap the tangential speed per mote at ω·r ≤ 0.45 × its rise speed. Note in glimmer.md how the spiral looks in a 10 s bench or editor run: at least one visible turn per mote.
- [ ] **Nothing else moves.**
  - `glimmer_night_held`, `glimmer_bound` and `water_*` stay within RMSE 0.004 of their current baselines.
  - The held and bound halo hues stay as they are: held is about 217°, bound's core is about 193–205°.
  - Re-approve `glimmer_dusk`, `glimmer_release` (its gold half inherits the halo) and `save_shrine_field`, if they move. Look at each one first.
- [ ] Back to **review** with **character** (Art Director) as the reviewer. Art re-measures with the method above and records the result in docs/kb/art/color_script.md, "Art sign-off".

## Notes
- The numbers come from M1-ART-05 (docs/kb/art/color_script.md, "Art sign-off 2026-10-23").
- The pre-RND-08 `glimmer_dusk` comes from `git show cb318dc^:tests/screenshots/baselines/glimmer_dusk.png`.

## Review log
