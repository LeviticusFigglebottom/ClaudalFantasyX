---
id: M2-RND-10
title: "Undertow events: Art's changes from M2-ART-03 (rents, curtains, rain, landfall dark, Letting, per-chapter flash)"
role: rendering
status: review
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
depends_on: [M2-ART-03]
milestone: M2
reviewer: character
request-from: character
---
## Goal
M2-ART-03 approved the Undertow's storm events (M2-RND-05) with changes. Lightning bolts, the sea reflection, the zone-shadow mechanism and the Low tier pass. `spawn_wound` (and `glimmer_held`, `glimmer_lift`) usage is settled in palette.json 0.2.1, so no colour changes. This task makes the changes. The measurements are in M2-ART-03's Review log (Oklab, on the 960×540 frames in `docs/kb/qa/gpu/rnd05/`).

## Acceptance criteria
- [ ] **1. Rents read as torn seams on Medium and High, as they already do on Low.** In `dusk_low` (full-res shells) each rent is a winding slit with a dark lip. In `day_ch08_high` and `night_high` (the 0.35-scale body) the cores spread into soft cyan blotches, the lip is lost, and the halo makes a glowing cloud band. In `eye_high` the rents break into rectangular cyan blocks. Start with: `wounds.width` 0.08 → **0.05**, `lip_dark` 0.8 → **0.9**, `halo_energy` 0.12 → **0.06**. If the half-res body still can't hold a slit, draw the seam cores in a full-resolution pass, or carry them in the composite.
  - **Pass:** in `day_ch08_high` and `night_high` the largest rents read as slits (core aspect ≥ 4:1), with a lip darker than the cloud beside it (lip OkL ≤ 0.8 × the surrounding cloud) on both sides. `eye_high` shows no blocky rents.
- [ ] **2. Curtains read as hanging sheets of light, not ladders or masts.** Now they are narrow rods with a stepped, ladder-like mote pattern (`night_high`). In `letting_ch21` they read as radio masts in silhouette. In `day_ch08_high` they stop well above the sea. Start with: `width_m` 380 → **900** with a soft (Gaussian) edge across the width, `mote_cover` 0.35 → **0.6** and a softer mote pattern so the sheet reads as continuous with brighter knots, and `energy` 0.6 → **0.4**, so total light stays about the same. Each curtain stays visible down to the sea (fade only the last 10%). The counts stand (8/12/16/24).
- [ ] **3. Rain reads as rain in `landfall_ch08`, not scratches.** Bright streaks now cover 27% of the frame (pixels more than 0.04 OkL above their row median; 10.5% in `day_ch08_high`), and they are uniform, parallel and crisp. Start with: inner-layer `alpha` 0.18 → **0.10**, streak length varied ±40%, and the outer layers softened into veils (wider, lower contrast). Colour `#7A8794` → **`overcast_slate` `#6F7E8E`** (a palette swatch, slightly darker). **Pass:** streak coverage ≤ 12% in `landfall_ch08`, and the far layers read as sheets.
- [ ] **4. `ch08_landfall` reaches near-night, with a teal-slate cast, not grey.** It now measures frame mean OkL **0.265**, against 0.316 for the day and 0.220 for night. Sky `#1E1E22` and sea `#161A1E` are neutral (C 0.008–0.010), which breaks colour script rule 5 (never neutral). Darken the zone shadow at full: `ambient_dim` 0.45 → **0.7**, and tint what's left toward `storm_slate` / `deep_teal_shadow`. **Pass:** frame mean OkL ≤ 0.22, sky and sea C ≥ 0.02 at hue 200–250°.
- [ ] **5. The Letting stays gold, not white.** In `letting_ch21` the rent cores clip to `#FEFEFA` (L 0.996, C 0.005). Only the outer light (`#DAD2C2` h 85°, `#9E9686`) is still `glimmer_lift`. Set `ch21_letting.wound_intensity` 3.5 → **1.8** (a starting point). **Pass:** the brightest 200 px of the rents read OkL ≤ 0.93 with C ≥ 0.02 at hue 70–95° (`glimmer_lift` +1 is `#E2DBCC`, L 0.893 C 0.022 h 86°), and clipped pixels (L > 0.98) are ≤ 0.5% of the frame.
- [ ] **6. `unbinding.rise_ratio` 0.6 → 2.0.** Colour script rule 1 has released light rising about 2× faster than held light drifts (0.15–0.4 against 0.05–0.2 m/s, midpoints 2.2×). Rising slower than the sinking was makes the exhale read as a stall.
- [ ] **7. Per-chapter lightning (closes "Per-chapter exposure flashes").** Presets gain `exposure_flash_gain` and `bolts` (on/off), and the sites' glow fades with `unbinding`:
  | Preset | Exposure flash gain | Bolts |
  |---|---|---|
  | `ch01_arrival` | **1.0 (off)**: a storm 18 km off under a noon sun doesn't double the scene's exposure | on |
  | `ch08_seawall`, `ch08_landfall` | **2.0** (colour script Ch8) | on |
  | `ch20_interior`, `ch21_heart` | **1.5**: frames at exposure 1.05–1.1 on navy jump too far at 2.0 | on |
  | `ch21_letting` | **1.0 (off)** | **off**, and the sites' glow goes to 0 as `unbinding` passes 0.5. The Letting is an exhale, not violence; there is a bolt in `letting_ch21` now. |

  Reduced motion stays at `reduced_motion_gain` (1.33), capped at each preset's gain.
