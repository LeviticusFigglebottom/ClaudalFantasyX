# GATE lead/gate-big8 @ aa55b77e: the failing shots (PC gate runner, 2026-10-24)

For each failing shot, `<id>_out.png` is the WSL2 lavapipe render and `<id>_diff.png` is compare.py's diff (the
baseline darkened, per-pixel error in red). `compare.txt` lists the RMSE values. **238 compared, 29 failed.**

| Group | Shots | Note |
|---|---|---|
| Arenas (env-art kits, expected) | 16 `battle_arena_*` | 0.014 (underway_tower) to 0.247 (raft) |
| Arena-based battle shots (expected) | 6 `battle_boss_intro_*`, `drownbell_flood` | the boss intros stage in the kit arenas |
| Creatures (expected) | `creature_portraits` | |
| **Not on the expected list** | `field_area_title`, `field_interact_prompt`, `field_objective_line`, `field_tip_card`, `dialogue_continue` | **UI unchanged.** The difference is the Haluna backdrop (the tidewall stone and the sand): env-art's kit change. All at 0.057-0.069 |

Expected drifts that **passed** (so their baselines already match): `settings_hub`, `settings_accessibility`, `shrine_s01`-`s05`.
