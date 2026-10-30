# Pell: Design Sheet

Owner: Character Artist (M3-CHR-506, design). Build: Character Artist (M3-CHR-506). Shaders: Rendering (the existing
`character_*` shaders; one open question on fur, §12). Story source: [`story/characters/pell.md`](../../story/characters/pell.md),
with [bible §8](../../story/bible.md) (the Kirru), [`vowbound.md`](../../story/vowbound.md) §5 (Nhoa),
[`act1_ch08.md`](../../story/beats/act1_ch08.md) (the seawall, Storm-Call), [`act1_ch09.md`](../../story/beats/act1_ch09.md)
N17-N18, B09-B10, and the voice guide. Shared conventions are in [`asha.md`](asha.md) §4.2 (masks), §6.2 (face shapes),
§8 (LOD rules) and §9 (pipeline), and the build layout is [`pipeline.md`](pipeline.md) §11-§16 (MPFB2 donor per ADR 0021,
the hero layout of §12, body clips of §13, battle scale of §14, rig guards of §16). This sheet lists only what differs.
Where the story is silent, the choice is marked **(art decision)**.

**One-line read:** the tallest and thinnest shape in the party, and the only one that isn't human. A long neck carried
forward in a shallow S, a narrow otter-like head with whiskers and a crest of fine grey heron feathers, sleek dark fur
with a cream stripe from the chin down the throat, a woven reed mantle over the right shoulder, a blank white shell at
the throat, cords of small shell tiles on the forearms, and a long, thin fishing-staff standing beside him in the left
hand like a wading bird's leg. Wet dark brown, cream, reed gold and bone. Animate him with stillness and economy;
**never comic.**

**Status:** M3 design target (Lead, 2026-10-24: "design sheets first"). Built on the MPFB2 hero path with a Kirru head
warp (§9). First seen at Corrow on the seawall (Ch8, as a guest in the Wave 3 encounter); joins after the Ebbing (Ch9).

---

## 1. Proportions

| Measure | Value | Notes |
|---|---|---|
| Height | **2.30 m** to the top of the skull, **2.36 m** to the crest's tips at rest, 2.43 m with the crest raised | The story's number (bible §8: 2.1-2.4 m). 41 cm over Toma. With the neck's S (below) his standing crown height on screen is about 2.26 m. |
| Head height | 0.275 m (**8.36 heads**), of which the muzzle projects 5.5 cm forward of where a human face would sit | A long, narrow head on a long neck. The "heads" count is a Kirru proportion, outside SPEC §7.3's human range by design (the Kirru are non-human, SPEC §3.4). |
| Shoulder width | 1.55 heads (0.43 m) | Lean and narrow for his height; sloped shoulders that run into the neck. |
| Chest depth | 0.95 heads | A swimmer's deep, narrow chest. |
| Waist / hip | 0.95 / 1.15 heads | Very lean (story: "lean"). |
| Crotch height | 4.05 heads (1.11 m) | Long legs: 48% of his height. |
| Neck length | **0.95 head (26 cm)** | Story and bible: "long-necked". Twice Ysolde's. |
| Arms | `arm_span_ratio` 1.07 | Long arms; the hands hang to mid-thigh. |
| Hands | **0.95 head (26 cm)**, long webbed fingers | Webbing between the fingers to the middle knuckle (§3). Four fingers and a thumb, as the human rig. |
| Feet | `foot_length_ratio` 0.17 (39 cm), long and narrow, webbed toes, bare | Kirru feet are long swimming feet; no footwear (§4.2). |
| Eyes | Large, dark and rounded (fissure 32 mm, a rounder opening than the human ×1.10 almond); IPD 70 mm; set forward, so he looks *at* people. | Not the human ×1.10 rule: a Kirru eye (§6). |
| Posture | **The wading-bird stand:** the spine plumb from the heels to the shoulders, the neck rising from the shoulders 20° forward of vertical and the head pitched back 15° so the face is level (a shallow forward S); weight evenly on both feet, the feet close (0.9× the shoulder-joint spacing); the left hand on the staff at hip height, the staff planted beside the left foot; the right arm long and loose. | **Idle sway 0.15** of the party default, the stillest living figure in the cast (Ysolde 0.3; Sefir 0.0 is not living). The Kirru "stand very still for a long time" (bible §8). He breathes (breath 1.0, slow). Every movement is economical: when he moves, it is one movement, then stillness again. |

**Age (about 120, Kirru middle age):** shown only in the fur and the crest: a few grey guard hairs at the muzzle and
brows (8%), and the crest's feathers a little worn at the tips. No lines, no stoop.

---

## 2. Silhouette from Three Angles

**Read test:** in the flat-black silhouette view at 64, 128 and 256 px he must be identifiable against Asha, Rhen,
Toma, Ysolde and Liss, against Sefir, and against Kerrid ([`kerrid.md`](kerrid.md)), at dialogue scale and at battle
scale (LOD1, §2.5). He is the easiest figure in the cast to tell apart; the risk is the reverse, that he reads as a
creature. **He must read as a person**: upright, with hands, a held tool, a garment, and a face turned to look at you.

| Against | Their read | Pell's read |
|---|---|---|
| Asha | Staff line above the head on her **right**, a lantern cage on top; 1.63 m; a sleeve flag, a braid, an A-line skirt. | His staff is on the **left**, thin, with **no bulb**: a single line ending in a small barbed tip 24 cm above his crest. He is 67 cm taller, and his head sits *forward* of his body on the neck's S, where hers is over her shoulders. |
| Rhen | A forward lean from the ankles, a lantern bulb over the right shoulder, crossed hooks, a short jacket. | Plumb from the heels to the shoulders; the forward line is the **neck**, not the body. Nothing on his back. |
| Toma | The widest trapezoid, a shield disc, a spear rising on his right. | The narrowest figure in the party (0.43 m shoulders) and the tallest. **His pole is never levelled or held like Toma's spear** (§3, §10.3): it stands, or it darts down like a heron's bill. |
| Ysolde | The darkest narrow column, a winged collar, a pin over the head. | Also narrow and dark, but **broken by the neck**: his column ends at the shoulders and the head rides forward of it on a thin stalk, with the crest on top. A cream stripe runs down his throat where her collar is dark. The reed mantle breaks his right shoulder. |
| Liss | Small, an X harness, a box at the hip, coat tails, a hair tail. | 74 cm taller; nothing crosses his chest except one thin cord under the left arm (§4). |
| Sefir | Tall (1.88), pale, plumb and motionless, a gilded disc behind the head, a gold half-mantle on the **right** shoulder. | Both have a mantle on the right shoulder, so the shapes differ: Sefir's is a stiff gold shell close to the shoulder; Pell's is a soft woven reed drape that falls to the elbow and the hip, matte straw-coloured, no metal. Sefir has a disc behind the head; Pell has a feather crest *on* the head and a neck. Sefir doesn't move; Pell barely moves, and breathes. |
| Kerrid | The widest low shape, a ragged straw mound, hunched; nothing above the head. | The tallest thin shape. In their Ch9 two-shot (B09: "two men who know each other's kind") the frame holds a haystack and a heron. |

