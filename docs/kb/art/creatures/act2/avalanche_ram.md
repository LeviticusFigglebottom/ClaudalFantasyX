# The Avalanche Ram (`avalanche_ram`), Ch12 boss

**Where:** the terrace wall above Keth Pass, where drowned glimmer seeps out of a Lit Age terrace (act_outline Ch12:
"a woolback grown monstrous on drowned glimmer seeping from a Lit Age terrace wall").

## The idea

An Ullari woolback, a long-necked shaggy pack animal, that drank where the seep runs and grew. It is
still a woolback: the long neck, the shaggy coat, the soft muzzle. But it stands 3 m at the head and its fleece has
matted into heavy wet plates, and where the fleece parts the seep's cold light shows through. The woolback
was someone's: a frayed herd-cord with a few knots is still tied round its neck.

The one exaggeration: **size, and the light under the fleece**. Nothing horned or demonic: the Ullari's own animal,
too big.

## Silhouette

- A long-necked, deep-chested animal 4 m long, the neck rising to 3 m, the head low when it charges.
- The fleece hangs in heavy sodden locks to the knees; the wool hangs wettest and darkest at the jaw and belly.
- The herd-cord at its neck, with its knots: the small, human detail.

## The head (M3-CRE-635)

The first PC render read the head as a duck's: a dark, flattened muzzle on a white face is a bill. The head is a
camelid's now (a llama's or an alpaca's proportions, not a copy of either):
- long and narrow (0.75 m, 0.29 m wide), deepest at the cheeks, the nose a little down;
- a soft, rounded muzzle in the coat's colour, `laterite` darkened **only at the nose and the lips** (slit nostrils,
  a split upper lip), a slim lower jaw with a wet beard underneath;
- eyes at the sides under a soft brow; long upright ears, their tips drooping a little out; the woolly cap kept;
- the neck slimmer under its fleece.

The dripping lock ends are few and uneven: one to three per lock chain (0.1-0.2 m past the strand's end, blunt and
rounded, soaked dark), two clumps under the belly and one under the jaw. Never a row of even spikes: that reads as
teeth.

**No ice (M4-A2P-059, ADR 0015, 2026-10-30).** The Ram's terrace is Ch12's set piece, so nothing on it is ice or frost:
the ice plates are wet mats of wool (`sand_cloth` and `overcast_slate` soaked dark, glossy by wetness), the icicles are
sodden lock ends, the ice beard is a wet one, and the `ice` material slot is gone. Snow on the pass is weather.

## Palette

Fleece `sand_cloth` (undyed wool) gone grey (`overcast_slate` in the shadows), the wet mats and lock ends soaked dark (no ice: M4-A2P-059); muzzle and legs
`laterite` darkened; seep light through the partings `spawn_wound` (the weak points), shedding `glimmer_held`; the
herd-cord `lacquer_red` faded.

## Battle read and clips

- **At battle distance:** a huge shaggy long-necked animal, pale, with cyan seams in its coat.
- `idle`: the neck sways, it chews, breath steams (VFX), the locks swing.
- `attack` (the charge): the head drops, a stamp, and it drives through; contact at 0.75 s of 1.6 s.
- `cast` (the bellow): the neck rises and it calls; snow sheds off the terrace wall (the field hazard, VFX).
- `hit`: it staggers back, the neck whips, water and snow shake off the locks (VFX puffs, no shards); peak near 0.1 s.
- `ko`: it kneels, then lies down; the herd-cord is the last thing in frame. (Pillar 1: no gore, no thrash.)

Budget ≤ 16k triangles. Rig: a quadruped (spine 5, neck 5, head, jaw, four legs of 3), plus six fleece-lock chains
of 2 that lag the body.

## As built (M4-CRB-005, the Act II move pass; ADR 0041 §3, ADR 0204 keeps `torn_fleece`)

**Budget:** 15,779 triangles (≤ 16k): the Ram 15,035, `TornShoulder` 264, `ShoulderPlate` 480. 43 bones, 23 clips.
No new material slot (the plate and the torn shoulder are `fleece`, the seep in the tear is its emission), so no new
PROVENANCE row.

