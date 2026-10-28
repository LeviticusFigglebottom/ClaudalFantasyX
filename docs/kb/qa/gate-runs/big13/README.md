# Gate run: lead/big13 renders (cloud lavapipe)

Tree: `lead/big13` @ 1d83553f plus `e2744adf` (Shell Shrine GI rebake), pushed as `lead/gate-big13`.
Renderer: Godot 4.6.3 (debian 4.6.3+ds-2) Forward+ on Mesa lavapipe, llvmpipe (LLVM 22.1.8, 256 bits), the full manifest in 2 shards (`LP_NUM_THREADS=2` each), then one `compare.py` over all 402 shots. Fresh `.godot/` import, exit 0, no crash. **No baselines were approved.** The Lead views and approves.

## Summary

| Compared | Passed | Failed (over limit) | No baseline | No capture |
|---|---|---|---|---|
| 402 | 250 | 98 | 54 | 0 |

`compare.txt` is the final compare. For every non-PASS shot this folder has `<id>_out.png` (the capture), `<id>_diff.png` (baseline darkened, error in red; over-limit shots only) and `<id>_sheet.jpg` (baseline | out | diff side by side, 640 px panels; out only for a new shot).

## Capture incidents (all re-rendered; none is in the final result)

- `villager_tavi_front`: the shard process crashed at startup (SIGSEGV after `propagate_notification()` called off the main thread, exit 134). A rerun alone rendered it in 17 s and it PASSES (0.00025). Treat it as a flake.
- Five shots hit capture.sh's 600 s per-shot guard at `LP_NUM_THREADS=2` with 2 shards running at once: `npc_haluna_dock`, `npc_haluna_market`, `npc_haluna_lane`, `slice_beach_h06_toma` and `slice_dock_night_yes`. They are slow, not deadlocked: `npc_haluna_chapel` finished in 543 s in the shard. Rerun alone at `LP_NUM_THREADS=4` with `HYMN_SHOT_TIMEOUT=1800`, they took 363 to 439 s each. **These five sit near or over the default 600 s guard on a 4-CPU host. They need a cheaper settle, or a per-shot timeout, before the next cloud gate.**
- Wall time: shards 9918 s and 10159 s (about 2.8 h) plus the 2021 s rerun.

## Over the limit, near it (13: within 7% of the limit, likely drift)

| Shot | RMSE | Limit |
|---|---|---|
| `battle_arena_causeway` | 0.00851 | 0.00800 |
| `battle_arena_derelict_deck_night` | 0.00843 | 0.00800 |
| `battle_choreo_vowbound_rise` | 0.00810 | 0.00800 |
| `battle_vowbound_call` | 0.00806 | 0.00800 |
| `battle_vowbound_out` | 0.00806 | 0.00800 |
| `battle_swap_menu` | 0.00805 | 0.00800 |
| `battle_swell_modes` | 0.00805 | 0.00800 |
| `battle_choreo_swap` | 0.00805 | 0.00800 |
| `battle_hud_preview` | 0.00804 | 0.00800 |
| `battle_swell_chant` | 0.00803 | 0.00800 |
| `battle_swell_ring` | 0.00802 | 0.00800 |
| `ch07_bell_galleries` | 0.00802 | 0.00800 |
| `battle_swell_brace` | 0.00801 | 0.00800 |

## Over the limit, real changes (85: view the sheets)

