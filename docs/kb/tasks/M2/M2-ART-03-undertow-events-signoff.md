---
id: M2-ART-03
title: Art sign-off on the Undertow's storm events and chapter presets (M2-RND-05)
role: character
status: done
owner_session: "env-art"
depends_on: [M2-RND-05]
milestone: M2
request-from: rendering
---
## Goal
M2-RND-05 built the Undertow as an event (docs/kb/tech/undertow.md, "Storm events"):
- torn rents;
- curtains of held light off the wounds;
- lightning bolts and the exposure flash;
- rain, the zone shadow, and the storm in the sea's reflection;
- chapter presets, including the Ch21 Letting.

Its acceptance asks Art to confirm the `spawn_wound` usage. This package asks for that, and for a read of the new looks against the colour script. As for M2-ART-01, the Art Director takes this under the character role.

**Key frames** are in `docs/kb/qa/gpu/rnd05/` (RX 9070 XT, 960×540). `*_high` frames use the High preset; the others use the capture rig's scene defaults.

| Frame | What to look at |
|---|---|
| `before_after_high` | Day, dusk and night, before (left) and after (right): the rents, the curtains and the reflection |
| `day_ch08_high`, `dusk_high`, `night_high`, `eye_high` | The four storm moods with every event part on |
| `strike_ch08` | A cloud-to-sea bolt with a fork (Ch8 storm wall) |
| `landfall_ch08` | Preset `ch08_landfall`: under the canopy's edge, the zone shadow at full and heavy rain ("darkens to near-night by 16:40") |
| `letting_ch21` | `unbinding` 1: the wounds, the curtains and the throat streaks turned to `glimmer_lift`, and rising |
| `dusk_low` | Low (shells): the rents and the curtains on the cheap tier |

The test scene is `game/levels/_tests/undertow/undertow_test.tscn`. A storm property in the inspector, or `Storm:preset` / `Storm:unbinding` in a shot's setup (`docs/kb/qa/gpu/2026-10-24-rnd-05-pending-shots.json`), shows any preset.

## Acceptance criteria
- [x] **`spawn_wound` for the storm's rents.** palette.json limits `spawn_wound` to "creature weak points only". The Undertow's rents use it, because the storm is the spawn's source (SPEC §7.5, bible §9). Either extend the usage note in palette.json, or name the swatch the rents should use. That's an edit to Art's file.
- [x] **The rents read as torn seams.** Each has an open glowing core, a dark torn lip and a faint halo of the poured-out light (undertow.json `wounds.lip_*` and `halo_*`). Confirm, or give the change: wider or darker lips, or less halo.
- [x] **The curtains of held light** (`streamers`): cyan, sliding down, hanging from the rents to the sea. Confirm the count, brightness and width, or give the change.
- [x] **Lightning:** the bolt's colour (the ch20 key `#C4D6FF`), width and fork count. The exposure flash is the colour script's Ch8 "2.0× exposure for 2 frames", capped at two a second and gentler under reduced motion. Confirm it for every storm chapter, or say which chapters drop it.
- [x] **Rain and the zone shadow** in `landfall_ch08`: is near-night dark enough, and does the rain read as rain, not scratches?
- [x] **The Letting** (`letting_ch21`): `glimmer_lift` at full on the rents is near-white at this exposure. Confirm, or set the Ch21 preset's `wound_intensity` and the `unbinding.rise_ratio` speed.
- [x] **Presets** (undertow.json `presets`, from the colour script): `ch01_arrival`, `ch08_seawall`, `ch08_landfall`, `ch20_interior`, `ch21_heart` and `ch21_letting`. Confirm the values, or give the changes. Rendering applies them.

