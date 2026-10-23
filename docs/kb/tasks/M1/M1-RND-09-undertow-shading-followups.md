---
id: M1-RND-09
title: Undertow placement and character-shader contract fixes
role: rendering
status: done
reviewer: environment
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-09-undertow-shading)
depends_on: [M1-RND-03, M1-RND-04]
milestone: M1
request-from: "environment"
---
## Goal
Review-sweep-C should-fix items on RND-03/RND-04 that are M1-sized.

## Acceptance criteria
- [x] Undertow: explicit sea_level property decoupled from the node's Y; doc example fixed
- [x] UndertowStorm is @tool (visible in editor)
- [x] undertow_eye baseline: no visible test-set edge
- [x] A daytime storm shot that reads as the bible's 'wall of dark water and cloud' (Ch1/Ch8), not a khaki cumulonimbus or sandstorm
- [x] Cloth band-id texture uses nearest filtering and no mip-bleed; the contract states the exception
- [x] Contract: wind weights as float colour attributes (no sRGB byte quantisation); uniform head texel density plus a pore tiling formula

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

## Notes (author, PC GPU session, 2026-10-23)
All six criteria done; report with GPU before/after, look metrics and the lavapipe drift list: docs/kb/qa/gpu/2026-10-23-rnd-09.md. New shot undertow_day_ch08 waits in docs/kb/qa/gpu/2026-10-23-rnd-09-pending-shots.json for a lavapipe baseline (Lead). Band-id import mips: request M1-CHR-03 (Character owns the asset). Reviewer (Environment raised these in review-sweep-C): judge the day shot against bible §9 and the Eye framing.

## Review log

- 2026-10-23 environment (review-sweep-G): **approve-with-fixes**.
  - **sea_level.** `sea_level()` comes from the water's rest plane or `sea_level_y` and ignores the node's Y, and it is tested.
  - **@tool.** The preview runs at `editor_preview_quality` (Low) with the clock stopped. Built nodes are added `INTERNAL_MODE_FRONT`, so they are never saved, and the editor guards hold in undertow_storm.gd.
  - **Cloth band-id.** The nearest-filter fix and the contract text are in place. Mips are requested in M1-CHR-03, as reported.
  - **Character contract.** The wind-weight attribute (`FLOAT_COLOR`/`POINT`) and the `detail_tiling` = mm ÷ 27.5 formula are clear.
  - **Looks.** The look values are data (undertow.json `looks.day_storm`), and `test_every_look_drives_body_uniforms` covers them.
  - **Tests and gates.** undertow 28, character_shad 11, 0 failed. The python gates pass.
  - **Judging `undertow_day_ch08`.** I rendered it on lavapipe from the pending manifest, twice, and the two runs are bit-identical (RMSE 0), so it is ready for a baseline. Against bible §175, "a wall of dark water and cloud lit from within by glimmer":
    - **Meets:** it is no longer khaki, cumulonimbus-gold or a sandstorm. A slate-black mass spans about 80% of the frame width, with cyan rents bleeding light, and the Ch8 slate sky and fog are right. This closes the review-sweep-C art-direction should-fix for M1.
    - **Misses, for M2-RND-01 (not an M1 blocker): the "dark water" half.** The wall's base sits on a flat, calm horizon line, with no spray curtain or lifted water joining sea and cloud. The sea in front shows no influence from the storm at 14 km (no swell, no darkening toward it). The two flank masses read as separate cumulus beside the main body rather than one wall. Please record these in undertow.md under M2 look work.
  - S1: in the lavapipe capture the wound glow shows a hard diagonal ordered-dither stipple (a 4× crop of the upper-left rent shows it clearly). With 6 settle frames and FXAA nothing integrates it, so the baseline will encode it, and future look reviews of this shot will see grain that in-game TAA removes. Either raise `settle_frames` for this shot or note it in the shot's manifest entry.
  - Nit: the Ch1 (10:30, clear sky into storm) daylight shot named in the AC alongside Ch8 is not made. Ch8 alone satisfies "Ch1/Ch8", but Ch1 is the player's first sight of the storm. Consider it for M2.
  - Nit: the mood tunables live in an exported dictionary in undertow_test_rig.gd (fog_density 6e-5 and the rest). That is a test rig, it follows the existing dusk/eye/night entries, and I accept it.
- 2026-10-23 lead: closing on review-sweep-G approve-with-fixes; the dither and the 'dark water' half of the day look go to M2-RND-01.
