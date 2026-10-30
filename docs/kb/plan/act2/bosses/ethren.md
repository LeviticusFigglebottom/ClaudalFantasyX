---
draft: pre-gate
adr: 0203
vowbound: ethren
element: glimmer
chapter: 13
owner: creatures-b
---
# Ethren, the Level Saint (`ethren`), Glimmer Vowbound: design sheet for Act II (draft: pre-gate)

**Built** (M3-CRE-644; final pass M4-CRB-008, 2026-10-30): 15,546 triangles, 29 bones (the two anchors added), 16
clips, seven slots; the gold measured at 0.27–1.35% of the frame before the pass's thin panel rims (inside the 5%
budget); the Act III held form with
`release` (M3-CRE-647). [Art sheet](../../../art/creatures/vowbound/ethren.md). **Built in M4-CRB-008:** the anchors,
the `stop` and `ward` clips, every clip from idle's first frame, the contacts. **Missing:** the `vowbound.json` row
and skills (M4-A2P-024), then `clip_by_skill` (the map is below); the summon and bind cinematics; Still Water's stop
(VFX and the battle's own stop); the `ethren_bound` and `ethren_summon` stings.

**Who:** Corran Ysel, the 60th Cantor, an Ansedran Tender and Ysolde's husband (patient, funny, a terrible cook). The
Order's showpiece Saint in the Sanctum of the Level (Ch13). **The Order's ideal made literal: beautiful and
impersonal.** The plain copper ring on his left hand is the only human thing about him and the only part that doesn't
shine.

**ADR 0015 guard:** the Sanctum's basin is a lit mirror, never ice. Nothing about him is frozen; stillness is shown by
not moving.

## 1. Silhouette

- 3.0 m to the halo's top, hovering 0.2 m. The one shape: **a closed four-leaf screen of lacquer wings behind a veiled
  figure with a bowl-halo**. At rest the wings are folded, so the HUD's right edge stays clear; they fan to 3.6 m only
  in `ready` (a little), `cast`, `special` and `victory`.
- **Facing:** `yaw_deg` −90; from the default camera (his left side) the folded wings read as two broad leaves, never an
  edge (as built). His rest pose holds the hands level at the waist, so the ring is on top of the near hand.
- **Stillness is the read:** his `idle` moves 1 cm. He is the most still thing on any field.

## 2. Materials (as built)

`lacquer` `lacquer_black`; `lacquer_red` `lacquer_red_deep`; `gold` `gold_leaf` on edges only; `seam` and `halo`
`glimmer_bound` 1.2, steady (the light is **inside** the shell and shows only at the seams and the halo); `veil`
`gauze_white` with a faint 0.2 behind; `ring` `laterite` toward `tortoiseshell`, rough 0.8, **no emission**. His seams
glow exactly like the Lit Age machines (the flat-engine, the Lamp Engine). That is the Act II truth in plain sight, and
nobody says it.

## 3. Rig

As built (29 bones; `veil` and `halo` on their own bones so cinematics can drop the veil in Ch20). **Built
(unweighted, M4-CRB-008):** `vfx_core` (the breastplate's split, y 1.76, on `spine_2`), `vfx_keepsake` (the ring, on
`finger_l1`, so it rides the hand in `stop` and `release`).

## 4. Move list *(skill ids proposed; Combat coins the ward names, never the series' spell names)*

| Skill (id) | Clip | Wind-up → contact (length) | What moves | Target | VFX and camera |
|---|---|---|---|---|---|
| rise | `rise` (built) | — (2.6 s) | from kneeling, wings closed, he stands | — | summon shot, full and short |
| idle | `idle`, `idle_b` (built) | — | 1 cm; `idle_b` a degree in the hands | — | — |
| ready | `ready` (built) | — (1.4 s) | the wings fan a little, hands lift level | — | — |
| `attack` | `attack` (built) | 0.0–0.55 s: the right hand rises palm out (0.32 s) and holds → 0.55 s (1.2 s) | a downward press, no weapon | one foe | — |
| `level_hand` *(proposed)* | `cast` (built) | 0.0–0.8 s: both hands swing out level, palms down; the wings part → 0.8 s (1.6 s) | as if smoothing water flat | one foe: Glimmer, Slow | the foe's outline goes still for a beat |
| `hold_the_hour` *(proposed)* | `stop` (built) | 0.0–0.45 s: the ringed left hand comes out, palm toward the foe; held perfectly still 0.45–0.7 s → closes, 0.9 s (1.6 s) | nothing moves but the hand closing | one foe: Stop | the foe's idle freezes (presentation) |
| `lacquer_screen` *(proposed)* | `ward` (built) | 0.0–0.3 s: the hands draw in; 0.3–0.6 s: the wings swing out and forward round the party's side → arms open, 0.8 s (1.6 s) | a lacquer screen | all allies: wards (`protect`, `shell` rules) | a pale gold-edged pane at each ally |
| `still_water` (Swell) | `special` (built) | 0.0–1.45 s: wings flung open, hands raised → 1.45 s, held to 2.05 s (2.4 s) | hands pressed down | all foes: Glimmer, and the field stops | everything on the field stops at contact (VFX and the battle's own stop) |
| defend | `defend` (built) | — | wings turned edge-forward round his sides | — | — |
| hit | `hit`, `hit_b` (built) | peak 0.1 s | a small stiff recoil; the veil never moves | — | — |
| KO | `ko` (built) | — (1.8 s) | he kneels (the bells telescope), the halo tips | — | — |
| dismiss / victory | built | — | kneels / wings fully open, then utterly still | — | — |

## 5. Phases

None as an ally. Every clip is played from `idle`'s first frame (built, M4-CRB-008). The veil-fall and Corran's face
are Act III (Ch20), with the characters track.

**The clip map** (M4-A2P-024 pastes it into `ethren` in creatures.json once the skills are in skills.json; the
validator rejects unknown skill ids before that). Contacts are already in creatures.json on `ethren` and
`ethren_held`: attack 0.55, cast 0.8, stop 0.9, ward 0.8, special 1.45.

```json
"clip_by_skill": {"level_hand": "cast", "hold_the_hour": "stop", "lacquer_screen": "ward", "still_water": "special"}
```

## 6. Where he is seen

- **Battle:** the Vowbound slot. In a bright arena the gold edges carry him; in the dark ones (`bridal_barge_night`) the
  seams and halo do.
- **Bind cinematic (Ch13 C4):** the Sanctum's still basin lit from beneath by a light that never moves; Ysolde before
  Corran, a Cantor beside her. The basin needs the still-mirror look (M4-A2P-047). Kerrid is never in the Sanctum.

## Balance, engine, owners

- **Balance:** bound from Ch13 (no Ch13 fights), so he first counts in Ch14's suites.
- **Engine:** Stop and Slow (statuses exist); Still Water's whole-field stop (check: a field-wide delay, or Stop on all
  foes).
- **Owners:** combat (row, skills, ward names); creatures-b (anchors, `stop`, `ward`); battle-presentation (the freeze
  read); rendering (the mirror); audio (stings).

## Open questions (answered: ADR 0204, 2026-10-30; the drafts stand unless marked)

1. Still Water: Stop on every foe, or a big delay for everyone but the party? Draft: Stop on every foe for one turn,
   so the timeline shows it plainly.
2. Echo check: Glimmer at the holy city is our special element, and the Saint is made of what the Order forbids. Keep
   every ward name ours (no tiered or series names).