## Review log
- 2026-10-24 Art Director (env-art): **approve with fixes** (filed as M2-RND-10). I looked at all nine frames in `docs/kb/qa/gpu/rnd05/` (`dusk_low` is 480×270). The numbers are Oklab, from sampled regions. "Brightest" means the median of the brightest 200 px in a region.
  - **`spawn_wound` for the rents: extended (palette.json 0.2.1).** The Undertow is the spawn's source, its rents are the same language, and the colour script already names `spawn_wound` as Ch8's glimmer. Its usage is now "wound surfaces only: Undertow-spawn creature weak points and the storm's own rents (body, Low shells, funnel sea)", never the held light from a rent, and never bound light. In the same edit, `glimmer_held`'s note now covers the storm's held light (pooled light, curtains, throat streaks), and `glimmer_lift`'s note covers the Letting's turned rents and curtains. Each had the same conflict. The rents' cores measure `#BAE2DE`–`#CAEEE6` (h 180–189°), on the `spawn_wound` hue (on-screen h 184°), so no colour changes.
  - **Rents as torn seams: changes.** On Low (`dusk_low`, full-res shells) they are exactly right: winding slits with dark lips. On High (the 0.35-scale body), `day_ch08_high` and `night_high` show soft cyan blotches with no lip, and the halo turns the night wound field into one glowing band. `eye_high` breaks them into rectangular cyan blocks. **Change:** narrower cores (`width` 0.05), darker lips (`lip_dark` 0.9), half the halo (`halo_energy` 0.06), or a full-res seam pass if the half-res body can't hold a slit. Pass: aspect ≥ 4:1 and lip ≤ 0.8× the surrounding cloud.
  - **Curtains: changes.** The count (16 High) and the cyan are right. They read as narrow rods with a stepped ladder pattern. In `letting_ch21` they read as masts, and by day they stop well above the sea. A curtain is a sheet. **Change:** `width_m` 900 with a soft edge, `mote_cover` 0.6 with softer motes, `energy` 0.4, reaching the sea.
  - **Lightning: confirm the bolt; flash per chapter.** The bolt is `#CED6E2` on screen (h 258°, from `#C4D6FF`), 2 px with 2–3 forks, cloud base to the sea. It reads as lightning (`strike_ch08`). The 2.0× flash for 2 frames with the 0.5 s cap is confirmed for **Ch8**. **Ch1 arrival drops the flash** (a storm 18 km off at noon), and keeps bolts. **Ch20 and the Ch21 heart use 1.5.** **The Letting drops bolts, flash and site glow**: it is the world exhaling, and there is a bolt in `letting_ch21` now (pillar 1).
  - **Landfall: not dark enough, and grey.** The frame mean OkL is 0.265 (day 0.316, night 0.220). Sky `#1E1E22` and sea `#161A1E` are neutral (C 0.008–0.010), against rule 5. **Change:** `ambient_dim` 0.7, with a slate/teal tint, to frame mean ≤ 0.22 and C ≥ 0.02. **Rain reads as scratches at this density:** 27% of the frame is bright streaks (10.5% by day), crisp and uniform. **Change:** alpha 0.10, varied length, veiled outer layers, colour `overcast_slate`. Target ≤ 12%.
  - **The Letting: change.** The rent cores clip to `#FEFEFA` (L 0.996, C 0.005): white, not gold. Only the outer light keeps `glimmer_lift` (`#DAD2C2`, h 85°, ΔE 0.027 from its +1 `#E2DBCC`). **`ch21_letting.wound_intensity` 3.5 → 1.8** as a start, with the target core ≤ OkL 0.93 and C ≥ 0.02 at h 70–95°. **`unbinding.rise_ratio` 0.6 → 2.0:** rule 1 has released light rising about 2× faster than held light drifts, and a rise slower than the sink reads as a stall, not an exhale.
  - **Presets.** Confirmed: `ch01_arrival` (0.75, wounds 0.7, 18 km), `ch08_seawall` (1.0, 1.2, 14 km), `ch08_landfall` geometry (10 km, wounds 1.6, auto rain), `ch20_interior` (2.5) and `ch21_heart` (3.0) as starting points, to be re-checked at their mood frames, and `ch21_letting` intensity 0.6 and rotation 0.006. Changed: as above, plus rain is 0 on a submerged camera (ch20/21 are underwater; their presets set rain 0.6/0.5).
  - **The reflection: approve.** A column of cyan glints sits under the wounds by day and dusk, and the night sea stays the one teal field. The `before_after_high` pairs show the rents, curtains and reflection adding to the storm without breaking the pillar-2 read (the gold upper flanks at dusk survive).
  - Out of scope, noted: `eye_high`'s cloud is still a near-uniform khaki with a visible dot-grid dither low right (the M2-RND-01 body, FSR2 without a reactive mask). That is for the body's own review.
