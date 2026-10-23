---
id: M2-RND-01
title: Undertow storm to production cost and quality
role: rendering
status: doing
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU, branch gpu/m2-rnd-01-undertow; resumed from the WIP handoff)"
depends_on: [M1-RND-03]
milestone: M2
request-from: ""
---
## Goal
The M1 prototype reads (horizon and eye shots) but its raymarched tiers are an estimated 5-15× over a storm shot's 2-3 ms GPU budget, and the agent self-assesses it at about a third of the bar for "the most important visual" (SPEC §8.2.9). See docs/kb/tech/undertow.md.

## Acceptance criteria
- [~] Body at half/quarter resolution with temporal reprojection (half-res done: High 4.94 → 2.27 ms; baked noise done in M1-RND-10; compute-pass occlusion inside the volume is the remaining step); baked 3D noise textures instead of hash noise; <= 2-3 ms estimated on the recommended tier
- [~] Billow surface detail and multiple scattering (multiple scattering done: 3 octaves, free; billow surface detail and striation regularity still open) (no uniform khaki lit tone, less regular striations)
- [ ] Wounds as real torn rents; storm-scale mote streamers
- [ ] Storm in sky and reflections, shadowing the zone, rain
- [ ] Lightning bolts plus exposure flash
- [ ] Per-chapter presets, including the Ch21 turn to rising gold
- [ ] Art confirms spawn_wound usage for storm rents (palette.json currently limits it to creature weak points)

## Notes
Needs a real GPU for final cost; the CPU-render ratios are the guide until then.

## Notes (PC GPU session, start, branch gpu/m2-rnd-01-undertow)
I started with the review-sweep-G findings on `undertow_day_ch08` (the dark-water half of the bible's wall). Report
with costs, looks and drift: `docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md`.
- **Base.** A skirt of lifted water and spray flares out at the wall's foot (shared envelope, so the Low shells
  follow it). The base is water-dark below 1.4 km, with scud rags below 2.6 km. The outer spray curtain now draws
  over the body, near half only (before, the depth-blind body hid it).
- **Sea.** A new water `storm` group, written by UndertowStorm from undertow.json `sea_response`. The sea darkens
  toward the storm and loses some of its reflected sky; it turns choppier and rougher, with wind streaks along the
  inflow. Without a storm the terms are an exact no-op. The funnel sea dims its reflection to match.
- **Flanks.** `band_join_m` fills the spiral-band troughs near the wall, so the flanks grow out of it.
- **Cost, High 1440p, RX 9070 XT:** Day 4.79 → 4.95 ms, Eye 5.25 → 5.43 ms, Night 5.06, Horizon 4.01. All within
  the 6 ms budget.
- **Drift:** `undertow_horizon_dusk`, `undertow_night`, `undertow_horizon_low` and the pending `undertow_day_ch08`
  (probably `undertow_eye` too). Not overwritten.
- **Status stays doing.** The acceptance list's other items remain: half-res body with reprojection, multiple
  scattering, torn rents and mote streamers, the storm in sky/reflections and rain, lightning bolts, and per-chapter
  presets.

## WIP handoff (PC GPU session, 2026-10-23): branch `gpu/m2-rnd-01-undertow`
The project moved to new sessions mid-item. The branch compiles and the `undertow` tests pass (35/0). It has the
integration branch merged in (d5cbda2) and isn't merged itself yet.
- **Done on the branch:**
  - The sweep-G ch08 wall foot.
  - The half-res body (High 4.94 → 2.27 ms).
  - 3-octave multiple scattering.
  - Reports: `docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md`; design in undertow.md, "Half-resolution body".
- **Two defects seen in a fresh 2× capture** of `undertow_day_ch08` (High, `--hold-storm`), not yet fixed:
  1. The sea's storm wind streaks (`storm_*` water uniforms, `sea_response` in undertow.json) render as hard,
     straight, parallel lines in the foreground. Soften them or noise-break them.
  2. The teal wound glow shows a coarse dot stipple. It may be the half-res composite's tent filter on emissive
     rents. Compare with `half_res_body_scale` 1.0 before changing the filter.
- **Exact next step (billow surface detail and striation regularity), as planned:**
  1. **Striations:** `undertow_striation()` in undertow_common.gdshaderinc is a pure cosine helix. Warp its phase
     with one low-frequency `undertow_noise` sample, in the rotating frame (`striation_warp`, `striation_warp_scale_m`
     in undertow.json `shape`, pushed by undertow_state.gd), and vary its strength along the helix. The shells and the
     sea also include common, with hashed noise; cost it there.
  2. **Billows:** in the body march, where the envelope is thin (the surface), add a billowy `1 - |2d - 1|` term from
     the detail sample cloud_noise already takes. Have `cloud_noise` return it through an `out`. Add a cheap
     sun-ward derivative shading term, `n(p) - n(p + L·eps)` with one extra lattice fetch, only on tiers where
     `octaves > UNDERTOW_LIGHT_OCTAVES`. This aims at sweep-G's "uniform khaki lit tone".
  3. **Validate** each with gpu_bench (High 1440p, the Day and Eye cameras; the budget is 6 ms, and the half-res
     body sits at ~2.3 ms) and capture_preset drift on the five Undertow shots.
- **After that:** compute-pass occlusion inside the volume (a CompositorEffect march with the game view's depth),
  then the other criteria (torn rents and mote streamers, storm in sky/reflections/rain, lightning bolts and
  exposure flash, per-chapter presets). Undertow High 1440p is AT RISK on an RTX 3060 (~3×).

## Review log
