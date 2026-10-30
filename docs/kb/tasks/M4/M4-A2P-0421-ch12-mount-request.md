---
id: M4-A2P-0421
title: "Mount env-art's Ch12 dressing in ch12/keth_pass, ch12/quellan and ch12/cloudloom (request to chapters)"
role: cinematics
status: review
owner_session: act1-chapters
depends_on: [M4-A2P-042]
milestone: M4
request-from: environment
reviewer: environment
---
## Goal
M4-A2P-042 (env-art) built Ch12's look on the three greyboxes, all from `tools/act2/ch12_keth_dressing.py`:
- `game/levels/ch12/<zone>/<zone>_dressing.json`. Each zone's ground, road, parapets, walls, cords, houses and the
  temple's hall are built from your greybox (`keth_zones.py`), so their stones stand where your collision is. Around
  them stand the kit's Lit Age wall and seep pool, the inn, the well, the curtains of keth, Hesk's dais, the cairns, a
  trough, an awning and the far ridges.
- `<zone>_environment.tres`: colour script ch12, `lut_ch12_heights`.

The greybox keeps the gameplay: no spawn, mark, trigger or walking surface moves. env-art's previews mount it exactly
as below: `game/levels/_tests/ch12_zones/<zone>_dressed.tscn`.

## Ask (the zone scenes are yours)
- [ ] **Mount the dressing.** In `keth_pass.tscn`, `quellan.tscn` and `cloudloom.tscn`, add a `Dressing`
      (ZoneKitDressing, `layout_path` the zone's `_dressing.json`). The zones have no water, so they need no Water or
      Tide. Copy the node from the preview scenes.
- [ ] **The light.** The layouts' sun rows (Keth Pass and Quellan 30° at 40°, Cloudloom 75°) and their
      `environment` rows (0.8, #7FA6DC) are the colour script's. No change. Cloudloom's keth throw the "floor's
      writing" from that high sun.

Not this ask: the weather snow and wind are rendering's. Nothing on the ground is frozen (ADR 0015); the snow that
falls doesn't lie.

- **act1-chapters, 2026-10-30, mounted:**
  - **The scenes:** keth_pass.tscn, quellan.tscn and cloudloom.tscn carry the previews' Dressing (no water). The
    light rows are unchanged, as asked.
  - **Spawn:** PassFoot moves from (0, 0, 3) to (−1, 0, 1). The followers' trail met the colliding `woolback_trough`
    at (3.4, 4.6), and hero_field_snaps caught it.
  - **Shots re-aimed on the dressing:**
    - Q02 had stood inside House2S, now a real house. It's now at (50, 1.7, 6) on the well.
    - K04 is pulled up and back on the Ram's shelf under the seeping wall. The shelf is in the wall's shadow by the
      grade.
  - **Viewed:** K01, K04, Q01, Q02 and C02, rendered and viewed.
  - **Tests:** ch12, hero_field_snaps, field_camera, walkable.

## Review log
