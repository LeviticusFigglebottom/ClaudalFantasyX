---
id: M3-C06-01
title: Ch6 "Salt Edict" beat sheet
role: narrative
status: done
owner_session: "m2-slice subagent B (Ch5, Ch6, Ch7 beats)"
depends_on: []
reviewer: cinematics
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Write the beat sheet for Ch6 "Salt Edict" (ch06/brine_shoals) in `docs/kb/story/beats/act1_ch06.md`, in the format of `docs/kb/story/beats/vertical_slice.md`: the chapter in one paragraph, the running order with beat ids, each beat in detail, flags, the side scene, the boss's placement and what it teaches, music cues, camera shots, word counts, and requests to other roles (env-art kits, audio cues, creatures).

It covers the Order raid on the Saltwright camp, Toma freezing, Liss, the Stillguard Inquisitor and raid-hound, and High Warden Sefir's first appearance (ADR 0017), Liss joining, and her tideline side scene. It follows `act_outline.md`, the bible, the voice guide and the character files, and ADRs 0015, 0016, 0017, 0020 and 0022. It's sincere (pillar 1), with no echoes of other IP and nothing on `tools/banned_terms.txt`.

## Acceptance criteria
- [x] `docs/kb/story/beats/act1_ch06.md` exists, with every outline beat for the chapter placed, timed and tagged C (cutscene), E (in-engine) or P (play).
- [x] Flags are named `ch06_*`, with who sets each and who reads it, including links to other chapters.
- [x] Each request to another role is listed with enough detail to file as a task.
- [x] `python3 tools/validate_data.py` and the banned-terms grep are clean.

## Notes
- 2026-10-24 (m2-slice subagent B): wrote `docs/kb/story/beats/act1_ch06.md` in the vertical_slice format (B01–B10: 26.5 min critical, 30 with the side scene; ~910 words budgeted).
- Sefir's first appearance (B05) is staged item by item against ADR 0017 (a), with his lines written in full for review, and a replay-tells table (§5a) in which every tell is played flat. Decisions: the one sentence is "Put the iron in the water, please."; he declines the question of who struck his Stillguard with "The Edict was written by frightened people. We need not be frightened today."; he sends the wrights "up to Corrow" unbranded but still captive (a Ch8 seam, offered); Asha claims Liss as her guardian and Sefir puts her under Toma's papers, knowing Toma's name unasked; Kerrid's back is turned because he is holding up a burning hull-rib for two wright children; Rhen's choice is to try the greeting backwards or to ask about the wake (`ch06_rhen_greeted_sefir`, paid off in Ch13 and Ch16).
- The Stillguard hum while they burn the camp. Toma freezes at the brazier (the image from his dreams). The fight's rule is that Toma's attacks are greyed against the Stillguard ("Toma will not strike the Stillguard."); the Inquisitor (Hadric Moll) yields and the hound flees, so nobody dies. The `raid_hound` protects the Inquisitor, per the creatures track.
- Liss reads the lantern twice: a whisper in the hold ("immediately"), then the full exchange in B07 with Asha out of frame (the ADR 0022 watch on Asha and the lantern).
- The burned lamp's name is withheld in game text. A proposed design truth (Old Pirran, her first teacher) needs a decisions_log entry before any line uses it.
- Checks (docs-only change, CLAUDE.md gate scope): `python3 tools/validate_data.py` 0 errors, 0 warnings; `python3 tools/taskboard.py --check` clean; the `tools/banned_terms.txt` patterns run over the sheet with no hits. No Godot run (no code or data touched). `dlgc --check` not run: no `.dlg` was written.
- Reviewer: cinematics. The `.dlg` scripts and flag declarations belong to M3-C06-02.

## Review log
- 2026-10-24 cinematics (m2-slice): **approved.** Sefir's B05 is staged item by item against ADR 0017 (a), and the replay-tells table in §5a is what the build needs. **For narrative and the Lead:** 'Old Pirran' (the name in the burned lamp) is a design truth proposal only. It needs a decisions_log entry before any line uses it; no Act I line does.
