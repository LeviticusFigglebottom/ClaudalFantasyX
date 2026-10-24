# Ysolde Ysel: Design Sheet

Owner: Character Artist (M3-CHR-01, design). Build: Character Artist (M3-CHR-01). Shaders: Rendering (the existing
`character_*` shaders; no new shader). Story source: [`story/characters/ysolde.md`](../../story/characters/ysolde.md).
Shared conventions are in [`asha.md`](asha.md) §4.2 (masks), §6.2 (face shapes), §8 (LOD rules) and §9 (pipeline), and
the build layout is [`pipeline.md`](pipeline.md) §11-§16 (MPFB2 donor per ADR 0021, the hero layout of §12, body clips of
§13, battle scale of §14, rig guards of §16). This sheet lists only what differs.

**One-line read:** the tallest, straightest and darkest shape in the party. A narrow indigo-black column from a winged
standing collar to an ankle hem, hair pinned high under a silver pin, one salt-white streak at the left temple, a black
lacquer book held shut against the right hip, and the left hand alone gleaming with long curved ink-guards. Indigo-black,
salt-white and gold script.

**Status:** M3 design target (Lead, 2026-10-24: "design sheets first"). Built on the MPFB2 hero path, as Rhen and Toma.

---

## 1. Proportions

| Measure | Value | Notes |
|---|---|---|
| Height | **1.76 m** | (art decision) "Tall and very straight": 13 cm over Asha, level with Rhen, so she reads tall without a hero-height contest. Her pinned knot and pin add 9 cm to the silhouette (1.85 m to the pin tip). |
| Head height | 0.233 m (**7.55 heads**) | The longest-limbed proportion in the party; inside SPEC §7.3's realistic range plus Asha's +2% leg allowance. |
| Shoulder width | 1.58 heads (0.37 m) | Narrow and square. The collar wings carry the width above the shoulder (§2), not the shoulders. |
| Waist / hip | 1.02 / 1.38 heads | Slim. The robe panels hang straight from the hip; no flare. |
| Crotch height | 3.62 heads | Long legs, hidden by the robe, which makes the column longer. |
| Neck length | 0.46 head | Long; the collar frames it. |
| Hands | 0.80 head, long fingers | The left hand is a performance instrument (§3); finger length +4% over the donor. |
| Eyes | The ×1.10 rule (fissure 30 → 33 mm). IPD 61 mm. Slightly hooded upper lids (age 47; §6). | |
| Posture | **Plumb**: spine neutral to slightly extended (chest lifted 2°), chin level to 1° raised, shoulders down and back, weight on both heels equally. | **Idle sway 0.3 of the party default**, the lowest of the living cast (Asha 0.4). She is still by discipline; Sefir (act1_npcs.md §1) is still because nothing in him moves. Keep the two distinct: Ysolde breathes. |

**Age (47):** shown in the textures and the posture, not in the shape: fine forehead lines, crow's feet, nasolabial
folds at 0.4 and a softening at the jawline, through the villager age layer (§9). No stoop, no thinning.

---

## 2. Silhouette from Three Angles

**Read test:** in the flat-black silhouette view at 64, 128 and 256 px she must be identifiable against Asha, Rhen and
Toma (and Liss and Sefir from act1_npcs.md):

| Against | Their read | Ysolde's read |
|---|---|---|
| Asha | Staff line above the head, pale sleeve flag on her right, braid over the left shoulder, A-line skirt. 40% light. | **No pole, no flag.** A closed narrow column with a winged top. The tallest point is the hair pin, centred over the head, not a staff to one side. About 70% very dark: the darkest silhouette in the party, Asha's value opposite. |
| Rhen | Forward lean, lantern bulb over the right shoulder, crossed hooks, short jacket. | Plumb, nothing on the back, robe to the ankle. |
| Toma | Widest trapezoid, shield disc, spear. | Narrowest figure; the collar wings are the only width, and only above the shoulders. |
| Sefir | Floor-length, a gilded bowl-crown behind the head, a gold half-mantle on the right shoulder, pale. | Ankle-length, no crown (her collar is cloth, dark outside, and stops below the ears); no mantle; dark. |

### 2.1 Front (0°)
- A **tall, narrow vertical**: a near-rectangle from the shoulders to the ankle hem, 0.40 m wide at the shoulders and
  0.38 m at the hem. The hem stops 9 cm above the floor so the feet read (soft slippers), never a floor-brushing bell.
- **The collar wings:** a stiff standing collar opens forward from the back of the neck in two curved wings that rise
  from the shoulder line to the lower ear (13 cm at the back, 8 cm at the sides) and stand 4 cm off the jaw. From the
  front it reads as a shallow **V of dark around the face**, so the face is framed like a lamp in a niche.
