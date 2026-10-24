---
id: M3-C04-01
title: Ch4 "The Pilgrim's Wake" beat sheet
role: narrative
status: review
owner_session: "m2-slice subagent A (Ch1, Ch4 beats)"
depends_on: []
reviewer: cinematics
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Write the beat sheet for Ch4 "The Pilgrim's Wake" (ch02/haluna night variant, ch04/brightwater_ferry) in `docs/kb/story/beats/act1_ch04.md`, in the format of `docs/kb/story/beats/vertical_slice.md`: the chapter in one paragraph, the running order with beat ids, each beat in detail, flags, the side scene, the boss's placement and what it teaches, music cues, camera shots, word counts, and requests to other roles (env-art kits, audio cues, creatures).

It covers the living funeral, Asha comforting Rhen on the dock, Ysolde boarding, the derelict trader and its name-board (ADR 0017: the ferry is never attacked), the Spar-Wraith, and Ysolde re-inking the wake-shell. It follows `act_outline.md`, the bible, the voice guide and the character files, and ADRs 0015, 0016, 0017, 0020 and 0022. It's sincere (pillar 1), with no echoes of other IP and nothing on `tools/banned_terms.txt`.

## Acceptance criteria
- [ ] `docs/kb/story/beats/act1_ch04.md` exists, with every outline beat for the chapter placed, timed and tagged C (cutscene), E (in-engine) or P (play).
- [ ] Flags are named `ch04_*`, with who sets each and who reads it, including links to other chapters.
- [ ] Each request to another role is listed with enough detail to file as a task.
- [ ] `python3 tools/validate_data.py` and the banned-terms grep are clean.

## Notes
- **Done (2026-10-24):** `docs/kb/story/beats/act1_ch04.md`, in the slice sheet's format: 15 beats (C4-01 to C4-15), each placed, timed and tagged; the critical path is 40.5 min (22 min playable), or 43.5 with the side scene. It has 9 `ch04_*` flags, plus a table of the earlier flags it reads (ch01–ch03, each with a fallback); the side scene "The Ink"; the Spar-Wraith's phases (Fire, then Ice, with Read and swapping); music and SFX cues; shots H12–H16, F01–F06 and D01–D08; word counts (~1,620 written; over its share, paid for by Ch1); requests per role; and an echo-watch table.
- **Reconciled with B11** (`ch03_dock_at_night.dlg`), in a table in §0. The village is dark and the dock is lit only by the sea. Rhen sits, Asha sits beside him, and Toma stays at the shore end. Her tell is to ask about Oruvel, not his day. No re-asking. B11's "At first tide. The causeway won't wait for me." becomes the dawn departure along the causeway to the islet's seaward landing where the ferry waits, and "Then you walk behind me" is honoured on that walk.
- **Decisions made here (for review):**
  1. **Ysolde arrives on the ferry's evening call.** She is seen once at the wake's edge, re-inks Asha's and Imra's shells in the night (it always happens in the world; the side scene is the player witnessing it), walks the causeway ahead, and presents her appointment at the gangplank.
  2. The village sings **"The Long Way Round"**, a homecoming song, knowing she won't come back. This pays off Ch3's dock night bark.
  3. **The derelict is the *Seventh Terrace***, Rhen's last sight of Oruvel; the ferry is never attacked, and it lies an oar's length off, never lashed.
  4. The Spar-Wraith's lines are what keep the dead ship sailing, and its death brings the sails down.
  5. **The first reach-band** is set up and faded before the needle (N-01, offscreen).
  6. **Swapping, Read and elements** are taught on the `bottle_hermit`, the first fight with a reserve.
- **Creatures:** the creatures track's `sail_leech`, `bottle_hermit` and `spar_wraith` are kept as proposed (the hermit's glass must read as an oil-lamp glass, never bound). The answers to their three questions are in §9.
- **Gates:** `validate_data` 0/0; banned-terms grep clean; `taskboard --check` OK. Skipped: Godot, lint, unittest and dlgc (docs only).
- **Reviewer:** cinematics.

## Review log
