---
id: M3-AUD-836
title: "Act III planning: the motif map and the cue list"
role: audio
status: blocked
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: story
depends_on: []
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
The Lead's queue item 5 (2026-10-27): plan Act III's music before its chapters are designed. The plan needs a motif
map (every recurring tune, where its notes live, and what Act III does with it) and a cue list for Ch17–Ch21 and
the Ending, with sizes.

## Acceptance criteria
- [x] docs/kb/audio/act3_plan.md §1, the motif map: the Hush (verse 1 is the Velamir lullaby, N-11), the seven
      verses, a new `LETTING`, Sefir's motif (its C# resolves only in H08), the Order's hum, the current-song,
      Kerrid's stair, the star-path, the farewell-tide, Liss, Ysolde and the Vowbound summons. Each row names the
      source constant its notes live in.
- [x] §2, the cue list: 30 cues plus the Vowbound releases, adopting act3_ending.md's ids as written and adding
      Ch17–Ch20's. Each has a kind (loop, stems, cue, sting), a sketch and a size estimate. The total is about
      76 MB (a range of 60–85), so Act III cannot ship committed; the storage question goes to ADR 0172 or LFS.
- [x] §3, constraints: the 5 MB file rule (split credits_suite), voices (SPEC §16 Q4/Q5), one goodbye per scene,
      rule 7, and stems in the sequencer (M3-AUD-834).
- [x] §4, open questions. For the human: the voice. For Story and the Lead: the farewell-tide carries the Letting,
      so Reedhollow's line is revised to the Letting's first cell. For the Lead: storage. For Cinematics: E5's
      silence.
- [ ] Story's review: the motif assignments for E1–E3 and H08 (the review log).

## Review log
