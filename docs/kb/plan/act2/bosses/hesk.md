---
draft: pre-gate
adr: 0203
vowbound: hesk
element: holy
chapter: 12
owner: creatures-b
---
# Hesk, the Cord-Keeper (`hesk`), Holy Vowbound: design sheet for Act II (draft: pre-gate)

**Built** (M3-CRE-643, in review): 13,602 triangles, 25 bones, 13 clips (`idle`, `idle_b`, `ready`, `attack`, `cast`,
`hit`, `hit_b`, `defend`, `ko`, `victory`, `rise`, `dismiss`, `special`), six slots; the Act III held form with
`release` (M3-CRE-647). [Art sheet](../../../art/creatures/vowbound/hesk.md). **Missing:** the `vowbound.json` row and
skills (M4-A2P-024), `clip_by_skill`, the anchors, a `cleanse` clip, the summon and bind cinematics, Pass-Cord's line of
knots (VFX), the `hesk_bound` and `hesk_summon` stings.

**Who:** Ama Quillo, the 47th Cantor, an Ullari keth-reader and a believer who started counting. Bound at Cloudloom, the
open-roofed weaving-hall on the summit (Ch12). **A reader, steady and plain**: a high-pass condor, the bird that lifts
the dead off the passes. Her keth wings carry real numbers (47, 7; her ledger), so Ysolde can read them.

**ADR 0015 guard:** Cloudloom is white stone under open sky. **No ice, frost or glacier in the hall or on her.** The
whiteness is `gauze_white` cord and high-pass daylight, not frost.

## 1. Silhouette

- Perched, wings half-folded and mantled: 2.45 m across, 2.34 m tall; the full 4.2 m span only in `special` and
  `victory`. The one shape: **a condor's bare head and ruff over a mantle of knotted cords**.
- **Facing:** `yaw_deg` −90 on the Vowbound slot; the near wing's knots face the camera. The keth bundle hangs from her
  left talon to 0.1 m over the water.
- **Framing (as built):** inside the default camera's safe frame in every clip (the tightest is the KO's fall, +0.001
  right); the summon shot cuts her feet under the HUD band. A new `cleanse` clip must not open past the `cast` span
  (4.03 m), or it crosses the right edge.

## 2. Materials (as built)

`plumage` `overcast_slate` → `storm_slate`; `cord` and `ruff` `gauze_white` with a `sand_cloth` strand, lit
`glimmer_bound` 1.2 (the mask 1.0 at the knots, 0.2 along the cord); `head` `bone`; `eye` `glimmer_bound` 0.55;
`bundle` `sand_cloth` and `faded_teal_cloth`, **never lit**. Dry. **The knots are what shines**: the truth held up to be
read. Holy as `glimmer_bound` is the art sheet's default; a white-gold holy light would be a palette ADR.

## 3. Rig

As built (25 bones). **Add (unweighted):** `vfx_core` (the breast, on `body`), `vfx_keepsake` (the keth bundle, on
`bundle_1`). Grounded: the right talon is solved onto the water at every frame; only `release` leaves it.

## 4. Move list *(skill ids proposed)*

| Skill (id) | Clip | Wind-up → contact (length) | What moves | Target | VFX and camera |
|---|---|---|---|---|---|
| rise | `rise` (built) | — (2.6 s) | from hunched and folded she opens and stands | — | summon shot, full and short |
| idle | `idle`, `idle_b` (built) | — | weight from talon to talon, cords sway | — | — |
| ready | `ready` (built) | — (1.4 s) | wings half open, cords lift, head raised | — | — |
| `attack` | `attack` (built) | 0.0–0.55 s: one wing drawn back → 0.55 s (1.2 s) | a wing-buffet, cords lashing | one foe | — |
| `knot_light` *(proposed)* | `cast` (built) | 0.0–0.8 s: wings spread, knots brighten in order from the hand outward → 0.8 s (1.6 s) | held wide | one foe: Holy | the knots read in sequence like a count |
| `cord_lift` *(proposed)* | `cleanse` *(proposed)* | 0.0–0.7 s: wings brought forward round the party's side → 0.9 s (1.6 s) | a lifting sweep | all allies: remove statuses | statuses lift off as pale threads drawn up |
| `hesk_mending` *(proposed)* | `mending` *(proposed)* | 0.0–0.6 s: she bows her head over the bundle → 0.8 s (1.4 s) | the bundle raised in the talon | all allies: Regen | one knot of light settles on each ally |
| `pass_cord` (Swell) | `special` (built) | 0.0–1.45 s: full 4.2 m span, then the downstroke → 1.45 s (2.4 s) | both wings sweep down and forward | all foes | a line of shining knots across the field (VFX); `finisher` |
| defend | `defend` (built) | — | wings mantled forward | — | — |
| hit | `hit`, `hit_b` (built) | peak 0.1 s | a flinch, head drawn into the ruff | — | — |
| KO | `ko` (built) | — (1.8 s) | she settles onto the water, wings flat, head bowed | — | — |
| dismiss / victory | built | — | fold and hunch / full span, cords raised | — | — |

## 5. Phases

None as an ally. Every clip from `idle`'s first frame. The held form (`release`) is Act III's.

## 6. Where she is seen

- **Battle:** the Vowbound slot. Her knots are her read, and they must hold in dark arenas too (`bridal_barge_night`
  at moon 0.25): the knots at 1.2 against sea-glow 0.12 is fine; the slate body will go nearly black, which is right.
- **Bind cinematic (Ch12 C3):** Cloudloom at noon, the keth's shadows written on white stone; Ysolde reads Ama's keth
  and lies. Her `rise` and `idle` serve; the shadows are environment and rendering.

## Balance, engine, owners

- **Balance:** bound from Ch12; in the suites after the Ram (she is bound after it).
- **Engine:** party cleanse (check the existing `cleanses` key), Regen (exists).
- **Owners:** combat (row, skills); creatures-b (anchors, `cleanse`, `mending`); battle-presentation (summons, the knot
  line); audio (stings).

## Open questions (answered: ADR 0204, 2026-10-30; the drafts stand unless marked)

1. Is `hesk_mending` a separate skill, or does `cord_lift` carry the Regen too? Draft: separate, so each gets its own
   clip and the player sees two different gestures.
2. Echo check: Holy fifth, in a mountain hall, with a believer's arithmetic as its beat. No pairing from the inspiring
   game's stretch survives (ADR 0015).
