# Gate session live log: big21

The cloud gate session (`session_01UPFyEAXofxWazWNnRTzFGJ`), on the Lead's rolling cadence (ADR 0205). It never writes
or approves baselines. One log per batch.

## big21

GATE-BUILT big21 @ e3e7deb1 (branch `lead/gate-big21`), from `lead/gate-big20` @ 597f7bf7. big20 is not merged yet (its two
batch reds wait on the Lead), so big21 carries big20 and its resolutions, plus:
1. claude/new-session-mj8c3c @ 3a5759ad: clean (the Lead's big19 approvals).
2. claude/env-art @ f3898456: **env-art and env-art-b both did M4-A2P-043 (Ansedra's dressing).** act2_tracks.md gives
   Ch13–16 dressing to env-art-b, so ours (env-art-b's dressing, environment, generator, its test and the task's
   `review` state) was kept over env-art's "in progress" version. env-art's other new kit pieces came in.
3. claude/env-art-b @ c46d29e4: the Haluna `kit_manifest.json` key-merged again (no clash, sorted); ownership.md both.
   shots.json: `slice_end_card_voice` stays removed (m2-slice's M3-CIN-1233 dropped the mid-Act I card).
4. claude/characters @ 7fbe446f, claude/creatures @ 4f53a834: clean.
5. claude/creatures-b @ 10490ad9: `game/data/import/creatures.json`'s `assets` list merged as a 3-way set (51); ours'
   `lods` and `_about` changes kept.
6. claude/battle-presentation @ 27dbad77: union only.
7. claude/act1-chapters @ 03b3d90c: `enemies.json` block-merged. **The four Act II bosses' stats and phases take
   act1-chapters' numbers** (the Lead, 05:51: chapters tunes the numbers on Combat's definition; act2_tracks.md gives
   chapters the boss tables). `creatures.json`: the vowbound_pending keys dropped (act1-chapters' 45faae4e: the rows exist).
8. claude/ui @ 391059f3: `codex.json`: ui's `keth`, `conclave`, `malcor_venn` and `heresy` (ui owns the codex) replace the
   story track's `conclave` and `malcor_venn`.
9. claude/hero-integration @ e7af4147: M3-CIN-1251's task took theirs (done by integration-qa, `review`).
10. claude/audio @ 6e3530f0: union only.
11. claude/act2-plan @ a766bdc2: `codex.json` held `farewell_tide` and `name_shells` twice. Kept act2-plan's (unlocked by
    `ch10_tide_witnessed`, set by three Ch10 dialogues); the other copy unlocked on `ch10_farewell_tide_seen`, which
    nothing sets. `test_codex.gd`'s pinned world total is the merged codex's 19 (ours said 17, theirs 16).
- Not merged: claude/m2-slice (nothing new since big20's seabed fix), claude/menus, the stale branches.

Merge fallout fixes:
- 17cd2bea: ENEMY_ and LORE_ for the Mangrove Drowner, Lamp Engine, Avalanche Ram and Wakefin were in strings.csv (the
  Lead's PROVISIONAL rows, 1dbfed6d) and in ch10/11/12/15.csv (act2-plan's bestiary pass M4-A2P-009); the story track's
  rows stay. PROVENANCE: avalanche_ram's and rime_urchin's `ice.tres` rows (deleted files, ADR 0015) out.
- e3e7deb1: kesh's `vowbound_pending` dropped (validate_data: vowbound.json has its row).

Checks at the build: validate_data 0/0; taskboard ok; dlgc 0/0; gdlint and gdformat clean; no duplicate loc keys, codex
ids, PROVENANCE rows or shot ids (669 shots); no conflict markers.

### Fast gate (07:55–09:03 UTC; big19's last capture paused for it)
- Godot import clean; **boot smoke 0 ERROR lines**.
- **Filtered Godot tests: 309 files** (diff against the integration branch, which then held big19 only). 6 red:
  - **FIXED on the gate (merge fallout), cf238776:** test_battle_vowbound_model: "kesh voice_water: its own clip" (6
    voices). creatures-b's kesh row (contacts per voice) met act1-chapters' M4-A2P-024/025 vowbound row and skills.
    Kesh's `clip_by_skill` was pasted from `docs/kb/art/creatures/vowbound/kesh.md` (the six voices, the_seven; kesh_shift
    isn't a skill yet). 4/0 after.
  - **FIXED on the gate, 9ffec236 (keep it, the Lead):** test_pseudo_loc_screens::test_party_pages_fit: a script
    error, battle_cycle.gd:23 "'cycle' on Nil". M4-A2P-025's cycle check in `skill_help()` ran with no current actor
    (the lattice menu, out of battle). A null guard: 17/0 after, test_battle_cycle 5/0, test_lattice_menu 25/0.
    (The end-of-run log check still flags its pre-fix log.)
  - **Routed: battle-presentation** (the Lead sent it): test_battle_vfx: "element of voice_glimmer / level_hand /
    still_water": the VFX map has no `glimmer` element for the new glimmer skills.
  - **Routed: battle-presentation / act1-chapters:** test_battle_act1_ability_vfx: "swell the_seven / farewell_tide has
    its own effect": the Act II finishers have no effects yet.
  - **Routed: env-art-b, red on claude/env-art-b alone:** test_ch14_16_walkable::test_hollowmeres_dock:
    "kit:hm_supper_table.glb@(41.4, 0.0, -0.9) blocks a body at (40.7, 0.00, -0.8)".
  - **Already FAST-TRACKed (big20):** test_hero_field_snaps (Lowlight, the Sanctum).
- **Tools suite: 201 units, 22 failing.** All branch content (re-run on the heads): the same as big20 (characters'
  13 villager rig checks; act1-chapters' test_act1_audio_audit; act2-plan's test_cutscene_sfx_files and test_hero_clips;
  env-art's test_keth; the known test_palette_check, test_villagers, test_screenshots), plus three new ones:
  - test_blender_builds: `assets/cutscene/ch01/oruvel_seabed.glb` has no Blender job (m2-slice's FAST-TRACK seabed;
    red on claude/m2-slice and claude/act1-chapters alone). Route to m2-slice.
  - test_arenas: `bridal_barge_night` and `ansedra_lagoon_escape` aren't reproducible from their generator (red on
    claude/env-art-b alone). Route to env-art-b.
  - test_status_names: "dialogue.csv DLG_NAME_KIRRU_SHELL_CARVER: 'Shell' is an old status name (ADR 0202: Tide Ward)"
    (red on claude/act2-plan alone). Route to act2-plan.
