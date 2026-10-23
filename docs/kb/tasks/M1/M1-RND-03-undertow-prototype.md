---
id: M1-RND-03
title: Undertow storm prototype
role: rendering
status: done
owner_session: rendering-stream-5
reviewer: environment
depends_on: [M1-RND-01]
milestone: M1
request-from: ""
---
## Goal
SPEC §8.2 item 9, the most important visual. A prototype is due in M1 (ahead of M2).

## Acceptance criteria
- [x] Colossal volumetric or layered vortex at sea scale: a hybrid. A raymarched body (Medium+) and lathe shells on the same envelope (Low), plus a maelstrom sea funnel, spray, and a depth-only lid that keeps the zone ocean out of the funnel
- [x] Glimmer wounds: `spawn_wound` rents in the eyewall's skins, sliding down; `glimmer_held` pockets, throat streaks and a held `GlimmerField`
- [x] Two composed shots: on the horizon (`undertow_horizon_dusk`) and high-angle into the eye (`undertow_eye`), plus `undertow_night` and `undertow_horizon_low` (the Low tier)

## Notes
- Docs: `docs/kb/tech/undertow.md` (approach, API, tunables, tiers, measured costs, assessment, M2 list).
- **Cost:** the raymarched tiers are an estimated 5–15× over a storm shot's frame budget on target GPUs (Low fits). This is M2's first job: half or quarter resolution plus temporal reprojection, and baked 3D noise.
- Requests for other roles (not edited here):
  - **Art:** confirm `spawn_wound` for the Undertow's rents (palette.json says "creature weak points only").
  - **Water (M1-RND-01):** (1) NaN at the anti-solar pixel, which glow blooms into a white disc. Seen with the sun 5° up behind the camera (az 262°, camera facing 90°). Likely a `normalize(L + V)` half vector. (2) SSS paints saturated green bands across open sea with a low sun behind the camera. The test scene works around both (sun azimuth 212°, `use_sss = false`).
- Baselines add about 1.7 MB (three 960×540 shots at 450–550 KB, because the raymarch dither compresses poorly, and one 480×270). The folder is now about 8.7 MB, against ADR 0005's 5 MB guidance, so QA or the Lead may want to drop `undertow_night` or halve it.

## Review log
- 2026-10-23 environment (review-sweep-C): **approve with fixes**. This is a credible M1 prototype of the look, and the API is enough to place the storm and tween it (`approach_distance_m`, clock pause/scrub, `force_flash`). I re-ran all 659 tests (0 failed; undertow suites included) and checked the cost arithmetic. The look still misses the bible's "wall of dark water", and the only shots are dusk and night, while the story's storm appearances are mostly day. Cost honesty is credible: 4730 ms over 233k covered px is about 20 µs/px, and 5418 ms over 440k px is about 12 µs/px. An independent op count (75k ops × 0.98M px ≈ 74 GFLOP, about 6 ms at 100% of a 3060's peak, so 12–20 ms at realistic utilisation) lands inside the stated 16–33 ms.
  - should-fix: `docs/kb/tech/undertow.md:63` and `game/vfx/undertow/undertow_storm.gd:141-143`. Sea level is the node's Y (`storm_center()` keeps `origin.y`), but the doc example places the node at `village_marker.position`. A marker on a 12 m headland puts the funnel, lid and spray 12 m above the zone ocean, and the lid then clears the ocean over a raised disc. Fix: take sea level from `water.global_position.y` when `water` is set, or document "the node's Y is sea level" next to the example.
  - should-fix: `undertow_storm.gd` (no `@tool`). The storm builds only at runtime, so an environment artist placing it in a zone scene sees nothing in the editor: no silhouette, no footprint, and no check that floors keep out of the funnel (Gotchas, undertow.md:196). Fix: a `@tool` gizmo (footprint circles plus an eye marker, and the Low shells in-editor), even with the raymarch off.
  - should-fix: baseline `undertow_eye.png`. From 20 km up the zone ocean ends inside the frame, so a grey slab (the −200 m floor) with hard diagonal edges against a navy void fills the lower left and right. The image reads as a test set, not as the Kite's view. Fix: extend the ocean or the floor past the frustum for this camera (or fog the far field), then re-approve.
  - should-fix (art direction): the colour script has no Undertow frame at dusk. Its story appearances are Ch1 (10:30–11:10, clear sky into storm, `lut_ch01_storm` slate) and Ch8 (16:00 to near-night, slate sky, 2× lightning flashes), and neither is shot. The dusk body reads as a khaki-gold cumulonimbus or mushroom cloud, and in the eye shot as a sandstorm. It does not read as bible §9's "wall of dark water and cloud lit from within". Fix: add a `ch01`/`ch08` daylight mood shot and darken and cool the albedo toward `storm_slate` for daylight before M2 tunes the surface.
  - nit: `undertow_storm.gd:62`. `quality` is a plain export, so `storm.quality = "low"` after `_ready` silently does nothing. Give it a setter that calls `set_quality`. Likewise, `water`/`motes` assigned after `add_child` don't update the lid height or the mote priority until `refresh()`. Document that, or add setters.
  - nit: undertow.md:162-164. "Low fits" is borderline: the 1.5–3 ms estimate is the whole 2–3 ms storm budget. Low is alpha-hash shells plus spray, so it is overdraw/bandwidth-bound, and scaling it by ALU ratio onto a GTX 1060 is the weakest estimate in the table. Say "Low is at the budget; measure first".
  - nit: the baselines folder is now 11 MB against ADR 0005's 5 MB guidance (the author flagged 8.7 MB). Lead/QA decision.
- 2026-10-23 lead: closing on review-sweep-C approve-with-fixes; follow-ups in M1-RND-09 (M1-sized) and M2-RND-01 (production).
