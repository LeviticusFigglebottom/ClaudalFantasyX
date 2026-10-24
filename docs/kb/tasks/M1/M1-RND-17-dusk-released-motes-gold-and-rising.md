---
id: M1-RND-17
title: Dusk released motes read gold and rising (halo chroma, streak axis)
role: rendering
status: doing
reviewer: character
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-17-dusk-motes)"
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

## Notes (PC GPU session, branch gpu/rnd-17-dusk-motes)

Report: `docs/kb/qa/gpu/2026-10-23-rnd-17-dusk-motes.md`. All numbers are on the GPU capture rig (960×540, scene
defaults), measured with the sign-off method, now `tools/screenshots/mote_metrics.py`. On the current baseline it
reproduces 87° / 175° / 136°, |Δab| 0.039, and a median streak angle of 37°.

**Met:**
- **Streaks:** median 5.7° (≤ 25), 84 % within 30° (≥ 70), 3 % beyond 60° (≤ 5).
- **Upper sky:** hue 76° (75–95), |Δab| 0.060 (≥ 0.06).
- **Halo chroma at or above the background:** horizon 0.044 against 0.043, mirror 0.045 against 0.036.
- **Coverage** 16.3 % (≤ 18).
- **The spiral keeps its radius, rise and rate:** 1.6 turns per mote in 10 s.
- **Nothing else moves:** `glimmer_night_held` 0.00004, `glimmer_bound` 0.0001, `save_shrine_field` 0.00001 RMSE on
  the GPU. Water is untouched.

**Not met:**
- **Horizon:** hue 139° and |Δab| 0.024, against 75–95° and ≥ 0.04.
- **Mirror:** hue 102° and |Δab| 0.031.
- Why: on a red-peach sky (a 0.037, b 0.024), added light reads gold only if its own a/L is at least the sky's. At
  83° that needs C/L ≥ 0.46, past the gamut. The inner-halo band there is also dominated by the pale cores, which
  this task says not to tint. The horizon-warm hue (55° within 8° of the horizon) moved it from 175° to 139°.
  Reaching 75–95 would need either a gold core near the horizon, or a target measured on the halo only. That is
  the Art Director's call.
- **Heads-down:** 6 % (≤ 2). By this script's definition the baseline was already 7 %, against the sign-off's 3/96,
  so the count method differs. Art should re-count with their own method.
- **Core chroma:** 0.031 (permitted ≤ 0.03, not required).

