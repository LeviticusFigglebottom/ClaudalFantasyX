---
id: M2-BPR-07
title: The Vowbound call cinematic reads the summon cinematic setting
role: combat
status: todo
owner_session: ""
depends_on: [M2-UI-23]
milestone: M2
request-from: ui
---
## Goal
SPEC §6.3: each Vowbound's call cinematic plays in full on first use, then shortened, with a skip toggle in settings. M2-UI-23 added the setting (Accessibility, "Vowbound calls": Full / Short / Off). The call cinematic, when it is built (M2-BPR-04's "Vowbound call", the C10 Ilun cinematic), has to obey it.

## Acceptance criteria
- [ ] Before a call cinematic plays, ask `UiSettings.shared().summon_cinematic_cut(first_call)`, where `first_call` is true the first time this Vowbound is ever called (keep that record per Vowbound in the save, not per battle).
- [ ] `UiSettings.CUT_FULL` plays every beat. `CUT_SHORT` skips the middle beats and keeps the arrival and the landing. `CUT_NONE` goes straight to the effect (the stage re-seat that `BattleVowboundHud._reseat` does today).
- [ ] Battle speed (`battle_speed`) still scales whichever cut plays. Instant pacing (tests, captures) plays none.
- [ ] Tests for all three cuts.

## Notes
- Depends on M2-BPR-04 too (it lives on claude/battle-presentation, so it is not listed in depends_on here).
- Setting data: `game/data/ui/accessibility.json` `summon_cinematics`. Docs: `docs/kb/tech/ui.md` § Battle speed and the Vowbound call cinematic.
- The default is Short, which plays the first call in full, so the slice's first Ilun call (vertical_slice.md B10) stays unmissable unless the player turns calls Off.

## Review log
