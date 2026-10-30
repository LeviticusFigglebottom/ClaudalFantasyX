# Hullgnaw (`hullgnaw`), Ch1 boss

**Where:** the breaking raft as the Rising tears Oruvel apart (act_outline Ch1). The game's first boss, a tutorial for
the turn-order timeline.

## The idea

Undertow-spawn: a great eel that grew **through** a sunken ship's hull. The ship's ribs ring its body like a cage
it carries; where the eel swelled between them the timber split, and the wounds bleed `spawn_wound` light. It is the
lantern eel's dark cousin: no lure, no beauty of its own, only what it took. It rises out of the water between the
raft's planks with the ribs streaming weed.

The one exaggeration: **the ribs it wears**. The eel is an eel; the ribs are a real ship's frames, oak gone black.

## Silhouette

- A thick black body rising 2.8 m in a hunched arc, then falling forward over the raft, the head low and forward.
- **Five curved ribs** round the body, spaced along it like a rib cage turned outside in, their broken ends
  sticking out past the body: a spiky, broken outline nothing else in Act I has.
- A blunt head with a lower jaw too wide for it, teeth like nails.

## Palette

`lacquer_black` to `abyss_navy` wet body (clearcoat); ribs `timber_weathered` darkened to near `lacquer_black` where
wet, with `bone`-pale salt at the broken ends; wounds between the ribs `spawn_wound` (emissive), shedding
`glimmer_held` motes (VFX). Eyes small, `spawn_wound` pinpoints.

## Battle read and clips

- **At battle distance:** a black arch hung with pale broken spars, cyan seams between them. Taller than Toma.
- `idle`: the body heaves with the swell, the ribs creak (they lag the body by a beat), the jaw works.
- `attack` (a slam): it rears back through the ribs, then falls on its target; contact at 0.8 s of 1.5 s.
- `cast`: the ribs spread like a trap opening and the wounds flare; a held breath.
- `hit`: the body flinches inside the ribs (the ribs barely move: they are dead wood).
- `ko`: it slides back down between the planks; the last thing seen is a rib going under.

Budget ≤ 14k triangles. Rig: a spine chain of 10, jaw, five rib bones (each riding one spine bone).

**Phase `breaking`** (m2-slice act1_ch01, 50% HP): the ship's frames are their own mesh, `Ribs`. `phase_break` (1.8 s)
thrashes the body while the frames burst off and fall into the water, and `hide_after: ["Ribs"]` removes them once
the clip has played. From then on it fights bare, with the wounds the frames held shut in plain view.

## Final pass (M3-CRB-002)

ADR 0041 (Act I at final quality). The model now builds the sheet's forms instead of primitives
(`assets_src/creatures/hullgnaw/build_hullgnaw.py`):

- **The body** is an eel's: a section pressed from the sides with a flatter `storm_slate` belly and a keel line down
  the back, a long low dorsal fin (torn, crushed flat under each frame, split across each seam) running onto the skull
  as a crest, a lateral line of pale pores on both flanks, skin pinched under each frame and swollen between them,
  folds bunched beside the frames and down the neck, healed welts and hull-rub scuffs, barnacle crusts (by the
  frames, on the crown, down the neck, at the waterline), and a frayed collar of weed-matted, foam-wet skin with
  fronds spread on the water where it leaves it.
- **The seams** (the weak point, ADR 0151) are open splits where it swelled between the frames: recessed, with
  swollen rolled lips, dark wet flesh at the torn edge and `spawn_wound` light coming up from the middle. Six seams
  in the four gaps; the largest, between the fourth and fifth frames on the fall of the arch toward the party, runs
  across the back and down both flanks. `vfx_wound` sits on it, on the back toward the party and the battle
  camera's flank (the stand-in's 90 degree yaw shows the battle camera the model's -X flank; the review stage's side
  view shows +X).
- **The frames** are squared oak timbers (chamfered, adzed faces, flat-shaded, a groove down the outer face where
  the doubled futtocks meet, worn paler edges, black where wet, drier on top, slimed toward the ends), each racked
  askew and broken differently (one snapped at the flank), splintered salt-pale `bone` at the broken ends, with
  treenail holes and pegs, iron spikes bleeding `laterite` rust (one left standing bent on each), weed hanging in
  ragged ribbons, and three stubs of hull planking still nailed across them, broken off both ends. All of it is the
  `Ribs` mesh on the rib bones, so `phase_break` still throws it off and `hide_after` still hides it.
- **The head** is a skull: a boxy section, heavy brow ridges over small `spawn_wound` eyes (a second, smaller
  pinpoint behind each), a crest, cheek bulges over the hinge, nostril pits, warty tubercles and wrinkles over the
  snout, three gill slits with raised flaps, a rolled upper lip, and a lower jaw wider than the skull (a lipped
  U-shaped scoop with an underbite and throat pleats) set with irregular square nail teeth, rust-stained at the gum,
  some broken, some missing.

