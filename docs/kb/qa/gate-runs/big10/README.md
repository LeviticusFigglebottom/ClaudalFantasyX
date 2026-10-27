# GATE lead/gate-big10 @ 181708a7: the failing shots (PC gate runner, 2026-10-27)

`<id>_out.png` is the WSL2 lavapipe render, `<id>_diff.png` compare.py's diff against the baselines committed on
big10 (which predate big9's 48 re-approvals). `compare.txt` lists every RMSE; `blender_diffs.txt` the Blender DIFFs.
Fresh `.godot` import, 2 shards.

## Summary: FAIL (expected drift plus the known M2-CHR-11 Blender DIFFs)

| Step | Result |
|---|---|
| validate_data, tools unittests, audio, taskboard, gdlint, gdformat, manifest | ok |
| Godot suite | **2637 run, 0 failed** |
| Coverage gate, boot smoke | ok |
| Blender (22 jobs changed since `lead/gate-big9`) | **20 identical, 2 DIFF**: rhen, toma (M2-CHR-11; the same rebuilt hashes as on big9) |
| Screenshots | **292 compared, 51 failed** |
| Wall | lanes A+B 35 min, then Blender 17.6 min |

This run skipped Blender inside ci_local (`HYMN_SKIP_BLENDER=1`) and ran `verify_blender_builds.py` for the changed
jobs afterwards, so the known DIFF can't stop lane A before the Godot suite (it did on big9).

## The 51 failing shots, against big9's 48

**New (6), not in big9's list:**

| Shot | RMSE | What changed |
|---|---|---|
| battle_boss_intro_hermit | 0.03932 | boss intro (new arena/boss work) |
| battle_boss_intro_inquisitor | 0.05418 | boss intro |
| battle_boss_intro_wraith | 0.06078 | the whole scene: the derelict deck at night, a new stage, hero rigs |
| field_hero_party | 0.06583 | all three heroes (new models and clips) |
| field_hero_rhen_walk | 0.07908 | Rhen's walk |
| field_hero_gait_strip | 0.07228 | the gait strip (Rhen, 15 frames) |

**Repeats of big9 with the same RMSE (37):** the same image as big9's re-approved render, so they pass once big10 is
merged over the integration branch's baselines. They are battle_hud_preview, battle_swap_menu, battle_statuses (+_colorblind), save_shrine_field,
battle_swell_{ring,modes,chant,brace,glyph}, battle_read_panel, battle_opening_banner, battle_vowbound_call,
battle_choreo_{cast,support,read,swap,lamp_dive}, the 16 battle_arena_* shots, drownbell_flood, settings_accessibility and field_tip_card.

**Repeats whose render CHANGED again in big10 (8): view these, big9's approval doesn't cover them:**

| Shot | big9 | big10 |
|---|---|---|
| battle_boss_intro_hullgnaw | 0.08516 | **0.26605**: the camera is reframed; the whole boss is in view (the playtest complaint looks fixed) |
| battle_boss_intro_drownbell | 0.06428 | 0.14139: a sunset stone-disc arena |
| battle_boss_intro_matron | 0.03139 | 0.11633 |
| battle_choreo_hit | 0.04019 | 0.09462 |
| battle_choreo_melee | 0.05422 | 0.07103 |
| battle_choreo_toll | 0.08298 | 0.07337 |
| battle_choreo_ko | 0.04996 | 0.06012 |
| creature_portraits | 0.07891 | 0.07096 |

**big9 failures that now pass (3):** battle_hud_16x10, battle_hud_21x9, formation_menu.

The manifest grew 281 → 292 with 11 new shots (asha/rhen/toma_clip_turn and _walk_cycle, ashcrown_a10_plume_from_the_rim,
oruvel_o17_pen_split, npc_stage_field, wildlife_stage, field_hero_gait_strip). All pass except field_hero_gait_strip
(0.07228 against its own new baseline, listed above).
