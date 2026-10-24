---
id: M3-AUD-07
title: Voice-ready dialogue audio: the per-speaker blip system as data, with tests
role: audio
status: doing
owner_session: "audio (claude/audio; worktree agents for M2-AUD-10, M3-AUD-02, -04, -06, -07)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
SPEC §16 Q4 default: no voice acting yet, but the architecture must be ready. Today one blip file is pitched per speaker (speakers.json).

## Acceptance criteria
- [ ] A per-speaker voice table (blip set, pitch, rate, timbre; a future `vo` path per line id), read by an Audio-side listener on DialogueBox (listen-only; request tasks for any DialogueBox change).
- [ ] A per-speaker blip set synthesized (a few timbres), PROVENANCE, tests; a documented path to real VO (line id -> file, falls back to blips).

## Notes

## Review log
