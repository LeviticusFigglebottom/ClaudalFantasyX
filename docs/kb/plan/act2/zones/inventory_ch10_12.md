---
draft: pre-gate
scope: the Act II kits for Ch10–Ch12 already on branches (env-art's chapters), against ADR 0041 §3's bar
author: env-art-b, 2026-10-30, on claude/env-art-b (merged with integration @ d987cc6b)
---
# Ch10–Ch12 kits: inventory against the final bar

Method: each kit's `TARGETS` against the committed glbs; its material slots against the Haluna kit's materials
(a StandardMaterial with a flat colour is "flat"); arenas, LUTs and baselines on the tree; zone dressing files.
The renders aren't re-judged here: the first PC renders of the kit rows are in `docs/kb/qa/gate-runs/big14/out/`
on act1-chapters, creatures and battle-presentation (act2_plan §3).

## Summary
| Kit (`assets_src/environments/kits/haluna/`) | Pieces | Built | Flat slots in use | Arena | LUT | Placed in a zone |
|---|---|---|---|---|---|---|
| `ossa_fen.py` (Ch10) | 7: `fen_bank_ground`, `mangrove_tree`, `mangrove_dead`, `reed_bed`, `fen_far_mangroves`, `kirru_roost`, `name_shell_cord` | 7/7 | `kit_fen_canopy_far`, `kit_fen_reed` (and `kit_interior_dark`) | `ossa_fen_roots` (baseline) | `lut_ch10_fen` (in the arena) | **no** (greybox) |
| `reedhollow.py` (Ch10) | 4: `root_walk_6m`, `reed_causeway_6m`, `reed_platform_6m`, `clutch_stone` | 4/4 | none found | — | as Ossa Fen | **no** |
| `lowlight.py` (Ch11) | 13: `engine_hall`, `conduit_run`, `lamp_niche_tier`, `conduit_housing`, `lowlight_nave_bay`, `lowlight_nave_bay_broken`, `well_shaft`, `vey_arcade_bay`, `vey_gallery_bridge`, `lowlight_sanctum`, `strangler_fig`, `vey_gallery_walk_6m`, `lowlight_lamp_bench` | 13/13 | `kit_lowlight_conduit`, `kit_lowlight_copper`, `kit_salt_glass` (and `kit_interior_dark`) | `lowlight_engine_hall` (baseline) | `lut_ch11_vey` (in the arena) | **no** |
| `keth.py` (Ch12) | 16: `quellan_inn`, `quellan_well`, `hesk_dais`, `keth_terrace_ground`, `lit_terrace_wall`, `seep_pool`, `pass_cord`, `cairn`, `keth_far_ridges`, `keth_road_switchback`, `keth_scree_slope`, `woolback_trough`, `cloudloom_hall`, `keth_curtain`, `quellan_house`, `woven_awning` | 16/16 | `kit_keth_grass`, `kit_keth_seep` (and `kit_interior_dark`) | `keth_seep_terrace` (baseline) | `lut_ch12_heights` (in the arena) | **no** |

## Against the bar
- **Built:** every listed piece exists as a glb, and every kit's tools test builds it.
- **Not final yet:**
  1. **No zone is dressed.** All seven Ch10–Ch12 zones (`ossa_fen`, `reedhollow`, `sunken_vey`, `lowlight`,
     `keth_pass`, `quellan`, `cloudloom`) are greybox, with no `*_dressing.json`. That's the act's largest volume of
     work (plan §5.1 item 4).
  2. **Flat slots** reach the screen in every kit: the fen's far canopy and reeds; Lowlight's conduits, copper and
     salt-glass (salt-glass may be intended as clear); Keth's grass and seep. Each needs a zone look (the Act I
     method: `kit_material_paths` and `KitSlotSwaps`), or a shader material in the kit. The flat `kit_interior_dark`
     is fine where it's only a void's backing; check each use.
  3. **The zone grades** exist only inside the arenas (the LUTs above). Each zone needs its own Environment, and its
     layout's `environment` row must carry the grade's fill (Act I's Ashcrown lesson).
  4. **The mangrove vegetation system** for Ossa Fen (plan: "no mangrove vegetation system beyond the kit trees") is
     env-art's gap.
  5. **Swap maps** exist in the art sheets (ossa_fen.md §4, lowlight.md §5, keth_pass.md §6). They are the
     dressing generators' input.
  6. **Guardrail check (act2_plan §2a):** `keth.py`'s snow must stay weather (no frozen pools or ice). `seep_pool`
     is a seep, not ice. Re-check when the Ch12 grade lands.
- **Sources of light:** `lowlight.py`'s conduits are the bound light's own source (good); the Keth inn and
  Cloudloom need lamp pieces for any fire light their grades add.

## Not in this inventory
Creatures, Vowbound, music and menus are in act2_inventory.md. Ch13–Ch16's kits are specified one zone at a time
in this folder.
