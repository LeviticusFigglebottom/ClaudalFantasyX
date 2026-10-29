# The Ending (E1–E7): Grade Notes

Owner: Environment Artist (M3-ENV-729). Lighting review: Rendering. Staging: Cinematics.
- **Story:** [act3_ending.md](../../story/beats/act3_ending.md) E1–E7 and §0 (the light grammar).
- **Grades:** [color script](../color_script.md) `ending_unbinding`, `ending_dock`, `post_credits`.
- **Generator:** `assets_src/environments/kits/haluna/ending_grades.py` writes
  `assets/environments/zones/ending/`: one Environment per frame, three LUTs and `ending_grades.json` (the key, rim,
  lamp and sea-glow rows a stager reads).

## 1. `ending_unbinding` (E1–E5, the Kite over the open sea)
- **No moon and no lamps.** The Kite's lamps are dark from H09. The key row (`#FFDCBF` 0.8) is the leaving person's
  rising motes, placed per scene by the stager above and in front of the face; the rim `#FFE9B8` 1.2 likewise.
- **The sea-glow steps** E1 0.15 → E2 0.11 → E3 0.08 → E4 0.07 → E5 0.06 (held), eased through the rests; the table
  is in `ending_grades.json` (`sea_glow_steps`).
- **The sky:** `#050A14` over `#0B1630`, a thin star field; fog `#0B1630` 0.004; exposure 1.15; `lut_ending_lift`
  (the navy toe, the warm gold only in the highlights, so the motes carry all the warmth).
- **The kit:** the Kite (M3-ENV-725) is the set. Its lamps dark is a material swap on its lamp surfaces (Cinematics').

## 2. `ending_dock` (E6, the final image)
- **Starlight only:** key `#D2DFFF` 0.25 from high behind the camera, fill `#0B1630` 0.1, rim `#DCE6FF` 0.3; no moon
  disc, no fog; a dense star field (`star_density` 0.2); exposure 1.2; `lut_ending_dock` (saturation ×0.8).
- **Sea-glow 0.0**, the first and only frame where it is. The mirror (roughness 0.02, SSR plus planar) is a per-shot
  water setting, the stager's.
- **The set** is Haluna's H10 dock with the camera turned out to sea. The ending variant of the zone is slice-polish's
  (`game/levels/ch02/**`); this Environment is what it swaps to.

## 3. `post_credits` (E7, Oruvel rebuilt)
- **Blue hour:** sky `#1A2E58` over `#6E7FA8`, the sun 6° under the east horizon (no disc), the directional row a
  cool `#9DB4D9` 0.4 sky light; fill `#3A5A8A` 0.35; fog `#3A4A6A` 0.006; exposure 1.05; `lut_post_credits`.
- **The only warm source** is the one oil lamp lit with Mother Kell's wick: the `lamp` row, `#FFAE67` 1.4, an
  OmniLight the stager places at the wick. No glimmer anywhere.
- **The set** is Oruvel's raft-town rebuilt (M3-ENV-730; oruvel.md §7): the Oruvel layout's `states.rebuilt`, with
  `first_lamp` where the OmniLight goes.

## Revisions
- 2026-10-27 (env-art, M3-ENV-729): first issue, the three grades.