- [ ] **8. No rain on an underwater camera.** ch20 and ch21 are underwater (colour script). `ch20_interior` and `ch21_heart` set `rain_amount` 0.6 and 0.5, and rain is a camera effect. Rain is 0 while an `UnderwaterRig` reports the camera submerged. Above-water memory layers keep the preset's rain.
- [ ] Recapture the rnd05 key frames, update the undertow_* lavapipe baselines if they move, and name Art (character) as the reviewer.

## Notes
- Values confirmed as built (M2-ART-03): the bolt colour `#C4D6FF` (on screen `#CED6E2`), `min_px` 2, forks 1/2/3/3, the 2-frame flash and the 0.5 s photosensitivity cap; the reflection; `ch01_arrival`, `ch08_seawall`, `ch20_interior`, `ch21_heart` numbers (ch20/21 again at their mood frames); `ch21_letting` intensity 0.6 and rotation 0.006.
- Nit, not blocking: the bolt is a bare line with no glow. A soft 3–4× width halo at about 25% would seat it in the rain.

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Key frames: `docs/kb/qa/gpu/rnd10/` (960×540; `before_after_high.png` is before on the left, after on the
right). The details are in docs/kb/tech/undertow.md, "Art's changes (M2-RND-10)". Reviewer: **Art (character)**.

| # | Criterion | Result |
|---|---|---|
| 1 | Rents are slits with a dark lip on Medium and High | **Pass on shape, close on the lip.** The half-res body hands its seam cores and lips to the composite, at full resolution. Largest rents: 12.6–23:1 (day), 8.4–14.7:1 (night); they were 1.2–5.7:1. `eye_high` has no blocky rents. The lip: the ring beside the core is 0.86× (day) and 0.95× (night) the cloud's OkL, against Art's ≤ 0.8 and 1.0–1.46× before. Wider lips didn't lower it; please judge by eye. |
| 2 | Curtains are hanging sheets | Done: 900 m, Gaussian edge, a soft 2-octave pattern over a veil, full to the sea's last 10%. Energy is **0.2**: Art's 0.4 measured about 4× the old total light. New: curtains within 1.5–4 km of the camera fade (from under the canopy they were a sky-wide smear). |
| 3 | Rain reads as rain | **Pass:** `landfall_ch08` bright-streak coverage is 11.6% (≤ 12%; it was 26.7%). Inner alpha 0.08, `overcast_slate`, length ±40%, the outer layers are veils. |
| 4 | Landfall near-night and slate-teal | **Close.** Frame mean OkL 0.211 (≤ 0.22; it was 0.263). Sky C 0.028 at h 225° (pass). Sea C 0.018 at h 236°, just short of 0.02. **Found:** at 10 km the zone was only 0.65 in shadow (the canopy's soft edge), so `ch08_landfall` is now 9.6 km. A sky-sourced ambient ignores `ambient_light_color`, so the tint goes in through the sky contribution. The visible sea is mostly the zone sky's reflection, which the storm doesn't tint. |
| 5 | The Letting stays gold | **Pass** at `wound_intensity` **0.9**, not 1.8: the brightest 200 px are OkL 0.898, C 0.020, h 85°, clipped 0%. The shot now carries the preset's intensity 0.6, wound intensity 0.9 and bolts off. |
| 6 | `rise_ratio` 2.0 | Done. |
| 7 | Per-chapter lightning | Done, matching Art's table. The sites' glow fades over unbinding 0.5–0.7, so the Letting has no bolt. |
| 8 | No rain underwater | Done: `UnderwaterRig.camera_submerged`. |

- **Cost (1440p, the storm's own, same build):** High +0.07–0.12 ms (0.67–0.91 ms), Medium +0.06–0.14 ms
  (0.83–1.19 ms).
- **Found:**
  - `capture_preset` ignores a shot's `setup` block. The storm's rnd05 frames came from the capture rig, which
    applies it.
  - An "Uniforms supplied for set (3)" Vulkan error, twice per run, is already on the integration branch (the
    compute body's warm-up). It goes into M2-RND-11.
- **Lavapipe baselines that will drift** (for the Lead to re-approve; I didn't touch them): every `undertow_*` shot,
  above all `undertow_letting_ch21` (its setup changed) and `undertow_landfall_ch08`.
- **Checks:** gdlint and gdformat, validate_data, `gen_undertow_compute.py --check`, the Godot `undertow` filter
  (57/0, 6 of them new in `test_undertow_art_fixes.gd`), and the full suite.

## Review log
