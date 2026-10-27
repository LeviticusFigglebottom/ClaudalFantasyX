# 0170 — The shipped-audio budget rises to 56 MiB through the Act II sketches

- **Status:** accepted
- **Date:** 2026-10-24
- **Roles affected:** audio, tech (repository size), lead
- **Author role:** audio

## Context
`tools/audio/targets.py` `TOTAL_BUDGET` caps every shipped audio file together, and `tools/tests/test_audio_loudness.py`
enforces it. It went from 24 MiB (the slice) to 48 MiB (Act I, mix.md "Budget"). With the Act I cues, the M3 SFX sets,
the field foley (M3-AUD-802) and the first Act II sketches (M3-AUD-804), shipped audio is now 47.1 MiB. The second
sketch set (M3-AUD-805) adds up to 2.4 MiB. Git LFS is deferred (ADR 0005), so every byte lives in plain git history.
Each file stays under the 5 MB limit (CLAUDE.md §8).

## Options
1. Keep 48 MiB: drop the Act II sketches back to very short or low-quality loops. The sketches exist so the human can
   judge a direction, so starving them defeats the point.
2. Re-encode the existing cues lower (q3 to q2) to make room. That saves about 25 %, but changes files the human has
   already heard and approved by measurement, and it rewrites history-heavy binaries.
3. Raise the budget to 56 MiB now, and put the full-game question (about 70–90 MB of audio once Acts II and III have
   final cues) to the Lead as a repository-size decision: LFS, or a release-time audio pack.

## Decision
Option 3. `TOTAL_BUDGET` is 56 MiB. New cues keep the per-cue aim (≤ 0.9 MiB for a 60 s loop; q2 for noise-heavy
textures). The 5 MB per-file limit is unchanged.

## Consequences
The Act II sketches fit. The repository grows by about 5 MiB more audio than the old cap allowed. Before Act III
cues start, the Lead should decide on Git LFS or another storage plan (a STATUS.md risk). The budget can then go up
again, or the old cues can move.