- **The hair:** drawn up into a high flat knot at the crown, 9 cm tall, with the **Level-pin** through it as a thin
  horizontal-then-vertical spike (§4, item 10). The **salt-white streak** at the left temple (viewer's right) is the
  brightest mark above the shoulders and reads at 128 px.
- **Asymmetry at the hands:** the right hand holds the folded book shut against the right hip (a small dark block
  breaking the robe's edge). The left hand hangs free: the pale turned-back cuff and the **ink-guards** (four curved
  points 4.5 cm past the fingertips) make a small bright claw-shape at mid-thigh.

### 2.2 Three-quarter (45°, her left side toward camera: the hero angle, because she casts with the left)
- The left cuff, the ink-guards and the left collar wing face the camera. The split of the robe's front-left panel
  opens 6–8 cm in the idle, showing the narrower dark trousers beneath, so the column has an inner vertical line.
- The gold-script border runs up the front edge of the robe from the hem to the collar (§3), a thin bright
  vertical along the column.

### 2.3 Profile (90°)
- A plumb line from heel to crown, with the chest slightly lifted and the chin level. The collar wing shows as a
  curved blade behind the jaw; the knot sits over the back of the crown and the pin's spike points back and up at
  20°.
- The book shows as a 4 cm deep block at the hip (closed). The robe's back panels fall straight.

### 2.4 Back (180°, field walking)
- The knot and pin over a plain dark back. The back of the collar is its tallest part (13 cm), so from behind she
  reads as a dark column with a dark rounded "headboard" that the knot rises out of.
- The salt-white cord belt's knot (left hip) and its two cord ends break the back at the waist.

---

## 3. The Asymmetric Hallmark: the Left Hand and the Book

The story gives two hallmarks, and the design pairs them: **the left hand writes, the right hand holds the page.**

- **Ink-guards (left hand only):** four curved metal sheaths, one on each of the index, middle, ring and little fingers
  (the thumb is bare: it steadies the stroke). Each sheath covers the distal phalanx and extends **4.5 cm** past the
  fingertip in a gentle downward curve (radius 6 cm), tapering from 1.2 cm wide at the nail to a blunt 1.5 mm point.
  Outer face `lacquer_black` lacquer; inner face bare `silver` (proposed swatch, §7); a single hairline of `gold_leaf`
  along each spine (the "nib"). These are scholar's tools (story sheet), not weapons: the points are blunt, and no clip
  uses them to strike.
- **The turned-back left cuff:** both robe sleeves are wrist-length and straight. Only the left cuff is turned back
  6 cm to show the salt-white lining, so the casting hand is framed in white. It is the only white below her collar.
- **The folding lacquer book (prop):** an accordion of **12 panels**, each 24 × 12 cm and 3 mm thick, of black lacquer
  over thin wood, hinged with indigo silk. Closed, it is a 24 × 12 × 4 cm block held in the right hand against the hip
  (or hung from the cord belt by a loop at the top-left corner when both hands are needed). **Cast state:** the right
  hand fans it open into a **160° arc of radius 24 cm**, panels standing on edge, the gold script facing the foe; the
  left hand traces over it.
- **The trace glyph on the book and the robe.** Each panel carries one Lamptongue glyph in gold script (original
  letterforms, authored as stroke data in `assets_src/characters/ysolde/motifs/`, never painted). One glyph recurs
  as her costume motif: the **five-stroke path of her Swell input, Glyph Trace** (formulas.md § Swell: down, right, up,
  right, down), written as a brush stroke. It reads as a stepped wave, a tide rising and falling once.
  - **On the robe:** a running border of that glyph, repeated, 2.2 cm tall, up the front-left edge of the robe from hem
    to collar, round the hem of every panel, and on the inner face of the collar wings (so it frames the face).
  - **On the book:** the glyph closes the panel sequence, the twelfth panel, which faces out when the book is shut.
  - **How it echoes the HUD without copying it (M2-UI-03):** the costume glyph is **calligraphy**: tapered entries,
    ink-pooled corners, a stroke weight varying 0.8–2.4 mm, a dry-brush break on the fourth stroke, gold leaf with
    lacquer clearcoat. It is never a constant-width line, never boxed or framed, never `ui_line_gold`, and never shows
    stroke-order numerals or arrows. The UI panel draws its own diagram of the same five directions. The shared idea
    is the stroke order; neither side traces the other's artwork. (A note to UI: if their panel wants the brush
    look, they author it from the same `motifs/` stroke data, not from a render of the costume.)
- **Gold budget:** the script covers about 2.5% of her silhouette (the border is thin), well under the frame's 5%
  with Asha's ≤4% in the same group shot at battle framing. The book open adds about 1% for the length of a cast.

---

## 4. Costume Layers and Materials

