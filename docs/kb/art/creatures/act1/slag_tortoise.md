# Slag tortoise (`slag_tortoise`), Ch5 the copper veins

**Idea.** A terrace tortoise whose shell carries cooled slag from the ash-plume: black glassy crust over the scutes,
with green copper weeping from the cracks (the stair-mountain's copper veins). A beast. One exaggeration: the slag
armour. Its armour is the lesson (Kerrid breaks armour).

**Silhouette and palette.** Low and massive: 1.3 m long, 0.8 m high, a dome of crust much bigger than the tortoise
under it. Crust `volcanic_stone` glassy (low roughness), copper `bronze_patina`, skin `laterite` dusty; weak point a
`spawn_wound` crack in the crust over the neck.

**Clips.** `idle`: the head bobs out and in. `attack`: a lunge and bite. `cast`: it withdraws into the crust and the
cracks glow (a guard). `hit`: it withdraws. `ko`: it rolls onto its side, legs still. Budget ≤ 8k (raised from 6k by M3-CRE-654 to the
regular tier's ceiling, the reef crab's 8k).

**Final quality (M3-CRE-654, ADR 0041).** The first build read primitive at review distance: stump legs, a featureless
head. What changed (4,624 to 7,786 triangles; the bones, the clip names and the contact time are unchanged):
- **Crust:**
  - it skirts down past its equator over the legs, its hem low over the flanks and raised over the neck and the tail;
  - slag drips hang from the hem, and seven faceted clinker lumps are fused on the dome;
  - each plate swells to its middle and has its own cooling: mostly black glass, some a grey ash-skinned crust, a
    few rust-stained;
  - the seams are deep, with `bronze_patina` copper weeping out of them and running down in streaks;
  - it is glassy only on the plate crowns (through the wet channel: crust `roughness_dry` 0.55, `wet_darken` 0.9), so
    the seams and vesicle pits stay dull.
- **Weak point:** one short, jagged, closed `spawn_wound` crack low on the crust's brow over the neck.
- **Legs:** elephantine ringed columns, each on a round pad with blunt `bone` nails (five on the fore feet, four on
  the hind). Thick overlapping scale plates run down the fore legs' fronts, with a few on the hind legs' backs.
- **Neck:** loose skin in deep folds, with a pleated collar of skin where it leaves the crust.
- **Head:** a wedge skull under big scutes, a hooked keratin beak (worn pale at the tip) over a mouth line, a dark eye
  with a lid ring under a brow, and two nostrils.
- **Tail:** a horny spur at its tip.
- **KO:** a root lift (in `ko` only) sets the crust's skirt, drips and clinker on the floor as it rolls.
- **The scree crawler** (Act II variant) shares the build. It is rebuilt (7,786 triangles) and keeps its frost-split
  scree.
