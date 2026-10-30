# 0175: Act II's new audio ships as plain git under `assets/audio/act2/`; the budget rises to 105 MiB

- **Status:** accepted (audio, on the Lead's 2026-10-30 direction under ADR 0205)
- **Date:** 2026-10-30
- **Roles affected:** audio, lead (repository size)
- **Author role:** audio
- **Amends:** [0174](0174-act1-small-sfx-plain-git-while-lfs-blocked.md) (the cap) and [0173](0173-act1-final-audio-in-lfs.md) for Act II.

## Context
ADR 0205 starts audio's Act II content now. The cue sheet (docs/kb/plan/act2/audio/act2_cue_sheet.md) adds about
25–30 MB of new files: scene cues, two people-boss stem sets, stings, about ten beds and the new foley. Every one of
them is under 5 MB. Git LFS uploads are refused from the cloud environments (ADR 0174). `assets/audio/music/act2/**`
is an LFS path, and its 16 finals are already uploaded and stay there. The Lead offered two routes: plain blobs
outside the LFS paths, or a change to `.gitattributes`.

## Decision
- **New Act II audio under 5 MB** goes to a new, non-LFS root, `assets/audio/act2/{music,ambience,sfx}/`, as plain
  blobs. `.gitattributes` is untouched, and the 16 LFS finals stay where they are.
- `tools/audio/targets.py` `TOTAL_BUDGET` is **105 MiB** (+32 over ADR 0174), sized to the cue sheet's estimate with
  a margin.
- **Anything over 5 MB** (there should be none) is listed in the live log for the PC, which can reach
  lfs.github.com.
- Each Act II file keeps Act I's bar: a PROVENANCE row, a targets.py rule, deterministic renders, loudness, and seams
  for loops.

## Consequences
- The repository's plain history grows by up to about 30 MiB over Act II.
- When LFS uploads work again, new Act II music above about 1 MB should go back to `assets/audio/music/act2/`.
  Nothing already committed is migrated.
