# Haluna villagers: build review (M2-CHR-03)

Build: `assets_src/characters/villagers/build.sh [npc ...]` (per villager about 30 s of Blender and 50 s of textures on
4 vCPUs; the shared cloth atlas once, 30 s). Pipeline: [`pipeline.md`](pipeline.md) §11-§15 (MPFB2 donor, ADR 0021; the
hero layout of §12 at an NPC budget). Review stage: `game/levels/_tests/characters/villagers/` (one stage per
villager on `asha_stage.gd`, `villagers_lineup.tscn`, two idle-clip scenes). Shots: `villager_lineup`,
`villager_<npc>_front` and `villager_<npc>_face` for all seven, `villager_neme_back`, `villager_vendor_back`,
`villager_neme_idle`, `villager_osu_idle`.

## 1. Who was built, and the capsule each one replaces

The brief named "Neme, Osu (Pila's granddaughter), Pila, the lane child and three generic villagers". The story has it
the other way round: **Grandmother Osu is Pila's granddaughter** (vertical_slice.md §4, vowbound.md), and Pila Marrin
lived 140 years ago and died at ninety-one; she never appears. The slice's Haluna scene has **four** non-named
speakers (Vendor, Reed, Netmender, Fisher), so the seventh build is the fourth of them, which covers every capsule in
`haluna.tscn` plus Osu for M2-FP-14:

| Villager | Who (source) | Build | Replaces (node in `game/levels/ch02/haluna/haluna.tscn`) | Swap in |
|---|---|---|---|---|
| `neme` | Asha's aunt, about 46, mends nets (asha_velamir.md; B02 `ch02_nemes_table`) | 1.58 m, sturdy; hair drawn back into a low knot, a little grey; faded sea-blue short-sleeved wrap top, indigo skirt and sash, undyed apron; reach-bands 3/2 | `NPCs/Neme/Neme` | `res://assets/characters/villagers/neme/neme_actor.tscn` |
| `osu` | Grandmother Osu, the elder at the wake-shell wall (B04, M2-FP-14) | 1.50 m, thin, age 0.95; white hair under an undyed head wrap set back off the hairline; undyed top with elbow sleeves, faded indigo skirt, sea-blue sash; dense faded reach-bands 14/12 | no capsule yet (M2-FP-14 places her at H08) | `res://assets/characters/villagers/osu/osu_actor.tscn` |
| `child` | the lane child singing the counting rhyme (`ch02_bark_lane`) | a boy of about eight: 1.27 m, 6.2 heads; short black hair; undyed cap-sleeved tunic, indigo knee trousers, sea-blue sash; barefoot; no bands | `NPCs/Lane/Child` | `res://assets/characters/villagers/child/child_actor.tscn` |
| `vendor` | the fish seller at the market (`ch02_bark_market`) | 1.62 m; indigo head wrap, sea-blue top, undyed calf skirt, indigo apron, sea-blue sash; bands 4/3 | `NPCs/Market/Vendor` | `res://assets/characters/villagers/vendor/vendor_actor.tscn` |
| `reed` | an Order novice sweeping the chapel steps (`ch02_bark_chapel`; bible §4 "Reeds") | 1.70 m, slim, close-cropped; the Order's white: a long-sleeved robe (top and shin skirt in one white) with a narrow pale-ochre sash; sandals; no bands | `NPCs/Chapel/Reed` (keep its `Broom`, see §5) | `res://assets/characters/villagers/reed/reed_actor.tscn` |
| `netmender` | the older fisher at the net (`ch02_bark_dock`) | 1.66 m, about 62, broad; grey cropped hair receding at the temples, grey stubble; faded teal sleeveless tunic, indigo shin trousers, undyed sash; bands 10/9 | `NPCs/Dock/Netmender` | `res://assets/characters/villagers/netmender/netmender_actor.tscn` |
| `fisher` | the younger fisher (`ch02_bark_dock`) | 1.74 m, about 26, lean-muscled; short black hair under a madder-red headband; open undyed vest over a bare chest, loose indigo knee trousers, red sash; barefoot; bands 3/2 | `NPCs/Dock/Fisher` | `res://assets/characters/villagers/fisher/fisher_actor.tscn` |

