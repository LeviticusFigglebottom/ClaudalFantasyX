# Gate big48 (fast gate, ADR 0205)

Base: **lead/gate-big47 @ cc107cea** (not merged yet; it holds the five FAST-TRACKs) merged with claude/undertow-lead-handoff-ze8rrn @ 8f593652
(big46 merged). Merge big47 first; big48 then adds only the commits below.

## Pinned heads (merged with --no-ff in this order)
1. claude/hero-integration @ 3a5d60cd: the Act I inventory refresh (2 low), placeholder_audit's out-of-scope arenas, test_hero_walk_cycle.gd.uid. Log: MERGE-READY @ 0ff56578.
2. claude/combat-systems @ 554bc2d4: M3-CMB-1252 (FieldSpell's result shape, a Silenced caster refused, a field Mend); M4-A2P-1202 (the sim's
   Vowbound call, p90 on banded rows). Log: MERGE-READY @ 2acd3abc.
3. claude/characters @ 38681bbf: row 55, Sabe's crop. Log: MERGE-READY @ 59fb4fc4.
4. claude/ui @ 59c46501: M4-A2P-081 portraits (the Kirru, the Ullari woman), M5-A3P-1700 credits (facts only, Godot's MIT notice, the OFL fonts). Log: MERGE-READY @ 1e18ff21.
5. claude/battle-presentation @ 4d4e35e7: M3-BPR-451 one Undertow per fight (storm tests on a real storm arena); row 70's float_fade_sheet tool.
   Log: MERGE-READY @ 304146c5 (later commits: a tool and its uid, log lines).
6. claude/m2-slice @ 9ba2de2a: **FAST-TRACK 4, M3-CIN-1252**, the storm cutscenes show the Undertow's vortex (Ch1's Rising, Ch8 B17's W20); a beat audit
   fix for slice_prologue_vigil_line. Log: MERGE-READY @ b3264a22.
7. claude/act1-chapters @ c3d84bdf: live log only (the Ch8 storm fights confirmed; LEAD-ANSWERED on oruvel_raft_storm).
8. claude/env-art @ ef8c6260: Act II, M4-A2P-115 (Quellan at eye height), M4-A2P-1501 (the Sunken Vey's flotsam; no flicker in Ch11).
9. claude/env-art-b @ 5c1c5b5a: storm_arenas.py, test_b_arenas and test_storm_arenas drop oruvel_raft_storm (the Lead's 18:04); M4-A2P-046
   drowned_choir_storm built; M5-A3P-1500 Ch17's dry-dock walk; M3-ENV-1341 answered. Log: MERGE-READY @ 74df3bdb (+ a uid).

Not moved: audio (its big47 head stands), creatures, creatures-b, act2-plan.

## Conflicts
- PROVENANCE, shots.json and loc by merge_union (ui, env-art).
- docs/kb/tasks/M3/M3-ENV-1341-storm-fight-arenas-fyi.md (battle-presentation's ask vs env-art-b's answer): both kept.
- arenas.json: storm.arenas now has oruvel_raft_storm and drowned_choir_storm; storm.pending is empty. oruvel_raft_storm is env-art's scene.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1134 files) · no duplicate loc keys · no new duplicate
PROVENANCE rows · no conflict markers · no gate-run images.

GATE-BUILT @ 79a3c1ff

## After the build
- big47 merged into -ze8rrn at cc107cea, **before** big47's shots.json fix (6b8990de: `battle_arena_oruvel_raft_storm` listed twice, so
  compare.py rejects the manifest). big48 merges lead/gate-big47 @ 6b8990de and drops the duplicate again (env-art-b's head carries both
  entries too), then merges -ze8rrn @ d89a9e23 (docs). **Merging big48 fixes the integration branch's manifest.**

## Fast gate
- Godot tests filtered to the touched areas: storm, battle_arena, battle_sim, field_spell, credits, portrait, cutscene, ch01_thread, drowned_choir,
  lacquer_court, ch08 (ch15 and ch16 match no test file). Tools suite: 226 units with -j 2. Unique XDG_DATA_HOME; HYMN_STEP_TIMEOUT=10800.

## Fast-gate results
- Import clean (godot_log_check 0); boot smoke 0 ERROR lines.
- **Godot: all green.** storm 48/0 and battle_arena 20/0 (big47's storm-arena reds are gone: env-art-b's tests no longer claim
  oruvel_raft_storm), battle_sim 56/0, field_spell 8/0, credits 8/0, portrait 22/0, cutscene 112/0, ch01_thread 2/0, drowned_choir 2/0,
  lacquer_court 2/0, ch08 25/0.
- **Tools: test_b_arenas is green** (big47's red cleared). One new batch red:
  - **test_arenas::test_scenes_are_reproducible (arena='sunken_vey_gallery')**: env-art's M4-A2P-1501 (9c1be5bf) adds flotsam to
    `game/levels/ch11/sunken_vey/sunken_vey_dressing.json`, which `arena_scenes.py` reads, but the committed arena scene wasn't regenerated
    (one more ext_resource). Routed: **env-art** (`arena_scenes.py --arena sunken_vey_gallery`, commit the scene). Act II only.
  - Still routed from big47: test_act1_audio_audit (**ui**: StatusGlyph, BattleStatusTips, StatusHelpPanel, StatusTipCard need a UI sound hook),
    test_audio_data (**audio**: storm_gale and storm_wall imports have loop=false).
  - This container's LFS pointers: test_dialogue_clarity, test_direction_holds. The standing list: test_cutscene_sfx_files, test_freed_cast_lint
    (audio), test_creatures (creatures-b), test_status_names (ui). Known: test_palette_check, test_screenshots.

GATE-FAST-DONE (merge-approved under the standing rule: the one new red is Act II content, routed to env-art; every Godot filter is green).

## Shots (36: the new shots, the tracks' self-rendered ids, the storm arenas and the Hullgnaw intro)
Published on `lead/gate-big48-shots` @ 5c679464 in `docs/kb/qa/gate-runs/big48/` (out, out/diff, compare.txt, contact grids g00–g05).
- **1 PASS, 11 DRIFT, 24 NO-BASELINE** (pending: the storm cutscene shots ch01_rising_eye, ch01_oruvel_storm, ch01_hullgnaw_rises,
  ch01_going_under_u10, ch01_sadi_mooring, ch08_storm_wall_f08w, ch08_storm_eye_f08e, ch08_wall_falls_w20, plus credits_roll, magic_menu, the status
  help pair and the two storm arenas; never baselined: the Act II/III zone shots ch14_court_*, ch15_open_sea_dawn, ch16_choir_*, ch17_hollowmere_*,
  battle_arena_drowned_choir_ring/_storm). Four cutscene shots hung past 600 s under the parallel gate load and were re-captured alone with
  HYMN_SHOT_TIMEOUT=1800; 0 failed in the end.
- Viewed (FAST-TRACK 4): **the vortex now reads in the storm cutscenes**: the Rising's eye, Oruvel's storm over the reef ("The reef's showing"), Ch8's
  storm wall and eye, W20 over the breach (with a bright sun glint on the sea, which env-art-b's big49 fix removes). battle_arena_drowned_choir_storm
  has rain over the Choir's ring.
- **Still watch: battle_boss_intro_hullgnaw (0.384):** the Hullgnaw is a near-black silhouette (as in big47).
- The slice drifts (slice_prologue_vigil_line 0.16, slice_beach_h05_asha 0.29, slice_beach_h06_toma 0.28, slice_dock_night_yes 0.03) are the beat
  audit's held-timing frames: the line is the same, and the frame is a later moment than the old baseline.

LEAD-REVIEW big48: 36 shots (1 PASS, 11 DRIFT, 24 NO-BASELINE), Godot all green, fixes the integration branch's duplicate shot id; routed: env-art (sunken_vey_gallery); watch the Hullgnaw intro silhouette; merge when you approve
