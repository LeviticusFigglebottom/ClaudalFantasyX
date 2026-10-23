---
id: M1-ARC-06
title: Save v4 (party HP/MP/statuses, shrine network, respawn) and return-to-world on load
role: architect
status: doing
owner_session: architect-stream-6
depends_on: [M1-ARC-03, M1-PRG-03]
milestone: M1
request-from: "architect"
---
## Goal
Make shrine heals, teleport, and Continue real for the M2 slice (M1-ARC-03 follow-ups).

## Acceptance criteria
- [ ] GameStateData v4: party HP/MP/persistent statuses, attuned shrine ids, respawn point (scene + spawn); v3->v4 migration + test
- [ ] party_full_heal_requested actually restores HP/MP and cures per rules
- [ ] Location registry game/data/world/locations.json (id -> scene, spawn, name key), validated
- [ ] On EventBus.game_loaded, SceneRouter moves the player to the respawn point
- [ ] Title screen wiring for TitleSaveEntry; Game.stop_play_clock() on title
- [ ] Haluna shrine instance values (sets_flag ch02_saved_once, location_id ch02/haluna) recorded for Environment

## Notes
Combine with M1-PRG-03 (starting gear after load) in one stream to avoid two concurrent save-path edits.

## Review log
