# 0173 — New Act I audio lands in Git LFS under assets/lfs/audio/

- **Status:** accepted
- **Date:** 2026-10-28
- **Roles affected:** audio; integration-qa (the gates); anyone who clones (`git lfs pull`)
- **Author role:** audio

## Context
ADR 0041 puts Act I at final quality first. The audio audit (M3-AUD-861, `tools/audio/act1_audio_audit.py`) lists
the new sounds Act I still needs:
- the Stillguard Inquisitor's voice;
- five enemies that today borrow another creature's voice;
- sixteen silent boss and support skills;
- three zone beds;
- a prologue score.

ADR 0171's plain-git audio budget is 72 MiB, and 71.52 MiB is used, which leaves about 0.48 MiB. ADR 0039 has
Git LFS live, and `.gitattributes` already routes `assets/lfs/**` to LFS, with its `.import` files kept as plain text.
CLAUDE.md §8 and the Lead's note forbid moving existing Act I files.

## Options
1. **Raise the plain-git budget.** This grows the repository's history with binaries, which is what ADR 0039 exists to stop.
2. **Delete the Act II sketches**, which the LFS finals now supersede, to free about 10 MiB. ADR 0041 says nothing is
   reverted, and the sketches are music.json's fallbacks.
3. **New Act I audio goes under `assets/lfs/audio/<kind>/`**, mirroring `assets/audio/` (sfx/creatures, sfx/battle,
   ambience, music). Existing files stay where they are.

## Decision
Option 3.
- **Where files go:** every new Act I audio file from M3-AUD-861 on is rendered into `assets/lfs/audio/`, with the
  same sub-folders as `assets/audio/`.
- **Loudness:** targets.py's rules apply to the path relative to `assets/lfs/audio/`, exactly as to one relative to
  `assets/audio/`. A creature voice there obeys `sfx/creatures/*_idle_*.ogg` and the rest.
- **Tests:** test_audio_loudness measures those files with the same rules, and keeps them out of the plain-git
  72 MiB total and the 5 MB file limit (validate_data already exempts `assets/lfs/`).
- **Rendering:** render_all.py renders them in its default run, like any other job. A job's output folder is simply
  under `assets/lfs/audio/`.
- **References:** the data rows (sfx_*.json, creature_voices.json, ambience.json, music.json) name the `res://` path
  as it is, so the runtime does not care where a file lives.

## Consequences
- Act I can gain the sounds it lacks without touching the budget or moving a file.
- A fresh clone needs `git lfs pull`; tools/ci_local.sh already runs it. A clone without it plays LFS pointer
  files as broken streams.
- Two roots for Act I audio. The audit and the tests walk both, so nothing is missed.
