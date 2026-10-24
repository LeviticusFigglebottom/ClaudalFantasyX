# Old Kerrid: Design Sheet

Owner: Character Artist (M3-CHR-05, design). Build: Character Artist (M3-CHR-05). Shaders: Rendering (the existing
`character_*` shaders; no new shader). Story source: [`story/characters/kerrid.md`](../../story/characters/kerrid.md),
with [ADR 0020](../../decisions/0020-kerrid-restaging.md) (c) as amended by [ADR 0022](../../decisions/0022-dace-imra-strangers-sweep-f.md)
(b), (g) and its sweep-G notes, [`act1_ch05.md`](../../story/beats/act1_ch05.md) B05-B07, [`act1_ch06.md`](../../story/beats/act1_ch06.md),
[`act1_ch08.md`](../../story/beats/act1_ch08.md) B15-B17, [`act1_ch09.md`](../../story/beats/act1_ch09.md) and the voice guide.
Shared conventions are in [`asha.md`](asha.md) §4.2 (masks), §6.2 (face shapes), §8 (LOD rules) and §9 (pipeline), and
the build layout is [`pipeline.md`](pipeline.md) §11-§16 (MPFB2 donor per ADR 0021, the hero layout of §12, body clips of
§13, battle scale of §14, rig guards of §16). This sheet lists only what differs. Where the story is silent, the choice
is marked **(art decision)**.

**One-line read:** a big, heavy man hunched forward as if walking into wind, under a shaggy haystack of grey-straw palm
fibre that makes him look larger and older than he is. A bare, broad, weathered face with a flattened nose and a short
grey-black beard, nothing on the head, an iron anchor-ring standing above the left shoulder and a hooked fluke past the
right hip, the left forearm wrapped black to the elbow, and a small knotted cord of faded red at the right hip. Dry
straw, iron, tar-black, faded watch-red and bone.

**Status:** M3 design target (Lead, 2026-10-24: "design sheets first"). Built on the MPFB2 hero path, as Rhen, Toma and
Ysolde. He joins at Pemakar (Ch5) and fights from Ch5 (the slag tortoises, then the Cinder Matron introduce his niche).

---

## 1. Proportions

| Measure | Value | Notes |
|---|---|---|
| Height | **1.86 m** | (art decision) "Tall and heavy": 3 cm under Toma (1.89) and 2 cm under Sefir (1.88), so he never wins a height contest. The hunch (below) takes 4 cm off his standing height on screen (about 1.82 m to the crown), and the cape makes him read bigger than both. |
| Head height | 0.251 m (**7.41 heads**) | A large, broad head on a short, thick neck. Inside SPEC §7.3's realistic range. |
| Shoulder width | 2.15 heads (0.54 m) | Heavy and sloped, a hauler's shoulders. The cape yoke adds 0.10 m each side (§2), which makes the shoulder line 0.74 m. |
| Chest depth | 1.20 heads | Deep and barrel-like, but under the cape it barely shows. |
| Waist / hip | 1.50 / 1.55 heads | Heavy, not fat: a fisher's build gone thick at forty-four. |
| Crotch height | 3.45 heads | Slightly short legs for his height, which keeps the mass low. |
| Neck length | 0.38 head | Short and thick (neck width 0.62 of head width). |
| Hands | 0.84 head | Large. Both are rope-scarred (§3); the left is wrapped. |
| Eyes | The ×1.10 rule (fissure 31 → 34 mm). IPD 66 mm. Deep squint-lines (§6). | |
| Posture | **A hunch, not a lean:** the upper back is rounded 8° forward at `DEF-spine.003`/`.004`, the head carried forward and counter-pitched 6° up so the gaze stays level, the shoulders rolled slightly in. From the hips down he is plumb and planted, feet at 1.2× the shoulder-joint spacing, knees soft 4°. | **Idle sway 0.5** of the party default: a heavy man settling, not fidgeting. **No breath** (§10): the unrisen don't breathe (bible §2). Rhen leans from the ankles (4°) and Liss crouches; Kerrid's bend is all above the waist, like a man walking into wind who has stopped walking. |

