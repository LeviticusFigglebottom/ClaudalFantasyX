# Inquisitor Hadric Moll: Design Sheet

**Task:** [M3-CHR-507](../../tasks/M3/M3-CHR-507-inquisitor-hadric-moll.md). **Story sources:** act1_ch06.md (B02 end,
B04 §5, B05 W10), M3-C06-06 #3, bible.md (the Stillguard). **Enemy:** `stillguard_inquisitor` (encounter
`ch06_inquisitor`, `enemies.json`). **Speaker:** `inquisitor` (CHAR_INQUISITOR).

**One-line read:** a full Stillguard in red-lacquered shell armour, with both pauldrons whole and the Level emblem bright
on them. A white Inquisitor's sash runs from the right shoulder to the left hip. He holds a long-hafted **brine-iron**
upright beside him like a standard, its head the Level in blackened iron, and carries a round shield on his left arm.
He is a man in his forties who stands very straight because he is tired, not proud.

**Who he is (for every choice below):** a sincere officer who still believes the Edict. He isn't cruel, and nothing on
him is ornamented for menace: no spikes, no skull motifs, no black. The horror of B03 comes from his kit being clean,
orderly and well kept while it is used to burn a camp. At the yield he goes to one knee and says "...Enough. Enough."
He must look like a man who could say that.

**The Toma rhyme:** he is what Toma was. His armour is Toma's pauldron *uncut* and doubled: the same lames, lacquer and
gold piping, and the emblem Toma chiselled out of his own is whole on Moll's. Put side by side in B04 (Toma's shield up
in front of Asha), the eye should match the two red shapes and see the difference: one scar, one emblem.

---

## 1. Proportions

| Measure | Value | Note |
|---|---|---|
| Height | 1.78 m (7.4 heads) | Average, upright, not a giant: the boss reads from the iron, not from bulk |
| Shoulder width | 2.0 heads (0.48 m) + pauldrons 0.10 m each side | 0.68 m across the pauldrons |
| Build | Lean-average, slight middle-age thickening at the waist | The base body `athletic` blend 0.4 toward `heavy` 0.2 |
| Posture | Upright; the chin a little down; the shoulders squared by habit | Persona `lean` 0, sway 0.4 (he breathes: he is alive) |

## 2. Silhouette

- **Front:** a straight vertical body between two rounded red shoulder shapes, the white sash a bright diagonal across
  the chest, and the **iron's haft a hard vertical line** to his right, 2.1 m tall, its Level head (a ring crossed by a
  bar, 22 cm across) above his head. The round shield (0.62 m, smaller than Toma's tide-shield) on the left forearm.
- **Three-quarter (his right toward camera):** the haft and the head of the iron dominate, the sash second.
- **Profile:** the cuirass's lames step down the chest in four overlapping rows; the shield is a shallow dome.
- **Back:** the sash's knot at the left hip, its tails to mid-thigh; the cuirass's back lames.
- **Battle scale (LOD1, 6 m):** the read is "a red figure with a standard". The Level head must stay readable at
  128 px: a 22 cm ring with a bar, blackened iron with a dull heat-glow at its lower rim (see §3).

## 3. The Hallmark: the Brine-Iron

- **What it is:** the Order's branding iron, used to burn the Saltwright line-marks off an arm (B03 W06). The clerk's
  are short irons heated in a salt brazier. The Inquisitor's is the same head on a 2.1 m ash haft, carried upright as an
  office.
- **Head:** the Level (glossary: a circle crossed by a horizontal line) forged in iron: a ring 22 cm across with a
  2.4 cm square-section stock, and a bar across the ring's diameter extending 4 cm past it each side. A socket and two
  rivets join it to the haft. Blackened (`iron_dark`); the ring's lower third shows a **dull ember heat-tint**
  (`ember_dull`, emission 0.15) in Ch6 (it was in the brazier). It is a material parameter, off by default.
- **Haft:** ash, 3.2 cm, oiled (`wood_ash_oiled`), with a red-lacquer band under the socket (8 cm) and a bronze ferrule
  at the foot. **Held** like Asha's staff: built through his right fist and gripped (M2-CHR-515's prop grip, a
  `DEF-iron` bone under `DEF-hand.R`, `GRIP_ALWAYS`). It is never shouldered or twirled.
- **The shield:** a Stillguard round shield, 0.62 m, domed 6 cm, red lacquer with a bronze rim and boss, and the Level
  painted in `bone` across the face. It rides the left forearm (`DEF-shield` under `DEF-forearm.L`).

## 4. Costume Layers and Materials