**Rig.** Added, unweighted: `vfx_wound` (the widest parting on the camera's flank, mid-barrel, `spine2`), `vfx_core`
(the chest, `spine3`), `vfx_phase` (the shoulder hump where the plate tears, `spine3`); creatures.json `vfx_anchors`
names the first two. Weighted: `cord` (on `neck1`, the herd-cord's frayed end, so it hangs and swings: every clip keys
it to turn back most of the neck's pitch and roll on a damped spring, settling on the plain hang at each clip's end)
and `plate` (on `spine3`, the felted shoulder plate, so `phase_tear` can tear it off).

**Mesh.** `ShoulderPlate`: a felted mat of the coat over the camera-side (−x) shoulder hump, ~0.9 m across, ragged at
the edge, the coat's furrows and lumps in it, darker where matted, grit and slate chips lodged in it, closed underneath
so it reads as a slab when it falls. `TornShoulder` under it: raw under-wool with a lip of pale torn fibres and the
seep's light welling up in a pool and five cracks (the torn phase's weak point). Nothing is ice (ADR 0015).

**Staging.** The clips are authored for the stand-in's `yaw_deg` 60: the battle camera and the party see the −x
flank (the plate's side), and the head points toward the party, so "away from the party" in the clips is +x.

**Clips** (each starts and ends on its phase's idle first frame, except the intro's start, the KOs' ends and the
`ready` loops; the legs are solved every frame under the body, so the hooves stay planted unless a track lifts one):

| Clip | Length | Contact | What moves |
|---|---|---|---|
| `idle` | 4.0 s loop | — | the neck sways, it chews, the locks swing; the cord hangs |
| `idle_b` | 1.4 s | — | it lifts its head and shakes it side to side, the locks shivering |
| `ready` | 1.6 s loop | — | the head dropped; the right fore paws the flags (lifts forward, drags back) |
| `intro` | 2.6 s | — | it drinks at the seep pool, lifts its head out, turns its neck to the party, stamps once |
| `charge_gather` | 1.2 s | — | the head drops low, the hindquarters coil (rump down, weight back), a forehoof scrapes once, it trembles |
| `attack` (the charge) | 1.6 s | 0.75 | 0–0.52: head drops, the right fore stamps; it drives through head low, then back |
| `cast` (the bellow) | 2.0 s | 0.9 | 0–0.4: chest draws in; 0.4–0.8: the neck rises to full height; 0.9: jaw wide, it calls, the locks shiver |
| `neck_sweep` | 1.5 s | 0.75 | 0–0.6: the neck swings wide away from the party (+x), low; then sweeps through at chest height |
| `fleece_shake` | 1.4 s | 0.6 | 0–0.5: it braces low; then a wet-dog shake running from the neck to the rump, the locks flung out |
| `hit`, `hit_b` | 0.6 s | peak 0.1 | `hit`: it staggers back, the neck whips; `hit_b` (authored): its front lifts, the neck whips the other way, the head rolls |
| `ko` | 3.8 s | — | it kneels, lies down on its folded legs, lays its head down; the herd-cord last in frame; no thrash |
| `phase_tear` | 2.2 s | 1.0 | it rears, calling, forehooves up (0.3–0.95); slams them down and the plate tears off its shoulder and falls on its back on the terrace in front of the near forelegs; it lands lower, in the torn stance |
| `idle_torn` | 4.0 s loop | — | lower (the body down 8 cm, pitched forward), the neck forward, the head lower, breathing harder, the torn shoulder's lock hanging out |
| `*_torn` | as above | as above | `attack`, `cast`, `charge_gather`, `neck_sweep`, `fleece_shake`, `hit`, `hit_b`, `ready`, `ko` from the torn stance |

The plate, once torn, is hidden (`hide_after`) and its bone keeps it where it fell in every torn clip, so it never
moves with the body or goes under the floor. `TornShoulder` is shown as the phase starts (`show`), under the plate
until it tears, so the seep shows the moment the plate goes.

**Clip map for combat** (skills are combat's; creatures.json has no `clip_by_skill` until the skills exist in
skills.json; the `contact` times are already in the row):

| Skill id (proposed) | Clip | Contact (s) | In `torn_fleece` |
|---|---|---|---|
| `ram_charge` | `attack` (after `charge_gather` on the gather turn) | 0.75 | `attack_torn`, 0.75 |
| `bellow` | `cast` | 0.9 | `cast_torn`, 0.9 |
| `neck_sweep` | `neck_sweep` | 0.75 | `neck_sweep_torn`, 0.75 |
| `fleece_shake` | `fleece_shake` | 0.6 | `fleece_shake_torn`, 0.6 |
| phase `torn_fleece` (40%) | `phase_tear` (`idle_torn`; shows `TornShoulder`, hides `ShoulderPlate` after) | 1.0 (the slam and the tear) | — |

```json
"clip_by_skill": {"ram_charge": "attack", "bellow": "cast", "neck_sweep": "neck_sweep", "fleece_shake": "fleece_shake"}
```
