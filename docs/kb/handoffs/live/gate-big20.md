# Gate session live log: big20

The cloud gate session (`session_01UPFyEAXofxWazWNnRTzFGJ`) builds `lead/gate-bigN` on the Lead's rolling cadence
(ADR 0205: a fast gate every ~90 min). It never writes or approves baselines. One log per batch.

## big20

GATE-BUILT big20 @ 4e3c74c9 (branch `lead/gate-big20`), from `claude/new-session-mj8c3c` @ 8de373e5 (big19 merged, plus
the Lead's 48 approvals).

Pinned heads, merged with `--no-ff` in this order:
1. claude/env-art @ 186d3c9e: PROVENANCE by merge_union.
2. claude/env-art-b @ a705831b: the Haluna `kit_manifest.json` (generated) gained pieces on both sides (env-art-b's
   Act II pieces, env-art's reedhollow ground). Key-merged 3-way, no clash, pieces sorted as the generator writes them.
3. claude/characters @ b7ef0755, claude/creatures @ 420703ed: clean.
4. claude/creatures-b @ 1d97dc66: ownership.md took its Act II row.
5. claude/battle-presentation @ 946faab5: a criss-cross merge (2 bases) garbled the text conflicts. `battle_sfx.json`,
   `enemies.json` and `battle_sandbox.json` were merged semantically per line (rows by id, keys by key, against
   c72011bd), with each file's own formatting kept. One clash: `boss_seats.mangrove_drowner` kept ours (creatures-b's
   M4-CRB-002 seat, [-5, 0, -3], framed on its own tree) over battle-presentation's [-2.8, 0, -2.2].
   `encounter_sweep.gd.uid` took theirs (the script's own uid; ours was the big19 gate's import). ownership.md both.
6. claude/act1-chapters @ 85e513cb: `encounters.json`, `enemies.json` and `skills.json` merged the same way against
   f6cb8190. **The Ch10 Mangrove Drowner was defined twice**, by act1-chapters and by the Combat side, with
   different stats, phases, skills (drowner_drag, rising_water, root_stamp) and loc. `game/data/battle/**` is Combat's
   (ownership.md), so every clashing field kept ours (the Combat side); act1-chapters' rows only add fields it alone
   set. M4-A2P-041's task kept both notes.
7. claude/ui @ c655f676: shots.json's `field_hud_over_haluna_wake` camera changed on both sides (env-art's f06c190d
   `Lane`, ui's later 602dcb31 `Wake`, both GPU QA row 43). Took ui's `Wake` (4e3c74c9): ui owns the field HUD shots.
8. claude/hero-integration @ 20266878, claude/m2-slice @ db4cdab2, claude/audio @ 2079ffd6: clean or union only.
9. claude/act2-plan @ 52e39207 (27 new commits since big19): `codex.json` took its 12 people entries (69 unique ids
   after); M4-A2P-008 took theirs (`review`, the story track did the work); M4-A2P-056 kept ours (the wildlife line
   was already there); `flags.tres` ch14_declared_heretics: only the description differs, kept ours.

Not merged: claude/menus (nothing new), first-playable, gate-runner-a/-b (stale), the retired -ze8rrn/-423ixt.

Merge fallout fixes (553ef19f):
- PROVENANCE: the 2 Haluna placeholder rows and avalanche_ram's `ice.tres` (creatures-b removed it, a70e62d3) out;
  env-art-b's new `lacquer_court_steps` arena (M4-A2P-044, a881234d) had no row on any branch: added from its
  generator `ansedra_arenas.py`. env-art-b should carry the same row.
- `ch10.csv`: SKILL_RISING_WATER, ENEMY_MANGROVE_DROWNER, PHASE_MANGROVE_DROWNER_UPROOTED and LORE_MANGROVE_DROWNER
  were duplicate loc keys (also in `strings.csv`, the Combat side). Removed from ch10.csv.

LEAD-ASK: the Ch10 Mangrove Drowner had two independent definitions (act1-chapters vs the Combat side:
creatures-b and battle-presentation). big20 keeps the Combat side's stats, phases, skills and loc text, and drops
act1-chapters' 4 duplicate loc rows. If act1-chapters' tuning or lore text was the intended one, it needs a Combat
follow-up.

Checks at the build: validate_data 0/0; taskboard --check ok; dlgc 0/0; gdlint and gdformat clean; no duplicate loc
keys, PROVENANCE rows or shot ids (653 shots); no conflict markers.
LEAD-ANSWERED (05:51): the Combat side's single definition of the Drowner is correct; act1-chapters tunes numbers on it.

### Fast gate (started 05:19 UTC; big19's capture paused for it)
- Godot import clean (seeded from big19's .godot); **boot smoke 0 ERROR lines**.
- **Filtered Godot tests: 233 files** (every changed test plus every test naming a changed game/ or assets/ file by
  res:// path or class_name; diff against the integration branch); no script errors in any log. 3 red:
  - **test_slice_primitives: FIXED.** "oruvel.tscn shows a PlaneMesh at CutsceneStage/Actors/seabed/Model/Seabed"
    (m2-slice's e3ad5bbe). Per the Lead, slice-polish's FAST-TRACK d207cb49 (a generated sand-and-rock seabed) was
    merged (5aca3d9b, claude/m2-slice @ cf413489): 1/0 after. Its PROVENANCE union re-added ice.tres; dropped (b76eae4c).
  - **BATCH RED (hero-integration):** test_hero_followers::test_no_follower_is_laid_out_in_front_of_the_lens: "asha
    still 0.31 m from the lens", "toma still 0.84 m from the lens". hero-integration's new guard (692b5515, GPU QA rows
    37/38). Deterministic (re-run alone) and **red on claude/hero-integration @ 20266878 alone**.
  - **BATCH RED (Act II):** test_hero_field_snaps::test_no_hero_body_snaps_in_any_zone: "lowlight.tscn: rhen never
    snaps (241 snaps)" is **red on claude/act1-chapters @ 85e513cb alone** (Ch11's marks and cameras, M4-A2P-011).
    "sanctum.tscn: asha (1), toma (3)" appears only in the merge: env-art-b's Sanctum dressing (M4-A2P-043, green
    alone) meets act1-chapters' Ch13 marks (M4-A2P-013). Route to act1-chapters, with env-art-b for the Sanctum.
- **Tools suite: 199 units, 2012 tests, 22 failing units.** Classified so far against the track heads:
  - known or routed: test_palette_check and test_villagers (red on the integration branch itself), test_screenshots
    (baselines pending).
  - **characters, red alone:** test_rig_integrity for 13 villagers (garments through the skin, e.g. Elder "penetration
    garment_in_body Costume, count 4 > 3"), test_sefir.
  - Still classifying: test_act1_audio_audit, test_battle_vfx_coverage, test_cutscene_sfx_files, test_keth and
    test_hero_clips (the remaining track heads are running).

GATE-FAST-DONE big20 @ b76eae4c (06:25 UTC). **Not green:** two batch reds (hero-integration's lens guard; the Act II snaps in
Lowlight and the Sanctum). Everything else is fixed, known or routed. Lead's call: merge with them FAST-TRACKed, or hold.
- Tools reds classified on the track heads (07:50): **none is merge fallout; all are branch content. FAST-TRACK list:**
  - act1-chapters: test_act1_audio_audit, test_battle_vfx_coverage (both red on claude/act1-chapters alone).
  - act2-plan: test_cutscene_sfx_files, test_hero_clips (red on claude/act2-plan alone; test_hero_clips takes ~10 min).
  - env-art: test_keth (red on claude/env-art alone).
  - characters: test_sefir and the 13 villagers' test_rig_integrity (garments through the skin).
  - Known: test_palette_check, test_villagers (red on the integration branch itself), test_screenshots.
