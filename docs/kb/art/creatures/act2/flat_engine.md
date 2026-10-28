# The flat-engine (`flat_engine`), Ch14 boss part

**Where:** the stern of Warden Malcor Venn's pursuit barge on Ansedra's still lagoon at night (act_outline Ch14).
In phase 1 the engine pulls the water flat and still round the party, so the timeline slows; Liss breaks it. The
Warden (a person) is the characters track's. This sheet is the machine on his barge.

## The idea

A bound Lit Age engine: a squat iron-and-brass drum on the barge's stern, half sunk through the deck into the
water, with a ring of long paddles held flat in the water like oars at rest. They are not rowing: they **press**,
fanning out on every side and laying the lagoon smooth. A salt-glass window on the drum shows its bound light,
steady (`glimmer_bound`, a construct, README rule 3). Its weak points are the paddle hinges, which glow
`spawn_wound` (ADR 0151: one small closed mark each).

The one exaggeration: **the paddles**. A real stern-mounted paddle drum, its paddles grown long and held flat,
smoothing water instead of moving it.

## Silhouette

- A 1.8 m drum on the stern deck, a short chimney with a bell-shaped cowl, and eight paddles 3 m long fanned on the
  water in a half ring astern and abeam (they lie at y 0, the water).
- **Broken:** the drum split along a seam, its window cracked dark, the paddles slack and fallen at odd angles.

## Palette

The drum `lacquer_black` iron with `brass` bands going `bronze_patina`; the window `salt_glass` with the bound light
behind it in `glimmer_bound`; the paddles `timber_weathered` darkened wet to the waterline; the hinges `spawn_wound`.
The lagoon at night is dark, so the window and hinges are its only lights.

## Battle read and clips

- **At battle distance:** a dark drum on the stern with a steady teal window, and a fan of paddles flat on the
  water.
- `idle`: the paddles press in a slow wave round the ring (a few degrees each); the window breathes very slightly.
- `cast` (the stilling): every paddle presses down together, and the window brightens and holds.
- `hit`: the drum jolts and one paddle kicks up (its peak near 0.1 s).
- `ko` (it breaks): the seam splits, the window goes dark (the shader's emission is static, so the broken mesh
  swaps in, as Hullgnaw's ribs do), and the paddles fall slack.
- No `attack`: it does not strike. The pipeline wants the clip, so `attack` is a copy of `cast`.

**Break part:** `whole` / `broken` meshes for CreatureActor `break_parts`, keyed to the charge skill that breaks it
(Liss's, once Ch14's combat kit names it; until then the creatures.json row lists no part).

Budget ≤ 8k triangles. Rig: drum, chimney, eight paddle hinges.
