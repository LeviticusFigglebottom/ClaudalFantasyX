---
id: M3-ENV-1325
title: Ashcrown at player height: the black tier faces, the flat copper and lacquer (GPU QA row 26, part of M3-ENV-1316)
role: environment
status: review
owner_session: "env-art-b (claude/env-art-b, 2026-10-29)"
depends_on: []
milestone: M3
reviewer: art
---
## Goal
ADR 0041: Ch5 Ashcrown as walked reads final. The PC's GPU QA row 26 saw "untextured grey tiers"; env-art-b's 10-29
player-height walk saw why, and none of it needs a kit change:
- **The tiers' shaded faces and the flying stair's flanks were near black** (RGB 19, 25, 31 whatever the albedo). Two
  causes, both zone-side: the layout's `environment` row (which `Ch05Zone.apply_variant` writes over any grade) gave
  the sky fill 0.45, and the kit's stone slots apply their baked occlusion (UV2) at 0.8, so fill barely reached tens
  of metres of ashlar out of the sun.
- **The kit's copper, gold and lacquer slots are flat StandardMaterials**, so the trial's bowls, rods and veins read
  as mint plastic and the posts as red plastic.

## Done (env-art-b, 2026-10-29)
All in `tools/act1/ch05_ashcrown_dressing.py` (writes everything below, reproducibly):
- Zone materials next to the zone, swapped in by slot on every Ashcrown kit piece (`material_paths`):
  `ashcrown_copper_vein/_copper_new/_gold_leaf/_lacquer_red/_lacquer_black_material.tres` on `env_bronze` (patina,
  streaks, edge wear; the lacquers chip to their undercoat), and `ashcrown_ashlar/_dressed_material.tres`, the kit's
  own stone with the baked occlusion at 0.3/0.35, and `ashcrown_vein_material.tres` for the tiers' per-tier vein
  slots and the hall's floor vein (verdigris streaked over dark copper; a strike still lights them by
  `ZoneKitDressing.glow`'s overlay, which is unchanged).
- The fill: the layout's `environment.ambient_energy` 0.45 → 1.8, and the zone's own grade
  `ashcrown_day_environment.tres` (env-art's Ch5 temple grade with the same fill) in the dressing.
- The flat grey ash dunes are the kit's ash soil as designed (the volcano's slope); not changed.

- **The arenas** `ashcrown_forecourt_day` and `ashcrown_anvil_court` (`b_arenas.py`): the same slot swaps through a
  new `KitSlotSwaps` node (`game/levels/act1/kit_slot_swaps.gd`, ZoneKitDressing's `swap_slots` for written scenes)
  at the end of each scene; the forecourt's fill is the zone's 1.8 (the court keeps its interior fill).

## Left for env-art (M3-ENV-1316)
The same flat slots in the kit itself (its preview and any other user of `ac_*`).

Checks: Godot `--filter=` ashcrown 22/0, ch05 13/0, zone_kit 12/0, battle_arena 18/0; tools test_b_arenas +
test_arenas (22); gdlint/gdformat; validate_data; taskboard --check. Self-rendered
`ch05_ashcrown_causeway/_forecourt/_tiers/_crown/_court`, `battle_arena_ashcrown_forecourt_day/_anvil_court`,
`battle_boss_intro_matron` (no baselines for the zone shots yet) and 30 player-height walk views.

## Review log
