# Shoal skipper (`shoal_skipper`), Ch6 Brine Shoals

**Idea.** A mudskipper grown to a dog's size on the mud-flats of the Brine Shoals, its skin crusted with dried salt.
It hops on its fins, gulps air, and goes for ankles. A beast. One exaggeration: scale.

**Silhouette and palette.** 0.9 m long, 0.5 m high, a big bulbous head with eyes on top, propped on its front fins,
a tall spined dorsal fin. Skin `sand_wet` mottled with `foliage_shadow`, salt crust `mortar_white` patches, the
dorsal edged `lacquer_red_deep`; weak point a `spawn_wound` gill.

**Clips.** `idle`: gulping, the dorsal fin flicking. `attack`: a hop-lunge. `cast`: dorsal raised, a display. `hit`: it
flips back. `ko`: it flops onto its side. Budget ≤ 5k.

**Final quality (M3-CRE-654, ADR 0041).** The first build read primitive at review distance: a smooth tube, ball eyes
on stalks, block fins, stick legs. What changed, within the 5k budget (1,644 to 4,952 triangles; the bones, the clip
names and the contact time are unchanged):
- **Head and body:** one loft with a blunt, wide, boxy head (a superellipse section, a rounded face) tapering to a
  laterally flattened tail; cheeks swell over an operculum crease.
- **Mouth:** a dark mouth line runs round the front of the snout and splits the lower jaw from the upper lip. The
  head's lower-jaw vertices ride the `jaw` bone, so the line opens. The clips' jaw keys now open it with a positive
  turn: a small gulp in `idle`, a gape at the bite, a slack jaw in the KO.
- **Eyes:** goggle eyes set in raised sockets on the head top, each with a lid fold round it. The eyeball has a gold
  (`dusk_gold`) iris and a level dark pupil.
- **Skin:** `sand_wet` and `timber_weathered` mottled with `foliage_shadow`, dark `lacquer_black` blotches, pale
  `sand_dry` speckles and a pale belly. Dry `mortar_white` salt crust on the back is matte and in its cavities; the
  rest is wet.
- **Weak point:** a small closed `spawn_wound` gill mark just behind the operculum (ADR 0151's beast form).
- **Fins:**
  - the pectorals are a muscular lobe and a pleated, rayed fan planted on the floor;
  - the dorsal sail is a scalloped membrane, dark with pale spots and edged `lacquer_red_deep`, with spines running
    past its edge;
  - a low second dorsal and a rounded tail fin complete it.
