---
id: M4-A2P-001
title: "Ch10 “Fen of the Kirru” dialogue scripts (.dlg), barks and codex text"
role: narrative
status: doing
owner_session: "act2 story track (claude/act2-plan, ADR 0205)"
depends_on: [M4-C10-01]
reviewer: cinematics
milestone: M4
request-from: lead
---
## Goal
Write Ch10's scripts from its beat sheet (M4-C10-01): `game/data/dialogue/ch10/*.dlg` for every C and E beat, the farewell-tide, the Drowner's intro and fall, the side scene (a Kirru child asks Asha why humans make their dead swim), Pell left at the fen's edge, Reedhollow NPC barks, and the codex text the chapter unlocks.

## Acceptance criteria
- [ ] Every beat in act2_ch10.md has its script, with `#line:` tags and emotion tags.
- [ ] Barks for the clutch and the villagers, state-changing by flag.
- [ ] `python3 tools/dlgc.py --check`, validate_data and the banned-terms grep are clean.
- [ ] Word count logged against SPEC §3.6's budget (40–60k for the game).
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch10. Kerrid's rope-burn glow starts here, without a word about it (ADR 0022 (g)).
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log
