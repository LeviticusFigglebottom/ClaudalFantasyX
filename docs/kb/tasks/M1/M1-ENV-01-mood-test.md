---
id: M1-ENV-01
title: Five-shot environment mood test (coastal village)
role: environment
status: doing
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