**Checks.** `mote_halo` and `mote_streaks` are in palette_checks.json as `advisory` (warn, don't fail), and
palette_check gained the `advisory` flag. Turn them strict when `glimmer_dusk` is re-approved.

**Drift:** `glimmer_dusk` (RMSE 0.0147 on the GPU) and `glimmer_release` (0.0140). Re-approve both after looking.

**Reviewer:** character (Art Director).

## Notes (PC GPU session, v2 after review-sweep-N; branch gpu/rnd-17-dusk-motes-v2)
- **B1:** the gold floor is gated by `smoothstep(0.6, 1, released)`, so mid-lerp motes keep their own hue.
  `glimmer_release` now differs from its baseline by RMSE 0.0043 on the GPU (v1: 0.0145).
- **B2:** the 55° near-horizon switch only applies to a field with `warm_horizon_halo` (glimmer_dusk sets it). Night
  and noon fields keep the released hue at the horizon. Tested.
- **S1:** `halo_chroma_min` 0.23 → 0.25. Upper sky: hue 76.0°, |Δab| 0.0598. |Δab| plateaus at about 0.060 inside
  75–95° (0.27 gives 0.0602 but hue 74°), so the check uses `dab_min` 0.059 with a note.
- **S2/S3:** `halo_hue_deg` is derived from `colors.released` (Oklab hue, `GlimmerField.released_hue_deg()`). No
  duplicated constants.
- **S4:** the checks carry the re-scoped targets (horizon ≤ 145°, mirror 75–110°, chroma not below the background,
  heads-down ≤ 0.07). They stay `advisory` until the Lead re-approves `glimmer_dusk`; flip them strict in that commit.
- **GPU, `glimmer_dusk`:** upper sky 76° / 0.060, horizon 138° (≤ 145 ✓), mirror 100° (75–110 ✓), chroma not below
  the background ✓, coverage 16.3 %, streaks 5.9° median / 86 % within 30° / 3 % beyond 60° / heads-down 0.05.
- **Drift (GPU):**
  - `glimmer_dusk` 0.0146: re-approve it.
  - `glimmer_release` 0.0043: just over the 0.004 gate. Its mid-lerp halos are the old cyan-white; only fully
    released motes are gold. Look at it before re-approving.
  - `glimmer_night_held`, `glimmer_bound` and `save_shrine_field`: ≤ 0.00004.

## Review log
- 2026-10-23 character (review-sweep-N, fresh reviewer, Art Director): **changes needed.** The streak fix and the dusk look are approved. The gold-halo floor breaks colour-script rule 1 in `glimmer_release`, so its baseline must not be re-approved as it stands.
  - **What I read:** this task, `docs/kb/qa/gpu/2026-10-23-rnd-17-dusk-motes.md`, color_script.md "Art sign-off 2026-10-23", and `git diff c3517dc^1 c3517dc` (process and draw shaders, glimmer.json, glimmer_field.gd, palette_check.py, mote_metrics.py and its test).
  - **Checks:** `HYMN_SKIP_BLENDER=1 HYMN_SHOTS=<glimmer_*, water_*, veg_*, haluna_h0*, asha_*, save_shrine_field> tools/ci_local.sh`: every gate up to the shots passes (Godot 1174/0). Lavapipe: `glimmer_dusk` **0.01471** and `glimmer_release` **0.01451** (both FAIL, as predicted). `glimmer_night_held` 0.00000, `glimmer_bound` 0.00000 and `save_shrine_field` 0.00160 pass. I ran `mote_metrics.py` on the lavapipe capture: it reproduces the GPU table to the third decimal.
  - **What I viewed:** both glimmer captures against their baselines at full size, plus 4× crops of the release shot's right-hand sky and its horizon band.
  - **What passes:**
    - **The streaks read rising.** Median 5.9°, 83 % within 30°, 3 % beyond 60°. The dusk still frame now reads as an ascent, not the held grammar. Leaving the tangential term out of `CUSTOM.xyz` is the preferred fix, and `spiral_rate_rad_s` 1.0 is kept.
    - **The upper sky reads gold.** Hue 76°, and coverage is 16.2 %, so the gold was not bought with size.
    - **Horizon and mirror:** chroma under the halo is now at or above the sky's (0.044 against 0.043, and 0.045 against 0.036). The halo no longer bleaches the sky.
    - Held and bound motes are untouched.
  - **Art decision on the horizon and mirror hue (asked in the report).** I accept the gamut argument: on the peach band, added gold cannot pull Δab to 75–95°. I re-scope those two targets as follows:
    - **horizon:** Δab hue ≤ 145° (from 175°), plus chroma not below the background;
    - **mirror:** hue 75–110°, plus chroma not below the background.
    - Keep the 0.04 |Δab| floor as advisory there.
    - Heads-down: by this script, ≤ 0.07 is a non-regression (the baseline was 0.085). Drop the sign-off's 2 % figure, because its count method can't be reproduced.
    - Don't tint the cores to chase the hue.
  - **Blockers:**
    - **B1: two hues per mote in `glimmer_release`** (glimmer_motes_draw_body.gdshaderinc:106-111). The floor is mixed in by `released` = `INSTANCE_CUSTOM.w`, the release blend, so mid-lerp motes get an amber halo around a cyan-white core. The 4× crop of x 600–960 shows it plainly; in the baseline those halos were white-cyan. Rule 1 and this task's own note say one hue per mote.
      - Fix: drive the floor by the core's own warmth (its Oklab b, as the old `warm` term did), or by `smoothstep(0.6, 1.0, released)`, and not by the raw blend.
    - **B2: the horizon hue band is geometric, not sky-aware** (:108-109). At night (`glimmer_release`, dark blue sky) the 8° band turns halos near the horizon a copper orange (55°). That is neither gold nor the held cyan. The 55° switch exists for a peach dusk sky only.
      - Fix: gate it per field or per mood (a `halo_hue_horizon_deg` the zone sets, defaulting to `halo_hue_deg`), or weight it by the sky warmth the scene publishes.
  - **Should-fix:**
    - **S1:** the upper sky |Δab| is 0.0597 on lavapipe, a hair under the 0.06 target. Once the check goes strict, it fails. Raise `halo_chroma_min` slightly (about 0.23), or set `dab_min` to 0.059 with a note.
    - **S2:** the halo hue is a fixed constant (`halo_hue_deg` 83), whatever the field's released palette is. A future released colour that isn't `glimmer_lift` (M2 Drownbell VFX) would still get a gold halo. Derive it from the released colour, or document the coupling in glimmer.md.
    - **S3:** glimmer_field.gd:540-541 duplicates the shader defaults (83.0) as fallbacks. Read them from glimmer.json only, or name a constant.
    - **S4:** turn `mote_halo` and `mote_streaks` strict, with the re-scoped targets above, in the same commit that re-approves `glimmer_dusk`.
  - **Baselines:**
    - **`glimmer_dusk` (0.0147): approve the look.** Re-approve it after B1/B2 land, because the fix will move it again.
    - **`glimmer_release` (0.0145): reject** (B1, B2).
  - **Still owed:** Art's numbers in color_script.md "Art sign-off" after the fix. This review log is the record until then.
- 2026-10-23 lead: the code merge was REVERTED on the integration branch (e97dd41 / 9a57a8c) because the review-sweep-N blockers broke lavapipe shots. The reports and notes are kept. The PC reworks it on its gpu/ branch: rebase on the integration branch, fix the blockers, and resubmit.
