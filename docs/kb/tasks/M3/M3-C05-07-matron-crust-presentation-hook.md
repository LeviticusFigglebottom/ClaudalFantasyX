---
id: M3-C05-07
title: Show the Cinder Matron's Crust when she re-crusts (a battle-presentation hook, not a phase)
role: ui
status: review
owner_session: "claude/ui"
reviewer: cinematics
depends_on: [M3-C05-02]
milestone: M3
request-from: cinematics
---
## Goal
For the battle-presentation track. Creatures' `cinder_matron` model hides its "Crust" when she enters phase `pour` (the crust breaks, and the plates beneath glow red-hot). In play, the crust comes back without a phase change, through two engine events (`game/battle/boss_mechanics.gd`):
1. **Her `recrust` skill resolves.** She telegraphs `recrust_gather` two turns ahead; `recrust` cleanses `armor_break` and adds `protect`.
2. **A reaction:** a water or ice hit lands on her during `pour` (enemies.json `reactions`). The hit result records `"reacted": true`, cleanses `armor_break`, and adds `protect` and `shell`.

Show the Crust on either event, and hide it again when Kerrid's `armor_break` lands. Creatures' model already supports `show: ["Crust"]`; this needs the presentation side to call it on those events.

## Acceptance criteria
- [x] The Crust shows on `recrust` resolving and on a `reacted` hit, and hides on `armor_break` landing. A battle-scene test covers each.

## Notes
### Implementation (claude/ui, 2026-10-24; reviewer: cinematics)
- `game/battle/scene/battle_part_cues.gd` (`BattlePartCues`, listen-only) on `BattleChoreo.contact`, so the crust
  closes or cracks as the blow lands (with the choreography off, contact comes as the action resolves). Per landed
  hit on a fighter whose creature has a cue row: a status in `hide_on_statuses` that the hit added hides the parts;
  then the action's skill in `show_on_skills`, or `"reacted": true` with `show_on_reaction`, shows them. Hide before
  show, the engine's own order (statuses, then the reaction's cleanse).
- Data: `game/data/ui/battle_sandbox.json → part_cues.cinder_matron` = parts `["Crust"]`, `show_on_skills:
  ["recrust"]`, `show_on_reaction: true`, `hide_on_statuses: ["armor_break"]`. Keyed by creatures.json row id.
- Wiring: `BattleStage.choreo` got a setter that attaches the helper (a retry's new sequencer replaces it), so
  `battle_controller.gd` (990 lines) and `battle_choreo.gd` (1000, at the cap) are untouched.
- Parts are toggled with `find_child(name).visible`, the same way CreatureActor's phase `hide`/`show` does;
  CreatureActor (character's file) is unchanged.
- Tests: `tests/unit/test_battle_part_cues.gd`, on the battle sandbox with the `ch05_cinder_matron` encounter and the
  real sequencer: Armor Break hides it (and a miss or another status does not), `recrust` shows it after the Pour
  broke it off, a water hit in the Pour shows it (the hit marked `reacted` by `BossMechanics.after_action` itself),
  and with choreography playing nothing changes until the contact beat.
- **Open (not UI's):** enemies.json's `cinder_matron` row has no `model` yet, so in play she is still a primitive
  stand-in and the cue has nothing to show; the test lends her `cinder_matron_battle.tscn` through
  `CreatureModels.models()` for its own battles and takes it back. When creatures adds the `model` field the hook
  works with no further change.

## Review log
