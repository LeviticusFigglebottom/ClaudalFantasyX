# Act I Named Characters: Sefir, Liss, Tavi Orse, Mother Kell (Design Sheets)

Owner: Character Artist (M3-CHR-02, M3-CHR-03, M3-CHR-04). Shaders: Rendering (the existing `character_*` shaders).
Shared conventions: [`asha.md`](asha.md) §4.2 (masks), §6.2 (face shapes), §8 (LOD rules), §9 (pipeline); hero layout
[`pipeline.md`](pipeline.md) §12-§14 and §16; villager path pipeline.md §15 and [`villagers_review.md`](villagers_review.md).
Story sources: [`sefir_aurane.md`](../../story/characters/sefir_aurane.md), [`liss_varrow.md`](../../story/characters/liss_varrow.md),
[`rhen_sallow.md`](../../story/characters/rhen_sallow.md) (Mother Kell, Tavi), [`act_outline.md`](../../story/beats/act_outline.md)
Ch1, Ch6-Ch8, ADR 0017, ADR 0020 (h), ADR 0022 and its sweep-G/H/I/J notes, decisions_log N-12, N-20, N-24, N-25.

Where the story is silent, the choice is marked **(art decision)**.

**Status:** M3 design target (Lead, 2026-10-24: "design sheets first"). Ysolde has her own sheet ([`ysolde.md`](ysolde.md)).

---

## 0. Which path each one takes

| Character | Path | Why |
|---|---|---|
| **Sefir Aurane** | **Hero** (§12 layout, face subdivision, 4-sheet textures) | The antagonist: dialogue close-ups from Ch6, the Ch13 and Ch16 confrontations, and the final boss's battle actor (pipeline.md §14). |
| **Liss Varrow** | **Hero** (not the villager path the brief expected) | **She is a party member**, not an NPC: she joins in Ch6, has a battle niche, a Swell input (the reel-stop), a speaker id and portrait in `speakers.json`, and the game's rawest grief scenes (Ch11, Ch13-Ch15). She needs the hero face, the 40 shapes with morph normals on all of them, and the rig guards. |
| **Tavi Orse** | **Villager** (pipeline.md §15) | A Ch7 speaker at medium range: the crowd, the naming rite and the moorings scene. One hard beat ("Kell couldn't swim") is staged on Rhen's face with Tavi over-shoulder (a recommendation to Cinematics, §3.6). |
| **Mother Kell** | **Villager** | A Ch1 side-scene speaker: the wick is a hands shot and a medium two-shot. The villager face at head-and-shoulders range is "passable for NPCs" (villagers_review.md §4), which fits a short, warm scene. |

