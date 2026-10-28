---
id: M3-AUD-851
title: "Act III planning: write the Letting (the Eighth Verse) down in motifs.py"
role: audio
status: blocked
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: story
depends_on: [M3-AUD-836]
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
The Lead's item 6 (Act III planning). act3_plan.md named one new motif, the Letting, still unwritten. Every later cue
that states it (the_letting, unbinding_swell, release_sting, and Reedhollow's farewell-tide once Story agrees) must
take the same notes from one place.

## Acceptance criteria
- [x] `assets_src/music/motifs.py` `letting()` takes the bible's rule literally ("the first verse's phrase turned
      upward"). It is the Hush's first cell (hush_theme_v2.py MEL_A, six notes, E D C | A G A) inverted
      diatonically in A minor around E5, so every step the Hush falls the Letting rises (E F G | B C B), in the Hush's
      own rhythm, closing up on E6, held, on *tash*. It is derived from MEL_A at call time, never retyped.
- [x] tools/tests/test_motifs.py: every interval is mirrored, the rhythm is the Hush's, the last step rises and is
      held, and the degree helpers round-trip. Cues that import motifs.py render byte-identical
      (`--determinism kerrid_stair`).
- [x] act3_plan.md §1 points at it.
- [ ] Story's review: is the inversion the right "turned upward" (against, for instance, a retrograde)? And
      Reedhollow's clutch line carrying the first cell (act3_plan.md §4 Q2).

## Review log
