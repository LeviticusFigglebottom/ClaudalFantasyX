---
id: M3-AUD-835
title: "Listening-note follow-up: a seam report over every loop, and tamsule_bell's wrap masked"
role: audio
status: review
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: design
depends_on: [M3-AUD-16]
milestone: M3
request-from: lead
---
## Goal
The Lead's queue item 4 (listening-note follow-ups). The human's verdict has not come, so this works through the
notes' own open questions with measurements. One note asked "please check the wrap of tamsule_bell.ogg".

## Acceptance criteria
- [x] synth.analysis.loop_seam_report on the decoded file of all 78 loops. Only `ambience/tamsule_bell.ogg` came near
      click level: its decoded wrap was 9.73 times an ordinary sample step (the PCM loop's was 2.5). The Vorbis
      encoder leaves a step at the file's two ends, and this quiet humming bed shows it. Every other loop was under 7.5
      on the jump and 2.9 on the flux.
- [x] act1_ambience.py: `quiet_seam` rotates the circular loop so the file starts at its quietest moment (applied to
      `QUIET_SEAM` beds only, so the other five beds keep their bytes). The wrap is now 0.12 (flux 1.22) at −26.1 LUFS.
      `render_all --only act1_ambience` passes its loop checks.
- [x] listening_notes.md: the wrap note marked; new sections for M3-AUD-831 (Act II creatures) and M3-AUD-832 (the
      UI screens).

## Review log