| Shot | RMSE | Limit |
|---|---|---|
| `slice_verse_steps` | 0.19261 | 0.00800 |
| `battle_boss_intro_hullgnaw` | 0.16210 | 0.00800 |
| `battle_boss_intro_drownbell` | 0.16177 | 0.00800 |
| `creature_mangrove_drowner_risen` | 0.14641 | 0.00800 |
| `wildlife_zone_underway_crown` | 0.13523 | 0.00800 |
| `creature_mangrove_drowner` | 0.13322 | 0.00800 |
| `battle_heroes_attack` | 0.13192 | 0.00800 |
| `ch09_corrow_strand` | 0.10905 | 0.00800 |
| `battle_boss_intro_matron` | 0.10139 | 0.00800 |
| `slice_beach_h05_asha` | 0.10132 | 0.00800 |
| `slice_beach_h06_toma` | 0.10046 | 0.00800 |
| `battle_boss_intro_reach` | 0.09695 | 0.00800 |
| `haluna_h02_tidewall_lane` | 0.08149 | 0.00800 |
| `field_interact_prompt` | 0.08124 | 0.00800 |
| `battle_choreo_toll` | 0.07692 | 0.00800 |
| `dialogue_continue` | 0.07641 | 0.00800 |
| `dialogue_voice_over` | 0.07641 | 0.00800 |
| `ch04_ferry_deck` | 0.07607 | 0.00800 |
| `npc_haluna_lane` | 0.07369 | 0.00800 |
| `field_tip_card` | 0.07191 | 0.00800 |
| `creature_tower_limpet` | 0.07171 | 0.00800 |
| `field_objective_line` | 0.07135 | 0.00800 |
| `field_area_title` | 0.07005 | 0.00800 |
| `battle_arena_wall_head` | 0.06721 | 0.00800 |
| `battle_ch08_stair_hold` | 0.06720 | 0.00800 |
| `creature_avalanche_ram` | 0.06548 | 0.00800 |
| `battle_heroes_hit` | 0.06383 | 0.00800 |
| `battle_heroes_ko` | 0.05840 | 0.00800 |
| `npc_haluna_dock` | 0.05517 | 0.00800 |
| `iskarra_i03_broken_tower` | 0.05464 | 0.00800 |
| `battle_heroes_victory` | 0.05310 | 0.00800 |
| `battle_heroes_finisher` | 0.05186 | 0.00800 |
| `iskarra_i02_gate_from_the_plaza` | 0.05117 | 0.00800 |
| `haluna_h01_village_from_sea` | 0.04941 | 0.00800 |
| `battle_heroes_idle` | 0.04921 | 0.00800 |
| `iskarra_p01_plaza_dusk` | 0.04873 | 0.00800 |
| `battle_choreo_read` | 0.04805 | 0.00800 |
| `creature_slag_tortoise` | 0.04679 | 0.00800 |
| `creature_reef_crab_attack` | 0.04018 | 0.00800 |
| `reefball_hud_choice` | 0.03903 | 0.00800 |
| `battle_statuses` | 0.03876 | 0.00800 |
| `battle_statuses_colorblind` | 0.03876 | 0.00800 |
| `ch09_corrow_road` | 0.03688 | 0.00800 |
| `battle_swell_glyph` | 0.03666 | 0.00800 |
| `battle_boss_intro_wraith` | 0.03626 | 0.00800 |
| `battle_choreo_cast` | 0.03612 | 0.00800 |
| `creature_tide_crawler` | 0.03456 | 0.00800 |
| `battle_heroes_cast` | 0.03228 | 0.00800 |
| `creature_shoal_skipper` | 0.03206 | 0.00800 |
| `field_menu_map_underway` | 0.03186 | 0.00800 |
| `creature_raid_hound` | 0.03019 | 0.00800 |
| `drownbell_flood` | 0.03007 | 0.00800 |
| `creature_spawn_polyp` | 0.02914 | 0.00800 |
| `brine_b01_arrival` | 0.02651 | 0.00800 |
| `corrow_c08_watcher_profile` | 0.02622 | 0.00800 |
| `battle_victory` | 0.02421 | 0.00800 |
| `creature_spar_wraith` | 0.02254 | 0.00800 |
| `battle_read_panel` | 0.02217 | 0.00800 |
| `creature_wall_polyp` | 0.02164 | 0.00800 |
| `ch07_bell_moorings` | 0.02137 | 0.00800 |
| `creature_drownbell_toll` | 0.02010 | 0.00800 |
| `creature_scuttler` | 0.01917 | 0.00800 |
| `brine_b05_barge_channel` | 0.01880 | 0.00800 |
| `battle_arena_causeway_route_afternoon` | 0.01654 | 0.00800 |
| `creature_cinder_matron` | 0.01524 | 0.00800 |
| `slice_haluna_villagers_village` | 0.01417 | 0.00800 |
| `battle_choreo_melee` | 0.01336 | 0.00800 |
| `battle_choreo_lamp_dive` | 0.01327 | 0.00800 |
| `battle_arena_ash_terrace_lanternfall` | 0.01299 | 0.00800 |
| `battle_choreo_ko` | 0.01240 | 0.00800 |
| `creature_bottle_hermit` | 0.01214 | 0.00800 |
| `creature_portraits` | 0.01201 | 0.00800 |
| `battle_arena_route` | 0.01176 | 0.00800 |
| `field_menu_codex` | 0.01121 | 0.00800 |
| `corrow_c01_wall_head` | 0.01074 | 0.00800 |
| `battle_choreo_hit` | 0.01061 | 0.00800 |
| `creature_wallcrab` | 0.00979 | 0.00800 |
| `battle_arena_oruvel_raft_morning` | 0.00975 | 0.00800 |
| `creature_reef_crab` | 0.00958 | 0.00800 |
| `ch08_corrow_stair` | 0.00914 | 0.00800 |
| `haluna_h10_dock_night` | 0.00912 | 0.00800 |
| `ch06_brine_camp` | 0.00904 | 0.00800 |
| `battle_hud_16x10` | 0.00881 | 0.00800 |
| `creature_wreck_crab` | 0.00860 | 0.00800 |
| `boot_title` | 0.00824 | 0.00400 |

