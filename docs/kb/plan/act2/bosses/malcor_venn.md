---
draft: pre-gate
adr: 0203
boss: malcor_venn
part: flat_engine
chapter: 14
owner: characters (Venn); creatures-b (flat-engine)
---
# Warden Malcor Venn and the flat-engine, Ch14 boss: design sheet (draft: pre-gate)

**Model and rig: the characters track's** (a person; M4-A2P-051). This sheet still writes his design for the fight.
The **flat-engine** on his barge is creatures-b's: built ([flat_engine.md](../../../art/creatures/act2/flat_engine.md):
mesh, rig, `whole`/`broken` meshes, 5 clips). **Nothing else exists:** no enemy row, music (`malcor_venn`, 2 stems, is
a gap), encounter or clips.

**Who, in the fight:** one of the five Wardens of the Conclave. He fights on the night of the wedding trap, on
Ansedra's lagoon, as **a living-seeming man**. **Nothing about what he is may be revealed** (plan §2a): no motes, no
held light, no wound that fails to bleed or a fall that he shrugs off. He is old, steady and very sure. The fight ends
with him **left standing on his crippled barge** in the first ripples the city has seen in four hundred years.

**What the fight teaches:** a part only one hero can break. While the engine runs, the water is pressed flat and the
timeline slows for the party. Liss breaks it, the water moves again, and the barges drift together.

## 1. Silhouette (at 12 m; phase 1 is farther)

- **Phase 1:** he is on his own barge, about 7 m beyond the enemy line, so the **barge and the engine are the big
  shape**: a black lacquer hull with a dark drum on the stern and a fan of eight 3 m paddles flat on the water. Venn
  stands at the near rail. His read is **a tall pale figure against black lacquer**: a long Warden's coat in
  `order_marble` white, a tall stiff collar, and a brass-shod **Warden's rod** about 2.6 m long, held upright (the
  Level's emblem at its head). The rod makes him readable at that distance; without it he is a man-sized speck.
- **Phase 2:** he crosses to the bridal barge's enemy seat, so he is at normal boss distance. His figure is about 1.9 m
  with the rod. He stands square to the camera, rod across his body or held level. He never turns his back.
- **The flat-engine** faces the camera with its window (a steady teal light, its only light) and its paddle fan.

## 2. Materials

| Slot (characters' kit) | Swatch | Notes |
|---|---|---|
| `coat` | `order_marble`, `gauze_white` lining | dry, heavy cloth; the hem wet and dark after he boards |
| `trim` | `gold_leaf` (edges only, ≤ 5% of frame) and `lacquer_red_deep` bands | the wedding's dress |
| `skin` | an old man's skin set (characters' palette) | **normal sss and blush**, never grey or waxen |
| `rod` | `brass` shaft, `bronze_patina` at the shoe; the head `gold_leaf` | a surveyor's level staff made into a mace of office |
| engine `drum` / `window` / `paddle` / `hinge` | `lacquer_black` + `brass` / `salt_glass` with `glimmer_bound` / `timber_weathered` wet / `spawn_wound` | as built |

Arena light: `ch14` dusk, sun 5°, key `#FFAA5F` 1.4, `lut_ch14_wedding` (reds pushed toward blood, shadows navy). No
lamp on either barge. Venn carries no light; the engine's window is the only bound light in the fight, and that is
the story's quiet point (the Order's own barge runs on what it forbids). Nobody says so.

## 3. Rig

