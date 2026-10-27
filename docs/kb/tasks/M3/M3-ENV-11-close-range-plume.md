---
id: M3-ENV-11
title: "A close-range Pemakar plume (it was built for 900 m; inside 300 m its billows facet and go black)"
role: environment
status: review
owner_session: "env-art"
depends_on: [M3-ENV-09]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Follow-up to M3-ENV-09, from its worker. The Pemakar plume (`plume_vent` and the plume billows, with
`env_ash_plume.gdshader`) was built to read at 900 m. Inside about 300 m, which covers the Ashcrown zone and its
crater loggia, its billows show sharp facets and their shaded side goes near-black. The Ashcrown worker dropped
its crater-loggia view because of it.

## Acceptance criteria
- [x] A near plume: a denser close LOD or a softer near piece, and a shader treatment so the shaded side keeps
      some value, built in the Pemakar or Ashcrown job.
- [x] Ashcrown's crater-loggia view restored and viewed. No existing Pemakar or Ashcrown baseline drifts unless
      the plume is in frame; any re-approval is viewed and has a stated reason.
- [x] Lights near any fog volume keep `light_volumetric_fog_energy = 0`.

## Notes (env-art worker, 2026-10-24)
- **Near piece** `ash_plume_near` (Pemakar job, `pemakar_skyline.py`): `ash_plume`'s own surface (the same noise,
  seeded by `ash_plume`), sampled 160 × 128 (40,832 tris, 1.45 MB) instead of 64 × 52; the creases between the
  heads rounded (`NEAR_CREASE`); normals smoothed over the grid (3 passes) and bent 30% toward the column's radial
  direction; UV2.x carries the small heads (0 crease, 1 crown, weighted like the displacement). **LOD1 is
  `ash_plume`'s LOD0** (identical mesh). `ash_plume.glb` is byte-identical (the generator was refactored into
  `_plume_shell` / `_plume_cap`; a test pins near LOD1 == far LOD0). PROVENANCE row appended; `.glb.import` on
  the Pemakar post-import (pemakar_import_settings.py).
- **Shader** `env_ash_plume`: a `near` group (all default 0, so `kit_plume` and the town's plume are unchanged:
  P01, P03 and the Lanternfall arena compare at rmse 0.00000): a sky-coloured lift (strongest away from the sun,
  `lift_all_round` of it everywhere, since the shader cannot see the temple's cast shadow), back-scatter through
  the edges looking sunward, the vent's ember on the foot, `billow_shade` from UV2.x, `sky_up`, and inside
  ~240 m a bumped billow normal (`near_detail`, 4 fbm taps, only when on). `alpha_mottle` (default 0.4 = the old
  0.8 + 0.4 n). Everything near fades out by `near_fade_m` (400 → 800 m in `ac_plume_day`).
- **Found:** close up, the plume's ~3% see-through (opacity 0.97 × mottle) showed the crater rim's silhouette
  through the dark column: that, and the temple's cast shadow on the plume's south face (which faces the sun, so
  a normal-based lift alone missed it), were most of the "near-black". `ac_plume_day` sets opacity 1 and
  alpha_mottle 0.04.
- **Ashcrown preview:** `ac_preview_layout.py` places `ash_plume_near` with LOD0 to 900 m (`PLUME_LOD1_M`);
  `ac_plume_day` carries the near parameters. **A08 the crater loggia** restored (from the hall north of the anvil,
  the loggia framing the plume's near face 8 m beyond the balustrade); **A10** (the design table's old A08 rim
  view, moved down the west outer slope: on the rim itself the column is 20 m away) shows the near plume best.
- **Baselines:** `ashcrown_a01_approach` re-approved (rmse 0.02389: the plume only; its black shards became
  modelled ash heads, still darker than the sky); `ashcrown_a04_anvil_hall` re-approved (rmse 0.00615, inside the
  gate: the loggia no longer shows the rim through the plume); **new** `ashcrown_a10_plume_from_the_rim` (the one
  new baseline: A08 is A04's loggia from closer, which A04 already guards). Pemakar P01/P03 and the arena: rmse 0.
- **Limits:** A08 is soft and plain (the near face is in the temple's shadow all day; only the lift and the bumped
  heads model it). O2 (660 m) still shows a few torn shards high in the column (edge-faded overhangs). The vent's
  foot is never in frame from the hall (the balustrade hides it). The billow bump is per pixel, not geometry, so
  the silhouette stays the mesh's.

## Review log
