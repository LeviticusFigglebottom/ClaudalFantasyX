---
draft: pre-gate
adr: 0203
boss: avalanche_ram
chapter: 12
owner: creatures-b
task: M4-CRB-001
---
# The Avalanche Ram (`avalanche_ram`), Ch12 boss: design sheet (draft: pre-gate)

**Built:** mesh, rig and 5 clips (`idle`, `attack`, `cast`, `hit`, `ko`; [art sheet](../../../art/creatures/act2/avalanche_ram.md),
the camelid head of M3-CRE-635). Choreo has its intro (`boss`, 2.0 s), the charge gather, `charge_side` framing and
camera pressure. Music `avalanche_ram` exists. **Missing:** the enemy row, skills, the snow field, a clip per skill,
`intro`, `ready`, `hit_b`, `idle_b`, the anchors, and **the wool swap** below.

**What the fight teaches:** mind the field. Its charge and its bellow bring the snow down off the terrace wall, and the
snow builds round by round. It is the Ullari's own animal grown too big, and someone's: a frayed herd-cord is still
knotted round its neck.

## The wool swap (ADR 0015) — filed as [M4-CRB-001](../../../tasks/M4/M4-CRB-001-avalanche-ram-wool-swap.md)

ADR 0015: **no ice, frost, glacier or frozen water in any temple or set piece from Ch12 to Ch15.** The Ram's terrace is
the Ch12 boss's set piece, and its current sheet and model carry ice ("fleece matted into plates of ice", "ice beards
it at the jaw and belly", icicles on the lock chains, `salt_glass` ice on the locks). All of it goes. Snow on the pass
is weather, so snow caked into wool is allowed; nothing on the Ram is frozen.

| Was (built) | Becomes |
|---|---|
| fleece "matted into plates of ice and wool" | **felted plates of matted wool**, heavy and grey, with grit and slate chips lodged in them from lying on the terrace |
| icicles at the lock tips (up to 0.32 m) | **felted lock tips**, knotted and weighted with **caked snow** (rounded clumps, never spikes) |
| ice beard at the jaw and belly | a **snow-caked wool beard**: clumped, dripping meltwater, soft at the edge |
| `salt_glass` ice on the locks (translucent, glossy) | snow cake in `foam_white` (opaque, rough 0.95, no clearcoat, no transmission) and grit in `cold_blue_stone` |
| `hit`: "ice cracks off" | `hit`: **snow and grit shake loose** from the locks (VFX puffs, no shards) |
| `cast`: "snow sheds off the terrace wall" | unchanged (the hazard is weather off the wall) |

The rest stays: the camelid head, the long neck, the herd-cord, the seep light through the partings. The swap is a
build-script change (lock geometry and the `fleece_ice` slot), not a new model.

## 1. Silhouette (at 12 m)

- A long-necked, deep-chested animal 4 m long, the neck rising to 3 m. The one shape: **a huge shaggy pack animal with
  a long neck**, unmistakably the woolback the player passed on the switchbacks.
