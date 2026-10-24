---
id: M3-C01-01
title: Ch1 "Lamp-Diver" beat sheet
role: narrative
status: review
owner_session: "m2-slice subagent A (Ch1, Ch4 beats)"
depends_on: []
reviewer: cinematics
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Write the beat sheet for Ch1 "Lamp-Diver" (ch01/oruvel, ch01/oruvel_underway) in `docs/kb/story/beats/act1_ch01.md`, in the format of `docs/kb/story/beats/vertical_slice.md`: the chapter in one paragraph, the running order with beat ids, each beat in detail, flags, the side scene, the boss's placement and what it teaches, music cues, camera shots, word counts, and requests to other roles (env-art kits, audio cues, creatures).

It covers the playable opening dive in the drowned tower using the underwater look (M2-RND-02), the raft-town, Mother Kell's side scene, the Rising, and Hullgnaw on the breaking raft (a tutorial for the timeline). It links the prologue to Ch2: the prologue's hand-off goes to Ch1, and Ch1 ends with Rhen going under into Cutscene A. It follows `act_outline.md`, the bible, the voice guide and the character files, and ADRs 0015, 0016, 0017, 0020 and 0022. It's sincere (pillar 1), with no echoes of other IP and nothing on `tools/banned_terms.txt`.

## Acceptance criteria
- [ ] `docs/kb/story/beats/act1_ch01.md` exists, with every outline beat for the chapter placed, timed and tagged C (cutscene), E (in-engine) or P (play).
- [ ] Flags are named `ch01_*`, with who sets each and who reads it, including links to other chapters.
- [ ] Each request to another role is listed with enough detail to file as a task.
- [ ] `python3 tools/validate_data.py` and the banned-terms grep are clean.

## Notes
- **Done (2026-10-24):** `docs/kb/story/beats/act1_ch01.md`, in the slice sheet's format: 15 beats (C1-01 to C1-15), each placed, timed and tagged C, E or P; the critical path is 35.1 min (24 min playable, 68%), or ~39 with the optional content. It has 10 `ch01_*` flags with setters, readers and cross-chapter payoffs (Ch2, Ch7, E7); the side scene; Hullgnaw's phases and what it teaches (the timeline, then delay); music and SFX cues; shots U01–U11 and O01–O18; word counts (~780 written); requests per role; and an echo-watch table.
- **Hand-offs:** the Prologue → `ch01/oruvel_underway` `Drop` (a flow request); C1-15 → black and silence → Ch2's Cutscene A, unchanged. The last thing heard is the current-song, and the first thing in Ch2 is a star-path hum.
- **Decisions made here (for review):**
  1. **Kell's wick is on the critical path.** E7 is never cut and needs it, so the gift (her trade habit) plays on every path, and the optional side scene is staying at her stall ("The Sea Owes Me a Favour", which plants `ch02_beach_023`'s line).
  2. **Lamp-divers walk weighted.** There's no swimming, and no breath meter; bell-rooms are full-heal rest points with no save.
  3. **No save shrine in Ch1**, so Ch2's save tutorial stays first. The chapter autosave and Fight again are the net, with a stated fallback.
  4. Ch1 is fought **solo**. Rhen never sees Kell go under (her lamp is lit when the water covers it).
  5. The ***Seventh Terrace*** is planted at Oruvel as the Ch4 derelict.
  6. The **current-song** is a distinct original motif (`rhen_current_hum`), never the Hush lullaby.
  7. Tutorials are gated by seen-flags.
- **Creatures:** the creatures track's ids are used (`wickfry`, `tower_limpet`, `oil_slug`, `hullgnaw`), plus Narrative's `scuttler` as the first Undertow-spawn (the reason is in §9). It suggests renaming `wickfry` (the word "wick" belongs to Kell's gift). The foe counts per encounter are given, and the raft is part of the arena, not the boss.
- **Open for the Lead:** the outline's "one month earlier" card against the travel calendar (Ch1–Ch4 alone take four days).
- **Gates:** `validate_data` 0/0; banned-terms grep clean on both sheets; `taskboard --check` OK. Skipped: Godot, lint, unittest and dlgc (docs only, no `.dlg` or tools change).
- **Reviewer:** cinematics.

## Review log
