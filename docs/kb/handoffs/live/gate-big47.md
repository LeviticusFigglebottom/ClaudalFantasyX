# Gate big47 (fast gate, ADR 0205)

Integration base: claude/undertow-lead-handoff-ze8rrn @ e2411fb0 (big45 plus the 11-03 Lead docs). big46 (characters' row 56 notch fix) isn't
merged yet; characters' head here carries it.

## Pinned heads (merged with --no-ff in this order)
The human's 11-03 playtest FAST-TRACKs, all five items:
1. claude/hero-integration @ e7cae923: **FAST-TRACK 1**, M3-HER-1231, the walk cycle no longer stops (3aee287c); placeholder_audit's summon
   scope (8c922bf4). Log: MERGE-READY @ 817699bb.
2. claude/combat-systems @ fa7476aa: **FAST-TRACKs 2 and 5**, M3-CMB-03..06: the Relighting Wick (revive) in the Act I economy, the fallen
   up at 1 HP after a win, field-castable spells (FieldSpell), the solo Ch1 Hullgnaw eased. Log: MERGE-READY @ 08eaf116 (plus log commits).
3. claude/characters @ 4a30d472: row 56 (big46's notch fix, verified), row 55 (Fenn, Sabe), row 54 steps (Sefir's hair). Log: MERGE-READY @ 6e3cd47a.
4. claude/ui @ e58f9938: **FAST-TRACKs 3 and 5**, M3-UI-1250 (status help, first-time cards, Codex Afflictions), M3-UI-1251 (the field Magic page on
   FieldSpell), M3-UI-1253 (field revive), Act I rows 68, 69, 73. Log: MERGE-READY @ 73699ed9.
5. claude/battle-presentation @ 60f90177: **FAST-TRACKs 3 and 4**, M3-BPR-450/451: statuses on the body (overlay, aura, prop, icon) and
   the storm fights' sky (BattleStorm). **Not marked MERGE-READY in its log** (one commit, 60f90177); taken as Act I FAST-TRACK content.
6. claude/act1-chapters @ 66c19e6e: **FAST-TRACK 4**, M3-C01-1252, the storm's fights on storm arenas with storm music. Log: MERGE-READY @ 1bcae269.
7. claude/audio @ 9ff655c1: **FAST-TRACK 4**, M3-AUD-865 storm music, M3-AUD-866 status, cure and revive cues. Log: MERGE-READY @ 25256466.
8. claude/env-art @ 9b51f2c8: **FAST-TRACK 4**, M3-ENV-1340 (oruvel_raft_storm with the Undertow); PC rows 24, 47, 77, 86. Log: MERGE-READY @ 4f450a7c.
9. claude/env-art-b @ 4d3c97ef: **FAST-TRACK 4**, M3-ENV-1334 (the Ch8 storm arenas); rows 71, 72, 82, 84; the anvil court rewrite. Log: MERGE-READY @ 211d8bd7.

Not moved since big45: m2-slice (slice-polish), creatures, creatures-b, act2-plan.

## Conflicts
- docs/kb/ownership.md (battle-presentation, env-art-b): three appended rows, all kept.
- assets/PROVENANCE.md, tests/screenshots/shots.json (audio, env-art): merge_union.
- **env-art-b vs env-art: both built `oruvel_raft_storm`** (env-art's 52bf4c11 through `arena_scenes.write_arena`; env-art-b's 6b8e416d through its
  new `tools/act1/storm_arenas.py`). env-art owns `assets/environments/arenas/**` (ownership.md), so **env-art's scene and preview are kept**, and
  env-art-b's duplicate PROVENANCE row is dropped. arenas.json takes act1-chapters' `storm` table, with `oruvel_raft_storm` pointed at its own scene
  and moved from `storm.pending` to `storm.arenas` (act1-chapters' logged next step; `drowned_choir_storm` stays pending).
- Merge fallout: two task files with id M3-ENV-1340 (env-art's arena; battle-presentation's storm FYI request). The request is renumbered
  **M3-ENV-1341** (its file, M3-BPR-451's and battle_status_looks.md's references).

### LEAD-NOTES (overlaps for the Lead to route; not changed by the gate)
- `tools/act1/storm_arenas.py` (env-art-b) still writes `oruvel_raft_storm`; re-running it would overwrite env-art's scene. Route: env-art-b to drop
  its Ch1 id, or env-art to hand the arena over.
- Three storm mechanisms meet in the Ch1 fights: BattleStorm (battle-presentation, keyed by encounter in storm_fights.json, adds the storm and the
  Undertow at spawn), env-art's storm arena (its own Undertow), and act1-chapters' storm table. A Ch1 storm fight may draw two Undertows. Also,
  storm_fights.json lists `ch08_headland_*` and `ch08_flue_moths` as storm fights, while act1-chapters' doc says the headland fights come before the storm.
  The shots will show it; route: battle-presentation + act1-chapters + env-art.

## Build checks
validate_data 0/0 · taskboard --check clean (after the renumber) · dlgc --check clean · gdlint and gdformat clean (1131 files) · no duplicate loc
keys · no conflict markers · no new binary over 5 MB · no gate-run images.

GATE-BUILT @ 16ee7393

### oruvel_raft_storm: env-art's scene (the Lead, 18:04)
2635d0a3 briefly took env-art-b's build (it passed test_storm_arenas); 76a19716 reverts it per the Lead's 18:04 answer: **the scene is env-art's**
(as first resolved). env-art-b's branch already drops Ch1 from `tools/act1/storm_arenas.py`, test_b_arenas and test_storm_arenas (8b92b3c3,
MERGE-READY for big48), so those two env-art-b reds below clear in big48. The shots capture env-art's scene.

## Fast gate
- Godot tests filtered to the touched areas, one run per filter: battle, status, storm, field_, hero, item, magic, codex, read_panel, shop, victory,
  audio, music, resident, formulas (the battle filter ran on env-art's scene, which is the final tree). Tools suite: 224 units with -j 2.
- XDG_DATA_HOME and logs under the gate's scratch dir; HYMN_STEP_TIMEOUT=10800. No GATE-HELPER lane.

## Fast-gate results
- Import clean (godot_log_check import 0 on the second pass); boot smoke 0 ERROR lines.
- **Green:** status 82/0, field_ 148/0, hero 121/0, item 83/0, magic 7/0, codex 16/0, read_panel 13/0, shop 28/0, victory 5/0, resident 15/0,
  formulas 42/0.
- **battle 888/2, audio 196/1, music 20/1: this container's LFS pointers**, not the batch: test_battle_stings (the boss stings under
  assets/lfs/ don't import), test_battle_audio's fire hit (`abl_ember` is a pointer, so `hit_fire` plays), test_music_transitions (`prologue_dusk`'s
  beat grid is a pointer). Audio's own log reports the same three.
- On env-art's scene (the final tree): **storm 41/2** (test_storm_arenas: oruvel_raft_storm has no rain, rim, soak or StormFarPlane, and
  `wetted_count`) and **battle_arena green** apart from that. On env-art-b's (2635d0a3, reverted): storm 41/0 but test_battle_arenas'
  storm-arena move red. env-art-b's big48 head removes oruvel_raft_storm from its tests, so the final tree's storm reds are expected to clear there.
- **Tools suite, batch-caused:**
  - test_b_arenas (arena='oruvel_raft_storm'): env-art-b's generator no longer matches the scene; cleared by env-art-b's big48 head (8b92b3c3).
    test_arenas is green on env-art's scene. The old ashcrown_anvil_court red is fixed.
  - **test_act1_audio_audit:** four new ui classes take input with no UI sound hook (StatusGlyph, BattleStatusTips, StatusHelpPanel,
    StatusTipCard; M3-UI-1250). Routed: **ui** (or audio for the hooks).
  - **test_audio_data::test_every_loop_imports_looping:** `assets/audio/ambience/storm_gale.ogg.import` and `storm_wall.ogg.import` are committed
    with loop=false (audio's M3-AUD-865 storm beds; red on claude/audio too). Routed: **audio**.
- Tools, this container (LFS pointers): test_dialogue_clarity, test_direction_holds. The standing routed list, unchanged: test_cutscene_sfx_files'
  sequencer check and test_freed_cast_lint (audio), test_creatures (creatures-b), test_status_names (ui). Known: test_palette_check, test_screenshots.

### ROUTED (big47)
- **env-art-b:** done on its branch (8b92b3c3, big48): storm_arenas.py, test_b_arenas and test_storm_arenas drop oruvel_raft_storm.
- **ui:** test_act1_audio_audit's four status-help classes. **audio:** the two storm beds' loop flag.
- **battle-presentation + act1-chapters + env-art (FAST-TRACK 4):** BattleStorm still adds its storm to the Ch1 fights on top of a storm arena,
  and storm_fights.json treats the ch08 headland fights as storm fights while act1-chapters' table doesn't. See the shots.

GATE-FAST-DONE (merge-approved for the FAST-TRACKs, with the routed reds above: the storm-arena reds that env-art-b's big48 head clears, and two small ui/audio reds; every other
red is this container's LFS pointers or the standing list).
- Merge fallout found by the shot compare: `tests/screenshots/shots.json` carried `battle_arena_oruvel_raft_storm` twice (env-art's and
  env-art-b's entries; merge_union keeps both when both sides add the same id). Fixed on this branch: env-art's entry (pending_baseline) kept.

## Shots (48: the tracks' self-rendered ids, the new shots, and the battle HUD/status/storm-arena shots the batch can affect)
Published on `lead/gate-big47-shots` @ 39e79747 in `docs/kb/qa/gate-runs/big47/` (out, out/diff, compare.txt, contact grids g00–g07).
- **5 PASS, 31 DRIFT, 12 NO-BASELINE** (pending: battle_status_help, battle_status_tip, magic_menu, ch01_net_pen, field_hero_walk_release,
  battle_arena_oruvel_raft_storm; never baselined: battle_arena_derelict_spar_wraith, battle_arena_drowned_choir_ring, ch08_corrow_flood,
  ch08_coilspire_gate, ch08_corrow_storm, crowd_zone_corrow). 0 failed to capture.
- Viewed (FAST-TRACKs):
  - **Statuses (3):** battle_statuses/_colorblind show the icons over the heads and the on-body ring/tint; battle_status_help (the Statuses
    panel: list, Last Tide's text, how it ends) and battle_status_tip read. magic_menu (FT5): caster, Asha's Mend, target with MP/HP preview.
  - **Storm (4):** battle_arena_oruvel_raft_storm has the storm sky over the raft-town and the Hullgnaw on the deck; **the vortex isn't in the rest
    frame** (env-art puts it 18 km behind the foe). The seawall stair-head arenas have rain and the storm grade; the merlons still hide the
    Undertow (M3-ENV-1341's ask, open).
  - **Watch: battle_boss_intro_hullgnaw (0.395):** the Hullgnaw reads as a near-black silhouette against the storm sky (the baseline shows its
    lit teal-green shell). Route: battle-presentation / env-art (the storm rim or grade doesn't light the boss).
- The remaining drifts are the merged content: Sefir's hair (row 54), Fenn's and Sabe's crops (row 55), Asha's skirt (row 56) in asha_clip_*, the
  battle HUD's help line and rank legend (ui, row 73) across battle_hud_preview, swap_menu, read_panel and heroes_victory, field_menu/status_menu
  /codex (ui), the Ch8 arenas and zones (env-art-b rows 71, 82, 84), oruvel_o17_pen_split and brightwater_landing_f01 (env-art rows 77, 24).

LEAD-REVIEW big47: 48 shots (5 PASS, 31 DRIFT, 12 NO-BASELINE), all five FAST-TRACKs in; routed reds: ui (audio hooks), audio (storm bed loops), env-art-b's storm reds clear in big48; watch the Hullgnaw intro silhouette; merge when you approve
