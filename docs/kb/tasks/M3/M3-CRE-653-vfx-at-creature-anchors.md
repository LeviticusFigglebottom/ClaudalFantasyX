---
id: M3-CRE-653
title: "Request to battle VFX: start enemy spawn and KO effects at the creature's own anchors (CreatureActor.vfx_anchor)"
role: rendering
status: todo
owner_session: ""
depends_on: [M3-CRE-651]
milestone: M3
request-from: creatures
---
## Goal
ADR 0041 asks that every Act I enemy have spawn and death VFX hooks. The creature side is in (M3-CRE-651):
`CreatureActor.vfx_anchor(&"wound")` and `vfx_anchor(&"core")` give the world position of the creature's weak point
and body centre, posed by the clip playing this frame, for all 20 Act I regulars (creatures.json `vfx_anchors`;
docs/kb/art/creatures/pipeline.md "VFX anchors").

Today `ko_release` (effects.json `events.ko`, plus `ko_overrides`) plays at the stand-in's `anchor_heights`, a
height fraction above the slot. On a long creature (the eel, the leech, the tide crawler) or a hovering one (the
gulls, the ashwing) that puts the effect beside the body, not in it.

## Ask (game/vfx/battle/**, game/data/vfx/battle/effects.json: yours)
1. **The KO:** when the stand-in's actor is a CreatureActor, play the KO effect at `vfx_anchor(&"wound")`. Fall back
   to the anchor height when it returns `Vector3.INF`.
2. **The spawn:** a foe joining mid-battle (`combatants_joined`; the polyps, any summon) and the opening line-up, if
   you have an entry effect. Use `vfx_anchor(&"core")`.
3. **Mid-battle hits:** keep `anchor_heights`, unless a hit on the weak point should read at the wound.

## Notes
- The anchor is a bone, so it moves with the clip: read it at the moment the effect starts, not at load.
- Bosses and the Vowbound are creatures-b's. They can add `vfx_anchors` the same way.

## Review log
