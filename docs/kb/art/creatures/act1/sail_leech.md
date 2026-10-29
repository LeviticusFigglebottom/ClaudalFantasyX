# Sail leech (`sail_leech`), Ch4 the drifting trader

**Idea.** Undertow-spawn: a flat, ray-shaped thing that clings to wet sailcloth and drops from the yards. Its back
is the wet black carapace of the spawn, but thin and flexible as leather, edged with a frill that ripples like canvas
in wind. One exaggeration: a ray that lives in the rigging.

**Silhouette and palette.** A 1.4 m-wide diamond that hangs in the air (hover 1.4 m) and ripples; a whip tail; two
small glowing eyes. Back `lacquer_black` to `abyss_navy` clearcoat; belly `storm_slate`; wound slits along the back
`spawn_wound`; motes `glimmer_held`. At battle distance: a dark rippling kite.

**Clips.** `idle`: the wing edges ripple in a travelling wave. `attack`: it drops and wraps (the wings fold over the
target). `cast`: it spreads flat and shudders. `hit`: it crumples and recovers. `ko`: it falls like a wet sheet.
Rig: a grid of wing bones (4 per side) and a tail chain. Budget ≤ 5k.

**Final quality (M3-CRE-654, ADR 0041).** The first build read as a featureless blue sheet. It is now a leech with
sails, inside the 5k budget for the first time (5,728 to 4,832 triangles). The bones (3 wing bones a side as built,
3 tail bones), the clip names and the contact time are unchanged.
- **Body:** a real leech down the middle, flattened and annulated. Each segment swells between dark grooves and its
  crown catches the light, with a faint dorsal stripe.
- **Weak point:** the four `spawn_wound` wound slits are open seams between segments (the spawn's form, ADR 0151).
- **Head:** a ribbed oral sucker under the front, opening forward and down. The two glowing eyes sit on the body's
  front, with smaller dark eyespots in an arc behind them.
- **Sails:** thin membranes either side that droop at the tips like a hanging wet sheet. Sixteen ridged battens
  radiate from the body, pleating the sail, out to a ruffled, canvas-pale (`storm_slate`) frilled edge with a dark
  hem.
- **Tail:** the whip tail is now the body narrowing to a ringed ribbon. It ends in the caudal sucker, a muscular disc
  with a thick rim and a pale ribbed cup, that it clings with.
- **The fen leech** (Act II variant) shares the build. It sets a flatter body and a slighter droop through its own
  parameters, so it stays ribbon-flat with its eyes on the body (5,980 triangles).
