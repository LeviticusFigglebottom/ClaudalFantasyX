# 0024 — Asha's hair, lash and brow shading values depart from asha.md §5

- **Status:** proposed (Art and Rendering to confirm on the GPU 2× High capture, M1-QA-05c)
- **Date:** 2026-10-23
- **Roles affected:** Character, Rendering, Art
- **Author role:** Character Artist (M1-CHR-10)

## Context
asha.md §5 specifies Asha's hair as black and lists the shading values: base `hair_black` #201A16, a primary highlight with exponent 120 and tint #E8D8C8 at 0.35, and a secondary with tint #8A5A3A at 0.5. Since M1-CHR-07 the asset has departed from the sheet's exponent (400). The review-sweep-L entry on M1-CHR-09 asked for the spec and the asset to be reconciled (S2). The same review found that the hair reads **auburn**, not black (asha.md:121).

The M1-CHR-10 diagnosis, on lavapipe at the asha stage's lighting:
- With every lobe off, the crown still rendered at sRGB 36/16/7 (R:B 5.4). A neutral grey under the same key reads R:B 2.0.
- The cause is the base colour. #201A16 is a warm brown-black. Under the stage's orange key and rim (1.0/0.72/0.48 and 0.95/0.65/0.29), it takes the light's hue almost unfiltered.
- The hair's root and layer occlusion (0.5 and 0.45) remove most of the cool sky fill, which is the only blue in the scene. Lit hair is therefore the key's colour times a warm albedo.
- The highlights add gold on top: #E8D8C8 under an orange key. The secondary and the transmission add #8A5A3A, the colour of light through *brown* hair. M1-RND-04 proposed #8A5A3A on a test bust, and character_shading.md records that it made black sheets read bronze.

## Options
1. **Keep #201A16 and change the stage lights.** Rejected. The stage is the reference for every asha_* shot, and in-game keys are warm too (SPEC §7.1: warm, high-key daylight).
2. **Change the shader** so that hair colour ignores the light's hue. Rejected. That isn't physical, and it would affect every hero.
3. **A neutral, slightly cool near-black base, with tints that suit black hair** (chosen). The value stays as dark as #201A16 (its luminance is a little lower). The hue is neutral-cool, so the warm key makes it warm-dark, not auburn.

## Decision
Asha's hair, lashes and brows use these values. They are written in `assets_src/characters/asha/write_materials.py` (`HAIR_BLACK` and the `HAIR_*` tints). The shader is unchanged.

| | asha.md §5 | As built (CHR-10) |
|---|---|---|
| Base colour (`col_root`, `col_tip`) | #201A16 | **#141417** (`Color(0.08, 0.08, 0.09)`) |
| Primary tint / intensity / exponent | #E8D8C8 / 0.35 / 120 | **`Color(0.76, 0.85, 1.0)` / 0.45 / 400** (exponent since CHR-07) |
| Per-strand highlight shift jitter | (shader 0.1) | **0.3** (the shader's cap) |
| Secondary tint / intensity | #8A5A3A / 0.5 | **`Color(0.30, 0.27, 0.25)` / 0.12** |
| Transmission tint / strength | #8A5A3A / (shader 1.5) | **`Color(0.29, 0.23, 0.19)` / 0.5** |
| Root / layer occlusion | (shader 0.5 / 0.45) | **0.7 / 0.75** |
| Scalp underpaint (head albedo) | #201A16 | **#16161A**, clamped by the albedo floor #1D1916 |

Lashes and brows take the same base colour, with nearly no environment specular (0.03 and 0.05).

The sheet's *intent* is kept: black hair, and a primary that reads as "a thin, cool-white ribbon" (never a broad sheen). Its numbers are not kept, because under a warm key they produce auburn and gold.

## Consequences
- Measured on `asha_face_neutral`: the crown's R:B goes from 5.4 to 2.6 in shadow and from 7.6 to 3.0 where lit. The neutral grey reads 2.0, so it is still slightly warm. That's expected under this key, and it reads near-black.
- **Watch:**
  1. Under a cool or neutral key (night, overcast, Act II), the cool tint may read blue-black. Check it in the first non-warm scene.
  2. The GPU 2× High capture (M1-QA-05c) is the final judge.
  3. Rhen's copper hair (`col_tip` #A65A2A) is not affected.
- **Art:** amend asha.md §5 to these values, or overturn this ADR with another. Until then, this table is the reference.
