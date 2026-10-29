---
id: M3-ENV-103
title: "Asha's packed bag by Neme's door (B02's insert) is still a box primitive"
role: environment
status: review
owner_session: "env-art (claude/env-art, 2026-10-29)"
depends_on: []
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
Found in the ADR 0041 beat audit (slice-polish, self-rendered `slice_neme_table`, 2026-10-28). In B02 Neme "never once
looks at Asha's packed bag by the door", and the scene cuts to it (`@camera B02_bag`, vertical_slice.md B02). The bag
is `NPCs/Neme/Bag` in `game/levels/ch02/haluna/haluna.tscn`: a 0.45 × 0.4 × 0.28 m BoxMesh, now visible behind Neme
in B02's new close camera. `test_slice_primitives` allows it ("Neme's bag") until a model lands.

## Ask
- [x] A Haluna kit prop, e.g. `travel_bundle`: a woven travel bag or a cloth bundle tied for a journey, about that
      size, packed full, with a strap. It is a departure, and it should read as one. (The kit has `cargo_sacks`,
      four sacks on a pallet, which doesn't fit.)
- [x] Tell slice-polish when it is built. Slice-polish swaps it in (haluna.tscn is ours), removes the allowlist row,
      and re-renders `slice_neme_table` and the B02_bag insert.

## Notes (env-art, 2026-10-29; built in 2ff511ab)
- **`travel_bundle`** (Haluna kit, `props.py`): an indigo cloth bundle packed full and knotted at the top, a rolled sleeping
  mat strapped along it, two rope bands round bundle and mat, a carrying strap down the front. 0.45 x 0.40 x 0.28 m like the
  BoxMesh, **origin at its centre** (as `woven_bag`), so it drops in at `NPCs/Neme/Bag`'s transform. 648 / 36 tris.
  Built in Blender (every other Haluna piece byte-identical), with its manifest and PROVENANCE rows.
- **Viewed** beside `woven_bag` in a scratch scene (not committed): it reads as a departure, a bag tied for the road.
- **For slice-polish (haluna.tscn is yours):** swap `NPCs/Neme/Bag`'s BoxMesh for an instance of
  `res://assets/environments/kits/haluna/travel_bundle.glb` at the same transform, drop the `test_slice_primitives` allow
  row ("Neme's bag"), and re-render `slice_neme_table` and the B02_bag insert.

## Review log
