---
id: M3-CMB-03
title: "FAST-TRACK: a revive item in the Act I economy (in battle and in the field)"
role: combat
status: review
owner_session: "combat-systems (claude/combat-systems)"
depends_on: []
milestone: M3
request-from: lead
reviewer: progression
---
## Goal
The human's playtest (2026-11-03): an original revive item that brings a KO'd ally back with some HP, usable in battle and in the field, reachable in Act I (shops and early drops or chests) and priced sensibly.

## Acceptance criteria
- [x] The item exists with an original name and lore: the **Relighting Wick** (`relighting_wick`, M1-CMB-06), a taper lit from a living lamp (glossary: "lamp" is a living being's inner glimmer). Revive 25% max HP, rank 3, `field: true`. Its description now says it works in the field; a glossary row records it.
- [x] Act I economy: Haluna Market sells it from the first visit (`ch02_met_asha`, was gated on the Drownbell), at 240 lume (was 300: four early fights); the Hullgnaw (Ch1) and the Spar-Wraith (Ch4) drop one each (100%), and the Gull Harrier (Ch2–Ch3 regular) 4%.
- [x] Tests: data rows and drops pinned (tests/unit/test_battle_revive_economy.gd); the field revive path (ItemsMenuModel) pinned in the same file.
- [x] Requests: ui-menus (field-menu use, M3-MNU-05) and battle-presentation (VFX check, M3-BPR-446).

## Notes
- The battle path (ItemBattleAction revive, BattleItemUse) and the field path (ItemsMenuModel.field_action: `field: true` + an ally target) already handled revives; the playtest gap was reach: no shop sold it before Ch3's Drownbell, no foe dropped it, and no chest held it.
- Chests in Ch2–Ch3 flows are slice-polish's (`game/flow/**`, `game/data/flow/chapters/ch0[1-3].json`); not touched here.

## Review log
