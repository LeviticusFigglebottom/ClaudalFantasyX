---
id: M4-C10-01
title: Ch10 "Fen of the Kirru" beat sheet (the first of Act II)
role: narrative
status: blocked
blocked-by: ADR 0041
owner_session: ""
depends_on: []
reviewer: cinematics
milestone: M4
request-from: act1-chapters
---
## Goal
The Lead approved starting the Act II greybox (Ch10 onward, M4) once Act I is at its quality bar (Lead, 2026-10-27).
act1-chapters builds the zones, flow and scripts the way it built Ch4–Ch9, from a beat sheet. Write the one for Ch10
"Fen of the Kirru" in `docs/kb/story/beats/act2_ch10.md`, in the format of `act1_ch09.md`: the chapter in one paragraph,
the running order with beat ids, each beat in detail (C cutscene, E in-engine, P play), flags (`ch10_*`, who sets and
who reads each), the side scene, the boss's placement and what it teaches, music cues, camera shots, word counts, and
requests to other roles.

From `act_outline.md` (Ch10): zones `ch10/ossa_fen` (mangrove channels) and `ch10/reedhollow` (the Kirru village);
Pell isn't allowed in; the Kirru farewell-tide at dusk (the clutch sings, turns its back, the motes lift straight up
into the stars; Asha can't stop looking); the boss, the Mangrove Drowner (spawn in the roots, two phases; creatures
has it as M3-CRE-621); the side scene, a Kirru child asking Asha why humans make their dead swim. Ch9's beat sheet §10
lists what Act I hands over (the party of seven, the S3 sleeve, three Vowbound, the flags Act II reads, Ch10 opening
at Ossa Fen's edge at dusk).

## Acceptance criteria
- [ ] `docs/kb/story/beats/act2_ch10.md` exists, every outline beat placed, timed and tagged C/E/P.
- [ ] Flags named `ch10_*` with setter and reader, and the Act I flags it reads.
- [ ] Each request to another role (env-art's fen and village kits, audio, creatures, characters for the Kirru)
      is listed with enough detail to file as a task.
- [ ] `python3 tools/validate_data.py` and the banned-terms grep are clean.

## Notes
- 2026-10-30 (act2-plan track, the Lead's assignment): **draft: pre-gate** written at `docs/kb/story/beats/act2_ch10.md`. It is not reviewed; the task stays `blocked` until the gate, then the story track takes it to review.

## Review log
