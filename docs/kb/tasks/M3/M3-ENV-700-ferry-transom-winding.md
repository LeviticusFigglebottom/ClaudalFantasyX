---
id: M3-ENV-700
title: "Brightwater kit: bf_common.transom is wound inward (the ferry's and drowned hulls' transoms vanish from astern)"
role: environment
status: doing
owner_session: "env-art"
depends_on: [M3-ENV-08]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Found by the M3-ENV-08B worker: `assets_src/environments/kits/brightwater_ferry/bf_common.py` `transom` is wound
against its own normals (0.95 of its triangles face inward), so the ferry's transom and the derelict hulks'
transoms are invisible from astern. The Seventh Terrace builds its transom another way and is unaffected.

## Acceptance criteria
- [ ] Wind `transom` outward. Rebuild `brightwater_ferry_kit`. Only the hulls that use it may change (`ferry_hull`
      and the derelict hulks), and `verify_blender_builds` is identical after the rebuild.
- [ ] Add a winding test (most faces' winding agrees with their normals), like the corrow and oruvel kits have.
- [ ] Re-capture the Brightwater shots and view them. No current baseline sees the stern, so none should move; if
      one does, view it and give the reason before re-approving.
- [ ] Note: `bf_import_settings.py` overwrites `lut_ch04_crossing.png.import` with 2D settings. Fix the script
      so it leaves the LUT's 3D-texture import alone.

## Review log
