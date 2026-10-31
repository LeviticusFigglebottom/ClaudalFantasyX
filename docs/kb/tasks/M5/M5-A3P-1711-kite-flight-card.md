---
id: M5-A3P-1711
title: "Act III UI: the Kite's flight card: where it is bound, on the black of the crossing"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: [M5-A3P-1702]
reviewer: cinematics
milestone: M5
request-from: lead
---
## Goal
The Lead's 10-31 notes ask for the Kite's flight HUD. A flight is the chart's question and Fly (SPEC §6.6). The
change of scene was a plain black fade, and the area title named the place on landing. The card fills the crossing:
it says where the Kite is bound while the screen is black.

## Acceptance criteria
- [x] **KiteFlightCard** (`game/ui/kite/kite_flight_card.gd`; data in `game/data/ui/kite_flight.json`):
  - It shows "The Kite" over "Bound for {place}" and the region.
  - It sits on a layer above the router's fade, under the SceneRouter, so the change doesn't free it.
  - Its opacity follows the fade. It goes once the fade has covered and lifted, or after max_sec.
  - It takes no input, and the router is not edited.
- [x] KiteMapMenu: Fly puts it up only when a change has really started (the router is busy). A refused flight, or
      one a test only records, shows nothing.
- [x] tests/unit/test_kite_flight_card.gd (3/0): it follows the fade, goes after the lift (not before the cover)
      and goes at max_sec, and a recorded flight shows no card. The kite tests pass 18/0.
- [x] **Shot `kite_flight`** (pending_baseline): rendered and viewed.

## Review log
