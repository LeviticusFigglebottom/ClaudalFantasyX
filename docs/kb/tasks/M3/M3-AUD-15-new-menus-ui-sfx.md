---
id: M3-AUD-15
title: UI SFX for the new menus: Lattice node activation, equip, the map, tips, the title screen
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
claude/ui and claude/menus add menus; ui_sfx.json hooks (M2-AUD-05 UiAudio) wire them by class and signal names.

## Acceptance criteria
- [x] Synthesized sounds (Lattice node lights, path unlock, equip/unequip, map open/scroll/marker, tip pop-in, title confirm and the title's first swell) and ui_sfx.json hooks for those classes (pending when absent), tests, PROVENANCE.

## Notes
- `assets_src/sfx/menu_sfx.py` -> 12 sounds in `assets/audio/sfx/ui_*.ogg` (+ .import), rows in
  `game/data/audio/sfx_ui_menus.json` (UI bus), JOBS row in `tools/audio/render_all.py` (`--only menu_sfx
  --determinism`: byte-identical). The existing `sfx/ui_*.ogg` rule fits (no targets.py change). Decoded momentary
  max: lattice_node -19.99, lattice_unlock -20.24, lattice_step -20.16, equip -20.44, unequip -20.29, map_open
  -20.05, map_close -20.19, map_tick -20.15, map_marker -20.53, tip -19.98, title_confirm -19.98, title_swell
  -20.00 LUFS; true peak -3.02 to -13.12 dBTP. PROVENANCE rows appended.
- `ui_sfx.json` hooks (appended; priority list extended): TitleMenu (live) gets `on_enter` ui_title_swell and an
  `is_launched()` watch for ui_title_confirm. Pending (claude/ui): FieldSubmenu, LatticeMenu, EquipMenu,
  ZoneMapMenu, ZoneMapView (`poi_clicked`), TipCard (`phase` == IN). The class names, signals and the public
  methods the watches read come from origin/claude/ui (same as claude/menus for these files).
- UiAudio: watch helpers `lattice_woken`, `lattice_places`, `worn_count`, `gear_signature`; an `audio_class` meta
  names a node's hook (test stand-ins). data_check: a class inherits its base script classes' signals (LatticeMenu's
  `closed` is FieldSubmenu's); test in `tools/tests/test_audio_data.py`.
- Tests: three new tests in `tests/unit/test_field_audio.gd` with runtime stand-ins (Lattice, Equip, map, tip,
  title; rows exist, import, are ranked; hooks pending). `-- --filter=audio`: 59 run, 0 failed.
- Once claude/ui merges: remove `pending` from the six hooks (validate_data then checks names), and add a test on
  the real LatticeMenu/EquipMenu. The M2 ShopMenu/InnMenu guesses don't match claude/ui (TownMenu declares only
  `closed`): a follow-up should rewrite them. Listening notes: docs/kb/tech/audio_runtime.md "M3 menus".

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
