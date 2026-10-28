# Raid-hound (`raid_hound`), Ch6 boss pair (with the Stillguard Inquisitor)

**Idea.** The Order raid's hound: a lean coursing dog, salt-grey, bred to run down wrights on the mud-flats, in a
branded leather harness with the Order's mark. It is not a monster, which is the point of the fight (Toma refuses to
strike to kill). A beast. No exaggeration: it is a dog.

**Silhouette and palette.** 0.8 m at the shoulder, long legs, deep chest, a narrow head. Coat mud-coloured (`sand_wet` into `tortoiseshell`, m2-slice act1_ch06 §9), a red-lacquered (`lacquer_red`) muzzle cage, a
greyhound's legs under a mastiff's chest; harness `tortoiseshell` leather, the Order mark `order_marble` stamped.

**Weak point (M3-CRE-650, ADR 0151; supersedes "no weak-point glow").** ADR 0151 gives every foe a weak point in
`spawn_wound`, so the hound now carries one, in the beast's form: one small closed mark. It is an old gaff scar,
healed shut, from the mud-flat wrights it was bred to run down: a seam of light 11 cm long and 2.4 cm wide, in a
raised dark lip (`tortoiseshell` into `lacquer_black`), slanting down across the breast below the throat, a little to
its near side (its right, -x, the battle camera's side once the stage turns it to the party). There the chest faces
forward and a little to that side, so both the battle camera and the review three-quarter (+x front) see it. It is
never an open seam and never sheds motes. It shows where it is hurt, not where to kill it; Toma's refusal stands.
The `coat` slot carries the emission (#3FE0C8, 1.4, pulse 0.35 Hz at depth 0.35, the reef crab's values), and the mask
is the seam alone. Clips, bones and rests are unchanged.

**Clips.** `idle`: standing ready, weight shifting, ears forward. `attack`: a lunge and bite. `cast`: a howl. `hit`: a
yelp and a skid. `ko`: it lies down, not dead (the fight's lesson: it is beaten, not killed). Budget ≤ 7k (3.8k).

## Final quality (M3-CRE-655, ADR 0041)

The first build read crude in the bestiary portrait and the review shot (M3-CRE-652): cylinders on stick legs and a
long, horse-like head in a cage of red hoops. The hound is re-modelled on the **same rig, bone names, clips and contact
times**. The node rests are identical. Only the grounding's upper-leg corrections moved (worst 0.074 in a quaternion
component, in the KO's hind legs), because the paws changed shape. GroundedClipsTest passes with no allow-list entry.

- **Body.** A torso lofted from superellipse sections: a keel under a deep, broad chest (bottom 0.44 m), a tucked
  waist (0.61 m), an arched loin and a sloping croup, the withers at 0.87 m. Shallow rib grooves are on the barrel's
  sides, with cavity in them, behind the elbows, and in the flank's tuck. The breast is broad and blunt at the front
  (the sheet's mastiff chest).
- **Legs.** A greyhound's, sectioned across. In front: the point of the shoulder, the upper arm with the elbow's
  point behind it, a fine forearm, the wrist's knob and a sloped pastern. Behind: a heavy thigh standing out past the
  croup, the stifle, the gaskin, the hock's point and a short upright rear pastern. Each leg is skinned along its
  three bones, and its top shares weight with the chest or hips, so the shoulder and haunch don't tear in the lunge
  or the KO. Each stands on a compact hare foot: a pad with four toes, dark nails, and the sole flat on the floor.
- **Head.** A wedge: broad at the cheeks, almost no stop, a long tapering muzzle with a dark mask to a wet black nose.
  It sits over a separate lower jaw on the `jaw` bone. Dark lips, a dark-red mouth and four canines show when it bites
  or howls. Dark eyes in pigmented rims. Rose ears: thin leaves folded back and down along the skull, dark behind,
  tortoiseshell inside. They droop at rest, so the clips' ear keys (+25 howl, +40 KO) lift them to about level
  instead of into a spike.
- **The Order's harness.** A Y-harness of oiled `tortoiseshell` leather laid on the body (the straps are cast onto
  its surface, not floating hoops):
  - a neck ring round the base of the neck;
  - a strap down the breast's midline, between the forelegs, to a girth behind the elbows;
  - a back strap over the withers carrying the Order's plate: an oval of `order_marble` on a `lacquer_black` rim,
    with the Level stamped on it (a level line under a dome's arc) and a brass leash ring behind;
  - a brass O-ring where the breast strap meets the neck ring, and brass D-rings at the girth's sides.
  The straps are burnished dark at their edges. The ends at the neck ring follow the neck in the howl.
- **The muzzle cage.** A basket of `lacquer_red` bars, clearcoated: three hoops and six bars that close over the
  nose. It hangs on a leather headstall over the poll behind the ears and up the forehead, with brass buckles. Its
  lower half rides the jaw, so it flexes when the hound bites or howls.
- **Coat.** `sand_wet` into `tortoiseshell` with a darker saddle and a faint brindle on the sides. The underparts are
  pale (`sand_wet` into `bone`). Wet mud from the flats darkens the lower legs and paws (wetness 0.75–0.85) and is
  splashed on the belly. All of it is vertex colour, cavity and wetness on the creature shader.
- **Materials.** `coat`, `leather`, `eye`, and two new slots: `lacquer` (the cage and the plate; clearcoat through
  vertex wetness, which doesn't darken it) and `metal` (brass, metallic 0.6).
- **The weak point** keeps its size, colours, values and slant. On the new, broader breast its centre moved to
  SHOULDER + (-0.058, -0.05, 0.17), projected onto the chest: just beside the breast strap (1.5 cm clear) and under
  the neck ring's front (4 cm clear). Its normal faces the review three-quarter at 0.43 and the battle camera at
  0.77. It reads in both views (the battle stage in `battle_boss_intro_inquisitor`, the review shot and the portrait).
- **Budget.** Raised from ≤ 7k to **≤ 8k**, the regular ceiling (the reef crab's and the wreck crab's). It is built
  at **7,424** triangles: torso 1,280 (scar included), neck 280, head 876, jaw 300, ears 224, tail 168, legs and feet
  1,952, harness 1,276, cage and headstall 1,068.
