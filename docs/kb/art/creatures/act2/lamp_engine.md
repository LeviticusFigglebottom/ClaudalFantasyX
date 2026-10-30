# The Lamp Engine (`lamp_engine`), Ch11 boss

**Where:** Lowlight, the half-drowned temple: the engine hall below the sanctum (act_outline Ch11: "a still-running
Lit Age machine full of bound dead, two phases; releasing its core makes a small upward lift").

## The idea

A Lit Age construct, the second after the Cinder Matron: a machine for keeping light. A tall brass frame
holds a lattice of salt-glass lamps around one core, and each lamp holds a bound dead light, steady and
unpulsing (`glimmer_bound`, color_script rule 2). Water has risen to its knees and it is still running, still
trimming, still turning its lamps toward a congregation that drowned. It isn't cruel. It keeps.

The one exaggeration: **a temple lamp-stand that walks**. Every part is a real lamp-stand's (gimbals, chimneys,
trimming arms, a bell-shaped hood); it is simply the size of a chapel and has four jointed feet.

## Silhouette

- A 3.4 m bell-hooded tower of lamps on four short jointed legs: twelve lamps on three gimballed rings, the
  rings turning against each other; two long trimming arms with scissor heads.
- **Phase 2:** the rings fold back like petals and the core shows: a single large salt-glass globe, cracked, with
  the brightest bound light in it.
- Reads as vertical and ringed, nothing like the Matron's squat body.

## Palette

Frame `brass` going to `bronze_patina` at the waterline, `lacquer_black` joints; chimneys `salt_glass`;
lamp lights and the core `glimmer_bound` (emissive, steady); its weak points (the gimbal hubs) `spawn_wound`.
Drips of `sea_glow` where water runs down the glass.

## Battle read and clips

- **At battle distance:** a tall ringed tower of steady lights on legs, its arms raised.
- `idle`: the rings turn slowly against each other; the trimming arms tick; water drips.
- `attack` (the trim): an arm's scissor head snips at the target; contact at 0.6 s of 1.3 s.
- `cast` (the gathering): every lamp swings to face the target and brightens in sequence; a held breath.
- `hit`: the rings jolt and a lamp swings loose on its gimbal; peak near 0.1 s.
- `ko`: the core goes dark and a small lift of motes rises out of it (VFX, `glimmer_lift`: the dead it held
  released), then the frame settles on its knees.
- **Phase `opened`** (50% HP): `phase_change` (2.0 s), the rings fold back and the core shows; `idle_opened`.

Budget ≤ 20k triangles. Rig: body, three ring bones, twelve lamp gimbals, two arms of 3, four legs of 2, the core.

**Break parts (proposal):** the lamp rings (one per ring). Each broken ring frees its lamps (they go dark) and
slows the cast. The conduit crawlers (roster) repair them.

## As built: the final-quality move pass (M4-CRB-003, ADR 0041 §3, ADR 0205)

Audited from the battle camera in `lowlight_engine_hall` (enemy slot 0) and up close; rebuilt to the Act I standard
(M3-CRB-013). Budget: **18,680 triangles** (≤ 20k), 12,826 vertices, 53 bones (50 + 3 anchors), 25 clips, four
materials unchanged (`frame`, `glass`, `hub`, `core`: no new `.tres`).

**Model fixes (what read unfinished at 12 m):**
- The housing read as one smooth brown egg. Each ring's plates now **flare out toward their lower edge** (`FLARE`
  0.1, radially) and overlap the ring below like shingles, with a **lacquered black lip** under each: three stacked
  bands, the "ringed tower".
- The lamps were small for the read. They are **1.2× larger** (`LAMP_SCALE`), the gimbal hubs set out to match.
- Arms and legs read as sticks. The arms are thicker, with tapered upper arms, bigger lacquered joints and sleeves; the
  shears' blades are **0.78 m and broad** (they read as shears, not needles). The legs are thicker, tapered, with a
  lacquered greave collar on each shank.
- The bared core read as a flat pale disc. Its light now falls from the face toward the rim, so it reads as a lit
  globe.
- **Stand-in yaw 90° → 55°** (creatures.json `stand_in`). At 90° the battle camera saw it side-on and the near arm
  crossed in front of the body, cutting the core in half in phase 2. At 55° it faces the camera and the party's
  quarter: symmetric, both arms raised either side, the core seen whole.
- No gold anywhere: the lamps and core stay `glimmer_bound` (steady, teal). The opened burst and the KO lift are VFX
  at the anchors.

**Anchors (unweighted):** `vfx_wound` (the near gimbal hub of the middle ring, on `petal1_0`, so it folds back with
it), `vfx_core` (the core's centre, on `core`), `vfx_phase` (the core's crack facing the party, on `core`). The row's
`vfx_anchors` names `vfx_core` and `vfx_wound`.

