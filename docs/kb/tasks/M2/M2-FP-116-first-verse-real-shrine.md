---
id: M2-FP-116
title: "FAST-TRACK: the First Verse plays in the real Shell Shrine, not on a CSG set"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-FP-04, M2-FP-112, M3-ENV-704]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
This is queue item 2, the human's "primitive moments". Cutscene B, "The First Verse", is the slice's emotional
peak, and it still played on M2-FP-04's placeholder set:
- a CSG island cylinder, dome, pillars and box steps;
- a flat-coloured sea plane;
- an emissive disc for the pool;
- a bronze sphere for the Drownbell.

The player has just walked through the real shrine in the level before.

## Acceptance criteria
- [x] **The set is the real shrine and kit.** `first_verse.tscn` loses every CSG node and the flat sea, pool and bell
  meshes. In their place:
  - env-art's `shell_shrine_dressing.tscn` (hall, vault, west portal, outer steps, islet);
  - the trial's pieces from the Haluna kit at the trial layout's positions: the inner pool with an octagon of the
    shrine's still water, the side pool, the four basins and the spring;
  - the shrine level's sea (WaterSurface at −2) and its exterior set dressing (rope, debris, net, offerings);
  - two of its interior bounce lights;
  - the Drownbell model ×2 offshore, past the islet, its hood 1.6 m out of the sea.
- [x] **Restaged in the real geography; the lines are unchanged.**
  - **S07:** Rhen and Toma stand in the west portal. The camera sits behind them on the steps, looking down the
    hall to the far chamber door, and Asha walks in from just inside.
  - **S08:** Asha stands at the inner pool's south-west edge under Ilun, from a low camera tilted up into the
    vault. A new stand-in clip, `@anim asha stand_at_pool`, places her during the black.
  - **S06:** the two sit on the outer steps at their measured tread heights, with the camera at the south end
    looking north-north-west. The sun is frame-left, per haluna.md §5.3.
  - **S09/S10:** Asha comes out of the portal onto the top step. S10 now faces Rhen from the west, because the
    mapped position sat inside the curved wall.
  - **C08:** looks from above the islet toward the bell and the low sun.
- [x] Tests:
  - test_fp_first_verse: a new test checks there is no CSG, the shrine hall is there, and Asha stands at the pool
    under Ilun;
  - fp_ 28, first_verse 2, shell_shrine_level 9, haluna_weather 3, hero_field_snaps 2, dialogue 76, cutscene 60,
    slice_shots 1, all 0 failed;
  - dlgc clean.
- [ ] PC renders: slice_verse_steps and the new slice_verse_hall (S07), then a framing pass.

## Notes
- **Ilun's chamber** (S08's "net caustics on the dome, the spectral manta") is not built. The hall's vault over
  the inner pool stands in for it. Request it of env-art if the PC frame doesn't read.
- **Rhen and Toma stand on the steps.** Their `sit_steps` clip is still a Character request.

## Review log
