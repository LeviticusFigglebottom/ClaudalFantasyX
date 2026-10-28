# Bottle hermit (`bottle_hermit`), Ch4 the drifting trader

**Idea.** A hermit crab that lives in a ship's **lamp glass**: the thick chimney of a deck lantern, salt-frosted, its
brass collar green. Its own small bioluminescence, trapped and magnified by the glass, makes the whole shell glow
softly. A reef beast. One exaggeration: the glass house.

**Silhouette and palette.** 0.5 m tall: the glass chimney lying on its side, the crab's red-brown legs and one big
claw out of the mouth, eyes on stalks. Glass `salt_glass` (rim sheen, a frosted roughness), collar `bronze_patina`,
crab `laterite`/`tortoiseshell`, its light `sea_glow` (not glimmer). Weak point: a `spawn_wound` spot on the soft
abdomen visible through the glass.

**Clips.** `idle`: the crab shifts in the glass, the light breathes. `attack`: claw jab. `cast`: it pulls in and the
glass flares (the reflect/ward read). `hit`: it retreats into the glass. `ko`: it slumps out of the glass mouth, the
light out. Budget ≤ 5k.

## Final pass (M3-CRB-004, 2026-10-28)

ADR 0041 (Act I at final quality) and the creatures-b critique (a toy: smooth tubes, a sphere body, a clean jar).

- **Scale.** As a boss it is now about **1.2 m** to its antennae (the glass's top at 1.0 m, 1.4 m long with a 0.49 m
  bulb): a giant hermit in a ship's big deck-lantern glass. creatures.json `stand_in` gives `height` 1.2 and `radius`
  0.75 (the effects anchors and the ring follow); the boss intro's `boss` shot frames it with room to spare.
- **The glass.** A thick (4.5 cm) chimney glass with a wobbled wall, a chip bitten out of its lip on the camera's
  side (-x) and two nicks, salt frost over most of it worn into clear windows (rough where frosted, glossy where
  clear: the vertex wetness), clusters of barnacles low on the sides and toward the neck, leafy weed lying slantwise
  down the curve and hanging. A green-bronze band with two rows of rivets and a bail lug and ring behind the lip; a
  domed brass seat with its burner boss at the neck. The crab's own `sea_glow` lights it from inside: the frost
  takes the light and glows softly, and the soft **abdomen** curled in it shows as a banded, backlit shape that
  spirals up the camera's side toward the neck (painted into the glass's vertex colour and emission, since the
  creature shader is opaque).
- **The crab.** A granular shield with a groove, side ridges and a pointed rostrum; eye stalks banded pale with
  faceted dark compound-eye caps and bristles; jointed antennae with long whips; folded, bristled mouthparts; two
  pairs of walking legs in flattened, keeled, granular segments (merus, carpus, propodus) with hard flared cuffs,
  pale joints, dark bands, spines and setal tufts, and long curved dactyls darkening to black points; one heavy
  claw (-x) with a lumpy palm, conical pale-tipped tubercles, a crest, a toothed fixed finger and a hinged dactyl
  with dark tips, and a small claw on the other side. Laterite and tortoiseshell mottle, roof-clay speckle.
- **Weak point.** One small closed `spawn_wound` mark (ADR 0151, a beast's) on the abdomen as seen through the
  glass, on the camera's side; bone `vfx_wound` sits on it (child of `glass`).
- **Anchors.** Unweighted bones `vfx_wound` (glass), `vfx_core` and `vfx_phase` (both at the crab's centre at the
  glass mouth, children of `body`; no phase, so the phase anchor is the core).
- **Clips.** `idle` (3.0 s loop), **`ready`** (1.6 s loop: up on its legs, the big claw cocked, eyes up, antennae
  forward; creatures.json `loop` lists it), **`intro`** (2.6 s: shut in the glass with the claw across the mouth, it
  hauls itself up and out, rears and raises the big claw high and snaps it while the glass rocks up and flares, then
  settles to the idle's first frame), `attack` (claw jab, contact still 0.45 s), `cast` (pulls in, the glass flares),
  `hit` (retreats into the glass, claw across, peak 0.1 s), `ko` (slumps out of the mouth, legs curled), and the
  kit's `hit_b` / `idle_b`. New bones: `antenna_l/r`, `claw_small_arm`, `claw_small`.
- **Budget.** 15.2k triangles (was 3.4k; the sheet's 5k is superseded by the boss budget, ≤ 25k).

## Polish (M3-CRB-004, 2026-10-28)

The shell and legs read glossy and plasticky, like a wet toy. Every hard-chitin part (the shield, leg segments and
spines, dactyls, claw palm, tubercles, fingers and eye stalks) now finishes through `chitin_finish`:

- a fine blotched mottle (sun-faded and darker patches) and granular pits (cavity, slightly darkened);
- a wetness gradient: dry on top, damp toward the floor and on the down-facing undersides, with damp pooled in the
  pits (the soft body behind the shield stays damp);
- pale, chalky, bone-dry salt crusted in broken patches into the joints (each segment's pale joint ends, the dactyl
  and finger roots, the wrist) and the shield's groove.

`chitin` material: roughness 0.86 dry / 0.42 wet, specular 0.3, clearcoat 0.15, detail albedo 0.2 and bump 0.6 (was
0.62 / 0.22 / 0.5 / 0.55, 0.12 / 0.45). The weed and the closed wound mark share the slot. Geometry, clips and the
15,170-triangle budget are unchanged.
