---
id: M1-RND-03
title: Undertow storm prototype
role: rendering
status: review
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
