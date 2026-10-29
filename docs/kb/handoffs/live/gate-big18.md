# Gate session live log: big18

The big18 cloud gate session (`session_01UPFyEAXofxWazWNnRTzFGJ`) builds `lead/gate-big18`, runs every check and
publishes the shots to `lead/gate-big18-shots`. It never writes or approves baselines; the Lead views and approves
every shot. Same process as big17 (`gate.md` on `lead/gate-big17`).

## big18

GATE-BUILT big18 @ 782be497 (branch `lead/gate-big18`), from `claude/new-session-mj8c3c` @ 96222b30 (big17).

Pinned heads, merged with `--no-ff` in this order:
1. claude/env-art @ d63eeea3: PROVENANCE by merge_union; pc-gpu.md kept ours (newer); M3-ENV-750's task file took
   theirs (a superset: done, the reviewer's line).
2. claude/env-art-b @ 0e9db81d: ownership.md kept both rows (append-only).
3. claude/characters @ 9fe30416: pc-gpu.md ours. `oruvel_layout.json` scaleman: ours' position (m2-slice) with
   theirs' new `scaleman_actor.tscn` model. `test_fp_prologue.gd` took theirs (Pell and Liss both have bodies now).
4. claude/creatures @ 93829b74: shots.json by hand with merge_union's `merge_rows` (the criss-cross virtual base held
   conflict markers, so merge_union crashed; base = f6846325, creatures' big17 head). `test_zone_cast.gd` took theirs
   (creatures' fix of big17's known red "the fisher idles / out of step").
5. claude/creatures-b @ 4d0150e3: clean.
6. claude/battle-presentation @ b1316ebb: pc-gpu.md ours.
7. claude/act1-chapters @ e7b065b4:
   - `oruvel_layout.json` per key against the base: kell and O09 from theirs (only act1-chapters changed them, GPU QA
     row 23); scaleman, O02, O07, O10, skipper_sadi and sabe from ours (changed on ours; Ch1 is m2-slice's).
   - `oruvel_underway_layout.json` U03: both sides re-aimed it independently (m2-slice 70169542 "Rhen in the right
     third", act1-chapters cb97a0cf "stepped clear of the post"); kept ours (Ch1's owner). See LEAD-ASK below.
   - `ashcrown_layout.json`: theirs (act1-chapters owns Ch5 NPC placement: Kahre's actor, cameras) with ours'
     `"cast": "tender"` (characters' M3-CHR-519 named NPCs).
   - `coilspire_layout.json`: ours' casts (fenn, tender) plus theirs' new `virel` actor.
   - `tools/act1/ch08_coilspire_dressing.py`: a comment-only conflict, kept ours (env-art-b owns it).
   - M3-ENV-744's task: ours' `status: done` (the reviewer closed it as superseded), both review lines.
8. claude/ui @ 3b792de6: shots.json by the same best-single-base `merge_rows` (base b2118f76); pc-gpu.md ours.
9. claude/hero-integration @ b0ec6ffd: `test_hero_field_actor.gd` took theirs (hero-integration owns HeroFieldActor;
   its check follows the data, so it holds with Pell's model in); pc-gpu.md ours.
10. claude/m2-slice @ 8aa6f6a6: union files only.
11. claude/audio @ 1cb9654d: no new commits since big17, not merged.

Merge fallout fix (782be497): PROVENANCE's line union re-added 6 rows for deleted assets: the Haluna
banyan/windbreak placeholders (M3-ENV-750), the ch04 wake dressing's 3 files (M3-ENV-744) and an old
`shrine_offering.glb` row claude/ui still carries. Removed.

Checks at the build: validate_data 0 errors 0 warnings; taskboard --check ok; gdlint and gdformat --check clean;
no duplicate loc keys, PROVENANCE rows or shot ids (619 shots); no conflict markers; no `docs/kb/qa/gate-runs/**`
images.

LEAD-ANSWERED: Coilspire may show Virel twice. env-art-b's M3-ENV-1320 (22b289bf, already in big17) put her model in
the crown chamber as a dressing piece (`coilspire_dressing.json` "piece": "virel"). act1-chapters' M3-CRE-627
(ed235044) adds a ZoneCast `virel` actor on her coil, which hides after the binding. big18 keeps both, per ownership.
One of them should go, probably the dressing piece, since the actor handles the after-binding state. Route to
env-art-b and act1-chapters?
LEAD-ANSWERED: Ch1 U03 (Oruvel Underway) and O02/scaleman (Oruvel) were re-framed by both m2-slice and act1-chapters (GPU
QA row 23). big18 keeps m2-slice's (Ch1's owner). Check the shots; if act1-chapters' framing is wanted, it needs a
follow-up on m2-slice's side.
(Lead, 21:48: keep both Virels in big18; env-art-b drops the dressing piece on its branch for big19. Keeping
m2-slice's Ch1 framing is right; the Lead judges the shots at review.)

### big18 checks in progress (on 4ee3a7b8)
- 2026-10-29 21:36 UTC: every non-shot step started (HYMN_STEP_TIMEOUT=10800, own HYMN_LOG_DIR and XDG_DATA_HOME;
  each step runs even if an earlier one fails). Data 0/0; audio, manifest ok.
- **Tool suite: 186 units, 1930 tests, 3 failing units** (big17: 4 failing). Fixed since big17: test_freed_cast_lint,
  test_npc, test_post_import.
  - test_screenshots: `villager_shopkeeper_front` has no baseline. **Known on big17.**
  - **NEW, branch content:** test_zone_map_pois: "ch01/oruvel/kell (actor:kell): at [31.0, -7.5] but the source is
    at [29.0, -7.0]". act1-chapters' cb97a0cf (GPU QA row 23) moved Kell without moving her zone-map POI. It's red
    on `claude/act1-chapters` @ e7b065b4 alone too. Route to act1-chapters.
  - **NEW, merge fallout, fixed (4ee3a7b8):** test_glimmer_forms: `glimmer_forms.json` was stale. m2-slice's forms
    (green on its own head) sample creatures' rebuilt models. Regenerated with `tools/cutscene/glimmer_forms.py`
    (two coordinates moved by under 0.01).
- Blender: 78 jobs touched since `origin/lead/gate-big17` (1bdaea53): heroes, villagers, crowd, creatures and 7
  zone kits. As on big17, they run after the timing-sensitive suite.
