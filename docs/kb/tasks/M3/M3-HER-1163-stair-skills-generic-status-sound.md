---
id: M3-HER-1163
title: "Request: the Ch8 Climb's three stair skills layer the generic status_apply under their own sounds (battle_sfx.json vfx rows from M3-BPR-1325)"
role: audio
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: qa
---
## Goal
`python3 tools/audio/act1_audio_audit.py --md` on `lead/gate-big17` lists 3 items, all under Abilities:

- ability `grip_the_stair` (effect `grip_the_stair`) borrows `status_apply`
- ability `hand_closes` (effect `hand_closes`) borrows `status_apply`
- ability `rope_dive` (effect `rope_dive`) borrows `status_apply`

M3-AUD-861 gave each of these skills its own sound: `skills/<id>` = `skill_<id>`, in `sfx_act1_skills.json`. Then
battle-presentation's M3-BPR-1325 (188c49e58, 10-28 18:53) gave them their own VFX effects and added
`game/data/audio/battle_sfx.json` `vfx/<id>` = `status_apply` rows for those effects. BattleAudio plays both the
effect's row (`_on_effect_played`) and the skill's row (`_on_action_resolved`). With different ids, dedupe doesn't
catch it, so the generic status cue now plays over each stair skill's real sound in the Ch8 Climb.

## Fix (3 rows, audio's data)
Delete the three `vfx` rows (`grip_the_stair`, `hand_closes`, `rope_dive`) from `battle_sfx.json`. Their `skills`
rows already give each one its own sound. Alternatively, point each at its `skill_<id>` id: then `dedupe_ms` drops
the second play.

## Acceptance criteria
- [ ] The audio audit lists 0 items on the merged tree. test_act1_audio_audit and Godot `--filter=audio` stay green.

## Notes
- Filed by integration-qa, 2026-10-29, while reviewing M3-AUD-861 on big17.

## Review log