The villager path's own limits apply to Tavi and Kell: age lives in the textures, not the shape; short hair is a little
flaky close up; no props in the GLB (props go on a `BoneAttachment3D` in the scene, as the Reed's broom).

---

## 1. High Warden Sefir Aurane (hero path)

**One-line read:** a tall, slender, perfectly upright man who does not move at all. A gilded shallow bowl stands on
edge behind his head, a stiff gold-scaled half-mantle covers the right shoulder, and plain pale-blue silk falls straight
to the floor on the left; long silver-white hair hangs loose and still. Gold, ivory and pale still-water blue.

### 1.1 Proportions
| Measure | Value |
|---|---|
| Height | **1.88 m** (art decision: one centimetre under Toma, so he stands eye to eye with the tallest guardian but reads slender, not broad) |
| Head height | 0.246 m (**7.65 heads**: the most elongated in the cast, inside SPEC §7.3) |
| Shoulder width | 1.75 heads (0.43 m), plus the mantle's 6 cm on the right |
| Waist / hip | 1.10 / 1.32 heads |
| Hands | 0.82 head, long and fine |
| Eyes | The ×1.10 rule. IPD 63 mm. |
| Posture | **Plumb and still.** No sway, **no breath** (story: "his breathing should be *absent*"), no weight shift. Hands joined loosely before the navel, right over left. Chin level. |

**Age:** about 1,040, ageless on screen. **No age layer at all** (art decision): no lines, no spots, no grey. His hair is
silver-white by nature of what he is, not by age texture.

### 1.2 Silhouette
- **Front:** a tall column, wider on the right shoulder (the mantle, viewer's left) and falling straight on the left.
  Behind the head, the **bowl-crown** makes a large open disc 34 cm across, tipped on edge (§1.3), the highest and
  widest shape above his shoulders. Loose hair falls to mid-back and frames the face in two straight lines.
- **Three-quarter (hero angle, his right toward camera):** the mantle faces the camera, a scaled gold shell from the
  neck to above the elbow; the crown's concave face catches light behind the head.
- **Profile:** a plumb line; the crown shows as a thin curved blade 6 cm deep standing 4 cm behind the back of the head;
  the hair falls straight between crown and back.
- **Back:** the crown's convex back (gilded, plain), the hair's long fall, the mantle's back half on the right.
- **Read test (64 px):** a vertical figure with a disc behind the head and one heavy shoulder. Against Ysolde (dark
  column, winged collar, no disc) and Asha (staff line, sleeve flag), he is the only figure with a disc behind the head.
  Against Toma's pauldron (on the *left*, red, lifted) the mantle is on the *right*, gold, and lies close.
- **Echo watch (the inspiring game's cleric antagonist, described in words only):** that figure is known by sculpted,
  upswept hair and markings on the face and arms. Sefir has neither: plain loose hair, a clean face, no markings, no
  half-bare chest. Keep it so in every revision.

### 1.3 Asymmetric hallmark: the half-mantle and the bowl-crown
- **Half-mantle (right shoulder only):** a stiff lacquered shell over the right shoulder, from the base of the neck to
  9 cm above the elbow, and down the chest and back to mid-ribcage, cut in a curve. It is worked with **tiny overlapping
  Level symbols like fish scales** (story sheet): about 900 scales, each an 18 mm Level (ring and bar), laid in rows
  like a fish's flank, **gold leaf on each scale, `lacquer_black` in the recess between scales**, so the gold coverage is
  about 55% of the mantle's area. The scales are normal-map and mask detail on a smooth shell (3.5k triangles), never
  geometry. The lower edge flares 4 cm off the arm so the arm can come forward to 60° without passing into it.
- **Bowl-crown:** a gilded bowl **34 cm across and 6 cm deep, tipped on edge** behind the head, its concave face toward
  the back of his head (story sheet: "a low halo-crown shaped like a shallow bowl tipped on edge"). It is held by a thin
  gilt band round the back of the skull at the occiput, so it sits 4 cm off the hair. It echoes Ansedra's bowl-domes and
  the Level itself (a circle is a bowl seen from above). Its rim is plain; its concave face is burnished `gold_leaf_hi`
  so it lights his head from behind in a key-lit shot (Rendering: no emission; it is reflective, never glowing).
- **The left side:** plain pale-blue silk, falling straight to the floor (§1.4). No ornament at all. The contrast of the
  heavy right and the empty left is the read.

### 1.4 Costume layers and materials
| # | Piece | Material | Color | Masks | Skinning notes (M1-CHR-14 lessons) |
|---|---|---|---|---|---|
| 1 | Under-robe, wrist-length sleeves, a high round collar | Ivory silk | `ivory_silk` `#E2D9C6` (proposed) | A 0.8 | Torso and sleeves; dropped-shoulder sleeve seam **12 cm below the shoulder joint**, gusset. |
| 2 | Trousers, full length, loose | Ivory silk | `ivory_silk` | A 0.8 | Leg tubes; they show at the over-robe's splits instead of leg. |
| 3 | Slippers, closed, thin-soled | Ivory leather | `#D6CCB8` | A 0 | Feet weights. |
| 4 | **Over-robe** (the "pale-blue silk falling straight to the floor") | Heavy silk satin | `still_blue_silk` `#9FBCC8` (proposed) | A 0.85 | **Split, not a tube.** From the hip down, four panels: front split at the centre to mid-thigh, sides to 6 cm below the hip joint. Each panel follows its own leg (`skirt_weights`), plus **4 panel bones** each (they are longer than Ysolde's). **Hem 1.5 cm off the floor at rest:** it reads floor-length on camera; his clips barely lift the feet (§1.8), and the panels clear a step. The left panels are stiff (spring stiffness 0.8, damping 0.9): they hang plumb. |
| 5 | **Half-mantle** | Lacquered shell, gold leaf scales (§1.3) | `gold_leaf` scales, `lacquer_black` recesses, a 1 cm `gold_leaf_hi` edge | B lacquer 1.0 · G gold on the scales and edge | One hinge bone `DEF-mantle` (as Toma's pauldron, a 6° hinge), weighted half to `DEF-shoulder.R`, half to `DEF-spine.003`. The arm under it is the probe's `skin_through_garment` worry: clearance 25 mm between the mantle's inner face and the shoulder skin at rest. |
| 6 | **Bowl-crown** and its band | Gilt metal | `gold_leaf` / `gold_leaf_hi` (concave face) | G gold (metallic 1, roughness 0.22 on the concave face) | Rigid on the head bone (`DEF-spine.006`); prop bone `DEF-crown` for the boss phases. Clearance from the mantle ≥ 30 mm at a head pitch of −20° and a yaw of ±40°. |
| 7 | Hands | Skin | — | — | Rings: none (art decision). His fingertips carry VFX markers (`DEF-f_*.03.L/R`) for the "motes at the fingertips when angered" (story sheet). |

**Gold budget (an open item for the Art Director):** mantle plus crown are about **7% of his silhouette**. In Act I's
framings (the barge in a medium-wide, Ch6) he is about 4–8% of the frame, so he adds 0.3–0.6% gold: well inside 5%. In
the Ch13 and Ch16 close-ups, a waist-up of Sefir alone can reach **6–7% gold**. Options: (a) a written exception for
Sefir's close-ups ("the Order's gold, on its maker"), (b) mantle gold coverage down to 40% (more black recess). The
sheet asks the Art Director to choose before M3-CHR-02's shots are approved.

### 1.5 Hair
- **Style:** silver-white, very long, straight and loose, parted at the centre, to mid-back (65 cm from the crown).
  Two lengths fall forward over the collarbones and frame the face; the rest falls behind, under the crown's disc.
- **Color:** `hair_silver` `#CFCAC0` (proposed; under the albedo ceiling), primary highlight `#F2F2F2` at 0.4 (cool),
  secondary `#9A948A` at 0.3.
- **Cards:** about 300 scalp cards (back-swept from a centre part), a back fall of 6 strand groups and a front fall of 2,
  about 10k triangles in all. Hair is not on the Head object, so it costs no morph targets.
- **Motion (a revenant tell):** chains of 5 bones per group, **stiffness 0.85 and a wind response of 0.1×** the global
  wind (party heroes take 0.25–0.6). His hair barely moves in the wind that moves everyone else's. Collision capsules on
  both shoulders, the mantle and the upper back.
- **Rig guards:** the hair groups go in `garments` for Sefir (`HairBack`), so long hair passing through the mantle or the
  shoulders in a head turn shows up in `garment_in_body` and is fixed by weights, not hidden.

### 1.6 Face
- **Shape:** long, handsome and ageless: high cheekbones, a straight nose with a narrow bridge, a clean defined jaw and
  chin, a full but closed mouth with a faint upturn at rest (his warmth is real). Brows straight and level, ash-silver
  `#B6B0A6`.
- **Eyes:** pale grey-green iris `#6F7E78`, a darker limbal ring `#4A5652`. **Act II tell (story sheet: "his eyes catch
  light like a still pool"):** a material variant `sefir_eye_still` with the cornea's specular raised and the iris
  roughness lowered, so the environment reflects in the eye like a mirror. Act I uses the normal eye.
- **Skin:** `skin_sefir` `#C29C84` (proposed): Iskarran and sunless, a pale warm olive. No age layer, pores at 0.6 of the
  heroes' strength (he is *too* smooth by design; the ADR 0019 painterly finish suits him). No freckles, no scars.
- **His tell is symmetry (art decision):** he is the only face in the cast with **no left/right difference** in any
  pose (every other sheet gives a personal asymmetry). Combined with the absent breath and a slow blink (one every
  10–14 s: a per-actor `blink` interval in `sequencer.json`, a Cinematics setting), it reads as composure first and as
  wrongness on a second look.
- **Blend timing:** 0.40 s, the slowest in the cast, no overshoot.
- **Close range:** ADR 0019's dialogue finish.

**Emotion tags** (all 15 shipped; the ones Act I uses are marked ●):
| Tag | Shape weights (symmetric) | Use |
|---|---|---|
| `neutral` ● | `mouth_smile` 0.08 | His rest face: faintly warm. The half-beat on Kerrid and the look at Liss's crate are this face plus a gaze; nothing else moves. |
| `soft_smile` ● | `mouth_smile` 0.30, `cheek_raise` 0.12, `lid_squint` 0.08 | Humble, witty. The gentle rebuke of the Inquisitor is `soft_smile` with `brow_down` 0.10 through `@face`: he rebukes kindly. |
| `smile` ● | `mouth_smile` 0.55, `cheek_raise` 0.35, `lid_squint` 0.20 | Warm; with Rhen ("an amusing young man"). |
| `laugh` | `mouth_smile` 0.70, `cheek_raise` 0.50, `jaw_open` 0.18, `lid_squint` 0.35 | Quiet and brief; head does not tilt. |
| `worried` | `brow_inner_up` 0.25, `mouth_press` 0.15 | Barely used. |
| `sad` | `brow_inner_up` 0.60, `lid_close` 0.28, `mouth_smile` 0.05, `mouth_press` 0.12 | "Public sorrow" at the wedding (Ch14): a sad face that keeps a trace of smile. M4-A2P-055: raised from 0.35/0.20 so it reads in Ch16's 85 mm temptation (C12, C17). |
| `grief` | `brow_inner_up` 0.60, `lid_close` 0.30, `mouth_frown` 0.20 | Only for Kesh in Ch21. |
| `angry` | `lid_squint` 0.12, `mouth_press` 0.20 | **His anger is almost nothing on the face**: the fingertip motes (VFX) carry it. |
| `cold` | `brow_down` 0.12, `mouth_press` 0.25, smile 0 | Ch16, when Asha refuses. |
| `surprised` | `brow_outer_up` 0.30, `brow_inner_up` 0.20, `lid_wide` 0.20 | Ysolde's rage (Act II) is the one thing that surprises him; small. |
| `afraid` | `brow_inner_up` 0.40, `lid_wide` 0.30 | Not used by the story; shipped for completeness. |
| `determined` | `brow_down` 0.15, `mouth_press` 0.20, `mouth_smile` 0.05 | Ch21, reaching into the heart. |
| `tender` ● | `brow_inner_up` 0.35, `mouth_smile` 0.35, `lid_close` 0.22, `cheek_raise` 0.15 | Ch6: "he knelt beside Asha's mother once and says so with real tenderness". M4-A2P-055: raised from 0.22/0.22/0.18 for the warm temptation at 85 mm (Ch16 C12). |
| `guilty` | `brow_inner_up` 0.20, `lid_close` 0.20 | Not used; shipped. |
| `exhausted` | `lid_close` 0.50, `mouth_smile` 0.20, `brow_inner_up` 0.10 | **The last expression is relief** (Defeat): staged as `exhausted` with the smile. |

### 1.7 Palette
| Area | Swatch | Hex | Share |
|---|---|---|---|
| Over-robe | `still_blue_silk` (proposed) | `#9FBCC8` | ~40% |
| Under-robe, trousers, slippers | `ivory_silk` (proposed) | `#E2D9C6` | ~15% |
| Hair | `hair_silver` (proposed) | `#CFCAC0` | ~18% |
| Skin | `skin_sefir` (proposed) | `#C29C84` | ~8% |
| Mantle and crown gold | `gold_leaf` / `gold_leaf_hi` | `#D4A437` / `#F1D27A` | ~7% (§1.4 gold budget) |
| Mantle recesses | `lacquer_black` | `#1D1916` | ~4% |
| (Act I frame note) | | | color_script Ch6: "the only clean white in the frame". His ivory and pale blue are the brightest cloth in the Brine Shoals; keep them under the albedo ceiling (`#EBE7DF`). |

**Value:** about 75% light. The lightest figure in the cast, as Ysolde is the darkest; side by side at the Choir (Ch16)
they are a white figure and a black one.

### 1.8 Clips and persona
**Persona:** `"sefir": {"sway": 0.0, "lean": 0.0, "staff": False, "arms_down": 30.0, "breath": 0.0, "hands_joined": True}`.
- `breath` 0.0 (new key, see ysolde.md §10): the idle has no breath term at all. `sway` 0.0 removes the weight shift. His
  idle is a held pose; **that is intended** (story), and the review must not "fix" it.
- **`hands_joined` (new key, art decision):** both forearms flex about 75° and the hands meet before the navel, right
  over left; walking arm swing 0.

| Clip | Loop | Beat (Act I unless marked) | Notes |
|---|---|---|---|
| `idle` | yes | Ch6, on the barge and after | No motion. The loop exists so the AnimationPlayer has something to hold. |
| `talk` | yes | Ch6 | The left hand parts from the right and opens 10° once per loop; the head moves ≤ 1°. The least gesture in the cast. |
| `raise_palm` | no | Ch6: "He stops the brine-branding of the captured wrights with one sentence" | The Order's gesture (bible §4: palms flat, face down, lowered slowly, "settling the water"), with **the left palm only** (art decision: the plain side, free of the mantle; Toma's `palms_level` is also left-handed, which keeps the gesture's grammar). The palm rises flat to chest height in 0.6 s, holds through the sentence, then lowers over 2.4 s. |
| `incline_head` | no | Ch6: to Asha, before "I knelt beside your mother" | A 10° bow and a 3° tilt, held 1 s, rising over 0.8 s. |
| `glance` | no | Ch6: the half-beat on Kerrid; the look at Liss's crate "a moment too long" | Head and eyes turn 20–25° and back; the body does not follow. Two variants by the `@mark`; the hold is the Cinematics `@wait`. |
| `pivot` | no | Ch6: on the poled barge, he turns to the shore | A 30° turn in place, heels pivoting, no step, no bob (the barge does the travelling). |
| `walk_glide` | yes | Act II (Ch13 onward); specify now, build with the Ch13 content | A 14° stride, no vertical bob, hips level, no arm swing (hands joined). |

Battle actor (Act III final boss): `game/characters/heroes/sefir_battle.tscn` on `sefir_lod1.glb`, later.

### 1.9 Budget
**LOD0 target 62,000** (ceiling 70k): head and face 21,000 · eyes 2,216 · body skin (hands, neck, hidden legs kept) 4,500 ·
hair 10,000 · under-robe and trousers 4,000 · over-robe panels 9,500 · mantle 3,500 · crown and band 1,500 · slippers 800 ·
total about 57,000. LOD1 28k (keeps the crown disc, the mantle outline, the hair's two front falls), LOD2 13k, LOD3 5k.
**Textures:** head 2K ×4, body 1K ×4, costume 2K (ORM 1K) with the mantle's scales at ≥ 16 px/cm (each 18 mm scale about
30 px), hair from the shared atlases, eyes shared 1K plus the `sefir_eye_still` variant (a material, not a new map).
GLB < 5 MB.

### 1.10 Modeling notes (deltas from pipeline.md §12)
- **Folder** `assets_src/characters/sefir/`: `build_sefir.py` on `build_asha`; `sefir_params.json`; `sefir_costume.py`
  (robe panels on `asha_costume`; the mantle as a lofted shell like `toma_costume`'s pauldron lames, without the chisel
  pass); `sefir_props.py` (the crown); `sefir_hair.py`; `sefir_textures.py`; `write_materials.py`; `motifs/` (the
  Level-scale tiling as vector data, never painted).
- **Params (starting values):** `height_m` 1.88, `heads_tall` 7.65, `shoulder_width_heads` 1.75, `chest_width_heads`
  1.24, `chest_depth_heads` 0.9, `waist_width_heads` 1.10, `hip_width_heads` 1.32, `crotch_height_heads` 3.7,
  `arm_span_ratio` 1.01, `hand_length_heads` 0.82, `neck_length_heads` 0.44, `neck_width_ratio` 0.52, `head_width_ratio`
  0.64, `femininity` 0.05, `muscle` 0.35, `mass` 0.15, `breast` 0.0, `eye_scale` 1.10, `ipd_m` 0.063, `eye_tilt_deg` 1.0,
  `jaw_width` 0.98, `cheekbone_height` 0.006, `cheekbone_width` 1.05, `chin_size` 1.02, `nose_bridge_width` 0.92,
  `nose_tip_projection` 1.02, `lip_fullness` 0.85, `lip_close` 0.6, `lip_seal` 0.96, `lip_lower_fullness` 0.75,
  `mouth_corner_lift` 0.0005, `brow_ridge` 0.95, `donor_mix_african` 0.1, `donor_mix_asian` 0.3, `donor_mix_caucasian`
  0.6, `skin_hex` `#C29C84`. Symmetric face: no asymmetric slider anywhere.
- **Rig extras:** over-robe panels 4 × 4; `DEF-mantle` (hinge); `DEF-crown` (prop, head child); hair 8 groups × 5.
- **Rig guards:** `sefir` in `rig_checks.json`: `garments` [`Costume`, `Mantle`, `HairBack`], `props` [`Crown`],
  `braid` null.
- **Blender job:** `sefir`, `"threads": 4`, sources including `asha/**`, `rhen/**`, `toma/**`, `base_body/**`,
  `third_party/mpfb2/**`; byte-identical across two runs; `PRE_ROUND` set in the texture run.
- **For Rendering and Environment (not this build; tasks to file):** his reflection never ripples (put the actor on a
  render layer the water's ripple distortion skips), and his shadow is "faintly too sharp" (a per-actor shadow without
  the soft penumbra the others get). Art supplies the layer and names; the effects are theirs.

---

## 2. Liss Varrow (hero path)

**One-line read:** a small, wiry young woman, always slightly crouched over something. A copper-green wire-mesh
sleeve and glove on the left arm, a bare right arm with fine circuit-like line-marks running up the collarbone and
neck onto the cheek, a crossed harness of tool pouches over a short patched sailcloth coat that is long at the back, a
boxy crank launcher at the right hip, and cropped hair with one long beaded tail. Oxidised copper green, sail-white and
rust, with pinpoints of bound light.

### 2.1 Proportions
| Measure | Value |
|---|---|
| Height | **1.56 m** (art decision: the smallest adult in the party) |
| Head height | 0.223 m (**7.0 heads**) |
| Shoulder width | 1.60 heads; wiry, not slight (`muscle` 0.55, `mass` 0.12) |
| Waist / hip | 1.05 / 1.32 heads |
| Hands | 0.80 head (a wright's hands, slightly large) |
| Eyes | The ×1.10 rule; IPD 61 mm |
| Posture | **A working crouch:** a 6° forward lean, knees soft (9°), feet a little apart (1.1× shoulder-joint spacing), head forward and down 4°, as if looking at something in her hands. Idle sway 1.2; quick small adjustments. |

### 2.2 Silhouette
- **Front:** small, with an **X of harness straps** across the chest. The left arm is a single bright-metal column
  (mesh sleeve and glove), the right a bare skin column. The **launcher** box breaks the right hip line (viewer's left),
  10 cm proud of the thigh, its crank sticking forward.
- **Three-quarter (hero angle, her right toward camera):** the line-marks on the right arm, collarbone, neck and cheek
  face the camera; the coat's long back panels show past the hips.
- **Profile:** the lean and the soft knees; the coat cut high in front (lower ribs) and long behind (two tails to the back
  of the knee); the hair tail hangs from the nape with its beads.
- **Back:** the X harness over the coat, the two coat tails, the hair tail.
- **Read test against Rhen** (both have the left arm covered and the right bare; the story requires both): Rhen is
  21 cm taller, leans the same way but is upright in the legs, has a *dark cloth* sleeve and gauntlet, a lantern bulb on
  the back and a short jacket. Liss has a *bright metal* sleeve, an X harness, a box at the hip, coat tails and a hair
  tail. At 64 px the difference is height, the coat tails and the hip box; check it in the silhouette lineup.
- **Echo watch (the inspiring game's mechanic-thief heroine, in words only):** that character is known for goggles worn on
  the head, bright yellow-and-green clothing with swirl patterns, a very short skirt and many loose belts. Liss has **no
  goggles** (her eye protection is the glove and sleeve), no yellow, no swirls, trousers not a skirt, and one crossed
  harness, not loose belts.

### 2.3 Asymmetric hallmark: the work-sleeve and the line-marks
- **Copper-wire mesh work-sleeve (left arm, story sheet):** a fitted tube from the shoulder to the wrist, with a
  **five-finger mesh glove** (art decision: protects against glass burns at the fingertips too), held up by a cap over
  the shoulder and a strap across the chest to the right armpit. The mesh is a solid tube with a fine woven normal map
  and an alpha-tested open weave only at the cuffs and the cap's edge (dithered like Asha's gauze). Oxidised:
  `bronze_patina` `#5F8A78` over a `copper` base `#A0603A` (proposed) that shows through on worn high points (knuckles,
  elbow, shoulder cap).
- **Line-marks (right side only, story sheet; ADR 0022 (k)):** **eleven** marks, fine parallel lines and node dots like
  circuitry (bible §7), each recording a device she restored. Placement (art decision): five on the forearm, three on the
  upper arm, two along the collarbone and up the right side of the neck, and the eleventh, the newest and crispest, on
  the right cheek below the cheekbone. Lines 0.6 mm wide with 1.2 mm gaps, dots 1.5 mm, each mark 3–6 cm long, in
  `tattoo_ink` `#24323A`; older marks softer (as the reach-band generator ages ink). **Never on the left arm**, never
  drawn under the sleeve.
- **Bound light in her gear:** three pinpoint `glimmer_bound` inserts (art decision): the launcher's sight (8 mm), a lamp
  cell in the right chest pouch (6 mm, through a slit), a vial clipped to the harness (5 mm). Steady emission, no flicker
  (palette rule for bound glimmer). In Act III's scene acknowledging that every gadget holds a person, these are the
  lights the camera finds.

### 2.4 Costume layers and materials
| # | Piece | Material | Color | Masks | Skinning notes |
|---|---|---|---|---|---|
| 1 | Work top, sleeveless, a wide neckline that drops on the right to bare the collarbone | Light sailcloth | `sailcloth` `#D8CFBC` (proposed) | A 0.3 | Torso only; armholes **12 cm below the shoulder joint**. |
| 2 | **Work-sleeve and glove** (§2.3) | Copper mesh | `bronze_patina` over `copper` | ORM metallic 1 (not G); A alpha at the open weave | A tight tube on the arm chain (2 mm off the skin), the glove on the finger bones, the cap blended over 4 cm into the clavicle. Listed in `garments` (`WorkSleeve`). |
| 3 | **Sailcloth coat**: sleeveless, short at the front (lower ribs), long at the back in **two tails** to the back of the knee; five patches in other sailcloths | Heavy sailcloth | `sailcloth`, patches `#C9BCA2`, `#B7A98E`, `#8A4A2A` (rust), `#5F8A78` | A 0.3 | Deep armholes (12 cm drop). **The back is split into two tails**, each following its own leg plus 3 bones (no tube). Open front. |
| 4 | Tool harness: two straps crossed front and back, six pouches, brass buckles | Leather | `#5A3A26` · buckles `brass` | A 0 | Torso only; the pouches rigid to their strap. |
| 5 | Trousers, loose, mid-calf, patched knees | Canvas | `rust_cloth` `#8A4A2A` (proposed) | A 0.3 | Leg tubes, crotch blend; she kneels and squats (§2.8), so the knees get one extra edge loop each. |
| 6 | Ankle boots, rope soles | Hide | `#4A3020` · soles `thatch` | A 0 | Feet weights. |
| 7 | **Launcher** (prop) at the right hip on a sling | A box 22 × 14 × 12 cm in copper and brass, a 10 cm crank on its right face, an 18 cm stubby barrel forward, the glimmer sight on top | `copper`, `brass`, `#3A3A3F` (iron fittings) | ORM metallic | Prop bone `DEF-launcher` (child of the hips at rest); **2 cm off the thigh** at rest, so a stride does not pass the thigh into it; listed in `props`. The battle draw moves it to the hands (later battle task). |

### 2.5 Hair
- **Style:** cropped short (2–4 cm), roughly cut, dark brown `#2A1C14` (proposed `hair_brown_dark`) with sun-rust tips
  `#7A4A2A` over the outer 25%, plus **one long tail** at the nape (story sheet): a two-strand twist 1.8 cm thick and
  45 cm long, threaded with seven salvaged glass beads (8–12 mm; four `salt_glass`, two copper-green glass `#4FA08A`,
  one amber `#B8782E`; transmissive).
- **Cards:** short scalp cards as Rhen's (about 300) and Toma's short-hair atlas for the crop; the tail as a twisted
  card tube on a spine (as Asha's braid strands, two strands not three).
- **Rig guards (braid):** the tail is a braid for the probe: `braid` `{ "mesh": "HairTail:hair", "scalp":
  ["HairHead:hair", "Head:skin_head"], "head_bone": "DEF-spine.006" }`. Seat the root on the head SDF and stop the scalp
  cards 12 mm from it (Asha's M1-CHR-14 fix), so the 2 mm gap and drift limits hold from the start.
- **Motion:** a 6-bone tail chain (stiffness 0.4, gravity 1.0) with capsules on the neck, upper back and harness straps.

### 2.6 Face
- **Shape:** small, heart-shaped, a pointed chin, wide cheekbones, a short straight nose. Brows straight, thick, slanting
  slightly down toward the nose (a resting scowl: `brow_down` 0.08 at rest).
- **Eyes:** quick and large (the ×1.10 rule), iris green-brown `#4E4A2C` (art decision; the only green-brown eyes in the
  party).
- **Mouth:** wide (0.42 of head width), a thin upper lip. **Her asymmetry: a wry, left-sided smile**, `mouth_smile`
  L = R × 1.3, with `nose_sneer_L` 0.10 added when the smile passes 0.3 (Rhen's crooked smile is on the right; theirs
  mirror each other).
- **Skin:** `skin_liss` `#A2765A` (proposed): sea-weathered; **dense freckles** across the nose and cheeks (60–90 dots);
  three to five small pale glass-burn scars on the right hand and forearm (3–8 mm, smoother and 10% lighter). The cheek
  line-mark is in the head albedo.
- **Blend timing:** 0.10 s, the fastest in the party, 5% overshoot.

**Emotion tags (all 15; her rest `brow_down` 0.08 added to every row):**
| Tag | Shape weights | Note |
|---|---|---|
| `neutral` | — | The rest scowl alone. |
| `soft_smile` | `mouth_smile` 0.30/0.23 | The wry half-smile. |
| `smile` | `mouth_smile` 0.65/0.50, `cheek_raise` 0.40, `lid_squint` 0.25, `nose_sneer_L` 0.10 | |
| `laugh` | `mouth_smile` 0.90/0.70, `cheek_raise` 0.65, `jaw_open` 0.40, `lid_squint` 0.55 | Loud; head forward, not back. |
| `worried` | `brow_inner_up` 0.45, `brow_down` 0.20, `mouth_press` 0.20 | |
| `sad` | `brow_inner_up` 0.55, `lid_close` 0.25, `mouth_frown` 0.35 | |
| `grief` | `brow_inner_up` 1.00, `brow_down` 0.40, `lid_squint` 0.50, `mouth_frown` 0.65, `mouth_stretch` 0.45, `jaw_open` 0.20 | Ch15, telling her father about Tobin. The rawest grief in the game (story sheet): the widest stretch of any table. Tear layer. |
| `angry` | `brow_down` 0.85, `lid_squint` 0.35, `nose_sneer` 0.35, `lip_upper_up` 0.25, `jaw_clench` 0.35 | Ch11, at Rhen. |
| `cold` | `brow_down` 0.30, `mouth_press` 0.45, smile 0 | "He put the fire out once it had finished" (Ch6). |
| `surprised` | `brow_outer_up` 0.80, `brow_inner_up` 0.45, `lid_wide` 0.55, `jaw_open` 0.30 | |
| `afraid` | `brow_inner_up` 0.85, `lid_wide` 0.65, `mouth_stretch` 0.45, `jaw_open` 0.15 | Ch6, sheltering from the raid. |
| `determined` | `brow_down` 0.55, `jaw_clench` 0.35, `mouth_press` 0.35 | Ch8, the hoist. Act III, building the dive rig. |
| `tender` | `brow_inner_up` 0.25, `mouth_smile` 0.18/0.12, `lid_close` 0.15 | Rare: Tobin; the children's windmills in the epilogue. |
| `guilty` | `brow_inner_up` 0.40, `mouth_press` 0.30, `lid_close` 0.25 | Gaze away. |
| `exhausted` | `lid_close` 0.40, `jaw_open` 0.10, `brow_inner_up` 0.15 | |

### 2.7 Palette
| Area | Swatch | Hex | Share |
|---|---|---|---|
| Coat, top | `sailcloth` (proposed) | `#D8CFBC` | ~25% |
| Trousers, rust patch | `rust_cloth` (proposed) | `#8A4A2A` | ~18% |
| Work-sleeve and glove | `bronze_patina` over `copper` (proposed `#A0603A`) | `#5F8A78` | ~12% |
| Skin | `skin_liss` (proposed) | `#A2765A` | ~22% |
| Leather (harness, boots) | — | `#5A3A26` / `#4A3020` | ~12% |
| Hair | `hair_brown_dark` (proposed) → tips | `#2A1C14` → `#7A4A2A` | ~5% |
| Launcher, buckles | `copper`, `brass` | `#A0603A`, `#B08D57` | ~5% |
| Bound-light points | `glimmer_bound` | `#4FB3B0` | < 0.2% (emissive) |

**No gold, no lacquer** (art decision): like Rhen, she is outside the sacred world. Her metals are copper, brass and iron.

### 2.8 Clips and persona
**Persona:** `"liss": {"sway": 1.2, "lean": 6.0, "staff": False, "arms_down": 36.0, "stance": 1.1, "knee": 9.0}`.

| Clip | Loop | Beat | Notes |
|---|---|---|---|
| `idle`, `walk`, `run`, `talk` | yes | everywhere | Talk: the right hand does the talking, quick and pointed; the gloved left stays low. |
| `crouch_shelter` | yes | Ch6: the party shelters her from the raid | A deep squat (knees about 110°) behind cover, one hand on the crate, head low and turning. |
| `carry_crate` | yes | Ch6: she escapes with one crate | Both forearms under a 50 × 35 × 30 cm crate at the hips, a short hurried walk (the crate is a scene prop on a `BoneAttachment3D`). |
| `bury_lamp` | no, holds | Ch6 side scene: she buries a burned lamp at the tideline | Onto both knees, scoop sand with both hands, set the lamp in, push sand over, hands rest on the mound. |
| `clock_lantern` | no | Ch6: "She clocks Rhen's lantern as a Saltwright make immediately" | A lean-in of 10°, the head tilts 8°, the right hand lifts halfway toward it and stops. |
| `point_up` | no | Ch7: "the Bell is glimmer-tech" | Chin up, the right hand points up at the Bell, then drops. |
| `haul_rope` | yes | Ch8: the rope-and-block hoist off the Watchers | Hand-over-hand pulls from overhead to the hip, a braced stance (stance 1.4 for this clip), body leaning back 12°. |

### 2.9 Budget
**LOD0 target 60,000** (ceiling 70k): head and face 21,000 · eyes 2,216 · body skin (bare right arm, collarbone, neck,
calves, hidden legs kept) 7,500 · hair (crop, the tail, beads) 6,000 · top 2,000 · coat with tails and patches 5,000 ·
work-sleeve and glove 3,500 · harness and pouches 4,000 · trousers and boots 4,000 · launcher 3,000 · total about 58,200.
LOD1 28k (keeps the X harness, the coat tails, the hip box, the hair tail and the sleeve's metal read), LOD2 13k, LOD3 5k.
**Textures:** head 2K ×4 (the cheek line-mark and freckles at ≥ 50 px/cm on the cheek), body 1K ×4 (the arm line-marks
need ≥ 14 px/cm: 1.2 mm gaps at about 1.7 px; give the right arm a larger body UV share or a 2K body albedo), costume 2K
(ORM 1K), launcher and harness props 1K, shared hair and eye atlases. GLB < 5 MB.

### 2.10 Modeling notes
- **Folder** `assets_src/characters/liss/`: `build_liss.py` on `build_asha`; `liss_params.json`; `liss_costume.py` on
  `rhen_costume` (`torso_sheet`, `limb_tube`) and `toma_costume`; `liss_hair.py` (crop on `toma_hair`'s short cards, the
  tail on `asha_hair`'s braid code); `liss_props.py` (launcher); `liss_textures.py` with a **line-mark generator** (new;
  shaped like `toma_textures._reach_bands`: seeded marks, count 11, placement table, ink age). The generator is the one
  every Saltwright will use (Tobin, Dace in the logs, Hollowmere NPCs), so it lives in `liss_textures.py` and other
  builds import it.
- **Params (starting values):** `height_m` 1.56, `heads_tall` 7.0, `shoulder_width_heads` 1.60, `chest_width_heads` 1.20,
  `chest_depth_heads` 0.86, `waist_width_heads` 1.05, `hip_width_heads` 1.32, `crotch_height_heads` 3.4, `arm_span_ratio`
  1.01, `hand_length_heads` 0.80, `neck_length_heads` 0.40, `neck_width_ratio` 0.5, `head_width_ratio` 0.67, `femininity`
  0.85, `muscle` 0.55, `mass` 0.12, `breast` 0.25, `eye_scale` 1.10, `ipd_m` 0.061, `eye_tilt_deg` 2.0, `jaw_width` 0.92,
  `cheekbone_height` 0.003, `cheekbone_width` 1.06, `chin_size` 0.90, `nose_bridge_width` 0.96, `nose_tip_projection` 0.98,
  `lip_fullness` 0.75, `lip_close` 0.6, `lip_seal` 0.96, `lip_lower_fullness` 0.7, `mouth_corner_lift` 0.0, `brow_ridge`
  1.0, `donor_mix_african` 0.3, `donor_mix_asian` 0.35, `donor_mix_caucasian` 0.35, `skin_hex` `#A2765A`.
- **Rig extras:** coat tails 2 × 3; hair tail 6; `DEF-launcher`. Rig guards: `liss` in `rig_checks.json` with
  `garments` [`Costume`, `WorkSleeve`], `props` [`Launcher`], the `braid` entry of §2.5.
- **Blender job:** `liss`, `"threads": 4`, sources `liss/**`, `asha/**`, `rhen/**`, `toma/**`, `base_body/**`,
  `third_party/mpfb2/**`; byte-identical; `PRE_ROUND` set.

---

## 3. Tavi Orse (villager path)

**Who (story):** captain of Oruvel's Reefball side and Mother Kell's grandson (ADR 0017; act_outline Ch7). His side
came to Tamsule a week before the storm. He finds Rhen in the crowd and learns from him that Kell couldn't swim; he
names the whole town at the captains' rite ("Oruvel."); after the opening round he withdraws the side to go home and
search (ADR 0020 (h)); he asks Asha to bless Oruvel's empty moorings under the Bell.

**One-line read (art decision):** a tall, broad-shouldered swimmer in his mid-twenties in a faded-teal sleeveless kit
and dark knee trousers, an ochre sash, and a **dark mourning band** round his head, barefoot. Kell's nose and eyes.

### 3.1 Body, age and silhouette
- **Age 24** (art decision: Kell's grandson, old enough to captain). **1.78 m**, 7.5 heads, a swimmer's build: wide
  shoulders, long arms, narrow hips (`muscle` 0.8, `mass` 0.18). Upright and open; a captain's stance, feet a little
  apart.
- **Silhouette:** an inverted triangle with bare arms, a dark band at the brow and a bright ochre sash at the hips. He
  is distinct from the Haluna fisher (red headband, open vest, shorter) by the closed teal top, the dark band and the
  ochre.

### 3.2 Costume and palette (art decisions)
- **The side's kit:** Oruvel's side plays in **faded teal**, the raft-town's sun-faded cotton (Rhen's jacket is the same
  cloth: the colour ties the side to the boy who dives for them) with an **ochre sash**, the colour of lamp oil, for the
  lamp-divers' town. The same ochre is Mother Kell's oiled apron (§4).
- **The mourning band:** since the news of the storm, the side wears a band of `mourning_indigo` (Maresh mourning colour,
  ysolde.md §7) round the head. Tavi's is the first the camera sees.
- Barefoot (Reefball is played in water). Reach-bands **L 6 / R 5** (trading voyages with the side).

| Area | Material slot | Tint | Notes |
|---|---|---|---|
| Sleeveless top, round neck, close-fitting | `cloth_a` | `#5E9A96` (`faded_teal_cloth`) | |
| Knee trousers, close | `cloth_b` | `#26243C` (`mourning_indigo`, proposed) | Dark: they and the band share the slot. |
| Mourning band (`headwrap` `band_only`) | `cloth_b` | `#26243C` | |
| Sash | `cloth_c` | `#B07A30` (`oruvel_ochre`, proposed) | |
| Skin | — | `#9A6646` | Sun-dark Low Reaches brown, a shade deeper than Rhen's. |
| Hair | — | `#141417` | Short, swept back (wet-combed look). |
| Iris | — | `#2A1A10` | Kell's (§4). |

### 3.3 Draft params (`assets_src/characters/villagers/params/tavi.json`; keys as the existing villager files)
```json
{
  "_about": "Tavi Orse, captain of Oruvel's Reefball side, Mother Kell's grandson, about 24 (ADR 0017; act_outline Ch7). Tall swimmer's build. Oruvel's side kit: faded-teal sleeveless top, dark knee trousers, ochre sash; a mourning band of Maresh indigo-black since the storm; barefoot. Reach-bands left 6, right 5. Kell's nose and iris. Face sliders relative to the MakeHuman donor (ADR 0021). Keys starting with '_' are read by the villager_* modules, not by bb_params. (Draft, M3-CHR-03.)",
  "name": "tavi",
  "height_m": 1.78, "heads_tall": 7.5,
  "shoulder_width_heads": 1.9, "chest_width_heads": 1.36, "chest_depth_heads": 0.98,
  "waist_width_heads": 1.12, "hip_width_heads": 1.36, "crotch_height_heads": 3.62,
  "arm_span_ratio": 1.04, "hand_length_heads": 0.82, "foot_length_ratio": 0.154,
  "neck_length_heads": 0.4, "neck_width_ratio": 0.6, "head_width_ratio": 0.66,
  "femininity": 0.0, "muscle": 0.8, "mass": 0.18, "breast": 0.0,
  "eye_scale": 1.08, "ipd_m": 0.064, "arm_abduction_deg": 47.0, "skin_hex": "#9A6646",
  "eye_tilt_deg": 1.5, "jaw_width": 1.06, "cheekbone_height": 0.002, "cheekbone_width": 1.04,
  "chin_size": 1.04, "nose_bridge_width": 1.08, "nose_tip_projection": 0.96,
  "lip_fullness": 0.82, "lip_close": 0.6, "lip_seal": 0.96, "lip_lower_fullness": 0.78,
  "mouth_corner_lift": 0.0, "brow_ridge": 1.05,
  "donor_mix_african": 0.45, "donor_mix_asian": 0.4, "donor_mix_caucasian": 0.15,
  "_skin": {"hex": "#9A6646", "age": 0.12, "freckles": 0, "reach_bands": {"L": 6, "R": 5},
            "ink_opacity": 0.7, "seed": 111, "lip": "#7A4838"},
  "_hair": {"kind": "short", "hairline": "male", "seed": 31, "length_m": [0.03, 0.05],
            "scalp_cards": [190, 150, 100], "hairline_cards": 40, "rise": 0.6,
            "colour": "#141417", "underpaint": "#16161A"},
  "_eyes": {"iris": "#2A1A10"},
  "_costume": {
    "top": {"mat": "cloth_a", "hem": "hip", "sleeve": 0.0, "neck_v_m": 0.03},
    "trousers": {"mat": "cloth_b", "hem": "knee", "loose_m": 0.008},
    "sash": {"mat": "cloth_c", "width_m": 0.07, "turns": 1},
    "headwrap": {"mat": "cloth_b", "band_only": true, "edge_lift": 0.012, "band_m": 0.035, "seed": 79}
  },
  "_tints": {"cloth_a": "#5E9A96", "cloth_b": "#26243C", "cloth_c": "#B07A30", "leather": "#FFFFFF"},
  "_build": {"shapes": "all"},
  "_persona": {"sway": 1.1, "lean": 1.5, "arms_down": 41.0}
}
```
(Pretty-printed in the real file, as the others. `rise` 0.6 for a flatter, swept-back crop than the fisher's 1.2;
check the value range in `villager_hair`.)

### 3.4 Face notes and emotion tags
- An open, broad face; a strong brow; **Kell's nose** (`nose_bridge_width` 1.08, the same as hers) and **her iris**: the
  family likeness the player can find if they look (art decision).
- He uses the villager default table for all 15 tags, with these overrides:

| Tag | Beat | Override |
|---|---|---|
| `surprised` → `smile` | Ch7: he finds Rhen alive in the crowd | Default rows; Cinematics blends them. |
| `worried` | Waiting a week for news | `brow_inner_up` 0.50, `mouth_press` 0.25 |
| `grief` | "Kell couldn't swim" | `brow_inner_up` 0.90, `brow_down` 0.35, `lid_squint` 0.40, `mouth_frown` 0.45, `jaw_clench` 0.30 (he holds it in front of his side) |
| `determined` | The naming: "Oruvel." | `brow_down` 0.35, `jaw_clench` 0.30, `mouth_press` 0.25; chin up |
| `tender` / `soft_smile` | Asking Asha to bless the moorings | Default rows |
| `sad` | Withdrawing the side | Default row |

### 3.5 Clips
`idle`, `talk`, `walk` (the villager set) plus three (a `villager_clips.py` extension for per-NPC clips, the same need
Osu's H08 scene has; villagers_review.md §5 item 4):
| Clip | Beat | Notes |
|---|---|---|
| `hand_on_shoulder` | Ch7: he pushes through the crowd and finds Rhen | Two steps in, stop, the right hand onto a partner's left shoulder at 1.45 m height; holds. |
| `hear_news` | Ch7: Rhen tells him | From `hand_on_shoulder`: the hand slides off, the head drops 18°, the shoulders fall; a long hold. |
| `name_rite` | Ch7: the captains' naming | Holds the woven float to his chest in both hands, chin lifted; the line is spoken from this pose. The float is the Reefball prop (environment's `reefball` woven float, haluna.md props) on a `BoneAttachment3D`. |

**Not here:** swimming clips for the Reefball match. The story match is a turn-paused set-piece (SPEC §6.10); its
players' animation is the Reefball match task's, and the rest of Oruvel's side are variants of `tavi.json` (other seeds,
heights and the same kit) made there.

### 3.6 Budget and staging note
Villager budget: LOD0 25–35k (`tools/tests/test_villagers.py` holds 20–36k), GLB < 3 MB, LOD1 about half. **Staging
recommendation to Cinematics:** the "Kell couldn't swim" beat plays on **Rhen's** face (the hero rig) with Tavi
over-shoulder or in a medium two-shot. If the beat must hold on Tavi in a head-and-shoulders close-up, he moves to the
hero path's head (face subdivision), which is a re-scope to file, not a tweak.

---

## 4. Mother Kell (villager path)

**Who (story):** Oruvel's **chandler**: she sells the lamp-divers their oil and wicks and trims them, and **never learned
to swim** (N-25 S1, ADR 0022 sweep-H S1; this corrects the earlier "old Oruvel diver"). Dace's one message was left at
her stall on Oruvel's second mooring; she took Rhen in at eight, **unasked**, as she took in every stray, raised him to
nineteen, taught him to haggle, never said a hard word about his father. In Ch1, before the storm, she presses a fresh
wick from her own stock into his hand "for luck", as she does for every diver going down. She drowns in the storm. Her
wick lights the post-credits lamp (E7).

**IP watch (ADR 0022 sweep-H B1, carried into art):** she is a busy neighbour who stepped in, **never a mentor or a
keeper charged by the father**, and never in the party. No signifiers of office or wisdom: no staff, no robe, no beads,
no walking stick, nothing handed down. Her warmth is in her hands and her laugh. The wick is trade stock, so it is drawn
as one wick from a bundle of identical ones on her apron.

**One-line read (art decision):** a short, stout old woman with cropped grey hair, sleeves rolled to the elbow, an
oil-darkened ochre apron with a bundle of wicks and a pair of trimming shears on a cord, nearly bare forearms in a
town of banded arms, and oil-stained fingertips.

### 4.1 Body, age and silhouette
- **About 70** (art decision: her grandson is 24). **1.52 m**, 6.9 heads, stout and solid (`mass` 0.62, `muscle` 0.35):
  a shopkeeper who lifts oil jars, not a frail elder. A slight forward stoop (5°, less than Osu's 6°).
- **Silhouette:** a short, wide figure with a big apron front and a cropped round head (no head wrap, so she does not
  read as Osu); the shears on their cord make a small hanging shape at the apron's right.
- **Reach-bands L 2 / R 1 (art decision with a story reason):** a Low Reaches adult carries one band per voyage survived
  (bible §5.1). Kell kept a stall on a mooring and could not swim: in a raft-town of banded arms, hers are nearly bare.
  The camera can find it in the wick shot.

### 4.2 Costume and palette (art decisions)
| Area | Material slot | Tint | Notes |
|---|---|---|---|
| Wrap top, elbow sleeves rolled, V neck | `cloth_c` | `#6F8F8C` | Oruvel's faded teal, faded further (older cloth than Tavi's kit) |
| Calf-length wrap skirt and sash | `cloth_b` | `#46557F` | Faded indigo. **Calf, not ankle** (M1-CHR-14 lesson; she has a two-handed reach clip). |
| Apron, wide, knee length, oiled canvas | `cloth_a` | `#8A6A3A` | Oil-darkened `oruvel_ochre` (the same ochre as Tavi's sash). |
| Sandals | `leather` | untinted | |
| Skin | — | `#A0694A` | Age 0.85; oil-dark fingertips (an albedo term on the hands, art decision: the body map's fingertip pads 25% darker and warmer). |
| Hair | — | `#6E6860`, grey `#C9C4BA` at 0.85 share | Cropped short and practical (loose hair near flame is dangerous). |
| Iris | — | `#2A1A10` | Tavi has it too. |

### 4.3 Draft params (`assets_src/characters/villagers/params/kell.json`)
```json
{
  "_about": "Mother Kell, Oruvel's chandler, about 70 (rhen_sallow.md; act_outline Ch1; N-25: a chandler who never learned to swim, not a diver). Short and stout; cropped grey hair; a faded-teal wrap top with rolled elbow sleeves, a faded indigo calf skirt and sash, a wide oil-darkened ochre apron (wicks and shears are scene props). Nearly bare forearms (reach-bands 2/1): she never sailed far. Oil-dark fingertips. Face sliders relative to the MakeHuman donor (ADR 0021). Keys starting with '_' are read by the villager_* modules, not by bb_params. (Draft, M3-CHR-03.)",
  "name": "kell",
  "height_m": 1.52, "heads_tall": 6.9,
  "shoulder_width_heads": 1.66, "chest_width_heads": 1.34, "chest_depth_heads": 1.04,
  "waist_width_heads": 1.34, "hip_width_heads": 1.6, "crotch_height_heads": 3.25,
  "arm_span_ratio": 1.0, "hand_length_heads": 0.8, "foot_length_ratio": 0.148,
  "neck_length_heads": 0.34, "neck_width_ratio": 0.56, "head_width_ratio": 0.7,
  "femininity": 0.95, "muscle": 0.35, "mass": 0.62, "breast": 0.55,
  "eye_scale": 1.06, "ipd_m": 0.062, "arm_abduction_deg": 47.0, "skin_hex": "#A0694A",
  "eye_tilt_deg": 0.5, "jaw_width": 1.06, "cheekbone_height": 0.0, "cheekbone_width": 1.05,
  "chin_size": 0.98, "nose_bridge_width": 1.08, "nose_tip_projection": 0.94,
  "lip_fullness": 0.72, "lip_close": 0.6, "lip_seal": 0.96, "lip_lower_fullness": 0.7,
  "mouth_corner_lift": 0.0004, "brow_ridge": 1.0,
  "donor_mix_african": 0.45, "donor_mix_asian": 0.4, "donor_mix_caucasian": 0.15,
  "_skin": {"hex": "#A0694A", "age": 0.85, "freckles": 0, "reach_bands": {"L": 2, "R": 1},
            "ink_opacity": 0.45, "seed": 112, "lip": "#7E4C40"},
  "_hair": {"kind": "short", "hairline": "female", "seed": 32, "length_m": [0.03, 0.05],
            "scalp_cards": [180, 140, 90], "hairline_cards": 50, "rise": 0.8,
            "colour": "#6E6860", "grey": "#C9C4BA", "grey_share": 0.85,
            "underpaint": "#5A544C", "brow": "#6A645C"},
  "_eyes": {"iris": "#2A1A10"},
  "_costume": {
    "top": {"mat": "cloth_c", "hem": "hip", "sleeve": 0.42, "neck_v_m": 0.06},
    "skirt": {"mat": "cloth_b", "hem": "calf", "folds": 8, "fold_amp": 0.008, "flare": 0.14, "seed": 61},
    "apron": {"mat": "cloth_a", "hem": "knee", "half_deg": 58, "seed": 62},
    "sash": {"mat": "cloth_b", "width_m": 0.08, "turns": 2},
    "sandals": "leather"
  },
  "_tints": {"cloth_a": "#8A6A3A", "cloth_b": "#46557F", "cloth_c": "#6F8F8C", "leather": "#FFFFFF"},
  "_build": {"shapes": "all"},
  "_persona": {"sway": 0.6, "lean": 5.0, "arms_down": 38.0}
}
```
(Check that `villager_hair` takes `hairline: "female"` on the `short` kind; the existing short styles are all male.
If not, that is a small `villager_hair` addition, re-verifying every `villager_*` job.)

### 4.4 Props (scene props, art-owned sources)
- **The wick:** a 9 cm twisted cotton wick, 4 mm thick, the top 1 cm stiffened with wax, `sand_cloth` with a darker waxed
  tip. **One source for every wick in the game**: Kell's hand (Ch1), the bundle on her apron, Rhen's tin, and the E7
  post-credits lamp (art decision: `assets_src/characters/props/wick.py`, a tiny Blender job or a pure-Python glTF
  writer, with PROVENANCE rows). It is never fitted to Rhen's lantern (ADR 0022 sweep-H/I/J watch).
- **The wick bundle** (twelve wicks tied with thread) and **trimming shears** on a cord at the apron's right: the same
  source file. Placed in the scene on `BoneAttachment3D`s (hips for the bundle and shears, `DEF-hand.R` for the wick).

### 4.5 Face notes and emotion tags
- A broad, round, deeply lined face (age 0.85: forehead lines, crow's feet, nasolabial folds), smile lines set deep from
  a life of haggling; a slight natural upturn at rest (`mouth_corner_lift` 0.0004).
- Villager default table for all 15 tags, with overrides for the tags her scene uses:

| Tag | Beat | Override |
|---|---|---|
| `soft_smile` | Ch1, the stall | `mouth_smile` 0.35, `cheek_raise` 0.25, `lid_squint` 0.20 (the lines do the work) |
| `laugh` | Haggling with Rhen | `mouth_smile` 0.85, `cheek_raise` 0.70, `jaw_open` 0.35, `lid_squint` 0.65; head back 5° |
| `tender` | Pressing the wick "for luck" | `brow_inner_up` 0.20, `mouth_smile` 0.25, `lid_close` 0.20 |
| `worried` | The lintel-gulls cry (the storm warning) | Default row; she looks up |
| `neutral`, `smile` | Ch1 | Default rows |

`afraid` and `grief` ship in the default table, but her death is **off screen** (art decision; the story never puts it
on screen), so no scene should need them.

### 4.6 Clips
`idle`, `talk`, `walk`, plus:
| Clip | Beat | Notes |
|---|---|---|
| `press_wick` | Ch1 side scene | Her left hand takes the partner's right hand at 1.0 m height; her right presses the wick into the palm with the thumb; both hands close his fingers over it; two pats; release. About 3 s. |
| `trim_wick` | Ch1, the stall (loop) | Both hands at chest height, shears snip every 2 s, a glance up between snips. |
| `haggle_laugh` | Ch1, the stall | One hand slaps the counter (0.95 m), head back 5°, then settles. |

### 4.7 Budget
Villager budget as Tavi (§3.6). Her short grey crop is the review's known weak spot (villagers_review.md §4: short hair
flaky up close); the wick shot is on the hands, which hides it.

---

## 5. Shared notes

### 5.1 Proposed palette swatches (Art adds them to `palette.json`, with on-screen values)
| Swatch | Hex | Who |
|---|---|---|
| `mourning_indigo` | `#26243C` | Ysolde's robe; Tavi's mourning band and trousers (Maresh mourning colour) |
| `mourning_indigo_hi` | `#3A3856` | Ysolde's satin back |
| `skin_ysolde` | `#B48A72` | Ysolde |
| `ash_white` | `#D6D2C8` | Ysolde's streak |
| `silver` | `#A9AEB3` | The Level-pin, ink-guard inner faces |
| `ivory_silk` | `#E2D9C6` | Sefir |
| `still_blue_silk` | `#9FBCC8` | Sefir |
| `hair_silver` | `#CFCAC0` | Sefir |
| `skin_sefir` | `#C29C84` | Sefir |
| `sailcloth` | `#D8CFBC` | Liss |
| `rust_cloth` | `#8A4A2A` | Liss |
| `copper` | `#A0603A` | Liss's sleeve base, launcher |
| `hair_brown_dark` | `#2A1C14` | Liss |
| `skin_liss` | `#A2765A` | Liss |
| `oruvel_ochre` | `#B07A30` | Tavi's sash; Kell's apron (oil-darkened `#8A6A3A`) |

### 5.2 Persona keys this sheet adds to `hero_clips.py`
`breath` (default 1.0; Sefir 0.0), `book` (Ysolde), `hands_joined` (Sefir). Each must leave Asha's, Rhen's and Toma's
libraries byte-identical at its default. `villager_clips.py` needs a per-NPC clip list for Tavi's and Kell's extra
clips (and Osu's H08).

### 5.3 What this sheet does not cover
Kerrid (joins Ch5) and Pell (joins Ch9) are party members with no art sheet yet; the Inquisitor, the raid-hound and the
Stillguard (Ch6 boss and crowd) are enemy and NPC work for their own tasks; Tobin, Merel and Liss's father are Act II.
