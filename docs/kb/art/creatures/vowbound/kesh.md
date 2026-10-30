# Kesh, the First Voice (`kesh`), Asha's Vowbound of all six elements: art sheet (built, M4-A2P-057)

**Who:** the seventh Vowbound bound and the first Cantor (docs/kb/story/vowbound.md §7): **Kesh Aurane**, a
Lamplighter and Sefir's wife. She sang herself in a thousand years ago and was displaced forty years later. Sefir
couldn't let her lift, so he bound her in the Choir's stones himself, and that night the Abiding began. She has been
awake in stone ever since, and she hid the Eighth Verse's melody there. She is bound at the Drowned Choir (Ch16 C4),
in a memory sequence. **Kind:** a Vowbound, bound light. **Role:** an ally from Act III. She cycles all six elements in
turn, and her Swell is *The Seven*. **Status:** built (M4-A2P-057). She has no row in game/data/battle/vowbound.json
yet, so her creatures.json row carries `vowbound_pending` (combat's M4-A2P-024/025). The build follows Nhoa's
pipeline (nhoa.md, M4-CRB-006). The design target is
[docs/kb/plan/act2/bosses/kesh.md](../../../plan/act2/bosses/kesh.md), and ADR 0204 §7 fixes her battle scale and the
element order.

**The idea:** a woman made of standing seawater, from the hips up, rising out of a column of water, dressed:
- a fitted bodice of the robe's deeper water to her collarbones, bound at the neckline with a cord of Choir-stone
  beads;
- a Cantor's stole over her shoulders;
- below the girdle, a long robe of four panels set with carved stone mouths in flowing bands, each on its own worn
  plaque, open as the Choir's singers' are, with a little of her light inside.

Her head is bare. Her hair is a dark fall of water from the hairline back over the crown and down her back, breaking
white at the ends. Her left palm rests over her heart, whose light shows under her hand. A Lamplighter's lamp-key
hangs at her hip from a girdle of Choir stone: the keepsake, the one object on her, never lit.

She reads as **patient, enormous and very tired**: a person, the oldest in the game, never a goddess or a monster.
So:
- nothing glows in her eyes, which are closed under heavy lids;
- her face is a woman's, calm and grieving;
- she stands still, and the water moves.

Original design (README rule 1). It starts from four things:
- standing water held in a shape;
- a singer's open mouth carved in stone (the Choir's own colossal singers);
- a cantor's stole;
- a lamplighter's long key with a flame cut through its bow.

There is no crown, no armour, no weapon, and no wings.

**IP and story guard.** She is no water spirit from any other series and no echo of any summoned water maiden:
- she is not a mermaid, has no tail, and doesn't sit in a shell or a pitcher;
- she doesn't pour from an urn;
- her finisher is named for the verses, not for any series' ultimate;
- her element cycling is always telegraphed and never reacts to being struck.

**ADR 0015** (no ice from Ch12 to Ch15) doesn't bind Ch16, but Ice stays one element among six on her: her Ice voice
is stillness and a cold haze (VFX). Nothing on her freezes, and there are no crystals, no frost, no glacier.

## Silhouette and size