**Clips.** Every one-shot is authored from rest and played from its phase's idle first frame (`in_pose`), so it starts
and ends exactly there. `phase_change` is pinned from the closed idle's first frame to the open idle's. The legs hang
from `root`. The body leans about the hips, and whenever the body drops (the intro's crouch, the KO kneel) the legs
are solved every 0.1 s so the feet stay planted (`legs_follow`). Nothing goes under the floor (GroundedClipsTest).

| Clip | Length | Contact | What moves |
|---|---|---|---|
| `intro` | 2.8 s | — | dormant on bent knees, arms folded down, lamps hanging; the rings wake bottom to top (a jolt, then they turn home), their lamps swing up level; it rises, the arms lift high with the shears open, and it settles |
| `idle` / `idle_opened` | 6.0 / 5.0 s loops | — | the rings turn against each other, the lamps sway, the shears tick / open, the petals breathe |
| `idle_b` | 1.4 s | — | the near arm lifts and trims the air twice |
| `ready` / `ready_opened` | 1.6 s loops | — | leans in; the middle ring turns, every lamp tips at the party; shears raised and open |
| `attack` / `attack_opened` (engine_trim) | 1.3 s | 0.6 | the arm winds up high and back with the shears open (by 0.35 s), reaches and snips |
| `lamp_gather` (+ `_opened`) | 1.8 s | 1.2 | ring by ring, every lamp swings onto one hero; the arms rise wide, the frame leans back: a held breath |
| `lamp_burn` (+ `_opened`) | 1.6 s | 0.8 | the lamps lock on, the frame draws back with the arms pulled wide (0-0.7 s), then pitches in as they fire and holds the beam |
| `call` (+ `_opened`) (call_the_tenders) | 1.4 s | 0.7 | the near arm swings up high with the shears shut, then knocks them against its own bowl; the frame and rings jolt |
| `twin_trim` (+ `_opened`) | 1.7 s | 0.85 | both arms cross high over the hood with the shears wide (0-0.7 s), then snip down and out at two foes |
| `cast` | 1.8 s | 1.0 | the generic gathering (fallback for unmapped skills) |
| `cast_opened` (core_flare) | 2.0 s | 1.0 | the petals spread wider, the frame leans back with arms flung wide (0-0.9 s), then the core leans out in its collars and the frame pitches in after it |
| `hit`, `hit_b` (+ `_opened`) | 0.7 s | peak 0.1 | the rings jolt, one lamp swings loose; `hit_b` the other way, heavier |
| `phase_change` | 2.0 s | 1.1 (the burst) | rings jolt; the middle ring folds back, then the top and bottom, the lamps a beat behind; the core lifts; arms spread |
| `ko` / `ko_opened` | 3.0 s | — | the core sinks and turns (its light going out is VFX), the rings sag, the arms drop into the water, it settles on its knees |

**Clip map for combat** (creatures.json `clip_by_skill` once the skills exist in skills.json; the `opened` phase's
`clips` map already sends each one to its open version):

| Skill id | Clip | Contact (s) | In `opened` |
|---|---|---|---|
| `engine_trim` | `attack` | 0.6 | `attack_opened`, 0.6 |
| `lamp_gather` | `lamp_gather` | 1.2 | `lamp_gather_opened`, 1.2 |
| `lamp_burn` | `lamp_burn` | 0.8 | `lamp_burn_opened`, 0.8 |
| `call_the_tenders` | `call` | 0.7 | `call_opened`, 0.7 |
| `twin_trim` | `twin_trim` | 0.85 | `twin_trim_opened`, 0.85 |
| `core_flare` | `cast` | (phase 2 only) | `cast_opened`, 1.0 |

**Not built here:** the ring break parts. CreatureActor keys `break_parts` by the charge skill a part silences, and
validate_creatures rejects unknown skills, so the parts wait for combat's skill ids (M4-A2P-022). A `broken` variant of
each ring's four lamps (dark glass, slack gimbals) costs about 1.4-4.8k triangles against the 1.3k left in the budget.
That is a budget call for the art lead when M4-A2P-022 lands.

## Own VFX (M4-A2P-058)

In the battle scene (`AmbientVfx`, CreatureAmbientVfx; data `game/data/creatures/creature_vfx.json`).

- **The lamps.** A soft `glimmer_bound` halo on each of the twelve lamps (on its gimbal bone, 0.6 m) and a larger one
  on the core (1.5 m, seen once the rings open), plus one dim `glimmer_bound` OmniLight3D in the core (0.6, 2.4 m).
  **Steady: no flicker** (colour script rule 2: bound light never flickers; the task's "flicker" is void, as the
  Ram's ice is). Never gold.
- **The KO.** From 0.3 s into the KO, over 1.8 s, the halos, the core light and the lamps' own glow (this instance's
  copies of the `glass` and `core` materials, `emission_energy` to 0) go dark. At 0.7 s twelve motes leave the core
  through its crack (`vfx_phase`), out from under the hood and up, blending `glimmer_bound` to `glimmer_lift`
  (rule 1's release; the act outline's "a small upward lift"); at 2.4 s a little cold dust lifts off the floor as it
  settles on its knees.
- **Viewed** (lavapipe, `lowlight_engine_hall` at enemy slot 0; battle camera and close): the halos are a quiet bloom
  round each lamp; at the KO the glass goes pale salt-glass and the motes rise past the hood's rim.
