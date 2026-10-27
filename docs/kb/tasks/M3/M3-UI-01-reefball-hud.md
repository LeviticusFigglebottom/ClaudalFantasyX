---
id: M3-UI-01
title: The Reefball match HUD (Ch7 story match)
role: ui
status: doing
owner_session: "claude/ui"
depends_on: []
milestone: M3
request-from: lead
---
## Goal
SPEC §6.10: the HUD for the Reefball minigame. It needs the score and clock, the ball carrier and the passing and shooting choices (in the battle UI's style), each player's stamina, the opponent read, and the story-match framing. Keyboard, mouse and pad parity are required (M2-UI-26).

## Blocked on
- **M3-RBL-01,** the Reefball engine (in Lead review; on no branch the UI track can merge yet). Start when it reaches the integration branch: the HUD reads its state, and no rules live in the UI.

## Acceptance criteria
- [ ] Layout data in `game/data/ui/reefball_hud.json`; views over the engine's state only.
- [ ] Parity tests with all three devices; shots of a pass choice and a scored goal.

## Review log
