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

**The idea:** a woman made of standing seawater, from the hips up, rising out of a column of water. Her robe is a long
fall of darker water set with a hundred small carved stone mouths, open as the Choir's singers' are, each with a little
of her light inside. Her head is bare, and her hair is water falling down her back, breaking white at the ends. Her
hands are open. The bound heart shows through her chest, a soft light deep in the water. A Lamplighter's lamp-key
hangs at her hip from a girdle of Choir stone: the keepsake, the one object on her, never lit.

She reads as **patient, enormous and very tired**: a person, the oldest in the game, never a goddess or a monster.
So:
- nothing glows in her eyes;
- her face is a woman's, the eyes lowered under heavy lids;
- she stands still, and the water moves.

Original design (README rule 1). It starts from three things: standing water held in a shape, a singer's open mouth
carved in stone (the Choir's own colossal singers), and a lamplighter's long key with a flame cut through its bow.
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
| Height | **4.2 m** in battle (ADR 0204 §7): the crown of her head at 4.12 m, the hips (the girdle) at 1.88 m. In the bind memory she rises colossal from the Choir's sunken bowl, matched to the ten 24 m singers: a cinematic scale of the same rig (cinematics and rendering scale the node, not the model) |
| The one shape | **A woman from the hips up on a column of water**: a long narrow bell (the robe and column) under a slim upright torso, open hands held a little out from her sides, the hair a dark fall down her back. At the battle camera's 13 m it reads as one tall glowing figure in a long robe, the brightest thing on her side of the field |
| The column | 1.4 m across where it meets the water (y 0.004, a foam lip), narrowing to 0.74 m at the girdle, with slow running folds round it. It is her lower body: there are no legs |
| Head | bare, 0.53 m crown to chin. A woman's face: a straight nose, a heavy brow, the eyes lowered under heavy lids, closed lips |
| Hair | water falling: one continuous sheet from the crown over the sides of her head (it frames the face), behind the shoulders and down her back to the girdle, ragged at the ends where it breaks white, with five loose strands over it |
| Hands | open, the palms toward the front: offering, not threatening |
| The robe | four panels of deeper water hanging from the girdle (front, back and the two sides), flaring toward a hem 0.17–0.22 m over the water, with slits between them where the column shows. Every mouth is set in them |
| The mouths | 88 (the design's "a hundred"), 0.10–0.18 m: a singer's open mouth, the corners pinched, the lower lip fuller, pale worn stone swelling out of the water round a dark opening lit from within. They are scattered (no rows, no grid), larger toward the hem |
| The girdle | a strand of 24 worn Choir-stone beads at the hips, where the column becomes her |
| The lamp-key | 0.7 m including its hanger, on her left hip (the camera's side; her +x faces the party's camera from the Vowbound slot), in the robe's front-left slit: a ring and cord from the girdle, a round bow with a flame cut through it, a collar, the shaft and a stepped bit with two wards |
| Facing | `stand_in.yaw_deg` −90, toward the foes. Her idle turns her shoulders 14° and her head 22° more (neck 7°, head 15°) toward the camera, so her face is three-quarters to it |

## How she is made of water (no particles, no transparency)

The creature shader is opaque, and the bound-light rule (color_script.md rule 2: steady, nothing drifts by itself)
holds. So the water is **geometry skinned to her bones**, as Nhoa's motes are, and it reads as water through these:
- **Gloss.** She is wet all over (clearcoat 1.0, roughness 0.06) with a fresnel rim (`rim_sheen` 0.55), so her edges
  catch the light the way standing water does.
- **Ripples.** A coarse detail bump (scale 3.5, 1.2) breaks every highlight.
- **Running streaks.** Vertical streaks in the vertex colour toward `turquoise_shallow` read as water running down
  her.
- **Depth.** She is deeper toward the column's foot (`deep_teal_shadow`) and paler at the thin edges (the hands, the
  hair, the robe's edges). A foam lip sits where the column meets the sea.
- **Her own light.** She holds a faint light everywhere (mask 0.06 × 1.6), and the heart's light shows through the
  chest (the `inner` slot, up to 1.0 × 1.6), steady.
- **Clips.** Running water is shown by motion: the hair's and the robe's chains sway, lagging down them. The splash
  where the column meets the water is battle VFX.

## Colour (palette.json swatches, by name)

| Slot | Albedo | Light |
|---|---|---|
| `water` (body, column, arms, hands, head, the robe's panels) | the `pale_rim` water's deep `#5E8C90` over `deep_teal_shadow` `#0E4A55` (deeper toward the foot), toward `turquoise_shallow` `#3FD0C9` at the thin edges and in streaks; `foam_white` `#EEF6F4` at the foot; the robe leans 0.4 further to `deep_teal_shadow` | `glimmer_bound` `#4FB3B0` at 1.6, mask 0.06 (0.04 on the robe) |
| `inner` (the heart, seen through the chest: the triangles whose glow passes 0.3) | the same water, a little deeper toward the heart | `glimmer_bound` at 1.6, mask up to 1.0 at the heart: the brightest part of her, the "Kesh pale cyan" of `lut_ch16_choir` |
| `hair` | `deep_teal_shadow` to `#5E8C90`, paler streaks, `turquoise_shallow` down the fall, `foam_white` at the ends | `glimmer_bound` at 1.6, mask 0.06 at the crown fading to 0 at the ends |
| `mouths` (the mouths and the girdle) | `cold_blue_stone` `#5E6E80` worn toward `salt_glass` `#BFE6E0` on the lips; `abyss_navy` `#061A2B` in the opening; the girdle's beads the same stone | `glimmer_bound` at 1.0: mask 0.4 in each opening, 0.18 on the inner lip, 0 on the girdle |
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

Every clip is authored from rest and played from idle's first frame (`ck.in_pose`), so each one starts where the idle
starts, and the one-shots end there. The exceptions are rise (it starts folded, as the call), and ko and dismiss
(they end sunk).

| Clip | Length | Wind-up → contact | What the water does |
|---|---|---|---|
| `idle` | 4.0 s, loop | — | the column sways as one, the hair and the robe sway lagging down their chains, she breathes; the face three-quarters to the camera |
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

18,824 triangles, 10,762 vertices, 39 bones, 5 slots, GLB 3.18 MB (26 clips). That is over the ~18k guide by 0.8k
because of the mouths: 88 at 60 triangles each (5,280). The mouths are the robe's identity, and smaller counts read
as polka dots, not a robe of mouths. The rest:

| Part | Triangles |
|---|---|
| body and column (`water` 2,841 + `inner` 1,047) | 3,888 |
| robe panels (both faces) | 2,352 |
| hair (sheet, both faces, and strands) | 1,994 |
| head | 1,872 |
| arms | 1,104 |
| hands | 1,080 |
| key | 774 |
| girdle | 480 |

## As built (M4-A2P-057, 2026-10-30)

`assets_src/creatures/kesh/build_kesh.py` (`--report` prints the numbers) builds `assets/creatures/kesh/kesh.glb`, and
`materials.json` gives the five slots through write_materials.py. The Blender job is `creature_kesh`, and the build
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
- **88 mouths, not "a hundred".** The budget note above explains why.
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
- **Up close:** the face is a calm, readable woman's face, but simple. A finer head (more rings, or a sculpted
  profile) would cost about 1k triangles. The hair's crown still shows a faint ridge where the sheet's side columns
  meet the cap.
