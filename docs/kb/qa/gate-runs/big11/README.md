# GATE lead/gate-big11 @ 23ea8c6f: the failing shots (PC gate runner, 2026-10-27)

- `<id>_out.png` is the WSL2 lavapipe render, and `<id>_diff.png` is compare.py's diff against big11's committed
  baselines. `compare.txt` lists every RMSE, and `blender_diffs.txt` holds the Blender step.
- The run used a fresh `.godot` import and 2 shards. Blender ran after the suite (base `claude/undertow-lead-handoff-ze8rrn`).
- Re-run from scratch by the new PC session: the PC went off mid-run on the first attempt.

## Summary: FAIL (expected drift, plus one new script error at shutdown)

| Step | Result |
|---|---|
| validate_data, audio, taskboard, gdlint, gdformat, manifest | ok |
| tools unittests | 1159 run, **1 known failure: test_shrine_gi_bake** (`test_the_bake_is_not_stale`; owned by the tracks). test_audio_loudness passed here. |
| Godot suite | **2738 run, 0 failed** (= the cloud) |
| Coverage gate, boot smoke | ok |
| Blender (13 jobs changed since ze8rrn: 9 kits, 4 creatures) | **13/13 identical** (rhen and toma weren't changed jobs this time) |
| Screenshots | **303 compared, 43 failed**. All 303 captured; both shards exit 1 on the script errors below. |
| Wall | lanes A+B 41 min (lane B 40.7 min), Blender 68 s; lane A re-run 19 min (see the note) |

**Note on lane A:** ci_local stops at the first failure, so the known test_shrine_gi_bake failure stopped lane A
before the Godot suite. The PC re-ran lane A on the same checkout with only that step made non-fatal (a local copy
of ci_local, not committed): Godot 2738/0, coverage and boot ok.

**New: `SCRIPT ERROR: Trying to cast a freed object.`** This error is printed at shutdown after 11 shots, all of
them villager, wildlife or Ch6 scenes: npc_haluna_dock, npc_haluna_market, npc_haluna_chapel, npc_haluna_lane,
npc_stage_field, wildlife_stage, wildlife_zone_brine_flats, wildlife_zone_brine_wrecks, wildlife_zone_underway_crown,
ch06_brine_road and ch06_brine_camp. Every capture itself is "ok", but capture.sh exits 1, so ci_local's own
screenshot step would fail. big10 had none: it's new in big11 (likely the villager/wildlife teardown, creatures and
m2-slice).

frame_clock and boot_card passed inside the 2738-test suite; no solo re-run was needed.

## The 43 failing shots

**New shots failing against their committed baselines (7 of big11's 11 new shots):**

| Shot | RMSE |
|---|---|
| wildlife_zone_brine_wrecks | 0.13466 |
| npc_haluna_lane | 0.11599 (the villagers, plus a wall block at bottom left) |
| wildlife_zone_brine_flats | 0.09370 |
| npc_haluna_chapel | 0.06385 |
| npc_haluna_dock | 0.06195 |
| npc_haluna_market | 0.03183 |
| ch06_brine_road | 0.02875 |

ch06_brine_camp, reefball_hud_choice, reefball_hud_goal and wildlife_zone_underway_crown pass.

**Newly failing (passed on big10): the Haluna villagers in the lane (5).** The diffs are the villagers, not the UI
(VillagerLayer, M2-FP-113):

| Shot | RMSE |
|---|---|
| field_objective_line, field_interact_prompt, field_area_title | 0.04019 / 0.04019 / 0.04018 |
| field_tip_card | 0.04014 (it failed on big10 at 0.02645 too) |
| dialogue_continue | 0.03743 |

**Repeats of big10's failures, with a changed RMSE (31):**
- **Boss intros (5):**

  | Shot | big11 | big10 |
  |---|---|---|
  | battle_boss_intro_drownbell | 0.12417 | 0.14139 |
  | battle_boss_intro_hullgnaw | 0.11489 | 0.26605 |
  | battle_boss_intro_matron | 0.08807 | 0.11633 |
  | battle_boss_intro_wraith | 0.06390 | 0.06078 |
  | battle_boss_intro_inquisitor | 0.05173 | 0.05418 |

- **Battle choreo/HUD (10):** choreo_hit 0.05810, opening_banner 0.01597, swell_brace 0.01381, choreo_melee 0.01156,
  choreo_toll 0.01094, choreo_read 0.01049, choreo_ko 0.01001, choreo_swap 0.00907, swell_chant 0.00846, and
  settings_accessibility 0.02151.
- **Arenas (16):** tideline 0.04768, causeway_route_afternoon 0.02381, route 0.02265, oruvel_raft_morning 0.01512,
  raft 0.01401, underway_tower 0.01271, underway 0.01154, ash_terrace_lanternfall 0.01041, terrace 0.01012,
  shoals 0.01008, causeway_disc_sunset 0.01000, camp 0.00990, causeway 0.00960, derelict_deck_night 0.00929,
  derelict 0.00924, tideline_dawn 0.00813.

Most moved closer to the baselines than on big10, since big10's re-approvals are in these baselines. Their
remaining drift is big11's battle and arena merges.

The Lead's expected "every UI page" drift didn't show up: of the UI shots, only settings_accessibility, the four
field_* shots and dialogue_continue fail, and the field_* and dialogue_continue diffs are the villagers.
