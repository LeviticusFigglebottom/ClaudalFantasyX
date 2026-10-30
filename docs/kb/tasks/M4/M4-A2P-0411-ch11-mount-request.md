---
id: M4-A2P-0411
title: "Mount env-art's Ch11 dressing in ch11/sunken_vey and ch11/lowlight (request to chapters)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M4-A2P-041]
milestone: M4
request-from: environment
reviewer: environment
---
## Goal
M4-A2P-041 (env-art) built Ch11's look on the two greyboxes, all from `tools/act2/ch11_lowlight_dressing.py`:
- `game/levels/ch11/<zone>/<zone>_dressing.json`. The Vey's walks, courts, parapets, conduit stand and Lowlight's gate,
  and Lowlight's atrium, hallway, engine hall, flights and drowned sanctum, are built from your greybox
  (`vey_zones.py`, `lowlight_zones.py`), so their slabs, rails, walls and doorways stand where your collision is. Around
  them stand the kit's drowned arcades, columns, strangler figs, the conduit housing (the mark), the lamp bench and the
  well-shaft.
- `<zone>_environment.tres`: colour script ch11 grey noon, `lut_ch11_vey`.
- `<zone>_water_material.tres` (overcast_lagoon) and `<zone>_waves.tres` (still water, the arena's).

The greybox keeps the gameplay: no spawn, mark, trigger or walking surface moves. env-art's previews mount everything
exactly as below: `game/levels/_tests/ch11_zones/<zone>_dressed.tscn`.

## Ask (the zone scenes and layouts are yours)
- [ ] **Mount the dressing.** In `sunken_vey.tscn` and `lowlight.tscn`, add a `Water`, a `Tide` and a `Dressing` as the
      Ch10 zones do. Copy them from the preview scenes:
      - Vey: the WaterSurface at y −0.3 (the Water block's top), `publishes_water_level`, `sunken_vey_waves.tres`.
      - Lowlight: the WaterSurface at the Waterline's −2.05 on a `PlaneMesh` the Waterline's size and centre. The temple
        is drowned below that line; the zone's water is not a sea.
- [ ] **The Lamp Engine in the field.** The `LampEngine` block's look is creatures' `lamp_engine` (an actor row or an
      instance at the block). The dressing hides the block like every other; the vault's fallen bay is over it.
- [ ] **The well's mouth.** It is open in the sanctum's floor, r 3.0 about (64, −8, 4), with the kit's `well_shaft`
      dropping from it. Your floor still walks over it. Either add a collision ring round the mouth (a low cylinder,
      r 3.1), or keep the party off the floor per the beat sheet's default (a): a dry ledge at y −2, the sanctum seen
      below underwater. `nhoa` and the Sanctum spawn stand outside the mouth (tested).
- [ ] **Wading (L02's "knee-deep").** The atrium's and hallway's floors are dry wet flags at y 0. The hall has a 3 cm
      water film over its flags, which splashes at your floor's level. If the nave should be waded, the greybox floor
      must go down; then the dressing raises a water plane over it. That is your call with the beat sheet.
- [ ] **Underwater.** Below −2.05 (Flight2's lower half and the sanctum) wants the underwater rig, as Ch1's Underway
      has.

Ambient: the layouts' `environment` row (0.7, #7FA3A8) already matches the grade's fill. No change.

Rendering's, not this ask: the cold haze off the well, the silt-light sifting down it, and the core's release lift
(beat sheet T03, N02).

## Review log
