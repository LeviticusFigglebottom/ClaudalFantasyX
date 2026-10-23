# First Playable: progress log

Branch `claude/first-playable`, session session_01ELR13ohWMPrprcpcgLa7UR. One line per pushed milestone.

- 2026-10-23: claimed M2-FP-01..04; CutsceneStage contract and sequencer API stub in `game/cutscene/`.
- 2026-10-23: pushed M2-FP-01 (cutscene sequencer, 10 tests), M2-FP-03 (prologue, BattleRequest/FieldBattle, end card; merged from worktree), and M2-FP-04 parts (Shell Shrine placeholder set for Cutscene B, HalunaStory driver, PLAYTEST.md draft). ci_local green (967 tests). The playable Haluna zone (M2-FP-02) is still in progress.
- 2026-10-23: M2-FP-02 merged (playable Haluna) and the whole thread wired (HalunaStory, Cutscene B set, end card). test_fp_thread.gd plus a real-runtime smoke run end to end. ci_local green (974 tests). All four M2-FP tasks are in review. **The thread is playable end to end**; see docs/PLAYTEST.md.
