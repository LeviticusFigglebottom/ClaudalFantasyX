---
id: M2-ENV-08
title: The village-to-causeway-head route and the village props at final quality (kit pieces + swap-in layout)
role: environment
status: doing
owner_session: "env-art"
depends_on: [M2-ENV-06]
milestone: M2
request-from: lead
reviewer: rendering
---
## Goal
The Lead's env-art queue item 5: the slice's one route between the village and the causeway head at final
quality. Haluna's layout (`game/levels/ch02/haluna/haluna_layout.json`, m2-slice) dresses houses, walls, the
dock and palms, but none of haluna.md §1.2's props and none of §2.2's causeway pieces exist, so the walk from
the lanes to the causeway head (the wake-shell wall, Osu, the save shrine) is bare sand.

## Acceptance criteria
- [ ] Causeway-head kit (haluna.md §2.2, Environment-owned): causeway slabs (flat 1.2 x 2.4 m, tilted/broken,
      sunk, slab steps), coral boulders (0.5–3 m, seeded, barnacle/algae bands per §4), pilgrim marker posts
      (2.4 m, shells and faded cloth strips; a leaning and a broken variant), the half-buried Lit Age ring
      (3 m, a faint `glimmer_bound` glint in a crack), a wreck rib.
- [ ] Village props (§1.2): water jars, baskets, an oil lamp post (2.2 m), a fish-drying rack, a salt-glass
      net-float cluster, a market stall frame (for the existing awnings), sandals by a doorway. Reuse the shrine
      kit's leaf-boats (M2-ENV-03) rather than building a second set.
- [ ] Each piece: LOD0/LOD1 within a budget, chained LODs, vertex-colour weathering, PROVENANCE rows,
      `verify_blender_builds` byte-identical.
- [ ] A swap-in note for m2-slice: the exact `haluna_layout.json` entries (piece, position, yaw) that dress the
      route from the north lanes to the causeway head, plus collision `piece_rules` for the new pieces.
      Previewed in an Environment-owned scene (not m2-slice's) with at least one composed view, viewed.

## Review log
