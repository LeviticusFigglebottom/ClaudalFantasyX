---
id: M4-A2P-0431
title: "Mount env-art's Ch13 dressing in ch13/ansedra, ch13/sanctum and ch13/lamp_archive (request to chapters)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M4-A2P-043]
milestone: M4
request-from: environment
reviewer: environment
---
## Goal
M4-A2P-043 (env-art) built Ch13's look on the three greyboxes, all from `tools/act2/ch13_ansedra_dressing.py`:
- `game/levels/ch13/<zone>/<zone>_dressing.json`;
- `<zone>_environment.tres` (colour script ch13, `lut_ch13_still`);
- for Ansedra and the Sanctum, `<zone>_water_material.tres` and `<zone>_waves.tres` (the still mirror).

The greybox keeps the gameplay. env-art's previews mount everything exactly as below:
`game/levels/_tests/ch13_zones/<zone>_dressed.tscn`.

## Ask (the zone scenes are yours)
- [ ] **Ansedra:** add a `Water` (WaterSurface at y −0.3, `publishes_water_level`, the zone's waves and material), a
      `Tide` and a `Dressing`, as the preview does.
- [ ] **The Sanctum and the Lamp Archive:** add a `Dressing` only. The basin's still water is the dressing's own
      `waters` row; the interiors have no sea.
- [ ] The layouts' sun and `environment` rows are the colour script's. No change.

Rendering's (M4-A2P-047): the still mirror mode replaces the waves and material files when it lands.

## Review log