**Echo watch (words only; no reference image):** the inspiring game has a tall, non-human, beast-folk party member who
learns enemy techniques and fights with a long polearm: he is known by blue fur, a lion-like mane and face, a broken
horn on the forehead, tattoos, and a spear held level and used with leaping attacks. Pell has **none of these**: dark
brown otter-like fur, no mane, no horn or anything on the forehead (the crest is fine feathers that lie flat), no
tattoos (the Kirru have no marks; the shell tiles are cords), a thin fishing-staff that stands upright or darts *down*,
never a levelled spear, and **no jumps** in any clip. He learns by *listening and imitating sounds*, so his learning
pose is a listening tilt (§10.3 `read`), not a technique drawn out of a foe. Keep it so in every revision. (A note
for Narrative, §12: the *story* shape, an exile with a visible mark of shame who returns to his people, sits close to
that character's arc too.)

### 2.1 Front (0°)
- A **tall, thin vertical** to the shoulders (0.43 m wide), then the **neck** rising forward of the body line, and the
  **narrow head** with its crest on top. The cream throat stripe runs from the chin down the neck to the sternum, the
  brightest vertical on him, so the neck reads at 64 px even against a dark ground.
- **The staff** stands on his left (viewer's right), planted 12 cm outside the left foot and leaning out 4°, rising 24 cm
  above the crest's tips: a single thin line with a small barbed tip (§3). The left hand holds it at hip height.
- **The reed mantle** over the right shoulder (viewer's left): a soft straw-coloured drape from the base of the neck,
  over the shoulder cap to 12 cm below the shoulder joint, down the right side of the chest and back to the hip. It
  makes the right shoulder line slope and soften; the left shoulder is bare fur.
- **The name-shell** at the throat: a small pale disc (5 cm) on a cord, sitting on the cream stripe. Visible but not
  featured in Act I (beat sheet).
- The forearm **shell-tile wraps**: bands of small pale-and-dark tiles from wrist to mid-forearm on both arms (§3).

### 2.2 Three-quarter (45°, his right side toward camera: the hero angle)
- The **right** side carries the read: the mantle's weave toward the lens, the right hand (the free one, the one that
  gestures and calls, §10) and the throat stripe.
- The neck's S shows clearly: the neck leaves the shoulders forward and the head tips back to level.

### 2.3 Profile (90°)
- **The S is the profile:** heels, hips and shoulders on one plumb line, the neck rising forward at 20°, the head level
  and the muzzle pointing forward. The crest lies back from the crown along the skull's line and lifts when he is alert
  (§5). The long feet show flat.
- The staff is a vertical line beside him; the counterweight stone (§3) is a small mass 30 cm above its foot.

### 2.4 Back (180°, field walking: he walks second, behind Toma, "as he was told", Ch9 D03)
- The dark fur saddle over the back and shoulders (bible §8: "sleek dark fur on the back and shoulders"), the mantle's
  back fall on the right, the crest above. A narrow dark shape with one softened shoulder.

### 2.5 Battle scale (LOD1 at 6 m; pipeline.md §14)
At battle framing he is about 100-110 px tall where the humans are 70-90 px. What must survive: the neck's S, the crest,
the staff line on his left, the throat stripe and the mantle's soft right shoulder. **A note to UI+Combat and
battle-presentation (§12):** his crown sits 40-60 cm above the others' and the staff's tip 30 cm higher still; the battle
camera's framings and the formation spacing must keep his head and the staff tip in frame (check
`pell_silhouette_lineup` at the battle camera's widest and its over-the-shoulder framings).

---

## 3. The Asymmetric Hallmark: the Mantle, the Staff and the Blank Shell

The story gives three costume marks; the design sets them on one diagonal: **the mantle on the right shoulder, the staff
in the left hand, and the shell on the centre line between them.**

- **The reed mantle (right shoulder, story sheet):** a woven drape of split river reed, plaited tight in a chevron weave
  (each plait 9 mm wide), about 70 × 105 cm, laid over the right shoulder so it falls front and back to the right hip,
  its outer edge over the upper arm to 12 cm below the shoulder joint. It is held by a thin cord that runs from its front
  corner across the chest, under the left arm, and up the back to its back corner, fastened at the left of the sternum
  with the **bone toggle** (story sheet): a 7 cm bar of pale bone, carved with nothing. The reed is dry and stiff; it
  sways little.
- **The fishing-staff (left hand, story sheet):** a long, light pole, **2.60 m**, of seasoned grey cane, 2.4 cm thick at
  the foot tapering to 1.5 cm at the tip, with five darker growth nodes. At the top, a **barbed bone tip**: a 14 cm point
  of pale bone with three small backward barbs on one side, lashed on with cord over 6 cm. Near the foot, a
  **counterweight**: a dark river stone 9 cm across in a cord net, lashed 30 cm above the foot, so the pole stands
  balanced when he lets go of it (he leans it on nothing; it stands in the mud where he plants it). **Held like a
  wading bird's leg** (story sheet): upright, beside him, as a third leg he rests his weight on lightly.
- **The name-shell (throat, story sheet):** a flat, round half-shell 5 cm across, pierced at the top and hung on a
  plaited cord close round the lower neck. **Act I and II state (blank):** ground smooth and matte, a dull white
  `shell_blank` with faint radial scratches where the carving was scraped off (bible §8: "ground blank"). **Act III
  state (carved):** a new shell, the same shape and size, glossier, carved with his name. A costume state change: two
  meshes, `NameShellBlank` and `NameShellCarved`, toggled by the scene (ch flag), never both visible.
- **The name carving (Act III; art decision):** the Kirru speak among themselves in whistle-clicks (bible §8), so a name is
  carved as a **spiral of notches**, long and short, from the rim to the centre: Pell's name as his clutch would whistle
  it. Original marks authored as data in `assets_src/characters/pell/motifs/` (a long/short sequence and the spiral's
  pitch), never painted, never letters of any script.
- **The shell-tile wraps (both forearms; art decision on the story's "beaded cord wraps"):** each forearm carries a wrap
  of plaited cord threaded with **small square shell tiles** (1.2 cm, 3 mm thick, rounded corners), in four tones: bone
  white, reed gold, a dark shell and a pale grey-blue nacre. Six turns per forearm from the wrist to mid-forearm, each
  turn carrying a run of five to seven tiles. **The left wrap's sequence is the call and the right wrap's is the response:**
  the same sequence of tones, mirrored. It echoes his Swell input (the story's "repeat back a shown sequence of
  shell-tiles", Combat's call-and-response) without copying any UI art: these are threaded tiles on a cord, a little
  uneven, worn, never a grid, never boxed, never numbered. (If UI later wants the tile look for the Swell panel, they
  author it from the same motif data, not from a render of the costume.)
- **The webbed hands:** a membrane between each pair of fingers to the middle knuckle, thin, darker at the fold and
  translucent at the edge (the skin mask's SSS thickness at 0.1). Weighted as a blend of the two neighbouring finger
  bones, so the fingers spreading stretch it and closing folds it; the clips keep the fingers near rest (§10).

---

## 4. Costume Layers and Materials

The Kirru dislike clothing (story sheet), so most of what the camera sees is the body: fur (§5). The costume is small,
and every piece is torso-only, on the forearms, or on the neck.

### 4.1 Layers (inner to outer)
| # | Piece | Material | Color | Mask channels | Skinning notes (M1-CHR-14 lessons) |
|---|---|---|---|---|---|
| 1 | **Reed mantle** (§3) | Plaited split reed, stiff, chevron weave in the normal map | `reed_plait` `#B3A062` (proposed), a green-gold straw; the plait's shaded faces `#8A7A48` in the albedo | A 0.35; no G (it is reed, not gold, and is never metallic) | **Torso and clavicle only** (`DEF-spine.003`/`.004`, `DEF-shoulder.R`), never the neck. The outer edge over the upper arm hangs to **12 cm below the shoulder joint**, its lowest 5 cm weighted 50% to `DEF-upper_arm.R`, so a raised arm lifts the edge rather than passing through it (the `cast` and `storm_call` clips raise the right hand to the throat). The front and back falls end at the right hip and are weighted to the spine and hips only, with **2 panel bones** each (stiffness high: reed, not cloth). Neck clearance ≥ 20 mm at the mantle's neck edge across a neck flexion of −30°/+20° and a turn of ±45° (the long neck moves more than a human's). |
| 2 | Mantle cord and **bone toggle** | Plaited reed cord 5 mm; bone toggle 7 cm | Cord `rope_old` `#7A6A52` (Kerrid's proposed swatch); toggle `bone` `#E6DAC0` | A 0.2 | Torso only. Under the left arm the cord lies on the ribcage **13 cm below the shoulder joint** (below the 11.5 cm line), offset 4 mm off the fur. |
| 3 | **Name-shell** on its throat cord (§3) | Shell; plaited cord | `shell_blank` `#D9D2C2` (proposed); carved state glossier with notches `#3A302A`; cord `rope_old` | A 0 (shell roughness 0.55 blank, 0.3 carved) | A neck item: the cord rides `DEF-spine.004` (the lower neck bone), **≥ 10 mm off the neck fur all round** at every neck pose of the clips; the shell hangs on the cord's front, rigid to the cord, sitting on the throat stripe with 6 mm clearance. Listed in `props` (`NameShell`), so `prop_in_body` catches the long neck's flexion pushing the skin into it. |
| 4 | **Shell-tile wraps** ×2 (§3) | Plaited cord with shell tiles | Cord `rope_old`; tiles `bone`, `reed_plait`, `shell_dark` `#4A3E36` (proposed), `nacre_grey` `#A8B2B4` (proposed) | A 0.2; tiles roughness 0.35, nacre roughness 0.2 | Rigid in runs on `DEF-forearm.L/R` and `.001` (the twist segment), 3 mm off the fur; the wrist turn stops 2 cm above the wrist crease, so a bent wrist doesn't drive the tiles into the hand. Listed in `garments` (`Wraps`). |
| 5 | Ankle cord (art decision) | Plaited cord with three tiles | as 4 | as 4 | One turn on the right shin, 4 cm above the ankle bone, shin-weighted only (never the foot). |
| 6 | Belt cord and pouch (art decision) | A plaited cord belt at the hips, a small woven-reed pouch (12 × 9 × 4 cm) at the left hip, and a coil of spare line (8 turns, 12 cm) at the right | Cord `rope_old`; pouch `reed_plait`; line `bone` | A 0.2 | Hips only (`DEF-spine`, `.001`); the pouch and coil 1.5 cm off the hip fur, rigid to the belt, so a stride doesn't pass the thigh into them (Liss's launcher lesson). |
| 7 | **Fishing-staff** (prop, §3) | Cane, bone, stone, cord | Shaft `timber_weathered` `#7E6A55` with nodes `#5E4E3C`; tip `bone`; stone `#3A3A3F` (`volcanic_stone`); cord `rope_old` | ORM roughness 0.6 cane, 0.4 bone | **Held in the left hand**, staff-style (the hand counter-rotates so it stays upright; §10.1 `staff_side`). **Offset from the grip:** the shaft sits **1.2 cm out from the fist's centre line**, and no lashing or node sits inside the grip span (Toma's spear lesson: the binding ends above the fist). The webbed fingers close round it with the membranes folded on the far side. Listed in `props` (`Staff`); its foot splays 4° outward so it never meets his left foot in a stride. |

### 4.2 What Pell does not wear
- **No footwear.** The Kirru feet are bare (they swim, and they dislike clothing). The M1-CHR-14 "footwear on the feet"
  lesson applies as: the feet are body, the ankle cord rides the shin, and nothing hangs onto the foot.
- **No garment on the legs or lower body.** The fur covers him (§5): the dark saddle continues over the hips and outer
  thighs. No anatomy is modelled. If the review finds the bare lower body reads as comic or awkward at any angle, the
  fallback is a short reed-fibre girdle at the hips split front and back (leg-following panels), not trousers; flag it
  rather than adding it silently.
- **Nothing on the head:** no hood, no hat, no band. The crest is his own feathers.
- **No metal, no gold, no lacquer, no Order mark** (the Kirru are tolerated by the Order, never converted, bible §8). His
  gear is reed, cord, cane, bone, stone and shell.
- **No keepsakes** except the name-shell (bible §8: "the Kirru do not keep graves or keepsakes"; the name-shell is his
  name, not a keepsake; see §12 for the Nhoa note).

---

## 5. Fur, Crest and Whiskers

- **Fur (the body's surface):** short, sleek and dense, lying in a clear flow (crown to tail of the spine, shoulders to
  wrists, hips to ankles). **Not cards over the whole body:** the fur is painted into the body and head albedo and normal
  (a fine fur-flow normal at 1.5 mm strand scale, generated from the flow field) with the skin mask's detail-normal
  weight at 1.0, the SSS thickness reduced to 0.25 (fur blocks the light), and a sheen term (§12, an open question for
  Rendering). A **silhouette fringe** of short fur cards (8-14 mm) sits only where the outline needs softening: the back
  of the neck, the shoulders' top line, the backs of the forearms and the calves (about 1,800 cards from a hero-owned
  `pell_fur.png` strand atlas, generated as `toma_shorthair.png` is).
- **Fur colour (bible §8 and the story sheet):** the **dark saddle** `fur_kirru_dark` `#3B2B22` (proposed) over the back,
  shoulders, outer arms, outer thighs and hips, wet-looking (roughness 0.35, the "wet dark brown"); a **mid brown**
  `fur_kirru_mid` `#5A4434` (proposed) on the front of the torso, the inner arms and the inner legs; the **cream stripe**
  `fur_kirru_pale` `#D9CDB4` (proposed) from the chin and the lower muzzle down the throat to the sternum, 7 cm wide at
  the throat, narrowing to 3 cm over the sternum; the palms and the soles bare dark skin `#2E2420`.
- **The crest (story sheet: "a crest of fine heron feathers that rises when he is alert"):** 14 fine, long feathers
  rooted along a 9 cm line on the crown, lying back along the skull at rest (the tips 6 cm above the back of the skull,
  22 cm long) and rising to about 35° when alert. Pale grey `crest_grey` `#B8B6AE` (proposed) with darker tips `#5A5650`
  and soft, separated barbs (alpha cards, two crossed per feather, from a hero-owned `pell_feather.png` atlas). **Driven
  by a shape key `crest_raise`** (0 flat, 1 raised) on the `Crest` mesh, plus `crest_flat` (wind- and rain-flattened,
  Ch8: "crest flattened by the wind"). The crest is head-rigid; no bones, no physics (its motion is the keys).
- **Whiskers:** 11 per side on the muzzle's whisker pads, 6-11 cm long, fine and pale (`#D8D0C0`), as thin alpha cards
  **in the Head object** (Toma's face-hair method, pipeline.md §12), so they move with the face shapes (`cheek_raise`
  and `mouth_smile` push them forward; `mouth_frown` lets them droop).
- **Brow tufts:** where a human has brows, a Kirru has two short tufts of paler, longer fur over the eyes (about 60 cards
  each, in the Head object); the brow shapes move them. They are the main instrument of his worry.
- **Ears:** small, rounded and set high and back on the skull (otter-like), fur-covered, with a darker inner face.
  **His personal asymmetry (art decision): a small old notch** in the rim of the left ear (8 mm), a bite from a fen
  creature long ago. It reads in close-ups only.
- **Wet state (Ch8: "wet, crest flattened"):** the fur's roughness down 0.15 and the albedo 10% darker (a material
  parameter), `crest_flat` 1.0. The scene sets it.

---

## 6. Face

### 6.1 Face shape
- **Long, narrow and otter-like** (story sheet; bible §8: "a long narrow face with whiskers"): a rounded skull, a muzzle
  projecting 5.5 cm forward of the human face plane with a broad, flat **nose pad** of dark bare skin (`#2A201C`, slightly
  moist: roughness 0.3), full **whisker pads** either side, and a small rounded chin under a closed mouth whose line runs
  back to below the eyes. The fur covers the whole face; the lips are dark and thin.
- **Eyes:** large, round-lidded and dark: iris `#1E1610` filling most of the visible eye, a warm limbal ring `#4A3426`,
  the sclera showing only at the corners in `lid_wide`. Set forward, so his look is direct (a person, not a prey animal).
  The eyelids are fur-edged with fine dark lashes.
- **Mouth:** the shape names of asha.md §6.2 are the API on his face too, re-fitted to a muzzle (§9): `mouth_smile` lifts
  the mouth corners and fills the whisker pads; `mouth_frown` draws them down and back; `nose_sneer` wrinkles the top of
  the muzzle behind the nose pad; `lip_upper_up` shows the teeth only at its top weight (and no tag uses it above 0.15:
  bared teeth read as an animal threat, never as Pell). **His asymmetry in motion:** the smile rises on the **right**
  first (`mouth_smile` R = L × 1.15).
- **Teeth:** a short muzzle's set: small, even, slightly pointed at the canines, mostly hidden. Built as the hero teeth,
  re-shaped by the head warp.
- **Close-range stylisation:** the ADR 0019 dialogue finish (painterly 0.6, detail 0.35) as every hero; `lid_wide` 0.18
  at rest, to check against the rounder Kirru lid (reduce to 0.10 if the eye looks startled at rest).
- **Blend timing:** 0.36 s, measured, no overshoot, and **a late start** (art decision): he answers a scene later (voice
  guide), so his expressions begin 0.25 s after the line or the cut, a per-actor onset delay in `sequencer.json` (a
  Cinematics setting, requested). Sefir stays the slowest blend in the cast (0.40 s); Pell is the latest to begin.

### 6.2 Emotion tags mapped to Pell's face
The 15 tags from `game/data/dialogue/emotions.json`. Weights 0-1, unlisted shapes 0, L/R as L/R. **Each row also gives
the crest** (`crest_raise`, 0-1), which Cinematics applies with the tag (a request, §12).

**His tells:** **the crest speaks before the face does.** It lifts with attention, interest and alarm, and flattens with
sorrow, shame and exhaustion; the face itself moves very little. **The whiskers** go forward with interest (through
`cheek_raise`) and droop with grief. He almost never opens his mouth except to call; when he is overwhelmed he hums the
storm's note (voice guide), which is `jaw_open` 0.05 and a closed mouth, never a cry.

| Tag | Shape weights | Crest | Pell note |
|---|---|---|---|
| `neutral` | — | 0.10 | Still, attentive. Most of Act I. |
| `soft_smile` | `mouth_smile` 0.12/0.14, `cheek_raise` 0.12, `lid_squint` 0.08 | 0.15 | "Beautiful." (Ch9 N17). Small. |
| `smile` | `mouth_smile` 0.32/0.37, `cheek_raise` 0.30, `lid_squint` 0.18 | 0.25 | Rare; with Liss (Act II), and the epilogue at Reedhollow. |
| `laugh` | `mouth_smile` 0.50/0.58, `cheek_raise` 0.50, `lid_squint` 0.40, `jaw_open` 0.10 | 0.35 | A soft huff, mouth nearly closed; the head dips 6°. Never a wide-open muzzle. |
| `worried` | `brow_inner_up` 0.40, `brow_down` 0.15 | 0.30 | |
| `sad` | `brow_inner_up` 0.40, `lid_close` 0.25, `mouth_frown` 0.20 | 0.0 | Whiskers droop (through the frown). |
| `grief` | `brow_inner_up` 0.75, `brow_down` 0.30, `lid_close` 0.40, `mouth_frown` 0.40, `jaw_clench` 0.15 | 0.0 (`crest_flat` 0.4) | Reserved: Ch11 before Nhoa (he kneels and doesn't speak for a full scene), the dive (Ending). No tear layer (art decision: a Kirru doesn't weep on screen; question §12). |
| `angry` | `brow_down` 0.60, `lid_squint` 0.30, `nose_sneer` 0.25 | 0.70 | The crest up hard and the muzzle wrinkled; the mouth stays closed. Rare. |
| `cold` | `brow_down` 0.20, `lid_close` 0.15, `mouth_press` 0.25 | 0.05 | At the elders (Ch10), from a distance. |
| `surprised` | `brow_inner_up` 0.35, `brow_outer_up` 0.50, `lid_wide` 0.35 | 0.85 | The crest does most of it. |
| `afraid` | `brow_inner_up` 0.60, `lid_wide` 0.45, `mouth_stretch` 0.15 | 0.90 | Rare: only for Asha (story: "this time he wants to be the one who lets go correctly"). |
| `determined` | `brow_down` 0.35, `lid_squint` 0.20, `mouth_press` 0.30 | 0.55 | Battle; the Storm-Call on the seawall (Ch8). |
| `tender` | `brow_inner_up` 0.25, `mouth_smile` 0.10/0.12, `lid_close` 0.20 | 0.05 | Teaching Asha the farewell-tide (Act III); turning his back to Nhoa (Ending). |
| `guilty` | `brow_inner_up` 0.45, `lid_close` 0.35, `mouth_press` 0.20 | 0.0 | The blank shell (Ch9 B09, when Rhen notices it, if Cinematics cuts to Pell). Gaze down 10°. |
| `exhausted` | `lid_close` 0.40, `brow_inner_up` 0.15 | 0.0 | "My neck is very tired." (voice guide). The neck lowers 6° (a clip or a gesture slot, not the face). |

**Ch9 B09 requirement (Cinematics):** "His crest lifts a little" at Kerrid: `crest_raise` 0 → 0.35 over 0.8 s with the face
held `neutral`. The two-shot holds; nothing else moves.

---

## 7. Color Callouts

Swatches marked *(proposed)* are not yet in `palette.json`; Art adds them (M3-CHR-506 acceptance) with their on-screen
values measured on the swatch card.

| Area | Swatch | Hex | Share of his silhouette |
|---|---|---|---|
| Fur saddle (back, shoulders, outer limbs, hips) | `fur_kirru_dark` *(proposed)* | `#3B2B22` | ~45% (front) / ~70% (back) |
| Fur front of torso, inner limbs | `fur_kirru_mid` *(proposed)* | `#5A4434` | ~18% |
| Throat stripe, lower muzzle | `fur_kirru_pale` *(proposed)* | `#D9CDB4` | ~6% (the brightest shape, at the top) |
| Reed mantle, pouch | `reed_plait` *(proposed)* | `#B3A062` | ~12% (front), ~10% (back) |
| Crest | `crest_grey` *(proposed)* + tips | `#B8B6AE` / `#5A5650` | ~2% |
| Nose pad, palms, soles, lips | bare skin | `#2A201C` / `#2E2420` | ~3% |
| Staff | `timber_weathered` | `#7E6A55` | ~3% |
| Bone (staff tip, toggle, line coil) | `bone` | `#E6DAC0` | ~1% |
| Name-shell (blank) | `shell_blank` *(proposed)* | `#D9D2C2` | ~0.3% |
| Shell tiles | `bone`, `reed_plait`, `shell_dark` *(proposed)* `#4A3E36`, `nacre_grey` *(proposed)* `#A8B2B4` | | ~1% |
| Cords | `rope_old` *(proposed in kerrid.md)* | `#7A6A52` | ~1% |
| Whiskers | — | `#D8D0C0` | < 0.5% |

**No gold, no lacquer, no metal** (art decision): the Kirru are outside the Order's world, and his only warm-light tone
is the reed's straw colour. He adds **0% gold** to any group shot. `reed_plait` is a matte straw albedo (no G channel, no
metallic); the Art Director should confirm it doesn't count against `gold_max_frame_fraction` (§12).

**Reed is not Kerrid's straw:** `reed_plait` is greener and more saturated than Kerrid's grey `palm_fibre` `#A08C66`, and
reads as a tight chevron weave, never hanging strands ([`kerrid.md`](kerrid.md) §7).

**Value check:** about 70% dark (the saddle and the mid fur), 18% mid (the mantle, the staff), 10% light (the throat
stripe, the crest, the shell, the bone). A dark figure with a light vertical down the throat and a light crest on top:
the light shapes lead the eye up the neck to the face.

**Albedo floor:** `fur_kirru_dark` (Rec.709 linear luminance about 0.026) is above `lacquer_black` (about 0.010); the
nose pad `#2A201C` (about 0.016) is the darkest albedo on him and also clears it. `fur_kirru_pale` and `shell_blank`
stay under the albedo ceiling `#EBE7DF`. **Night risk:** in Ch8's storm-dark (the seawall parapet, spray) and Ch9's night
strand, the saddle merges with the dark. The wet fur's sheen, the throat stripe and the crest must hold his shape;
Rendering checks him in the Ch8 parapet framing (`pell_storm_ch8` shot).

---

## 8. Budgets

Sheet targets follow SPEC §7.3 (40-70k per hero). **Pell shows almost all of his body**, so the hidden-face deletion that
saves the other heroes 10-15k triangles barely applies; the fur is texture, not cards, to fit. The 5 MB GLB cap binds
first, as for every hero (the whiskers and brow tufts are in the Head object and carry the 40 morph targets).

### 8.1 Triangles (LOD0 target 62,000; hard ceiling 70,000)
| Part | Target | Notes |
|---|---|---|
| Head and face (skin, muzzle, ears, lashes, mouth; donor face subdivision) plus whiskers and brow tufts in the Head object | 22,000 | Watch the GLB size (§8.2) |
| Eyes | 2,216 | |
| Body (nearly all visible: torso, neck, arms, webbed hands, legs, webbed feet) | 20,500 | The donor's full body minus the head, with the hands' membranes added |
| Fur silhouette fringe cards | 4,100 | Neck, shoulder line, forearm backs, calves only |
| Crest (14 feathers, crossed cards) with its two shape keys | 900 | Not on the Head object |
| Reed mantle (front and back falls, the plait edge bevel), cord and toggle | 2,800 | |
| Name-shell, both states (one visible at a time) and cord | 400 | |
| Shell-tile wraps ×2, ankle cord | 2,000 | Tiles as instanced bevelled boxes, about 150 tiles |
| Belt cord, pouch, line coil | 900 | |
| Fishing-staff (shaft with nodes, bone tip and barbs, stone and net, lashings) | 1,800 | |
| **Total** | **57,616** | Leaves 4.4k under the target for an Act II fallback girdle if one is needed (§4.2) |

**LODs:** LOD1 28k (from 6 m; the battle actor), LOD2 13k, LOD3 5k. **LOD1 keeps:** the neck's S, the crest outline, the
staff line and its tip, the mantle's shape, the throat stripe (texture), the name-shell disc, the long fingers and feet.
Cut detail (the fur fringe's inner rows, the tiles' bevels, the whiskers below 6 cm, the net round the stone), never
shape.

### 8.2 Textures
| Set | Resolution | Maps | Notes |
|---|---|---|---|
| Face and head | 2K ×4 (albedo, normal, ORM, skinmask) | | The fur-flow normal on the face at ≥ 40 px/cm. |
| Body | **2K ×4** (not 1K) | albedo, normal, ORM, skinmask | The body *is* his costume: the fur flow and the saddle's edge need the resolution. |
| Costume and props atlas (mantle, cords, tiles, shell, toggle, pouch, staff) | 2K (ORM 1K) + clothmask 1K | | The chevron plait at ≥ 12 px/cm. |
| Fur fringe | hero-owned `pell_fur.png` 1K strand atlas | alpha, flow | Generated in `pell_textures.py` as `toma_shorthair.png` is. |
| Crest | hero-owned `pell_feather.png` 1K | alpha, flow | Generated feathers (a shaft and barbs from a seed), never a photo. |
| Eyes | shared 1K, with a Kirru iris (§6.1) | | A material on the shared eye atlas. |

`pell.glb` < 5 MB, `pell_lod1.glb` < 1.5 MB, every PNG < 5 MB (ADR 0005).

---

## 9. Modeling Notes (deltas from Asha §9 and pipeline.md §12)

- **Folder:** `assets_src/characters/pell/` on the §12 layout: `build_pell.py` imports `build_asha` as a helper library;
  `pell_params.json`, `pell_head.py` (the Kirru head warp, below), `pell_costume.py` (the mantle on `rhen_costume`'s
  `torso_sheet`; the cords and tiles), `pell_fur.py` (the fur flow field, the fringe cards, the crest and the whiskers
  on `asha_hair`'s card helpers and Toma's face-hair method), `pell_props.py` (staff, name-shell both states),
  `pell_textures.py`, `write_materials.py`, `motifs/` (the name spiral, the tile sequences).
- **The Kirru head (the hard part):** the donor is a human. Pell keeps the donor's topology and the whole pipeline by
  adding one step, **`pell_head.kirru_warp`**, between the face sculpt and `build_shapes`: a polyharmonic RBF warp (the
  same kind as pipeline.md §11's fit) from the donor's face landmarks onto a Kirru landmark set in `pell_params.json`'s
  `_kirru` block: the nose tip and the mouth pushed forward to the muzzle (5.5 cm), the nose pad broadened, the whisker
  pads filled, the mouth line drawn back toward the cheek, the chin reduced, the cranium lengthened and rounded, the
  ears scaled to 0.55 and moved up and back 2.5 cm. **The landmarks are re-read after the warp** (as the fit does), so the
  eyes, teeth, lashes and the 40 shapes are built on the Kirru face, under the same names. The warp is deterministic
  (no random terms) and runs before the host-determinism snaps.
  - **Risk:** the shared expression and viseme shapes were authored for a human mouth. On a muzzle some may need a
    Pell-only correction (a delta added after `build_shapes`, as Toma's beard takes deltas). Check every shape in the
    face pose stage before the face shots.
  - **If the warp can't reach a believable muzzle** without breaking the face shapes, stop and write an ADR before
    building a non-donor head: ADR 0021 makes the MPFB2 data our base topology, and replacing the head for one hero is a
    departure Rendering and Cinematics (the face pipeline) must agree to.
- **Params (`pell_params.json`, the bb_params block; face sliders relative to the donor):**

  | Key | Value | | Key | Value |
  |---|---|---|---|---|
  | `height_m` | 2.30 | | `eye_scale` | 1.0 (the Kirru eye is set in `_kirru`) |
  | `heads_tall` | 8.36 | | `ipd_m` | 0.070 |
  | `shoulder_width_heads` | 1.55 | | `eye_tilt_deg` | 0.0 |
  | `chest_width_heads` | 1.12 | | `canthus_offset_m` | 0.0 |
  | `chest_depth_heads` | 0.95 | | `jaw_width` | 0.80 |
  | `waist_width_heads` | 0.95 | | `cheekbone_height` | 0.0 |
  | `hip_width_heads` | 1.15 | | `cheekbone_width` | 0.92 |
  | `crotch_height_heads` | 4.05 | | `chin_size` | 0.80 |
  | `arm_span_ratio` | 1.07 | | `nose_bridge_width` | 1.10 |
  | `hand_length_heads` | 0.95 | | `nose_tip_projection` | 1.0 (the muzzle is the warp's) |
  | `foot_length_ratio` | 0.17 | | `lip_fullness` | 0.55 |
  | `neck_length_heads` | 0.95 | | `lip_close` | 0.7 |
  | `neck_width_ratio` | 0.42 | | `lip_seal` | 0.98 |
  | `head_width_ratio` | 0.52 | | `lip_lower_fullness` | 0.55 |
  | `femininity` | 0.0 | | `mouth_corner_lift` | 0.0 |
  | `muscle` | 0.60 (0.30 until GPU QA pass 3: the arms read thin) | | `brow_ridge` | 0.95 |
  | `mass` | 0.25 (was 0.05, then 0.15; GPU pass 5: the arms still read thin) | | `donor_mix_african` | 0.34 |
  | `breast` | 0.0 | | `donor_mix_asian` | 0.33 |
  | `arm_abduction_deg` | 47.0 | | `donor_mix_caucasian` | 0.33 |
  | `skin_hex` | `#3B2B22` (the fur saddle; the fur map supplies the rest) | | | |

  Plus a `_kirru` block read only by `build_pell.py`: `muzzle_m` 0.055, `nose_pad_width_m` 0.032, `whisker_pad` 1.0,
  `ear_scale` 0.55, `ear_offset_m` [0.0, 0.025, −0.025], `cranium_length` 1.08, `eye_fissure_m` 0.032,
  `eye_roundness` 0.7, `neck_s_deg` [20.0, −15.0] (the rest neck forward and the head's counter-pitch, for the stage
  and the clips), `web_depth` 0.5 (to the middle knuckle), `ear_notch` {side "L", depth_m 0.008}, `crest` (count 14,
  line 0.09 m, length 0.22 m, raised 35°), `whiskers` (11 per side, 0.06-0.11 m). Starting values.
- **Neck rig:** the two standard neck bones (`DEF-spine.004`, `.005`) span his 26 cm neck. The S is posed with both (the
  lower forward, the upper and the head back); the clips key them (they are in the 31). If the long neck creases at the
  middle in the clips (a long span on two bones under linear skinning), the fix is a hero-specific third neck bone
  between them, re-weighted, kept at rest by the clips and driven as the mean of its neighbours by the stage: write it
  up in the review, and do not add it to `bb_rig`.
- **Fur:** `pell_fur.py` builds the flow field on the anatomy field (as the hair flow), bakes it into the body and head
  normal maps and a `*_hairflow`-style flow texture (if Rendering takes the fur sheen request, §12), and places the
  fringe cards along the silhouette regions. Seeded and deterministic.
- **Rig extras (on `bb_rig.build_game_skeleton`, as `build_toma.add_bones`):** mantle front and back falls 2 × 2; the staff
  prop bone `DEF-staff` (child of `DEF-hand.L`); the name-shell is rigid to `DEF-spine.004` (no bone of its own). The
  crest uses shape keys, not bones. Fingers stay at rest in every clip unless a clip says otherwise (the webbing).
- **Host-determinism snaps (M1-CHR-14 and M1-CHR-15, as `build_ysolde`):** `MIDLINE_SNAP` on the head vertices (and on
  the crest, whisker and tuft cards rooted on the midline), `quantize_uvs` after each unwrap, `snap_shape_noise` on every
  exported object (including the crest's `crest_raise` and `crest_flat`), and `asha_textures.PRE_ROUND =
  PRE_ROUND_DECIMALS` in the texture run.
- **Rig guards:** add a `pell` entry to `tools/dev/rig_checks.json`: `garments` [`Costume`, `Wraps`, `Crest`], `props`
  [`Staff`, `NameShell`], `braid` null, seam groups as Toma's (Head/Body neck seam, the long neck makes it the one to
  watch). The crest is a garment so that a head pitched back into the neck's S (the `storm_call` and `hit` clips) can't
  push its tips into the back of the neck or the mantle unseen (as Sefir's `HairBack`). Probe `crest_raise` 1.0 as a
  separate stage pose. Ratchets only with a written reason.
- **Blender job:** `pell` in `tools/dev/blender_builds.json` with `"threads": 4`, sources including
  `assets_src/characters/pell/**`, `asha/**`, `rhen/**` (the torso sheet), `toma/**` (the face-hair method, the short-card
  atlas generator), `base_body/**` and `third_party/mpfb2/**`; two runs must be byte-identical.

---

## 10. Clips and Persona (hero_clips, pipeline.md §13)

### 10.1 Persona
`"pell": {"sway": 0.15, "lean": 0.0, "staff": True, "staff_side": "L", "arms_down": 30.0, "stance": 0.9, "breath": 0.8,
"neck_s": 20.0}`.
- `sway` 0.15: the stillest living figure (bible §8: the Kirru "stand very still for a long time").
- `breath` 0.8 (the key Ysolde's sheet added): a slow, deep breath, the chest only. He is alive; this tells him apart
  from Sefir's and Kerrid's held stillness at a glance.
- **`staff_side` (new key, default "R"):** which hand holds the staff when `staff` is True. Asha and Toma keep "R"; Pell's
  is "L", so `staff_hold`'s counter-rotation and the walk's reduced arm swing (0.35) apply to the left arm. Asha's and
  Toma's libraries must stay byte-identical with the default.
- **`neck_s` (new key, default 0.0):** degrees of forward flexion at `DEF-spine.004` (the lower neck), with `DEF-spine.005`
  and the head (`DEF-spine.006`) counter-pitched back by 0.75 × the value so the face stays level. Added to
  `hero_clips.stand` and `walk_pose` the way `lean` is. Every other library byte-identical with the default.
- `arms_down` 30: long arms hanging close (his lean body; he takes up little space).
- `stance` 0.9: feet close, a wading bird's stand.
- **The walk (art decision):** a long, slow stride (stride length 1.15× the human ratio for his leg), the feet lifted a
  little higher than a human's and set down flat, and a **head-hold**: the head stays level and moves forward smoothly
  while the neck's S takes up the body's bob (the head's vertical motion at 0.3 of the hips'). A heron's walk, but
  restrained: **no forward-and-back head pumping**, which would read as comic.

### 10.2 Story clips (Act I, from the beats)
| Clip | Loop | Beat | Notes |
|---|---|---|---|
| `idle` | yes | everywhere | The wading-bird stand, sway 0.15, breath 0.8; one slow head turn of 10° every 10-14 s, then still. |
| `walk` | yes | field (second in line, behind Toma) | The long, level-headed stride of §10.1, the staff planted every second step on the left (it swings forward and lands with the left foot). |
| `run` | yes | field | A long lope, the neck lowered 10° forward, the staff carried upright in the left hand off the ground. Rarely seen. |
| `talk` | yes | everywhere | **Economy:** once per loop the right hand opens slightly at hip height, palm up, and closes; the head tilts 4°. Most of his lines are a still body and a face. |
| `storm_call` | yes | Ch8 B13 (Wave 3, the outer parapet in spray: "imitating the storm's own sounds to lure spawn away"; `pell_storm_note`, "one huge, low, rising-and-falling note from a throat") | The neck extends up and forward (the S straightens by 15°), the chest lifts, the right hand rises flat to the base of the throat (palm on the cream stripe, the mantle's edge lifting with the arm, §4 layer 1), the staff planted; the chest swells and settles over a 4 s loop with the note. The mouth is the face's (`jaw_open` 0.20 through `@face`). |
| `descend_rocks` | no | Ch9 N17: "a very tall shape has come down the rocks at the strand's end" | Two steps down (30 cm each), the staff placed first on the lower rock each time, then the feet, slow and sure; ends in the stand. |
| `go_still` | no, holds | Ch9 N17: "Pell stands still for a long time, the way the Kirru do" | The sway and the head turn ease to 0 over 0.6 s and hold; the breath continues. |
| `listen_tilt` | no, holds | dialogue (he answers a scene later; the moment he takes in a question); battle `read` (§10.3) | The head tilts 15° to his right and turns 10°, the neck extending 4 cm; holds. The crest is the face table's. |
| `back_to_sea` | yes | The Prologue and Ch9 B10 vigils (P02: "Pell with his back to the sea"; P03, the slow push) | The stand, the staff planted, the head bowed 10°, the eyes closed (the face's `lid_close` 0.8 through `@face`), sway 0.1. **The facing comes from the `@mark`** (his back to the water). **Only for the vigil frame and Act III**: before Ch10 he never turns his back to the sea (the refusal is his arc), and no other clip faces him away from the water by default. |
| `walk_behind` | — | Ch9 N18 / D03: "walk behind me, then" | The `walk`; the order is the sequencer's. No separate clip. |

Act II and III clips (specify with their chapters): `stand_apart_back` (Ch10: he stands with his back to the party, facing
Reedhollow he may not enter), `kneel_still` (Ch11: he kneels in front of Nhoa and doesn't speak for a full scene: onto
both knees, the staff laid on the ground before him, the neck lowered, held), `teach_farewell` (Act III, beside Asha at the
tideline), `turn_back` (the Ending: as Nhoa lifts, he **turns his back to her**, a slow 180° turn over 3 s, the head last,
then the stand with the eyes closed; the most important body clip he has, so it is specified now and built with the
dive).

### 10.3 Battle clip idiom (the M2-CHR-07 contract)
The 12 contract clips of the M2-CHR-07 block of `assets_src/characters/asha/hero_clips.py` (`idle` plus `BATTLE_CLIPS`),
in place, lengths from `BATTLE_FRAMES`, the strike poses keyed at `BATTLE_CONTACT`. **His idiom: a fishing heron.** Long
stillness, then one fast, exact movement, then stillness again. The staff stands or darts *down*; it is never levelled
as a lance, never twirled, and he never leaves the ground (§2 echo watch). Combat's niche (story sheet): he learns enemy
abilities by hearing them; the Swell input is call-and-response tiles.

| Clip | Pose and motion | Striker (`BATTLE_STRIKER`) |
|---|---|---|
| `idle` | The field stand with the staff planted beside the left foot, sway 0.15, the crest at 0.3 (the battle stage applies it). | — |
| `ready` | The neck draws back 6° into a deeper S (the heron's cocked neck), the knees soften 6°, the staff lifts 5 cm off the ground; back to idle. | — |
| `attack` | **The heron's dart:** the staff raised to vertical-high in the left hand with the right hand joining it below, the neck drawn back, a held beat, then one fast jab **down and forward** with the barbed tip to knee height, the neck and both arms extending together; contact 0.55; a slow return to the stand. | `DEF-hand.L`, (0, −0.5, 0.85) |
| `cast` | **The imitation** (the enemy ability he has learned): the right hand to the throat, the neck stretching up (`storm_call`'s shape), a held call, then the right hand sweeps out flat toward the foe, sending the sound; contact 0.8. The staff stays planted. | `DEF-hand.R`, (0, 0.2, 0.98) |
| `item` | The right hand reaches out long and low, palm up, and opens; contact 0.7. | `DEF-hand.R`, (0, −0.3, 0.95) |
| `read` | **Listen** (also the Read action, and his proposed "Listen" stance, §12): `listen_tilt`'s pose, the neck extending, the head turning its right ear to the foe; contact 0.6. | `DEF-spine.006`, (0, 0, 1) |
| `defend` | He folds: the knees bend 25°, the neck lowers to a deep S, the right (mantled) shoulder turns to the blow, the staff held upright in front of him with both hands; contact 0.6. | `DEF-spine`, (0, −1, 0) |
| `finisher` | **Call and response** (his Swell): the *call*, the staff planted, the neck rising straight and the chest lifting (keys 0.15-0.35); the *response*, the staff swept from the left in one wide, flat arc at knee height round to his right, his body turning 90° with it, the counterweight end leading the swing; contact 0.62; then the staff planted again on the far side, and stillness. | `DEF-hand.L`, (0, 0, 1) |
| `hit` | The neck takes it: the head snaps back 10° and the neck's S deepens, the body sways back 2 cm, the feet stay. | — |
| `dodge` | A lean away over the right foot, the left foot lifting 8 cm for a beat (the one time he stands on one leg, briefly), the neck swaying the other way to keep the head level; back down. | — |
| `ko` | The knees fold and he sinks back onto his heels, then the long neck lowers forward until the head is a hand's width from the ground, the staff laid across his knees; holds. (Distinct from Toma's one knee and Kerrid's forward fall.) | — |
| `victory` | Very still: the stand, the head lifted 5°, the eyes half closed, listening to the quiet; the crest settles from 0.3 to 0.1 over the first loop. **He does not turn his back** in victory: that gesture belongs to the dead (bible §8) and to the Ending. | — |

**For the M2-CHR-07 block:** add `pell` to `BATTLE_HEROES`, his rows to `BATTLE_STRIKER` (above), `FOOT_FLAT["pell"]` 1.0
(bare feet, no hem, so the feet stay flat), a `_pell_keys` function, and an explicit `pell` branch in `_victory` (its final
`else` is Toma's today; make Toma's explicit, keeping his library byte-identical). The staff is on the left: his keys
turn `DEF-hand.L` where Asha's turn `DEF-hand.R` (`staff_side`, §10.1). `tools/tests/test_hero_battle_clips.py` gains him.

Battle-scale actor: `game/characters/heroes/pell_battle.tscn` on `pell_lod1.glb` (pipeline.md §14).

---

## 11. Acceptance Checklist (M3-CHR-506)

- [ ] Silhouette test in the flat-black view at 64, 128 and 256 px, and at battle scale (LOD1), beside Asha, Rhen, Toma,
      Ysolde, Liss, Kerrid and Sefir: identifiable by the neck's S, the crest, the thin staff on the left and the soft
      right shoulder; reads as a person, not a creature; the §2 echo watch holds (no horn, no mane, no levelled spear,
      no blue).
- [ ] Every number in §1 and §9 is in `pell_params.json`; the build is headless and byte-reproducible (two runs, same
      sha256), job `pell` with `"threads": 4`; the host-determinism snaps of §9 are applied (`MIDLINE_SNAP`,
      `snap_shape_noise`, `quantize_uvs`, `PRE_ROUND`).
- [ ] The Kirru head is the donor topology through `pell_head.kirru_warp` (or an ADR exists for a non-donor head, §9).
      Shared modules imported, not copied; any shared change re-verifies the `asha`, `rhen`, `toma`, `ysolde` and
      `villager_*` jobs.
- [ ] All 40 shapes (30 expression, 10 visemes) on the muzzle, with the whiskers and brow tufts following them;
      `game/levels/_tests/characters/pell/pell_face_poses.json` with the 15 tags of §6.2 and their crest values.
- [ ] M1-CHR-14 lessons: no garment below the hips (nothing to clip at the legs); the mantle on the torso and right
      clavicle with its arm edge ≥ 11.5 cm below the shoulder joint and its arm blend band; the cord under the left arm
      ≥ 11.5 cm below the joint; the name-shell cord ≥ 10 mm off the neck at every neck pose; the staff 1.2 cm off the
      grip with no lashing in the grip; the feet bare and whole.
- [ ] `tools/dev/rig_checks.json` has a `pell` entry (garments `Costume`, `Wraps`, `Crest`; props `Staff`, `NameShell`),
      including the `crest_raise` stage pose; `python3 tools/dev/rig_probe.py --hero pell --report` passes the defaults
      (3 mm penetration, 0.5 mm seams, 0 exposed boundary vertices, clean weights), or each ratchet is pinned with a
      viewed reason; `tools/tests/test_rig_integrity.py` covers him.
- [ ] LOD0 ≤ 62k (ceiling 70k), LOD1 ≈ 28k; `pell.glb` < 5 MB, `pell_lod1.glb` < 1.5 MB; every PNG < 5 MB.
- [ ] No gold, no metal; no albedo below `lacquer_black` or above `gauze_white`. Proposed swatches added to
      `palette.json` by Art with on-screen values.
- [ ] Both name-shell states exist and only one is visible at a time; the carved spiral is from `motifs/` data.
- [ ] PROVENANCE rows for every new output (GLBs, textures, the fur and feather atlases, materials, clips, face poses,
      the motif data).
- [ ] Body clips of §10.2 and the 12 battle clips of §10.3 in `assets/characters/pell/anim/pell_clips.tres` via
      `hero_clips.py --hero pell`, with every other hero's library byte-identical after the `staff_side` and `neck_s`
      keys land; `tools/tests/test_hero_clips.py` checks the staff upright in the left hand, the level head through the
      walk, and the feet flat; `test_hero_battle_clips.py` checks his contact markers and striker peaks.
- [ ] Review stage `game/levels/_tests/characters/pell/` on `asha_stage.gd`; shots `pell_front`, `pell_back`,
      `pell_three_quarter`, `pell_face`, `pell_face_stylized`, `pell_silhouette_lineup` (at the battle camera's widest
      and over-the-shoulder framings too), `pell_clip_storm_call`, `pell_clip_walk`, `pell_battle_attack` (at the
      contact frame), `pell_storm_ch8` (wet, crest flat, the storm-dark edge check of §7). Baselines viewed and
      approved; run with `HYMN_SHOTS` set to these ids only.
- [ ] `docs/kb/art/characters/pell_review.md` written (strict SPEC §14 assessment, including whether he reads as a
      person and never as comic), and a handoff.

---

## 12. Open Questions

For Narrative (not the human):
1. **The story echo (§2 echo watch):** a tall non-human party member who learns enemy abilities, carries a long pole,
   bears a visible mark of shame from his own people, and returns to them to be accepted is close to the inspiring
   game's beast-folk guardian in shape. The costume avoids every visual cue, but the arc's outline is Narrative's to
   check (his Act III return and re-carving at Reedhollow).
2. **No tail** (art decision). "Otter-like" could suggest one; neither the bible nor the story sheet gives one, and a tail
   adds a rig chain and a comic risk. Confirm.
3. **No lower garment** (§4.2, art decision on "the Kirru dislike clothing"). Confirm, or name what a Kirru wears.
4. **The name carving as a spiral of notches** (§3) is an art invention on the whistle-click speech. Confirm.
5. **Keepsakes:** bible §8 says the Kirru keep none, and Pell's name-shell is a name, not a keepsake; but vowbound.md §5
   calls Nhoa's own carved name-shell "the keepsake". Confirm the shell is fine on a Kirru and that "keepsake" there is
   the Vowbound mechanic's word.
6. **No tears** (§6.2 `grief`): a Kirru doesn't weep on screen (art decision). Confirm.

For the Art Director:
7. The ten proposed swatches (`fur_kirru_dark`, `fur_kirru_mid`, `fur_kirru_pale`, `reed_plait`, `crest_grey`,
   `shell_blank`, `shell_dark`, `nacre_grey`, plus `rope_old` shared with Kerrid), and that `reed_plait` (a matte straw
   albedo) is not counted as gold.

For Rendering:
8. **Fur shading.** The sheet uses the existing skin shader with a fur-flow detail normal, low SSS and the hair shader on
   the fringe cards. A sheen lobe along the fur flow (reading a flow map, as the hair shader does) would sell the "wet
   dark brown" far better. Is that a parameter on `character_skin`, or does it stay out of scope?

For Combat, UI+Combat and battle-presentation:
9. **Which choreo style plays "Listen"?** The sheet maps it to the `read` clip (a listening tilt). If Listen gets its own
   style, the clip set needs a 13th clip.
10. **Framing a 2.30 m hero** (§2.5): the battle camera and formation spacing must keep his head and the staff tip in
    frame.
11. **Learned abilities** play the `cast` clip (the imitation). If a learned physical ability should play `attack`
    instead, that is a style choice in `choreo.json`, not a new clip.

For Cinematics:
12. The crest column of §6.2 applied with each `@face` tag (the `crest_raise` shape on the `Crest` mesh), and the 0.25 s
    onset delay of §6.1.

Nothing here needs the human (no SPEC §16 item).
