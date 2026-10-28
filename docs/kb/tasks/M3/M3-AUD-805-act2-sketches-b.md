---
id: M3-AUD-805
title: Act II music sketches II: Ch13 Ansedra and the Lamp Archive, Ch14 the Peace Wedding, Ch15 Unlamped, Ch16 the Pale Rim and the Drowned Choir
role: audio
status: blocked
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
SPEC §3 and act_outline.md Act II, the second half.

## Acceptance criteria
- [x] Original seamless loops at −16 LUFS, cue rows (no zone rows), listening notes, PROVENANCE, determinism.

## Notes
- 2026-10-25 audio: finished from the handover WIP (docs/kb/audio/wip/). Six loops of about 61 s each, every one at
  −16.0 ±0.05 LUFS integrated with true peak ≤ −1.4 dB; `render_all --determinism` gives identical bytes for each;
  the seams pass (jump ≤ 3.8x, flux ≤ 0.67x). They ship 3.4 MiB, which keeps the total under ADR 0170's 56 MiB.
  Cue rows only: no zone rows until Act II's scenes exist. What to listen for is in listening_notes.md.

## Review log