**Venn:** the characters' human rig, plus a `rod` prop bone in the right hand (swappable to the left for the level
guard), a `coat_*` cloth chain of 3 at the hem, and unweighted `vfx_wound` (none glows; it marks where hits land, on
the chest), `vfx_core` (the sternum), `vfx_phase` (the rod's head). **Grounding:** feet planted by IK on a deck that
rocks (the barge's rock is staging): the feet follow the deck, never slide. **The crossing:** a `board` root offset
(about 4 m along −z) for the phase clip, so he steps off his rail onto a gangplank the grapnel line drew in.
**Engine:** drum, chimney, eight paddle hinges, plus `vfx_core` (the window) and `vfx_phase` (the drum's seam).

## 4. Move list

| Skill (id) | Clip | Wind-up → contact (length) | What moves | Target | VFX and camera |
|---|---|---|---|---|---|
| intro | `intro` *(proposed)* | — (2.6 s) | he plants the rod on his deck; the engine's paddles press down together | — | `boss`, on the `the_engine` hint |
| idle | `idle`, `idle_b` | — (4.0 s / 1.6 s) | he stands still, rod upright; `idle_b` he shifts the rod a hand's width | — | — |
| ready | `ready` *(proposed)* | — (1.4 s) | the rod comes down to level | — | — |
| `flat_pulse` *(proposed; the engine's)* | engine `cast` (built, "the stilling") | 0.0–0.7 s: every paddle lifts a little → 0.8 s (1.6 s) | all paddles press down; the window holds bright | the party: Slow (`field_rules`); a timeline `entries` row (role `tide`) shows the pulse coming | the water pressed flat round the bridal barge (the still-mirror look) |
| `venn_sentence` *(proposed)* | `sentence` *(proposed)* | 0.0–0.6 s: he raises the rod head high → 0.75 s (1.6 s) | he lowers it level at one hero | one foe: magical damage, `magic_break` | a cold line across the water, no glimmer |
| `grapnel_line` *(proposed)* | `grapnel` *(proposed)* | 0.0–0.55 s: he draws back, the line coiled → 0.7 s (1.4 s) | a thrown grapnel bites the bridal barge's rail | one foe: damage and delay; pulls the barges closer (the board's set-up) | the line stays taut across the gap until phase 2 |
| *(phase 2)* `rod_sweep` *(proposed)* | `rod_sweep` *(proposed)* | 0.0–0.6 s: the rod swings back over the shoulder → 0.75 s (1.5 s) | a wide level sweep | the front two foes | `boss_sweep` |
| *(phase 2)* `still_hand` *(proposed)* | `still_hand` *(proposed)* | 0.0–0.6 s: he steps in, left palm raised → 0.7 s (1.4 s) | the palm pressed down on a hero's shoulder | one foe: a long delay (the Order's gesture) | `target` shot |
| *(phase 2)* `level_guard` *(proposed)* | `level_guard` *(proposed)* | — (1.2 s) | the rod held level across his chest | self: `protect`, counters the next melee | — |
| hit | `hit`, `hit_b` *(proposed)* | peak 0.1 s | an old man's flinch; a step back; he recovers his footing | — | a hit spark, never motes |
| break the engine | engine `ko` (built: the break) | — | the seam splits, the window goes dark, the paddles fall slack | Liss's skill only (M4-A2P-023) | the first ripple ring (M4-A2P-047) |
| phase `boarded` *(proposed)* | `board` *(proposed)* (2.4 s) | — | he walks the gangplank and steps onto the bridal barge, unhurried | — | the gangplank is staging; the city's windows light behind him |
| end | `left_standing` *(proposed)* | — (3.0 s) | at the yield he steps back across, the line is cut, and he stands on his crippled barge as they part | — | `yield_at_hp_pct` (the Inquisitor's precedent): no KO, no fall |

## 5. Phase change

- **Trigger:** the engine's break (the part), not his HP. If the party drives him to 50% first, he calls for the
  board anyway (`boarded` at 50% *or* on the break, whichever comes first), and the engine keeps pulsing until Liss
  breaks it.
- **Clip:** `board`, ending on `idle_boarded` *(proposed)*: rod held level, feet wider on the rocking deck.
- **Stance map:** every phase-2 clip starts from `idle_boarded`; `hit`, `hit_b` and `ready` get `_boarded` versions.
- **What the player learns:** the slow was the engine, not him. Liss broke it. He is just a man with a rod now, and he
  is still dangerous.

## 6. Arena read (`ansedra_lagoon_escape`)

- **Light:** `ch14` dusk (2,800 K), contrast 0.70, the game's peak.
- **Placement:** phase 1 on the `BossAnchor` on the pursuit barge's deck (−4.5, −0.2, −7.0); the engine on its poop.
  Phase 2 on enemy slot 1 on the bridal barge.
- **Must never happen:** the grapnel line or the gangplank crossing the camera ray to a party slot; Venn's figure
  hidden behind the engine's chimney from the default camera; any cutaway showing him unhurt by a hit.
- **Hazard:** the flat pulse (party Slow) while the engine runs.
- **Camera:** `boss` intro on `the_engine`; the break gets a short hold on the window going dark and the first ripple;
  `the_city_watching` for the end.
- **Rules:** `scripted` (no Escape). Liss is `locked_active` in phase 1, or carries a lent skill (set_piece_battles §1).

## Balance, engine, owners

- **Curve:** Act II boss. The step-hold before it (an objective battle) is on the set-piece curve.
- **Engine (§4.6):** a part only one hero breaks (gap, M4-A2P-023); timeline-slow field (`field_rules` exists); a tide
  `entries` row for the pulse; yield (exists).
- **Owners:** characters (Venn's model, rig, clips, face); creatures-b (the engine's anchors and a retimed `cast`);
  combat (rows, AI, Liss's break skill, suite); battle-presentation (the board, the barge rock, the end); rendering (the
  pressed-flat water and the ripples); audio (M4-A2P-092); narrative (his lines, if any; he names the heresy, not
  himself).

## Open questions

1. Does Liss carry the break as her own skill (Ch14 kit) or as a lent set-piece skill? Draft: a lent skill, so her
   Act III kit doesn't carry a one-fight move.
2. Echo check: a church elder fought on the wedding night is close to the inspiring game's shape. Plan §2a moves it: the
   fight is on open water during the escape, nothing is revealed, he is not killed, and there is no aftermath trial.
   This draft keeps all four. The Lead reviews the staging (risk R4).
