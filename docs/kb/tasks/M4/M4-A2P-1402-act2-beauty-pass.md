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
- **Viewed and kept:**
  - The fen edge and Pell's mark look into a low sun, so the bank's sheen there is the backlight, not the material.
  - The Sunken Vey's landing and gallery, and Lowlight's engine hall, lamp bench and sanctum, read intact,
    cold and empty, as designed.
  - The Vey landing is sparse (a bare flagged platform and a rail). Dressing it would be new content; that's the
    Lead's call.

## Review log
