---
id: M1-AUD-01
title: Audio synthesis proof of concept
role: audio
status: done
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
- 2026-10-24 review-sweep-O (qa): **approve.** Every criterion holds against the repo.
  - **Checks:**
    - I decoded every shipped .ogg and re-measured it with `synth.loudness`. `hush_theme_sketch` is −16.05 LUFS, −1.42 dBTP and 68.7 s long. The four SFX sit at −20 to −27 LUFS, all under −6 dBTP. AUD-01's five files total 0.82 MiB, as claimed.
    - `render_all.py --only ui_sfx` re-rendered the four SFX byte-identical to the committed files (no git diff), so they reproduce from source.
    - The audio synth tests pass (9 OK). PROVENANCE has a row for every file (rows 14-18).
  - **Instruments:** the piano, metallophone, flute, pad, reverb and loudness modules are all under tools/audio/synth/.
  - **Not judged here:** how it sounds. That is SPEC §16 Q3, which the human answers on M1-AUD-02. It does not block the proof of concept.
