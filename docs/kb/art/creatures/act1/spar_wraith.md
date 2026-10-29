# Spar-Wraith (`spar_wraith`), Ch4 boss

**Idea.** Undertow-spawn tangled in the dead trader's rigging (act_outline Ch4). It came aboard in the Rising and the
rigging held it: now it **wears** the rigging. A long, many-jointed black body hangs in a web of shrouds and ratlines
between two broken spars it uses as limbs, a ship's block-and-tackle swinging from it. It is fought on the deck, under
it. One exaggeration: the rigging as its body.

**Silhouette.** 3.4 m tall, hanging: a dark shape in a web of lines, two long spars angled down to the deck like a
mantis's legs. The rigging lines are the read: nothing else in the game is a silhouette of ropes.

**Palette.** Body `lacquer_black` wet; rigging `timber_weathered`/`sand_cloth` hemp, tarred black near the body;
spars `timber_weathered`; wounds `spawn_wound`. Its changing elemental weak points glow in turn on three knots of the
web (the art is the knots; the colour per element comes from the VFX).

**Clips.** `idle`: it sways in the web, lines tightening and slackening. `attack`: a spar stabs down. `cast`: the web
draws taut and the body rises into it. `hit`: it jerks in the lines. `ko`: the lines part one by one and it drops to
the deck. Rig: a body chain, two spar arms, a dozen line bones. Budget ≤ 18k (raised by M3-CRB-005, below).

## The two phases (m2-slice act1_ch04 §5, built 2026-10-24)

- **Shrouded** (phase 1): its own sail-membranes, a torn and tarred canvas, wrap the body (`Shroud`, its own mesh,
  two-sided, rotted through in rents, with a ragged hem short of the head). Fire is the weak point there; the burn
  is VFX.
- **Hauled Down** (`hauled_down`): the shroud goes at once (`hide`), `phase_drop` (1.6 s) drops the body out of the web
  onto the deck while the spars stay planted, and the sea it hauled up its lines then sheathes it (`Sheath`, a
  streaked water skin, `show_after`). The head stays bare. On the deck it idles on `idle_deck` and strikes with
  `attack_deck`, `cast_deck` and `hit_deck` (the base clips played from the deck pose, mapped by the phase's
  `clips`). 8.0k triangles in all.

## Final pass (M3-CRB-005)

ADR 0041 (Act I at final quality). The model now builds the sheet's forms instead of primitives
(`assets_src/creatures/spar_wraith/build_spar_wraith.py`):

- **The spars** are a snapped mast and its partner: tapered, hewn eight-sided timber (flat-shaded adze faces, dents),
  silvered by salt on top and browner, wetter and tarred low down, two long checks, three iron bands with bolt heads
  bleeding `laterite` rust below them, cleats on the outboard face (one with a line made fast in figure-eight turns and
  a hanging bight), a fid hole under each break, splintered salt-pale `bone` tops with loose splinters, the butts sawn
  flat on the deck. A broken yard is lashed across the right (-X) spar and sticks out toward the battle camera, a frayed
  line hanging off its end. Lines are belayed round both spars in tight turns.
- **The rigging** is laid three-strand rope of every thickness, sagging under its weight, pale hemp (`sand_cloth`,
  salt-crusted) going to tar black toward the hub and the body: four shrouds set up on wooden deadeyes (three holes,
  a lanyard) and iron chainplates bolted to the deck; a ratline ladder on each flank (one rung on the +X side parted,
  both ends hanging frayed); a stay lashed through the hub between the spar tops and turns hitched round the tail;
  lines from the belays to the body (blended to both bones, so they stretch when it moves); long lines from the spar
  tops to ring bolts aft; broken lines hanging frayed from the hub and the left spar; a line spiralling down the upper
  body. **The three knots** are big monkey's fists (three sets of three turns, each set over the last so the weave reads,
  the crossings shaded), pale and salt-white, a faint `spawn_wound` heart showing between the turns; each has a frayed
  tail. **The block-and-tackle**: two squared blocks with iron strops, brass sheave pins and the sheave in its slot,
  three falls, a frayed hauling part, a hook (the lower block is its own bone, `tackle`).
- **The body** is chitin over wet skin: eight telescoping plates (a lip rolled toward the tail, crusted with dried
  brine for the night read; a dorsal keel; lateral flanges with a spine at each rear corner; hooks down the keel;
  pitted and scratched), paler slate sternites in front with a midline groove, a soft pleural seam between back and
  belly plates, wet teal-dark membranes between the plates, no two plates quite alike. A hooked tail spike is lashed
  into the hub. Four jointed limbs (coxa, femur, tibia, a hooked tarsus with a thumb hook, spurs at the joints, pale
  membranes at the joints): the upper pair grip the spars, the lower pair hook through the shrouds.
- **The seams** (the weak point, ADR 0151): where the membranes split they are open, recessed, lipped seams glowing
  `spawn_wound` from inside. Four: the largest between the fifth and sixth plates, running across the front and round
  the -X flank (the boss-intro camera looks at the front; the battle camera's flank is -X with the stand-in's 90 degree
  yaw), two small ones on the -X flank and near the neck, one on the back. `vfx_wound` sits on the largest, on the front
  toward -X.
- **The head** is wrong: a long dark skull with a crest of spines and neck rings, and on its front a pale, blank mask
  in two curved halves with a skinned-over socket in each (no eyes), split down the middle by the mouth: a seam that
  glows from inside and runs on under the chin and down the throat, lipped, with a hooked mandible at each lower corner
  of the mask and small palps behind. The head is 1.3 times its old size.
- **`Shroud`** (phase 1): torn, tarred sailcloth wrapped round the back and both flanks and open in front (toward the
  party), gathered and lashed at the hub, flaring toward the hem: seven panels with doubled seams, faded per panel and
  stained, a reef band with its reef points hanging, a bolt rope down each free edge with brass grommets, rotted rents
  edged in tar, a ragged hem with long tatters; two-sided. **`Sheath`** (phase 2) now follows the plates' profile, so the
  plates show through the streaked water skin.

**Materials:** carapace less glassy (roughness_wet 0.2, clearcoat 0.55, stronger detail bump), emission 2.8; rim sheen
on rope (0.5), sail (0.6) and timber (0.3) so the pale hemp, cloth and salted wood keep an edge on the night deck.

**Clips:** `idle`, `ready` (new: drawn up into the web, twitching, the head raised to the party; a loop), `intro` (new,
2.8 s: curled slack low in the web with the spars lifted, the spars come down and plant, the lines snap taut and haul
it up, it uncurls and lifts its face to the party, and settles on idle's first frame), `attack` (contact 0.8 s,
unchanged), `cast`, `hit` (peak 0.1 s), `ko`, `phase_drop` and the deck clips (`idle_deck`, `attack_deck`, `cast_deck`,
`hit_deck`), plus the kit's `hit_b` and `idle_b`. In the deck clips and the KO the tackle swings aside, the head turns
up and the body lifts the least it takes to lie on the deck (common/grounding.py).

**VFX anchors** (unweighted bones): `vfx_wound` (on the largest seam, under `body2`), `vfx_core` (the body's centreline
at mid-length, under `body2`), `vfx_phase` (the upper body, where it tears out of the web and drops, under `body1`).

**Budget:** 17,983 triangles (15,633 body, rigging and spars; `Shroud` 1,642; `Sheath` 708), so the budget is now
**≤ 18k** (a boss may take 25k). GLB 1.84 MB.
