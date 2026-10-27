---
id: M2-HER-1108
title: "Repoint the battle hero stand_ins at the HeroBattleActor wrappers (request to ui-menus)"
role: ui
status: todo
owner_session: ""
depends_on: [M2-HER-1103, M2-UI-07]
milestone: M2
request-from: combat
---
## Goal
The real heroes already stand in battle (M2-UI-07 points `stand_ins.<hero>.scene` at characters' `*_battle.tscn`), but
they play the clips with the AnimationPlayer's flat 0.3 s blend: the attack's anticipation is swallowed and a revive
springs up. The hero track's `HeroBattleActor` wrappers (`game/hero_motion/battle/<hero>_battle_actor.tscn`, on
claude/hero-integration and in big9) instance the same models and add per-pair cross-fades (strikes in fast, hit
0.06 s, ko → idle 0.9 s), an offset idle phase per hero and idle micro-motion. They go through the same BattleClips
path, so no code change is needed.

## Acceptance criteria
- [ ] Once big9 is on the integration branch, `game/data/ui/battle_sandbox.json` `stand_ins.{rhen,asha,toma}.scene`
      point at `res://game/hero_motion/battle/{rhen,asha,toma}_battle_actor.tscn` (three lines; the hunk is in
      `docs/kb/tech/hero_battle_proposed.patch`).
- [ ] Also Ysolde (2026-10-27): `stand_ins.ysolde` is still a capsule, though characters' `ysolde_battle.tscn` exists.
      Give it `"scene": "res://game/hero_motion/battle/ysolde_battle_actor.tscn", "yaw_deg": -90.0` (her contract clips
      are placeholders until M2-HER-1115; the wrapper tunes those too).
- [ ] The battle filter stays green; the battle shots that show heroes are re-captured, viewed and re-approved.

## Notes
- The other hunks of `hero_battle_proposed.patch` are already applied by their owners: the KO no-sink is on
  claude/ui and claude/battle-presentation (`fighter_stand_in.gd` set_ko), and the three choreo test hunks are on
  claude/battle-presentation. Only the stand_ins repoint is left.
- The hero track will check every clip transition on the integration branch after the repoint (M2-HER-1103).

## Review log
