---
id: M4-UI-1256
title: "Request: the Act III card as ActCard's two-line act card from ch16_act_break (the act_card event)"
role: ui
status: todo
owner_session: ""
depends_on: [M3-UI-210]
milestone: M4
reviewer: cinematics
request-from: cinematics
---
## Goal
The Lead (11-03) gave the Act II break to act1-chapters and asked ui-menus to wire the card. The break now plays at
the Prologue's plaza (`game/data/dialogue/ch16/ch16_act_break.dlg`, PrologueScene's `visits` row). Its card is a
`#card` line today ("Act III: The Unbinding", `ch16_act_card_001`), so it shows as ActCard's one-line caption, the
way Ch9's "Act II: The Truth" does.

## Acceptance criteria
- [ ] B12 shows `act_card.json` `acts."3"` as the two-line act card (numeral line, gold rule, name), from the
      sequencer's `<<event act_card 3>>` (events.json `act_card`, M3-C09-09) or another hook ui-menus prefers.
      act1-chapters swaps the `#card` line for the event once it is wired (or ui-menus edits the .dlg; tell us).
- [ ] The same for Ch9's `ch09_act_card` ("Act II: The Truth") if you want both breaks to match.

## Review log
