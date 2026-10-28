# Kahre, the Forge-Crowned (`kahre`), Asha's Lightning Vowbound

**Who:** the second Vowbound (docs/kb/story/vowbound.md §2): the glimmer of **Daro Pemakan**, the 36th Cantor, a
seventy-one-year-old terrace smith of Pemakar, the oldest Cantor on record. He went because the chosen girl died of
fever and the Calm was failing. Gruff, practical, and tired of three hundred years of standing still. Bound in the
anvil hall of Ashcrown (Ch5 B10, `ch05_kahre_bound`; environments/ashcrown.md §2.4). **Kind:** a Vowbound, so bound
light, not an animal and not Undertow-spawn. **Role:** an ally. Asha calls him (vowbound.json `kahre`: `attack`,
`forge_bolt`; Swell technique `last_strike`), and he stands alone on the middle party slot while the party has
stepped off, as Ilun does.

**The idea:** a towering beast with a hornbill's head, built like a smith: heavy forearms he walks on like a smith's
fists on the bench, a shoulder hump, and a chest that **is an anvil**, a dark iron plate in the anvil's own profile
(the flat face under his throat, the horn jutting forward, the waist below), with the white star of an old strike
on it. A **mane of running sparks** stands along the back of his neck: zig-zag bolts of bound light, rigid geometry
that moves only with his neck. **A smith's hammer is fused into his casque**: its handle grows out of the casque,
standing up like a crest, and its iron head sits crosswise on top. It is the keepsake, the one thing about him that is
an object and not light. He reads as **weight and work**: planted, square, patient, and when he strikes, the whole
body goes into one blow.

Original design (README rule 1). It starts from two real animals, a ground hornbill's casque and bill and a bison's
hump and stance, and one human object, a Pemakar terrace smith's cross-peen hammer with a cloth-wrapped ash handle. No
teeth, no horns other than the casque, no armour other than the anvil plate.

## Silhouette and size

| | |
|---|---|
| Height | **3.37 m** to the top of the hammer's head (the casque's top at 2.95 m, the shoulder hump at about 2.6 m, the hips at 1.38 m) |
| Length | 2.85 m from the rump and tail (z −0.89) to the bill's tip (z +1.96): upright and compact, not long (see the framing below) |
| Width | 1.7 m across the shoulders' and fists' outsides (x ±0.85) |
| Stance | four feet planted on the water: the fists (knuckle-walking) at z +0.7, x ±0.56, and the three-toed hind feet at z −0.46, x ±0.42 |
| Head | a ground hornbill's: a long down-curved bill (0.8 m), a laterally flat casque along its top with an upturned front, two bound-light eyes |
| The hammer | a 0.40 m ash handle rising from the casque, raked back 10°, a 0.48 m iron cross-peen head across its top (face forward, peen back) |
| The anvil | a dark iron plate on his chest: the face (flat top) 0.42 m deep with its top at 1.9 m, the horn to z +1.48, the waist down to 1.3 m |
| The mane | 25 zig-zag spark-bolts (0.3–0.62 m) in three rows along the back of the neck and over the hump |
| Tail | five hornbill tail feathers hanging behind the rump (to 0.85 m over the water), fanned, banded pale near the tips |

**Why 3.37 m.** He has to read as the larger of the first two Vowbound in kind, not in span: Ilun is wide (4.6 m) and
low (1.92 m), Kahre is tall and narrow. 3.37 m is about twice a hero (Asha 1.62 m), so at the battle camera (README
rule 6: about 110 px a metre at 720p) he stands about 370 px tall, and he is the tallest thing on the field. The
ceiling is the summon frame: the camera `summon` shot (choreo.json camera.shots) sits 4.2 m back along the battle
axis and 2.6 m to the viewer's side of his mark, 0.35 m up, looking at a point 1.6 m above the mark with a 46°
vertical FOV. It is about 4.95 m away, so at his mark it holds roughly −0.5 to 3.7 m vertically. The camera is behind him, so the
hammer, at his far (front) end, sits lower in that frame than his height suggests.

