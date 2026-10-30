# Ethren, the Level Saint (`ethren`), Asha's Vowbound: design sheet (proposed, M3-CRE-644)

**Who:** the sixth Vowbound (docs/kb/story/vowbound.md §6): the glimmer of **Corran Ysel**, the 60th Cantor. He sang
24 years ago, a 31-year-old Ansedran Tender and Ysolde's husband: patient, funny and a terrible cook. He was displaced
when Imra sang, then placed in the Sanctum of the Level as the Order's showpiece Saint. He is bound in Ansedra (Ch13).
**Kind:** a Vowbound: bound light. **Role:** an ally, Glimmer. His battle identity is stillness: Slow and Stop on foes,
and mass wards on the party. His Swell is *Still Water*. **Status:** built (M3-CRE-644, 2026-10-27; first PC render
pending); he is not yet in vowbound.json (creatures.json `vowbound_pending`: M3-CRE-644).

**The idea:** the Order's ideal made literal: an armoured, winged figure of **gold lacquer** with a **veiled face** and
a **bowl-halo** behind the head, lit from inside by a steady bound light that never drifts. He is beautiful and
impersonal. **A plain copper wedding ring** sits on one gauntleted finger, the keepsake: the only human thing about
him, and the only part of him that does not shine.

**People or creature?** He is a winged *figure*, not a person: Corran never appears in it except as the face under the
veil, in the final fight (Act III, Ch20, cinematics). So the form is this track's, built with the creature pipeline. If
the characters track's base body (MPFB2 topology, ADR 0021) would serve its proportions better, a shared build is a
fair request. The veil-fall face is theirs (Corran's face, a person).

## Silhouette and size

| | |
|---|---|
| Height | **3.0 m** to the top of the halo (head at 2.3 m): a standing figure, hovering 0.2 m off the water, the robe's hem 0.1 m above it |
| Wings | four, folded close behind him like a closed screen: long, flat lacquered panels (not feathers), 2.0 m tall. They open only in `ready`, `cast`, `special` and `victory`, to 3.6 m across. Folded at rest, so the HUD's right edge stays clear |
| Armour | a long, smooth, closed armoured robe like a lacquer shrine-figure, no visible body. It has gauntlets, and the hands are the only joints that read as human |
| Veil | a fine, still veil over the whole face, falling to the chest: it never moves, even when he does (the stillness) |
| The halo | a shallow bowl-shaped disc behind the head, 0.9 m across, its inner face lit |
| The ring | a plain copper band on the left ring finger, matte: albedo `laterite` toward `tortoiseshell` (the palette has no copper; the closest unlit warm metal), roughness high, no emission, no metallic shine |

## Colour, and the gold budget

palette.json limits `gold_leaf` and `gold_leaf_hi` to **≤5% of the frame area in any shot**. A gold figure filling the
summon shot would break that. So he is built as the Order builds its shrines:
- the bulk is `lacquer_black` `#1D1916` and `lacquer_red_deep` `#7A1712`, a deep lacquer whose glossy highlights
  carry the light;
- `gold_leaf` only on the **edges**: panel rims, the halo's lip, the gauntlet ridges and the veil's border. That is
  enough to read "gold lacquer" at battle distance and stays inside 5% (to be measured on his first render, as the
  palette tool does).

If the Lead wants him truly gold all over, that needs a palette exception (Ansedra's interiors already have a
lacquer_red exception at ≤15%); this sheet does not assume one.

| Part | Albedo | Light |
|---|---|---|
| Armour and robe | `lacquer_black`, `lacquer_red_deep` panels | none on the surface |
| Edges, halo lip | `gold_leaf` (metallic 1.0) | none |
| Halo inner face, armour seams | — | **`glimmer_bound` 1.2, steady**: the bound light is *inside* the lacquer shell and shows at the seams and the halo, never as a surface glow |
| The veil | `gauze_white`, thin | faint `glimmer_bound` (0.2) from behind (the face under it is never seen here) |
| The ring | `laterite`/`tortoiseshell`, rough | **none** |

This colour plan also serves the story: the light under his gold is the same bound glimmer the Order burns Saltwright
camps for (vowbound.md §6, Ch13). His seams glow exactly like the Lit Age machines, the flat-engine and the Lamp
Engine, which is the Act II truth hanging in plain sight.

## Clips

| Clip | Length | What it shows |
|---|---|---|
| `idle` | 4.0 s, loop | **almost nothing moves**: a very slow rise and fall of 1 cm. The veil is still. His stillness *is* the idle, the most still thing on the field |
| `ready` | 1.4 s | the wings open a little; the halo stays as it is (bound light is steady, so it never brightens) |
| `attack` | 1.2 s, contact ~0.55 s | one gauntleted hand raised, palm out, then a downward press: no weapon |
| `cast` | 1.6 s, contact ~0.8 s | Slow and Stop: both hands spread level, palms down, as if smoothing water flat |
| `ward` (or `cast`) | 1.6 s | the wings open forward around the party's side, a lacquer screen |
| `hit` | 0.5 s, peak ~0.1 s | a small, stiff recoil; the veil doesn't move |
| `defend` | 1.2 s | the wings close in front of him |
| `ko` | 1.8 s | he kneels, his wings folding down; the halo tips |
| `victory` | 2.2 s | wings fully open, the hands lowered, utterly still at the end |
| `rise` | 2.6 s | from kneeling, wings closed, he stands |
| `dismiss` | 1.0 s | he kneels again |
| `special` | 2.4 s, contact ~1.45 s | Still Water: wings flung fully open, both hands pressed down; at the contact everything on the field stops (VFX and the battle's own stop) |

## Rig and budget

About 30 bones: `root`, a three-bone `spine`, `neck` and `head` (the veil rigid on the head), two bones per arm plus
hand, and two finger groups on the ring hand so the ring can be framed. Four wings of two bones each, and the halo
on the head. Up to 16k triangles. Seven slots: `lacquer`, `lacquer_red`, `gold`, `seam`, `halo`, `veil`, `ring`.

## Open questions
- His vowbound.json row (Combat).
- The gold budget: edges only (the default above) or a Sanctum-wide palette exception (a Lead ADR).
- Corran's face under the veil, for Ch20's veil-fall: the characters track's, with the veil a separate rigid piece
  that cinematics can drop.

## As built (M3-CRE-644)

The build is `assets_src/creatures/ethren/build_ethren.py` → `assets/creatures/ethren/ethren.glb` (the Blender job
`creature_ethren`). **14,406 triangles** (budget 16k), 27 bones, 13 clips, GLB 1.53 MB. Per slot: `lacquer` 5,392,
`lacquer_red` 3,012, `gold` 3,444, `seam` 1,350, `veil` 672, `halo` 320, `ring` 216. Rest bounds: x ±0.59, y 0.10 (the
hem) to 3.01 (the halo's lip), z −0.68 (the folded wings' lower back edges) to +0.56 (the fingertips).

### Changes from the proposal above (recorded here, as the task allows)

- **Height.** As proposed: head centre 2.33 m (crown 2.47), the halo's top 3.0 m. The sole line (the feet, not
  modelled under the robe) is 0.2 m over the water and the robe's hem 0.1 m; he is **built hovering** (the origin is
  the water under him, no stand-in `hover`), as Ilun is. Every clip stays above the water (GroundedClipsTest, no
  allow-list entry).
