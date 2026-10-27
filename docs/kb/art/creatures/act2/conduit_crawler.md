# Conduit crawler (`conduit_crawler`), Ch11

**Where:** Lowlight temple, along its conduits. **Kind:** construct. **Role:** it **repairs** the Lamp Engine's
parts; it ignores the party until the engine is struck.

**The idea:** a Lit Age conduit-cleaning machine still on its rounds: a salt-glass shell on six brass feet, a brush
and a wiper on its fore-arms, a dim bound light inside to see by. It isn't hostile. It tends. The one
exaggeration: **it has kept working for four hundred years**.

**Silhouette:** a beetle-like dome 0.7 m long on six thin legs, the shell clear, the light inside visible; two short
fore-arms with brush heads.

**Palette:** shell `salt_glass`; frame `brass` going to `bronze_patina`; feet and joints `lacquer_black`; its light
`glimmer_bound` (steady, small: a construct, README rule 3); weak point (the shell's seam) `spawn_wound`.

**Clips:** `idle` (it scrubs at the floor, feet ticking); `attack` (a brush jab: contact 0.45 s of 1.0 s); `cast`
(the repair: it scuttles to the engine and its arms work); `hit` (it rocks on its legs; peak near 0.1 s); `ko` (its
light dims and its legs fold under it). Budget ≤ 5k triangles. Rig: body, six legs of 2, two arms of 2.
