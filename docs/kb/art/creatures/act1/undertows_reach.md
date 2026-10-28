# The Undertow's Reach (`undertows_reach`), Ch8 boss (with the PC GPU session)

**Idea.** A colossal limb of the storm reaching over Corrow's seawall (act_outline Ch8: multi-phase, scripted escape;
the wall falls anyway). The storm itself is Rendering's (the Undertow shaders). The creatures track builds the
**near part**: where the limb comes over the wall-head, a lashing mass of black water, wreckage and spawn bodies
fused together, with held-glimmer wounds the size of doors. Its far body is the storm VFX.

**Silhouette.** It fills the top of the battle frame: a curved column 8–10 m high coming down out of the storm, its
end splitting into grasping fingers of water and wreck. Phases: its fingers (targets) break away one at a time.

**Palette.** `lacquer_black`, `storm_slate` water, `abyss_navy`; wounds `spawn_wound`; motes `glimmer_held`.

**Coordination.** A joint task with the PC GPU session (the storm limb's shader, rain and lightning). Art makes the
mesh, rig and the finger `break_parts`; Rendering makes it water. Budget ≤ 24k (one per scene).

## Built (M3-CRE-06, 2026-10-24): first pass, per m2-slice act1_ch08 §5 and §9

- **Form.** A forearm of black water about 16 m long and 3 m thick, coming down over the top out of the storm behind
  the parapet and flaring where it breaks into a **six-fingered** grip of spawn-crust on the wall-head (six, so it never
  reads as a man's hand). Four broken spars are driven through it, and two drowned spawn shells are half sunk in it. Two
  door-sized `spawn_wound` wounds face the party. 10.9k triangles (budget 24k), 25 bones.
- **States** (creatures.json `phases`; the ids `dark` and `breach` are placeholders until m2-slice names the phases in
  enemies.json): the Grip is `idle`; the Dark is `phase_dark` → `idle_dark` (the hand lifts off the stone and hangs
  over the wall-head, closing slowly); the Breach is `phase_breach` → `idle_breach` (it lets go and draws back over the
  sea, the hand raised and open, gathering).
- **Clips.** `attack` (Crust Slam: lift and slam, contact 1.2 s), `cast` (Undertow Pull / Close the Hand: the fingers
  rake back and close, 1.3 s), `hit` (a shudder up the limb), `ko` (drawn back up into the storm; never used by the
  design, kept for safety).
- **For the PC GPU session:** the materials (`water`, `crust`, `wreck`) are creature-shader stand-ins. The forearm's
  vertex data carries the wound mask in the emission channel and a streak pattern in the albedo. Swap the `water`
  slot for the Undertow look whenever it suits; the mesh and rig won't change shape under you.
- **Phase strikes (fixed 2026-10-24):** the Dark and the Breach play their own strikes from their pose
  (`attack_dark`, `cast_dark`, `hit_dark`, `attack_breach`, `cast_breach`, built by adding the phase pose to the
  base clip), mapped by each phase's `clips` in creatures.json, so nothing snaps back to the Grip.

## Final pass (M3-CRB-007)

ADR 0041 (Act I at final quality). The model now builds the sheet's forms instead of primitives
(`assets_src/creatures/undertows_reach/build_undertows_reach.py`):

- **The forearm** is a rope of six twisting water strands (deep grooves between them, each strand its own girth),
  with diagonal surge folds riding the strands (foam-pale on their crests), streaks stretched along the flow, pale
  `storm_slate` stretches in the `abyss_navy` / `lacquer_black`, and `deep_teal_shadow` depth. Three strands peel off
  it and rejoin. Past the bones' curve it turns up into the storm as a narrowing, twisting spout, mist-pale
  (`overcast_slate`) toward its tip, where the storm VFX takes over (an earlier ragged crown read as a second fist in
  the intro; it is kept compact because the boss-intro camera fits the model's bounds and its title-card test fails
  on a taller model).
- **Wreckage fused into it:** two broken octagonal masts with iron bands and splintered pale ends (mast A's short
  end under a cap block, a chain draped from it over the arm; mast B carrying a yard, rope lashing at the crossing, a
  loose rope end and a drowned brass lantern, clouded and unlit), half a ship's wheel sunk in the -X flank (hub, a
  broken rim, turned spokes, three snapped short), three hull planks with nail heads, and rope wound round the wrist.
- **Two drowned spawn bodies**, half swallowed (the water piles round them): seven overlapping tergites with a keel
  and pleural spines, a blunt head shield with dead milky eyes and hooked mandibles, legs curled against the water.
- **The wounds** (the weak point, ADR 0151) are door-sized open seams (3.0 × 1.35 m and 2.4 × 1.05 m): recessed half a
  metre, two layers of rolled, torn lip (pale at the tear), bruised water round them, dark flesh strands across the
  split and the `spawn_wound` light coming up between them along the middle. The larger faces the party, turned
  toward the battle camera's flank (the stand-in's 90° yaw shows it the model's -X side; the review stage's
  three-quarter view sees +X and the smaller wound).
