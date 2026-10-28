---
id: M3-AUD-839
title: "Act II final cues: the list, sizes, and the LFS-pending render path"
role: audio
status: blocked
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: lead
depends_on: []
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
The Lead (10-27, after ADR 0039): write the Act II final cues' render scripts and sizes now, so they land the
moment LFS works. Keep the files uncommitted and leave .gitattributes alone.

## Acceptance criteria
- [x] docs/kb/audio/act2_finals.md: 30 cues (14 zones, 6 bosses, scenes and stings), with estimates and a column
      for measured sizes; total about 72 MB, all for LFS.
- [x] render_all.py: `ACT2_FINALS` and `--act2`, rendered into assets/audio/music/act2/ and outside the default run,
      the budget and the tests. tools/tests/test_act2_finals.py: every final renders from act2 into act2, and nothing
      there is tracked until .gitattributes routes it to LFS.
- [x] The 12 zone finals from the sketches (M3-AUD-840..843): sources merged, 17.4 MB measured; audio waits for LFS.
- [x] The four modelled bosses (M3-AUD-844/845): sources merged, 7.2 MB measured.
- [ ] Malcor Venn, the Abiding guard and the scene cues, as Act II's fights and beat sheets arrive.

## Review log
