---
id: M3-C09-01
title: Ch9 "The Ebbing" beat sheet
role: narrative
status: done
owner_session: "m2-slice subagent C (Ch8, Ch9 beats)"
depends_on: []
reviewer: cinematics
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Write the beat sheet for Ch9 "The Ebbing" (ch08/corrow night variant) in `docs/kb/story/beats/act1_ch09.md`, in the format of `docs/kb/story/beats/vertical_slice.md`: the chapter in one paragraph, the running order with beat ids, each beat in detail, flags, the side scene, the boss's placement and what it teaches, music cues, camera shots, word counts, and requests to other roles (env-art kits, audio cues, creatures).

It covers Asha's first great Ebbing, Pell joining, Kerrid alone on the stair (ADR 0022 (f)), the road out ('Somebody's still below'), the act-break voice-over at the Iskarra vigil, and Toma's side scene. It follows `act_outline.md`, the bible, the voice guide and the character files, and ADRs 0015, 0016, 0017, 0020 and 0022. It's sincere (pillar 1), with no echoes of other IP and nothing on `tools/banned_terms.txt`.

## Acceptance criteria
- [x] `docs/kb/story/beats/act1_ch09.md` exists, with every outline beat for the chapter placed, timed and tagged C (cutscene), E (in-engine) or P (play).
- [x] Flags are named `ch09_*`, with who sets each and who reads it, including links to other chapters.
- [x] Each request to another role is listed with enough detail to file as a task.
- [x] `python3 tools/validate_data.py` and the banned-terms grep are clean.

## Notes
- 2026-10-24 (m2-slice subagent C): written: [act1_ch09.md](../../story/beats/act1_ch09.md). 11 beats (B01–B11), 19.5 min on the critical path and 23.5 with the side scene "Shield-Mate". There's no fight of any kind. §10 covers what Act I hands to Act II (all seven in the party, S3 sleeve, three Vowbound, the flags Act II reads, and Ch10 starting at Ossa Fen's edge at dusk). It is ready for the cinematics review.
- **Story calls decided here:**
  - Every Ch9 mote is held, with no `release()`. The vigil keeps the Prologue's own light.
  - The Ebbing is three movements, each carried by one held no-fail input ("Hold to raise the staff"), so the player lets the dance go on.
  - The motes cling to the mourners and leave reluctantly, which is the visual of Asha's "They didn't want to go."
  - Kerrid's cutaway is one shot: alone, a silhouette, no mote toward him and no glow.
  - The fishwife's word reaches Toma through a silent background moment with Marra, so the player doesn't hear the 1001 story before Ch12.
  - Pell's first words are the mandated line. He answers "Who are you?" on the dawn road, and Toma admits him with "Walk behind me, then." (the Ch3 echo).
  - The dawn road keeps Asha off-frame and Kerrid last.
  - Marra's bark explains "Stair's clear." for E3.
  - The act-break VO, recommended: "Seven of us walked out of Corrow that morning. I didn't count us then. I count us every night now." The alternate is in B10.
- **Rendering:** the Ebbing request (§9) is detailed enough to file as one task: held-only fields, the staff attractor tuned to lag and sink, mourner attractors ramping down, a multi-field density plan, reflection, and an optional absorption bloom. There's also a joint `@vfx` cue extension with Systems.
- **Checks:** `validate_data` is clean, and `taskboard --check` passes. This is docs only, so there was no Godot run.

## Review log
- 2026-10-24 cinematics (m2-slice): **approved.** Every mote is held, the Kerrid cutaway is one shot, and Asha is off-frame for 'Somebody's still below.' Recommended act-break VO: 'Seven of us walked out of Corrow that morning…'. The Ebbing rendering requests go to Rendering via the live log.