| # | Layer | Material | Swatch (asha.md / toma.md palette) | Mask |
|---|---|---|---|---|
| 1 | Under-tunic, long-sleeved, to mid-thigh | Undyed cotton | `bone` `#E6DAC0` | A 0.3 |
| 2 | Cuirass: four rows of overlapping shell lames front and back, over a leather jack | Shell and lacquer (Toma's pauldron lames, `toma_props`) | `lacquer_red` / `lacquer_red_deep` edges / `gold_leaf` piping | B lacquer · G piping |
| 3 | Pauldrons ×2, five lames each, the Level emblem whole on the top lame | as Toma's pauldron, **uncut** | as above; emblem `gold_leaf` | B · G |
| 4 | Inquisitor's sash, right shoulder to left hip, knotted at the hip, tails to mid-thigh | Fine white linen, 14 cm | `linen_white` `#EEEAE0` (proposed) | A 0.35 |
| 5 | Trousers and shin wraps | Cotton | `indigo_dye` at 80% value (kept, not faded: an officer's issue) | A 0.3 |
| 6 | Sandals on leather soles | Leather | `leather` `#4A3020` | — |
| 7 | Bracers, both forearms | Leather with a bronze edge | `leather`, `bronze_patina` | — |

**What he does not wear:** no helmet (his face is the scene: "Lady Cantor. Step away from the hold."), no cloak, no
blood or soot on the armour (it is kept clean), and nothing black.

## 5. Hair and Face

- **Hair:** short, grey at the temples, dark brown elsewhere, cropped in the Order's fashion. Toma's short-hair cards
  (`toma_hair` method) with a grey blend at the temples.
- **Face:** forties, long and lean, with deep nasolabial lines, slight bags under the eyes, a straight nose and a
  close-shaven jaw with a day's shadow. He looks tired, not cruel. On the base face (MPFB2 donor) with the age terms
  of the villager pipeline at 0.4.
- **Expressions (the 15 face poses of the hero path; his tags):** `level` (neutral, the default: a level gaze, mouth
  set), `tired` (lids 0.2, brow inner up 0.2), `stern` (Ch6 "Step away from the hold": brow down 0.3, mouth press
  0.35), `yield` ("...Enough. Enough.": lids 0.35, brow inner up 0.5, mouth slightly open).

## 6. Colour Callouts

Dominant: `lacquer_red` (armour) about 45% from the front; `linen_white` sash 8%; `bone` tunic 12%; `indigo_dye`
trousers 15%; the iron's haft and head 5%. The white sash and the red are the read. No yellow, no teal (teal is the
Saltwrights' glimmer).

## 7. Budgets

LOD0 ≤ 55,000 triangles (head and face 18k as the hero path; the cuirass's lames 9k; the pauldrons 5k; the shield
2k; the iron 1.6k). LOD1 ≤ 26k. `moll.glb` < 5 MiB, `moll_lod1.glb` < 1.5 MB, every PNG < 5 MiB (ADR 0005). Textures:
face 2K, body 1K, costume atlas 2K (the lames, sash, tunic, trousers, bracers), shield and iron 1K each.

## 8. Modeling Notes

- Folder `assets_src/characters/moll/` on the pipeline.md §12 hero layout (as Liss and Kerrid): `build_moll.py` with
  `build_asha` as the helper library, `moll_params.json`, `moll_costume.py` (the cuirass lames reuse `toma_props`'
  pauldron lame builder), `moll_props.py` (the brine-iron, built upright and turned into the fist with
  `asha_staff.held_frame`/`to_held`, and the shield), `moll_textures.py` (`PRE_ROUND` set), `write_materials.py`,
  `build.sh`. Host snaps opted in (M2-CHR-11). A `tools/dev/blender_builds.json` job verified on the three numpy paths.
- **He is a foe, not a party member**, so there is no field locomotion set beyond `idle`, `walk` and the story clips.
  `stillguard_inquisitor.model` points at a battle scene with his LOD1. His clips go through `hero_clips.py` (PERSONA
  `moll`), as the heroes' do, so the battle contract, the prop grip and the rig-probe guards all apply.

## 9. Clips

| Clip | Use | Notes |
|---|---|---|
| `idle` | field and battle | Upright, the iron grounded at his right foot, the shield low; breath; sway 0.4 |
| `walk` | `@mark inquisitor hatch walk` (B02) | Measured, the iron carried upright and lifted clear (the carry) |
| `look_at` | `@anim inquisitor look_at hound` (B02) | Head and chest turn to his left and down, about 30° |
| `kneel` | `@anim inquisitor kneel` (B05 W10: "on one knee in the mud") | On the right knee, the iron **set down** beside him (M2-CHR-520), the shield arm on the raised knee |
| `attack` | battle | A two-handed thrust of the iron's head, the bar leading, at chest height; contact 0.55; the shield arm swings back |
| `hit` | battle | A step back on the left foot, the shield coming up late |
| `ko` → **the yield** | battle (0 HP) | Down onto the right knee, the iron's foot grounded and both hands on the haft, the head bowed; holds. **Not** lying down (§5 of act1_ch06: "goes to one knee and yields") |
| `cast` | battle (phase 2: "Torch the Hulk") | The left hand raised, palm out toward the hulk, the order given |

## 10. Acceptance Checklist

- [ ] This sheet reviewed by Rendering (and the Art Director for `linen_white`, `ember_dull`).
- [ ] Built from source, verified on the three numpy paths, PROVENANCE rows, budgets of §7 met.
- [ ] Rig probe clean (the iron gripped and out of the clothes); battle clips pass the contract tests.
- [ ] Shots: front, three-quarter, profile, face (`level`, `yield`), the yield clip, and a silhouette next to Toma.
- [ ] `stillguard_inquisitor.model` set (a request to Combat if the battle scene is theirs).

## 11. Open Questions

None for the human. For the Ch14 owner: if Moll reappears at the wedding (`ch06_inquisitor_yielded`), he wears the
same kit with the sash removed (a demotion), which is a material switch, not a new model.
