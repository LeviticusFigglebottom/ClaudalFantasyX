---
id: M3-AUD-861
title: "Act I as played, every sound final (ADR 0041): audit title→Ch9 for silent, temp or reused sounds and fix them"
role: audio
status: doing
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: integration-qa
depends_on: []
milestone: M3
request-from: lead
---
## Goal
ADR 0041 (the human's directive) and the Lead's refocus at 01:12 on 10-28 set the target:
- Every Act I zone has its ambience bed.
- Every enemy has its voice, hit and death sounds.
- Every ability and UI action has its sound.
- Every cutscene has its score and foley.
- There are no temp or reused-placeholder sounds.

## The audit
`python3 tools/audio/act1_audio_audit.py --md` reads the data the runtime reads. It covers:
- zones;
- enemies;
- skills (BattleVfx's map, then BattleAudio);
- cutscenes, in the sequencer's own order (the file first, then the stand-in);
- pending UI hooks;
- notes that say temp.

It reported 46 items at the start. The worked list, with the cause and plan for each, is in
docs/kb/handoffs/live/audio.md.

## Acceptance criteria
- [ ] The audit reports zero items. Anything left is either another track's blocker, with its request task
      named, or a documented by-design case (such as a cutscene that is meant to be silent).
- [ ] New Act I audio goes to Git LFS under `assets/lfs/audio/` (ADR 0173). The plain-git budget has about
      0.5 MiB left, and no existing Act I file is moved.
- [ ] Every new file has its PROVENANCE row and loudness rule, renders deterministically, and has tests.

## Review log
