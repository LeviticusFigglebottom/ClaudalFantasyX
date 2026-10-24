---
id: M2-UI-05
title: Vowbound commands and HUD (call, the Vowbound's menu, Dismiss, the call preview)
role: ui
status: doing
owner_session: "agent-a9031fbbea441e647"
depends_on: [M2-CMB-04]
milestone: M2
request-from: combat
---
## Goal
M2-CMB-04 added the Vowbound engine rules (battle_ctb.md § Vowbound, ADR 0027): `engine.summon(id)`, `engine.dismiss()`, `engine.vowbound.unleash(engine, targets)`, `callable_ids`, the refusal reasons, and the `called` and `departed` signals. Nothing draws them yet, so Ilun cannot be called in play.

## Acceptance criteria
- [ ] The controller builds `engine.vowbound` from the story flags before `begin()` (`ch03_ilun_bound` → `ilun`; the engine never reads `Game`)
- [ ] The caller's root menu gets a call row: greyed with its reason (loc keys for `not_bound`, `silenced`, `vowbound_fallen`)
- [ ] The Vowbound's own menu: its skills, its finisher when the gauge is full, and Dismiss. Swap, items and escape are hidden or greyed while it is out
- [ ] Pillar 4: the timeline previews the call (the caller's `call_rank` delay once the party returns) and the dismissal
- [ ] The stage: the stood-down party steps off the field, and the Vowbound stands in (placeholder, as the Drownbell's stand-ins do)
- [ ] Tests and the affected screenshots

## Notes
- Keep the controller edit small (it is near the lint cap). A `BattleVowboundHud` view built like `BattleBossHud` (claude/first-playable) is the clean shape.
- The summon cinematic (SPEC §6.3) is a cinematics task, not this one.
