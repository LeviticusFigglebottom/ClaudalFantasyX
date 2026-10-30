---
draft: pre-gate
adr: 0203
boss: wakefin
chapter: 15
owner: creatures-b
---
# The Wakefin (`wakefin`), Ch15 boss: design sheet (draft: pre-gate)

**Built:** mesh, rig and 5 clips (`idle`, `attack`, `cast`, `hit`, `ko`; [art sheet](../../../art/creatures/act2/wakefin.md),
the open spine wounds of M3-CRE-635). Choreo has its intro (`boss`, 2.4 s), the blade-under gather and camera pressure
(M3-BPR-418). Music `wakefin` exists. **Missing:** the enemy row, skills, a clip per skill, `intro`, `ready`, `hit_b`,
`idle_b`, the breach rig, the anchors, the darkness-lit telegraphs (M4-A2P-062).

**What the fight teaches:** the dark doesn't hide the rules. It is fought on the drifting, unlamped bridal barge, with
Tobin's bier under the stern canopy. Its telegraphs are sounds and the sea-glow, and the timeline still shows every
turn (pillar 4). It is a quiet, cold fight before the act's emotional peak (Kerrid's confession, later that night).

## 1. Silhouette (at 12 m)

- **Most of the fight: the blade alone.** A tall swept dorsal blade, 2.2 m above the water, circling off the bow with a
  bright sea-glow wake. The one shape: **a fin cutting black water**. Nothing else in the game is that.
- **On a strike:** the whole fish breaches alongside, 6 m long, bill first. The body is wet lacquer black, so it only
  reads against the sea-glow it throws up. The breach must clear the rail by at least 1.2 m so its outline sits
  against the brighter water, not the dark deck.
- **Facing:** broadside to the camera when it circles (`stand_in.yaw_deg` 60); the blade's flat faces the camera on the
  pass nearest the party, never edge-on. An edge-on blade at 12 m is a stick.

## 2. Materials

| Slot | Swatch | Notes |
|---|---|---|
| `body` | `lacquer_black` → `abyss_navy` | wet, clearcoat 0.9 |
| `membrane` | `deep_teal_shadow` | lit from below by the sea-glow (subsurface tint, not emission) |
| `seam` | `sea_glow` emissive 0.12–0.3 | the flank seam; brightens along its path before a strike (the telegraph) |
| `wound` | `spawn_wound` | eight open seams along the spine at the waterline; show only on a breach |

**The arena has no other light** (`ch15`, moon 0.25, sea-glow 0.12, `lut_ch15_unlamped`, no lamps and no flames:
`test_bridal_barge` pins it). The Wakefin carries no light either, only the glow it stirs. The seam's brightening is
the one place it may exceed the arena's sea-glow, and only along its own path, for its own telegraph.

## 3. Rig

