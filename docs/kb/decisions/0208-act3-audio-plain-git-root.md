# 0208: Act III's new audio ships as plain git under `assets/audio/act3/`; the budget rises to 150 MiB

- **Status:** accepted (audio, on the Lead's 2026-10-30 21:56 direction under ADR 0207)
- **Date:** 2026-10-30
- **Roles affected:** audio, lead (repository size)
- **Author role:** audio
- **Amends:** [0175](0175-act2-audio-plain-git-root.md) (the cap), for Act III.

## Context
ADR 0207 opens Act III production per track. Audio's share is the Act III score. The drafts and act3_ending.md name
about 34 new cues, among them the Unbinding themes, the finale, the ending and the credits suite, plus Ch17–Ch20's
scene and memory cues. That is roughly 35–45 MiB of new files, each under 5 MB. Plain-git audio already stands at
100.3 MiB of ADR 0175's 105 MiB. `assets/audio/music/act3/**` is an LFS path (`.gitattributes`), and LFS uploads are
still refused from the cloud environments (ADR 0174). Its eight earlier finals are uploaded and stay there.

## Decision
- **New Act III audio under 5 MB** goes to a new, non-LFS root, `assets/audio/act3/{music,ambience,sfx}/`, as plain
  blobs. This is the same route as Act II's (ADR 0175). `.gitattributes` is untouched.
- `tools/audio/targets.py` `TOTAL_BUDGET` is **150 MiB** (+45 over ADR 0175), sized to the estimate with a margin.
- Each file keeps the bar every act has:
  - a PROVENANCE row;
  - a targets.py rule;
  - a deterministic render;
  - loudness to target;
  - a seam for loops;
  - the mono fold (`tools/audio/mono_check.py`).
- Sung Lamptongue follows docs/kb/audio/lamptongue.md:
  - Asha's own voice stays the vowel-shaped breath-flute vocalise until SPEC §16 Q4 settles it;
  - choirs and congregations use the procedural formant voices (`synth/voice.py`), as Act II's do.

## Consequences
- Plain history grows by up to about 45 MiB over Act III.
- When LFS uploads work again, new Act III music above about 1 MB should go back to `assets/audio/music/act3/`.
  Nothing already committed is migrated.
