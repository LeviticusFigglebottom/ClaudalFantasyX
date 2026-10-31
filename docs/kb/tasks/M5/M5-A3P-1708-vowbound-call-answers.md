---
id: M5-A3P-1708
title: "Act III UI: a called Vowbound answers; Kesh's answer changes once Asha chooses (act3_ch17 B09)"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
act3_ch17 B09 "Kesh, once more" and drafts README decision 6: "B09 (Kesh's call bark) has no hook in the game yet.
Combat/UI would play the scene from the Vowbound menu." `ch17_bark_kesh_chosen.dlg` has Kesh's two lines: "I hold.
Call, and I will come." before the choice, and "You chose. A thousand years, and one of you finally chose." after
`ch17_chose_the_unbinding`.

## Acceptance criteria
- [x] `game/data/ui/vowbound_answers.json`: what a Vowbound says back as it is called. The first row for it whose
      `when_flag` is set wins, and its `key` is the scene's own line.
- [x] BattleBarks: after the caller's call bark, the called Vowbound's answer floats over it. Flags come from the
      save in a live battle; a capture or test has none unless it passes its own `read_flag`.
- [x] tests/unit/test_battle_barks.gd (6/0):
  - Kesh holds before the choice and says "You chose" after it, floating over her;
  - Ilun says nothing;
  - every answer's key is a line of its scene, and its flag is the one the scene tests.
- [x] No shot changes: captures read no flags, and the vowbound_call fixture binds Ilun only.

## Review log
