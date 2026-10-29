# Handoff — cinematics (slice-polish) — 2026-10-28 #1

Session `session_01F3vrUPLtDQMGSRrMHJtpz1` on `claude/m2-slice`. It replaced `session_01KZCgTq` per ADR 0042. The
live log `docs/kb/handoffs/live/slice-polish.md` has every item, its checks and the renders viewed.

## Done
- **Merges:** `lead/gate-ft-beach` @ 93d0741e (a fast-forward), then the integration branch @ eca37107 and @ 8870ea9c.
- **The First Verse (the Lead's item 2):**
  - a built clip now plays on its clip mark (`CutsceneSequencer._cue_anim`), so `sit_steps` sits;
  - S06 is re-staged per haluna.md §5.3: seated on the steps, the sea behind, Toma turning to the lens;
  - Rhen and Toma rise in the black and turn to Asha; S10 is the reverse on Rhen; S09 is clean.
- **Beat audit, the slice:**
  - B02 gets the `NemeTable` camera volume;
  - B11 gets the `DockEnd` volume;
  - the beach gets H05_up, its standing two-shot (PC GPU QA row 32);
  - the C07 harrier shot no longer sets `ch03_harrier_won` (row 18);
  - the end card's credits read "Original music";
  - scene stills run their sequencer under the level, so the party hides as it does in play.
- **Beat audit, Ch1:**
  - the scale-hull and the chandlery face their customers;
  - O02, O09, U03 and O10 are re-aimed;
  - the LowHull wears the kit (outrigger and salvage);
  - the scaleman faces his counter.
- **Infrastructure:**
  - `pending_baseline` in shots.json, compare.py and test_screenshots;
  - M3-CRE-657 (creatures' patch, GreyboxZone `_build_villagers()`);
  - test_fp_prologue (Liss), test_zone_cast and test_ch01_oruvel_kit updated.
- **Filed:**
  - M3-CHR-101 (Rhen's eyes red under a rim);
  - M3-CHR-102 (Asha's kneeling skirt through Rhen, row 31);
  - M3-ENV-103 (Asha's packed bag is a box).

## Done (later the same session)
- **Ch1 zones on env-art's dressings** (the Lead's ruling): Oruvel (M3-ENV-740) and the Underway (M3-ENV-742). My
  generators are retired, the cutscene side is re-staged onto their hulls, and the storm set follows StormWall
  (M3-ENV-751).
- **Cutscene VFX at final quality:** `@vfx glimmer_*` builds Rendering's GlimmerField (CutsceneVfx), with
  per-mode energy, `center_y_m`, `amount_multiplier` and `end_after_sec` from sequencer.json "vfx". CutsceneMotes is
  deleted.
- **New pending stills, all viewed:** slice_verse_c08 (C08 re-framed, the bell brought in), slice_end_card,
  slice_end_card_voice. O07 holds Sadi's line 003 again.
- **Haluna:** the seven villagers' static capsules are gone (M3-ENV-748); the trees use their real names
  (M3-ENV-750).
- **Filed:**
  - M3-ENV-104 (Oruvel gaps, the storm sky);
  - M3-ENV-105 (high: the Underway's walls stand inside the collision);
  - M3-ENV-106 (the grades for `@camera grade=`).

## In progress
- Nothing uncommitted. The gate baselines my pending shots at big15 or big16 (the Lead's answer).

## Exact next step
0. When env-art lands M3-ENV-105 (the Underway's walls on the greybox lines), re-render ch01_underway_crown and
   ch01_underway_gallery and view them. When they land M3-ENV-106, wire `@camera grade=` and the nodes' `grade:` in
   the sequencer, through a helper like CutsceneVfx (the sequencer is at 995 of 1000 lines).
1. Merge the integration branch when the Lead announces big15 or big16.
2. Re-run `--filter=haluna`, `cutscene`, `fp_`, `ch01`.
3. Answer M3-CHR-102 when characters reply: move Asha's kneel mark by the clearance they name, keeping both faces
   in H05 and H06.
4. Swap in M3-ENV-103's bag when env-art builds it.
5. Then continue the audit: the causeway's B05/B06 banters on the field camera (row 37 is hero-integration's) and
   Ch1's battles (row 40: env-art-b and creatures).

## Known issues
- Not mine:
  - `test_act1_cutscene_walks` (Ch4 Haluna wake, act1-chapters);
  - `test_villager_routines` (creatures', fixed on their branch);
  - test_screenshots, for other tracks' unbaselined shots, until the gate.
- `slice_haluna_villagers_village` now shows B02's close framing: its spawn is inside the new volume.
- The shallow clone: deepen it before merging (`git fetch --deepen=400 ...`), or a merge shows false conflicts.

## Files touched
- **Code and tests:**
  - game/cutscene/cutscene_sequencer.gd;
  - game/world/zone/greybox_zone.gd;
  - game/levels/_tests/slice_shots/slice_cutscene_shot.gd;
  - tests (fp_prologue, qa_cutscene_motion_audit, zone_cast, ch01_oruvel_kit, slice_primitives, dialogue_vs_scenes,
    haluna_zone).
- **Scenes and data:**
  - game/levels/ch03/first_verse/first_verse.tscn;
  - game/levels/ch02/haluna/haluna.tscn;
  - game/levels/ch01/oruvel/*, game/levels/ch01/oruvel_underway/oruvel_underway_layout.json;
  - game/data/dialogue (ch03_the_first_verse, ch02_girl_on_the_beach) and their compiled JSON;
  - game/data/loc/strings.csv (CREDITS_MUSIC).
- **Tools and shots:**
  - tools/ch01/ch01_oruvel_dressing.py;
  - tools/screenshots/compare.py, tools/tests/test_screenshots.py, tests/screenshots/shots.json.
- **Docs:** three task files, the live log, this handoff.
