---
id: M3-C07-01
title: Ch7 "The Tidecup" story beats and cutscenes (Reefball gameplay is a separate Lead agent's)
role: narrative
status: review
owner_session: "m2-slice subagent B (Ch5, Ch6, Ch7 beats)"
depends_on: []
reviewer: cinematics
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). m2-slice owns Ch7's story beats and cutscenes; a separate Lead agent owns the Reefball match's gameplay. Write `docs/kb/story/beats/act1_ch07.md`, covering:
- Rhen and Tavi Orse (Mother Kell's grandson);
- the Tidecup opening as Reefball always has (N-12: each captain names one person the sea has taken; Tavi names "Oruvel");
- the match played as Oruvel's opening round, with no interruption (ADR 0020 (h): they don't win the cup);
- Tavi withdrawing the side;
- Toma and Asha in the galleries, and Liss noting the Bell is glimmer-tech;
- the side scene at the empty moorings.

Mark clearly where the match's gameplay starts and ends, and which flags and results it hands back (a reward only, never a branch). Then build the cutscenes and dialogue around that hand-off.

## Acceptance criteria
- [x] The beat sheet exists in the vertical_slice format, with the match's hand-off points marked for the Reefball agent.
- [ ] The `.dlg` scripts and cutscenes for the story beats, with flags declared, and `validate_data` and `dlgc --check` clean.

## Notes
- 2026-10-24 (m2-slice subagent B, the story half only): wrote `docs/kb/story/beats/act1_ch07.md` in the vertical_slice format (B01–B10, ~30 min critical with a ~10 min match; ~860 words budgeted). **§5 "Hand-off to the Reefball match"** is the contract with the Reefball agent: B05 (the naming) ends on `<<event start_reefball ch07_tidecup_oruvel_sorrin>>` (a new event, requested from Systems). The match receives Oruvel (Tavi + four + Rhen in Pio's place), no other party member, and Sorrin as the opponent (not Tamsule, which must win offscreen). It returns `ch07_tidecup_played` always and `ch07_tidecup_won` on a win, as a reward only (the Oruvel Float), with no retry. B07 resumes identically for a win and a loss, and a test should assert that no story `.dlg` reads `ch07_tidecup_won`.
- Decisions: the crowd answers each name at the naming with one word, "Up."; Rhen tells Tavi "She couldn't swim, Tavi."; the missing youngest is Pio (sixteen; "a dead boy's place", ADR 0020 (h); never found); Rhen wears Pio's side-band and ties it to the *Gull*'s empty ring in the side scene; the cup's winner is mentioned once, by a boatman in B10; Kerrid stays outside the Bell, knee-deep at the river moorings.
- Checks (docs-only change, CLAUDE.md gate scope): `python3 tools/validate_data.py` 0 errors, 0 warnings; `python3 tools/taskboard.py --check` clean; the `tools/banned_terms.txt` patterns run over the sheet with no hits. No Godot run (no code or data touched). `dlgc --check` not run: no `.dlg` was written.
- **Open on this task:** the second acceptance item (the `.dlg` scripts, cutscenes and flag declarations) is not done. This run was scoped to the beat sheet only. That work is written against §1–§5 and needs the `start_reefball` event first. Either keep this task open for it after review, or split it into a new task (the Lead's call).

## Review log
