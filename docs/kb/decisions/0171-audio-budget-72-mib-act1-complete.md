# 0171: The shipped-audio budget rises to 72 MiB to complete Act I's scripted cues

- **Status:** accepted (audio), for the Lead's review
- **Date:** 2026-10-27
- **Roles affected:** audio, tech (repository size), lead
- **Author role:** audio
- **Supersedes:** the 56 MiB figure of [0170](0170-audio-budget-56-mib.md); its per-cue aims and its storage question stay.

## Context
Shipped audio is 53.8 MiB of ADR 0170's 56 MiB. Act I's scripts (claude/act1-chapters, claude/m2-slice) still name
about two dozen `@music` cues that don't exist, so those scenes play in silence. The requests are M3-C04-05,
M3-C05-04, M3-C06-04, M3-C07-06, M3-C08-101 and M3-C09-06. Eight of them are aliases of cues already composed for the
same scenes, at no cost. The rest come to about 12 MiB at 0170's aims: cutscene scores sized to their scene, stings
of 8 s or less, a few beds and stems. The 68 cutscene `@sfx` (M3-AUD-818) add 2.1 MiB. Git LFS is still deferred
(ADR 0005), and every file stays under the 5 MB limit (CLAUDE.md §8).

## Options
1. Hold 56 MiB: leave most of Act I's scored scenes silent, or ship them as stand-ins (the sequencer's
   `music_stand_ins`). That is the playtest's "primitive" again.
2. Re-encode older cues lower to make room. This changes files already measured and delivered, and every rewritten
   binary stays in git history anyway.
3. Raise the cap to 72 MiB, enough to finish Act I, and keep 0170's aims for every new cue: a 60 s loop ≤ 0.9 MiB,
   a through-composed cutscene cue no longer than its scene, a sting ≤ 0.15 MiB, q2 for noise-heavy textures.

## Decision
Option 3. `tools/audio/targets.py` `TOTAL_BUDGET` is 72 MiB. Act II finals do not fit after this: the storage plan
0170 asked the Lead for (Git LFS, or a release-time audio pack) is now **needed before Act II's final cues**, and is
on STATUS.md's risks.

## Consequences
Act I can be fully scored in plain git (+16 MiB over 0170). The repository's audio history grows with it. The next
raise should not happen without the storage decision.
