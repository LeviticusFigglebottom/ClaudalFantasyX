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
- [~] Body at half/quarter resolution with temporal reprojection; baked 3D noise textures instead of hash noise; <= 2-3 ms estimated on the recommended tier. Half-res done (High 4.94 → 2.27 ms), baked noise done (M1-RND-10), compute-pass occlusion inside the volume done (ADR 0027; High Day 2.45 ms). **Open:** the compute body's own reprojected history, and a quarter-res tier for min-spec (RTX 3060 projection ~7.4 ms).
- [x] Billow surface detail and multiple scattering (no uniform khaki lit tone, less regular striations). Multiple scattering: 3 octaves, free. Billows: fringe billows with sun-ward shading. Striations: noise-warped helix. See undertow.md, "Striations, billows and the wound skin".
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

## WIP handoff (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-23): branch `gpu/m2-rnd-01-undertow`
The branch isn't merged. It has the integration branch merged in (a504072, `claude/undertow-lead-handoff-423ixt`).
The `undertow` tests pass (35/0).
- **Done on the branch:**
  - The sweep-G ch08 wall foot.
  - The half-res body.
  - 3-octave multiple scattering.
  - **This session:**
    - Noise-warped striations.
    - Fringe billows with sun-ward shading.
    - The sea wind streaks: meander, flecks and a soft profile (sweep defect 1).
    - The rents' stipple (sweep defect 2): wound-skin step refinement on a fractional step budget. The cause was
      skin undersampling that FSR2 doesn't average, not the half-res tent.
  - Report: `docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md`, last section.
- **Cost, High 1440p:** Day 2.56 ms, Eye 3.11 ms. Within the 6 ms cap here, but about 7.7 and 9.3 ms projected on an
  RTX 3060. **AT RISK** for min-spec High.
- **Drift:** all five Undertow shots (table in the report). The Lead re-approves them on lavapipe.
- **Compute body done** on `gpu/m2-rnd-01b-undertow-compute`, cut from this branch: ADR 0027 (proposed);
  report section "Compute body". The pillar test passes. Cost: Day 2.45 ms, Eye 2.84 ms. Merge
  `gpu/m2-rnd-01-undertow` first, then this branch (it contains it).
- **Exact next step (was: compute-pass occlusion, now done):** min-spec cost on the compute body.
  - Try `body_scale` 0.33–0.25 on High, with the compute pass's own history (reproject last frame's body by its
    front distance), so a quarter-res march holds up under FSR2.
  - Then put the compute pipeline on the prewarm list (with M1-RND-22).
- **After that:**
  - Torn rents and mote streamers.
  - Storm in the sky, in reflections and rain.
  - Lightning bolts and the exposure flash.
  - Per-chapter presets.
- **Known residue:** a faint stipple on two small seams on the right of `undertow_day_ch08` (High, FSR2).

## Review log
