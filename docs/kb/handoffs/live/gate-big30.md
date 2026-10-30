# Gate big30 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 46d8a067 (Merge lead/gate-big29).

## Pinned heads (merged --no-ff, in order; the Lead's priority first)
- claude/hero-integration @ 3b8d02d7
- claude/env-art @ 937389e9
- claude/act1-chapters @ 88db8446
- claude/env-art-b @ af85efce
- claude/audio @ d04d7942
- claude/characters @ 3bb5084b
- claude/m2-slice @ e262e104
- claude/creatures-b @ 589c2767
- claude/battle-presentation @ 5dfae816
- claude/audio @ 1b52f647
- claude/battle-presentation @ 15d1b779
- claude/characters @ de7e4e3d
- claude/creatures-b @ 90073e53
- claude/env-art-b @ 944f7d2c
- claude/ui @ df8e23d0

The Lead's list:
- integration-qa @ 3b8d02d7 traces the Drownbell return (Haluna's reveal held 3.1 s by VillagerLayer's per-frame builds).
  It files **M3-HER-1168 for creatures** (villagers built off the main thread) plus a LEAD-ASK. The fix itself isn't
  pushed yet; it goes in when it posts.
- In: env-art's newest (the last Oruvel outrigger, the Ch4 beauty pass), act1-chapters 3e62a325, env-art-b fd5cf5a8, and
  every other new head. characters' d8c9b942 syncs Sefir's shipped poses (big29's routed red).
- act2-plan and creatures had no new commits.

## Resolutions
- Every merge was clean.
- **Merge fallout, fixed (63f6aa2b):** validate_data flagged music.json `battle.pending_encounters` still listing
  ch14_malcor_venn, ch14_water_steps and ch16_abiding_guard, now that act1-chapters' encounters.json has them. Audio's
  own rule is "an id here drops off once encounters.json has it", and the cues were already wired under
  battle.encounters, so I removed them. ch14_hold_the_steps stays pending.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1062 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ 63f6aa2b

## Fast gate
- Selected: 104 test files (plus test_cutscene_face_per_actor and test_villager_routines, to re-check big29's routed reds).
- Lane A (mine): 52; lane B (GATE-HELPER): 52, in `gate-big30-lanes-b.txt` @ f2b6b633.

## Fast-gate results
- Import check clean · boot 0 ERROR lines · log check 0.
- Lane A (mine, 52 files): 50 green. **test_cutscene_face_per_actor** is green again (characters' d8c9b942 synced Sefir).
  - **test_qa_capsules** 3/1: abiding_first, abiding_guard and court_stillguard fight as primitive stand-ins (no actor
    scene). They are new foes from act1-chapters' f0739178 (M4-A2P-1200, ch14_water_steps) and the Ch16 guard; no branch
    ships their bodies. Routed: **act1-chapters**, which should file the body requests with the creature/character seats.
  - **test_villager_routines** 19/1 (Kell's row matches 7 stage actors): unchanged from big29; creatures has no new
    commits. Still routed: **creatures**.
- Lane B (GATE-HELPER, 52 files @ f2b6b633, arrived 20:51): all green.
- Tools suite (-j 2): beyond the known test_palette_check, test_screenshots and test_villagers:
  - **test_act1_audio_audit** and **test_battle_vfx_coverage**: skills `cut_the_line`, `court_reinforce` and `court_wait`
    (act1-chapters' new Ch14 fights) have no sound or effect entry and no gap note. Routed: **act1-chapters** (with
    requests to audio and battle-presentation, or gap notes).
  - **test_rig_integrity** (Asha, Pell, Liss, Rhen, Ysolde and Stillguards A/C/D/E): body-boundary and garment-penetration
    limits fail on poses from characters' new clip work (for example `turn_back@8`, `wake@8`). This is classified by the
    failing poses and the related characters test_hero_clips red (big29), **not probed on claude/characters** (about 4 min
    per rig; 15-min rule). Routed: **characters**.
  - **test_hero_clips** (characters) and **test_zone_map_pois** (m2-slice): unchanged from big29; still routed.

GATE-FAST-DONE @ df6b2f93 (merge-approved: the one batch-caused red, music.json pending, is fixed; the rest is
routed). Routed: act1-chapters (test_qa_capsules, test_act1_audio_audit, test_battle_vfx_coverage); characters (test_rig_integrity,
test_hero_clips); creatures (test_villager_routines); m2-slice (test_zone_map_pois). Known: test_palette_check, test_screenshots,
test_villagers.
