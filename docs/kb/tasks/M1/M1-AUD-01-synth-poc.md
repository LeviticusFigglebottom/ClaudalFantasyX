---
id: M1-AUD-01
title: Audio synthesis proof of concept
role: audio
status: review
owner_session: "audio-stream-1"
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §9 and §14: prove the self-synthesized instrument palette.

## Acceptance criteria
- [x] Piano, metallophone, flute, pad, reverb, loudness normalization
- [x] A Hush theme sketch at −16 LUFS
- [x] UI SFX and a text blip
- [x] PROVENANCE rows

## Notes
Delivered 2026-10-22. The theme is at -16.05 LUFS and all five files total 0.82 MiB; renders are deterministic (`python3 tools/audio/render_all.py --determinism`). Self-assessment: about 30-40% of the way to a commercial piano-led theme, usable as a placeholder. The piano model is the weakest link. **Nobody has listened to it yet**: the agent cannot hear audio, so the human must listen before §16 Q3 is answered. Reviewer: Lead plus the human.

## Review log
- 2026-10-22 lead: provenance rows merged, validator clean. Listening review pending (human).
