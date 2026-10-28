# Nhoa, the Rootlight (`nhoa`), Asha's Vowbound: design sheet (built, M3-CRE-642)

**Who:** the fifth Vowbound (docs/kb/story/vowbound.md §5): the glimmer of **Ressa**, the 56th Cantor, about 70
years ago. She was the only Kirru Cantor and Pell's clutch-sister, a hearer who believed she could end the storm
from inside. She is bound in Lowlight's drowned sanctum (Ch11), at the foot of the Lit Age well-shaft where the
deep's cold wells up. **Kind:** a Vowbound: bound light. **Role:** an ally, Ice. Her battle identity is ice carried
on sifting mote-swarms, and copying the last enemy action (an echo of Pell). Her Swell is *Farewell-Tide*.
**Status:** built (M3-CRE-642, in review; "As built" at the end). She is not yet in game/data/battle/vowbound.json;
Combat adds the row. Until then her creatures.json row carries `vowbound_pending`. The build follows Ilun's pipeline
(ilun.md, M3-CRE-638).

**The idea:** a tall Kirru-like figure made entirely of motes held in her shape, like silt hanging in deep still
water. She has antlers of mangrove root, a long heron neck, and **a carved name-shell at her throat**, the keepsake
and the only solid object on her. She moves through water as if it were air, and the cold moves with her. She reads
as **grave and kind**: a sister, not a spirit of winter.

Original design (README rule 1). It starts from the Kirru's own look (glossary: heron- and otter-like; she is
*Kirru-like*, never a heron or an otter as a beast), a mangrove's prop-roots for the antlers, and silt suspended in
cold water. **IP and story guard (vowbound.md, ADR 0015):** nothing about her is frozen. No ice crystals, frost, icicles
or a frozen surface; her cold is the deep's. The ice reads through the colour of the light, the stillness and a cold
haze, never through frozen matter.

## Silhouette and size

| | |
|---|---|
| Height | **3.2 m** to the antler tips (head at 2.5 m): tall and narrow. A vertical silhouette, so the summon camera's ±2.1 m vertical hold around 1.6 m fits her and the crowded HUD right edge stays clear (Ilun's tail crossed it) |
| Body | a long, slight Kirru figure: a heron's long neck (0.9 m) carrying a small, sleek otter-like head; narrow shoulders; long arms ending in webbed, long-fingered hands; a robe-like lower body that thins into hanging strands of motes above the water instead of legs |
| Hover | the strands' lowest ends 0.15 m above the water. She stands in the water as if in air, never touching it |
| Antlers | two branching crowns of mangrove root (0.7 m), knuckled and uneven like the prop-roots the Drowner was built from (shared visual language, different meaning: here the roots hold light up, not down) |
| The name-shell | a carved spiral shell (9 cm) on a cord at her throat: `bone` albedo, the carving dark lines. It is an object, so it never glows |

## How "made of motes" is built (no particles)

The bound-light rule (color_script.md rule 2, palette.json `glimmer_bound`: "steady: no flicker, no drift, no shed
motes") holds for a Vowbound. So her motes are **geometry skinned to her bones**, as Ilun's net is: about 1,800 small
flattened beads (each 2–4 cm), seeded with a `default_rng`.
- They are scattered through a shell 4–8 cm deep around her body surface, densest at the core and thinning toward the
  edges, so the silhouette reads soft and grainy rather than as a solid.
- A dark inner body (`abyss_navy`) shows between the beads, so she reads as light held in deep water.
- The beads move only with her body. Nothing drifts by itself.
- "Sifting" is shown by the clips: the hanging strands sway, and her hands trail strands.

The one exception is Farewell-Tide's rising column, the only Vowbound finisher where the motes go up (vowbound.md
§5, a seed for the Letting). That column is battle VFX (battle_vfx.md, the rendering and battle-presentation tracks),
not the model; the model's `special` clip lifts her arms and the strands into the column's shape.

