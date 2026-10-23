---
id: M1-ENV-01
title: Five-shot environment mood test (coastal village)
role: environment
status: done
owner_session: environment-stream-3 (worktree agent-aaa0dfc3de4f41ded)
reviewer: rendering, art-director
depends_on: [M1-RND-01, M1-ART-01]
milestone: M1
request-from: ""
---
## Goal
SPEC §10.2 M1 exit criterion.

## Acceptance criteria
- [x] Procedural kit sample (village timber/thatch + ruined coral concrete): 31 seeded pieces in
  `assets_src/environments/kits/haluna/` (byte-identical rebuilds), with PROVENANCE rows
- [x] 5 composed camera shots matching the Act I color script frame: `haluna_h01`–`h07` baselines, graded
  to `ch02_noon` with the zone LUT
- [x] GI choice recorded in the zone README (`game/levels/_tests/haluna_mood/README.md`): SDFGI is the
  shipping choice, but the frames are rendered with SDFGI off (it measured black shade on lavapipe), and a
  GPU re-test is requested

## Notes
- The review, checklist and gap analysis are in `docs/kb/art/environments/haluna_mood_review.md`. My
  honest estimate is ~40% of art-complete for these five frames. The sky is the largest gap.
- Weathering shader: `game/shaders/environment/env_weathering*.gdshader`, with 4 tiers and a live wet line
  through `WeatheringTide`.
- Placeholders (tagged): `banyan_placeholder`, `windbreak_placeholder`, `shell_shrine_massing`.
- Requests:
  - Lead: a `hymn_tide` global, and a packing ADR.
  - Rendering: an SDFGI GPU re-test, adopting the LUT tool, the sky, and a weathering preset mapping.
  - Vegetation: the banyan and the windbreak tree.
- **Rework on review-sweep-F (environment-stream-3, 2026-10-23).** Merged the session branch first
  (M1-RND-08 water, M1-RND-09, M1-ENV-04 shrine), then approved the five baselines once with everything
  included. Measured with the new `tools/screenshots/palette_check.py` (Oklab, ΔE_ok). The targets are
  checked on every tools test run by `tests/screenshots/palette_checks.json` + `tools/tests/test_palette_check.py`.
  The old baselines fail 15 of the 19 checks; the new ones pass all 19.

  | Check | Before | After | Target |
  |---|---|---|---|
  | H01 zenith | #7D9DB7, C 0.052, ΔE 0.062 | #66A6D0, C 0.090, ΔE 0.029 | `sky_zenith_noon` +1 #6DAFDC, ≤ 0.045 |
  | H04 zenith | #84A3B7, C 0.045, ΔE 0.057 | #85B5D0, C 0.064, ΔE 0.038 | as above |
  | H07 zenith | #81A1B6, ΔE 0.059 | #80B2D0, ΔE 0.029 | as above |
  | Lit tops L p95 (H01 / H04) | 0.837 / 0.836 | 0.904 / 0.899 | `cumulus_lit` +1 L 0.905 |
  | Undersides C, h (H01 / H04) | 0.021, 267° / 0.013, 256° (grey) | 0.031, 240° / 0.028, 230° | `cumulus_shadow` +1 C 0.025, h 248° |
  | Cloud grain (median 2nd difference, H01 / H04) | 0.0039 / 0.0040 | 0.0019 / 0.0028 | ≤ 0.0033 |
  | H07 chapel sun face | #B1B1AE, ΔE 0.043, grain 0.0116 | #BABCBC, ΔE 0.013, grain 0.0032 | `order_marble` 0 #C1BEB9 |
  | H07 banyan roots (shaded) | #181E1E, L 0.23 | #385259, L 0.42 | above the toe, ≥ 0.33 |
  | H04 planks | #B8A28E, ΔE 0.064 | #9D846D, ΔE 0.033 | `timber_weathered` +1 #A48F78 |
  | Red, HSV mask (H02 / H03) | 4.2% / 16.4% | 4.3% / 5.2% | ≤ 8% |