**The framing check (M3-CRE-640, numpy projection of every vertex, no render).** Measured with the director's own
math (`shot_pose`: the battle axis is the default camera's flat −x, the viewer side its flat +z) on the Vowbound slot
(battle_sandbox.tscn party Slot1, x 3.0, z −1.1), the model turned by `yaw_deg` −90, 16:9:
- **Default battle camera.** His length runs along the battle axis, i.e. across the screen, and slot 1's mark sits at
  u 0.765 of the screen width, so only about 0.85 m behind his mark is inside the safe frame's right edge (u 0.85,
  safe_frame right 0.15). The first build (3.6 m long, centred on the mark, tail out behind) crossed it at u 0.92,
  the same failure as Ilun's tail. So he is built **upright and compact**: the hips forward under him (z −0.42), the
  rump at z −0.89, the tail feathers hanging down instead of back. As built, every frame of every clip keeps u ≤ 0.851
  (idle 0.848, attack 0.849, hit_b's peak 0.851, the KO 0.843, Last Strike 0.846), and the left edge is never near.
  At rest the top is at v 0.110 (inside the 0.1 margin); the raised head in `cast` (v 0.011) and the rear in
  `special` (v −0.001 for one frame at 1.23 s) go above the HUD margin, which is acceptable: during an action the
  director plays the action's lead shot, not the resting frame.
- **Summon shot.** x 0.37–0.62 of the width and the top at v 0.16–0.23 (the hammer and mane), inside the safe frame.
  His feet, like any grounded fighter's from that low camera, are below the safe frame's bottom (v 0.90, under the
  HUD's 0.26 band): the shot looks up at a point 1.6 m above his mark from 0.35 m. Nothing about the model can change
  that short of hovering him, which the design rejects (he stands on the water).

**The stand-in's anchors.** Kahre has no battle_sandbox.json row (UI's), so the default spec would give him a 1 m
height and a 0.3 m ring. creatures.json `stand_in` therefore carries **`height` 3.3** and **`radius` 0.75** (merged
last by BattleStage.stand_in_spec, and now allowed by validate_creatures.py), so the VFX anchors (effects.json
`anchor_heights`, fractions of the height from the water) land on him: chest 0.6 → 1.98 m (the anvil's face), head
1.0 → 3.3 m (the hammer), feet 0.05 → 0.17 m, and the ring is 1.05 m across his footprint. `yaw_deg` −90 turns his
+Z face toward the foes, as the heroes' actors and Ilun are turned. No `hover`: he stands on the water.

## Colour (palette.json swatches; README rule 7)

Pemakar is ash terraces and bronze (ashcrown.md: black volcanic stone dusted grey, green copper veins, red
lacquer). Kahre carries the stone and the metal; the red belongs to the temple, not to him.

| Part | Albedo | Light |
|---|---|---|
| Hide (body, neck, legs) | `volcanic_stone` `#3A3A3F`, mottled toward `storm_slate` `#3E4A57` and darker (`lacquer_black` `#1D1916`) underneath, dusted with ash (`coral_stone_weathered` `#B9AE98`, 0.25 at most) along the back, the hump and the tops of the forearms | a faint inner light: `glimmer_bound` at 1.2 on a low mask (0.05), so the dark hide reads as light held in stone |
| The anvil plate | dark iron (`lacquer_black` and `volcanic_stone`), worn to `brass` `#B08D57` at the face's edges and the horn's tip (old bronze wear) | none on the iron |
| The struck star | — | **`glimmer_bound`, 1.2, steady**: a white-hot strike point on each flank of the anvil's waist with seven jagged crack lines (raised ribbons, emission mask 1.0) |
| Bill and casque | `bone` `#E6DAC0` at the bill, going to `brass` along the casque (a hornbill's casque, in Pemakar's bronze) | none |
| Claws, knuckle plates | `bone` mixed with `coral_stone_weathered` | none |
| The mane | `salt_glass` `#BFE6E0` | **`glimmer_bound`, 1.2, steady**: emission mask 0.75 at each bolt's root to 1.0 at its tip (the sparks "run" outward) |
| Eyes | `deep_teal_shadow` `#0E4A55` | `glimmer_bound`, 0.6 |
| Tail feathers | `volcanic_stone`, with a pale `bone` band near the tips | the hide's faint light |
| **The hammer** | head: iron (`storm_slate` and `lacquer_black`); handle: `timber_weathered` `#7E6A55` ash wood, a `sand_cloth` `#C9B48E` wrap | **none**: it is an object, not light |

Albedo stays between `lacquer_black` and `gauze_white`. No `spawn_wound` anywhere: **he has no weak point** (ADR 0151
is for foes; he is an ally). No `glimmer_held` or `glimmer_lift`: he is bound until his Act III release, and only then
does his light turn to rising gold (color_script rule 1; not built here). No lacquer red, and no orange: his
element is lightning, but his light is bound light (color_script rule 2), so the sparks are `glimmer_bound` teal like
Ilun's net. The white flash and the thunder of every blow are battle VFX and audio, not the model.

**The bound light (color_script.md rule 2).** Every emissive slot is `glimmer_bound` at 1.2 with `emission_pulse_hz`
0: no breath, no flicker, no drift, no shed motes, no trails, **no particles**. The mane is rigid geometry skinned to
the neck and chest bones, so it moves only because his neck moves.

**Translucency.** As with Ilun, the creature shader is opaque: he reads as spectral through the faint inner light, a
rim sheen on the hide, and the bright mane and struck star, not alpha. The keepsake is the only matte, unlit thing.

## The anvil chest

A smith's anvil in profile, built as three rounded blocks (no image, no texture): the **face**, a flat slab 0.42 m
deep and 0.68 m wide just under his throat (its top at 1.82 m); the **horn**, a tapered cone jutting forward from the
face to z +1.4 and curving a little down; and the **waist**, narrowing from the face down to his sternum at 1.25 m.
All three ride the `chest` bone, so the plate heaves with his breathing and leads every blow. Seen from the default
battle camera (his left side) the anvil's profile is the silhouette of his chest. The **struck star** is on both
flanks of the waist: a bright strike point (a 5 cm boss) with seven jagged crack lines 0.09–0.2 m long, raised 6 mm,
in their own emissive slot `strike`.

## The spark mane

Twenty-five zig-zag bolts in three rows (nine in the middle row upright in the neck's plane, eight in each side row
splayed 25° outward), from the back of the skull, down the neck's crest and over the shoulder hump. Each is a flat
double-faced blade (a lightning bolt in profile: four kinks, a seeded `default_rng` jitter), 0.3 m long at the skull,
0.62 m at mid-neck, shorter on the hump, 8 cm wide at the root tapering to a point. They are flat in the neck's plane so the
default camera, which sees him from the side, sees their full zig-zag. Skinned with the neck's chain weights (the
hump's to `chest`).

## The hammer (the keepsake)

A Pemakar terrace smith's cross-peen hammer, scaled to him (its head about 0.5 m with the face and the peen, its
handle 0.40 m visible): the handle grows out of the casque's top behind the eyes and rakes back 10°, wrapped in
`sand_cloth` where it leaves the casque, and the iron head sits crosswise on its top, the flat face forward, the wedge
peen back. It is rigid on the `head` bone, fused, so every head blow is a hammer blow: because the face looks
forward, any nose-down swing leads with it. In `attack` the face meets the foe at chest height (1.41 m, 2.1 m in
front, looking straight down); in the Last Strike his head comes down past vertical, the bill tucked under, and the
face is the lowest point of him at the contact (its lowest vertex 3 cm over the water, 1.6 m in front of his mark). It never glows. In the finale it is the last thing to fade (not built here).

## Clips (contact seconds go in creatures.json `contact`)

All in place: the stage moves him (the entry's rise from 2.6 m under the water, the dismissal's sink, the fall's tip
back and draw under; choreo.json `vowbound`), and the clips play on top. **He is grounded**: every planted foot is
solved onto the water at every frame (a two-bone solve per leg in its own plane, the foot kept level), and every
frame of every clip stays at or above the water (GroundedClipsTest, no allow-list).

| Clip | Length | What it shows |
|---|---|---|
| `idle` | 4.0 s, loop | slow, heavy breathing (the anvil heaves), the head swinging a little and the weight shifting between the forearms; all four feet planted |
| `ready` | 1.4 s | he squares up: the head comes up, he stamps the left fist once (lifted 0.25 m at 0.45 s, down at 0.7 s), the bill clacks |
| `attack` | 1.2 s, contact **0.55 s** | the casque strike: the neck draws back and up (0.3 s), then the head drives forward and down so the hammer's face leads, the body lunging behind it; also the plain `attack` |
| `cast` | 1.6 s, contact **0.8 s** | Forge Bolt: he lifts his head to the sky with the bill open (calling the strike down into the hammer), then thrusts the head at the foes on the contact, bill open, and settles |
| `hit` | 0.5 s, peak **0.1 s** | rocked back on his haunches, the head snapped up and back, the bill opening |
| `hit_b` | 0.5 s, peak 0.1 s | authored, not mirrored (the kit's scaled copy would push the solved feet through the water): rolled to the other side, heavier |
| `defend` | 1.2 s | he braces: drops 0.12 m, the head pulled in low over the anvil, casque forward like a shield; held 0.3–0.85 s |
| `ko` | 2.0 s | setting the tools down: a last lift of the head, then his legs fold and he lies down on the water (the hips 0.8 m lower), the head laid forward and down with the hammer's face turned down to the water, held from 1.6 s |
| `victory` | 2.2 s | a short rear (the forearms lift), both fists come down together at 1.0 s like a hammer on the anvil, the head high and the bill clacking |
| `rise` | 2.6 s | stepping up out of the water as the stage lifts him: from crouched with the head bowed, he plants the left fist up and forward, then the right, straightens and lifts his head |
| `dismiss` | 1.0 s | he bows his head and sets the hammer down toward the water; it ends bowed (the stage sinks him) |
| `special` | 2.8 s, contact **1.55 s** | Last Strike: he rears on his hind legs (18°), the forearms drawn up, the neck arched back and the hammer high (0.9 s), holds (to 1.25 s), then the whole body comes down into one overhead blow, the forearms planting 0.18 m forward and the hips dropping 0.4 m, the head driving the hammer's face onto the water in front of him at the contact; held braced to 1.95 s, then he straightens |
| `idle_b` | 1.2 s | authored fidget: a shake of the head and the mane and one clack of the bill |

creatures.json maps `forge_bolt` → `cast` and `last_strike` → `special` (a creature's own action clip wins over the
style's), and `attack` is the physical default.

**What the stage plays today.** choreo.json `vowbound` names `ready` for the entry and the dismissal and `ko` for the
fall (battle-presentation's request from M3-CRE-638 asks for `rise` and `dismiss`, which Kahre has too). `ready` works
for both today: a squaring up on the way in, a last stamp on the way out.

## Rig (22 bones)

`root` (the water point), `body` (the hips, 1.3 m: rearing pitches about them), `chest` (the shoulders and the
anvil), `neck_0..2`, `head` (skull, bill, casque, the hammer), `jaw` (the lower bill), `arm_l0`, `arm_l1`, `hand_l`
and `arm_r0..`, `hand_r` (the forearms: shoulder, elbow, wrist; +x is `l`), `leg_l0`, `leg_l1`, `foot_l` and
`leg_r0..`, `foot_r` (hip, knee, ankle), `tail_0`, `tail_1`.

**Lowest vertex per clip** (skinned from the GLB, GroundedClipsTest's measure): 0.000 m in every clip (a planted
foot's sole, held on the water by the solve); nothing else reaches the water. Highest: the Last Strike's rear,
4.11 m; the resting top is 3.37 m.

## Budget

≤ 16k triangles (a Vowbound; the creature range is 5k–16k), GLB ≤ 2 MB. Seven slots: `body`, `anvil`, `strike`,
`mane`, `beak`, `eye`, `hammer`.

**As built (M3-CRE-640):** 14,080 triangles (feet and fists 3,440, limbs 2,128, torso 1,904, bill and casque 1,656,
anvil 1,272, neck 1,040, hammer 1,008, mane 500, skull 360, strike 352, eyes 240, tail 180), 7,986 vertices,
22 bones, 13 clips, GLB 1.37 MB.

## As built: the held form (M3-CRE-647, 2026-10-28)

The foe form for the Ch20 release fight (act3_roster.md, "The Vowbound as foes").

- **`release`** (3.4 s, its KO as a foe; the only clip added, every other clip samples identically): "setting the tools down": he draws himself up to full height, the casque and its hammer raised to the sky, held (0.6–1.8 s); then the weight goes out of him, the head settles, and he lifts off the water 1.5 m up and 0.5 m back, the feet still solved, hanging easy. Relieved, not felled.
  Lowest vertex over every frame 0.000 m. GLB 1.37 → 1.46 MB.
- Scene `game/creatures/kahre/kahre_held_battle.tscn` (the same GLB; `CreatureActor.material_dir` puts on `assets/creatures/kahre/materials_held/`, written by write_materials.py from the `held` block in materials.json: 4 emissive slots glimmer_bound to glimmer_held `#7FC6D9` at the same energy, steady; the rest as they are). creatures.json row `kahre_held`: no `vowbound` key, `ko` = `release`, `phases.release` = {clip `release`, `hold` true}, `stand_in.yaw_deg` 90 (facing the party), height 3.3 and radius 0.75 kept. Review shot `creature_kahre_held` (not rendered yet). No enemies.json row (Combat's, with the chapter designer). The turn to `glimmer_lift` and the rising motes are presentation (battle VFX), not the model.

## Final pass (M3-CRB-008, 2026-10-28)

ADR 0041 (Act I at final quality). The critique of the M3-CRE-640 render: primitive. Plain cylinder limbs on ball
joints, a smooth bean of a body, a black box for the anvil, a white plastic comb for the mane and a tiny block on a
stick for the hammer. build_kahre.py's mesh is rewritten on the same kit. The skeleton's joints, every clip name, the
contact times (creatures.json unchanged: attack 0.55 s, cast 0.8 s, special 1.55 s), the held form (`release`,
`materials_held/`, kahre_held_battle.tscn) and the seven material slots are all kept.

- **Sculpted, not lofted tubes.** Every hide part is a ring grid along its path, displaced along the normal by
  anatomy: muscle masses (ellipsoid blobs), grooves (segment falloffs) and the stone's lumps (two octaves of fbm,
  plus a third on the torso). The torso has a hump (+0.16 m), shoulder masses that carry the arms, scapulae, a deep
  keel under the chest, pectorals, haunches, four ribs a side under the hide, a furrow along the spine and a tucked
  belly. The neck is thinner (0.28 to 0.12 m) with six throat folds, the nape's muscle and cords down each side.
- **Smith's arms.** A domed root inside the shoulder mass, a deltoid down the arm, biceps and a heavy triceps, a
  bony elbow point, then the forearm swelling to 0.225 m below the elbow (extensors and flexors parted by a groove)
  with five tendons standing out toward the wrist, and three wrap-round keratin scutes down its front. The fist: a
  broad back of the hand, three thick curled digits with knuckle bulges and knuckle plates, hooked claws (10 cm)
  resting on the water ahead, and a short thumb on the inside. The hind legs: a heavy haunch and thigh (quadriceps,
  hamstrings), a calf, a bird's tarsus with three scutes down its front, and banded, scaled toes.
- **Hide: dark stone and old iron, never teal.** Charcoal (`lacquer_black` with `volcanic_stone`) to ash-grey
  (`volcanic_stone` with `coral_stone_weathered`), mottled, with a little `tortoiseshell` warmth. Ash collects in the
  grain of the upper surfaces and on the worn tops of the muscle masses, the underside goes darker, and the creases
  and cavities (measured from the surface's concavity and the sculpt) go ember-warm (`lacquer_black` with
  `tortoiseshell`), with cavity in UV2. About 40 jagged cracks (kinked strips 9–12 mm wide, half of them branched) run over the
  flanks, shoulders, neck and limbs. **The hide has no light of its own any more**: the faint `glimmer_bound` mask
  0.05 of the first build tinted the stone teal, so it is dropped (the body slot keeps its emission colour for the
  held swap, with a 0 mask). materials.json `body`: rougher (0.88), detail scale 28, albedo 0.35, bump 2.0 (pitting),
  cavity 0.5, rim sheen 0.25. The detail coordinate wraps each part (along its path and round it, the seam on the
  hidden side), so the pitting is not smeared.
- **Plated keratin over the back.** 24 shingled scutes in five columns from the hump to the rump (24 triangles each:
  a curved sheet with a low keel, its front and sides sunk into the hide, the rear free edge standing proud over a
  dark lip, worn pale along it), plus the forearm, knuckle and tarsus scutes. They share the hide's `body` slot (matte
  horn; the glossy `beak` slot caught the sky and went white).
- **The anvil is the sternum.** The face (0.42 × 0.56 m, its top at 1.92 m) worn bright `coral_stone_weathered` to
  `gauze_white` in the middle (the wet channel marks the polish; `anvil` has no wet darkening and a clearcoat), iron
  at the sides worn to brass along the top edges, rust (`tortoiseshell`) in the pits; the hardy hole (square) and the
  pritchel hole (round) at the heel; 16 hammer scars on the face (dark dents and bright fresh strikes); the step; the
  horn (to z 1.64) tipped brass; the waist deep front to back, pinched, going down and back into the keel. The struck
  star sits on each flank of the waist (rays 10–20 cm).
- **The casque**, massive and sculpted: it rises from the brow (where it merges with the skull) to a tall keel over
  the bill, and its front sweeps up off the bill into an upturned horn. It is laterally flat and wider at its foot,
  with two grooves along each flank and six growth lines across it (both cut in the geometry and darkened), and
  horn grain along its length: worn ivory (`bone`) along the top, `brass` on the flanks, darker brass and horn in the
  grooves.
- **The hammer (the keepsake, `vfx_keepsake`).** An octagonal forged head (0.65 m, 0.2 m across the flats,
  flat-shaded so the facets read), a neck behind the chamfered face, the face slightly domed and worn bright, the peen
  a cross wedge; the eight chamfers' worn edges catch the light; iron with rust; a wedge and the handle's end grain on
  top. The ash handle (8.4 cm thick) leaves the casque 0.3 m below the head's centre, raked back 10°. Its foot is grown
  over by the casque (a lumpy ivory-and-brass collar with three tendrils climbing the wood), and a leather strap
  (`tortoiseshell` with `lacquer_black`) is wound six times over the grip. No light (it is the one object).
- **The mane: running sparks.** 240 filaments of bound light along the back of the skull, down the neck's crest and
  over the hump, rooted on the surface. Each is a thin double-faced blade (2.8 cm at the root to a point) kinked
  once or twice in a spark's zig-zag and swept back. They come in three layers: the long middle (up to about 0.8 m at
  mid-neck) and shorter flanks, splayed to the sides. `salt_glass` at the root to `foam_white` at the tip, emission
  mask 0.7 to 1.0, `glimmer_bound` 1.2, steady. Each filament is rigid on the bone under its root.
- **Head:** a larger skull (0.35 m) with brows over sunken eye sockets, cheeks and a ground hornbill's heavy lashes
  over each eye. The bill has a culmen ridge and a keen cutting edge, dark horn at the base going to ivory with a
  worn tip.
- **Tail:** five feathers with a raised shaft and a fringed vane, charcoal barred with ash, a pale band near the tip.
- **VFX anchors (unweighted):** **`vfx_core`** on `chest` at (0, 1.86, 0.42), the chest's centre behind the anvil,
  and **`vfx_keepsake`** on `head` at the hammer head's centre (0, 3.20, 1.08). Rig: 24 bones.
- **Last Strike:** the casque's upturned horn reaches further down than the old casque, so `special`'s blow
  (`BLOW`) lowers the hips 0.31 m instead of 0.4 m (and 0.28 m on the held brace). At the contact the casque's horn
  tip touches the water and the hammer's face is 5.5 cm over it. The head bone is at 0.80 m, 2.3 m under the held
  rear (the test asks for under 0.9 m and at least 2.0 m). Contact second unchanged.

**As built:** 17,706 triangles (≤ 18k): mane 2,240, limbs 2,544, torso 2,040, hands 1,548, anvil 1,346, feet 1,312,
casque 1,040, plates 1,008, neck 960, bill 712, cracks 482, tail 440, skull 384, collar 324, hammer head 320, handle
280, leather 246, eyes 240, struck star 240. 13,093 vertices, 24 bones, 14 clips, GLB 1.91 MB. Rest bounds: x ±0.81,
y 0 to 3.35 m (the hammer), z −0.89 to 1.96, so the framing checks above still hold (narrower and no taller). Lowest
vertex 0.000 m in every clip (a planted foot, solved). Highest: idle 3.42, attack 3.88, cast 4.04, the Last Strike's
rear 4.11, release 5.12 m. The M3-CRE-640 budget, colour (the hide's inner light), anvil, mane and hammer
descriptions above are history where this section differs.

**Not done:** no portrait (test_creature_portraits fails on the missing Vowbound portrait PNGs, before and after this
pass). A real alpha shader for the spectral read is still a kit change (another track's).

## Polish (M3-CRB-008, 2026-10-28)

Two flaws seen in the final-pass render; nothing else is redone.

- **The hammer is fused, not perched.** It stood on a 0.2 m stick over the casque like a hat ornament. Now the
  handle (thicker: radius 5.2 cm, worn ash) is sunk into the casque at z 1.40, in the saddle in front of its hump,
  raked back 16°. The head lies along the crest, face forward and tilted up with the horn's sweep, with its underside
  resting on the hump behind the handle (2 to 9 cm over the crest along its length), so the casque and hammer read
  as one silhouette. Only 8 cm of handle shows. The casque's keratin has grown up round its lower half (to 4.8 cm) in
  three layered ridges. Each ridge is a shelf whose lip overhangs the one below and wanders round the handle, higher
  on one side. The growth is long along the crest and narrower than the casque across it, so it sinks into the
  flanks, and a dark crack splits it up the front where it tore round the wood. A leather wrap (2.6 turns) covers the
  wood between the growth and the head. The forged head is unchanged. **`vfx_keepsake`** moves with it, to
  (0, 3.065, 1.349) on `head`.
- **Forearm plates with a clean lip.** The three scutes down each forearm sank into the hide, where the hide's bumps
  cut a ragged line. They are now laid onto the arm's own surface: their five columns land on the arm grid's
  segments, so the sheet never chords under a bulge. Each is a domed sheet standing proudest at its wrist edge, longer
  than before so that each tucks under the free edge of the one above. All round it runs a bevelled lip, raised a
  little and worn pale, with a doubled outline so the edge stays crisp. The lip turns down over the hide to 4 mm
  under it, and its foot is a dark seam (cavity 1). 64 triangles a plate instead of 24.
- **Last Strike:** the hammer's face now sits lower and further forward, so the blow's hips come down 0.245 m
  instead of 0.31 m (0.215 m instead of 0.28 m on the held brace). This keeps the face landing *on* the water
  (lowest vertex −0.002 m) and not 6.7 cm through it. Contact second unchanged.

**As built:** 17,830 triangles (≤ 18k): plates 1,248, collar 448, handle 160, leather 126, hammer head 320, the rest
as above. 13,162 vertices, 24 bones, the same 14 clips. Rest bounds y 0 to 3.25 m: the hammer is 10 cm lower, so the
creature is now shorter than its 3.3 m stand-in.

## Polish 2 (2026-10-28)

The wrist, where the forearm runs into the back of the hand, showed a ragged intersection line up close. A **wrist
cuff of hide folds** now wraps each wrist below the last forearm scute: a short ring loft (4 rings × 10, 80
triangles) skinned with the forearm, its upper edge tucked under the forearm's hide, swelling 2.5–3 cm proud in four
creased lobes, and its lower lip turned down over the back of the hand (cavity dark at both edges, ash on its top
like the rest of the hide). 17,990 triangles (≤ 18k; was 17,830). Bones, clips, contacts and anchors unchanged.