- **The robe is three nested lacquer bells** (the top one red, the lower two black, each with a gold hem): a closed,
  rigid robe that can still kneel. When he kneels the bells **telescope** into one another (the hips sink 0.45 m, the
  middle bell 0.24 m, the bottom 0.04 m), so nothing bends or stretches. There are no legs: the bells are the robe's
  joints, and the `robe_1` and `robe_2` bones carry the lower two. A ring of bound light closes each join.
- **The wings.** Four wings of two flat leaves each (an upper and a lower leaf, 0.98 m each, hinged with a bar of
  bound light): 2.0 m tall, 0.30 m wide, cusped at the free ends, the outer face black lacquer with a red inset field,
  the inner face red, gold only on the rims. Folded, they hang from a yoke on his upper back, leaning back 6° to clear
  the robe's flare, each side's inner and outer leaf turned 35° and 30° off the back plane, so from behind they read as
  a closed four-leaf screen and from the default camera (his left side) as two broad leaves, not an edge. They **open
  by fanning out** from the yoke (the inner pair to about 36°, the outer to 57°: 3.6 m across in `victory` and
  `special`), turning their faces to the field as they go. They open only in `ready` (a little), `cast`, `special`
  and `victory`. In `defend` they turn edge-forward round his sides (the "close in front" read, without crossing the
  robe); in the KO the closed screen slumps apart and down; in `rise` and `dismiss` they stay closed and ride 0.3 m up
  his back as he kneels, so they stay off the water.
