---
id: M5-A3P-1952
title: "Act III score, part 3: the ending (E1-E7, the rests, the credits)"
role: audio
status: review
owner_session: "claude/audio (session_01UPFyE9L9BA3QodpCNJEfAs)"
depends_on: [M5-A3P-1950]
reviewer: story
milestone: M5
---
## Goal
The ending's music as act3_ending.md names it.

## Acceptance criteria
- [x] **`goodbye_imra`** (E1, 16 s, -24): one piano note, the lullaby's home A, after she is gone. Her hum is the scene's `@sfx velamir_lullaby_hum` (the Act III sfx batch, next).
- [x] **`ending_lift_bed`** (R2/R3, a 40 s loop at -20): the drone on A and a faint glass shimmer on A major, no melody. R4 fades it.
- [x] **`goodbye_dace`** (E2, 92 s, -18): the current-song on a plucked harp and, inside it, four bars of the Velamir lullaby. It's the same seven notes (D dorian and A minor), so the lullaby is in his song without a change of key. Home on an open D.
- [x] **`goodbye_kerrid`** (E3, 112 s): his stair on the bowed low string with a gamelan pulse, each stride 9 % longer, from 48 BPM to a held last A: the end of the walking.
- [x] **`ending_dock`** (E6, 60 s): solo piano, the Hush's first phrase resolving at last (B D E | A, to A major), then its first line an octave lower, ending on A.
- [x] **`credits_suite`** (CR, 5 min 38 s): the game's themes as shipped, in the pilgrimage's order (eight excerpts crossfaded at their own levels), ending on the lullaby's first phrase on the piano alone.
- [x] **`post_credits_lamp`** (E7, 27 s, -20): the star-path's first phrase two octaves down on a low metallophone. The match is the scene's sound.
- [x] Loudness to the targets.py rules (the quiet ones have their own), determinism, the loop seam, the mono fold (the suite thins by 7.5 dB for a moment at the hush-to-piano join), PROVENANCE.

## Notes
- The credits run 7 min in act3_ending.md; the suite is 5 min 38 s. If the roll is longer, the last held A rings into silence. A ninth excerpt (`hollowmere` or `going_under`) is an easy add.
- `credits_suite` reads the shipped renders of its eight themes. Re-render it when any of them changes.

## Review log
