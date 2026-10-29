---
id: M3-AUD-813
title: Menu sounds after the integration merge (FormationMenu live, Key Items tab, refusals heard via M2-AUD-15)
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M2-AUD-17, M2-AUD-15]
milestone: M3
request-from: audio
---
## Goal
The integration branch brought claude/menus' FormationMenu, the Items page's Bag / Key Items tabs (M3-MNU-03) and
the public reads audio asked for in M2-AUD-15. Switch the hooks on and keep audio's tests green.

## Acceptance criteria
- [x] FormationMenu's hook is live (no `pending`).
- [x] Items: the tab switch plays `ui_page`; a refused use (`is_refused()`) plays `ui_error` on Confirm.
- [x] Formation and Equip: a refused pick, move, equip, take-off or craft (`is_refused()`) plays `ui_error`.
- [x] test_field_audio walks the Key Items tab; test_battle_ko_once keeps its primitive-stand-in case now that
      wickfry has a model (the test lifts the model for the one fight).

## Notes
- 2026-10-25 audio: `LatticeBoardView.is_dragging()` and `EquipMenu.is_armed()` are not used yet: the map pan
  already has its own row and Customize's first Confirm already sounds through the level change.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
