---
id: M2-RND-05
title: "Undertow storm, part 2: torn rents, storm in sky and reflections, rain, lightning, chapter presets"
role: rendering
status: done
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
depends_on: [M2-RND-01]
milestone: M2
request-from: "rendering"
reviewer: environment
---
## Goal
These are M2-RND-01's remaining acceptance criteria, split out (2026-10-24) when its cost and quality half reached
review. The body now has a production cost (High 1440p: about 0.6–0.8 ms of the frame for the storm itself, ~2–2.4
ms projected on an RTX 3060) and exact occlusion (ADR 0028). What's left is the storm as an event, plus its
chapter looks. Design and state: docs/kb/tech/undertow.md; history: M2-RND-01 and
`docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md`.

## Acceptance criteria
- [x] Wounds as real torn rents; storm-scale mote streamers
- [x] The storm in the sky and in reflections, shadowing the zone, rain
- [x] Lightning bolts plus an exposure flash
- [x] Per-chapter presets, including the Ch21 turn to rising gold
- [ ] (filed as **M2-ART-03**, Art's to tick) Art confirms spawn_wound usage for the storm's rents (palette.json currently limits it to creature weak points)
- [x] The storm's own GPU cost stays within ~1 ms at High 1440p on the RX 9070 XT (~3 ms projected on an RTX 3060); measure it with `gpu_bench --hide-storms` by difference

## Notes
- Render layer 20 is the half-res body's (UndertowHalfRes.BODY_LAYER). The cutscene key light also uses 20
  (sequencer.json `key_light.layer`); see `docs/kb/qa/gpu/2026-10-24-fp-10-keylight.md`. Settle that before
  any storm cutscene.
- The compute body has no own temporal history. The motion check found TAA/FSR2 reprojection enough at High's
  0.35, but not at 0.25.

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Report: `docs/kb/qa/gpu/2026-10-24-rnd-05-undertow-events.md`. Design: undertow.md "Storm events". Key frames:
`docs/kb/qa/gpu/rnd05/`.
- **Rents.** A dark torn lip and a halo of poured-out light around each seam, on every tier. The seams' and
  throat streaks' drift is now integrated (`wound_drift_m`, `glow_drift_m`); it's identical while held.
- **Streamers.** Curtains of held light hanging from the rents down the outer face to the sea, motes sliding down
  them. 8/12/16/24 per tier.
- **The storm in reflections.** The sea reflects the half-res body's own pixels (Medium, High), wounds and
  lightning included, or an impostor (off screen, Low, Ultra).
  - **The sky:** the storm is in it as geometry. The sky dome's overcast toward the storm is open; it's in the
    report's findings.
- **Zone shadow.** The key light and ambient dim under the canopy, or with the storm toward the sun. The storm
  stays lit by the undimmed key, and both are restored on exit or hide.
- **Rain.** Camera curtains by distance to the eye, dry above the cloud base, with layers by tier and strength.
- **Bolts.** Cloud-to-sea strokes with forks, on the camera's half; `site_facing()` gives a cutscene a site in
  view. The `lightning_struck(site, bolt)` signal is there for thunder.
- **Exposure flash.** 2.0× for 2 frames, at most two a second, gentler under reduced motion.
- **Presets.** Ch1 arrival, Ch8 seawall and landfall, Ch20 interior, Ch21 heart and letting. `unbinding` 0..1 is
  the Letting: the drift reverses, then the hue turns to `glimmer_lift`.
- **Cost.** The storm's own, at High 1440p by `--hide-storms`, is **0.59–0.84 ms** on every camera, against
  0.55–0.76 ms before. Rain is most of the increase.
- **Shots.**
  - All four `undertow_*` baselines drift by design, GPU 0.005–0.022: please re-approve them on lavapipe.
  - Three new pending shots are in `docs/kb/qa/gpu/2026-10-24-rnd-05-pending-shots.json`; each repeats exactly.
  - Haluna is unchanged.
- **Tests.** `tests/unit/test_undertow_events.gd` (11). The `undertow` filter is 51/0, and the full suite
  1386/0.
- **Findings.**
  - Low's full-res shells cost more than High's compute body (1.36 against 0.66 ms on Day).
  - The sky dome doesn't know the storm.
  - Ultra reflects the impostor.

## Review log
- 2026-10-24 review-sweep-R (environment): **approve-with-fixes.** All criteria but M2-ART-03 (Art's) are in. `UndertowEvents`: rents, streamers, bolts, rain, zone shadow, reflection and presets, with `unbinding` reversing the drift and turning to `glimmer_lift`. All the tuning is in `undertow.json`. The bolts are deterministic (`UndertowState.hash01` with salts; there is no RNG). `restore_zone` gives back the sun, ambient, a flash's exposure and the water's reflection. The exposure flash is capped at 0.5 s apart, with a reduced-motion gain, and its `min_interval_s` matches the battle contract. It measures the interval in wall time, which is the right clock for photosensitivity. The storm's cost by `--hide-storms` is 0.59–0.84 ms at High 1440p, inside ~1 ms. The four re-approved and three new undertow shots were viewed on lavapipe (2ab646c). `--filter=undertow`: 51/0. The "layer 20" note is stale: M2-FP-10 moved the key light to layer 19, with a test. **Fixes (M2-RND-11):** literals in `undertow_events.gd` (the 0.6 site-height bias, the golden angle `2.39996323`, `threshold * 0.25`, `0.5 +` reach, `2147483647.0`); and findings 2 and 3 were never filed. Ultra reflects the impostor while High reflects the body, a top-tier quality inversion; the sky dome doesn't know about the storm.
