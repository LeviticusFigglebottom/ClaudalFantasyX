---
id: M2-ENV-07
title: The hero banyan and the windbreak tree at final quality (replace the two PLACEHOLDER trees)
role: environment
status: doing
owner_session: "env-art"
depends_on: [M1-ENV-03]
milestone: M2
request-from: environment
reviewer: rendering
---
## Goal
`banyan_placeholder` and `windbreak_placeholder` (assets_src/environments/kits/haluna/placeholders.py) are
honest stand-ins with cluster-card crowns, tagged PLACEHOLDER in their glTF extras and kit_manifest.json.
SPEC §8.4 allows no visible placeholders at M2. H07 is framed by the banyan's aerial roots; H01/H02 need the
windbreak rows' dark value masses (haluna.md §1.3, vegetation.md "Not built").

## Acceptance criteria
- [ ] A hero banyan (about 14 m, fused stems with buttresses, spreading limbs, aerial and prop roots, a
      broad crown of leaf-level clusters in the vegetation format) and a windbreak tree (an original
      thick-leaved coastal tree: short trunk, dense upright oval crown, `foliage_shadow`-heavy), built by
      the vegetation generators (assets_src/environments/vegetation/), with LODs chained as vegetation.md
      "One LOD at every distance" requires, and wind channels per the vegetation convention.
- [ ] The pieces keep their scene contract (or the dresser maps the old names), so Haluna swaps in with no
      layout change; the PLACEHOLDER tag and reasons are removed.
- [ ] Bark that reads in H07 (the aerial roots are not white sticks or black poles).
- [ ] haluna_h01/h02/h07 (and veg shots if touched) re-captured and viewed; drift listed for re-approval.

## Review log
