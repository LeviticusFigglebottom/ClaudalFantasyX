# Live log: env-art-b environment

Environment-art track B, cloud session `session_01F3vrUNt6trAMrjeYavaDNC`, branch `claude/env-art-b` (cut from the
integration branch `claude/undertow-lead-handoff-ze8rrn` on 2026-10-28). **This environment owns this file**
(CLAUDE.md §7a). The Lead is `session_018aiGwGLGkxsnMnu8VfCu1m`.

## Scope (ADR 0041, the Lead's brief of 2026-10-28)
The Act I zones of Ch5–Ch9 (`game/levels/ch05..ch09`) and the battle arenas those chapters use, at final quality:
dressed, lit, walkable and seamless, with no greybox geometry or material and no box stand-ins. env-art keeps the
Prologue–Ch4 zones and the shared kits; act1-chapters keeps the story (layouts' marks, triggers, states, scripts,
dialogue, casts). Claims: the last row of `docs/kb/ownership.md`.

## How this branch is built (read first when merging)
- **It carries two unmerged track heads**, because Ch5–Ch9's dressing and kits live there and building beside them
  would only make conflicts:
  - `claude/act1-chapters` @ 47de5a00: every Act I commit up to Ch6's last pieces (M3-C05-1213 Pemakar,
    M3-C07-1211 the galleries, M3-C08-1210 Coilspire, M3-C09-1209 Ch9, the casts, the walks). Nothing of its Act II
    (Ch10+) work.
  - `claude/env-art` @ 9cced155 (its head at 01:14): the Ch5 Pemakar pieces (M3-ENV-1214), the Tamsule port kit
    (M3-C07-04), the Ch8 arenas (M3-ENV-713), Ashcrown's flights (M3-ENV-715), and its paused later-act work.
  Merging this branch brings both in; their own heads merge cleanly on top afterwards.
- **Not applied here:** battle-presentation's `M3-BPR-407-seawall-repoint.patch` (the Ch8 encounters onto env-art's
  seawall/coilspire arenas). It is theirs, and the Lead applies it after env-art. Until then the Ch8 fights still
  load `wall_head_storm` (the greybox).

## NEW ACCOUNT (from 2026-10-25)

### 2026-10-28
- **Ch7 port, M3-C07-04 (ea946ec8):** `ch07/tamsule` dressed from env-art's port preview
  (`tools/act1/ch07_tamsule_port_dressing.py`): the quay, market, stilt lane, gantry foot, Tavi's boats, the harbour
  and the trader, and the Bell's whole ring at (0, −1.6, −75). The river is water now (it was a floor 1 m down):
  invisible rails on every open deck edge (`tamsule_collision.json`) keep the player on the decks. The Bell's mark and
  T08/T09 look at the kit's ring; the zone takes the galleries' Ch7 noon sun and grade. New test
  `test_ch07_port_walkable` (6/0); `--filter=ch07` 12/0; `--filter=cutscene_walks` 1/0. Shots `ch07_tamsule_mouth`,
  `_market`, `_gantry` (new, rig `ch07_tamsule_shots.tscn`): viewed; the stalls, bunting, Bell and water read. The two
  capsules in them are Liss and Kerrid, who have no field body yet (characters' work, not kit).
- **MERGE-READY @ 00e15816** (with ea946ec8 above). Items:
  - **M3-ENV-1301, Ch5 Pemakar (70664cd0):** env-art's harbour pieces placed (M3-ENV-1214): `harbour_quay` replaces
    the module quay; `wake_wall` and `crown_bell` follow their blocks; the `sea_cut_weir` at the quay's EAST END
    (env-art's preview put it at the bottom channel's outlet, x −39, but B05's staging is at the quay's east end, so the
    weir moved to the story: cheek tops flush with the deck, `--weir-relayout` moved the weir folk 4.6 m east with
    P11/P12/P02D); a lamp pillar and the spill's light at night; the dawn variant takes `pemakar_day_environment.tres`.
    No greybox kept in Ch5 Pemakar.
  - **M3-ENV-1302, Ch8/Ch9 (00e15816):** `ZoneKitDressing` `waters` and `storms` rows (game/levels/act1, additive;
    **act1-chapters please note**). Ch8's Flood (waist-deep) and Lake, Ch9's lake and Iskarra's sea are water. **The
    Undertow now appears in Ch8** (it was missing entirely): Corrow from the beacon's opening to the cut rope (a new
    `Storm` marker block, `--storm-relayout` in `ch08_corrow_dressing.py`), and from Coilspire's gallery on the
    StormWall block. Ch9's landing, Pell's rocks (path on the RocksDown ramp), the mole gangway and the vigil burner are
    kit pieces. Coilspire's flue gates, niche seal, lamp niche and wright's mark (M3-ENV-1222's Coilspire half) too.
    Ch8 and Ch9 keep no greybox except Coilspire's `Virel` (the Vowbound's body: creatures-b).
  - **Kit pieces (99063a1e):** Corrow `b_strand.py` (3), Coilspire `b_trial.py` (4), Ashcrown `b_trial.py` (11, for
    the next item). Each kit rebuilt `--all` in Blender 5.0.1: every older glb, texture and material byte-identical.
  - **Checks run:** Godot `--filter=` zone_kit 10/0, corrow 18/0, ch08 23/0, ch09 12/0, ch05 8/0, pemakar 10/0,
    ch07 12/0, ch07_port 6/0, cutscene_walks 1/0; tools test_corrow_kit, test_coilspire_kit, test_ashcrown_kit OK;
    gdlint/gdformat, validate_data 0/0, taskboard --check. `test_screenshots` is red only for the new shots' missing
    baselines (I never write baselines).
  - **Checks skipped:** the full Godot suite and coverage (no battle/progression code); the whole tools suite (only
    the kits' tests can see these changes); Blender verify for other jobs (none touched).
  - **Known, not mine:** "12 resources still in use at exit" after the ch08/ch09 thread tests; it happens with the
    storms removed too, so it predates this branch.
  - **Known, follow-up:** the weir's cut has no channel feeding it down the flank, so by day its water reads as a pale
    slab; Coilspire's niche and mark have no shot (the flue-key wheels hang in front of them from every interior view).
- **In progress (M3-ENV-1303): Ch5 Ashcrown on its kit.** Merging hero-integration @ bccce923 (the steep-stair
  traversal) next; plan in the task file.

### Render requests
(Self-rendered per TRACK-RULES; lines are SELF-RENDERED notes.)
SELF-RENDERED @ ea946ec8: ch07_tamsule_mouth, ch07_tamsule_market, ch07_tamsule_gantry — new shots, read final (Liss and Kerrid are capsules: no field body yet).
SELF-RENDERED @ 00e15816: ch05_pemakar_weir, ch05_pemakar_harbour_day, ch08_corrow_storm, ch08_coilspire_storm, ch08_coilspire_gate, ch08_corrow_flood, ch08_corrow_lake, ch09_corrow_landing, ch09_corrow_rocks, ch09_corrow_strand — new shots (the strand is an existing baseline: no longer dark); viewed after fixes (re-aimed cameras, the flood lifted, the rocks' lamp). ch05_pemakar_harbour drifts by the new quay (the party's lanterns are the two glows).
