---
id: M3-C05-01
title: Ch5 "Terraces of Ash" beat sheet
role: narrative
status: done
owner_session: "m2-slice subagent B (Ch5, Ch6, Ch7 beats)"
depends_on: []
reviewer: cinematics
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Write the beat sheet for Ch5 "Terraces of Ash" (ch05/pemakar, ch05/ashcrown) in `docs/kb/story/beats/act1_ch05.md`, in the format of `docs/kb/story/beats/vertical_slice.md`: the chapter in one paragraph, the running order with beat ids, each beat in detail, flags, the side scene, the boss's placement and what it teaches, music cues, camera shots, word counts, and requests to other roles (env-art kits, audio cues, creatures).

It covers the Lanternfall festival, Kerrid joining (ADR 0020), the Ashcrown copper-vein trial and Kahre, the Cinder Matron, and the smith's side scene. It follows `act_outline.md`, the bible, the voice guide and the character files, and ADRs 0015, 0016, 0017, 0020 and 0022. It's sincere (pillar 1), with no echoes of other IP and nothing on `tools/banned_terms.txt`.

## Acceptance criteria
- [x] `docs/kb/story/beats/act1_ch05.md` exists, with every outline beat for the chapter placed, timed and tagged C (cutscene), E (in-engine) or P (play).
- [x] Flags are named `ch05_*`, with who sets each and who reads it, including links to other chapters.
- [x] Each request to another role is listed with enough detail to file as a task.
- [x] `python3 tools/validate_data.py` and the banned-terms grep are clean.

## Notes
- 2026-10-24 (m2-slice subagent B): wrote `docs/kb/story/beats/act1_ch05.md` in the vertical_slice format (B01–B11: 38.5 min critical, 44 with the side scene and the optional reward; ~1,050 words budgeted).
- Decisions made in the sheet (Narrative's, for review): Lanternfall runs on day 1 night and the trial on day 2 at 13:00 (the color script's two times); the town walks down the terraces beside its boats, and the held grave-motes follow the boats to the sea (planted, never said); Rhen's boat choice (Kell / Oruvel / "Not yet", three mutually exclusive flags that pay off in Ch7); Kell's wick stays in his tin, shown by an insert (ADR 0022 sweep-H watch); Kerrid is introduced by catching a child's collar at the sea-cut weir, hears "Sallow" from Toma, says exactly "I held a stair for your mother once." to Asha, plus "Kerrid." and "Corrow." to Toma, nothing at all to Rhen, and falls in last in line; the Cinder Matron is a Lit Age forge-construct with a bound core that "tests the Cantor's guardians", fought **before** the binding so the armour lesson is Kerrid's (water and cold re-crust her, so calling Ilun is the wrong answer); the second verse is sung "to the mountain that taught it", and the plume's thunder answers with nothing coming (a rhyme with Ch3); Pemakar calls the thunder "Daro's hammer"; the smith is Garo Tenmak, and his son Benet went to Oruvel to learn to dive.
- Creatures use the creatures track's ids (`ashwing`, `slag_tortoise`, `cinder_matron`), with one proposed addition, `vein_sparker`, so the climb asks for Ysolde (cut it if creatures prefers); foes on screen per zone are in §9 item 15.
- Requests to other roles are in §9 (30 items: Environment kits and shots P01–P12 and A01–A12, Rendering, Character Art, creatures, Combat (Kerrid's data, Kahre, the Matron band), Audio, Cinematics watches, Systems, Lead glossary).
- Checks (docs-only change, CLAUDE.md gate scope): `python3 tools/validate_data.py` 0 errors, 0 warnings; `python3 tools/taskboard.py --check` clean; the `tools/banned_terms.txt` patterns run over the sheet with no hits. No Godot run (no code or data touched). `dlgc --check` not run: no `.dlg` was written.
- Reviewer: cinematics. The `.dlg` scripts and flag declarations belong to M3-C05-02.

## Review log
- 2026-10-24 cinematics (m2-slice): **approved.** Kerrid's entrance (the collar at the weir, the head turn, three words in all) and the Matron's water-re-crusts rule (Ilun is the wrong answer) both serve the beats. Note for M3-C05-02: `vein_sparker` is optional. Keep it only if creatures has budget.