## Colour (palette.json swatches)

| Part | Albedo | Light |
|---|---|---|
| The inner body | `abyss_navy` `#061A2B` | none |
| The motes | `salt_glass` `#BFE6E0` | `glimmer_bound` `#4FB3B0` at 1.2, steady (a mask varying 0.4–1.0 per bead, so the swarm has depth) |
| The antlers | `timber_weathered` `#7E6A55` paling toward `bone` at the tips | a faint `glimmer_bound` (0.25) along the tips only |
| The eyes | `deep_teal_shadow` | `glimmer_bound` 0.55 |
| The name-shell | `bone` `#E6DAC0` with `tattoo_ink` carving | none |

The "cold" is the motes' pale `salt_glass` and the light's blue-green against the `abyss_navy` dark. That is enough
for Ice inside the palette without inventing a frost colour. No `spawn_wound` (she is an ally, ADR 0151). No
`glimmer_lift`: her light rises only in the finale's release (Ch20).

## Clips (contact seconds go in creatures.json `contact`)

| Clip | Length | What it shows |
|---|---|---|
| `idle` | 4.0 s, loop | the strands sway as if in a slow current; the neck sways; the hands drift |
| `ready` | 1.4 s | she lifts her head and spreads her hands; the strands gather in |
| `attack` | 1.2 s, contact ~0.55 s | a sweeping open-handed strike, the trailing strands following |
| `cast` | 1.6 s, contact ~0.8 s | the ice: both hands drawn up and pushed forward, the strands streaming forward |
| `hit` | 0.5 s, peak ~0.1 s | the neck snaps back, the strands scatter outward and settle |
| `defend` | 1.2 s | her arms cross before her and the strands wrap around her front |
| `ko` | 1.8 s | she bows her neck, folds in on herself, and the strands hang straight down |
| `victory` | 2.2 s | she straightens to full height and the antlers lift |
| `rise` | 2.6 s | from folded low (neck bowed, arms crossed) she unfolds upward, strands last |
| `dismiss` | 1.0 s | she folds back down, neck bowed |
| `special` | 2.4 s, contact ~1.45 s | Farewell-Tide: arms lifted high and the strands drawn up into a column around her (the VFX column takes over) |
| `echo` (optional) | 1.2 s | her copy of the last enemy action: a mirror-like pause, then her version of a generic strike. Only if Combat's copy skill wants its own clip; otherwise `attack` serves |