| | |
|---|---|
| Height | **4.2 m** in battle (ADR 0204 §7): the crown of her head at 4.1 m, the hips (the girdle) at 1.88 m. In the bind memory she rises colossal from the Choir's sunken bowl, matched to the ten 24 m singers: a cinematic scale of the same rig (cinematics and rendering scale the node, not the model) |
| The one shape | **A dressed woman from the hips up on a column of water**: a long narrow bell (the robe and column) under a slim, slightly leaning torso, one hand at her heart, the other low and loose, the head tilted. At the battle camera's 13 m she reads as one tall figure: luminous water at the face, neck and arms, a dark gown below set with a pale stone pattern |
| The column | 1.4 m across where it meets the water (y 0.004, a foam lip), narrowing to 0.74 m at the girdle, with slow running folds round it. It is her lower body: there are no legs |
| Head | bare, 0.53 m crown to chin. A woman's face, calm and grieving: a brow ridge whose inner ends lift a little, the eyes closed under heavy lids (the lid line and crease cut in), a straight nose with a bridge, wings and tip, high cheekbones, full lips closed with the corners a little down, a rounded chin. The head's grid crowds its rows and columns onto the face for this |
| Hair | dark water: one sheet of side-by-side strands from the hairline (framing the face over the temples and ears), back over the crown and down her back to the girdle, ragged at the ends where it breaks white, with three loose strands from behind the crown. No light in it, so her face is the brightest part of her head |
| The bodice | fitted, of the robe's deepest water (its own satin `robe` slot, so it doesn't mirror the sky as her glassy skin does), from under the girdle to her collarbones, cut down to the armholes at the sides, softly gathered under the bust. A cord of pale Choir-stone beads binds the neckline and armholes: the line between garment and skin |
| The stole | a Cantor's stole: two strips over her shoulders, from under the hair at her back down her front to the girdle, darker still, with pale edges and white-breaking ends, a small carved mouth on a plaque at each end |
| Hands | the left palm flat over her heart, the fingers soft; the right low and loose, a little forward |
| The robe | four panels of the same deep water hanging from the girdle (front, back and the two sides), flaring toward a hem 0.17–0.22 m over the water that breaks white, with slits between them where the column shows |
| The mouths | 46 (44 on the panels in flowing vertical bands, two on the stole). Each is a worn, irregular plaque of Choir stone 0.22–0.32 m tall (larger toward the hem), tilted with the band's lean. A singer's open mouth is carved in it: some round "o", some wider "ah", the lower lip fuller, the upper with a soft dip, the corners pinched, a little crooked, the lips pale and worn, the opening dark and lit faintly from within. They follow two bands on the front and sides and three on the back, each meandering down the drape |
| The girdle | a strand of 24 worn Choir-stone beads at the hips, where the column becomes her and the bodice meets the robe |
| The lamp-key | 0.7 m including its hanger, on her left hip (the camera's side; her +x faces the party's camera from the Vowbound slot), in the robe's front-left slit: a ring and cord from the girdle, a round bow with a flame cut through it, a collar, the shaft and a stepped bit with two wards |
| Facing | `stand_in.yaw_deg` −90, toward the foes. Her idle turns her shoulders 14° and her head 22° more (neck 7°, head 15°) toward the camera and tilts it 11°, so her face is three-quarters to it |

## How she is made of water (no particles, no transparency)

The creature shader is opaque, and the bound-light rule (color_script.md rule 2: steady, nothing drifts by itself)
holds. So the water is **geometry skinned to her bones**, as Nhoa's motes are, and it reads as water through these:
- **Gloss and rim.** Her skin is glassy (clearcoat 0.8, roughness 0.08) with a strong fresnel rim (`rim_sheen` 0.85):
  a dense, darker core and edges that catch the light.
- **Ripples.** A coarse detail bump (scale 3.5, 1.4) breaks every highlight.
- **Flow.** Streaming bands meander down her in the vertex colour (nine sinuous bands round her, toward
  `turquoise_shallow`), with running streaks over them.
- **Runnels.** Ten raised streams of water are laid on the surface:
  - three over each shoulder and down the arm, spiralling a little;
  - four down the bodice from the neckline.

  They are paler than the body and lit a little more (mask 0.16), and they break white at their tails.
- **White breaking.** Foam shows where water thins or ends: at the fingertips, the hair's ends, the robe's hem, the
  stole's ends and the column's foot.
- **Depth.** She is deeper toward the column's foot (`deep_teal_shadow`) and paler at the thin edges.
- **Her own light.** She holds a faint light everywhere (mask 0.06 × 1.6; 0.1 on the face), and the heart's light
  shows through the bodice as a soft pool under her hand (the `inner` slot, up to 0.6 × 1.6).
- **Clips.** Running water is shown by motion: the hair's and the robe's chains sway, lagging down them. The splash
  where the column meets the water is battle VFX.

## Colour (palette.json swatches, by name)

