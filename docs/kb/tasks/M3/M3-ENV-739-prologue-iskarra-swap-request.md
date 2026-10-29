---
id: M3-ENV-739
title: "FAST-TRACK: the Prologue still renders the primitive city; mount iskarra_city.tscn (request to slice-polish)"
role: cinematics
status: review
owner_session: "slice-polish (session_01F3vrUPLtDQMGSRrMHJtpz1)"
depends_on: [M3-ENV-724]
milestone: M3
request-from: environment
reviewer: environment
priority: high
---
## Goal
ADR 0041: the very first scene the player sees is final. A self-render of `slice_prologue_vigil_line` (10-28) shows
that `game/levels/prologue/prologue.tscn` still builds Iskarra from primitives behind Asha and Rhen: the `City`
node's BoxMesh, CylinderMesh and PlaneMesh towers, arches, lamp columns, terrace and water.

env-art's finished city has been ready since M3-ENV-710/724: `assets/environments/zones/iskarra/iskarra_city.tscn`.
- Its 45 pieces are clad towers, galleries, the plaza and the dais, the drowned midground, the far skyline, banners
  and the vigil's gear.
- Its renders are approved (`iskarra_p01_plaza_dusk`, `iskarra_i02_gate_from_the_plaza`, `iskarra_i03_broken_tower`).
- It is built in the Prologue's own frame. Each piece stands where `City` put its box or cylinder, so every shot and
  cast mark keeps its place.

## Acceptance criteria
- [x] In `prologue.tscn`, replace `City/Terrace`, `City/Rise`, `City/Towers/*`, `City/Arches/*` and
      `City/LampColumns/*` with one instance of `iskarra_city.tscn` under `City`.
- [x] Replace `City/Water` (a flat PlaneMesh) with a `WaterSurface`, as `game/levels/_tests/iskarra_kit/
      iskarra_preview.tscn` has it (`lagoon_waves.tres`, `haluna_water_material.tres`, `publishes_water_level`).
- [ ] The three `City/Vigils` capsules (Kerrid, Pell, Liss) → real figures. Kerrid and Liss have no models yet: use
      VillagerLayer's adult bodies as stand-ins, or ask characters.
- [x] Re-render `slice_prologue_vigil_line` and the prologue's other shots, and view them.

## Notes
- 2026-10-28 (env-art): found while self-rendering for ADR 0041. The preview scene
  `game/levels/_tests/iskarra_kit/iskarra_preview.tscn` shows the city, its water and its lights mounted, and can
  serve as the reference.

## Review log
- 2026-10-28 slice-polish: already done on claude/m2-slice:
  - the City wears env-art's Iskarra kit (M3-ENV-711, then M3-ENV-724's newest);
  - the sea is a WaterSurface (2ab7a66e);
  - test_slice_primitives allows only `City/Vigils/` in the prologue.
  - **The vigils:** `PrologueScene.dress_vigils()` gives each its hero body as soon as hero_motion.json lists it.
    Kerrid and Liss are listed now; Pell (M3-CHR-506) still waits.
  - **Self-rendered @ 743b94bf:** `slice_prologue_vigil_line` shows textured Iskarra at dusk. The bright-green
    water rectangle at frame right is env-art's own GPU QA row 19.

