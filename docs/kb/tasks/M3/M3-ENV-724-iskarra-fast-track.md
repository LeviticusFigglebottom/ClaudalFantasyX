---
id: M3-ENV-724
title: "FAST-TRACK: Iskarra to Haluna quality for the Prologue (materials, trim, set dressing; the vigil gap)"
role: environment
status: doing
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-710]
milestone: M3
reviewer: rendering
---
## Goal
The Lead (2026-10-27, fast-track): the Prologue is the first thing the human plays, and Iskarra read as greybox
(untextured cylinders and towers, flat colour, capsule figures in iskarra_p01, i02, i03 and the background of
slice_prologue_vigil_line). Give it the Haluna-level material, trim and dressing pass, and close the paving and
vigil gap in test_iskarra.

## Acceptance criteria
- [x] **The root cause of the flat look.** Every tower shaft and lamp column was wound inside out since M3-ENV-710,
  so Godot culled their outer walls and drew the inside of the far wall. They are fixed and covered by a test
  (`test_the_shafts_face_out`).
- [x] **Materials.**
  - Iskarra's own glazed-tile texture (`iskarra_tile`, 0.4 x 0.2 m running bond, crazed and chipped) on the shafts
    as `kit_iskarra_cladding`, using mesh UVs in metres.
  - `kit_iskarra_glaze`, the same tile in reef_blue, for the bands, the stepped towers' domes and the paving inlay.
  - The flagstone texture (`iskarra_flag`) on `kit_iskarra_paving`.
- [x] **Trim.**
  - Two storeys of arched windows (a dark opening, a cast frame, a sill) under every gallery.
  - The galleries are real ledges: a slab, its edge and soffit, a parapet rail on posts.
  - A blue glazed band under each gallery; deeper flutes.
- [x] **Dressing.**
  - The plaza's inlaid channels are glazed, and a Lit Age sunburst is inlaid at its middle.
  - Fallen glazed tiles lie on the paving.
  - A drowned midground (`iskarra_drowned_block` x2, `iskarra_drowned_dome` x2, `iskarra_arcade_sunk`) and the far
    skyline (`iskarra_far_towers`: 44 towers at 180-520 m), placed in
    `iskarra_city.py`.
- [x] **Figures.** The preview's capsules are replaced by the four modelled heroes, as battle stand-ins at the
  Prologue cast's marks (`iskarra_preview_figures.gd`).
- [x] **The vigil gap.** `test_the_cast_stands_on_the_paving_or_the_dais` checks every cast mark of the Prologue,
  and all of them pass.
- [ ] PC renders viewed and approved: iskarra_p01_plaza_dusk, iskarra_i02_gate_from_the_plaza,
  iskarra_i03_broken_tower, and on m2-slice slice_prologue_p01 and slice_prologue_vigil_line.

## Notes
- **For slice-polish (the Prologue's staging).**
  - The Prologue's `City/Water` is a flat PlaneMesh with a plain material. The preview uses the lagoon
    WaterSurface (`water_surface.gd` + `lagoon_waves.tres` + `haluna_water_material.tres`), which carries the
    reflections, depth and foam the towers' waterline band was made for. Swap it there for the same read.
  - The three `City/Vigils` capsules (Kerrid, Pell, Liss) are the last greybox in the frame.
- Budgets: a tower is 36k / 2.4k (it was 16k / 1.2k), because the windows are geometry; the spire is 22k.

## Review log
