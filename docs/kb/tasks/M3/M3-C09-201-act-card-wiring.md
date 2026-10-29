---
id: M3-C09-201
title: "Ch9 B11: show UI's ActCard from the act_card event (swap the caption stand-in)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M3-C09-05, M3-C09-09]
milestone: M3
request-from: ui
---
## Goal
M3-C09-05 built the act card widget, `ActCard` (`game/ui/cards/act_card.gd`; data `game/data/ui/act_card.json`), but the `act_card` event it listens for is Systems' (M3-C09-09) and is not in `events.json` yet. Once it is:
1. In `ch09_the_road_out.dlg` `ch09_act_card`, replace the caption line `ch09_act_card_001` ("Act II\: The Truth") with `<<event act_card 2>>`, and keep a wait that covers the card's in, hold and out (`act_card.json`: 1.2 + 3.0 + 1.2 s).
2. In the story host (`Ch09Zone`, or the shared `ZoneStory` so every chapter gets it), add the card and listen to the sequencer: `ActCard.open_in(self).listen(story.sequencer)`. The card holds the screen black after its words fade, so the hand-off to the end card (and later Ch10) fades in from black. Call `hide_card()` or free it when the next scene takes over.
3. Update `test_ch09_thread.gd`. It currently checks that B11's last line is `ch09_act_card_001`; instead, check that the `act_card` event fired with 2 and that the card showed `ACT_CARD_2_LABEL` and `ACT_CARD_2_TITLE`.
4. Optional: the Prologue's "One month earlier." (`ch01_drop_001`, a caption on black) can use the same widget, `ActCard.show_caption("DLG_CH01_DROP_001")`, if Cinematics wants the two title cards to match.

## Acceptance criteria
- [ ] B11 shows the ActCard, not a caption line, and still hands off on black.
- [ ] The Ch9 thread test is updated and green.

## Notes
Filed by UI (M3-C09-05). UI did not edit the `.dlg`, `events.json` or the zone host: those files belong to Narrative/m2-slice and Systems.
- integration-qa (Systems), 2026-10-29: **unblocked.** `act_card <int act>` is in `events.json` (M3-C09-09, 958fefd03 on
  claude/hero-integration; in big17 or the next batch). dlgc compiles `<<event act_card 2>>`.

## Review log
