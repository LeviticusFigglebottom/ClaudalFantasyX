# Cinder Matron (`cinder_matron`), Ch5 boss

**Source of the design.** m2-slice's act1_ch05 beat sheet §9 (item 14) supersedes this sheet's first version (a
seated laterite Watcher): the Matron is "a tall forge-construct, broad-hipped and matronly in outline: a copper frame
like a kiln with arms, slag-crusted, with a ladle-hand and a tong-hand, and a teal bound heart behind the slag.
Silhouette: a kiln with shoulders." Two phases: crust, then pour (the crust breaks); a re-crust telegraph; a quench
reaction to water and cold.

**Idea.** A Lit Age machine that kept Ashcrown's forge: a standing bottle-kiln of riveted brass and copper plates,
built in the shape of a matron because the forge was hers to keep. The mountain's fire still burns in her firebox,
and behind a grated port in her chest the Lit Age bound a heart (a dead soul's light) to drive her. Slag from
centuries of pours has cooled over her in a black, cracked crust. She is calm, bowed, and sad; she does not hate
the party, she is keeping the forge. Influences and their transformations (references.md rule 4): Khmer carved faces
→ her brass mask (closed eyes, open mouth, the Watchers' language, here a grille with the fire behind it); English
bottle kilns with their iron hoops → her body, given hips, shoulders, a hood and a smith's apron.

**Silhouette (3.6 m, standing, facing +z).** From the ground up: a long hip-skirt of three shingled plate courses
flaring to a hooped hem (radius 1.0 m at the hips), a belted waist, the kiln's belly in iron-hooped courses
narrowing to a shoulder dome, a broad riveted yoke with layered pauldrons (2.8 m across with the arms), and a
bell-shaped chimney-hood with a chimney stack on its crown. The head is bowed 8° at rest: she looks down at the
party. Arms hang wide of the body on ball elbows and bell cuffs; plated fists close round her tools, four fingers
and a thumb each.

| Part | Where | Read at battle distance |
|---|---|---|
| Firebox | belly front, an arched iron-framed door with grate bars, coals glowing `ember_orange` | the brightest warm shape, always visible (the crust stays clear of it) |
| Heart port | chest, a brass ring with three bars over a faceted heart `glimmer_bound` `#4FB3B0` (its own `heart` slot, steady, no pulse) | phase 1: a teal slit through the slag; phase 2: the whole port |
| Mask | the hood's opening, polished brass: a raised brow with grieving inner ends, closed eyes (downturned lash grooves), a nose ridge, an open oval mouth with a three-bar grille and the fire behind it | a calm pale face under a dark hood |
| Ladle (right hand) | a foundry ladle hanging to the floor, its bowl brimming with molten slag | an orange dish at her right foot |
| Tongs (left hand) | long smith's tongs, the jaws hooked and a little open, pointing forward | a dark forked line |
| Apron | a smith's apron of `bronze_patina` with brass trim and rivets over the skirt's front | the green panel that makes her a figure, not a pot |

**Palette.** Plates `brass` and `copper` (#A65A2A) per plate, verdigris `bronze_patina` weeping from the seams and
heavier toward the hem, soot (`lacquer_black`) above the firebox; hoops, frames, grate bars and tongs dark iron
(`lacquer_black` to `volcanic_stone`). Crust `lacquer_black`/`volcanic_stone`. Every emission except the heart is
`ember_orange`, the mountain's fire, never glimmer. **The heart is bound light** (color_script.md rule 2: machines and
Lit Age conduits use `glimmer_bound`; README rule 3's "creatures never use glimmer_bound" is about living creatures, and
she is a Lit Age machine): steady, no pulse, no motes, moving only with her body.

**Phases.** Phase 1, *crust*: the `Crust` mesh (its own node) covers the belly, the yoke, the pauldrons and the upper
arms in pillowed slag cells: each cell is its own dark dome (a Voronoi cell of even, dart-thrown seeds), inset from
its neighbours by a 3 cm crack whose floor glows `ember_orange`, so the cracks are a network of fine ember lines at
any distance and any tessellation (M3-CRE-04 polish; the first pass's two-shell underlayer read as orange patches);
a slag collar sits on her belt and ropes of slag run down the skirt's sides and back. It leaves the firebox clear
and a slit over the heart. Phase 2, *pour* (creatures.json phase `pour` hides `Crust`): the plates the slag lay on run
red-hot, with molten seams glowing in the joints, and the whole heart port shows. The
re-crust telegraph and the quench reaction are VFX and battle-presentation work (not in the model): the re-crust can
show `Crust` again through a phase `show` list.

**Clips.** `idle` (4 s loop): a slow bellows breath, the head and arms settling. `attack` (1.6 s, contact 0.85): a
ladle pour-swing; she winds the ladle back, twisting at the waist, then flings it forward and up to shoulder height so
the slag leaves the bowl toward the party. `cast` (1.8 s): the tongs raised high overhead, the head lifted, the other
arm out (the heart's flare is VFX). `hit`: a grinding shudder of the plates. `phase_change` (2 s): a hunch, then she
heaves up and throws her arms out as the crust bursts. `ko` (2.4 s): she settles onto her skirt, the head bowing
low, the tools sagging. The rig keeps the first pass's bone names (root, torso, head, arm/fore/hand l and r).

**Budget.** ≤ 24k triangles (the art pass raised it from 16k for the Ch5 boss): about 18.6k body and 4.6k crust.

**Build.** `assets_src/creatures/cinder_matron/build_cinder_matron.py` (surfaces of revolution with dense front
columns for the firebox, port and mask, shingled plate courses, pillowed crust cells), `materials.json` (`metal`,
`crust`, `heart`).

**Re-crust (m2-slice, 2026-10-24).** It is not a phase change: she stays in `pour`. The `Crust` mesh comes back
when her `recrust` skill resolves, or on a water or ice hit with `reacted: true`, and hides again when the armour
break lands. That event hook is battle-presentation's; the mesh needs nothing new.

## Final pass (M3-CRB-006)

ADR 0041 (Act I at final quality). A light pass on the closest-to-final boss; what read as primitives is rebuilt
(`assets_src/creatures/cinder_matron/build_cinder_matron.py`):

- **The slag crust** (still its own `Crust` mesh, hidden by `pour`, shown again on `recrust`) is no longer an even
  honeycomb of pillows. Its cells are thrown in a vertically shortened domain, so they come out as runs of cooled slag
  longer than they are wide, of every size (broad flows over the belly, shards toward the yoke, the belt and every
  edge), with cracks of every width. Each cell is pitted grey pumice on top, slumped low, and its downhill edge is a
  thick, glassy black lip sagging over the crack below. Only the deep cracks (about one in three, more where the slag
  is thick) still glow `ember_orange`; the rest are cold dark seams. Twelve cooled drips hang from the crust's lowest
  free lips (none over the firebox or the sight-glass).
- **The arms** are Lit Age mechanism, not tubes: three overlapping riveted plate bands per segment, each tucked under
  the one above and flaring to a darkened rolled lip; a hinged elbow (a knuckle barrel on the forearm, the upper
  arm's two cheek straps outside it, a through-pin with domed nuts); a piston linkage outboard (cylinder on the upper
  arm, rod on the forearm); the plates temper-coloured (straw, bronze, purple, blue) toward the elbow and sooted
  underneath. The fingers are three plate phalanges each with iron hinge pins at the knuckles, the thumb two plates,
  the back of the hand three overlapping plates with rivets.
- **The apron** is a heavy smith's apron of oiled leather (`tortoiseshell` to `hair_dark_brown`, its own `leather`
  slot), not a teal panel: hanging in folds that deepen toward the hem, worn pale on the fold ridges, scorched black
  toward a ragged burnt hem, turned thick edges with a running stitch of waxed thread (`sand_cloth`), four burn holes
  cut through (the skirt shows behind; one still smoulders `ember_orange`), and a riveted leather strap round her
  waist with a brass buckle at her left hip. The sheet's "green panel" read is now a dark leather panel against the
  warm copper skirt.
- **The hood** carries the chimney's heat rainbow (temper bands from straw low on the crown, through bronze and
  purple, to blue at the stack's collar, wavering) and its soot, streaked down the hood from the collar; the stack is
  heat-blued with a sooted lip. The mask stays polished and clean.
- **Rivets** everywhere are 6-triangle heads (were 30), which pays for the above: 24,836 triangles (body 18,292,
  crust 6,544), within the boss budget of 25k (was 23,858).

**The weak point** (ADR 0151, a construct: one small closed mark): a cracked **sight-glass** on her right flank
beside the firebox (angle -0.62 rad, y 1.62 m), where the review camera and the boss-intro camera (on her right) both
see it: a shallow domed glass in a screwed brass bezel on a heat-blued iron boss, three cracks across it but sealed,
the binding's cold light leaking through in `spawn_wound` (its own `wound` slot). It is smaller, lower and barless
next to the `glimmer_bound` heart port, which keeps its `heart` slot, steady. The crust keeps clear of it.

**VFX anchors** (unweighted, on `torso`): `vfx_wound` at the sight-glass, `vfx_core` in the firebox (her centre of
mass; the intro's flare), `vfx_phase` in the chest behind the heart port, where the crust bursts.

**Clips.** New: `ready` (2.0 s loop: she straightens, the head lifts from its bow, the ladle drawn up, the tongs
raised forward, a quicker breath; creatures.json `loop` lists it) and `intro` (2.6 s: dormant and slumped deeper
than her rest bow; the anvil's ring jolts through her at 0.35 s; the head lifts and the body heaves up while the
firebox flares (VFX at `vfx_core`); the arms raise the ladle and the tongs; she settles onto idle's first frame).
Kept: `idle` (the bowed, grieving rest pose), `attack` (contact 0.85 s unchanged), `cast`, `hit`, `ko`,
`phase_change`, and `hit_b`/`idle_b` from the kit; `clip_by_skill` unchanged.

## Polish 2 (2026-10-28)

The biggest slag cells on her belly front read smooth up close. The crust cells broader than 0.05 m² within 100° of
her front (five cells: the broad flows the review and boss-intro cameras see) are re-topped: a ring of 2k points
(corners and edge middles) between the centre and the rim, bubbled up and sunk into pits by noise (the pits darker,
with cavity), and two fine cracks sunk from the centre to the rim across the cell, dark and deep. +4k triangles a
cell: 24,988 (body 18,292, crust 6,696), within the 25k boss budget (was 24,836). The rng sequence of the other cells
is untouched (the crack direction is hashed), so every other cell, crack and drip is where it was. Bones, clips,
contacts and anchors unchanged.