The three **generic villagers** are the vendor, the netmender and the fisher: the same pieces in different cuts and
colour variants (cloth tints per villager on one shared atlas, §2).

### How m2-slice swaps a capsule (the scene is theirs; nothing here edits it)
- Under each NPC `StaticBody3D` (its origin is at the feet), replace `StandIn` and `Facing` with an instance of the
  villager's `<npc>_actor.tscn` at the local origin. The actor is the GLB turned 180 degrees: a glTF character faces
  +Z, and the capsules face -Z (their `Facing` box), so the body's existing transform stays right.
- **Materials need nothing**: the `characters` import rule (`game/data/import/characters.json`) maps every glTF slot
  to `<asset dir>/materials/<slot>.tres`, so the instanced GLB is already dressed in its skin, hair, eye and cloth
  materials. No material table, no stage script.
- **Clips**: the same rule puts `anim/<npc>_clips.tres` on an `AnimationPlayer` at the GLB root, with `idle`, `talk`
  and `walk`. Play `idle` (autoplay, or from the field script) or the villager stands in the bind A-pose; `talk`
  during a bark.
- **Faces**: the pose tables are `game/levels/_tests/characters/villagers/<npc>_face_poses.json` (all 15 emotion tags,
  shared shape API). Add them to `sequencer.json` `face_poses` under the speaker ids (`neme`, `vendor`, `reed`,
  `netmender`, `fisher`, `child`, and `osu` when M2-FP-14 adds the speaker) so lines and blinks drive the faces.
- The child is 1.27 m against a 1.1 m capsule: `Shape_child` could grow to about 1.25 m.
- `<npc>_lod1.glb` sits beside each GLB (half the triangles, no blendshapes) for a visibility-range swap if the market
  gets crowded; Godot's own auto-LODs work inside `<npc>.glb` already.

## 2. How it is built (what is shared)

One parametric build, seven params files, nothing copied from the heroes:

| Stage | Villagers | Shared |
|---|---|---|
| Body, face, rig, weights | `params/<npc>.json`: the bb_params block (height, heads tall, widths, femininity, muscle, mass, donor mix) and face sliders; **no face subdivision** (the donor's own density) | `bb_donor`, `bb_rig`, `build_asha` helpers |
| Face shapes | all 40 (30 expression shapes and the 10 visemes) kept: with no subdivision they cost about 1 MB; morph normals on the 12 expression shapes the pose tables lean on (brows, cheek raise, squint, smile, frown) | `asha_face_shapes`, `asha_glb.add_morph_normals` |
| Eyes, lashes, brows, teeth | as the heroes; the brow cards are seated on the shipped skin (`surf.project`): without the subdivision the 1.9 mm facets cross the smooth field and field-seated brows sank into the skin in dashes | `asha_eyes`, `asha_mouth` |
| Hair | `villager_hair.py`: one `HairStyle` per villager, which is also the hairline and flow interface the skin maps paint the scalp from. `short` (multi-segment cards from a crown whorl, the fringe clamped near the hairline), `cropped` (toma-style single cards), `bun` (cards traced back to a gather point that stop there, plus the knot as coiled ribbons round a ball), `wrap` (only a hairline row below the head wrap); a share of `hair_grey` cards | `asha_hair` (`_ribbon`, atlas columns), `toma_hair._emit` |
| Clothing | `villager_costume.py`: wrap top (V or round neck, sleeveless or with sleeves; or an open vest), wrap skirt, trousers, apron, sash (tails cropped short), head wrap or headband, leg wraps, sandals, each optional | `rhen_costume` (`torso_sheet`, `limb_tube`, `arm_path`, `leg_path`), `asha_costume` (`skirt`, `sandal`, `limb_wrap`, `_panel`), `toma_costume` (`sash`, `skirt_open`) |
| Head wrap | a cloth cap cast from the head centre onto the head field over the scalp from a rolled lower edge (over the hairline, above the ears, to the nape) to the crown, with soft folds, a fuller back and a two-lobed knot; `band_only` makes the fisher's headband | `asha_costume` charts |
| Skin maps | `villager_textures.py`: Asha's generator at an NPC size (head 1K albedo and normal, 512 ORM and skinmask; body 512) with per-villager knobs; plus **age** (forehead lines, glabella, nasolabial folds, marionette lines, crow's feet and the under-eye line in the normal map through a wrapped `detail_height`, a little darker in the albedo, less saturation, age spots past 0.6), **reach-bands** (toma_textures' generator with each villager's counts, seed and ink opacity; old ink softer), **stubble**, the scalp density of short hair, a lip colour per skin | `asha_textures.skin_maps`, `toma_textures._reach_bands`, `_forearm`, `_Bald` |
| Cloth atlas | **one** 2K atlas for every villager in near-neutral undyed tones (plain weave, fade, hems, a woven stripe on the sash, crepe for the wrap, linen wraps, leather sandals); each villager's `cloth_a`, `cloth_b`, `cloth_c` materials tint it (`col_albedo`), `leather` is untinted | — |
| Materials | `villagers/write_materials.py` (Asha's writer, by path) per villager folder, plus the `<npc>_actor.tscn` | eye, hair, lash, brow atlases, detail normals |
| Clips | `villager_clips.py`: `idle`, `talk`, `walk` from each villager's `_persona` (sway, lean, arms) | `hero_clips` as a library |

No shared module was changed, so Asha's, Rhen's and Toma's outputs are untouched.

## 3. Numbers

| Villager | LOD0 tris | head | body skin | costume | hair | wrap | LOD1 tris | GLB | LOD1 GLB |
|---|---|---|---|---|---|---|---|---|---|
| neme | 34,324 | 9,856 | 6,036 | 9,320 | 6,896 | — | 16,321 | 2.15 MB | 0.82 MB |
| osu | 27,706 | 9,852 | 5,586 | 8,572 | 440 | 1,040 | 13,013 | 1.67 MB | 0.56 MB |
| child | 29,330 | 9,848 | 7,266 | 7,500 | 2,500 | — | 13,826 | 1.80 MB | 0.64 MB |
| vendor | 29,262 | 9,856 | 6,590 | 9,320 | 240 | 1,040 | 13,791 | 1.72 MB | 0.58 MB |
| reed | 26,834 | 9,860 | 4,994 | 7,884 | 1,880 | — | 12,576 | 1.76 MB | 0.65 MB |
| netmender | 28,416 | 9,872 | 7,020 | 7,428 | 1,880 | — | 13,366 | 1.83 MB | 0.68 MB |
| fisher | 29,768 | 9,856 | 8,260 | 6,316 | 2,800 | 320 | 14,044 | 1.83 MB | 0.65 MB |

Every LOD0 includes 2,216 eye triangles. Textures per villager about 2.5 MB (eight maps); the shared cloth atlas 3.6 MB
(its 2K normal is 2.94 MB, the largest file). `tools/tests/test_villagers.py` holds the budget (20-36k LOD0, under
3 MB per GLB).

## 4. Strict §14 assessment (lavapipe, stage lighting)

**Field and battle range: believable.** The lineup reads as a village: seven distinct people by height, build, age and
dress, in the haluna.md palette (indigo, sea blue, sand, one red note). The elder's white head wrap and stoop, Neme's
apron and knot, the vendor's indigo wrap, the Reed's imported white, the netmender's grey crop and the fisher's red
band all read in silhouette. With the `idle` clip they stand naturally (arms down, a slight sway; Osu leans).
Nothing reads chibi or toy-like.

**Close range (the face shots): passable for NPCs, not hero quality.**
- Faces read as people, each different, with no doll stare (the heroes' eyes, lids and lashes). Without the face
  subdivision the lips are slightly puffy and the soft smile a little pursed; the jaw and lip silhouettes are a
  touch faceted at 0.6 m.
- **The child does not convincingly read as a child up close.** The donor ships only young-adult macro targets
  (ADR 0021 vendored no child targets), so his face is an adult face scaled to a child's head with the young sliders
  (big eyes, small nose, chin and jaw, no brow ridge). His proportions (1.27 m, 6.2 heads, short legs, narrow chest)
  carry him at field range; at the face camera he reads as a small adolescent. A real fix is the MakeHuman child
  targets (more CC0 data under ADR 0021's scope, an Art/Lead call) or a child head remap of our own.
- Age is in the textures and the posture, not the shape: Osu's folds and wrinkles are normal-map lines and darker
  albedo; her face shape is the donor's adult. The marionette lines were toned down after they read as cuts.
- Short and cropped hair: the heroes' long-strand atlas at short lengths. The Reed's crop reads brown and flaky close
  up (the stage's orange key and 85% scalp density over warm skin, as Toma's did); the netmender's grey crop reads as
  salt-and-pepper flecks. The boy's and the fisher's fringes are a little stringy.
- Head wraps read as wraps from the side and back (the knot) but a little like a soft cap from the front; the crepe is
  faint.
- Clothing: clean pattern-grid panels with soft folds. The skirts are smooth cones (no walking cloth sim); the sash
  knots are simple balls; the open vest is plain.

## 5. Known gaps and follow-ups (honest list)
1. The child's face (above). 2. No props: the Reed's broom stays the capsule's `Broom` node (re-parent it to a
   `BoneAttachment3D` on `DEF-hand.R` with the `idle` clip, or a pose with the hand closed); no rag and bowl for Osu,
   no net for the netmender, no wrapping leaf for the vendor. 3. A short-hair atlas column (shared with Toma's
   follow-up). 4. Clips are only `idle`, `talk`, `walk`; Osu's H08 scene (cleaning shells, patting one) needs its own
   (M2-FP-14). 5. A GPU capture for the skin and hair verdict.

## 6. Act I additions: Tavi Orse and Mother Kell (M3-CHR-03)

Design: [`act1_npcs.md`](act1_npcs.md) §3-§4. Jobs `villager_tavi`, `villager_kell`, `props_wick`. Shots
`villager_{tavi,kell}_{front,face,idle}`, `villager_tavi_clip_name_rite`, `villager_kell_clip_press_wick`,
`villager_lineup_act1` (the two with seven Haluna villagers).

| Villager | LOD0 | head | body skin | costume | hair | band | LOD1 | GLB | LOD1 GLB |
|---|---|---|---|---|---|---|---|---|---|
| tavi | 30,198 | 9,856 | 7,970 | 7,036 | 2,800 | 320 | 14,258 | 1.85 MB | 0.66 MB |
| kell | 33,596 | 9,856 | 8,056 | 9,968 | 3,500 | — | 15,958 | 2.03 MB | 0.76 MB |

**New in the build (opt-in per params file; the seven above are byte-identical):** `_build.host_snaps` (M1-CHR-14's
host-determinism snaps), `_build.garment_fit` (top on the torso only, skirt and apron follow the legs, sandals on the
feet), top `armhole_drop_m` / `cover_margin_m`, skirt `keep_above_knee_m`, `_skin.fingertip_oil`, and per-villager
scene clips (`villager_clips.EXTRA_CLIPS`). Tavi and Kell are in `tools/dev/rig_checks.json` as villager entries, and
`rig_probe.py --hero tavi` probes them.

**Read (lavapipe):** both read at field range in the lineup. Tavi is the tallest of the nine, with an inverted triangle,
the teal kit, the ochre sash and the dark band. Kell is short and wide, with a big ochre apron front, a cropped grey
head (no wrap, so she does not read as Osu) and nearly bare forearms. At the face camera, Tavi's band sits across the
brow but reads a little like a soft visor, as the fisher's does. Kell's crop is flaky up close (§4). Her face is the
donor's adult face, broad and a little masculine; her age is in the lines and the posture.

**Scene props (one source, `assets_src/characters/props/wick.py`):** `assets/characters/props/wick/wick.glb` (origin
at the wick's middle, length along +Y; on a `BoneAttachment3D` for `DEF-hand.R`, between the thumb and the index
finger, offset about 1 cm from the palm). `wick_bundle.glb` and `trimming_shears.glb` have their origins at the hang
point; hang them on a `BoneAttachment3D` for `DEF-spine` (the hips) at the apron's right, about 12 cm to her right
and 13 cm in front of the hip joint at sash height, so they clear the apron. The wick is never fitted to Rhen's
lantern.