**The Pell scene** (Ch20's final fight, vowbound.md §5): he turns his back and sings. That is Act III cinematics, not
built here.

## Rig and budget

About 22 bones: `root`, a three-bone `spine`, a four-bone `neck`, `head`, two bones per antler, two per arm plus
`hand`, and three strand chains of three bones each. Up to 16k triangles. The motes are most of it (about 1,800
beads at 4–6 triangles each), so the body under them is cheap. Five slots: `body`, `motes`, `antler`, `eye`,
`shell`.

## Open questions (for Combat and the Lead, not the human)
- Her row in vowbound.json (skills, the copy skill, `farewell_tide`). The model waits for no stats; the build can
  start from this sheet.
- Farewell-Tide's rising column needs the rendering track's sanction as the one bound-light exception. vowbound.md
  already calls it out; color_script.md should say so too.

## As built (M3-CRE-642, 2026-10-27)

`assets_src/creatures/nhoa/build_nhoa.py` (`--report` prints the numbers) → `assets/creatures/nhoa/nhoa.glb` (1.77 MB).
The changes from the proposal above are recorded here.

- **14,820 triangles** (budget 16k), 10,861 vertices. The motes are 9,738 of them: **1,623 beads** (not about 1,800),
  each a flattened triangular bipyramid of 6 triangles, 1.4–4 cm across. They sit 0 to 6 cm out from the surface,
  most near it. The rest is the inner body (2,980), the antlers (1,272), the shell (420), its cord (250) and the eyes
  (160). Five slots, as proposed.
- **28 bones** (not about 22): `root`, `spine_0..2`, `neck_0..3`, `head`, two per antler, three per arm (`upper`,
  `fore`, `hand`), and three strand chains of three (`strand_l`, `strand_r` and `strand_b`, at 60°, −60° and 180°
  round her). The proposal's count left out the hands and the third segment. Strand beads are skinned to the two
  chains either side of them, blended by bearing. The hem blends into the chains' first bones.
- **Rest:** x ±0.47, y 0.15 to 3.19, z −0.25 to +0.30. The head bone sits at 2.45 m and the antler tips at 3.19 m. The
  strands' lowest ends are at 0.15 m (built hovering, no stand-in `hover`). Across every clip the lowest vertex is
  0.05 m (the KO's lowered strands), so nothing goes under the water.
- **The bow is softened.** The first fold (ko, rise's start, dismiss's end) bowed about 130° through the spine, neck
  and head, so the antlers pointed straight at the foes like a charge. That reads as a threat, not as grave and kind.
  The head now counter-turns, so in the folded pose the crowns lean forward and stay up. Only the KO lowers them
  toward level.
- **Clips** as the table above, plus the kit's `idle_b` and an authored `hit_b` (rolled to the other side). The hit
  peaks at 0.10 s. Contacts: attack 0.55 s, cast 0.8 s, special 1.45 s. With no skill ids yet, `clip_by_skill` is
  empty, and magical skills play `cast` by kind. `echo` is not built (see the open questions).
- **Framing correction.** The summon shot's ±2.1 m does *not* hold her whole height inside the HUD safe frame. From
  that low camera the bottom safe line on her mark is at about 0.6 m, so the lower 0.45 m of her strands sit under the
  HUD's bottom band in every clip, as Kahre's feet do. At rest the summon margins are left 0.40, right 0.30, top 0.04
  and bottom −0.11. The top stays inside in `idle`, `ready` and `rise` (what the shot plays); only hit_b's peak (−0.003)
  and Farewell-Tide's raised arms (−0.006) pass it. **Default battle camera** (Vowbound slot, yaw −90): inside in every
  frame of every clip. At rest the margins are left 0.70, right 0.05, top 0.05 and bottom 0.14; the tightest are
  hit_b's right edge (0.008) and cast's (0.010).
- **The name-shell never glows:** the `shell` slot's emission energy is 0, and the shell and cord carry no emission
  mask. No mote is placed within 7.5 cm of the shell or within 4 cm of an eye.

## As built: the held form (M3-CRE-647, 2026-10-28)

The foe form for the Ch20 release fight (act3_roster.md, "The Vowbound as foes").

- **`release`** (3.4 s, its KO as a foe; the only clip added, every other clip samples identically): she straightens and opens her hands; the hanging strands of motes swing out and up round her hem (her Farewell-Tide's column shape, the only time her motes rise), arms raised and open, face lifted, held (1.3–1.9 s); then she rises with them 1.5 m up and 0.5 m back.
  Lowest vertex over every frame +0.15 m. GLB 1.77 → 1.89 MB.
- Scene `game/creatures/nhoa/nhoa_held_battle.tscn` (the same GLB; `CreatureActor.material_dir` puts on `assets/creatures/nhoa/materials_held/`, written by write_materials.py from the `held` block in materials.json: 3 emissive slots glimmer_bound to glimmer_held `#7FC6D9` at the same energy, steady; the rest as they are). creatures.json row `nhoa_held`: no `vowbound` key, `ko` = `release`, `phases.release` = {clip `release`, `hold` true}, `stand_in.yaw_deg` 90 (facing the party), height 3.2 and radius 0.5 kept. Review shot `creature_nhoa_held` (not rendered yet). No enemies.json row (Combat's, with the chapter designer). The turn to `glimmer_lift` and the rising motes are presentation (battle VFX), not the model.
