---
id: M3-C07-1206
title: Ch7's real Reefball match replaces the stand-in (TidecupMatch, the story's side of the seam)
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-RBL-01, M3-C07-02]
milestone: M3
request-from: ""
---
## Goal
Queue item 3: the naming beat hands off to a real Reefball match instead of the stand-in (act1_ch07.md §5).

## Acceptance criteria
- [x] `ch07.json` `reefball_match` is a `scene` step to `game/levels/ch07/tidecup_match/tidecup_match.tscn`.
- [x] `TidecupMatch` plays `tidecup_opening` (data `game/data/flow/ch07_tidecup.json`: match, seed, flags, reward,
      return) through the Reefball HUD and its controller (M3-UI-01) when they are in the build, else the engine's AI
      plays both sides at once; it sets `ch07_tidecup_played` always, `ch07_tidecup_won` and the win reward on a win
      only (a draw is a loss for rewards), and returns to `ch07/tamsule_bell_galleries` at `CatchPool`.
- [x] `test_ch07_thread` plays the match at the seam; `test_ch07_tidecup_match` covers win, loss, draw and the
      fallback.
- [ ] When M3-UI-01 reaches the integration branch: type the HUD and controller references (they are loaded by path
      and duck-typed until then), and play the match once through the HUD in a test.

## Notes
- Requests: M3-PRG-1207 (the Oruvel Float accessory; the game has no accessory slot), M3-RBL-1208 (the opponent
  side and the match's barks, act1_ch07.md §5.2–5.3).
- Reviewer: combat (the engine's use), narrative (§5.4).

## Review log