Spine chain of 10, the bill, the dorsal fin (3 bones), pectorals, tail lobes. **Add:** a **`breach` root bone** (the
fish's whole travel: circling, the dive and the breach run on it, so the mesh never has to move the spine to travel).
**Anchors (unweighted):** `vfx_wound` (the third spine wound), `vfx_core` (mid-body), `vfx_phase` (the fin's base).
**Water rule:** the water line is at −0.6 (the barge deck at 0). Most of the body is under it on purpose; the stage's
opaque-water floor hides it (the `creature_wakefin` shot). No part may pass through the barge's hull or deck: the
breach arcs over the rail, and the sweep stays above the deck by at least 0.3 m.

## 4. Move list

| Skill (id) | Clip | Wind-up → contact (length) | What moves | Target | VFX, sound and camera |
|---|---|---|---|---|---|
| intro | `intro` *(proposed)* | — (3.0 s) | the blade rises out of flat water far off, turns, and comes in on one long pass | — | `boss`, 2.4 s; a single long hiss of water |
| idle | `idle`, `idle_b` | — (4.0 s / 1.6 s) | it circles; `idle_b` the blade dips and rises | — | the wake |
| ready | `ready` *(proposed)* | — (1.6 s) | the blade slows and turns its flat to the party | — | — |
| `fin_cut` *(proposed)* | `attack` (built) | 0.0–0.8 s: the seam brightens along its path and the water hisses → 0.8 s (1.6 s) | it breaches along the rail; the blade sweeps across the deck | the front line (all foes in slots 0–1) | sound first, then glow; `boss_sweep` |
| `sound_dive` *(proposed, charge)* | `dive` *(proposed; the built `cast` retimed)* | — (1.4 s, holds) | the blade sinks and the water goes dark | **evasion up while dived, with a clear telegraph** (ADR 0204: not untargetable); the timeline shows its return | choreo blade-under gather; camera pressure |
| `wakefin_rise` *(proposed)* | `rise_strike` *(proposed)* | 0.0–0.7 s: a ring of sea-glow opens under one hero's side of the barge → 0.85 s (1.8 s) | it breaches straight up under the rail, bill first | one foe (the ring's hero) | the ring is the telegraph; `target` shot |
| `wake_wash` *(proposed)* | `wake_wash` *(proposed)* | 0.0–0.6 s: it turns hard away, tail lobes high → 0.75 s (1.6 s) | a tail slap sends its wake over the deck | all foes: delay | water over the deck, never over the bier |
| `bill_strike` *(proposed, phase 2)* | `bill_strike_close` *(proposed)* | 0.0–0.55 s: it rears at the bow, bill raised → 0.7 s (1.4 s) | a stab over the bow | one foe | `boss_blow` |
| hit | `hit`, `hit_b` *(hit_b proposed)* | peak 0.1 s | the fin jerks, the body rolls | — | — |
| phase `close_circle` *(proposed)* | `phase_close` *(proposed)* (2.0 s) | — | it rams the hull once (the barge rocks), then circles tight | — | `vfx_phase`; the barge's rock is staging (battle-presentation) |
| KO | `ko_close` *(proposed)* | — (3.0 s) | it rolls belly-up and drifts away, the wake fading | — | the sea goes quiet |

## 5. Phase change *(proposed: the plan names none)*

- **Trigger:** 50% HP.
- **Clip:** `phase_close`, ending on `idle_close`.
- **Stance:** a tighter circle, half the radius, the blade torn at the tip. The `clips` map covers `attack`, `dive`,
  `rise_strike`, `wake_wash`, `hit`, `hit_b` and `ready`.
- **What the player learns:** it is closer, so it comes faster (camera pressure one step), and it adds the bow stab.
  The ring of sea-glow still marks every rise.

## 6. Arena read (`bridal_barge_night`)

- **Light:** moonlight 0.25 and sea-glow 0.12 only. **No lamp, no flame.**
- **Placement:** the `BossAnchor` (−10, −0.6, −1.5) off the bow. The deck runs along X, the bow toward the enemy side.
- **Must never happen:** the breach or the sweep covering a party slot when it isn't the target; any splash or wash
  VFX over the bier or the stern canopy (it is Tobin's); the blade leaving frame during a telegraph.
- **Hazard:** none from the barge. The dark is the challenge, and it must never hide what the timeline should show.
- **Camera:** `boss` intro, `boss_sweep` for the cut, and the pressure close-in by turn.

## Balance, engine, owners

- **Curve:** Act II boss. **Role answer:** Liss or Rhen ready a strike for the surface turn; Asha heals the wash.
- **Engine:** an evasion-up status while dived (existing status data; ADR 0204, not untargetable); darkness-lit telegraphs (presentation gap,
  M4-A2P-062).
- **Owners:** creatures-b (the breach bone, new clips, anchors); combat (row, skills, AI, suite); battle-presentation
  (glow and sound telegraphs, the barge rock); rendering (the seam brightening, the glow ring); audio (stems exist;
  the hiss and the wake).

## Open questions (answered: ADR 0204, 2026-10-30; the drafts stand unless marked)

1. **Echo check, to confirm.** A fight against a great fin from a boat's deck is a beat in the inspiring game (an
   early fight on a ship against the fin of something colossal). Ours differs in form and stage: it is one whole
   animal (a sailfish, its body shown on every breach), not a part of a giant; there are **no adds landing on the deck**;
   the fin is never a separate target; and the barge is unlamped and drifting at night. The draft keeps it so. The Lead
   should confirm, and nothing should ever add deck adds or a "fin" part to this fight.
2. ~~Should `sound_dive` use the full untargetable rule, or only an evasion boost while dived?~~ **Answered (ADR 0204):
   evasion up while dived, with a clear telegraph; never untargetable.**
