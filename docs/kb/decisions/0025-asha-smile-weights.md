# 0025 — Asha's `smile` weights depart from asha.md §6.3 (the Duchenne smile)

- **Status:** proposed (Art adopts the values in asha.md §6.3, or overturns them)
- **Date:** 2026-10-23
- **Roles affected:** Character, Art, Cinematics
- **Author role:** Character Artist (M1-CHR-11)

## Context
Review-sweep-M found that `asha_face_smile` reads as a smirk with dead eyes. asha.md §6.3 calls this smile her most important expression. At `cheek_raise` 0.45 and `lid_squint` 0.25 the lower lid rose 3.3 mm, and nothing else around the eye moved.

## Options
1. Keep the weights and only strengthen the shapes. At 0.45 the fuller shape still under-reads.
2. **Strengthen `cheek_raise` into a fuller AU6 and raise the smile's weights** (chosen).

## Decision
- `cheek_raise` becomes a fuller FACS AU6: crow's feet, a stronger lower-lid push and roll, the lid–cheek crease, and a brow-tail drop (asha_face_shapes.py).
- The `smile` tag uses `cheek_raise` **0.60** (was 0.45) and `lid_squint` **0.30** (was 0.25) in `asha_face_poses.json`.
- The other tags keep their weights. They get the fuller shape through `cheek_raise`.

## Consequences
- The smile's eyes take part: the lower lid lifts 5.2 mm (max) and the eye narrows.
- Art amends the asha.md §6.3 `smile` row.
- Shape names are unchanged, so `@face` overrides keep working.
