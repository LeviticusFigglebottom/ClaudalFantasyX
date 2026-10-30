---
draft: pre-gate
adr: 0203
boss: mangrove_drowner
chapter: 10
owner: creatures-b
---
# The Mangrove Drowner (`mangrove_drowner`), Ch10 boss: design sheet (draft: pre-gate)

**Built:** mesh, rig, `idle`, `attack`, `cast`, `hit`, `ko`, `phase_change`, `idle_risen`, `attack_risen`,
`cast_risen`, `hit_risen` (M3-CRE-622; [art sheet](../../../art/creatures/act2/mangrove_drowner.md), risen lean 48°
approved). Choreo has its intro (`boss_tall`, 2.2 s) and the `uprooted` moment (M3-BPR-418). Music `mangrove_drowner`,
2 stems. **M4-CRB-002 (the move pass, 2026-10-30):** every clip in §4 is built, with the planted roots held by IK, every
clip on its phase's idle first frame, the anchors, the snag roots' motes and their broken meshes, `contact` and the
phase `clips` map in creatures.json (art sheet "As built", with the clip map for combat). **Missing:** the
`enemies.json` row and the encounter, the skills, `clip_by_skill` and `break_parts` wired (combat; ready to paste), the
boss seat, and the VFX (the motes' lift, rising water).

**What the fight teaches:** a boss that holds the dead down. Breaking its roots frees motes that go **up**, the first
time the player sees what release looks like (a seed for the Letting and the farewell-tide). The pillar is beauty in
decline: a dead tree, still standing in the fen, that won't let go.

## 1. Silhouette (at 12 m, with the party in frame)

- **Rooted:** a pale dead trunk about 4.2 m tall over a lopsided tangle of roots, a black mass with cyan seams wedged
  low at its foot. The one shape a player recognises is **a dead tree standing in the water**. It stays vertical and
  never spreads into a spider (the M3-CRE-622 rules hold).
- **Risen:** a felled tree that walks: the trunk leans 48° toward the party on three uneven root-feet.
- **Facing:** `stand_in.yaw_deg` 90 turns the core's wound folds to the party. The bank-side root cluster (−x) reaches
  away from the party lane, so it never crosses the party's slots or the camera's ray to them.
- The two **snagged-mote roots** (the break parts) hang on the camera side, each with six pale lights, so the player
  can see what they are breaking.

## 2. Materials (creature-kit slots)

| Slot | Swatch | Notes |
|---|---|---|
| `bark` | `timber_weathered` drying to `bone` above 2.6 m | dry, rough 0.85 |
| `bark_wet` | `lacquer_black`, clearcoat 0.6 | below the waterline, wet |
| `barnacle` | `coral_stone_weathered` | bands at the waterline |
| `core` | `lacquer_black` → `abyss_navy` | wet, clearcoat 0.8 |
| `wound` | `spawn_wound` emissive | the seams down the folds (ADR 0151); dimmer while rooted, opens wider risen |
| `mote_snag` | `glimmer_held`, steady 1.0 | small beads held in the two break-part roots; never drifts until released |

The arena light is overcast dusk (`ch10`, key 0.9 at 2°, dense fog). The Drowner carries no light of its own except
the wound seams and the snagged motes. In the fog those are what the player reads first, and that is the point.

## 3. Rig

Core chain of 4; twelve roots of 3 (six become the three foot-pairs risen); `stump` (hidden after the phase) and its
splinters; one bone per aerial root. **Add (unweighted):** `vfx_wound` (the largest front fold, on `core_2`),
`vfx_core` (the core's centre of mass, on `core_1`), `vfx_phase` (the trunk's torn break at about 3 m, where the
splinters burst from). **Break-part bones:** `snag_root_a`, `snag_root_b` (two of the twelve, each carrying its motes'
mesh as `whole` and a torn, empty `broken` mesh). **Grounding:** y 0 is the water. The risen feet are planted by IK at
every frame; only `root_stamp_risen` lifts and plants a pair.

## 4. Move list

| Skill (id) | Clip | Wind-up → contact (length) | What moves | Target | VFX and camera (battle-presentation) |
|---|---|---|---|---|---|
| intro | `intro` *(proposed)* | — (2.6 s) | the core heaves up between the roots, the aerial roots swing, the motes sway; ends on `idle` | — | `boss_tall`, 2.2 s hold; fog parts a little |
| idle / fidget | `idle`, `idle_b` | — (4.0 s / 1.4 s) | roots flex with the tide; `idle_b` a root knuckles and resettles | — | — |
| ready | `ready` *(proposed)* | — (1.6 s loop) | the core rises 10 cm, two front roots lift off the mud | — | — |
| `drowner_haul` *(proposed)* | `attack` (built) | 0.0–0.7 s: the water draws toward it first, two roots reach → 0.7 s (1.4 s) | the two front roots reach along the water and haul back | one foe (`random_foe`), delays it | water-draw ripple line from the target to the core |
| `rising_water` *(proposed)* | `rising_water` *(proposed)* | 0.0–0.9 s: roots spread, wounds flare, the water starts up the roots → 1.0 s (2.0 s) | roots part, the core lifts; the water climbs | all foes; sets the `rising_water` field (Slow while it holds) | the field VFX (water up to the party's shins); `push` shot |
| `drowner_snag` *(proposed)* | `snag` *(proposed)* | 0.0–0.6 s: one root lifts high and hangs → 0.75 s (1.6 s) | one root drops and wraps a hero's legs | one foe: **Rooted** (no swap; M4-A2P-020) | the target's feet in the root; `target` shot |
| *(phase 2)* `drowner_haul` | `attack_risen` (built) | as above → 0.7 s | from the lean | one foe | as above |
| *(phase 2)* `root_stamp` *(proposed)* | `root_stamp_risen` *(proposed)* | 0.0–0.65 s: the trunk rocks back, the front pair lifts high → 0.8 s (1.8 s) | the front pair stamps; the trunk lurches | all foes | mud and water burst; `boss_blow` |
| *(phase 2)* `drink_the_fen` *(proposed)* | `cast_risen` (built, retimed) | 0.0–0.8 s: the roots dig in, the wounds pulse → 1.0 s (2.0 s) | the roots dig, the core swells | one foe: **drain** (M4-CMB-1001) | a dark draw from the target into the roots |
| *(phase 2)* `drowner_snag` | `snag_risen` *(proposed)* | as `snag` | from the lean | one foe | as above |
| hit | `hit`, `hit_b` *(hit_b proposed)*; risen `hit_risen`, `hit_b_risen` *(proposed)* | peak 0.1 s (0.6 s) | the cage shudders, the core recoils; `hit_b` rolls the other way, heavier | — | — |
| break a snag root | `snag_break` *(proposed, additive)* | — (0.8 s) | the root jerks and hangs slack | — | its six motes come loose **upward** (`glimmer_lift`); a 0.6 s hold on `the_dead_crown` hint |
| phase `uprooted` | `phase_change` (built, 2.2 s) | — | wrenches free, `stump` splinters off, the trunk tips, three clusters plant | — | choreo `uprooted` moment; `vfx_phase` splinter burst |
| KO | `ko_risen` *(proposed; maps the KO in phase 2)* | — (2.6 s) | the roots let go one by one, the trunk keels back, the mass slumps onto the water | — | every remaining mote lifts; the water's sinking VFX |

**As built (M4-CRB-002):** every clip above exists under the name in its row; `idle_b`, `ready`, `ready_risen`,
`hit_b_risen`, `snag_break` and `snag_break_risen` too, plus `rising_water_risen` so the field can be raised from either
phase. `snag_break` is a full clip from idle (not additive). **Clip map for combat** (paste into `clip_by_skill` once
the skills are in skills.json; the phase map sends each to its risen clip):

| Skill | Clip | Contact (s) | Phase 2 |
|---|---|---|---|
| `drowner_haul` | `attack` | 0.7 | `attack_risen` 0.7 |
| `rising_water` | `rising_water` | 1.0 | `rising_water_risen` 1.0 |
| `drowner_snag` | `snag` | 0.75 | `snag_risen` 0.75 |
| `root_stamp` | `root_stamp_risen` | 0.8 | phase 2 only |
| `drink_the_fen` | `cast` | 1.0 | `cast_risen` 1.0 (phase 2 only) |

## 5. Phase change

- **Trigger:** 50% HP (`at_hp_pct` 50).
- **Clip:** `phase_change` (2.2 s), ending on `idle_risen`'s first frame.
- **Stance:** the 48° lean on three root-feet. The phase `clips` map gains `snag` → `snag_risen`, `hit_b` →
  `hit_b_risen`, `ready` → `ready_risen` and `ko` → `ko_risen`, on top of the built three (built, M4-CRB-002, with
  `rising_water` → `rising_water_risen` and `snag_break` → `snag_break_risen`).
- **What the player learns:** the tree was the cage. Once it stands it hits everyone (`root_stamp`) and feeds
  (`drink_the_fen`), so a broken snag root, which weakens the haul, is worth more now.

## 6. Arena read (`ossa_fen_roots`)

- **Light:** `ch10` overcast dusk, `lut_ch10_fen` (greens to grey-teal; only the lifting motes keep full saturation).
- **Placement:** on the `BossAnchor` (−8.2, −0.15, −3.8), in the tannin water at the dead tree's foot. The party is on
  the mudbank's level floor.
- **Must never happen:** the bank-side roots or the leaning trunk crossing the party slots or the camera ray at 0.9 m;
  the trunk's top leaving the top of the frame in `boss_tall` (it may cut at the snapped top, as the art sheet says).
- **Hazard:** the `rising_water` field (data: `field_rules`, a per-turn Slow), with the water VFX climbing the shins.
- **Camera and seats:** `boss_tall` intro; a 0.6 s mote-lift hold on the snag-root break; `boss_blow` for the stamp.

## Balance, engine, owners

- **Curve:** Act II boss. **Role answer:** Ysolde breaks the snag roots (single-target magic), and Asha keeps the
  Rooted hero healed. Re-run on the Ch10 loadout (M4-A2P-019), with Pell in.
- **Engine (§4.6):** Rooted (gap, M4-A2P-020), drain (M4-CMB-1001, blocked), break parts wired to a skill (CreatureActor
  `break_parts` exists).
- **Owners:** creatures-b (new clips, anchors, snag-root parts); combat (row, skills, AI, suite); battle-presentation
  (mote lift and water field VFX staging); rendering (`glimmer_lift` look); audio (stems exist; SFX for snag and
  stamp); ui (bestiary, the part's broken state).

## Open questions (answered: ADR 0204, 2026-10-30; the drafts stand unless marked)

1. Does breaking a snag root lower the haul's power or remove the Rooted effect? Draft: it weakens the haul (as the art
   sheet says), and Rooted stays the snag's.
2. Echo check: a tree boss that roots the party is generic, not anyone's signature fight. The rising motes are ours.
   No change needed.