### 4.1 Layers (inner to outer)
| # | Piece | Material | Color | Mask channels | Skinning notes (M1-CHR-14 lessons) |
|---|---|---|---|---|---|
| 1 | Under-gown: a sleeveless salt-white shift to the hip, a high round neck under the collar | Fine cotton | `gauze_white` `#EBE7DF` | A 0.3 | Torso only. Visible at the collar's front gap and the left cuff. Armhole dropped **12 cm below the shoulder joint** (the 11.5 cm rule plus margin). |
| 2 | Trousers, narrow, ankle length | Silk twill | `mourning_indigo` `#26243C` (proposed) | A 0.6 | Leg tubes per thigh/shin chain (Rhen's `limb_tube`), crotch blend as Rhen's trousers. These are what keep the robe split (layer 4) from showing bare leg in a stride. |
| 3 | Slippers: soft closed slippers with a thin sole | Indigo leather | `#2E2A3E` | A 0 | Take the feet's weights (as Asha's sandals after M1-CHR-14). |
| 4 | **Long split robe** (the mourning dress) | Heavy silk crepe, matte face, a satin back that shows at the splits and turn-backs | `mourning_indigo` `#26243C`, satin back `mourning_indigo_hi` `#3A3856` (proposed) | R embroidery: the gold-script border (as *raised* thread where the script is couched; see G) · G gold: the script (gold leaf over lacquer size) · A 0.75 | **Split, not a tube** (M1-CHR-14: floor-length tubes clip under linear skinning). From the hip down the robe is **four panels**: front-left, front-right, back-left, back-right, split at both sides to 6 cm below the hip joint and at the front left-of-centre to mid-thigh. Each panel follows its own leg (Asha's `skirt_weights` with a left/right blend only across the back seam) plus 3 panel bones down its centre line. Hem 9 cm above the floor (ankle bone), so a kneel or a stride never drives the hem through the floor. |
| 5 | Robe sleeves (part of 4) | as 4 | as 4; left cuff turned back to the `gauze_white` lining | as 4 | **Dropped-shoulder sleeves** with an underarm gusset: the sleeve seam sits **12 cm below the shoulder joint**, so the arm-to-torso blend happens inside one continuous panel and no armhole edge stands beside a lowered arm. Sleeves straight and only 2 cm off the forearm at the wrist (no hanging sleeve: Asha's right sleeve is the party's flag, and a second long sleeve would blur both reads). Sleeve weighted to the upper arm and forearm, with a 4 cm blend band at the gusset. |
| 6 | **Winged standing collar** | Buckram-stiffened silk, lacquered outside | Outside `mourning_indigo` with a lacquer clearcoat at 0.5; inner face `gauze_white` silk with the gold-script border | B lacquer 0.5 (outside) · G gold (inner border) · A 0.75 (inner) | **Rides the upper torso** (`DEF-spine.003`/`.004`), never the neck or head, so it does not swing with a head turn. Clearance: ≥ **25 mm** from the head skin and hair at a head turn of ±40° and a pitch of −20°/+15° (the clips' range). The front gap is 8 cm wide at the throat. The collar is a garment in `rig_checks.json`, so `garment_in_body` measures it against the head skin. |
| 7 | Cord belt | Salt-white silk cord, 8 mm, two turns, knotted at the left hip; two ends to mid-thigh, each with a small gold-leaf weight (a bead 1.4 cm) | `gauze_white`, weights `gold_leaf` | A 0.8 · G on the weights | Cord ends: 2 × 3 bones (as Toma's sash tails, shorter). |
| 8 | **Ink-guards** ×4 (left hand) | Lacquered metal (§3) | `lacquer_black` / `silver` / a `gold_leaf` hairline | B lacquer · G hairline | Each is **rigid to its finger's distal bone** (`DEF-f_index.03.L` and so on). Props in `rig_checks.json` (`grip_bones` already exempts the hand). The clips leave the fingers at rest, so a closed fist never drives a guard into the palm; any new clip that curls the left fingers must be checked with `rig_probe`. |
| 9 | **Folding lacquer book** (prop) | Lacquered panels, silk hinges (§3) | `lacquer_black`, script `gold_leaf`, hinges `mourning_indigo` | B lacquer 1.0 · G script | One mesh, **one blendshape `book_fan`** (0 closed → 1 the 160° fan), on a prop bone `DEF-book` parented to `DEF-hand.R`. **Offset from the grip:** the closed block sits 1.2 cm proud of the palm surface on the thumb side, so the probe's `prop_in_body` stays at 0 outside the grip bones (Asha's staff lesson: 1 cm off the fist line). |
| 10 | **Level-pin** | Silver, 16 cm, through the knot from front-left to back-right at 20° up; its head is the Order's Level (a 3 cm ring crossed by one bar) | `silver` (proposed) | metallic via ORM (not G) | Rigid on the head bone. Removed in Act II (§5). The Level is correct on Ysolde (she is the Order's), unlike on Toma. |
| 11 | Wedding ring (art decision) | A plain gold band on the right ring finger | `gold_leaf` | G | Tiny; for close-ups only. It ties to Asha's ring band for Corran (asha.md §3.1, S6). A proposal to Narrative (§12). |

### 4.2 What Ysolde does not wear
- **No reach-bands.** She is Ansedran; reach-bands are a Low Reaches custom (bible §5.1).
- **No veil, no gilt line, no mantle.** The Order's ceremonial gold belongs to Sefir and to the rites. Her gold is
  written, not worn as leaf on a surface.

---

## 5. Hair

- **Style (Act I):** black, very long, drawn straight back from the hairline with no parting and wound into a **high,
  flat knot** at the crown (a disc 11 cm across and 9 cm tall, slightly forward of the crown so it sits over the head
  in profile, not behind it). The Level-pin passes through the knot. The hairline is smooth and severe; no strands are
  left free, except the streak.
- **The salt-white streak:** a band 2 cm wide from the left temple back into the knot. It is **ash** worked into the hair
  (story sheet: an Ansedran widow's custom she keeps deliberately), so it is matte: `ash_white` `#D6D2C8` (proposed)
  with the primary highlight off (intensity 0.05) and roughness raised, against the black hair's cool ribbon highlight.
  Build it as its own card group, so its material differs and it never reads as a grey hair.
- **Grey:** 6% of strands `#8C867D` (her age), spread evenly, never at the streak.
- **Cards:** scalp layers pulled back (Asha's scalp layers with a back-swept flow), about 220 cards; the knot as
  coiled ribbons round a disc (`villager_hair`'s `bun` knot, flattened and moved to the crown), 40 ribbons; the streak
  30 cards; 20 flyaways at the knot only (her hair is controlled).
- **Shading:** base `hair_black` `#201A16`; primary tint `#E0D8D0` at 0.35, secondary `#6A4A36` at 0.4.
- **Act II variant (design now, build with the Ch13 content):** the pin is gone; the knot is half unwound, and a loose
  fall of hair drops from the crown to between the shoulder blades on the left side (a 6-bone chain, collision capsules
  on the collar and left shoulder). The streak runs into the fall. Same head, a second hair mesh `HairDown` toggled by
  the scene.
- **Motion:** none on the scalp or knot (head-rigid). The streak is part of the scalp.

---

## 6. Face

### 6.1 Face shape
- **Long oval**, narrow (head width 0.64), with **high, wide cheekbones** (the widest point 0.42 head heights below
  the vertex), a fine straight jaw softening slightly at 47, and a defined chin.
- **Eyes:** almond, a 3° upward outer tilt, with **slightly hooded upper lids** (the crease half hidden); Iris
  `#2C1E16` (dark brown) with a cooler limbal ring `#3E3430`. Lower lids flat and level: she looks *at* people.
- **Brows:** thin, groomed and precisely arched, the arch at the outer third. **Her personal asymmetry: the left brow
  sits 1.5 mm higher at rest** (a permanent faint evaluation; the shape key `brow_outer_up_L` 0.08 is part of her rest
  pose).
- **Nose:** long and straight, a narrow bridge, a defined tip.
- **Mouth:** medium width (0.39 of head width), thin upper lip, a fuller lower lip, corners level to very slightly down
  (`mouth_corner_lift` −0.0005 m). At rest she looks composed, not unkind.
- **Skin:** `skin_ysolde` `#B48A72` (proposed): a cooler, less sun-darkened brown than the Low Reaches cast (Ansedran,
  a scholar indoors). Age layer at 0.4 (§1), no freckles. **No makeup.** At Order rites (Ch13, Ch14, Ch16) she wears no
  gilt line (that is a Cantor's custom, N-04).
- **Close-range stylisation:** the ADR 0019 dialogue finish (painterly 0.6, detail 0.35, `lid_wide` 0.18 at rest) as
  every hero. Check the hooded lids with `lid_wide` 0.18: the rest crease must stay half hidden, or reduce her
  `lid_wide` rest to 0.12.
- **Blend timing:** 0.28 s, measured, with **no overshoot**. Her emotions are held back, not slow: they arrive late
  and leave early.

### 6.2 Emotion tags mapped to Ysolde's face
The 15 tags from `game/data/dialogue/emotions.json`. Weights 0–1, unlisted shapes 0, L/R as L/R. Her rest
`brow_outer_up_L` 0.08 is added to every row.

**Her tells:** she **presses the mouth before anything reaches it** (`mouth_press` appears in nearly every row), and
her feeling shows in the **lids**: sorrow lowers them, anger narrows them, and only real surprise widens them. Her
smile is small and **lifts on the left first** (`mouth_smile` L = R × 1.2). Her laugh is caught and fought (Rhen makes
her laugh, and she resents it): `mouth_press` stays on under the laugh.

| Tag | Shape weights | Ysolde note |
|---|---|---|
| `neutral` | `mouth_press` 0.10 | The composed face: correct, not cold. |
| `soft_smile` | `mouth_smile` 0.18/0.15, `lid_squint` 0.08, `mouth_press` 0.10 | Witheringly polite. Most of her Act I lines. |
| `smile` | `mouth_smile` 0.42/0.35, `cheek_raise` 0.25, `lid_squint` 0.18 | Rare and real; with Asha from Act II. |
| `laugh` | `mouth_smile` 0.70/0.58, `cheek_raise` 0.50, `lid_squint` 0.45, `jaw_open` 0.12, `mouth_press` 0.25 | The fought laugh: mouth kept nearly shut, eyes give it away. Head dips 4° (she looks down, not back). |
| `worried` | `brow_inner_up` 0.40, `brow_down` 0.20, `mouth_press` 0.30 | |
| `sad` | `brow_inner_up` 0.45, `lid_close` 0.30, `mouth_press` 0.25, `mouth_frown` 0.15 | Gaze drops 8°. |
| `grief` | `brow_inner_up` 0.85, `brow_down` 0.35, `lid_squint` 0.35, `mouth_frown` 0.45, `mouth_press` 0.35, `jaw_clench` 0.25 | Reserved: the Sanctum before Ethren (Ch13), the dive release (Ending). Tear layer as Asha's. **Not used at the Corrow Ebbing (Ch9)**: she is the only one who does not cry there; use `cold`. |
| `angry` | `brow_down` 0.60, `lid_squint` 0.45, `mouth_press` 0.40, `nose_sneer` 0.10 | Her Act II fury is precise: narrowed lids, a still mouth, no shouting face. |
| `cold` | `brow_down` 0.20, `lid_close` 0.22, `mouth_press` 0.40 | Her Act I armour, and the Ch9 Ebbing (held, dry-eyed). |
| `surprised` | `brow_inner_up` 0.45, `brow_outer_up` 0.60, `lid_wide` 0.40, `jaw_open` 0.12 | |
| `afraid` | `brow_inner_up` 0.75, `brow_outer_up` 0.30, `lid_wide` 0.50, `mouth_stretch` 0.30, `mouth_press` 0.15 | Rare: for Asha only. |
| `determined` | `brow_down` 0.40, `lid_squint` 0.20, `mouth_press` 0.45, `jaw_clench` 0.15 | Chin lifts 2°. Casting face; the Ch16 denunciation. |
| `tender` | `brow_inner_up` 0.25, `mouth_smile` 0.15/0.12, `lid_close` 0.22 | The Ch4 side scene (re-inking the wake-shell, alone) and Asha in Act III. |
| `guilty` | `brow_inner_up` 0.45, `lid_close` 0.35, `mouth_press` 0.40 | The Cloudloom confession (Act II). Gaze down 12°, not away: she makes herself look back. |
| `exhausted` | `lid_close` 0.40, `brow_inner_up` 0.15, `mouth_press` 0.10 | Head pitch −4°; shoulders stay up. |

---

## 7. Color Callouts

Swatches marked *(proposed)* are not yet in `palette.json`; Art adds them (M3-CHR-01 acceptance), with their
on-screen values measured on the swatch card.

| Area | Swatch | Hex | Share of her silhouette |
|---|---|---|---|
| Robe, sleeves, trousers, collar outside | `mourning_indigo` *(proposed)* | `#26243C` | ~62% |
| Robe satin back at splits and turn-backs | `mourning_indigo_hi` *(proposed)* | `#3A3856` | ~4% |
| Skin | `skin_ysolde` *(proposed)* | `#B48A72` | ~10% (face, neck at the collar gap, hands) |
| Hair | `hair_black` | `#201A16` | ~8% |
| Under-gown, cuff lining, collar inner face, cord belt | `gauze_white` | `#EBE7DF` | ~6% |
| Book, ink-guards (outside) | `lacquer_black` | `#1D1916` | ~3% |
| Salt-white streak | `ash_white` *(proposed)* | `#D6D2C8` | ~0.5% (small, bright, by the face) |
| Gold script, cord weights, ring | `gold_leaf` / `gold_leaf_hi` | `#D4A437` / `#F1D27A` | ~2.5% (+1% with the book open) |
| Level-pin, ink-guard inner faces | `silver` *(proposed)* | `#A9AEB3` | <0.5% |
| Slippers | — | `#2E2A3E` | ~1% |

**Value check:** about 70% very dark and 7% light: the darkest figure in the party (Asha is about 25% dark). The
face, the white collar lining and the streak are the light shapes, all at the top of the column, so her face is the
focal point of her silhouette by value.

**Albedo floor:** `mourning_indigo` (Rec.709 linear luminance about 0.020) is above `lacquer_black` (about 0.010), so it
keeps the albedo-floor rule. **Night risk:** in Ch4's night grade the robe can merge with the night fog
(`#22354F`). The silk sheen (A 0.75), the satin back at the splits and the rim light must hold the edge; Rendering checks
her in the Ch4 dock and ferry framings (M3-CHR-01 shots).

---

## 8. Budgets

Sheet targets follow SPEC §7.3 (40–70k per hero). The as-built column is what Rhen and Toma came in at on the same
pipeline (rhen_review.md §2, toma_review.md §2): **the 5 MB GLB cap, not the triangle count, is the binding limit** (every
Head vertex carries the 40 morph targets).

### 8.1 Triangles (LOD0 target 60,000; hard ceiling 70,000)
| Part | Target | As-built expectation |
|---|---|---|
| Head and face (skin, ears, lashes, brows, mouth; donor face subdivision) | 21,000 | ~20,900 (as Rhen and Toma) |
| Eyes | 2,216 | 2,216 |
| Visible body skin (neck at the collar gap, hands, a little ankle) plus the hidden legs kept under the robe (M1-CHR-14) | 5,500 | |
| Hair (scalp, knot, streak, flyaways) and the Level-pin | 6,500 | Not on the Head object, so no morph cost |
| Robe (four panels, sleeves, the turn-back cuff) | 9,000 | |
| Collar | 2,200 | |
| Under-gown, trousers, slippers, cord belt | 4,800 | |
| Ink-guards ×4 | 900 | |
| Book (12 panels with bevels and hinges; the `book_fan` shape) | 3,200 | |
| Ring | 100 | |
| **Total** | **55,416** | Leaves 4.6k under the target for the Act II `HairDown` mesh (built later, about 4k) |

**LODs:** LOD1 28k (from 6 m; the battle actor, pipeline.md §14), LOD2 13k, LOD3 5k. **LOD1 keeps:** the collar wings,
the knot and pin, the streak, the ink-guard points, the book block, and the robe splits. Cut detail (flyaways, the
ring, hinges, script relief), never shape.

### 8.2 Textures
| Set | Resolution | Maps | Notes |
|---|---|---|---|
| Face and head | 2K ×4 (albedo, normal, ORM, skinmask) | | As built for Rhen and Toma: a 4K PNG passes the 5 MB per-binary cap (ADR 0005). |
| Body | 1K ×4 | | |
| Costume atlas (robe, collar, gown, trousers, belt, slippers) | 2K (ORM 1K) + clothmask 2K | albedo, normal, ORM, clothmask | The gold-script border needs ≥ 18 px/cm (a 2.2 cm glyph over about 40 px): give the border strips a larger UV share. |
| Props (book, ink-guards, pin, ring) | 2K shared | albedo, normal, ORM, clothmask (B lacquer, G gold) | The book's script at ≥ 12 px/cm. |
| Hair | the shared hair atlases (`assets/characters/asha/textures/`) | | The streak uses the same atlas with its own material. |
| Eyes | shared 1K | | |

---

## 9. Modeling Notes (deltas from Asha §9 and pipeline.md §12)

- **Folder:** `assets_src/characters/ysolde/` on the §12 layout: `build_ysolde.py` imports `build_asha` as a helper
  library; `ysolde_params.json`, `ysolde_costume.py`, `ysolde_hair.py`, `ysolde_props.py` (book, guards, pin, ring),
  `ysolde_textures.py`, `write_materials.py`, `motifs/` (the glyph stroke data).
- **Params (`ysolde_params.json`, the bb_params block; face sliders relative to the donor, 1.0 / 0.0 = unchanged):**

  | Key | Value | | Key | Value |
  |---|---|---|---|---|
  | `height_m` | 1.76 | | `eye_scale` | 1.10 |
  | `heads_tall` | 7.55 | | `ipd_m` | 0.061 |
  | `shoulder_width_heads` | 1.58 | | `eye_tilt_deg` | 3.0 |
  | `chest_width_heads` | 1.16 | | `canthus_offset_m` | 0.001 |
  | `chest_depth_heads` | 0.86 | | `jaw_width` | 0.92 |
  | `waist_width_heads` | 1.02 | | `cheekbone_height` | 0.006 |
  | `hip_width_heads` | 1.38 | | `cheekbone_width` | 1.06 |
  | `crotch_height_heads` | 3.62 | | `chin_size` | 1.02 |
  | `arm_span_ratio` | 1.01 | | `nose_bridge_width` | 0.92 |
  | `hand_length_heads` | 0.80 | | `nose_tip_projection` | 1.04 |
  | `foot_length_ratio` | 0.148 | | `lip_fullness` | 0.68 |
  | `neck_length_heads` | 0.46 | | `lip_close` | 0.6 |
  | `neck_width_ratio` | 0.48 | | `lip_seal` | 0.96 |
  | `head_width_ratio` | 0.64 | | `lip_lower_fullness` | 0.66 |
  | `femininity` | 0.95 | | `mouth_corner_lift` | −0.0005 |
  | `muscle` | 0.25 | | `brow_ridge` | 0.9 |
  | `mass` | 0.18 | | `donor_mix_african` | 0.15 |
  | `breast` | 0.32 | | `donor_mix_asian` | 0.6 |
  | `arm_abduction_deg` | 47.0 | | `donor_mix_caucasian` | 0.25 |
  | `skin_hex` | `#B48A72` | | | |

  (Starting values for the build; tune against the face shots, as Asha's were.)
- **Age layer on a hero:** `ysolde_textures.py` imports the villager age terms (`villager_textures`: forehead lines,
  glabella, nasolabial and crow's feet in the normal map, a little darker in the albedo) at 0.4 and calls
  `asha_textures.skin_maps`. No shared module changes; if the age terms need a hook in `asha_textures`, file it as a
  shared-module change that re-verifies every hero job.
- **Robe panels:** pattern-as-data (asha.md §9.2): four hip-down panels, a bodice front-left, front-right and back,
  two dropped-shoulder sleeves with gussets, the turn-back cuff (a second, inverted cuff band on the left sleeve only),
  and the collar (two wing pieces and a back piece, solidified 2.5 mm, edge bevel 0.8 mm so it catches a highlight line).
  The border motif is rasterised into the clothmask (R and G) from `motifs/`, as Asha's bands.
- **Rig extras (on `bb_rig.build_game_skeleton`, as `build_toma.add_bones`):** robe panels 4 × 3 bones; cord ends 2 × 3;
  `DEF-book` (prop, child of `DEF-hand.R`); `DEF-pin` is not needed (the pin is head-rigid). The `HairDown` fall (Act II)
  adds a 6-bone chain then. Fingers stay at rest in every clip unless a clip says otherwise.
- **Rig guards:** add a `ysolde` entry to `tools/dev/rig_checks.json`: `garments` [`Costume`, `Collar`], `props`
  [`Book`, `InkGuards`, `Pin`], `braid` null, seam groups as Toma's plus `Collar`. Ratchets only with a written reason.
- **Blender job:** `ysolde` in `tools/dev/blender_builds.json` with `"threads": 4`, sources including
  `assets_src/characters/asha/**`, `rhen/**` (limb tubes), `toma/**` (sash tails), `villagers/**` (the knot and the age
  terms), `base_body/**` and `third_party/mpfb2/**`; two runs must be byte-identical. Texture runs set
  `asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS` (M1-CHR-15 note) so the PNGs are host-independent.

---

## 10. Clips and Persona (hero_clips, pipeline.md §13)

**Persona:** `"ysolde": {"sway": 0.3, "lean": -1.0, "staff": False, "arms_down": 34.0, "book": True, "breath": 1.0}`.
- `lean` −1.0: the 2° lifted chest reads as a hair of backward lean from the ankles (negative is a new value for
  `lean`; check `walk_pose` and `stand` accept it).
- `arms_down` 34: arms closer to the body than Asha's 40 (her sleeves are narrow, and her hands are held, not hung).
- **`book` (new key):** the right forearm flexes 65° so the closed book rests against the right hip, the hand turned
  palm-in; the walk's right-arm swing drops to 0.2 (like `staff` at 0.35). Added to `hero_clips.stand` the way
  `staff` is. No `stance` (her feet are together: ankles at 0.9× the shoulder-joint spacing is the bind pose's natural
  stand).
- **`breath` (new key, default 1.0):** scales the idle's breath terms (`DEF-spine.003` and the left upper arm), which
  are fixed today. Ysolde keeps 1.0; it exists for Sefir (act1_npcs.md §1, 0.0). Asha's, Rhen's and Toma's libraries
  must stay byte-identical with the default.

**Clips (Act I, from the beats):**
| Clip | Loop | Beat | Notes |
|---|---|---|---|
| `idle` | yes | everywhere | Stillness by discipline: sway 0.3, breath visible. |
| `walk`, `run` | yes | field | Short, even stride (her robe panels). The run is a fast walk-run with the book held to the hip; she never sprints with her arms. |
| `talk` | yes | everywhere | Only the **left** hand lifts, palm down, to emphasise; the right keeps the book. |
| `board_step` | no | Ch4 dawn ferry: she boards by Order appointment | One step up (18 cm) onto a deck, no hand on the rail, then she settles plumb. |
| `vigil_book_shut` | yes | Prologue: "Ysolde with her book shut" | Both hands on the closed book in front, at the waist; head bowed 6°; sway 0.15. |
| `reink_shell` | no, holds | Ch4 side scene: she re-inks Asha's wake-shell by lamplight, alone | **Standing** at the shrine wall (art decision: the shells are set in the wall at chest height, so no kneel): the right hand holds the shell's place (open palm on the wall), the left hand writes with the index guard as the nib, small strokes. The book hangs from the belt. |
| `stand_apart` | yes | Ch4 Pilgrim's Wake: she stands apart | The idle with the head turned 15° toward the feast and the eyes down; arms folded at the waist, left over right. |
| `book_fan` | no | battle and the Prologue montage | The right hand fans the book open into the 160° arc in 0.5 s (the `book_fan` shape 0 → 1 over the same keys), the left hand rises to it. Holds. |
| `cast_glyph` | no | battle (Spar-Wraith, Ch4, introduces her magic; Ch8) | From `book_fan`: the left hand traces the five strokes (down, right, up, right, down) in 1.2 s, about 12 cm per stroke, in front of the open book; a 0.2 s hold; the book folds back (shape 1 → 0) over 0.4 s. The five strokes are the glyph's (§3), so the battle and the HUD agree. |

Battle-scale actor: `game/characters/heroes/ysolde_battle.tscn` on `ysolde_lod1.glb` (pipeline.md §14). The battle's
cast and Swell animations beyond `book_fan` and `cast_glyph` are a later battle-animation task.

---

## 11. Acceptance Checklist (M3-CHR-01)

- [ ] Silhouette test in the flat-black view at 64, 128 and 256 px beside Asha, Rhen and Toma: identifiable by the column,
      the collar wings, the knot and pin, and the left-hand points; and beside Sefir (no crown, no mantle).
- [ ] Every number in §1 and §9 is in `ysolde_params.json`; the build is headless and byte-reproducible (two runs, same
      sha256), job `ysolde` with `"threads": 4`.
- [ ] Shared modules imported, not copied; any shared change re-verifies the `asha`, `rhen`, `toma` and `villager_*`
      jobs.
- [ ] All 40 shapes (30 expression, 10 visemes); `game/levels/_tests/characters/ysolde/ysolde_face_poses.json` with the 15
      tags of §6.2, including the rest `brow_outer_up_L` 0.08.
- [ ] Robe split into four leg-following panels with panel bones; dropped-shoulder sleeves with the seam ≥ 11.5 cm below
      the shoulder joint; collar on the upper torso with ≥ 25 mm head clearance across the clips; book 1.2 cm off the
      grip; ink-guards rigid to the distal bones.
- [ ] `tools/dev/rig_checks.json` has a `ysolde` entry; `python3 tools/dev/rig_probe.py --hero ysolde --report` passes
      the defaults (3 mm penetration, 0.5 mm seams, 0 exposed boundary vertices, clean weights), or each ratchet is
      pinned with a viewed reason; `tools/tests/test_rig_integrity.py` covers her.
- [ ] LOD0 ≤ 60k (ceiling 70k), LOD1 ≈ 28k; `ysolde.glb` < 5 MB, `ysolde_lod1.glb` < 1.5 MB; every PNG < 5 MB.
- [ ] Gold ≤ 2.5% of her silhouette closed and ≤ 3.5% open; the costume glyph is brush calligraphy (§3), not a
      reproduction of any UI panel art.
- [ ] Proposed swatches added to `palette.json` by Art with on-screen values; no albedo below `lacquer_black`.
- [ ] PROVENANCE rows for every new output (GLBs, textures, materials, clips, face poses).
- [ ] Body clips of §10 in `assets/characters/ysolde/anim/ysolde_clips.tres` via `hero_clips.py --hero ysolde`, with
      Asha's, Rhen's and Toma's libraries byte-identical after the `book` and `breath` keys land;
      `tools/tests/test_hero_clips.py` checks the book at the hip and the `cast_glyph` stroke order.
- [ ] Review stage `game/levels/_tests/characters/ysolde/` on `asha_stage.gd`; shots `ysolde_front`, `ysolde_back`,
      `ysolde_three_quarter`, `ysolde_face`, `ysolde_face_stylized`, `ysolde_silhouette_lineup`, `ysolde_clip_cast_glyph`,
      `ysolde_clip_reink_shell`, `ysolde_night_ch4` (the night-grade edge check of §7). Baselines viewed and approved.
- [ ] `docs/kb/art/characters/ysolde_review.md` written (strict SPEC §14 assessment), and a handoff.

---

## 12. Open Questions

For Narrative (not the human):
1. **The wedding ring** (§4, item 11): may Ysolde wear Corran's ring? It ties to Asha's ring band (asha.md §3.1, S6:
   "interlocked rings in gold thread only, for Corran's ring"), and it gives the Ending's release of Ethren a prop. If
   the ring band means Corran's *own* ring is in his temple, she wears none.
2. **The streak is ash** (story sheet: "a single streak of salt-white ash"). Art reads it as literal ash renewed by
   custom, matte, not grey hair. Confirm, or it becomes a white lock of hair (glossier, same shape).
3. **Ch4 re-inking is staged standing at the shrine wall** (art decision). If Cinematics wants her kneeling, the robe
   panels already allow it; the `reink_shell` clip changes, not the costume.

For Art Director:
4. The five proposed swatches (`mourning_indigo`, `mourning_indigo_hi`, `skin_ysolde`, `ash_white`, `silver`).

Nothing here needs the human (no SPEC §16 item).
