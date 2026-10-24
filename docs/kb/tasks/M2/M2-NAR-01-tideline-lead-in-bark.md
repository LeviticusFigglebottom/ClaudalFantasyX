---
id: M2-NAR-01
title: A lead-in bark for the tideline fight (one line as the encounter stinger rises)
role: narrative
status: todo
owner_session: ""
depends_on: [M2-BPR-05]
milestone: M2
request-from: combat
---
## Goal
The Lead's intro audit asked for a lead-in bark on the battle transition into the first fight (`ch02_tideline`, the
Haluna tideline at dawn). The hook exists (M2-BPR-05): a row in `game/data/flow/battle_transition.json`
`barks.rows.ch02_tideline` = `{line_key, speaker_key, hold_extra_sec}` shows "Speaker: line" over the rising water,
holds the stinger `hold_extra_sec` longer, and announces it on `EventBus.dialogue_event("battle_bark", ...)` for
audio. Write the line and add the row.

## Acceptance criteria
- [ ] One short line (voice_guide.md; sincerity: no quip that undercuts the moment), its loc key appended to
      `game/data/loc/strings.csv`, and the speaker's name key.
- [ ] The row in `battle_transition.json` (hold_extra_sec long enough to read it, about 0.8-1.2 s).
- [ ] Optional: tell audio (claude/audio) the line key if it gets a voice or a stinger cue.

## Notes
- Docs: docs/kb/tech/battle_presentation.md "Encounter transition", "Lead-in bark".

## Review log