**Clips:** `idle`, `ready` (new: coiled back inside the frames, jaw ajar, breathing fast; a loop), `intro` (new, 2.6 s:
it rears out of the water to full height, jaw wide, the frames creaking, and settles on idle's first frame), `attack`
(contact 0.8 s, unchanged), `cast`, `hit` (peak 0.1 s), `ko`, `phase_break`, plus the kit's `hit_b` and `idle_b`.

**VFX anchors** (unweighted bones): `vfx_wound` (on the largest seam, under `spine6`), `vfx_core` (the body's
centreline at the crown of the arch, under `spine4`), `vfx_phase` (the middle frame's centre, where the frames burst
off, under `spine4`).

**Budget:** 15,768 triangles (11,662 body, 4,106 frames), so the budget above is now **≤ 16k** (a boss may take 25k;
the extra 2k went to the frames' squared timbers and the head the battle camera looks at).

## Polish 2 (2026-10-28)

The neck read as a glossy tube under the battle sun (battle_boss_intro_hullgnaw). Its specular is broken up now, by
vertex data only, from the last frame to the head: the upper ridge has dried (wetness about 0.05, a little paler
`storm_slate` over the lumps), slime runs down the flanks in streaks (wet and glossy) between drier bands, and the
wrinkle valleys hold cavity, so the sheen catches along the folds and streaks instead of in one long highlight.
materials.json `carapace` roughness_dry 0.35 → 0.62, so the dry skin is matte (the wet skin, roughness_wet 0.26 and the
clearcoat, is unchanged; the chafe bands and scars, already part-dry, go a little duller with it). Triangles, bones,
clips, contacts and anchors unchanged (15,768).

## Move pass (M3-CRB-013, 2026-10-30)

Seen from the battle camera on the raft (big18): Gnaw plunged the head down into the deck, and the intro and KO rose
out of and sank into solid planks (the sheet assumed open water). All three skills played `attack`, and Coil played
the barely moving `cast`. What changed:

- **The breach** (model side, part of the body mesh on a root bone of its own, `breach`, so it stays put while the
  body goes through it): it came up through the deck and smashed it. A dark well of water 4 mm over the deck,
  stirred teal and flecked with foam round the body and black under the broken edge. Its hole is about 1.12 m in
  radius round the arch's waterline and torn further on the party side, where the fourth frame's long broken arm
  comes through. Round it are the deck's boards (running along the planks, model x), snapped across the hole: most
  prised up (it came from below), some bent down into the water, some snapped off nearly flat, a few gone; the
  broken ends are splintered pale. Weed thrown up with it floats on the water and drapes over the boards (the fronds
  that used to lie on the "water" round the collar moved here). `breach` is also an anchor for a splash.
  tools/tests/test_creatures.py `HullgnawBreachTest` holds it to the rule: at every frame of every clip, nothing goes
  under the deck except inside the hole.
- **`intro`** (2.6 s): it bursts out of the breach and runs its body out along its own arch, the way an eel leaves a
  hole. The head comes first, straight up, then over the crown and down toward the party (0-1.2 s). It rears
  roaring with the jaw wide (1.55 s) and settles on idle's first frame.
- **`ko`** (2.4 s): a death throe (it rears, jaw gaping, shuddering, 0-0.75 s), then it slides back down into the
  breach along its arch, the head last (0.75-2.3 s).
- **`phase_break`** (1.9 s): it thrashes, the frames wrench round the body and burst loose (0.35-0.5 s), then slide
  down its arch one after another, the lowest first, and go under through the breach (all under by 1.8 s). Before,
  they fell through the deck. Turns round the body are about the spine's tangent, so they never cut into it.
- **Gnaw (`attack`, contact 0.8 s)**: it coils back through its frames, the snout drawn 0.55 m back and 0.4 m up and
  the head cocked at the party with the jaw gaping (telegraph 0.15-0.64 s). Then it lunges level: the arch leans in
  and the neck straightens, so the snout runs 0.85 m out at the height it started (it ends 0.85 m past where it
  stood at idle), and the jaw snaps shut at contact. It overshoots and settles on idle's first frame.
- **Rib Lash (`rib_lash`, contact 0.8 s, new)**: it winds its body away from the camera's flank with the frames
  clenched (0.15-0.6 s). Then it whips across toward the party and camera, the head sweeping low, and the frames
  swing round the body after it like flails, peaking a beat after contact.
- **Thrash (`thrash`, contact 1.25 s, new; the `breaking` phase, frames gone)**: it whips side to side across the deck
  (0-0.7 s) and rears up (0.8-1.2 s). Then it slams its head down on the party, the jaw stopping 7 cm over the
  planks; it rebounds and settles.
- **Coil (`coil`, new, played by gnaw_coil)**: it sinks 0.2 m into the breach and winds down tight, the arch drawn
  in, the head tucked, the jaw shut, the frames wrung round it. It holds in two slow tightening breaths (about 0.95
  and 1.65 s; the buff reads best at about 1.0 s), then lets go back to idle (2.2 s).
- **`idle_b`** is authored now (it was the kit's echo of `cast`): it lifts its head, works the jaw open and snaps it
  shut, and shakes its head once (1.5 s).
- **`hit`** turns each spine bone 1.8° instead of 3° (the turns add up along the chain: the head flung 1.4 m in
  0.1 s; now about 0.8 m). Its peak is unchanged at 0.1 s.
- `cast` is unchanged, but no skill plays it now.

creatures.json: `clip_by_skill` gnaw → attack, rib_lash → rib_lash, thrash → thrash, gnaw_coil → coil; `contact`
attack 0.8, rib_lash 0.8, thrash 1.25. Every strike starts and ends on idle's first frame.

**Budget:** 17,652 triangles (13,546 body, of which the breach is 2,388; 4,106 frames). That is over the ≤ 16k above
by the breach, inside the 25k a boss may take. The body alone keeps under 16k.
