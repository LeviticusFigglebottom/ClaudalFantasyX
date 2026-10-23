---
id: M2-ART-01
title: Art review of the Swell gauge and ring panel, the Read panel, the opening banner and the bestiary
role: character
status: todo
owner_session: ""
depends_on: [M2-UI-01, M2-UI-02]
milestone: M2
request-from: ui
---
## Goal
M2-UI-01's third criterion asks for an Art Director review of the Swell gauge placement and the ring panel (tech/ui.md deviations 8 and 9). M2-UI-02 adds three views with no art/ui.md spec yet (deviations 10 to 12). Confirm them or push back, and record the outcome in docs/kb/art/ui.md. As for M1-ART-05, the Art Director takes this under the character role.

## Acceptance criteria
- [ ] Deviation 8: the Swell gauge under the name, 64 x 4 px, with its night-gap-and-white frame when full (baseline `battle_swell_ring`).
- [ ] Deviation 9: Rhen's ring panel where the command menu was, and the timing-assist tag at its top left (M2-UI-01; there is no baseline with the tag shown; set `timing_assist` to see it).
- [ ] Deviation 10: the Read panel and the bestiary page (baselines `battle_read_panel`, `bestiary_menu`).
- [ ] Deviation 11: the opening banner, a shortened location banner on a fading dark band with side-shape rule ends (baseline `battle_opening_banner`).
- [ ] Deviation 12: the Swell root row at any gauge and the fill-mode rows on the Swell page (baseline `battle_swell_modes`).
- [ ] art/ui.md gains a section for whatever is accepted. Anything rejected becomes a UI task.

## Notes
- Every shot is in tests/screenshots/baselines/. The layout numbers are in game/data/ui/battle_hud.json (`read_panel`, `enemy_page`, `opening_banner`, `swell_ring`) and game/data/ui/bestiary_menu.json.

## Review log
