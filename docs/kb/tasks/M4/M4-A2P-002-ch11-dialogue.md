---
id: M4-A2P-002
title: "Ch11 “Lowlight” dialogue scripts (.dlg), barks and codex text"
role: narrative
status: review
owner_session: "act2 story track (claude/act2-plan, ADR 0205)"
depends_on: [M4-C11-01, M4-A2P-001]
reviewer: cinematics
milestone: M4
request-from: lead
---
## Goal
Ch11's scripts from M4-C11-01: Liss reads the housing-mark and Rhen admits he is Dace's son (paying Ch8's stopped "My—"), the Lamp Engine, the descent and Nhoa's binding (Pell kneels and says nothing for a full scene), the side scene (Rhen and Liss repair a lamp in silence), and one more of Wenna's marks.

## Acceptance criteria
- [ ] Every beat scripted; `#line:` tags; dlgc, validate_data and banned-terms clean.
- [ ] Reads `ch08_liss_found_marks`, `ch08_rhen_froze` where act1_ch09 §10 says Act II pays them.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch11. ADR 0016: no founders' records here (they are in Ch13's Archive).
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Done (story track, 2026-10-30)
- Scripts written in `game/data/dialogue/ch1x/` from the beat-sheet draft, ADR 0204 applied; compiled; speakers, voices and loc rows added; flags declared. `tests/unit/test_act2_dialogue.gd` runs every Act II scene down every path (PASS). Scripts written; reviewer: cinematics.

## Review log