**Age:** he looks forty-four, and has for eleven years. Age in the textures (crow's feet and squint-lines at 0.6,
forehead lines 0.4, nasolabial folds 0.5, through the villager age layer as Ysolde's), grey in the hair and beard. **The
unrisen don't age** (bible §2), so nothing about him is weathered *further* than a living sea-captain of forty-four
would be: no corpse cast, no grey skin. The only hint (art decision) is a skin albedo **6% less saturated** than a living
Corrow fisher would be (§6), which nobody should notice before Ch15.

---

## 2. Silhouette from Three Angles

**Read test:** in the flat-black silhouette view at 64, 128 and 256 px he must be identifiable against Asha, Rhen,
Toma, Ysolde and Liss, against Sefir, and against Pell ([`pell.md`](pell.md)), at dialogue scale and at battle scale
(LOD1, §2.5).

| Against | Their read | Kerrid's read |
|---|---|---|
| Asha | Staff line above the head on her right, pale sleeve flag, braid over the left shoulder, A-line skirt; upright and still. | **No pole.** Nothing rises above his head. A ragged-edged mound from the shoulders to the backs of the knees, hunched; the iron ring stands *below* the crown, above the left shoulder. Mid-value straw top over a dark lower body. |
| Rhen | Forward lean from the ankles, lantern bulb over the **right** shoulder, crossed hooks, short jacket, bare right arm. | Bent at the upper back, not the ankles. The round shape over a shoulder is a **ring** (hollow, iron, 11 cm) over the **left** shoulder, never a solid bulb on the right. Long fibre to the knee behind, where Rhen is short-jacketed. |
| Toma | The widest *clean* trapezoid, upright, a red pauldron lifting the left shoulder, a shield disc on the back, a spear rising above the head. | Almost as wide (0.74 m against Toma's 0.72 m plus the shield), but **ragged at every edge** (hanging fibre), sloped not squared, hunched not upright, and nothing above the head. From behind: a shaggy vertical mound with a blade across it, not a patterned disc. |
| Ysolde | A narrow very dark column with a winged collar, hair pin centred over the head; plumb. | Twice her width, mid-value at the top, and bent. No collar near the face: the fibre stops at the base of his neck (§4, layer 6). |
| Liss | Small (1.56 m), a crossed X harness on the chest, a bright metal left sleeve, a box at the right hip, coat tails, one hair tail. | 30 cm taller and twice as broad. His chest rope is **horizontal** (two parallel turns), never an X. His left forearm is dark cloth, not bright metal, and stops at the elbow. |
| Sefir | Tall, slender, pale, plumb and motionless; a gilded disc behind the head; a gold half-mantle on the right shoulder. | Dark-bottomed and mid-toned, broad, bent, swaying slightly; nothing behind the head; no gold anywhere. (Kerrid stands with his back to Sefir in Ch6, so their shapes meet back-to-front in that frame: Sefir's disc against Kerrid's shaggy back, §2.4.) |
| Pell | 2.30 m, the thinnest shape, a long forward S of neck with a crest on top, a thin staff higher still on his left. | The lowest, widest shape in the party next to the tallest, thinnest one. Their Ch9 two-shot (B09) is the party's two outsiders side by side: a haystack and a heron. |

### 2.1 Front (0°)
- **A ragged dome on a dark base.** The cape yoke rounds over both shoulders and stands 10 cm out past each deltoid, its
  fibre ends hanging to 12 cm below the shoulder joint; behind the arms, the back tiers show past both sides of the
  torso down to the backs of the knees, so from the front he reads as a big straw mound open down the middle, with the
  arms and the dark body between its edges.
- **The face is completely clear.** The yoke's neck edge sits at the base of the neck, **at least 4 cm below the jaw line
  all round** (ADR 0020 (c) and its IP watch: no mask, no high collar). His bare broad face, the grey of the beard and
  the cropped hair read cleanly against the straw behind.
- **The anchor-ring** of the cleaver's pommel (§4, item 11) stands 14 cm above the left shoulder's top line, just
  outboard of the neck, a hollow iron circle 11 cm across. The **fluke's hook** shows past his right hip behind him, a
  dark crescent 26 cm long breaking the cape's right edge at the hip.
- **The chest rope:** two parallel horizontal turns of old rope across the yoke's open front at 10 cm and 16 cm below
  the collarbones, knotted at the left of the sternum. The only horizontal lines on him besides the belt.
- **Asymmetry at the arms:** the left forearm is a dark column from knuckles to elbow (tarred wrap); the right forearm is
  bare skin with the paler rope-scar spiral (a texture read at 256 px only). The **watch cord** hangs from the belt at
  the right hip, three knots of faded red to mid-thigh, a small warm accent against the dark trousers.

### 2.2 Three-quarter (45°, his left side toward camera: the hero angle)
- The **left** side carries the read: the anchor-ring above the shoulder, the wrapped forearm toward the lens (the Ch8
  stair-foot shot's "wrapped left arm toward lens" and W24's hand on Rhen's collar are both this side), and the yoke's
  left edge stepping down over the shoulder in two layered tiers.
- The hunch shows: the head forward of the chest, the back rounded under the fibre.

### 2.3 Profile (90°)
- **The hunch is the profile:** a rounded back under a thick layer of fibre (8-14 cm deep), the head forward of the chest
  line by about 7 cm, the face level. From the hips down a plumb, planted line.
- The cleaver crosses the back diagonally (ring up behind the left shoulder, hook down past the right hip), so in
  profile the ring shows above the shoulder line and the fluke's hook below the back tier's edge on the far side.

### 2.4 Back (180°, field walking: he always walks last)
- The back is **all fibre**: a shaggy mound from the neck to the backs of the knees, split at the centre below the waist
  (§4, layer 7) so it follows his stride. Across it lies the **anchor-cleaver** on the diagonal, iron-black on straw,
  from the ring above the left shoulder to the hook at the right hip: the strongest line on his back.
- **Read test (64 px):** a dark diagonal across a ragged straw mound. This is the shape at the end of every line of
  march in Act I (Ch5 B05 and B07, Ch9 D03), and the shape Sefir's eyeline rests on in Ch6.

### 2.5 Battle scale (LOD1 at 6 m; pipeline.md §14)
At battle framing he is about 70-90 px tall. What must survive: the mound outline with a ragged edge (LOD1 keeps the
fringe as alpha cards, not as a smooth shell), the hunch, the cleaver held low in both hands with the hooked head down
near the right foot (§10.3 `ready`), and the dark left forearm. In the formation lineup he is the widest low shape;
Toma is the widest *upright* shape with a pole, Pell the tallest thin one. Check in `kerrid_silhouette_lineup` with all
seven party members at battle scale, plus Sefir.

---

## 3. The Asymmetric Hallmark: the Wrapped Left Forearm and the Rope-Burns

The story gives three marks of his death on the stair, and the design keeps them all on the arms (ADR 0020 (c): no
face scars, no eye effect).

- **The rope-burns (both arms, his death-wounds):** a spiral scar from the heel of each palm to the elbow, as a rope
  runs when it is held while it slides: three turns per forearm, the band 2.2-3 cm wide, raised 0.6 mm in the normal map
  with a glossy, hairless surface (roughness −0.15) and a pale, slightly pink-grey colour (`skin_kerrid` lifted 14% in
  value, saturation −30%). The palms carry the deepest part, a burn across the four finger pads and the heel of the
  hand. They never healed: the edges stay sharp, never softened like an old scar.
- **The left forearm is wrapped** from the knuckles to the elbow in **tarred hauling-cloth** (story sheet; ADR 0020 (c)):
  a 6 cm strip wound in overlapping turns, the turns running the same way as the rope did, tied off with a half-hitch
  under the elbow. The wrap stops at the knuckles, so the fingers are bare and scarred. Tar-black with a dull sheen where
  it has been gripped (roughness 0.45 on the palm side and the inner wrist, 0.75 elsewhere).
- **The right forearm is bare**, showing the paler spiral. It is the arm he holds still when he talks.
- **The light (from Ch10 only):** the burns carry an emission mask. An unrisen's light is held, so they leak a very faint
  **`glimmer_held`** `#7FC6D9` in dim scenes (ADR 0022 (g)). A material parameter `burn_glow` (0-1) drives it:
  - **0 in Ch5 to Ch9**, without exception: never in the Ch5 weir shots, never at the Ch8 stair foot, never in W24's
    hand on Rhen's collar, never in the Ch9 cutaway. The build ships with 0 as the default.
  - **0.15 from Ch10** (emission energy 0.12 at night, 0 under a key light brighter than k 1.0; a scene property, set
    per scene by Cinematics). On the left arm it leaks only through the wrap's gaps at the turns and at the bare
    knuckles.
  - **Ch15:** up to 0.6 as the motes leave his hands, sideways (color script `ch15`); the VFX sockets are in §9.
  - **H09:** a single 1.5 s lerp of the emission colour from `glimmer_held` to `glimmer_lift` (color rule 1). From then
    on every mote off him rises gold. No gold before H09, ever.
- **The watch cord (right hip):** the stair-watch captain's knotted cord (story sheet; ADR 0022 (b)): a 6 mm cord of
  faded **watch-red** with **three knots** 8 cm apart, looped through the belt and hanging 34 cm to mid-thigh. It is
  not an Order cord and carries no Order mark. He kept it deliberately, and it is the only colour on him.

**Why the left:** the left hand took the rope's full run (story sheet). It is also the hand that catches the child at
the weir (Ch5 B05: "a big hand in a wrapped sleeve") and hauls Rhen off the wall (Ch8 W24), so the wrap is what the
camera sees each time he saves someone, before anyone knows why.

---

## 4. Costume Layers and Materials

### 4.1 Layers (inner to outer)
| # | Piece | Material | Color | Mask channels | Skinning notes (M1-CHR-14 lessons) |
|---|---|---|---|---|---|
| 1 | **Smock**: a heavy hemp fisher's smock, hip length, a round neck, **elbow-length sleeves** rolled once (so both forearms show) | Coarse hemp, salt-faded | `iron_hemp` `#5B5A55` (proposed) | A 0.3 | **Dropped-shoulder sleeves** with an underarm gusset: the sleeve seam sits **12 cm below the shoulder joint**, so no armhole edge stands beside a lowered or raised arm (Ysolde's layer 5). The body of the smock rides the torso only (`DEF-spine.001`-`.004`); the sleeves the upper arm, with a 4 cm blend band at the gusset. The rolled cuff ends 3 cm above the elbow crease, so a full elbow bend (the `carry_child` clip, 110°) never folds cloth into the forearm. |
| 2 | Wading trousers, loose, to mid-calf | Tarred canvas | `tar_black` `#2A2622` (proposed) | A 0.2 · roughness 0.55 (the tar's dull sheen) | Leg tubes per thigh/shin chain (Rhen's `limb_tube`), crotch blend as Rhen's trousers. The hem rides the shin 9 cm above the ankle bone, so a flexed ankle never pushes the instep through it (FOOT_FLAT 0.5, §10.3). |
| 3 | **Rope sandals**: a plaited rope sole with a toe loop and two ankle ties | Rope | `rope_old` `#7A6A52` (proposed) | A 0.2 | **On the feet:** they take the feet's and toes' weights (as Asha's sandals after M1-CHR-14); the ties ride the ankle at 70% foot, 30% shin. |
| 4 | Left forearm wrap (§3) | Tarred hauling-cloth | `tar_black` | A 0.1 · roughness per §3 | Weighted to `DEF-forearm.L`/`.L.001` and the hand at the knuckle turn; offset 2.5 mm off the skin (it is cloth over a scar, not a sleeve). Listed under `garments` (`Wrap`). |
| 5 | Belt | Old leather, 5 cm, an iron ring buckle | Leather `#4A3020` · buckle `iron_dark` | A 0 | Torso only (`DEF-spine`, `.001`). The watch cord (layer 9) hangs from it. |
| 6 | **Cape yoke** (tier 1): the shoulder tier of the rain-cape, open at the front | Layered woven palm fibre: a woven base mat with long loose fibre ends hanging from each row (card strips) | `palm_fibre` `#A08C66` (proposed), sun-bleached tips `palm_fibre_pale` `#C2B08A` (proposed) on the outer 30% of each strand | A 0.4 (dry fibre fuzz); fibre cards alpha | **Rides the upper torso** (`DEF-spine.003`/`.004`) and the clavicles (`DEF-shoulder.L/R`), never the neck or head, so a head turn doesn't swing it. **The neck edge stays ≥ 25 mm from the neck and jaw skin** at a head turn of ±40° and a pitch of −25° (looking down the stair) / +15°, and its top is ≥ 4 cm below the jaw line at rest (no high collar). Over the shoulder the fibre ends hang to **12 cm below the shoulder joint**; the lowest 5 cm of each strand over the deltoid is weighted 50% to the upper arm, so the strands lift with a raised arm instead of the arm passing through them (the cleaver's overhead swing, §10.3). |
| 7 | **Cape back tiers** (tiers 2 and 3) | as 6 | as 6 | as 6 | **Back only**, behind the arms' swing plane: tier 2 from the shoulder blades to the waist, its outer edges reaching round to the mid-axillary line and no further; tier 3 from the waist to the backs of the knees, **split at the centre into two halves**, each following its own leg (Asha's `skirt_weights` with a left/right blend only across a 6 cm centre band) plus **3 panel bones** down each half's centre line. Not a tube: a stride, a kneel (the `ko` clip) or the Ch8 wade never drives one half through the other leg. The hem stops at the back of the knee (52 cm above the floor), so no kneel drives it into the floor. |
| 8 | **Chest rope**: two horizontal turns across the yoke's open front and round the body, knotted at the left of the sternum; the same rope holds the cleaver across the back | Old hemp rope, 2.2 cm | `rope_old` | A 0.25 | Torso only (`DEF-spine.003`). Under the arms it lies on the ribcage **14 cm below the shoulder joint** (below the 11.5 cm line), offset 6 mm off the smock. |
| 9 | **Watch cord** (§3) | Cord, three knots | `watch_red` `#8E3B2E` (proposed) | A 0.3 | 1 × 3 bones (a short pendulum, as Ysolde's cord ends). |
| 10 | Cape **wet state** (Ch8 B15 to the Ch9 dawn road) | as 6 | `palm_fibre_wet` `#5E5038` (proposed) | A 0.15, roughness −0.2 | A material variant plus one shape key `cape_wet` on the cape meshes (0 dry → 1 wet): the fibre ends hang 3 cm longer and 1.5 cm closer to the body. The scene sets both; the clips don't touch them. (`act1_ch08.md`: "a wet-state straw cape, darker, heavier, hanging closer".) |
| 11 | **Anchor-cleaver** (prop) | Forged iron: a ship's anchor fluke for the head, a forged spine, a tarred-rope grip, the anchor's shackle ring as the pommel (art decision) | Iron `iron_dark` `#4A4C4E` (proposed), forge-scale pitting, a ground edge `iron_edge` `#8E9296` (proposed) 1 cm wide · grip `tar_black` · ring `iron_dark` | ORM metallic 1, roughness 0.6 (scale) / 0.3 (edge) | **Field:** across the back on a prop bone `DEF-cleaver` (child of `DEF-spine.003`), held by the chest rope: the ring 14 cm above the left shoulder, the hook past the right hip, the blade lying **≥ 12 mm off the cape fibre's outer surface** at rest and in every field clip. **Battle:** a second instance on a `BoneAttachment3D` to `DEF-hand.R` in `kerrid_battle.tscn`, the back one hidden (§9). **Offset from the grip:** the haft sits **1.2 cm out from the right fist's centre line** (Toma's spear lesson), and the grip wrap ends 2 cm above the fist so the binding never sinks into the palm. Listed in `props` (`Cleaver`). |

**Cleaver dimensions (art decision):** 1.30 m overall. The haft and grip 0.42 m (room for two hands, the wrapped left
above the right), the blade 0.88 m. The blade is 14 cm wide at the haft, widening along a straight back edge to the
**fluke head**: a broad, slightly spooned palm 26 cm wide, curving at the tip into the **bill**, a blunt hook that
turns 9 cm toward the edge side. Thickness 1.2 cm at the spine, 3 mm at the edge. It reads massive, old and
working: an anchor made into a tool for hauling and breaking, not a sword. The ring (11 cm outer, 2 cm stock) hangs on
a forged eye at the haft's end and can turn.

### 4.2 What Kerrid does not wear
- **No hat or head covering of any kind**, ever, including in rain (story sheet IP note). A straw cape with a straw hat
  is a familiar wandering-swordsman image in this genre; without the hat he isn't it.
- **No mask, scarf, high collar or anything over the face; no eye effect; no eyewear** (ADR 0020 (c) and its watch).
- **No coat worn off one arm**, no sling, no gourd or flask (story sheet IP note). The cape is symmetrical over both
  shoulders; the asymmetry is the forearm wrap only.
- **No Order insignia, no Level, no title mark, no Stillguard red** (ADR 0022 (b)). His only red is the faded watch cord,
  under 0.5% of his silhouette.
- **No reach-bands.** He is Corrow-born, not Low Reaches (bible §5.1 has them as a Low Reaches custom).
- **No armour.** He breaks armour; he doesn't wear it.

---

## 5. Hair and Beard

- **Hair:** grey-black, **cropped short like a soldier's** (ADR 0020 (c)): 6-10 mm all over, a squared hairline at the
  forehead, slightly receding at the temples. Toma's short-card technique (pipeline.md §12, M2-CHR-04): a dense layer of
  about 550 tiny cards from Toma's `toma_shorthair.png` strand atlas (imported, not copied), plus the scalp albedo
  shadow at 60%. Colour `hair_black` `#201A16` with **25% grey strands** `#8A867E` (forty-four, a hard life), the grey
  heavier at the temples.
- **Beard:** short (12-18 mm) and full along the jaw and chin, the cheeks clean above the line, the moustache trimmed
  off the lip so the mouth shows when he finally speaks at length (Ch15). About 850 short cards **in the Head object**
  (Toma's face-hair method, pipeline.md §12: each card vertex takes the delta and the weights of its nearest skin vertex,
  deltas under 0.15 mm zeroed). Grey 35%, heaviest at the chin.
- **Shading:** primary highlight tint `#D8CCC0` at 0.25 (matte, as Toma's), `kajiya_diffuse_mix` 0.15.
- **Wet state (Ch8 B15 to Ch9):** the hair and beard roughness down 0.2 and the albedo 12% darker (a material parameter,
  shared with the cape's wet variant).
- **Motion:** none (head-rigid).

---

## 6. Face

### 6.1 Face shape
- **Broad and square** (head width 0.70), a heavy brow ridge (1.12), wide cheekbones set low, a strong jaw (1.02) under
  the beard. The face of a fisher who has squinted into glare for thirty years.
- **The nose, broken flat years before he died** (story sheet): a low, wide bridge (`nose_bridge_width` 1.18), a flattened
  dorsum and a tip with little projection (0.88), the bridge **displaced 3 mm to his left** at the break (a face-space
  deformation `nose_break` in `kerrid_head.py`, §9; it is his personal asymmetry).
- **Eyes:** **both clear** and grey (ADR 0020 (c)): iris `#6C7378`, a darker limbal ring `#4A5056`. Deep-set under the
  brow, with **deep squint-lines** fanning from the outer corners (a normal-map layer always on at 60%, to 100% under
  `lid_squint`). The lower lids are slightly raised at rest (`lid_squint` 0.10, the left 0.15: the left eye squints a
  little more, the side the light came from at the gate).
- **Brows:** thick, low and straight, grey-black with grey hairs; set close to the eyes.
- **Mouth:** wide (0.42 of head width), a thin upper lip, corners level to very slightly down (`mouth_corner_lift`
  −0.001). Mostly hidden by the beard: his smiles read through `cheek_raise` and `lid_squint` (as Toma's).
- **Skin:** `skin_kerrid` `#9A6C50` (proposed): sea-weathered brown with sun-darkening across the nose and the tops of
  the cheeks (+5% redness), salt-dry lips (roughness 0.6), the age layer of §1. **6% less saturated** than a living
  Corrow fisher (art decision, §1): not grey, not pale, just a little drained. No freckles. No scars on the face (ADR
  0020 (c)); the scars are on his arms (§3).
- **Close-range stylisation:** the ADR 0019 dialogue finish (painterly 0.6, detail 0.35, `lid_wide` 0.18 at rest) as
  every hero. Check the deep-set eyes with `lid_wide` 0.18: the squint-lines must stay readable, or reduce his rest
  `lid_wide` to 0.12.
- **Blend timing:** 0.30 s, measured, **no overshoot**. He arrives at an expression and stays there.

### 6.2 Emotion tags mapped to Kerrid's face
The 15 tags from `game/data/dialogue/emotions.json`. Weights 0-1, unlisted shapes 0, L/R as L/R. His rest
`lid_squint` 0.10 (L 0.15) is added to every row.

**His tells:** **he answers with the body, not the face** (voice guide: "he often answers with an action instead of a
line"; give him a gesture slot): before Ch15 most of his rows are small, and the clip (§10) carries the beat. **His feeling
shows in the brow and the jaw**: grief and anger both clench the jaw under the beard, and only the brow tells them apart.
**He almost never smiles before Act III**, and then only with the eyes and one cheek (`cheek_raise` L ahead of R: the
smile pulls toward the broken side). **No breath shapes:** he doesn't sigh. Cinematics should never layer a breath or
sigh on him (bible §2: the unrisen don't breathe).

| Tag | Shape weights | Kerrid note |
|---|---|---|
| `neutral` | — (the rest squint alone) | Watching the sea. Most of Act I. Nothing moves. |
| `soft_smile` | `cheek_raise` 0.18/0.12, `lid_squint` 0.12, `mouth_smile` 0.12 | The beard hides the mouth; the eyes give it. Act III mostly ("warmer, dryer, almost funny"). |
| `smile` | `cheek_raise` 0.45/0.35, `lid_squint` 0.35, `mouth_smile` 0.40 | Rare and real. E3: "Stand up straight. Your father slouched." |
| `laugh` | `cheek_raise` 0.65/0.55, `lid_squint` 0.55, `mouth_smile` 0.60, `jaw_open` 0.18 | A short, low laugh, head down 5° (never back). Act III only, at a dead man's joke. |
| `worried` | `brow_inner_up` 0.35, `brow_down` 0.30 | Barely used: his worry is a look down the line. |
| `sad` | `brow_inner_up` 0.45, `lid_close` 0.20, `mouth_frown` 0.15 | Gaze drops 6°. |
| `grief` | `brow_inner_up` 0.80, `brow_down` 0.45, `lid_squint` 0.40, `mouth_frown` 0.35, `jaw_clench` 0.45 | Reserved: Ch15 ("I got your mother up the stair. That's all I did."), Ch16 at the Choir. He holds it; no tear layer (the unrisen don't weep, art decision: a question for Narrative, §12). |
| `angry` | `brow_down` 0.80, `lid_squint` 0.30, `jaw_clench` 0.55, `nose_sneer` 0.10 | The Ch16 fury at Sefir is this face held, with no shouting (ADR 0022 (h) watch: no steel). |
| `cold` | `brow_down` 0.30, `mouth_press` 0.35 | Ch6, his back to the barge (seen only if Cinematics cuts to his face). |
| `surprised` | `brow_outer_up` 0.45, `brow_inner_up` 0.30, `lid_wide` 0.25 | Small. Ch5 P12 is **not** this: it is `neutral` with the `go_still` clip (beat sheet: "no face change"). |
| `afraid` | `brow_inner_up` 0.60, `lid_wide` 0.35 | Not used by the story; shipped for completeness. |
| `determined` | `brow_down` 0.45, `lid_squint` 0.25, `jaw_clench` 0.40 | His battle face, the Ch8 stair foot, Act III's "first down the stair". |
| `tender` | `brow_inner_up` 0.25, `cheek_raise` 0.12/0.08, `lid_close` 0.18 | Rare: E3's collar fix; Ch5's collar catch if Cinematics cuts to him. |
| `guilty` | `brow_inner_up` 0.50, `lid_close` 0.35, `jaw_clench` 0.20 | Ch15, to Rhen: "Your father reached back for me. He missed." Gaze down 15°, then makes himself look up. |
| `exhausted` | `lid_close` 0.35, `brow_inner_up` 0.15 | Head pitch −5°. The fraying in Act II (Ch15 onward), never Act I: in Act I he isn't even breathing hard. |

**Ch15 requirement (Cinematics):** the first time he uses Rhen's name should "hit like a blow" (voice guide). Stage it
on Rhen's face; on Kerrid, hold `guilty` and let `jaw_clench` fall to 0 over the name. No snap.

---

## 7. Color Callouts

Swatches marked *(proposed)* are not yet in `palette.json`; Art adds them (M3-CHR-05 acceptance) with their on-screen
values measured on the swatch card.

| Area | Swatch | Hex | Share of his silhouette (front / back) |
|---|---|---|---|
| Cape fibre (yoke and back tiers) | `palm_fibre` *(proposed)* | `#A08C66` | ~32% / ~78% |
| Fibre tips, sun-bleached | `palm_fibre_pale` *(proposed)* | `#C2B08A` | ~6% / ~8% |
| Smock | `iron_hemp` *(proposed)* | `#5B5A55` | ~14% / — |
| Trousers, left forearm wrap, cleaver grip | `tar_black` *(proposed)* | `#2A2622` | ~20% / ~6% |
| Skin (face, neck, forearms, hands, calves) | `skin_kerrid` *(proposed)* | `#9A6C50` | ~14% / ~2% |
| Hair and beard | `hair_black` + grey `#8A867E` | `#201A16` | ~4% / ~1% |
| Cleaver (iron) and ring | `iron_dark` / `iron_edge` *(proposed)* | `#4A4C4E` / `#8E9296` | ~3% / ~5% |
| Rope (chest rope, sandals) | `rope_old` *(proposed)* | `#7A6A52` | ~3% / ~1% |
| Belt | leather | `#4A3020` | ~1% |
| Watch cord | `watch_red` *(proposed)* | `#8E3B2E` | ~0.4% |
| Rope-burn glow (Ch10 on, dim scenes only) | `glimmer_held` (emissive) | `#7FC6D9` | < 0.2% |
| Wet cape (Ch8-Ch9 variant) | `palm_fibre_wet` *(proposed)* | `#5E5038` | replaces `palm_fibre` |

**No gold and no lacquer** (art decision, as Rhen and Liss): he was never part of the sacred or ceremonial world, and
his only light is held, never gold, until H09. He adds **0% gold** to any group shot.

**The straw is grey, not gold:** `palm_fibre` is a desaturated, greyed straw (saturation about 36%), well off `thatch`
`#B08A52` and off Pell's reed plait (`reed_plait` `#B3A062`, [`pell.md`](pell.md) §7), which is greener and woven tight.
Two straw-coloured materials in one party must read apart by texture (shaggy hanging strands against a tight chevron
plait) and by hue (grey-brown against green-gold).

**Watch-red is not Stillguard red:** `watch_red` is browner and duller than `lacquer_red` `#B3261E` (about 60% of its
saturation), a dyed cord faded by eleven years of sun and sea, never a lacquer. It is not counted against the
`lacquer_red_max_frame_fraction`.

**Value check:** a mid-value top (the straw) over a dark base (smock, trousers): about 40% mid, 45% dark, 15% light
(face, fibre tips, edge of the blade). From the back, about 80% mid. He sits between Ysolde (the darkest) and Sefir (the
lightest), and his value pattern (light over dark) is the inverse of Toma's (dark sash over light tunic).

**Albedo floor:** `tar_black` (Rec.709 linear luminance about 0.019) is above `lacquer_black` (about 0.010); every swatch
here keeps the floor. **Night risk:** the wet cape (`#5E5038`) in Ch8's storm-dark (16:40, spray) is close to the wall's
wet laterite. The fibre's fringe silhouette and the rim light must hold his edge; Rendering checks him in the Ch8
stair-foot framing (`kerrid_storm_ch8` shot).

---

## 8. Budgets

Sheet targets follow SPEC §7.3 (40-70k per hero). As for Ysolde, **the 5 MB GLB cap, not the triangle count, is the
binding limit**: every Head vertex carries the 40 morph targets, and the beard lives in the Head object.

### 8.1 Triangles (LOD0 target 60,000; hard ceiling 70,000)
| Part | Target | As-built expectation |
|---|---|---|
| Head and face (skin, ears, lashes, brows, mouth; donor face subdivision) plus the beard cards in the Head object | 22,500 | Toma's head and beard came in near this; watch the GLB size (§8.2) |
| Eyes | 2,216 | 2,216 |
| Visible body skin (neck, forearms, hands, calves, feet) plus the hidden legs kept under the cape tiers (M1-CHR-14) | 7,500 | |
| Scalp short-hair cards | 3,000 | Not on the Head object |
| Cape: yoke, two back tiers, woven base mats and fibre card strips | 11,000 | The fibre is cards on a shell, as hair is; never per-strand geometry |
| Smock | 2,600 | |
| Trousers, sandals | 3,600 | |
| Left forearm wrap | 900 | |
| Belt, chest rope, watch cord | 1,800 | |
| Anchor-cleaver (blade, haft, grip wrap, ring) | 2,400 | The battle instance is the same mesh, not counted twice |
| **Total** | **57,516** | Leaves 2.5k under the target |

**LODs:** LOD1 28k (from 6 m; the battle actor, pipeline.md §14), LOD2 13k, LOD3 5k. **LOD1 keeps:** the cape's ragged
edge (alpha fringe cards on the outline), the hunch, the anchor-ring and the fluke hook, the wrapped forearm, the watch
cord and the chest rope. Cut detail (inner fibre layers, sandal ties, the ring's eye), never shape.

### 8.2 Textures
| Set | Resolution | Maps | Notes |
|---|---|---|---|
| Face and head | 2K ×4 (albedo, normal, ORM, skinmask) | | As built for Rhen, Toma and Ysolde. |
| Body | 1K ×4, with a larger UV share for the forearms | | The rope-burn spiral needs ≥ 10 px/cm on the forearms (a 2.2 cm band over about 22 px), plus the `burn_glow` emission mask (a body texture's spare channel or a 512 mask). |
| Costume atlas (smock, trousers, wrap, belt, rope, cord, sandals) | 2K (ORM 1K) + clothmask 2K | albedo, normal, ORM, clothmask | |
| Cape fibre | a hero-owned fibre atlas `kerrid_fibre.png` 2K (strand bundles with tapered, split ends, alpha) and the woven base mat 1K | albedo, alpha, normal | Generated in `kerrid_textures.py` (the strand atlas method of `asha_hair`, wider and flatter strands). |
| Prop (cleaver) | 1K ×3 (albedo, normal, ORM) | | Forge-scale pitting and the ground edge as a procedural mask. |
| Hair | Toma's `toma_shorthair.png` | | Referenced, not copied. |
| Eyes | shared 1K | | |

`kerrid.glb` < 5 MB, `kerrid_lod1.glb` < 1.5 MB, every PNG < 5 MB (ADR 0005).

---

## 9. Modeling Notes (deltas from Asha §9 and pipeline.md §12)

- **Folder:** `assets_src/characters/kerrid/` on the §12 layout: `build_kerrid.py` imports `build_asha` as a helper
  library; `kerrid_params.json`, `kerrid_head.py` (the `nose_break` deformation), `kerrid_costume.py` (on
  `rhen_costume`'s `torso_sheet` and `limb_tube`, `asha_costume`'s `skirt_weights` for the back tier halves, Ysolde's
  dropped-shoulder sleeve), `kerrid_cape.py` (the fibre tiers), `kerrid_hair.py` (on `toma_hair`'s short cards and
  Toma's beard-in-Head method), `kerrid_props.py` (the cleaver), `kerrid_textures.py` (with the villager age terms and
  the rope-burn generator), `write_materials.py`.
- **Params (`kerrid_params.json`, the bb_params block; face sliders relative to the donor, 1.0 / 0.0 = unchanged):**

  | Key | Value | | Key | Value |
  |---|---|---|---|---|
  | `height_m` | 1.86 | | `eye_scale` | 1.10 |
  | `heads_tall` | 7.41 | | `ipd_m` | 0.066 |
  | `shoulder_width_heads` | 2.15 | | `eye_tilt_deg` | 0.0 |
  | `chest_width_heads` | 1.45 | | `canthus_offset_m` | 0.0 |
  | `chest_depth_heads` | 1.20 | | `jaw_width` | 1.02 |
  | `waist_width_heads` | 1.50 | | `cheekbone_height` | 0.002 |
  | `hip_width_heads` | 1.55 | | `cheekbone_width` | 1.08 |
  | `crotch_height_heads` | 3.45 | | `chin_size` | 1.05 |
  | `arm_span_ratio` | 1.03 | | `nose_bridge_width` | 1.18 |
  | `hand_length_heads` | 0.84 | | `nose_tip_projection` | 0.88 |
  | `foot_length_ratio` | 0.152 | | `lip_fullness` | 0.70 |
  | `neck_length_heads` | 0.38 | | `lip_close` | 0.6 |
  | `neck_width_ratio` | 0.62 | | `lip_seal` | 0.96 |
  | `head_width_ratio` | 0.70 | | `lip_lower_fullness` | 0.70 |
  | `femininity` | 0.0 | | `mouth_corner_lift` | −0.001 |
  | `muscle` | 0.60 | | `brow_ridge` | 1.12 |
  | `mass` | 0.45 | | `donor_mix_african` | 0.30 |
  | `breast` | 0.0 | | `donor_mix_asian` | 0.40 |
  | `arm_abduction_deg` | 47.0 | | `donor_mix_caucasian` | 0.30 |
  | `skin_hex` | `#9A6C50` | | | |

  Plus a `_kerrid` block read only by `build_kerrid.py` (so the shared bb_params reader is unchanged): `nose_break_m`
  0.003, `nose_break_side` "L", `skin_desaturate` 0.06, `burn_turns` 3, `burn_width_m` [0.022, 0.030], `hunch_deg` 8.0
  (for the stage's rest pose and the clips, §10), `cape_tiers`, `cleaver` dimensions (§4). Starting values; tune
  against the face shots, as Asha's were.
- **Age layer on a hero:** as Ysolde's (§9 of her sheet): `kerrid_textures.py` imports the villager age terms at 0.5 and
  calls `asha_textures.skin_maps`. No shared module changes.
- **Rope-burn generator (new, in `kerrid_textures.py`):** a seeded helix on each forearm's UV (3 turns, the band width
  varying 2.2-3.0 cm along it, ragged edges from noise), plus the palm burn; writes the albedo lift, the normal relief,
  the roughness term and the emission mask. The same generator draws the *healed* rope scars a Corrow fisher NPC might
  carry, with an age parameter.
- **Cape:** pattern-as-data (asha.md §9.2). Each tier is a woven base mat (a shell 4 mm off the layer beneath) with rows of
  fibre card strips hanging from it, 6-10 strips per 10 cm of row, 12-26 cm long, each strip 2 cards crossed at 70°
  (so the fringe has depth from every angle). Rows overlap like thatch, each covering the base of the row below.
  Deterministic placement from a seed; strip lengths and tilts from the same seed.
- **Rig extras (on `bb_rig.build_game_skeleton`, as `build_toma.add_bones`):** cape back tier halves 2 × 3; watch cord
  1 × 3; `DEF-cleaver` (prop, child of `DEF-spine.003`). The yoke has no bones of its own (torso and clavicle weights
  plus the arm blend band). **VFX sockets** (empties, not deforming bones; for Ch15 and H09): six per forearm along the
  burn spiral (`VFX-burn.L.1`-`.6`, `VFX-burn.R.1`-`.6`) and one per palm (`VFX-palm.L`, `VFX-palm.R`), parented to the
  forearm and hand bones.
- **Host-determinism snaps (M1-CHR-14 and M1-CHR-15, as `build_ysolde`):** `MIDLINE_SNAP` on the head vertices (and on
  the beard cards rooted on the midline), `quantize_uvs` after each unwrap, `snap_shape_noise` on every exported object
  (including the cape's `cape_wet` key), and `asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS` in the texture run.
- **Rig guards:** add a `kerrid` entry to `tools/dev/rig_checks.json`: `garments` [`Costume`, `Cape`, `Wrap`], `props`
  [`Cleaver`], `braid` null, seam groups as Toma's plus `Cape`. Probe the `cape_wet` shape at 1.0 as a separate stage
  pose (the wet fibre hangs closer, so it is the worse case for `garment_in_body`). Ratchets only with a written reason.
- **Blender job:** `kerrid` in `tools/dev/blender_builds.json` with `"threads": 4`, sources including
  `assets_src/characters/kerrid/**`, `asha/**`, `rhen/**` (limb tubes), `toma/**` (short hair, the beard method),
  `ysolde/**` (the dropped-shoulder sleeve, if imported from there), `villagers/**` (the age terms), `base_body/**` and
  `third_party/mpfb2/**`; two runs must be byte-identical.
- **Battle actor:** `game/characters/heroes/kerrid_battle.tscn` on `kerrid_lod1.glb`. The cleaver is its own mesh
  object (`Cleaver`) so the scene can hide the back instance and show the hand instance (a `BoneAttachment3D` on
  `DEF-hand.R`, the haft's grip point at the attachment, rotated so the hook faces down and forward in `ready`). The
  battle clips (§10.3) are authored with the cleaver in the right hand and the left hand above it on the haft.

---

## 10. Clips and Persona (hero_clips, pipeline.md §13)

### 10.1 Persona
`"kerrid": {"sway": 0.5, "lean": 0.0, "staff": False, "arms_down": 44.0, "stance": 1.2, "knee": 4.0, "breath": 0.0,
"hunch": 8.0}`.
- **`breath` 0.0** (the key Ysolde's sheet added; Sefir also uses 0.0): the unrisen don't breathe (bible §2), and in
  Ch5 Rhen says it aloud: "You're not even breathing hard." Under the cape the missing breath is subtle, which is right:
  it is a clue, not a reveal. **The review must not "fix" it.** He is told apart from Sefir's held stillness by his
  sway (0.5 against 0.0) and his weight shifts: Sefir doesn't move; Kerrid moves and doesn't breathe.
- **`hunch` (new key, default 0.0):** degrees of flexion added at `DEF-spine.003` and `.004` (split 50/50), with the head
  (`DEF-spine.006`) counter-pitched up by 0.75 × the hunch so the gaze stays level, and the shoulders (`DEF-shoulder.L/R`)
  rolled forward 0.4 × the hunch. Added to `hero_clips.stand` and `walk_pose` the way `lean` is. Asha's, Rhen's, Toma's,
  Ysolde's and Sefir's libraries must stay byte-identical with the default.
- `arms_down` 44: his bulk and the cape yoke carry the arms out from the body.
- `stance` 1.2 and `knee` 4: planted like Toma's, narrower and straighter (he stands like a man on a stair step, not a
  soldier in a line).
- **Walking arm swing:** the left (wrapped) arm swings at 0.6 of the right's, the hand loosely curled (a keyed finger
  pose is not needed: the curl is the hand bone's 12° flexion, inside the 31 keyed bones).

### 10.2 Story clips (Act I, from the beats)
| Clip | Loop | Beat | Notes |
|---|---|---|---|
| `idle` | yes | everywhere | The hunch, sway 0.5, **no breath**, a slow weight shift every 6-8 s. |
| `walk` | yes | field (always last in line: Ch5 B05/B07, Ch9 D03) | A heavy, short-stepped walk into wind: the hunch deepens 2° on each footfall, the head stays level. Never fast. |
| `run` | yes | field | A heavy jog: he runs badly and rarely. The cape tiers' panel bones carry the bounce. |
| `talk` | yes | everywhere | **Almost nothing:** one small chin lift or a 4° head turn per loop; the hands stay down. He answers with actions (voice guide). |
| `collar_catch` | no | Ch5 B05 P11: a child slips at the weir; "a big hand in a wrapped sleeve takes her by the collar and sets her back on the step" | The **left** hand reaches down and forward to hip height in 0.4 s, closes, lifts 20 cm and draws back, sets down 0.5 s later; then the head turns 30° away (out to sea) and holds. Plants the Ch8 W24 haul and the E3 collar fix. |
| `go_still` | no, holds | Ch5 B05 P12: "he goes completely still" at Asha's face (`@wait 1.2`, no face change); Ch9 N17-style holds | The sway and weight shift ease to 0 over 0.4 s and hold. The only difference from `idle` is that nothing moves; with `breath` 0 he becomes a statue. |
| `turn_at_name` | no | Ch5 B05: "Kerrid's head turns at 'Sallow'", one look held 1.0 s, then away | Head and eyes turn 35° (the shoulders follow 8°), hold 1.0 s, back over 0.6 s. Variants by the `@mark`. |
| `set_bowl_on_post` | no | Ch5 B06: he takes the offered bowl, sets it on the gate post untouched, and goes back to watching the dark | Both hands take a bowl at chest height, a half-turn of 40°, set it on a post at 1.1 m with the right hand, turn back to the sea. |
| `stand_watch` | yes | Ch5 B06 (the inn gate), Ch6 (the ridge's seaward end, his back to Sefir's barge), Ch9 D01-D02 (the milestone), the Prologue and Ch9 B10 vigils (P02: "Kerrid standing") | The idle with the right hand holding the left wrist in front at the belt (the wrapped forearm across the body), the head lifted 3° toward the horizon, sway 0.35. **He never sits in Act I** (beat sheets), so there is no seated clip. The facing (out to sea; his back to the barge) comes from the `@mark`. |
| `wade` | yes | Ch8 B15 (into the storm water at the stair foot); his habit of going into the water | A walk at waist depth: a slower stride, the arms carried higher (forearms at 30° above the water line), the hunch deeper (+4°). The water surface is the scene's; the clip only poses the body. |
| `push_climber` | yes | Ch8 B15: "waist-deep in the black water at the foot, pushing them up one by one" | A braced wade stance, the right foot up one step (18 cm), both hands pushing up and forward from chest to head height, the body leaning into the stair 12°; one push per 2.2 s loop with a reset. |
| `down_a_step` | no | Ch8: the fishwife says "Captain?"; "he says nothing and goes down a step" | One step backward and down (18 cm), the eyes dropping 10°, then the head turns back to the climbers. |
| `collar_haul` | no, holds | Ch8 W24: "from behind Rhen, a hand takes his collar and hauls him back off the lip": **his left hand, wrapped** | The left hand grips at Rhen's collar height (1.4 m) from behind, the body leans back 15° and steps back 40 cm in 0.5 s, the right arm out for balance; holds. |
| `look_down_stair` | no, holds | Ch8 W25 and B17: "Kerrid already turning away to look down the stair, which is now just sea"; "stands at the head of the drowned stair, looking down" | A 60° turn away, the head pitched down 25° (inside the yoke's clearance, §4 layer 6), the arms hanging; holds. |
| `carry_child` | yes | Ch9 cutaway: "a big man in a straw cape alone on the Fisher Stair, carrying a child's body up it" | A child's body across both forearms at chest height (the child is a scene prop on a `BoneAttachment3D` to `DEF-forearm.L`), climbing steps in place (18 cm rise per step, 1.6 s per step). Elbows bent 110° (the smock's rolled cuffs, §4 layer 1, stay above the crease). |

Act II and III clips (specify with their chapters): `sit_moorings` (Ch13-14: he sits out the nights among the
barge-polers; his first seated clip, and the first time he sits on screen), `hold_water_steps` (Ch14), `confess_hands`
(Ch15: seated on the barge, hands held still on his knees, palms up, as the motes leave them), `walk_last_rim` (Ch16),
`fix_collar` (E3: both hands straighten Rhen's collar).

### 10.3 Battle clip idiom (the M2-CHR-07 contract)
The 12 contract clips of the M2-CHR-07 block of `assets_src/characters/asha/hero_clips.py` (`idle` plus `BATTLE_CLIPS`),
all in place, lengths from `BATTLE_FRAMES`, the strike poses keyed at `BATTLE_CONTACT`. **His idiom: weight and hauling.**
The cleaver is held low in both hands like a hauling tool, never shouldered or twirled (a large blade rested on the
shoulder is a famous genre image; he never does it). Every blow is slow to start and ends the fight. Combat's niche
(story sheet): armour and power breaks, heavy high-rank blows; the Swell input is a *weighted swing* (a long charge
released at the right moment).

| Clip | Pose and motion | Striker (`BATTLE_STRIKER`) |
|---|---|---|
| `idle` | The battle stance: the cleaver held low across the body in both hands, the fluke head down and forward near the right foot, the wrapped left hand above the right on the haft; the hunch; sway 0.5, no breath. The field `idle` with the hands on the haft (or a separate battle idle if the field idle's hands can't hold it). | — |
| `ready` | The cleaver comes up 15 cm and the hunch deepens 3°, the feet settle wider (stance 1.35); back to idle. | — |
| `attack` | **The haul-chop:** the cleaver lifted back over the right shoulder (the arms first, then the blade turns: Toma's spear-lift order, so the hook doesn't sweep through his head), held a beat, then chopped down and forward to knee height with a short step of the left foot; contact 0.55; a slow recovery. | `DEF-hand.R`, (0, −0.6, 0.8) |
| `cast` | **Throwing a line** (his support actions; later "Spend the Light"): the left fist closes hard at the chest (the rope grip), then the arm throws forward and up and opens, palm up, as a captain throws a line to someone below; contact 0.8. The cleaver rests head-down in the right hand. **Not** the Order's flat-palm gesture (that is Sefir's and Toma's grammar). | `DEF-hand.L`, (0, 0.3, 0.95) |
| `item` | The left hand reaches forward and down, low, as if handing something to someone a step below; contact 0.7. | `DEF-hand.L`, (0, −0.4, 0.92) |
| `read` | The hunch deepens 5°, the head pushes forward and the squint tightens (the face's `determined` is Cinematics'); contact 0.6. | `DEF-spine.006`, (0, 0, 1) |
| `defend` | **Holding the stair:** the cleaver planted head-down in front of him as a wall, both hands on the haft below the ring, knees bent, the left shoulder into it; contact 0.6. | `DEF-spine`, (0, −1, 0) |
| `finisher` | **The weighted swing** (his Swell; also the Armor and Power Breaks' heavy form): the cleaver swung back past the right hip like a weight on a line and **held** there, coiled (the charge: keys 0.15-0.45 hold the coil with a slow 2° settle, so the clip shows the "more power the longer you dare" of the input), then released in a long low hauling sweep from right-back to left-front at knee height, the hook leading, the body turning 100°; contact 0.62. Flat and low, never overhead, so it reads apart from both his `attack` and Toma's overhead `finisher`. | `DEF-hand.R`, (0, 0, 1) |
| `hit` | He takes it: a 2 cm settle at the hips, the shoulders sink, the head barely moves (5°). The heaviest, smallest reaction in the party. | — |
| `dodge` | A quarter turn of the chest (shoulder in, 35°), the feet planted, letting the blow pass as a man on a stair turns to let a climber by. | — |
| `ko` | Down onto **both** knees, then forward onto the left (wrapped) hand, the cleaver laid flat beside him, the head bowed; holds the last frame. (Toma's `ko` is one knee and leaning on the spear; Kerrid's is a man on the bottom step.) | — |
| `victory` | The cleaver's head grounded at his right foot, the right hand on the haft; once per loop his head turns 25° over the right shoulder to look back down the line (the watch's count: is everyone up?), and back. No breath term: his loop's motion is the head turn and the sway only. | — |

**For the M2-CHR-07 block:** add `kerrid` to `BATTLE_HEROES`, his rows to `BATTLE_STRIKER` (above), `FOOT_FLAT["kerrid"]`
0.5 (the trouser hem rides the shin), a `_kerrid_keys` function, and an explicit `kerrid` branch in `_victory` (its
final `else` is Toma's today; make Toma's branch explicit too, keeping Toma's library byte-identical). His contact
fractions are the contract's; `tools/tests/test_hero_battle_clips.py` gains him.

Battle-scale actor: `game/characters/heroes/kerrid_battle.tscn` on `kerrid_lod1.glb` (pipeline.md §14), with the
cleaver swap of §9.

---

## 11. Acceptance Checklist (M3-CHR-05)

- [ ] Silhouette test in the flat-black view at 64, 128 and 256 px, and at battle scale (LOD1), beside Asha, Rhen, Toma,
      Ysolde, Liss, Pell and Sefir: identifiable by the ragged mound, the hunch, the ring above the left shoulder, the
      hook past the right hip and the dark left forearm; nothing above the head; the face clear.
- [ ] Every number in §1 and §9 is in `kerrid_params.json`; the build is headless and byte-reproducible (two runs, same
      sha256), job `kerrid` with `"threads": 4`; the host-determinism snaps of §9 are applied (`MIDLINE_SNAP`,
      `snap_shape_noise`, `quantize_uvs`, `PRE_ROUND`).
- [ ] Shared modules imported, not copied; any shared change re-verifies the `asha`, `rhen`, `toma`, `ysolde` and
      `villager_*` jobs.
- [ ] All 40 shapes (30 expression, 10 visemes) with the beard following them;
      `game/levels/_tests/characters/kerrid/kerrid_face_poses.json` with the 15 tags of §6.2, including the rest squint.
- [ ] M1-CHR-14 lessons: the cape's back tier split into two leg-following halves with panel bones (no tube); the yoke
      on the upper torso and clavicles with ≥ 25 mm neck clearance across the clips and its top ≥ 4 cm below the jaw;
      the smock's sleeve seam ≥ 11.5 cm below the shoulder joint; the chest rope on the torso only; the cleaver 1.2 cm
      off the grip and ≥ 12 mm off the cape on the back; the sandals on the feet.
- [ ] `tools/dev/rig_checks.json` has a `kerrid` entry (garments `Costume`, `Cape`, `Wrap`; props `Cleaver`), including
      the `cape_wet` stage pose; `python3 tools/dev/rig_probe.py --hero kerrid --report` passes the defaults (3 mm
      penetration, 0.5 mm seams, 0 exposed boundary vertices, clean weights), or each ratchet is pinned with a viewed
      reason; `tools/tests/test_rig_integrity.py` covers him.
- [ ] LOD0 ≤ 60k (ceiling 70k), LOD1 ≈ 28k; `kerrid.glb` < 5 MB, `kerrid_lod1.glb` < 1.5 MB; every PNG < 5 MB.
- [ ] No gold; no glow in the default material (`burn_glow` 0); the glow at 0.15 is `glimmer_held` only, checked in a
      night shot; no albedo below `lacquer_black`. Proposed swatches added to `palette.json` by Art with on-screen values.
- [ ] PROVENANCE rows for every new output (GLBs, textures, the fibre atlas, materials, clips, face poses).
- [ ] Body clips of §10.2 and the 12 battle clips of §10.3 in `assets/characters/kerrid/anim/kerrid_clips.tres` via
      `hero_clips.py --hero kerrid`, with every other hero's library byte-identical after the `hunch` key lands;
      `tools/tests/test_hero_clips.py` checks no breath term in his idle, the hunch's level gaze and the left hand in
      `collar_catch` and `collar_haul`; `test_hero_battle_clips.py` checks his contact markers and striker peaks.
- [ ] Review stage `game/levels/_tests/characters/kerrid/` on `asha_stage.gd`; shots `kerrid_front`, `kerrid_back`,
      `kerrid_three_quarter`, `kerrid_face`, `kerrid_face_stylized`, `kerrid_silhouette_lineup`,
      `kerrid_clip_collar_haul`, `kerrid_clip_push_climber`, `kerrid_battle_attack` (at the contact frame),
      `kerrid_storm_ch8` (wet cape, storm-dark edge check of §7), `kerrid_glow_ch10` (`burn_glow` 0.15, night).
      Baselines viewed and approved; run with `HYMN_SHOTS` set to these ids only.
- [ ] `docs/kb/art/characters/kerrid_review.md` written (strict SPEC §14 assessment), and a handoff.

---

## 12. Open Questions

For Narrative (not the human):
1. **No breath in the idle** (§10.1). Bible §2 says the unrisen don't breathe, and Ch5 has Rhen say "You're not even
   breathing hard." Art reads that as no breath motion at all (only the clue, under the cape). Confirm, or the idle gets
   a breath at 0.3 and the clue is only the fog in Ullar (Ch12).
2. **No tears** (§6.2 `grief`): the bible says the unrisen don't bleed; Art extends it to no tears. Confirm, or Ch15
   gets Asha's tear layer.
3. **The anchor's shackle ring as the pommel** (§4, item 11) is an art invention on "forged from a ship's anchor fluke".
   It is a strong read above the left shoulder. Confirm it is welcome (it adds no lore).
4. **The slight desaturation of his skin** (§1, §6.1: 6%, art decision). Too much and it is a tell before Ch15; this is
   meant to be invisible until the player knows. Confirm or set it to 0.

For the Art Director:
5. The ten proposed swatches (`palm_fibre`, `palm_fibre_pale`, `palm_fibre_wet`, `iron_hemp`, `tar_black`, `rope_old`,
   `iron_dark`, `iron_edge`, `watch_red`, `skin_kerrid`), and the reading that `watch_red` is not counted as lacquer red.

For Combat:
6. **Which clip plays Armor Break and Power Break?** The sheet assumes the `melee` style (the `attack` clip), with the
   `finisher` clip for his Swell and any break that Combat styles as a heavy technique. If the breaks get their own
   style, the clip set needs a 13th clip.
7. **The cleaver swap** (§9): the battle actor shows a hand-held cleaver and hides the back one. If the battle intro
   wants a draw on screen, that is a later battle-animation task (as Liss's launcher draw).

Nothing here needs the human (no SPEC §16 item).
