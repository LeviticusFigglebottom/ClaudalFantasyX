---
id: M3-ENV-103
title: "Asha's packed bag by Neme's door (B02's insert) is still a box primitive"
role: environment
status: todo
owner_session: ""
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
- [ ] A Haluna kit prop, e.g. `travel_bundle`: a woven travel bag or a cloth bundle tied for a journey, about that
      size, packed full, with a strap. It is a departure, and it should read as one. (The kit has `cargo_sacks`,
      four sacks on a pallet, which doesn't fit.)
- [ ] Tell slice-polish when it is built. Slice-polish swaps it in (haluna.tscn is ours), removes the allowlist row,
      and re-renders `slice_neme_table` and the B02_bag insert.

## Review log