- **`ward` is not a separate clip.** The mass ward plays `cast` (its kind's default) until Combat's skill ids exist;
  the clip map (`clip_by_skill`) waits on his vowbound.json row. (Superseded by M4-CRB-008: `ward` and `stop` are
  built; see the last section.)
- **The veil** is its own mesh (`ethren_veil`, slots `veil` and `gold`) on its own bone (`veil`, a child of the head
  that no clip keys): a still gauze hood hanging from a red crown band, round the face and falling to the chest at
  1.92 m, narrowing round the shoulders so it clears them; a gold border at its hem. Cinematics can hide the mesh or
  drop the bone for Ch20's veil-fall. No face is modelled under it (the head is a smooth lacquer ovoid).
- **The halo** is on its own bone (`halo`, a child of the head): a 0.9 m bowl 0.10 m deep, its concave face toward the
  head and lit (`halo`, `glimmer_bound` 1.2), its back black lacquer, its lip gold.
- **The ring**: a plain band on the left ring finger (the third finger from the thumb), in the `finger_l1` group with
  the little finger; `finger_l0` holds the index and middle. Colour `laterite` mixed 35% toward `tortoiseshell`,
  roughness 0.8, metallic 0.3, no emission.
- **Rest pose**: the hands held level before him at the waist, palms down (the Level Saint's gesture), so the ring
  is on top of the near hand from the default camera.
- **Rig** (27 bones): `root`, `body`, `spine_0..2`, `neck`, `head`, `veil`, `halo`, `robe_1`, `robe_2`, `arm_l0`,
  `arm_l1`, `hand_l`, `finger_l0`, `finger_l1`, `arm_r0`, `arm_r1`, `hand_r`, `wing_{li,lo,ri,ro}_{0,1}`.
- **Stand-in**: no battle_sandbox.json row (UI's), so his creatures.json `stand_in` carries `height` 2.5 (the VFX
  anchors' fractions; the head point lands at his crown) and `radius` 0.6 (the hem's half-width), as Kahre's does.

### Gold, measured

The gold is the hem bands, the breastplate's and pauldrons' rims, the cuffs, the knuckle ridges, the collar's rim,
the halo's lip, the wing leaves' rims and walls and the veil's border. Projected from the build's own vertices
(painter's algorithm, every visible triangle's slot counted per pixel) on the two cameras that see him:
- **default battle camera** (the Vowbound slot, 1280×720): gold 0.27% of the frame at rest, at most 0.33%
  (`special`'s contact; he fills about 3% of the frame, 9–13% of him is gold);
- **summon shot** (choreo.json `summon`): gold 1.23% of the frame at rest, at most 1.35% (`victory`, wings open; he
  fills 9–13% of the frame).

So the edges-only plan holds the palette's **≤5% of the frame** with a wide margin; no palette exception is needed.
On the first PC render the palette tool should confirm it (specular gold can bloom a little wider than its area).

### Framing (every baked frame of every clip, the camera director's math)

Projected through the default battle camera on the Vowbound slot (yaw −90) and the `summon` shot, 16:9, margins to
choreo.json `camera.safe_frame` as fractions of the screen:
- **Default camera: every frame of every clip is inside the safe frame.** Rest: left 0.67, right 0.027, top 0.074,
  bottom 0.113. The tightest frames: right 0.005 (`rise`'s start and `dismiss`'s end, the kneel with the wings hoisted),
  0.011 (KO), 0.014 (`hit_b`, `defend`); top 0.071 (`defend`).
- **Summon shot**: left, right and top inside in every clip (top 0.056 at the tightest, `hit_b`); the robe's lower
  bells sit under the HUD's bottom band (bottom −0.13 to −0.15), as any grounded fighter's feet do from that low
  camera looking 1.6 m up (Kahre's precedent).

### Clips as built

| Clip | Length | Lowest vertex (GLB, skinned) | What it does |
|---|---|---|---|
| `idle` | 4.0 s loop | 0.093 | only a 1 cm rise and fall; nothing else moves |
| `ready` | 1.4 s | 0.098 | the wings fan a little and turn their faces out; the hands lift level |
| `attack` | 1.2 s, contact 0.55 | 0.066 | the right hand rises palm out (0.32 s), then presses down |
| `cast` | 1.6 s, contact 0.8 | 0.098 | both hands swing out level, palms down; the wings part |
| `hit` / `hit_b` | 0.5 s, peak 0.10 | 0.024 / 0.008 | a stiff tip back of a few degrees, 4.5 cm back, rolled to one side (hit_b the other, heavier: authored) |
| `defend` | 1.2 s | 0.098 | the wings turn edge-forward round his sides; arms drawn in; held 0.3–0.85 s |
| `ko` | 1.8 s | 0.060 | a flinch, then he kneels (the bells telescope), bows, hands lowered, the wings slump apart, the halo tips 10° forward and 9° aside |
| `victory` | 2.2 s | 0.098 | the wings fan fully open, the hands lower; held still from 1.4 s |
| `rise` | 2.6 s | 0.060 | from the kneel, wings closed, he stands |
| `dismiss` | 1.0 s | 0.060 | he kneels again; it ends kneeling |
| `special` | 2.4 s, contact 1.45 | 0.098 | Still Water: wings flung open, the hands raised, pressed down at the contact, held still to 2.05 s |
| `idle_b` | 1.6 s | 0.098 | authored (the kit's would open the wings): the hands settle a degree, the head dips a degree |

### Requests (in the task file)

UI: a `stand_ins.ethren` row (or keep creatures.json's); Combat: his vowbound.json row and skill ids (then drop
`vowbound_pending` and add `clip_by_skill`); battle-presentation: `first_call_flags.ethren` and `rise`/`dismiss` as
the entry and dismissal clips; battle-vfx: Still Water's stop at the contact; characters: Corran's face for Ch20.

## As built: the held form (M3-CRE-647, 2026-10-28)

The foe form for the Ch20 release fight (act3_roster.md, "The Vowbound as foes").

- **`release`** (3.5 s, its KO as a foe; the only clip added, every other clip samples identically): the screen of wings opens all the way, slowly; his left hand comes forward to chest height, open, the copper ring toward Ysolde (the ring is his most forward point through the hold, z 0.69 m), held (1.5–2.1 s); then he rises 1.4 m up and 0.5 m back, the wings open, the ringed hand still held out, nearest her and last. The veil is not keyed (its fall is the cinematic's).
  Lowest vertex over every frame +0.10 m. GLB 1.53 → 1.65 MB.
- Scene `game/creatures/ethren/ethren_held_battle.tscn` (the same GLB; `CreatureActor.material_dir` puts on `assets/creatures/ethren/materials_held/`, written by write_materials.py from the `held` block in materials.json: 3 emissive slots glimmer_bound to glimmer_held `#7FC6D9` at the same energy, steady; the rest as they are). creatures.json row `ethren_held`: no `vowbound` key, `ko` = `release`, `phases.release` = {clip `release`, `hold` true}, `stand_in.yaw_deg` 90 (facing the party), height 2.5 and radius 0.6 kept. Review shot `creature_ethren_held` (not rendered yet). No enemies.json row (Combat's, with the chapter designer). The turn to `glimmer_lift` and the rising motes are presentation (battle VFX), not the model.

## As built: the Act II final pass (M4-CRB-008, 2026-10-30)

The Act I Vowbound bar (ADR 0041 §3, M3-CRB-013's move pass) for his Act II debut (ADR 0205). He was audited from the
battle camera with him standing on the party's `vowbound_slot` (a scratch fixture in an Act I arena, the Cinder
Matron's forge) and up close. ADR 0015 holds: nothing on him or in his clips is frozen; Hold the Hour and Still Water
show stillness by not moving.

**Audit fixes (in budget: 15,546 triangles of 16k, 29 bones, the same seven slots)**
- **The light reads as light, not white.** The seams and the halo had `gauze_white` under their emission, so from the
  battle camera they read as white paint. They now carry `glimmer_bound` itself, so the teal shows.
- **A bowl of light, not a plate.** The halo's inner face was one even disc. It is now lit dimmer at its centre than
  at its lip (emission mask 0.45 to 1.0), with a red lacquer rim set inside the bowl at 0.27 m.
- **A veil, not a lampshade.** The veil read as a turned white shade set on a ball: up close the bare lacquer crown
  of the head stood out of its open top, and its hem stood 0.33 m proud of the chest. A red lacquer crown cap now
  closes the head over the veil's top edge (the veil hangs from it); the hem is drawn in to 0.275 m (still clear of
  the breastplate); it hangs in six soft pleats (2 mm deep at the crown, 9 mm at the hem; 25 stations across, from
  17); and the gauze is thin: 16% toward `lacquer_black` everywhere and up to 55% over the face, where the lacquer
  head is behind it. The face is still never modelled, and the veil is still unkeyed on its own bone (Act III's
  veil-fall; the crown cap stays on the head).
- **The bells nest.** Each bell's top covers the hem of the bell above it, but the middle bell's hem stood through the
  bottom bell's front (1.7 cm) and the top bell's hem nearly touched the middle bell's mouth. The bells are re-cut
  (top: forward shift 0.01; middle: top half-width 0.36, shift 0.02; bottom: top half-width 0.50, flare 0.18, the
  hem 1 cm wider) so every join clears by 1.9 cm or more, past the 1.4 cm plates.
- **Joined panels, not cones.** Each robe bell has a band of the other lacquer at its lowest visible edge (red on the
  black bells, black on the red one: just above the mouth of the bell below, or above the bottom bell's gold hem) and
  six thin gold panel rims down it (eight wider ones read as a striped cage from the
  battle camera). The gold measured above predates these rims; they add strips 8 mm wide, a small fraction of the
  existing hem bands, so the frame stays far inside the 5% budget (the palette tool should confirm on the next PC
  render).
- **Screens, not planks.** The red inset on each leaf's outer face was vertex colour across a coarse grid and blurred
  into the black, so each wing read as one plain red plank. The outer face is now black with a raised, hard-edged red
  panel on it, and the red inner face (the one the battle camera sees on his near side) carries a black one.

**Rig.** Two unweighted anchors were added last, so every other bone keeps its index: `vfx_core` (the breastplate's
split, y 1.76, z 0.20, on `spine_2`) and `vfx_keepsake` (the copper ring, on `finger_l1`, so it rides the hand in
`stop` and `release`).

**Every clip is played from idle's first frame.** The clips are authored from rest and offset by idle's first pose
(`ck.in_pose`), so each one starts where the idle starts, and the one-shots that return end there too. `rise` starts
kneeling (it is the call). `victory` ends with the wings open and held still, as the sheet says; `ko` and `dismiss`
end kneeling, and `release` away from the party.

**New clips.**
| Clip | Length | Contact | What it shows |
|---|---|---|---|
| `stop` | 1.6 s | 0.9 s | Hold the Hour: his left hand, the ringed one, comes up and out to breast height, palm toward the foe (0.45 s), and is held perfectly still (0.45–0.7 s); then the fingers close, slowly, as if on the hour itself. Nothing else of him moves: the head, the wings and the other hand stay at rest |
| `ward` | 1.6 s | 0.8 s | The lacquer screen: the hands draw in to his breast and the wings part (0.3 s); the four leaves swing out and forward round the party's side, curving in front of him like a folding screen set down (0.6 s), and at the contact his arms open wide, palms out, holding it; held to 1.15 s, then the wings fold back |

**Lowest vertex over every clip:** 0.008 m (`hit_b`'s tip back); the new clips stay at 0.096 m or higher. Nothing goes
under the water.

**The clip map for combat** (M4-A2P-024 pastes it into `ethren` in creatures.json once the skills are in skills.json;
the validator rejects unknown skill ids before that; the ids are the design sheet's proposals):

```json
"clip_by_skill": {"level_hand": "cast", "hold_the_hour": "stop", "lacquer_screen": "ward", "still_water": "special"}
```

The basic attack plays `attack` by kind. Contacts, already in creatures.json (`ethren` and `ethren_held`): attack
0.55, cast 0.8, stop 0.9, ward 0.8, special 1.45. Every wind-up is ≥ 0.45 s.

**Tests:** tests/unit/test_creature_vowbound_act2.gd (`test_ethren_...`) checks the clip set on both forms, the
wind-ups, that the anchors are unweighted and placed (the keepsake on the ring's finger), that every clip runs from
idle's first frame, Hold the Hour's still, held-out hand closing at the contact with nothing else moving, and the
screen swinging forward round the party's side.

**Portraits** `ethren` and `ethren_held` are re-baked (the crown, the lit bowl, the robe's bands and the wing panels
show). **Open:** from the party side of the battle camera the veil is seen edge-on, so its face shading reads only
from the front (the summon shot, cinematics). The screen's near leaf swings toward the battle camera in `ward` and
crosses his robe for 0.3 s; it reads as the screen going up round the party, but battle-presentation may prefer to
frame it. Hold the Hour's closing hand is small at battle distance: the foe's freeze (VFX) carries the read.

## As built: the polish (M4-CRB-008, 2026-10-30, after the Lead's view)

The Lead's track viewed `creature_ethren` after the final pass and he still read as primitive (ADR 0041 §3): the robe was
three cones stacked like lampshades, the arms mannequin cylinders on ball joints, the halo a flat plate, and the wings
doors. This pass rebuilds those surfaces. The rig (29 bones, the same indices), every clip and its name, the contacts,
the anchors, the veil (its own mesh on its own unkeyed bone, for Act III's veil-fall) and the palette are kept. The
cuirass, the breastplate, the collar, the head, the crown cap and the veil are as they were.

**Budget:** 17,304 triangles (the Act I Vowbound bar is 18k; he was at 15,546), 29 bones, 16 clips. Per slot:
`lacquer` 4,800, `lacquer_red` 2,992, `gold` 3,384, `silk` 3,690, `seam` 734, `halo` 480, `veil` 1,008, `ring` 216.

**One slot added: `silk`** (materials.json, write_materials; PROVENANCE rows for `materials/silk.tres` and
`materials_held/silk.tres`). The cloth needed a sheen the glossy lacquer cannot give: roughness 0.55, `rim_sheen` 0.45,
cavity 0.45/0.8 so the folds' creases darken. Its colours are palette swatches: `lacquer_red_deep` and an oxblood black
(`lacquer_black` 30% toward `lacquer_red_deep`, so the sheen shows). It is not emissive, so the held set copies it.

- **The robe is layered cloth.** A red silk under-robe hangs from under the belt in sixteen folds (round crests, sharp
  creases, drifting a little and varying in depth round him, 3.4 cm deep at the hem); its hem is uneven (the folds,
  and 1.2 cm longer behind), rolled (a 4 mm lip) and banded in black silk with a thin gold edge. Over it are three
  lacquered panels with eleven stiffer folds: two in front, parted from the belt (the opening widens from 5° to 26°
  each side, so the red silk shows), and one behind, longer (hem 0.20 m behind, 0.28 m at the sides, 0.34 m in
  front), which the front pair overlaps at his sides from 98° to 118°. Each panel is rimmed in gold down both edges and
  along its hem; the rims are cut from the folded surface, so they follow the folds. The panels are lined in red silk
  (the lining is kept only where it can be seen, at the hems). A red lacquer belt with gold edges closes the top, with
  a knot at the left hip and two red silk tails hanging over the front panel, turning as they fall, tipped in gold.
- **Kneeling.** The cloth is skinned by height (`body` above 1.22 m, blended to `robe_1` by 0.80 m, `robe_2` by
  0.34 m). The hips sink furthest, so the robe settles onto itself as the bells used to telescope; nothing stretches,
  and the hem stays above the water.
- **A mantle over the shoulders.** Two layers of lacquered cloth (red over a longer black one), fourteen folds, gold
  hems and gold front edges, parted at the breast (±50°, clear of the veil and showing the breastplate and its seam of
  light). It covers the shoulders and the sleeves' tops, so no joint shows; its sides go 40% with the upper arms. The
  pauldrons are gone.
- **Sleeves, not cylinders.** Each sleeve is close at the shoulder (under the mantle), widens down the arm, and under
  the forearm hangs in a deep bag (22 cm) that is sewn shut in front and rounds up to the opening round the wrist,
  as a hanging sleeve is. Six soft folds round it. Black silk outside, red silk inside; the opening is turned back in
  a red band and edged in gold, 3 cm past the wrist, so only the hand shows, and the bound light glows deep in the
  cuff. Skinned positionally: the upper sleeve on the upper arm (its top 35% on the chest), the forearm and the bag
  on the forearm, blended across the elbow.
- **Hands, not tongs.** Each hand (1.2 times a man's, for his 3 m) is a palm lofted from inside the cuff to the
  knuckles, four three-jointed fingers in a relaxed curl, each joint a little proud (the knuckles' read), a two-jointed
  thumb, and a gilded nail on every finger. The left hand's index and middle ride `finger_l0` and its ring and little
  fingers `finger_l1`, as before; the copper ring sits on the ring finger 1.7 cm past the knuckle, and `vfx_keepsake`
  is placed there (it is computed from the finger, so the anchor and the ring agree).
- **The halo is light.** A thin bowl (6 mm) floating clear of the head (its lip 0.12 m behind the back of the head,
  its hollow's edge 0.23 m), open at its centre (a 0.26 m hollow, the crown shows through it). Its lit face
  is brightest at the hollow's edge (emission 1.0) and falls off to 0.1 toward the rim, its colour going from the
  light toward the black lacquer, so it reads as a glow, not a painted ring. Then a red lacquer rim and the gold lip;
  the back is black lacquer.
- **Screens, not doors.** Each wing leaf is now two half-panels hinged down its middle and set at a shallow V (the
  middle stands 3.5 cm out), like a folding screen: one half catches the light and the other does not, so the screen
  reads at battle distance. Each half is rimmed in gold on its outer edges (none down the hinge), 1.2 cm thick (from
  3). The outer faces are black lacquer worn at the edges to the red ground under it (noise-broken, the lacquer's own
  wear), with a red field set in each half; the inner faces (the ones the battle camera sees on his near side) are
  red, with two darker red fields in each half above and below a rail, their borders sunk. The bound light runs in the
  hinge line between the halves and between the upper and lower leaves, which are joined by two lacquer knuckles each;
  a knuckle hangs each leaf from the yoke.
- **Grounding.** Lowest vertex over every clip, skinned: 0.006 m (`hit_b`, the lower leaves' outer corners as he
  tips back; the hit's leaf lift is 3° from 2° so they clear the water as before); everything else 0.017 m or
  higher. Nothing goes under the water.
- **Gold, measured roughly from the renders** (gold-hued pixels): 0.2% of the battle frame at rest (as before the
  pass) and about 1% in a frontal full-figure shot at 5 m: far inside palette.json's 5%. The palette tool should
  confirm on the next PC render.

**Viewed** (a scratch clip sheet: every clip at five beats from the battle camera on the party's `vowbound_slot` in an
Act I arena, and close-ups of the front, side, back, hands, head and halo, robe, wings, the kneel, `ward` and
`victory`): at battle distance he is a robed, veiled figure with a lit halo and lacquer screens, and every clip reads as
before (`stop`'s held hand, `ward`'s screen round the party's side). Up close the cloth has folds, the sleeves hang and
are lined, the hands have fingers, knuckles and nails, the halo glows from its hollow, and the screens have hinges,
fields and worn edges.

**Portraits** `ethren` and `ethren_held` are re-baked.
