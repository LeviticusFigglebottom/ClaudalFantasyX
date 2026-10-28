---
id: M3-CRE-645
title: "Polish the plain reads: the gallery ray and glass skate (flat sheets at battle distance), the ridge lynx's short muzzle"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "creatures (worktree agent)"
reviewer: art
depends_on: [M3-CRE-628]
milestone: M3
request-from: creatures
---
## Goal
The "parts look primitive" audit (TRACK-RULES backlog 4), from the approved PC render fce2e82. At review distance
the gallery ray and the glass skate read small and plain, a flat pale sheet with two eyes, and the ridge lynx's
muzzle reads short and pug-like. Give each a stronger read within its sheet and budget:
- **Gallery ray:** more shape and surface. A visible spiracle and eye ridge, a raised midline and pectoral
  musculature, a whip tail with a barb, and a wing-tip curl in idle, so it reads as a ray gliding, not a sheet.
- **Glass skate:** the near-clear back stays (its role is ambush), but the silhouette needs readable edges:
  thornback ridges along the midline and tail, a rim of darker pigment, and the eyes raised on turrets.
- **Ridge lynx:** a longer, wedge muzzle with a cat's nose leather and whisker pads, and ear tufts kept.

## Notes (M3-CRE-645, 2026-10-28)
Done without a render: before/after preview sheets from the GLB vertices (PIL, painter's algorithm; the review
shot's three-quarter view, yaw 35 and pitch 14, plus a ~110 px/m battle-scale panel), kept in the session scratchpad.
Triangles (budget): gallery ray 4,104 to 4,504 (5k); glass skate 2,624 to 3,638 (4k); ridge lynx 6,988 to 7,304 (8k).
Bones, clip names and contact times are unchanged; every clip stays at or above the floor (GroundedClipsTest, no new
allow-list entry).
- **Gallery ray:** a midline keel with four raked tubercles, pectoral bulges with a shaded groove, eye sockets under
  dark brow ridges, rimmed spiracles, a whip tail with dark bands and a dark serrated barb, a darker trailing edge,
  pale freckles, and an idle whose wave grows out to curl the tips (6/10/20 degrees). The disc is re-gridded (52
  around, 26 along; more vertices near the midline). The weak point is now one small closed mark (ADR 0151): a
  `spawn_wound` lens on the camera-side spiracle's shut valve. The disc's emission mask is gone.
- **Glass skate:** thornback rows (ten on the midline, three on each shoulder, six on the tail), a `sand_wet` margin
  rim (a new swatch on its sheet), taller turrets (TURRET_TOP 0.072; the eye bones unchanged) that darken toward a
  black lid ring, and modelled spiracles in place of the painted ones that smeared grey on the coarse centre.
- **Ridge lynx:** a lofted wedge muzzle reaching to z 0.822 (the head bone unchanged), nose leather, pale whisker pads
  with dark spots, four whiskers a side swept back, a mouth line and a longer chin; the ear tufts are kept. The KO's
  head-bone yaw is halved (8 to 4 degrees at full), so the longer muzzle doesn't go under the snow (it had dipped
  to -0.033 m).
Gates: verify_blender_builds for the three jobs (each identical); unittest test_creatures + test_blender_builds OK;
validate_data 0 errors (1 old warning: haluna shrine_offering.glb); taskboard --check OK; gdlint and gdformat clean;
Godot import, then `--filter=creature`: 71 run, 1 failed, the known test_creature_portraits missing-PNG failure only.
The review shots creature_gallery_ray, creature_glass_skate and creature_ridge_lynx need a PC render (not run here).

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.
