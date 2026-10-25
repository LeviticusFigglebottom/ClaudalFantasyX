---
id: M2-ART-01
title: Art review of the Swell gauge and ring panel, the Read panel, the opening banner and the bestiary
role: character
status: done
owner_session: "env-art"
depends_on: [M2-UI-01, M2-UI-02]
milestone: M2
request-from: ui
---
## Goal
M2-UI-01's third criterion asks for an Art Director review of the Swell gauge placement and the ring panel (tech/ui.md deviations 8 and 9). M2-UI-02 adds three views with no art/ui.md spec yet (deviations 10 to 12). Confirm them or push back, and record the outcome in docs/kb/art/ui.md. As for M1-ART-05, the Art Director takes this under the character role.

## Acceptance criteria
- [x] Deviation 8: the Swell gauge under the name, 64 x 4 px, with its night-gap-and-white frame when full (baseline `battle_swell_ring`).
- [x] Deviation 9: Rhen's ring panel where the command menu was, and the timing-assist tag at its top left (M2-UI-01; there is no baseline with the tag shown; set `timing_assist` to see it).
- [x] Deviation 10: the Read panel and the bestiary page (baselines `battle_read_panel`, `bestiary_menu`).
- [x] Deviation 11: the opening banner, a shortened location banner on a fading dark band with side-shape rule ends (baseline `battle_opening_banner`).
- [x] Deviation 12: the Swell root row at any gauge and the fill-mode rows on the Swell page (baseline `battle_swell_modes`).
- [x] art/ui.md gains a section for whatever is accepted. Anything rejected becomes a UI task.

## Notes
- Every shot is in tests/screenshots/baselines/. The layout numbers are in game/data/ui/battle_hud.json (`read_panel`, `enemy_page`, `opening_banner`, `swell_ring`) and game/data/ui/bestiary_menu.json.

## Review log
- 2026-10-24 Art Director (env-art): **approve with fixes** (filed as M2-UI-08). I looked at all five baselines, plus one capture with `timing_assist` = `auto` (lavapipe, a scratch default flip that was reverted and not committed). Colours are pixel samples. Contrast is WCAG against the measured fill. Accepted rules: art/ui.md §10.
  - **Dev 8, Swell gauge: approve.** Under the name, 64 × 4 at 1080p (43 × 3 at 720p). The full frame measures white `#F2F5FA`, gap `#050A14` (night), fill `#F5C771`–`#F6CC7F` (`ui_swell` `#F2B84B` plus glow). It reads at 720p as a clear white box. Full is a shape cue and not hue alone, so pillar 4 holds.
  - **Dev 9, ring panel: approve, one fix.** Where the command menu was, it covers neither fighters nor timeline. The title (10.0:1) and hint (11.2:1) read. The pips grade by shape and fill: filled `ui_swell` diamond for perfect, `ui_focus`-outlined next beat, dim later beats. The timing-assist tag ("Assist: misses count as Good", the longer string) wraps to two lines at the top left, clear of the ring and the title. **Fix (M2-UI-08):** at rest the lamp is a muddy disc, `#4A4231` (OkL 0.38, C 0.029), inside a grey halo `#474B4B` (C 0.005). That comes from `gauge_back` (translucent `night_sky`) lerped toward `ui_swell`. A lamp must read as lamplight even at rest. `ui_swell` × 0.3 gives `#483716` (C 0.054, h 82°).
  - **Dev 10, Read panel and bestiary page: approve, one fix.** The Read panel sits between the help line and the command menu, and the timeline stays whole. Body text measures 10.1–12.4:1 and the lore line 6.7:1, even with a fighter showing through. The page design is shared with the bestiary, which I want: one page in battle and in the book. "Not Read" is in words. **Fix (M2-UI-08):** defeat counts for Read foes are `ui_focus` (`#65CCC8` sampled), which is the cursor and current-actor colour. They become `ui_line_white`, and unread counts stay `ui_text_dim` (`#A8B7CB`, 7.9:1).
  - **Dev 11, opening banner: approve.** The band is `ui_panel_low` at 0.72 over the noon sky (`#324253`). The title is 9.4:1 and the caption 9.0:1. The gold rules are `#D9B45A`, with `ui_danger` `#E85A44` chevron ends. Under the help line, off the timeline. The caption ends 6 px (720p) above the band's lower edge: tight but clean. The shortened timing is right for battle. A capture note, not a defect: instant pacing shows the ambush banner over Rhen's turn after the foes have already acted, so the baseline pairs "Every foe acts before your party" with "Rhen, Acting now". In live pacing the banner plays during the foes' turns.
  - **Dev 12, Swell root row and mode rows: approve.** The root row says "Ballast" dim below full. On the page, "In use" is `ui_swell` (7.2:1) and "No time" `ui_focus` (5.6:1 on the raised row), consistent with Swap. Disabled "Lamp Dive" is 2.2:1, at the 0.5 disabled alpha by design. The help line states the cost ("Choosing it costs no time"), and the timeline shows no ghost. Tactical clarity holds.
  - **IP guardrail:** pass. The panels are tide-notch with gold/white hairlines. There are no rounded blue windows, the Read page is our own grid (not a one-line scan readout), the banner wording and shapes are original, and the fill modes are plain rows with original names and no per-mode counters or mode screen. Nothing in the five shots is on or near `banned_terms.txt`.