- **What changed, and why each baseline was re-approved** (each frame inspected before and after):
  - **All five, sky + fog (B1, S1):** `env_sky_cumulus` reworked. The old per-pixel white-noise march
    jitter was turned into 2×2 stipple by the half-res pass, so the march is now adaptive: coarse steps,
    then quarter steps at the first density, so no step adds about 40% opacity. That removes both the grain
    and the contour rings a fixed offset gave. The coverage field is 3 octaves (finer 2D detail extruded up
    the dome walls as the vertical streaks), with coarser 3D billows that fade with distance. Light that
    crossed cloud is tinted to `cumulus_shadow`, so the undersides stay blue. `background_energy` 1.5
    lifts only the visible sky; fill and water reflection are unchanged. Both fogs are cut, and the
    volumetric fog had been hazing the sky. Drift is expected everywhere the sky or the haze showed.
  - **H01:** re-staged to 120 m offshore at 8 m (proposed in haluna.md Revisions; needs AD sign-off). The
    nearshore shelf varies along the shore (`shelf_variation` 0.8 over 45 m), so the wash band changes width
    instead of reading as one stripe. The M1-ENV-04 shrine sits behind the palms and doesn't read, so it
    was not moved.
  - **H02:** sky and fog only, plus darker weathered timber (all timber now has a `col_tint` and per-board
    variation).
  - **H03:** camera 0.3 m lower, tilted up about 4°. The near roof is now a strip and the red budget passes.
  - **H04:** weathered planks. The net rack is turned square to the lens; it had been seen exactly edge-on.
    The net is alpha scissor, not blend: blended, it wrote no depth and the transparent sea drew over it,
    which is why the nets were invisible. The twine is thicker and tannin-brown (`timber_weathered`).
    "Backlit" is proposed for removal from H04's brief.
  - **H07:** the lime-wash is at the albedo ceiling #EBE7DF, fully covering a smooth base (no coral
    stipple). The banyan bark has a gain above 1 over the shared frangipani texture (linear ≈0.26), giving
    a pale grey bark at about 0.40 linear, with occlusion 0.9 → 0.35.
- **Ready for review (Rendering + Art Director).** `HYMN_SHOTS=<the five haluna_h0* shots> tools/ci_local.sh`
  passed all gates: tools tests, 847 Godot tests with 0 failed, coverage, boot, and 5/5 screenshots against
  the re-approved baselines. AD sign-off is needed on the two haluna.md Revisions proposals (the H01
  re-stage, and dropping "backlit" from H04).
