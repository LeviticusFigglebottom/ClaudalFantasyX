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
