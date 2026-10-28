---
id: M3-CHR-101
title: "Rhen's eyes read red under a sunset rim (the First Verse's S10)"
role: character
status: todo
owner_session: ""
depends_on: []
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
Found in the ADR 0041 beat audit (slice-polish, self-rendered `slice_verse_recognition`, 2026-10-28). S10 is the
reverse on Rhen at sunset: the sun is behind him (`ch03`, 6° / 268°) and his face is in fill (haluna.md §5.3).
In that light, the whites of his eyes render a saturated red, as if bloodshot, at 65 mm.

This is the slice's held recognition close-up: at least 6 s on his face through the verse (N-13). Red eyes read as
injury or the uncanny there, not as grief.

## Asks
- [ ] Find the cause (a guess: subsurface or transmission on the sclera picks up the warm backlight, or the eye's
      wet layer adds the rim). Fix it in the hero eye material, so every hero's eyes hold up under a rim key.
- [ ] Check it in `slice_verse_recognition` (S10), and in `slice_beach_h05_asha` (low sun) for Asha.

## Notes
- The scene: `game/levels/ch03/first_verse/first_verse.tscn` (shot S10); the still is `slice_verse_recognition` in
  shots.json.

## Review log