## No baseline (54: new shots, out only)

`ch05_pemakar_harbour`, `ch05_pemakar_crown`, `asha_clip_bow_palms_flat`, `rhen_clip_lift_housing`, `toma_clip_stack_bowls`, `ysolde_clip_read_letter`, `rhen_clip_talk_explain`, `liss_front`, `liss_back`, `liss_three_quarter`, `liss_face`, `liss_face_stylized`, `liss_silhouette_vs_rhen`, `liss_clip_haul_rope`, `reefball_outfitter`, `creature_wakefin_body`, `creature_tannin_archer`, `creature_gallery_ray`, `creature_rime_urchin`, `creature_conduit_crawler`, `creature_ridge_lynx`, `creature_cord_moth`, `creature_glass_skate`, `creature_root_crab`, `creature_fen_leech`, `creature_scree_crawler`, `creature_rim_crawler`, `creature_flat_engine`, `slice_dock_night_yes`, `ch01_oruvel_dressed`, `ch01_underway_crown`, `ch01_underway_gallery`, `slice_verse_hall`, `ch01_o07_name_board`, `ch01_o10_gull`, `battle_arena_seawall_stairhead_storm`, `battle_arena_seawall_stairhead_hoist`, `battle_arena_seawall_stairhead_surge`, `battle_arena_coilspire_headland_path`, `battle_arena_coilspire_tier_landing`, `pemakar_p04_harbour_day`, `pemakar_p11_sea_cut_weir_day`, `tamsule_tp01_port_and_bell`, `tamsule_tp03_floating_market`, `tamsule_tp05_gantry_foot`, `battle_arena_keth_seep_terrace`, `battle_arena_lowlight_engine_hall`, `battle_arena_ossa_fen_roots`, `battle_arena_bridal_barge_night`, `battle_arena_ansedra_lagoon_escape`, `revenant_tells_reflection`, `revenant_tells_reflection_off`, `revenant_tells_shadow`, `revenant_tells_shadow_off`

## Spot check

`field_tip_card`, `battle_heroes_attack` and `creature_reef_crab` were viewed. They are valid, lit renders (no black or partial-import frames). The diffs are content changes: palms at another wind phase, a recomposed battle-heroes attack, crab leg poses. The other field and UI shots near 0.07 (`field_*`, `dialogue_*`) are probably the same Haluna wind drift, but only `field_tip_card` was viewed.
