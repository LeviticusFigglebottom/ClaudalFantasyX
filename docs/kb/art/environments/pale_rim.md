# The Pale Rim and the Drowned Choir (Ch16): Design Notes

Owner: Environment Artist (M3-ENV-722; the sheet first, then the kit). Lighting review: Rendering.
- **Story:** [act_outline Ch16](../../story/beats/act_outline.md); bible §5.10 and the Founding (§2).
- **Grade target:** [color script](../color_script.md) `ch16` (the Rim at noon; the Choir at moonrise,
  `lut_ch16_choir`).
- **Zones:** `ch16/pale_rim` and `ch16/drowned_choir`.
- **Kit:** in the Haluna kit as `drowned_choir.py`.
- **Arena:** `drowned_choir_ring` (Sefir's Abiding guard).

**The feeling in one line:** the edge of the world goes white; then the ring of colossal mouths at moonrise.

**What the place is** (bible §5.10):
- **The Pale Rim:** the southern edge of the known sea. Ankle-to-waist-deep water lies over white sand for days of
  travel, and the horizon goes white.
- **The Drowned Choir** stands at its end: a ring of colossal stone figures standing in the water, mouths open,
  round a sunken amphitheatre. This is where every Cantor ends. Kesh, the first heart, is bound in its stones, and
  the Eighth Verse's melody is hidden in them.

**The figures** (our original): **robed singers**, 24 m tall, in the Lamplighters' Lit Age white ceramic, weathered.
- **Pose:** each stands in the sea at the ring's edge, faces the centre, and tilts its head up 25° toward the sky,
  the mouth a deep open dark.
- **Form:** the robe falls straight to the water; the hands are folded flat at the breast.
- **Not heads:** they are singers, not idols. No crowns, no faces of gods, no script.
- **Their gaze:** they look past the amphitheatre, up.

**The amphitheatre** is a bowl:
- the singer's dais at its floor (dry, y 0);
- a flooded ring channel round the dais;
- six seat-tiers rising outward, broken in places, the lowest half-drowned.

## 0. Lighting

- **The Rim (`ch16`):** white overcast noon. Sun 70° / 180°, key `#E6EBFF` 2.2, fill `#E6EBF0` 1.0, exposure 0.70,
  S-curve 0.25, saturation ×0.7, `lut_ch16_rim`. Near-white, with no shadows; the horizon dissolves.
- **The Choir (moonrise):** the moon low in the east, `#D2DFFF` 0.35; fill `#2A3A4E` 0.25; the `pale_rim` water at
  night (deep `#2E4C50`); sea-glow 0.1; exposure 1.1; `lut_ch16_choir`: moonlit, stone faces cold, Kesh pale cyan
  (`glimmer_held`).

## 1. Kit pieces (metres; LOD0 / LOD1 triangle budgets)

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `choir_singer` | One colossal robed singer standing in the sea, head tilted up, mouth open; origin at its foot on the sand (−0.6) | 9 × 24 | 5k / 300 |
| `choir_amphitheatre` | (arena frame) The dais (dry, r 7.5, y 0), the flooded ring channel, six tiers rising to r 22 and +2.4, broken in places | 46 × 46 | 18k / 1.4k |
| `pale_rim_flats` | White sand shallows to the horizon: a heightfield ring r 25–600 just under the water, sandbars breaking it | r 600 | 6k / 800 |

## 2. The arena (`drowned_choir_ring`)

- **The floor:** the dais at the amphitheatre's floor, level at y 0. The water lies at −0.25 in the ring channel and
  over the white sand outside.
- **The ring:** ten singers stand at r 44, facing the centre. Behind the enemy line the ring's far side fills the
  frame, the moon rising between two of them.
- **No `BossAnchor`:** the Abiding guard are a group, and they take the enemy slots.
- **Hints:** `the_mouths` (low on the dais, up at the singers' open mouths) and `the_ring` (wide, the moon between
  two singers).

## Revisions

- 2026-10-27 (env-art, M3-ENV-722): first issue, with the arena.
