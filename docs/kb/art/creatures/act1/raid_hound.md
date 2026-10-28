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
