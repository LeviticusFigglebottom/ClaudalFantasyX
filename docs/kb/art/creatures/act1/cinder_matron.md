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
arms in pillowed slag cells whose edges sink into a glowing molten underlayer, so the cracks are crisp ember lines at
any distance; a slag collar sits on her belt and ropes of slag run down the skirt's sides and back. It leaves the
firebox clear and a slit over the heart. Phase 2, *pour* (creatures.json phase `crust_breaks` hides `Crust`): the
plates the slag lay on run red-hot, with molten seams glowing in the joints, and the whole heart port shows. The
re-crust telegraph and the quench reaction are VFX and battle-presentation work (not in the model): the re-crust can
show `Crust` again through a phase `show` list.

**Clips.** `idle` (4 s loop): a slow bellows breath, the head and arms settling. `attack` (1.6 s, contact 0.85): a
ladle pour-swing; she winds the ladle back, twisting at the waist, then flings it forward and up to shoulder height so
the slag leaves the bowl toward the party. `cast` (1.8 s): the tongs raised high overhead, the head lifted, the other
arm out (the heart's flare is VFX). `hit`: a grinding shudder of the plates. `phase_change` (2 s): a hunch, then she
heaves up and throws her arms out as the crust bursts. `ko` (2.4 s): she settles onto her skirt, the head bowing
low, the tools sagging. The rig keeps the first pass's bone names (root, torso, head, arm/fore/hand l and r).

**Budget.** ≤ 24k triangles (the art pass raised it from 16k for the Ch5 boss): about 18.6k body and 5.2k crust.

**Build.** `assets_src/creatures/cinder_matron/build_cinder_matron.py` (surfaces of revolution with dense front
columns for the firebox, port and mask, shingled plate courses, pillowed crust cells), `materials.json` (`metal`,
`crust`, `heart`).