- Sky users in the manifest: only the five `haluna_h0*` shots (`haluna_kit_sheet.tscn` also uses the
  environment but isn't a registered shot).

## Review log
- 2026-10-23 art director (review-sweep-F, first AD review): **request-changes.** I read all five baselines (`tests/screenshots/baselines/haluna_h0{1,2,3,4,7}_*.png`, ids in tests/screenshots/shots.json:408-456) against haluna.md §0 and §5.1, color_script (conventions, water looks, `ch02_noon`), palette.json `onscreen_hex`, ADR 0014, the zone README, haluna_mood_review.md, and haluna_noon_environment.tres. I sampled region means in Oklab (ΔE_ok).
  - **What passes:**
    - **Composition** broadly follows haluna.md:163-169. In H03 the gull fills about 41% of the frame height and faces the sea. H04's leading lines run to the shrine roof on the left third. H07's door is the only hard rectangle.
    - **Exposure per ADR 0014.** `tonemap_exposure` 0.65, key 3.2 and sky fill 0.65 (.tres:17, :20; haluna_mood.tscn:79) give k = 2.1. Sunlit horizontals read at the +1 column: H02's lane is #D9CCBB (0.031 to `sand_dry` +1), H04's sand is 0.046, and H03's roof is #D37E63 (0.008 to `roof_clay` +1). Nothing clips (the brightest pixel is 233), there is no pure black (the darkest is #03161B), and auto-exposure is off.
    - **Water** is `lagoon_clear` ×1.5 with `col_deep` #0E4A55 (haluna_water_material.tres:9-12). H01's near water is #63A5A7 (0.042 to `lagoon_teal` 0), and H04's mid shallows are #7FC4C3 (0.040 to `turquoise_shallow` 0). Both are inside the 0.07 band.
    - **Shade:** shaded sand in H07 is hue about 183°, inside haluna.md:208's 170-200°.
  - **Blocker B1: the sky.** It fills 45-55% of H01 and H04 and misses the palette.
    - The zenith reads #7D9CB7-#8AA6B9 (Oklab chroma 0.041-0.053), against `sky_zenith_noon` +1 #6DAFDC (C 0.094). That is half the chroma: ΔE_ok 0.056-0.063 to +1 and 0.09-0.125 to 0.
    - Lit cumulus reads #B6B7B6-#C3C2C0 (L 0.78-0.81), against `cumulus_lit` +1 #E1DFDD (L 0.90).
    - The undersides are neutral grey (#A6AAAC, C 0.005), against `cumulus_shadow` "never grey, always blue-lilac" (palette.json:327; C 0.025-0.032).
    - The cumulus also shows vertical march banding and grain (H01's top half, all of H04's sky).

    The Act I reference grade reads hazy and pale, which flattens the colour script's Act I-to-Act II arc. AC 2 ("matching the Act I color script frame", :17) is over-claimed while this stands. Fix it one of two ways. Either fix `env_sky_cumulus` (zenith chroma, lit-top value, lilac underside, banding) and re-approve the five baselines. Or, with the Lead's OK, re-scope AC 2 to "ground, water, light and composition match; the sky is waived" and open the Rendering task it is waived to. No M1 task owns the sky; it is only a note at :28. Then mark the baselines provisional in the README.
  - **Should-fix S1 (haze).** The volumetric fog (density 0.003, near-white albedo, 96 m) and the depth fog (0.00035, aerial perspective 0.7) at haluna_noon_environment.tres:34-42 are not in the `ch02_noon` row (haluna.md:23). They are part of why H01 is flat (luminance p1 99, p99 209) and why the far water goes grey: #93A8AC (C 0.024) at H04's horizon and #7FA0A6 in H01's mid water. Record the fog in the frame row, or cut it.
  - **Should-fix S2 (the chapel doesn't read white).** H07's sun-side face is #A0A5A6 (L 0.72, cool), and the long face is #547281 (L 0.54, blue). The target is `order_marble` 0, #C1BEB9 (L 0.80). Under a 74° sun the walls take N·L of about 0.28. README:38 ("the chapel reads white") is optimistic, and the brief's "small foreign whiteness" (haluna.md §1.1) depends on it. Re-aim H07 so the door face takes more sun, or raise the lime-wash albedo within `order_marble`. Also remove the stipple grain visible on its walls.
  - **Should-fix S3 (red budget).** Red is about 16% of H03 against haluna.md:206's "red ≤ 8%" (my estimate is an HSV mask, hue < 25° or > 340° and saturation > 0.35, because the swatch-mask view doesn't exist yet). H02 is about 4%. Reframe H03 so the roof is the lower quarter, or record a close-up exception in haluna.md.
  - **Should-fix S4 (value).** H07's banyan aerial roots read as near-black poles, the darkest shapes in the frame. That works against the value check (haluna.md:205: darks in one or two shapes). It's a placeholder, but it still needs a value pass.
  - **Should-fix S5 (H01).** The surf band across the full width (y about 355-380, #B7BDB9, C 0.009) reads as a flat milky stripe. The tide-wall's white curve (haluna.md:163) doesn't read, and the village is a dotted line. I'd accept a re-staged H01 (for example, about 120 m offshore at 8 m). Propose it in haluna.md, and the Art Director signs it off.
  - **Should-fix S6 (H04).** The planks are #B9A492, new and warm (0.070 to `timber_weathered` +1). The nets are invisible. I agree "drying nets backlit" can't happen at noon: drop "backlit" from H04 (haluna.md:166) with AD sign-off, and make the nets read opaque.
  - **Process.** The front matter names `reviewer: rendering` (:6), but Art also has to sign this off (SPEC §8.4 mood frames). Record both reviewers.
  - **Nit.** A shadow sample right of H02's wall (about x 820-860, y 440-470) reads hue about 126°, a green-grey. It may be the tuft. Re-check it with the swatch-mask view when it exists (haluna.md:208).
  - **GI.** SDFGI off for the frames, with a GPU re-test requested (README "GI choice"), is reasonable and documented. It's not a review item.
- 2026-10-23 lead: reopened on review-sweep-F request-changes. The sky blocker is fixed here; no waiver. Reviewers are Rendering and Art.
- 2026-10-23 art director (review-sweep-G, re-review after sweep F): **approve (Art), with should-fixes.** Rendering has not yet logged a re-review of the rework, so the task stays in `review` until it does.
  - **What I read:** the five baselines (`tests/screenshots/baselines/haluna_h0{1,2,3,4,7}_*.png`), against palette.json `onscreen_hex`, color_script (conventions, rule 3, `lagoon_clear`), haluna.md §0, §5.1, §6 and Revisions, `tools/screenshots/palette_check.py`, `tests/screenshots/palette_checks.json`, `tools/tests/test_palette_check.py` and haluna_noon_environment.tres. `palette_check.py check` gives 19 ok and 0 failed. `validate_data.py` gives 0 errors and 0 warnings, and `unittest discover -s tools/tests` gives 322 OK.
  - **Sweep-F items:**
    - **B1 (sky) is resolved in the pictures.** The H01 and H07 zeniths sit on `sky_zenith_noon` +1 (ΔE_ok 0.029, C 0.090). The lit tops read at `cumulus_lit` +1 (L p95 0.90). The undersides read blue-grey by eye, the grain is gone, and the Act I grade is clear rather than hazy.
    - **S1 (haze):** cut. That is the right call, since the `ch02_noon` row never asked for fog (haluna.md:218 (3)).
    - **S2 (chapel):** reads white (#BABCBC, ΔE 0.013 to `order_marble` 0), and the stipple is gone.
    - **S3 (red):** 5.2% in H03 and 4.3% in H02.
    - **S4 (banyan roots):** they are now pale grey (L 0.42), not near-black poles.
    - **S5 (H01):** partly resolved; see the decision below.
    - **S6 (H04):** the planks are on `timber_weathered` +1 (ΔE 0.033), and the nets are visible.
  - **Art Director decisions on the haluna.md Revisions proposals (haluna.md:218):**
    1. **H01 re-staged to 120 m offshore at 8 m: APPROVED** as the shot's camera, with the horizon at about 0.36 of frame height. Environment should write the new numbers into the §5.1 H01 row (haluna.md:163 still says 180 m at 6 m) and mark the Revisions entry approved.
       - The brief text stays. "The tide-wall reads as one white curved line" and "a beach crescent" are still unmet, because the beach is a straight white band across the frame and the roofs are still a dotted line behind the palm trunks (S5 below).
       - For the Cutscene A close under `ch02` dawn, check that the three walking figures still read at 120 m (about 8 px tall at 24 mm).
    2. **H04 drops "backlit": APPROVED.** At 12:30 the sun is 74° up behind the camera, so backlit nets are impossible. Replace the phrase with "drying nets, dark tannin mesh, against the shallows" in haluna.md:166.
  - **The palette checker: targets and value as a CI check.**
    - The `near_swatch` targets are the palette's. They read palette.json `onscreen_hex` live by swatch name (palette_check.py:123-131), so a palette edit flows through.
    - The red budget is haluna.md §6's 8%.
    - The bounds (zenith C minima, grain maxima, root L) are bespoke, not palette values.
    - It is a meaningful gate, but a narrow one. test_palette_check.py:84-86 runs the checks on the committed baselines in every tools test run, so a re-approval that drifts off the palette fails, and the screenshot diff ties renders to those baselines. It is not wired to fresh renders, and it doesn't need to be.
  - **Should-fix:**
    - **S1 (check validity). The "undersides" checks mostly measure sky.** These are palette_checks.json:11-16 and :26-31. Of the selected pixels, 51% (H01) and 57% (H04) are nearest `sky_horizon_noon`, and only 19% and 11% are nearest `cumulus_shadow`. The L 0.6-0.8, C ≤ 0.045 window contains `sky_horizon_noon` 0 and -1 (L 0.675-0.786, C 0.029-0.035, h 222°).
      - Consequence: a grey underside could pass on horizon sky, and H04's 230° median is 18° off the swatch's 248°, toward cyan.
      - Fix: select the cloud bodies themselves (rects inside the cloud, or require ΔE_ok to `cumulus_shadow` below a bound), and tighten the hue window to about 235-265°.
    - **S2 (check validity). A filtered selection can pass on a small minority of its rect.** The default `min_fraction` is 0.02 (palette_check.py:251). The zenith checks (palette_checks.json:5-8, :20-23, :37) filter `C_min 0.03`, so a mostly grey sky is filtered away rather than failed. Set `min_fraction` to about 0.9 on the zenith checks; today they cover 1.00 of the rect.
    - **S3 (H04 "zenith").** palette_checks.json:20-23 samples the top of a 28 mm frame at 1.2 m, about 20° up, not the zenith. Its C minimum of 0.06 sits just under the measured 0.064, against the swatch's 0.094. Rename it "upper sky" and target a zenith-to-horizon interpolation, or record why it is looser than H01's 0.075.
    - **S4 (coverage). Add the haluna.md §6 checklist items the tool can already measure:**
      - shaded-sand hue 170-200° in H07;
      - gold ≤ 5% by swatch mask in H07 (the door and finial);
      - the water and sand ΔE values sweep F passed (H01 near water against `lagoon_teal` 0, H04 shallows against `turquoise_shallow` 0, H02 lane against `sand_dry` +1).

      As it stands, a regression in those parts of the frame would go uncaught.
    - **S5 (H01 dressing).** Curve the beach and tide-wall into a crescent, and thin or stagger the front palms so the roofs read as a band (haluna.md:163). This is not a blocker for the M1 mood test.
    - **S6 (H04 dressing).** The nets read as a taut chain-link fence panel. Give them drape and sag between the rack posts. The brief's outriggers and seagrass patches (haluna.md:166) are absent: the dock now leads to the marker posts.
    - **S7 (sky artefacts).** Detached cloud specks at H01 about (675, 127) and H07 about (306, 93) read as floating dots. Suppress blobs below a size threshold in `env_sky_cumulus`.
    - **S8 (record).** `background_energy` 1.5 (haluna_noon_environment.tres:8) lifts the visible sky but not the reflection or fill, so the water now reflects a sky at 1/1.5 of what is seen. Record this as a deliberate per-zone exception in the zone README and color_script, so other zones don't copy it without re-validating their water looks.
  - **Nit.** In H07 the two window slits are also hard rectangles; the brief (haluna.md:169) wants the door to be the only one. Soften them, or accept and amend the brief.
- 2026-10-23 rendering (review-sweep-H, fresh reviewer; the Rendering sign-off after the AD's sweep-G approve): **approve-with-fixes (Rendering).** With the AD's approval, both reviewers have now signed, and the task can move to `done` once the Lead records it.
  - **What I read:** env_sky_cumulus.gdshader (all of it; f322c44), haluna_noon_environment.tres, kit_net.tres with materials.py:140-143, the water reflection path in water_surface_body.gdshaderinc (:443-526), project.godot AA, graphics_settings.md, the zone README "Sky and palette checks", palette_check.py and palette_checks.json, and the H01 and H04 baselines.
  - **Checks run:** `palette_check.py check` gives 19 ok and 0 failed. The tools tests give 329 OK. `validate_data` gives 0/0.
  - **Signed off:**
    - **Fog removal.** It is correct for the `ch02_noon` row. It also drops the volumetric-fog cost from this zone. The clouds' own distance haze (:184-185) stays as the only aerial perspective, which is enough at this range.
    - **Visible-sky-only brightness.** `background_energy` is applied only when `!AT_CUBEMAP_PASS` (:214). So the radiance cubemap behind the sky ambient (`ambient_light_source` 3) and the water's engine reflection (`SPECULAR`, water_surface_body:523) keep `sky_energy` 1.0, as the README says. The water's SSR only hits geometry, never the sky, so no on-screen sky at 1.5× leaks into the reflection and causes a seam. The radiance fill and the reflection are consistent with each other.
    - **March jitter.** The fixed half-step start (:135) and the adaptive coarse-to-fine refine (:136-181) are deterministic. The half-res pass turned per-pixel jitter into stipple, so dropping it was right, and captures run without TAA. The baselines show no rings or grain (grain 0.0019 and 0.0028).
    - **2D detail stretch.** Limiting the height field to 3 octaves (:80-83) removes the vertical streaks. The extruded-column look remains (H01's left tower has smooth vertical walls), but it belongs to the model and is the signature sky's problem, not this one's.
    - **Net alpha scissor.** Scissor is the right fix. A blended net sat in the transparent pass with the water, which reads the screen texture, so the sort dropped the net. In the opaque pass it writes depth and is refracted correctly where it dips under the surface. `cull_mode` disabled is fine, because the engine flips back-face normals. The discard costs early-Z on one small mesh only.
  - **Should-fix (route to the Rendering sky task that the shader header asks for; none of these block the M1 mood test):**
    - **R1 (performance; the main trap).** The sky has no quality tiers, and it runs a full ALU march every frame.
      - The march is up to `cloud_steps * 3` = 192 iterations (:138). Each lit sample makes three `cloud_density_at` calls (:143, :158): about 3 fbm2 octaves plus 4 octaves of PCG-hashed fbm3, or roughly 40 hashes per call.
      - That runs at half resolution every frame, and again for the radiance cubemap whenever the sky is dirty.
      - My estimate is several ms of GPU on the minimum tier (GTX 1060 at 1080p). The sky isn't in graphics_settings.md's budget table, and `HYMN_QUALITY` isn't set for this shader.
      - Fixes:
        - per-preset `cloud_steps` (about 24 on low);
        - `detail = 0.0` for the two light samples at :158, since shadows don't need billows;
        - a cheaper cubemap march (fewer steps under `AT_CUBEMAP_PASS`);
        - eventually a baked, tool-generated 3D noise texture in place of the hashed fbm3;
        - a row in the budget table.
    - **R2 (radiance re-render trap).** The shader reads `LIGHT0_*`, and the header invites drifting `cloud_offset_m`. With `process_mode` automatic, any per-frame change of the sun or the offset re-renders the 6-face radiance cubemap with the full cloud march and the high-quality filter. That is a hitch every frame. If time-of-day or drift is ever animated, use `PROCESS_MODE_REALTIME` with a small `radiance_size`, or keep `clouds()` out of the cubemap pass.
    - **R3 (iteration budget).** On grazing rays the coarse-to-fine re-entries can use up the 192-iteration cap before `t1`. The far clouds are then cut short without any signal, and how far depends on `cloud_steps`. Finish the remainder coarse when the budget runs out, or count only fine steps against it.
    - **R4 (compositing).** `light` is already premultiplied: it accumulates `trans * a * c` (:171). `mix(c, cl.rgb, cl.a)` at :214 multiplies it by alpha a second time, so thin edges and hazed far clouds are darkened quadratically. The look was tuned around this, so fix it together with a retune: `c * (1 - a) + light * haze_fade`.
    - **R5 (record, the AD's S8, half done).** The zone README records `background_energy` 1.5 (README:63). color_script and water.md do not yet say that the visible sky sits 1.5× over its reflection in this zone. Another zone copying the value would put a value step between the horizon sky and the grazing-angle sea. For the signature sky, move the lift into `sky_energy` and re-validate `lagoon_clear`, rather than keep a split.
    - **R6 (net at distance).** With a threshold of 0.4 over twine of about 0.56 coverage, the far mips go solid (materials.py:141 says so on purpose). At range the net becomes an opaque tannin sheet, which is part of the "fence panel" read the AD noted. The project runs TAA (project.godot:71), so alpha hash (`transparency` 3) is the better long-term mode for thin cutouts.
  - **palette_check flaws from sweep G: do they matter? I probed both with mutated copies of the baselines (scratch, not committed).**
    - **Zenith `min_fraction`: yes, it matters.** I greyed 90% of H01's zenith rect to C 0.01 and left 10% blue. Both zenith checks still pass ("0.10 of rect", C_median 0.090). The default 0.02 (palette_check.py:251) lets the gate pass the very defect it guards. Set `min_fraction` to about 0.9 on the zenith checks. It's a one-line change per check, and today's coverage is 1.00.
    - **Underside sampling: it matters less than feared for chroma, and fully for hue.** I greyed every pixel within ΔE 0.05 of `cumulus_shadow`, and then only every other one. The chroma check fails in both shots both times (C_median 0.005-0.012), so a grey underside is caught. The hue check passes every time (219-258°), because it is measured mostly on horizon sky and on near-grey pixels whose hue is noise. So a cyan drift in the undersides would go uncaught. Apply the AD's sweep-G S1 fix (select by ΔE to `cumulus_shadow`, hue 235-265°) with the sky task. It doesn't block this task.
  - **Nit.** The cloud deck ends at elevation 0.86° (`t0 > cloud_max_distance_m`, :120) while the haze still leaves about 60% alpha. That produces the thin clear band above H04's horizon. It reads as haze today, but at a wider lens or a lower horizon it could read as a cut. Fade alpha to 0 before `cloud_max_distance_m`.
- 2026-10-23 lead: closing: Art Director approved (sweep G), Rendering approved with fixes (sweep H). The sky perf and quality follow-ups are in M1-RND-12.
