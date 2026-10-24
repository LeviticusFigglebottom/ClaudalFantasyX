---
id: M3-MNU-02
title: Memories gallery (SPEC §6.11): replay seen cutscenes from the title
role: ui
status: doing
owner_session: "menus (claude/menus)"
depends_on: [M2-FP-01]
milestone: M3
request-from: ui
reviewer: cinematics
---
## Goal
SPEC §6.11: a "Memories" scene-replay gallery (post-game). Handed to the Menus track by the UI track (2026-10-24). Replays go through CutsceneSequencer, which m2-slice owns: the replay host is agreed with them first.

## Acceptance criteria
- [ ] game/data/memories/memories.json (validated): chapter, dlg scene id, title key, stage scene, unlock flag.
- [ ] A title Memories row and gallery page (locked memories hidden or unknown); keyboard, mouse and pad parity tests; screenshot viewed.
- [ ] Replay plays the scene with no side effects (no events acted on, no flags, no autosave) and returns to the gallery; agreed with m2-slice.

## Notes
- 2026-10-24: proposal sent to m2-slice (data and menu here; a replay mode for zone stories needs their call).

## Review log
