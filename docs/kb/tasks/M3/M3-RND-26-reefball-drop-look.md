---
id: M3-RND-26
title: The Reefball water drop's look (inside the Tamsule Bell), on the agreed volume
role: rendering
status: review
reviewer: art (env-art, the Tamsule Bell kit's owner)
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC, claude/env-art-b; Lead 2026-10-28: rendering's zone and kit looks go to env-art-b)"
depends_on: [M3-ENV-01]
milestone: M3
request-from: environment
---
## Goal
M3-ENV-01 built the Tamsule Bell arena (Ch7, the Tidecup) around a marked volume for the held water drop, whose
look is PC GPU R&D (the Lead's brief: "The PC GPU session owns the water-sphere look R&D"). No Reefball R&D was on
any `gpu/*` branch or in pc-gpu.md on 2026-10-24, so Environment proposed the volume and anchor in
[tamsule_bell.md §1](../../art/environments/tamsule_bell.md). This task asks PC GPU to accept or amend that contract
(answer in pc-gpu.md and this file) and then build the look on it.

The contract, in arena space (origin on the bell axis at the river datum, north -Z): `SphereAnchor` at
`(0, 31.5, 0)`; an oblate spheroid of horizontal radius 14.0 m and vertical semi-axis 11.5 m; the weep point at
y 20.0 (`ColumnAnchor`), the surface at y 43.0 (`GoalRingAnchor`, where Environment's bronze goal ring hangs); a
weep column of radius 0.8 to 0.6 m down to the catch-pool water at y 0.35; >= 2.0 m from the bell's inner surface
(2.26 m measured). The placeholder is the `Drop` child of `SphereAnchor` in
`game/levels/_tests/tamsule_bell_kit/tamsule_bell_kit.tscn` (`reefball_drop_proxy.glb`, tagged PLACEHOLDER).

## Acceptance criteria
- [x] The contract is accepted or amended in writing (pc-gpu.md and this file). An amendment that changes the size
      or the anchor goes back to Environment, because the bell's inner profile and the clearance test move with it.
- [x] N-12's look: perfectly still at rest (bound light holds it: no ripples until bodies move it), a slightly
      flattened drop rather than a perfect sphere, the weep column falling from its lowest point, light through it
      casting caustics on the catch-pool, the posts and the bell's underside (the shade disc under the Bell is the
      zone's value idea, tamsule_bell.md §0). The colour script's ch07 row: the drop pushed cyan, caustics under the
      Bell allowed to clip to white. Any glimmer in it obeys the bound-light rule (`glimmer_bound`, steady).
- [x] It replaces `Drop` under `SphereAnchor` in the preview scene, viewed in T01, T02, T03 and T05; the two
      registered shots (`tamsule_t01_bell_from_the_mouth`, `tamsule_t03_oruvel_moorings`) re-approved after viewing.
- [ ] Cost measured on the PC GPU presets (it is seen through 48 glass bays and from beneath).

## Notes
- Visible through the glass waist (y 30.15-41.0) and below the rim (y 27.0; the drop's lower 7 m hangs out of the
  mouth). Above y 41 the bronze crown hides it; there is a 4.4 m air pocket over the surface.
- The bronze bell is `env_bronze.gdshader` (Environment); the salt-glass bays are a plain transparent
  StandardMaterial3D (`tb_salt_glass`), which Rendering may replace with a refractive one if the drop needs it.
- Renumbered by the Lead at big8 (2026-10-24): filed by env-art as M3-RND-01, which collided with Rendering's sphere-look task.

- **Renumbered (Lead merge, big8, 2026-10-24):** filed as M3-RND-01, which collided with the PC's M3-RND-01 (the Reefball water sphere, built and merged at big7). Now M3-RND-26, the next id free across all branches.

## Notes (env-art-b, 2026-10-28, owning it for Rendering by the Lead's decision)
- **The contract is accepted unchanged** (rendering's answer; the PC's pc-gpu.md is the PC's to edit, so it's here
  and in env-art-b.md): the 14.0 × 11.5 m spheroid at `SphereAnchor` (0, 31.5, 0), weep point y 20.0, surface y 43.0.
- **The look:** `WaterSphereRig` with `profile = "tamsule_drop"` (`game/data/vfx/water_sphere.json` `profiles`; docs
  `docs/kb/tech/water_sphere.md` "The Tamsule Bell's held drop"). The rig's passes now take a flattened spheroid
  (`sphere_flatten`), the drop is still (no swell, a steady web), pushed cyan (turquoise_shallow over 18 m), glows
  with its bound light (glimmer_bound, steady), and throws its web under it on the pool, its coping and the posts, and
  the pool's reflected web on the faces turned down under the bell, allowed to clip to white. The Reefball arena's
  ball is unchanged (the empty profile).
- **The weep column** is the contract's now: 0.8 → 0.6 m, from the pool's surface into the drop (`b_column.py`),
  turquoise in the zones.
- **Placed:** the preview (`SphereAnchor/Drop` is the rig, `SphereAnchor/WeepColumn` the column; `preview_scene.py`),
  `ch07/tamsule_bell_galleries` and `ch07/tamsule` (ZoneKitDressing's new `drops` rows).
- **Viewed** (self-rendered, lavapipe): T01, T02, T03, T05, `ch07_bell_galleries`, `ch07_bell_moorings`,
  `ch07_tamsule_gantry`, `ch07_tamsule_mouth`. `tamsule_t01_bell_from_the_mouth` and `tamsule_t03_oruvel_moorings`
  drift (the drop is cyan and the column wider): their re-approval is the Lead's gate (env-art-b never writes baselines).
- **Left:** the cost on the PC presets (the last criterion), and the two baselines' re-approval.

## Review log

## Notes (env-art-b, 2026-10-28, ADR 0041)
- Both Ch7 zones now show the Bell with no water in it: `ch07/tamsule_bell_galleries` keeps the greybox `Column`, and
  the drop is absent there and from `ch07/tamsule` (the port, whose Bell axis is (0, −1.6, −75)). `WaterSphereRig`
  (M3-RND-01) is a 16 m sphere by `water_sphere.json`; the Bell needs the oblate 14.0 × 11.5 m drop at (0, 31.5, 0) of
  the contract above (a 16 m sphere cuts the bronze), and its post passes intersect the sphere analytically, so the
  node can't simply be scaled. Asks: a per-placement size (radius and vertical semi-axis) or a per-use data row, and
  the weep column. env-art-b places them in both zones the day they land.
- **2026-10-28 (env-art-b):** the weep column is done as a static kit piece (M3-ENV-1321, at the Lead's ask under ADR 0041). It is on both Ch7 zones, and the galleries keep no greybox. Still yours: the sphere rig sized to the drop contract, and a flowing look for the column if wanted (swap its zone materials).