- **The hand:** a broad palm of water whose strands fan into the knuckles, under keeled crust plates. Six long jointed
  digits: a water core (three twisting strands, knuckles swelling at each joint, creases under them) under three
  overlapping crust plates each (keeled, growth-ridged, the side edges notched, the trailing edge serrated, worn
  pale at the rims, salt-crusted), keel spurs, barnacles, and a hooked crust claw at each tip gouging into the stone
  (the digit tips now stand at y 0.45; the claws reach y -0.29).
- **Battle read:** in the default battle camera the hand fills the frame next to the party (checked with a local,
  uncommitted shot), so most of the budget is in the digits; the forearm is seen whole only in the boss intro.
- **Materials:** `water` `wet_darken` 0.55 (was 0.2, which crushed every vertex colour to black); crust and wreck
  carry more detail. Slots unchanged (`water`, `crust`, `wreck`); Rendering may still swap `water`.

**Clips:** all of the first pass's (`idle`, `attack` contact 1.2 s, `cast` 1.3 s, `hit`, `ko`, `phase_dark`,
`idle_dark`, `phase_breach`, `idle_breach`, `attack_dark`, `cast_dark`, `hit_dark`, `attack_breach`,
`cast_breach`, unchanged) plus `ready` (new, a 2.0 s loop: the grip eases off the stone, claws lifted, the fingers
flexing, the limb surging faster) and `intro` (new, 2.8 s: it comes down out of the storm over the parapet with the
hand open, slams its grip onto the wall-head at 1.32 s with the limb whipping after it, clenches, and settles on
idle's first frame; it starts 11 m above its rest, out of the top of the frame), and the kit's `hit_b` and `idle_b`.

**VFX anchors** (unweighted bones): `vfx_wound` (in the larger wound, under `arm3`), `vfx_core` (the forearm's
centreline mid-way, under `arm2`), `vfx_phase` (the wrist, where the grip breaks, under `hand`).

**Budget:** 23,966 triangles (≤ 24k): forearm 5.0k, peeling strands 0.6k, palm 1.8k, digits 12.0k, wreckage 2.7k,
spawn bodies 1.8k. 28 bones.

## Polish (M3-CRB-007, 2026-10-28)

In the default battle camera the hand is right next to the party, and the digit and palm crust plates showed hard,
flat facets with harsh specular planes. Fixed in `crust_plate` without new triangles:

- **Shading.** Each plate's broad face is one smooth-shaded surface with its own normals (refined from K rings to
  about 1.5 K, two more columns across, from a smooth Catmull-Rom of the plate's path). The rim is a separate wall
  from the face's edge down into the part beneath (the old inner shell and end caps are gone), so the edge stays
  crisp while the face reads as curved shell.
- **Form.** The face domes across and along (tapering at the ends), the keel is softer, the growth ridges are lower
  (kept in colour and cavity), the per-vertex random lumps are now a smooth interpolated field, and the face rolls
  over into the rim. The side edges are notched by angle, so the silhouette breaks without kinking the shading.
- **Surface.** Two-tone granular mottle (pale grains, black pits), lighter growth bands, a crusted slate lift off
  the lacquer black, and salt in the grooves. Wetness pools in the grooves and low ground, and the crests, keel, ends
  and rim are dry. The rim wall is pale and worn at the lip and dark and wet at its foot. `crust` material:
  roughness 0.8 dry / 0.32 wet, specular 0.35, clearcoat 0.3, detail scale 12 / albedo 0.38 / bump 2.0 (was 0.45 /
  0.15 / 0.5 / 0.8, 5 / 0.3 / 1.2). Claws, spurs, barnacles and the drowned spawn bodies share the slot.
- **Budget and bounds.** 23,978 triangles (≤ 24k; palm plates +48, digit plates -36). The bounds are unchanged
  (min x -3.802 against -3.805), so the boss intro framing and its title-card test are unaffected.
