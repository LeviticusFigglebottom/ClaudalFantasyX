# Gate big49 (fast gate, ADR 0205)

Base: **lead/gate-big48 @ 9f9f5011** (not merged yet). Merge big48 first; big49 then adds only the commits below.

## Pinned heads (merged with --no-ff in this order)
1. claude/audio @ d7b5bcec: **big47's routed red fixed**, M3-AUD-865 the storm beds import looping (storm_gale, storm_wall). Log: MERGE-READY @ d3052411.
2. claude/ui @ f136fa1f: **big47's routed reds fixed** (status help's UI sound hooks for the panel and tip card, audit notes for the controller and
   chip; test_status_names allows Ch4's beat). Log: MERGE-READY @ c71894a7.
3. claude/m2-slice @ 029bba8a: beat audit (the last three frame-timed cutscene shots hold their line), Act III M5-A3P-1203/1701/1704/1707 (the
   Ending's last stops, the credits' beach-rite vignette, Ch18's seen flags, the Ch17 ledger page). Log: held-timing shots self-rendered and viewed.
4. claude/env-art-b @ b10d44fd: **FAST-TRACK follow-up**, Corrow's storm sea takes no sun glint (slice-polish's W20). Log: MERGE-READY.
5. claude/act1-chapters @ 05b7d427: M4-A2P-071..075 taken; the Act II break at the Prologue's plaza (LEAD-ANSWERED); ch16_act_break_vigil
   shot (pending). Log: MERGE-READY.

## Conflicts
- game/data/ui/credits.json (ui's M5-A3P-1700 sections vs slice-polish's vignette): ui's sections and layout kept, with slice-polish's
  `beach_rite` vignette scene (`res://game/flow/ending_beach_rite.tscn`) and `next_scene` (post_credits.tscn). Both scenes exist.
- PROVENANCE, loc and shots.json by merge_union. test_hero_walk_cycle.gd.uid: the same uid on every branch.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1139 files) · manifest valid (812 shots, no duplicate
id) · no duplicate loc keys · no new duplicate PROVENANCE rows · no conflict markers · no gate-run images.

GATE-BUILT @ ff9eefd2

## Fast gate
- Godot tests filtered to the touched areas: status, credits, audio_loops, storm, ch08, ch14_16, ch17, ch18, ending, end_card, zone_kit_waters,
  beat. Tools suite: 226 units with -j 2. Unique XDG_DATA_HOME; HYMN_STEP_TIMEOUT=10800.

## Fast-gate results
- Import clean (godot_log_check 0); boot smoke 0 ERROR lines.
- **Godot: all green.** status 82/0, credits 8/0, audio_loops 3/0, storm 48/0, ch08 25/0, ch14_16 6/0, ch17 3/0, ch18 4/0, ending 4/0,
  end_card 7/0, zone_kit_waters 4/0, beat 6/0.
- **Tools: big47's routed reds are green**: test_act1_audio_audit (ui's hooks), test_audio_data (audio's storm loops), test_status_names (ui).
- New batch reds (both Act III, both on claude/m2-slice's own head too):
  - **test_act1_flow_audit** (unreachable `ch01/oruvel arrive[0]`; `credits_seen` never set) and **test_qa_flag_reach** (`credits_seen` has no
    setter: "a softlock"). slice-polish's M5-A3P-1203/1701 (e086e9a7) adds an Oruvel arrival row for E7 that waits on `credits_seen`. The flag
    is set at runtime, but through `Game.set_flag(CreditsRollModel.SEEN_FLAG)` (ui's credits_roll.gd), a constant the audits can't read, so the
    softlock is a false positive. Routed: **ui** (set it as `Game.set_flag(&"credits_seen")`, CLAUDE.md §3's form) or **slice-polish**.
  - Still routed: test_arenas sunken_vey_gallery (**env-art**, big48).
  - This container's LFS pointers: test_dialogue_clarity, test_direction_holds. The standing list: test_cutscene_sfx_files, test_freed_cast_lint,
    test_creatures. Known: test_palette_check, test_screenshots.

GATE-FAST-DONE (merge-approved under the standing rule: the two new reds are an audit-visibility false positive in Act III content, routed;
every Godot filter is green).

## Shots (18: the new Ending and act-break shots, the beat audit's changed shots, the Corrow storm shots)
Published on `lead/gate-big49-shots` @ b50a9362 in `docs/kb/qa/gate-runs/big49/` (out, out/diff, compare.txt, contact grids g00–g02).
- **0 PASS, 4 DRIFT, 14 NO-BASELINE, 0 failed to capture.** The container restarted mid-capture; the one missing shot (ch08_storm_wall_f08w)
  was re-captured alone.
- Viewed: **ch08_wall_falls_w20 no longer has the sun glint on the storm sea** (env-art-b's FAST-TRACK follow-up), and the vortex holds over the
  breach. ch08_corrow_storm is the wall walk under the vortex. The Ending shots (e11 the dark sea at Haluna's dock, e12 the beach rite with Toma's
  line, e13 the first lamp in Oruvel) and ch16_act_break_vigil (the Prologue's plaza) read cleanly.
- Drifts: slice_prologue_vigil_line 0.125 and slice_verse_hall 0.195 (the beat audit's held frames), ch01_o10_gull 0.052, ch08_corrow_lake 0.040
  (the storm fills and the glint).

**Note (the Lead's FINAL, 21:50):** the project is stopped, and the Lead folded every track head straight into -ze8rrn, so big48's and big49's
content is already on the integration branch (its shots.json has one `battle_arena_oruvel_raft_storm`). These two gate branches stay for their
logs and shots only; on resume, view big48's and big49's shots and the routed reds (env-art: sunken_vey_gallery; ui or slice-polish: credits_seen's
setter visible to the audits; battle-presentation/env-art: the Hullgnaw intro's black silhouette).

LEAD-REVIEW big49: 18 shots (4 DRIFT, 14 NO-BASELINE), Godot all green; content already folded in by the FINAL; view on resume
