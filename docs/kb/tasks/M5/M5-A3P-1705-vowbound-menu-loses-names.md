---
id: M5-A3P-1705
title: "Act III UI: the Vowbound menus lose a name when it is released (act3_ch20 §9 UI)"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: combat
milestone: M5
request-from: narrative
---
## Goal
act3_ch20 §9: "the Vowbound menu losing names (no animation that makes it a reward; a name greys and goes)". Each
release (U01–U06) sets `ch20_<vowbound>_released`. From then on the Vowbound can't be called, and the menus stop
naming it. By R2 only Kesh is left.

## Acceptance criteria
- [x] `BattleVowboundHud.bound_ids`, the live battle's list of callable Vowbound, leaves out a row whose
      `released_flag` is set, however long ago it was bound.
- [x] The Status page's "Bound" line uses the same rule, so the two menus never disagree. It has no animation and
      no notice; the name simply isn't there.
- [x] tests/unit/test_battle_vowbound_hud.gd: `test_a_released_vowbound_is_no_longer_bound`. Freeing the sandbox
      in both bound_ids tests also fixes a leftover node that was already there.

## Notes
- The data half belongs to combat (M5-A3P-1013): a `released_flag` on each of the six vowbound.json rows (the
  `ch20_<id>_released` flags, already declared), and validate_data checking it like bound_flag.
- Until combat adds the column, nothing changes in play; the UI reads the field as soon as it exists.
- No shot: nothing on screen changes until a release flag is set, and no shot sets one.

## Review log
