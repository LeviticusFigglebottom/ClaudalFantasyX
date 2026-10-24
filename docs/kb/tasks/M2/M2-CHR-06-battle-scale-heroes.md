---
id: M2-CHR-06
title: Battle-scale Asha, Rhen and Toma (LOD and import rule for the battle stage)
role: character
status: review
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
reviewer: lead
depends_on: [M2-CHR-01, M2-CHR-02]
milestone: M2
request-from: lead
---
## Goal
Battle-scale versions of the three heroes so the battle stand-in capsules can be swapped; coordinate the hook with
the battle scene owners in characters.md.

## Delivery (2026-10-24)
- `game/characters/heroes/{asha,rhen,toma}_battle.tscn` (claimed `game/characters/**` in ownership.md): each instances the
  hero's LOD1 GLB (29.5k / 27.0k / 27.0k triangles, 1.42 / 1.31 / 1.43 MB). The `characters` import rule gives them the
  hero materials, and now the clips too (`animations.strip_suffixes: ["_lod1"]`, so `asha_lod1` shares `asha_clips.tres`).
- Shots `asha_battle_idle`, `rhen_battle_idle`, `toma_battle_idle` (the stage plays `idle`; Toma's clips arrive with M2-CHR-04,
  so his shot is in the A-pose until then).
- **The hook is UI+Combat's:** filed **M2-UI-07** (FighterStandIn instances a `"scene"` spec). Battle clips beyond the body
  set (attack, cast, hit, KO) on request once the hook exists.

