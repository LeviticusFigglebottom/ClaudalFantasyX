---
id: M4-A2P-109
title: "Act II text: objective lines, tip and prompt cards, item, gear and key-item descriptions, inn and save-shrine flavour"
role: narrative
status: review
owner_session: "act2 story track (claude/act2-plan, ADR 0205)"
depends_on: [M4-A2P-001, M4-A2P-108]
reviewer: ui
milestone: M4
request-from: lead
---
## Goal
The Lead's 2026-10-30 request: Act II's "where to next" lines, tip cards for the new mechanics, descriptions for the
Act II drops and shop stock, and save-point and inn flavour. Everything goes through a loc key, sincere and clean of
banned terms. The ids are coordinated with their data owners in
[act2_text_ids.md](../../plan/act2/act2_text_ids.md).

## Acceptance criteria
- [x] 42 objectives.json rows (29 main, 13 side), with `OBJ_CH1N_*` text in the chapter csv files.
- [x] 12 battle prompts, 3 field tips, the set-piece HUD lines and Pell's formation line, all from ui's tutorials.md and hud.md ids.
- [x] Names and descriptions for 11 items and key items and 12 gear pieces, plus 2 inns, at the ids in act2_text_ids.md.
- [x] Six save-shrine flavour scripts, with dark variants for the Order's shrines after the heresy.
- [x] validate_data, dlgc --check, taskboard, the loc and tip tools tests, and Godot `objective`, `act2_dialogue`, `zone_map` and `pseudo_loc` are all clean.
- [ ] **Owners' data rows** (progression M4-A2P-031, combat and chapters, ui-menus) use these ids.
- [ ] ADR 0041 §3's final bar.

## Review log
