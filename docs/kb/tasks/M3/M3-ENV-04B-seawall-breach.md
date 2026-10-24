---
id: M3-ENV-04B
title: Ch8 the Seawall falls: the breach state of the Corrow kit (and the Ch9 night pass)
role: environment
status: review
owner_session: env-art worktree
depends_on: [M3-ENV-04]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Follow-up to M3-ENV-04 (filed by env-art when the kit landed without its destroyed state). Ch8 "The Seawall":
"**The wall falls anyway.** The stair was not wide enough" (act outline), and after the storm the Stillguard
cut Liss's hoist down. Ch9 "The Ebbing" plays on the same pieces at night (`ch09`). The kit is built for this:
every wall piece is a 12 m segment on the R = 300 m arc (docs/kb/art/environments/corrow.md §2), so a breach
replaces segments one for one.

## Acceptance criteria
- [x] `seawall_breach_a/b` (12 m each, on the same arc, LOD chains): the wall broken through to below the town
      level, its courses torn in steps, blocks tumbled into the low town and out onto the rip-rap; the walk's
      paving hanging over the gap; `seawall_breach_end` caps for the segments either side.
- [x] `watcher_head_fallen`: a head down on its side in the rubble (the face still humming), and a cracked
      head leaning out of the line.
- [x] `fisher_stair_broken`: the upper flight hanging where the wall went, the hand-line slack.
- [x] `liss_hoist_cut`: the spar down on the walk, the cut rope ends, the strap-plates still bolted into the
      head (corrow.md §1.4; act outline Ch8 last beat).
- [x] A rubble field for the flooded lanes (`lowtown_rubble`), so the stair foot reads after the fall.
- [x] The preview gains a `fallen` phase (post-storm grey light) and a `ch09` night phase (stars, half moon,
      sea-glow, the motes going out to sea are VFX, not the kit), with one composed view each; at most one
      new screenshot baseline.
- [x] `verify_blender_builds --job corrow_kit` byte-identical; PROVENANCE rows; no glow at the stair foot
      in any shot (ADR 0022 (g)).

## Notes (env-art, 2026-10-24)
- Built inside the kit and job `corrow_kit` (`cw_breach.py`, `cw_fallen.py`; `verify_blender_builds --job
  corrow_kit` 44 identical): `seawall_breach_a/b`, `seawall_breach_end_w` / `_e` (one end per side: a mirrored
  piece would need a negative scale, which collision shapes do not take), `lowtown_rubble`,
  `watcher_head_fallen`, `watcher_head_cracked`, `fisher_stair_broken`, `liss_hoist_cut`, and the optional second
  carving `watcher_head_b` (`cw_common.CARVING_B`). New slot `cw_laterite_broken`. Design: corrow.md §7.
- The second carving is a kit piece and carves the fallen head and the broken relief; it is **not** placed in
  the intact preview row, because that would change the two approved corrow baselines (C01 and C08 see the whole
  row). They re-capture at rmse 0.00000. m2-slice can mix `watcher_head_b` into the zone's row (below).
- Preview phases `fallen` (`ch08_after`, no colour-script row yet: proposed in corrow.md §7) and `ch09`; C10 is
  the new baseline `corrow_c10_breach_fallen`, C11 is the night view (manifest only).
- Story flag for Narrative: in the preview the breach takes the stair's middle, so in Ch9 the stair climbs only 12
  steps (+3.4 m) before the break. "Carrying a child's body up it" still reads (up the standing flight, toward
  the gap), but a zone that wants a whole climb in Ch9 should put the breach east of the head landing instead
  (any run of slots works; Liss's head must stay out of it).
- `ch09` ambient is 0.7, not the script's 0.3 fill: at 0.3 the stair foot was black. Rendering may prefer a real
  fill light; noted for review.

## Swap-in note for m2-slice (`game/levels/ch08/corrow/`)
- **Segments.** A breach is a run of 12 m slots: replace the `seawall_curve` at each slot with
  `seawall_breach_end_w`, then one or more `seawall_breach_a` / `_b`, then `seawall_breach_end_e`, with the
  **same transform** (arc pose at the slot's centre s, yaw -s/R). The ends are the seawall's own generator and seed,
  so they join the intact neighbours exactly; the floors meet at every joint. Remove the heads over the gap slots
  (4 per slot) and the reliefs the tear took (gap slots: both; `_w`: the relief at +3 m; `_e`: the one at -3 m).
  The ends keep their heads (0.3 m of parapet torn). The rip-rap (`wall_apron`) stays.
- **Heads.** Swap the edge head (`_w` at +4.5 m, `_e` at -4.5 m) for `watcher_head_cracked`, same transform. Place
  `watcher_head_fallen` (origin on the ground under its centre, already sunk 0.3 m) on the gap floor
  (`cw_breach.floor_base(z)` + debris cone), in the lanes (+1.0 m) or on the rip-rap (mound + 0.45 m).
  Optionally alternate `watcher_head_b` into the intact row (same frame and footprint as `watcher_head`).
- **Hoist and stair.** `liss_hoist_cut` replaces `liss_hoist` (the head's frame); `fisher_stair_broken` replaces
  `fisher_stair` (the stair's frame). Both assume the preview's breach (stair foot at s -40, gap s -36 .. -24,
  hoist head at s -16.5); a different breach needs `cw_fallen.BREAK_X` / `HANG_FROM` moved with it.
- **Lanes.** `lowtown_rubble` cells at +1.0 m: lane down local x = 0 kept clear (|x| < 1.7 m), +Z end toward the
  wall; hide the houses under a breach's debris fan.
- **Anchors and collision.** The stair's walkable path now ends at the 12th step (+3.4 m) and resumes only at the
  head landing; the walk ends at the torn top course (about 1.2 m back from each end slot's gap side). Walk
  collision should follow the `_w`/`_e` walk mesh, not the old segment box; the gap floor, the debris cones and
  the rubble cells want trimesh or simplified convex shapes (blocks are separate rounded boxes). The hanging
  flight, the hanging slabs and the slack hand-line are set dressing (no collision, no anchors). The
  `corrow_kit` post-import maps every new slot; there are no new collision rules in it.
- **Lighting.** `ch08_after` and `ch09` as in corrow.md §7; nothing in these pieces is emissive (ADR 0022 (g)).
  Keep the `ch09` sea below +0.4 m (the breach sill) or sea-glow reaches the stair foot.

## Review log