| Slot | Albedo | Light |
|---|---|---|
| `water` (her skin: the column, arms, hands, neck, head; the runnels) | the `pale_rim` water's deep `#5E8C90` over `deep_teal_shadow` `#0E4A55` (deeper toward the foot), streaming bands and streaks toward `turquoise_shallow` `#3FD0C9`, paler at the thin edges, `foam_white` `#EEF6F4` at the foot and the fingertips | `glimmer_bound` `#4FB3B0` at 1.6, mask 0.06 (the face 0.1, the runnels 0.16) |
| `robe` (the bodice, the stole, the four panels): satin water, matte beside her skin | the same water leaning 0.55–0.7 to `deep_teal_shadow` and 0.25–0.3 to `abyss_navy` `#061A2B`; the gathers' crests and the stole's edges paler (`#5E8C90`, `salt_glass` `#BFE6E0`); `foam_white` at the hem | `glimmer_bound` at 1.6, mask 0.04 |
| `inner` (the heart's pool on the bodice: the triangles whose pool passes 0.3) | the bodice's water | `glimmer_bound` at 1.6, mask up to 0.6 at the heart: the "Kesh pale cyan" of `lut_ch16_choir` |
| `hair` | `deep_teal_shadow` to `#5E8C90` strand by strand, `turquoise_shallow` down the fall, `foam_white` at the ends | none |
| `mouths` (the plaques and their mouths, the girdle, the neckline's cord) | `cold_blue_stone` `#5E6E80` darkened toward `deep_teal_shadow`, worn toward `salt_glass` on the lips and on the cord's beads; `abyss_navy` in the opening | `glimmer_bound` at 1.0: mask 0.4 at each opening's floor, 0.24 in the throat, 0.1 on the inner lip; 0 on the stone |
| `key` | `brass` `#B08D57` going to `bronze_patina` `#5F8A78` in its hollows | **none** (energy 0): it is an object |

Her light is `glimmer_bound` because she is bound, as an ally. The Choir art sheet calls her pale cyan in the bind
(`glimmer_held`, pale_rim.md §0). That colour is the memory sequence's grade, not a material swap. Act III's held
form (the fight before Sefir) gets a `held` block like the other six's, with Act III.

## The element shift: how each element reads on her

Combat telegraphs her next element on the timeline (M4-A2P-025, pillar 4). The body adds three reads:

1. **The shift itself** (`kesh_shift`, her free action at the start of a turn). The whole body goes still, then the
   robe's mouths turn outward in a ripple from the waist down: each panel segment swings out in turn, 0.12 s apart.
2. **An accent per element.** Each `shift_<element>` clip adds a small promise of that voice's wind-up during the
   stillness:

   | Element | Accent during the stillness |
   |---|---|
   | Water | the hands lift, palms up |
   | Lightning | the hair lifts off her back |
   | Fire | the hands are drawn together, cupped |
   | Ice | complete stillness: nothing moves, not even the hair, and the ripple comes late and slow |
   | Holy | the head lifts and the hands turn up; the ripple is bigger |
   | Glimmer | the chest opens and the shoulders go back |

   The plain `shift` stays for any element combat doesn't map.
3. **Each voice's wind-up has its own silhouette**, readable at 13 m (the clip table below): a bow, an arm overhead with
   the hair standing, cupped hands, a dead stillness, a bell of open mouths, an opened chest.

**Colour is VFX's (open item for battle-presentation).** The element colours are effects.json's. They go on top of her
own steady light: a light or glow at `vfx_core` in the coming element's colour from the shift until the voice lands,
plus the voice's own VFX. Her material never changes: bound light stays `glimmer_bound`, steady.

## Rig (39 bones)

- `root` at the water. No clip moves it, so the column's foot ring, skinned to it, never leaves the water.
- `column_0..2`: the standing water. It sways as one, and it shortens or grows by moving `column_1` and `column_2`
  along y (the rise, the KO, The Seven).
- `spine_0..2` (the girdle to the shoulders), `neck`, `head`. `spine_0` moves along y to sink her into the column.
- Per arm: `clav`, `upper`, `fore`, `hand`. `+x` is `l`.
- `hair_l0..2` and `hair_r0..2`, from the head. The hair sheet is blended across them by side.
- `robe_f0..2`, `robe_l0..2`, `robe_r0..2`, `robe_b0..2`: the four panels, from the girdle on `column_2`. The
  mouths ride them.
- `key_0`, `key_1`: the hanger and the key, from the girdle.
- **Anchors (unweighted, added last):** `vfx_core` (the heart, y 2.8, on `spine_1`) and `vfx_keepsake` (the key's
  bow, on `key_1`).

The skinning is two bones per vertex, as the kit requires:
- the body, column and neck go up one axis chain, with the foot held by `root` and the shoulder caps blended toward
  `clav`;
- each robe panel and each mouth follows its own chain;
- the head and the key are rigid.

## Clips (contact seconds are in creatures.json `contact`)

Every clip is keyed from idle's first frame (the build's `BASE`): a bone a key doesn't name holds its idle pose, so
each clip starts where the idle starts, and the one-shots end there. The exceptions are rise (it starts folded, as the
call), and ko and dismiss (they end sunk). A key that names a bone sets it outright, so an action's arms aren't skewed
by the idle's hand at her heart. The hits and `idle_b` are added on top of the idle pose instead, so she keeps her
stance through them.

| Clip | Length | Wind-up → contact | What the water does |
|---|---|---|---|
| `idle` | 4.0 s, loop | — | she stands with her left palm over her heart and the right hand low and loose, her weight a little to one side (the column leans, the spine answers), her head tilted and turned three-quarters to the camera, eyes closed. The column sways as one, the hair sheet falls and falls (its chains sway, lagging down them), the robe stirs, she breathes |
| `idle_b` | 1.6 s | — | a breath with her eyes closed: the head bows a little and the chest rises, held, then lets go |
| `ready` | 1.4 s | — | the panels swing out (the mouths open wider) and the hands lift |
| `rise` | 3.0 s | — | from folded and sunk (shoulders at about 2 m, the column 0.35 m short, the robe pooled outward) the column climbs, then her body, and her head lifts last |
| `dismiss` | 1.2 s | — | she pours back down into the column, ending folded (the splash and fade are presentation) |
| `attack` | 1.2 s | 0.32 s drawn back → **0.55 s** | the fallback strike: the near hand swept out at the foes |
| `cast` | 1.6 s | 0.45 s drawn up → **0.8 s** | the fallback cast: both hands drawn up, then opened forward |
| `hit`, `hit_b` | 0.5 s | peak 0.1 s | the water shudders through her: the column ripples one way and the chest the other, the hair and the robe flung (`hit_b` rolls to the other side) |
| `defend` | 1.2 s | — | the robe wraps forward (the mouths turned in), the arms fold before her, the head bows |
| `ko` | 2.2 s | — | she sinks into the column to the shoulders (1.15 m, the column 0.3 m short), head bowed, the robe pooled out |
| `victory` | 2.2 s | — | she straightens and looks up |
| `shift` + six `shift_<element>` | 0.9 s | — | still, then the ripple (above) |
| `voice_water` | 1.8 s | 0.0–0.75 s she bows and draws the water up into her arms → **0.9 s** | a wave poured forward from both hands |
| `voice_lightning` | 1.4 s | 0.0–0.6 s her hair lifts and stands, the near hand goes up over her head → **0.7 s** | one sharp downward cut of the hand |
| `voice_fire` | 1.6 s | 0.0–0.68 s the hands cupped close before her (the water boils: VFX) → **0.8 s**, then 1.05 s and 1.3 s | three quick casts, left, right, left |
| `voice_ice` | 1.6 s | 0.0–0.8 s **completely still** from 0.25 s (a cold haze: VFX; nothing freezes) → **0.9 s** | the hands open slowly downward |
| `voice_holy` | 1.6 s | 0.0–0.7 s the robe bells out, every mouth open (the light inside them: VFX) → **0.8 s** | a lift of both arms |
| `voice_glimmer` | 1.8 s | 0.0–0.8 s she opens her chest (the heart's light through it: VFX at `vfx_core`) → **0.9 s** | both palms pressed flat toward the foes, held |
| `special` (The Seven) | 3.0 s | 0.0–1.8 s she rises **1 m** on the column, every mouth open, arms wide → **1.8 s** | arms sweep forward and up (all six at once, then the seventh note held to 2.35 s); she settles |

Act III's held form needs a `release` clip, in which the key is the last thing to fade. It waits for Act III, as the
sheet says.

## The clip map for combat

M4-A2P-024/025 paste this into `kesh` in creatures.json once the skill ids are in skills.json. validate_creatures
rejects unknown ids before that. The ids are the design sheet's proposals, and combat owns them:

```json
"clip_by_skill": {
  "kesh_shift": "shift",
  "voice_water": "voice_water", "voice_lightning": "voice_lightning", "voice_fire": "voice_fire",
  "voice_ice": "voice_ice", "voice_holy": "voice_holy", "voice_glimmer": "voice_glimmer",
  "the_seven": "special"
}
```

The shift's element accent is the presentation's choice per turn: play `shift_<element>` (for example `shift_fire`)
for the element the timeline shows next. Any unmapped skill falls back to `attack` or `cast` by kind. The contacts
are already in creatures.json:

| Clip | Contact (s) |
|---|---|
| `attack` | 0.55 |
| `cast` | 0.8 |
| `special` | 1.8 |
| `voice_water` | 0.9 |
| `voice_lightning` | 0.7 |
| `voice_fire` | 0.8 |
| `voice_ice` | 0.9 |
| `voice_holy` | 0.8 |
| `voice_glimmer` | 0.9 |

`voice_fire`'s second and third hits land at 1.05 s and 1.3 s (for the multi-hit VFX). Every wind-up is at least
0.55 s, over the 0.45 s floor.

## Budget

19,366 triangles, 10,700 vertices, 39 bones, 6 slots, GLB 3.2 MB (26 clips). That is over the ~18k guide by 1.4k,
within the ~20k the second pass allowed. The extra pays for three things:
- the garment (bodice, cord and stole, 1,840);
- the runnels (1,060);
- a face crowded with rows and columns (2,400).

The mouths came down from 88 to 46, on plaques. The parts:

| Part | Triangles |
|---|---|
| plaques and their mouths (46 at 110) | 5,060 |
| head | 2,400 |
| body and column, less what the bodice covers (`water`) | 2,426 |
| robe panels (both faces) | 1,904 |
| hair (sheet, both faces, and three strands) | 1,622 |
| runnels | 1,060 |
| bodice (`robe` and `inner`) | 1,008 |
| hands | 976 |
| arms | 920 |
| key | 774 |
| the neckline's cord | 432 |
| stole | 400 |
| girdle | 384 |

## As built (M4-A2P-057, 2026-10-30)

`assets_src/creatures/kesh/build_kesh.py` (`--report` prints the numbers) builds `assets/creatures/kesh/kesh.glb`, and
`materials.json` gives the six slots through write_materials.py. The Blender job is `creature_kesh`, and the build
is byte-identical across runs (verify_blender_builds, run twice). The scene is `game/creatures/kesh/kesh_battle.tscn`
and the review shot `creature_kesh` (`pending_baseline` until the Lead approves it). Her portrait is
`assets/ui/portraits/creatures/kesh.png`.

**Grounding.** The lowest vertex is +0.004 m (the column's foot ring) in every frame of every clip. The ring is
skinned to `root`, so nothing goes under the water, the KO included.

**Framing** (the default battle camera, her on the party's `vowbound_slot`, measured on every frame against the 0.1
HUD-safe top):

| Moment | Screen measure |
|---|---|
| At rest | top v 0.211, x 0.60–0.69 of the width |
| The Seven at its contact (risen 1 m) | top v 0.113, the tightest frame, inside the line |
| `voice_lightning`'s raised hand | top v 0.138 |
| `voice_holy`'s lifted arms | top v 0.154 |
| Widest | x 0.55–0.74, clear of the 0.15 right margin |
| Foot | v 0.565 |

So the column didn't have to shorten, and The Seven keeps the sheet's full 1 m.

**What was judged, and fixed, from the renders** (the battle camera in an Act I arena with a scratch fixture, and
close-ups):
- **The face.** The first face read as a mask with lit eye sockets, so the eyes no longer take any light. The sockets
  now hold heavy lids, and the head is shorter and rounder with a clearer brow, nose and lips.
- **The hair.** The hair started as thin strips that read as plastic ribbons, with points sticking up at the crown.
  It is now one continuous sheet with five loose strands, starting inside the head's hair cap.
- **The robe.** A first stole over the shoulders read as braces and was cut. The mouths read as washers, then
  donuts: their hollow sank behind the robe's surface, and the stone came out darker than the lit water. They are now
  pale worn-stone lips, the lower lip fuller and the corners pinched, round an opening lit from within, scattered
  rather than in rows. The flared panels read as stiff boards, so their swing now grows toward the hem.
- **The key.** It was half inside the front panel and now hangs clear of it.
- **The silhouette.** The shoulders and arms have more weight. The idle turns her chest 14° toward the camera, so
  two-handed gestures don't overlap from the battle camera, which sees her left side.
- **The bodice.** The robe's deeper water is carried up her body as a bodice to a scooped neckline (colour only). In
  a dark arena the heart's light fills her chest through it.

**Changes from the design sheet:**
- **`shift_<element>` (six clips) were added** to the sheet's single `shift`, so the element reads on her body
  (above).
- **`idle_b` closes her eyes by bowing her head for a breath.** There are no eyelid bones; the face is too small at
  battle distance to need them.
- **46 mouths on plaques, not "a hundred".** At battle distance fewer, larger, better-shaped mouths in bands read as a robe of mouths; many small ones read as polka dots (the second pass).
- **The rig has 39 bones, not about 34.** The proposal didn't count the clavicles, the hands or the anchors.

**Open items:**
- **Combat** (M4-A2P-024/025):
  - her vowbound.json row and the skills (`kesh_shift`, the six `voice_*`, `the_seven`);
  - then the clip map above pasted into creatures.json, and `vowbound_pending` dropped;
  - the element cycle and its timeline telegraph.
- **Battle-presentation:**
  - the element colour at `vfx_core` from the shift until the voice lands;
  - which `shift_<element>` to play;
  - `voice_fire`'s three hit times;
  - the splash at the column's foot on `rise` and `dismiss` (the clip ends folded but not gone);
  - The Seven's six-then-seven VFX.
- **Cinematics and rendering:** the bind memory scales this rig colossal in the Choir's bowl (pale cyan by
  `lut_ch16_choir`). Living Kesh (the Lamplighter, the same lamp-key) and the young Sefir belong to the characters
  track.
- **Act III:** the held form (a `held` block in materials.json, `kesh_held`), and the `release` clip in which the key
  fades last.
- **Up close:** the face is a calm, grieving woman's face at the size the battle and portrait cameras see it. A
  cinematic close-up of her (the bind memory) wants a sculpted head of its own.

## As built: the second pass (M4-A2P-057, 2026-10-30)

The coordinator viewed `creature_kesh` and found a smooth teal mannequin. The notes were:
- water, not plastic;
- she reads as bare;
- the face is blank;
- the mouths read as polka-dot washers;
- the idle is a mannequin with its arms down.

All were addressed and judged on the review shot, a battle-camera clip sheet and close-ups.

- **A missed step, found and fixed.** `game/data/import/creatures.json` didn't list `assets/creatures/kesh/`.
  Materials bind by slot name either way (checked in Godot: every surface wears its `.tres`), but the list now has
  her for the import rules' bookkeeping.
- **Water.** The changes:
  - the skin is darker and denser, with a stronger fresnel rim;
  - sinuous streaming bands meander down her in the vertex colour;
  - ten runnels are raised streams of water down the shoulders, the arms and the bodice;
  - white breaks at the fingertips, the hair's ends, the hem, the stole's ends and the column's foot.
- **A garment.** She now wears a fitted bodice and a stole:
  - **Its own slot.** The bodice is real geometry, 1.6 cm off her body from under the girdle to the collarbones, cut
    to the armholes and gathered under the bust. It is in its own satin `robe` slot, so it doesn't mirror the sky as
    her glassy skin does.
  - **Its edge.** A cord of pale Choir-stone beads binds the neckline and armholes: the legible line between
    garment and skin.
  - **The stole.** It runs over her shoulders and down her front, with pale edges, white-breaking ends and a carved
    mouth at each end.
  - **The robe.** The panels moved to the `robe` slot too.
  - **What made her look bare.** The heart's light had covered the whole chest in the skin's own colour. It is now a
    soft pool under her hand (radius 0.18 m, mask 0.6).
- **The face.** The head's grid crowds 30 rings and 40 columns onto the face, with features carved in:
  - the lids closed, with the lid line and crease cut in;
  - the brow ridge, its inner ends raised (grief);
  - the bridge, wings and tip of the nose;
  - the cheekbones and the hollows under them;
  - the philtrum, full lips closed with the corners a little down, and the chin.

  The hair sheet now starts at the hairline, framing the face over the temples and ears, strand by strand, and holds
  no light. The face holds a little, so it is the brightest part of her head.
- **The mouths.** 46 worn, irregular Choir-stone plaques, each carved with a singer's open mouth: lipped and
  asymmetric, "o" or "ah", the opening dark with a faint glow. They follow flowing vertical bands that meander down
  the drape (two on the front and sides, three on the back), tilted with the band's lean, larger toward the hem.
- **Pose.** The idle has life now:
  - her left palm is over her heart, the fingers soft (the arm angles solved for the palm to lie flat on the bodice);
  - the right hand is low and loose;
  - her weight leans a little to one side;
  - her head is tilted 11° and turned three-quarters to the camera;
  - the hair sheet sways more.

  The clips are keyed from the idle's base. An action's keys set its arms outright, so no clip inherits the hand at
  her heart as an offset, and the hits and `idle_b` add to her stance.
- **Kept.** These are unchanged:
  - the 4.2 m height and the clip names;
  - the contacts, the wind-ups and the anchors;
  - the clip map.

  The re-measured numbers:
  - **Grounding:** the lowest vertex is +0.004 m in every clip.
  - **Framing** (the default battle camera, against the 0.1 top line):

    | Moment | Screen measure |
    |---|---|
    | At rest | top v 0.211 |
    | The Seven, the tightest frame | top v 0.117 |
    | `voice_lightning` | top v 0.146 |
    | Widest | x 0.554–0.754 |
