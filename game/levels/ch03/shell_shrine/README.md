# Shell Shrine trial (M2-FP-16)

`shell_shrine.tscn` is the slice's temple trial (vertical_slice.md B07). The causeway head opens it (`first_playable.json` `haluna.ending_scene`), and its flooded door leads to Cutscene B (`shell_shrine.next_scene`).

| File | Role |
|---|---|
| `shell_shrine_trial.gd` (`ShellShrineTrial`) | The rules, headless: basins, outlets, the water's trace, filling, draining, the idle hint, and a shortest-solution search. |
| `shell_shrine_level.gd` (`ShellShrineLevel`) | The view: it builds the **greybox** room from the JSON, turns basins on interaction, lights the channels on the water's path, raises the pool, sinks the door, empties the side pool, offers the charm, plays the hint bark, and hands off at the exit. |
| `shell_shrine.tscn` | The root, environment, oculus light, Rhen, the camera director (S03 overview, with S02 at the threshold) and the S04/S05 inserts. |
| `game/data/trials/shell_shrine.json` | Puzzle data, layout and greybox metrics (see its `doc`). |

**Puzzle.** The spring pours into `b1`. Each basin pours out of one lip, toward `outlets[rotation]`: another basin, the inner pool, the side sluice, or a spill grate. Using a basin turns it 90° clockwise. While the water reaches the inner pool, the pool fills over `fill_sec`; when it's full the door sinks and stays open (`ch03_shrine_door_open`). The first time the water reaches the sluice, the side pool empties for good (`ch03_side_pool_drained`), and the net-float charm can be taken: the `net_float_charm` key item and `ch03_found_net_float`, which Cutscene B reads. Toma's one hint (`ch03_trial_hint`) comes after `hint_idle_sec` with no turn. Water that loops is lost.

**M2-FP-22 (review-sweep-Q):** there are four basins. The water starts out going round (b1 → b4 → b1), so b4 has to be turned *away* from b1, through two spill grates, before it feeds b3. The shortest solution is 6 turns (b1 → b4 → b3 → the pool), and the side pool takes 4 (b1 → b2 → the sluice). Draining it never breaks the main route, because rotations cycle. A random turner needs a median of about 75 turns, so Toma's 90 s hint can play. `tools/tests/test_shell_shrine_trial.py` holds the band (5–10) and the random-turner floor (a median of 20 or more, seeded). Change the data, not the code.

**Greybox.** It stands in until M2-ENV-03, and Audio is M2-AUD-01. Asha and Toma aren't in the room yet (there are no followers), and the hint is Toma's voice only.

**Hooks.** `trial.rotated`, `flow_changed`, `pool_filled`, `side_pool_drained`, `hint_due`, and the level's `charm_taken`.

**Tests.** `tests/unit/test_shell_shrine_trial.gd`, `tests/integration/test_shell_shrine_level.gd`, and the whole thread in `test_fp_thread.gd`.
