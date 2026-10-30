---
id: M4-A2P-1402
title: "Act II Ch10–Ch12 beauty pass at eye height as played: the fen, Lowlight, the Sunken Vey (the Lead, 10-30)"
role: environment
status: review
owner_session: "claude/env-art"
depends_on: []
reviewer: art
milestone: M4
request-from: lead
---
## Goal
Eye-height beauty pass on Act II's Ch10–Ch12 zones as played, keeping them beautiful-and-doomed (pillar 2).

## Acceptance criteria
- [x] Every interactable and zone-map POI still viewed (tools/act1/poi_stills.py): Ossa Fen 7, the Sunken Vey 5,
      Lowlight 5.
- [x] Defects fixed or noted.

## Notes
- **Fixed (`assets_src/environments/kits/haluna/materials.py`):**
  - The fen's reed platforms read plastic green under the fen grade; `kit_fen_reed` is now dried straw-grey.
  - The fen mud and bank used the shader's mirror-wet defaults (roughness 0.12, normals flattened).
    `kit_fen_mud` and `kit_fen_bank` now take a matte damp.
- **Ch12 (Keth Pass 6, Quellan 6, Cloudloom 4, Reedhollow 4 stills):** the volcanic crag behind every cliff block
  read as flat black masses, against keth_pass.md's "grey crags", and the road's granite read near black.
  `kit_keth_crag` takes a neutral grey tint over 1 (a cool one read blue), and `kit_keth_road` (which is also
  M_DRYSTONE) lifts a step. Reedhollow reads well. A few POI stills still face a shaded cliff from a metre away;
  that is the probe's standing spot.
- **Viewed and kept:**
  - The fen edge and Pell's mark look into a low sun, so the bank's sheen there is the backlight, not the material.
  - The Sunken Vey's landing and gallery, and Lowlight's engine hall, lamp bench and sanctum, read intact,
    cold and empty, as designed.
  - The Vey landing is sparse (a bare flagged platform and a rail). Dressing it would be new content; that's the
    Lead's call.

## Review log
