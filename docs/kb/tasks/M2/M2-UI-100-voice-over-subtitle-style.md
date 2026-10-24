---
id: M2-UI-100
title: Voice-over and narrator lines as subtitles, so the dialogue box stops covering the prologue's frame
role: ui
status: todo
owner_session: ""
depends_on: []
milestone: M2
request-from: cinematics
---
## Goal
The human's playtest (Lead, 2026-10-24) said the prologue's "Everyone I'm going to tell you about is still here tonight" still read grey. m2-slice fixed the scene: the vigil figures wear palette colours, Rhen's lantern is lit and there is a dusk grade stand-in (583759c0). But while the line is up, the dialogue box covers the bottom of the frame:
- **The panel:** `hymn_theme.tres:57/66`, #133A66 at 85% alpha, 1600×252 px at 1080p, from `game/ui/dialogue/dialogue_box.tscn` offsets -300 / -48.
- **Coverage:** about 19% of the frame, plus the letterbox's 22%, directly over the figures the line is about.
- **Measured:** whole-frame Oklab chroma is about 0.055, against 0.070 for the scene above the box.

Renders: m2-slice's scratchpad `grey2/after_presets_t10.png`. The cause and numbers are in the m2-slice live log.

## Acceptance criteria
- [ ] Narrator and voice-over lines (the narrator speaker and the `vo` tag) show as a subtitle: no panel, or one at about 0.35 alpha, with a text shadow or outline for legibility, set in the lower letterbox band when one is up.
- [ ] Spoken character lines keep the panel.
- [ ] The prologue's frame keeps its figures visible while the line is up.

## Notes
- This is UI's file and style. m2-slice won't edit it. An alternative is a shorter panel (about 160 px).

## Review log
