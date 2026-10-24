---
id: M3-MNU-02
title: Memories gallery (SPEC §6.11): replay seen cutscenes from the title
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M2-FP-01]
milestone: M3
request-from: ui
reviewer: cinematics
---
## Goal
SPEC §6.11: a "Memories" scene-replay gallery (post-game). Handed to the Menus track by the UI track (2026-10-24). Replays go through CutsceneSequencer, which m2-slice owns: the replay host is agreed with them first.

## Acceptance criteria
- [x] game/data/memories/memories.json (validated): chapter, dlg scene id, title key, stage scene, unlock flag.
- [x] A title Memories row and gallery page (locked memories hidden or unknown); keyboard, mouse and pad parity tests; screenshot viewed.
- [x] Replay plays the scene with no side effects (no events acted on, no flags, no autosave) and returns to the gallery; agreed with m2-slice.

## Notes
- 2026-10-24: proposal sent to m2-slice (data and menu here; a replay mode for zone stories needs their call).
- 2026-10-24: built on m2-slice's hooks (ReplayStage.prepare, CutsceneSequencer.replay; nothing in game/cutscene or game/flow changed). Eight Act I memories in game/data/memories/memories.json (validated, tools/tests/test_memories_validate.py), titles in game/data/loc/memories.csv. MemoriesModel (records: the live Game.state and the newest readable save, read without loading), MemoriesMenu (a FieldSubmenu: chapters with "N of M", remembered memories only), MemoryReplay + memory_replay.tscn (record copy with per-memory replay_flags, threaded stage load under a held reveal, ReplayStage.prepare, spawn / night staging from data, replay sequencer, then back to the title with the gallery open on the memory). Title: a fifth row after Settings, shown only when a memory is remembered; the page grows upward so the four-row title (boot_title) is unchanged (RMSE 0). replay_flags exist because two scenes read their own unlock flag or a later zone flag (Pila's second visit, Oruvel's storm at Kell's stall). Shot memories_menu approved after viewing; 130% text and the five-row title checked with scratch drivers. Docs: docs/kb/tech/ui.md "Memories gallery (M3-MNU-02)". Reviewer (cinematics): do the per-memory spawns and replay_flags stage each scene as first seen? Kell's stall has no spawn (the zone has none at the stall; O09 frames it).

## Review log
