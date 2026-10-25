---
id: M3-RND-26
title: The Reefball water drop's look (inside the Tamsule Bell), on the agreed volume
role: rendering
status: todo
owner_session: ""
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
- [ ] The contract is accepted or amended in writing (pc-gpu.md and this file). An amendment that changes the size
      or the anchor goes back to Environment, because the bell's inner profile and the clearance test move with it.
- [ ] N-12's look: perfectly still at rest (bound light holds it: no ripples until bodies move it), a slightly
      flattened drop rather than a perfect sphere, the weep column falling from its lowest point, light through it
      casting caustics on the catch-pool, the posts and the bell's underside (the shade disc under the Bell is the
      zone's value idea, tamsule_bell.md §0). The colour script's ch07 row: the drop pushed cyan, caustics under the
      Bell allowed to clip to white. Any glimmer in it obeys the bound-light rule (`glimmer_bound`, steady).
- [ ] It replaces `Drop` under `SphereAnchor` in the preview scene, viewed in T01, T02, T03 and T05; the two
      registered shots (`tamsule_t01_bell_from_the_mouth`, `tamsule_t03_oruvel_moorings`) re-approved after viewing.
- [ ] Cost measured on the PC GPU presets (it is seen through 48 glass bays and from beneath).

## Notes
- Visible through the glass waist (y 30.15-41.0) and below the rim (y 27.0; the drop's lower 7 m hangs out of the
  mouth). Above y 41 the bronze crown hides it; there is a 4.4 m air pocket over the surface.
- The bronze bell is `env_bronze.gdshader` (Environment); the salt-glass bays are a plain transparent
  StandardMaterial3D (`tb_salt_glass`), which Rendering may replace with a refractive one if the drop needs it.

- **Renumbered (Lead merge, big8, 2026-10-24):** filed as M3-RND-01, which collided with the PC's M3-RND-01 (the Reefball water sphere, built and merged at big7). Now M3-RND-26, the next id free across all branches.

## Review log
