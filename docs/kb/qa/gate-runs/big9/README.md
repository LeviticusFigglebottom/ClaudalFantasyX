# GATE lead/gate-big9 @ ae4666e0: the failing shots (PC gate runner, 2026-10-24/27)

For each failing shot, `<id>_out.png` is the WSL2 lavapipe render and `<id>_diff.png` is compare.py's diff (the
baseline darkened, per-pixel error in red). `compare.txt` lists the RMSE values; `blender_diffs.txt` lists the Blender
DIFFs. Fresh `.godot` import (NIT-902 scripts), 2 shards.

## Summary: FAIL (expected drift plus the known M2-CHR-11 Blender DIFFs)

| Step | Result |
|---|---|
| validate_data, tools unittests (1101, 17 skipped), audio, taskboard, gdlint, gdformat, manifest | ok |
| Godot suite | **2561 run, 0 failed** (frame_clock and boot_card didn't flake, so no rerun was needed) |
| Coverage gate, boot smoke | ok |
| Blender (51 jobs changed since `claude/undertow-lead-handoff-ze8rrn`) | **40 identical, 11 DIFF**: rhen, toma, villager_{neme, osu, child, vendor, reed, netmender, fisher, tavi, kell}. All are the M2-CHR-11 kind: `Head`/`HairHead` POSITION/NORMAL and the head normal maps (AVX2 host). sefir, ysolde, asha and every creature and kit job are identical. |
| Screenshots | **281 compared, 48 failed** |
| Wall | lanes A+B 37 min (Blender 25.6 min); lane A rerun without Blender 18 min |

The Blender DIFF stopped the first lane A before the Godot suite, so lane A was rerun with `HYMN_SKIP_BLENDER=1` on
the same ref. The gate's up-front `--import` aborted (core dump) on that rerun; ci_local's own Godot import step passed.

## The 48 failing shots

| Group | Shots | RMSE | Note |
|---|---|---|---|
| Battle with the hero rigs (expected) | battle_hud_preview, battle_swap_menu, battle_swell_{ring,modes,chant,brace,glyph}, battle_statuses(+_colorblind), battle_read_panel, battle_opening_banner, battle_vowbound_call, battle_choreo_{melee,hit,cast,support,read,ko,swap,lamp_dive,toll}, battle_hud_16x10, battle_hud_21x9 | 0.023-0.083 | The diff is the party only: the hero models replace the capsules. |
| Arenas (hero rigs + env-art kits, expected) | 16 battle_arena_* | 0.024-0.119 | Party plus kit backdrops (raft, route, underway largest). |
| Boss intros, Flood (expected) | battle_boss_intro_{hullgnaw,drownbell,matron}, drownbell_flood | 0.015-0.085 | Hullgnaw's diff is the backdrop; **its camera is still framed too close** (the open playtest item, not in big9). |
| Field | save_shrine_field 0.032, field_tip_card 0.026 | | save_shrine_field: the real hero model at the shrine plus tip card text; field_tip_card: tip card text only. |
| Menus/UI | settings_accessibility 0.028, formation_menu 0.013 | | The settings labels shift; formation: the "fallen" note re-wraps. Both read correctly in the out PNG. |
| Creatures | creature_portraits 0.079 | | A new grid layout (more creatures). |

**For the Lead to look at:**
- `battle_choreo_toll`: Toma and Asha are real models, but a tan **capsule** stands in front of the camera (third party
  slot, Ysolde). It's unchanged from the baseline, so Ysolde is still a placeholder in battle, or the
  capsule is a stray stand-in.
- No other field shot drifted. The hero field shots (`field_hero_party`, `field_hero_rhen_walk`,
  `hero_cutscene_turn_strip`) pass, so their baselines already show the real heroes. The cutscene shots
  (`cutscene_hold_prompt`, `cutscene_act_card`) pass too; there's no shot of the prologue's "everyone is still here"
  colour in the manifest.