- **Facing:** side-on to the camera (`stand_in.yaw_deg` 60, choreo's `charge_side` lead), so the neck and the length
  read. Head-on it would be a wool blob.
- The felted plates hang to the knees in uneven locks; the herd-cord's red is the only warm note on it.

## 2. Materials

| Slot | Swatch | Notes |
|---|---|---|
| `fleece` | `sand_cloth` gone grey, `overcast_slate` in the partings' shadows | dry, rough 0.9 |
| `fleece_snow` (was `fleece_ice`) | `foam_white`, with `cold_blue_stone` grit | opaque, rough 0.95 |
| `skin` | `laterite` darkened at the nose and lips only | |
| `seep` | `spawn_wound` emissive | the weak points, in the partings |
| `shed` | `glimmer_held` | a few motes shed from the partings when hit (VFX) |
| `cord` | `lacquer_red`, faded | the herd-cord and its knots |

Arena light: `ch12` 09:00, cold, high contrast, `lut_ch12_heights` (the woven reds kept). The seep runs down the wall
behind it in sheets of held light, which is the only cyan in the frame besides its own partings.

## 3. Rig

A quadruped (spine 5, neck 5, head, jaw, four legs of 3) and six lock chains of 2 that lag the body. **Add
(unweighted):** `vfx_wound` (the widest parting, on `spine_2`), `vfx_core` (the chest), `vfx_phase` (the shoulder hump,
where the fleece tears). **Prop:** `cord` bone on `neck_1` so the herd-cord swings and can be framed in the KO.
**Grounding:** all four hooves planted by IK; only the charge and the stamp lift them.

## 4. Move list

| Skill (id) | Clip | Wind-up → contact (length) | What moves | Target | VFX and camera |
|---|---|---|---|---|---|
| intro | `intro` *(proposed)* | — (2.6 s) | it lifts its head from the seep pool, turns its long neck to the party, stamps once | — | `boss`, 2.0 s; `under_the_wall` hint |
| idle | `idle`, `idle_b` | — (4.0 s / 1.4 s) | the neck sways, it chews, breath steams; `idle_b` a shake of the head | — | breath VFX (the living animal fogs) |
| ready | `ready` *(proposed)* | — (1.6 s) | the head drops, a forehoof paws the flags | — | — |
| `ram_charge` *(proposed, charge)* | `charge_gather` *(proposed)* then `attack` (built) | gather 1.2 s (head low, hindquarters coil); strike 0.0–0.75 s → 0.75 s (1.6 s) | it drives through | one foe and the slot beside it; brings snow (field +1) | choreo gather and `charge_side`; snow off the wall |
| `bellow` *(proposed)* | `cast` (built, retimed) | 0.0–0.8 s: the neck rises full height → 0.9 s (2.0 s) | it calls | sets or deepens the `snowfall` field | snow sheets down the wall (VFX) |
| `neck_sweep` *(proposed)* | `neck_sweep` *(proposed)* | 0.0–0.6 s: the neck swings wide away from the party → 0.75 s (1.5 s) | the neck swings through | the front two foes | `boss_sweep` |
| `fleece_shake` *(proposed)* | `fleece_shake` *(proposed)* | 0.0–0.5 s: it braces, legs wide → 0.6 s (1.4 s) | a whole-body shake | all foes: Darkness (snow in the eyes) | snow and grit puffs, never shards |
| hit | `hit`, `hit_b` *(hit_b proposed)* | peak 0.1 s | staggers, the neck whips, snow shakes loose | — | — |
| phase `torn_fleece` *(proposed)* | `phase_tear` *(proposed)* (2.2 s) | — | it rears, a felted plate tears from the shoulder; it lands lower | — | `vfx_phase`, the seep light bright through the tear |
| KO | `ko_torn` *(proposed)* | — (2.6 s) | it kneels, then lies down; the herd-cord is the last thing in frame | — | no gore, no thrash (pillar 1) |

## 5. Phase change *(proposed: the plan names none)*

- **Trigger:** 40% HP.
- **Clip:** `phase_tear`, ending on `idle_torn` *(proposed)*.
- **Stance:** head lower, neck forward, the torn shoulder showing the seep. The `clips` map covers `attack`,
  `charge_gather`, `neck_sweep`, `fleece_shake`, `hit`, `hit_b` and `ready` with `_torn` versions.
- **What the player learns:** it is hurt and charges every other turn, and each charge adds snow. Taking the charge on a
  guard (Toma) and ending the fight before the field stacks matters more now. Hesk is bound after this fight (C3), so
  her cleanse is not part of the answer.

## 6. Arena read (`keth_seep_terrace`)

- **Light:** `ch12` 09:00, sun 30°, key 2.8, `lut_ch12_heights`. No sea in frame.
- **Placement:** the `BossAnchor` beside the `seep_pool` at (−9, −4.2), side-on, under the seeping `lit_terrace_wall`.
- **Must never happen:** the neck sweep or the charge crossing the camera ray at 0.9 m before contact; the head
  leaving the top of the frame when the neck is raised in `bellow`.
- **Hazard:** `snowfall`, a `field_rules` entry that builds by round (stack 1–3: Slow, then Slow plus damage per turn),
  and a falling-snow field VFX that never covers the party's faces or the timeline.
- **Camera:** `charge_side` for the charge; `the_pass_below` stays free for Kerrid's breath frame outside the fight.

## Balance, engine, owners

- **Curve:** Act II boss. **Role answer:** Toma guards the charge's target; Liss or Rhen keep damage on the partings.
- **Engine:** field hazard by round (`field_rules` exists); stacking per round may need a small extension.
- **Owners:** creatures-b (wool swap M4-CRB-001, new clips, anchors); combat (row, skills, field, suite);
  battle-presentation (snow field VFX staging); rendering (snow particles and breath); audio (stems exist; bellow).

## Open questions

1. Is the `torn_fleece` phase wanted, or should the Ram stay single-phase with the field as its only escalation?
2. Echo check: a giant mountain beast on a pass is generic. The fight's beats (someone's animal, the herd-cord, the
   seep) are ours, and with the wool swap nothing is frozen.
