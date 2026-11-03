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
