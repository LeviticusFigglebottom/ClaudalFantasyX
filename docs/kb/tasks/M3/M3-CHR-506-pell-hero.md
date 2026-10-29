---
id: M3-CHR-506
title: "Pell, the Kirru party hero, on the MPFB2 hero path with a Kirru head warp (build, face poses, story and battle clips, shots)"
role: character
status: review
owner_session: "characters worktree chr-pell-wip (/home/user/pell-wt)"
depends_on: [M2-CHR-01, M2-CHR-02, M1-CHR-14, M2-CHR-07, M3-CHR-01]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Pell is first seen on the Corrow seawall in Ch8 (a guest in the Wave 3 encounter, Storm-Call) and joins after the Ebbing
(Ch9). He is the only non-human hero: 2.30 m, long-necked, furred, with a crest, whiskers and webbed hands. Build him on
the pipeline.md §12 layout (MPFB2 donor, ADR 0021) from the design sheet
[`docs/kb/art/characters/pell.md`](../../art/characters/pell.md), adding one step, the Kirru head warp of pell.md §9, so
the face pipeline and its 40 shape names still apply. In order: design (done in the sheet) → head-warp proof (a clay
face and the 15 face poses, before the rest) → build → face poses → clips → shots.

## Acceptance criteria
- [ ] **Design:** pell.md is reviewed by Rendering (including the fur question of §12), and by the Art Director for the
      proposed swatches. The open questions in §12 are answered by Narrative, Combat and battle-presentation, or carried
      with their default.
- [ ] **Head:** the Kirru head is the donor topology through `pell_head.kirru_warp`, with the landmarks re-read after the
      warp and the 40 shapes built on the warped face. If a believable muzzle needs a non-donor head, an ADR is written and
      accepted first (pell.md §9).
- [ ] **Build:** `assets_src/characters/pell/` imports Asha's, Rhen's and Toma's modules, with nothing copied.
      `pell_params.json` holds every number in pell.md §1 and §9. M1-CHR-14 lessons apply:
      - nothing hangs below the hips (no tube skirt; the fallback girdle of pell.md §4.2, if ever needed, is split
        leg-following panels);
      - the reed mantle rides the torso and the right clavicle, its arm edge at least 11.5 cm below the shoulder joint
        with a blend band; the toggle cord under the left arm is at least 11.5 cm below the joint;
      - the name-shell cord is at least 10 mm off the neck at every neck pose of the clips;
      - the staff sits 1.2 cm off the grip, with no lashing inside the grip;
      - the feet are bare and whole (the ankle cord rides the shin).
- [ ] **Host determinism:** the M1-CHR-14 snaps as `build_ysolde` applies them: `MIDLINE_SNAP` on the head (and the
      midline crest, whisker and tuft cards), `quantize_uvs` after each unwrap, `snap_shape_noise` on every exported object
      (including `crest_raise` and `crest_flat`), and `asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS` in the texture run.
- [ ] **Reproducible:** job `pell` in `tools/dev/blender_builds.json` with `"threads": 4`. Its sources include
      `pell/**`, `asha/**`, `rhen/**`, `toma/**`, `base_body/**` and `third_party/mpfb2/**`. Two runs give byte-identical
      outputs (sha256), also with `NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4"`. Any change to a shared module re-verifies the
      `asha`, `rhen`, `toma`, `ysolde` and `villager_*` jobs.
- [ ] **Budgets:** LOD0 at most 62k triangles (ceiling 70k) and LOD1 about 28k. `pell.glb` is under 5 MB,
      `pell_lod1.glb` under 1.5 MB, and every texture PNG under 5 MB.
- [ ] **Rig guards:** a `pell` entry in `tools/dev/rig_checks.json` (garments `Costume`, `Wraps` and `Crest`; props `Staff`
      and `NameShell`; the `crest_raise` stage pose). `python3 tools/dev/rig_probe.py --hero pell --report` passes the
      defaults, or each ratchet is pinned with a viewed reason in `_allowances`. `tools/tests/test_rig_integrity.py`
      covers him.
- [ ] **Face poses:** all 40 shapes on the muzzle with the whiskers and brow tufts following them, and
      `game/levels/_tests/characters/pell/pell_face_poses.json` with the 15 tags of pell.md §6.2 and their crest values. A
      `face_poses` entry (with the crest column and the 0.25 s onset delay) is requested from Cinematics.
- [ ] **Costume states:** `NameShellBlank` and `NameShellCarved` exist, one visible at a time; the carved spiral comes from
      `motifs/` data; the wet state (`crest_flat`, the fur parameter) exists for Ch8.
- [ ] **Clips:** `hero_clips.py --hero pell` writes `assets/characters/pell/anim/pell_clips.tres` with the story clips of
      pell.md §10.2 and the 12 battle-contract clips of §10.3 (the M2-CHR-07 block: `BATTLE_HEROES`, `BATTLE_STRIKER`,
      `FOOT_FLAT`, `_pell_keys`, an explicit `_victory` branch). The new persona keys `staff_side` and `neck_s` leave every
      other hero's library byte-identical. `tools/tests/test_hero_clips.py` checks the staff upright in the left hand and
      the head level through the walk; `tools/tests/test_hero_battle_clips.py` checks his contact markers.
- [ ] **Battle scale:** `game/characters/heroes/pell_battle.tscn` on `pell_lod1.glb` (pipeline.md §14); the framing note of
      pell.md §2.5 sent to UI+Combat and battle-presentation as a request task.
- [ ] **PROVENANCE:** a row in `assets/PROVENANCE.md` for every new output: GLBs, textures (the fur and feather atlases
      included), materials, clips, face poses and the motif data.
- [ ] **Shots:** a review stage at `game/levels/_tests/characters/pell/` on `asha_stage.gd`, with the shots of pell.md §11
      (`pell_front`, `pell_back`, `pell_three_quarter`, `pell_face`, `pell_face_stylized`, `pell_silhouette_lineup`,
      `pell_clip_storm_call`, `pell_clip_walk`, `pell_battle_attack`, `pell_storm_ch8`). Baselines are **viewed** and
      approved, including the check that he reads as a person and never as comic. Run with `HYMN_SHOTS` set to these ids
      only.
- [ ] `docs/kb/art/characters/pell_review.md` (a strict SPEC §14 assessment), an update to the live log
      (`docs/kb/handoffs/live/characters.md`, by the characters session), and a session handoff.

## Notes
- Gate scope (CLAUDE.md §3): the Blender rebuild for the `pell` job, plus the shared jobs only if a shared module changed;
  the rig probe and the hero-clip tests; `HYMN_SHOTS` limited to the shots above.
- Echo watch (pell.md §2, words only): no horn, no mane, no blue fur, no tattoos, no levelled spear, no jumps. The
  victory clip never turns his back (that gesture is the Ending's).
- The highest-risk step is the head warp: prove it on a clay face with all 15 poses before building the costume.
- 2026-10-24: design sheet written (docs-only worktree subagent of the characters session); no build yet.

- 2026-10-28 (characters worktree chr-pell-wip): **built; ready for review (reviewer: rendering).** Summary of what
  is in the branch, and the honest state of the art:
  - **Open questions of pell.md §12 carried with their defaults** (M3-NAR-1000 is still `todo`): no tail; no lower
    garment; the name carving is a spiral of long and short notches (`motifs/pell_name.json`); the name-shell is fine on
    a Kirru; no tears (no tear layer in his face poses); the costume avoids every beast-folk-guardian cue (no horn, no
    mane, no levelled spear, no blue). Listen plays `read`; learned abilities play `cast`; the battle framing note and
    the crest-led face poses went out as request tasks **M3-BPR-1340** (combat / battle-presentation, UI+Combat) and
    **M3-CIN-1240** (cinematics). Rendering's fur question (Q8) is open in `pell_review.md`.
  - **Head proof first:** `pell_head.kirru_warp` on the MPFB2 donor head (RBF on landmark controls, the seam faded so
    Head and Body stay welded, landmarks re-read after the warp, donor expression units carried through it), the 40
    shapes on the warped face; the clay face and its 15 poses were rendered and viewed before the costume was built.
    No non-donor head, so no ADR.
  - **Build** (`assets_src/characters/pell/`, `build.sh`; Asha's, Rhen's, Toma's and Ysolde's modules imported, nothing
    copied): LOD0 46,982 tris (head 20,806, body 11,010, fur fringe 3,600, costume 4,318, wraps 1,668, staff 1,700, eyes
    2,216, crest 336, whiskers 176, brow tufts 480, webs 288, name-shell 384), `pell.glb` 4,086,316 B; LOD1 27,320 tris,
    `pell_lod1.glb` 1,329,592 B; 14 textures, the largest `pell_head_normal.png` 3.90 MB; 21 materials (fur, wet fur,
    whisker, crest and crest_wet, the dialogue finish). Rig: 77 deform bones (with the M1-CHR-15 armpit pair) plus
    `DEF-staff` (under `DEF-hand.L`) and the mantle's two 2-bone panel chains. Measured: mantle arm edge 120 mm under
    the shoulder joint; the toggle cord 121 mm under the left one; the shell cord 10.8 mm off the neck (pushed out over
    the trapezius); the staff's grip 1.2 cm off the fist with no node or lashing in it.
  - **States:** `NameShellBlank` and `NameShellCarved` (one visible: `PellNameShell.apply(root, carved)`, tested);
    the wet state is `*_wet.tres` plus the Crest's `crest_flat` key. The LOD1 has no shape keys, so its crest is baked
    at the battle idle's `battle_raise` 0.3.
  - **Clips** (`pell_clips.tres`, 21): idle, walk, run, talk, storm_call, descend_rocks, go_still, listen_tilt,
    back_to_sea, the 12 contract clips and revive. New persona keys `neck_s`, `staff_side` and `staff_arm` (absent for
    every other hero: all other libraries rebuild byte-identical, test_hero_clips). His `ko` is his own (KO_OWN): he
    folds down onto his heels and bows the neck to the floor (a squat, the sheet's "sinks back onto his heels"); the
    shared yield test now names Moll only (`YIELD_HEROES`). Deviations to judge: the finisher's staff leans about 30°
    from upright (staff_hold's wrist limit), so its foot sweeps a hand above the floor rather than at knee height; the
    victory turns the chest and head about 6° (the contract's minimum) in his stillness.
  - **Rig guards:** `rig_checks.json` `pell` (garments Costume, Wraps, Crest; props Staff, NameShell and both shells);
    rig_probe passes with pinned allowances (reasons in `_allowances`: the ko/revive squat and the right arm across
    the chest). rig_probe applies no morph targets, so the `crest_raise` stage pose is checked in test_pell instead.
    `TestRigIntegrityPell` added.
  - **Shots:** 14 (`pell_*`), self-rendered and viewed, no baselines written. Read `docs/kb/art/characters/pell_review.md`:
    the silhouette, the staff, the battle dart, the costume and the crest read; **the face still reads as a muzzled
    human and the fur as a varnished carving at full figure; these are not final art.**
  - **Checks (2026-10-28, on 76f2ff2e):** `verify_blender_builds.py --job pell` 37/37 identical natively, with
    `NPY_DISABLE_CPU_FEATURES="X86_V4"` and with `"X86_V3 X86_V4"` (a vis_o delta flipped a 1 um grid step on the
    non-AVX512 paths until the shape deltas were rounded in two steps). No other Blender job imports anything changed
    (hero_clips.py is the clip generator, imported by no build script), so the shared jobs were not re-verified.
    unittest: test_pell 18, test_hero_clips + test_hero_battle_clips + test_hero_locomotion 42, test_blender_builds +
    TestRigIntegrityPell 57 (2 skipped), all OK. rig_probe --hero pell OK with the allowances. Godot 4.6.3:
    `--import`, then run_tests `--filter=post_import` 21/0 failed, `--filter=hero_stage` 11/0, `--filter=pell` 3/0.
    validate_data, taskboard --check, dlgc --check, gdlint, gdformat --check: clean.

- 2026-10-28 (later), **look-dev pass after the coordinator's review of out3** ("not at Kerrid's bar": a deformed
  human with a snout, wood-grain fur, reads unclothed). Same worktree and branch, four commits:
  1. **Head (5256844e):** `pell_head.KirruWarp` rewritten. The donor head's skin now goes onto a Kirru head surface
     (`_kirru.otter_head`: a broad, low cranium, crown 7 cm lower; a short broad muzzle flowing out of the skull line
     with the nose pad and whisker pads on it; jowls and a small chin; a neck thickened under the jaw) along rays from
     a centre in the skull (one-to-one, so nothing folds), the move smoothed and only 25% of the donor's own relief
     kept away from the eyes and mouth. The eyes (with their lids and frames, eye_scale 0.85), the mouth (with its bag,
     teeth and tongue, drawn in to a short line) and the ears (scaled, low and back) ride rigidly. Still the donor
     topology and all 40 shapes, so **no ADR 0141** was needed. `neck_width_ratio` 0.55 and `eye_scale` 0.85 changed
     from the sheet on review (test_pell updated).
  2. **Fur (5e71217c):** fine, low-contrast strands and clumps (the 0.32 streaks read as wood grain), Asha's thread
     detail normal at a finer tiling and lower strength, a rougher, less specular response; the silhouette fringe
     stands on the skin (cards face-on at the outline) and runs along the upper arms, hips, thighs and left flank too
     (4,200 cards, 2-3.5 cm).
  3. **Girdle (5e71217c): pell.md §12 Q3's default ("no lower garment") is overridden on review**, because the default
     read as nudity, against the Sincerity pillar. §4.2's fallback is built: a reed-fibre girdle of four split panels
     (front-left, front-right, back-left, back-right) from the belt cord down 22 cm, each weighted from the hips onto
     its own thigh by the hem, so nothing tube-like hangs below the hips (M1-CHR-14; test_pell checks no vertex takes
     both thighs). Found on the way: the Crest was exported unskinned and floated off the head in every clip; it is
     now rigid on the head bone (and rig_probe now checks it).
  4. **Smaller items (7ccfd2af):** the shared shapes scaled on the Kirru head (`_kirru.shape_gain`: brows 1.6-1.8,
     lids 1.4, cheeks 1.4, frown 1.5, smile 1.3); the face shot frames the crest; whiskers 3.6 mm; storm_call's palm
     lies up the throat (the elbow tucked 22 cm under the shoulder). The fingers stay open (no free-hand finger poses
     on the right), so the palm reads as a spread hand on the throat.
  Budgets after it: LOD0 52,328 tris, `pell.glb` 4,720,100 B; LOD1 27,190 tris, `pell_lod1.glb` 1,310,416 B (the fur
  fringe kept at 20% in the LOD1). Rig allowances re-pinned with reasons (`_allowances`).
  **Checks after the pass (on 7ccfd2af):** `verify_blender_builds.py --job pell` 37/37 identical natively, with
  `X86_V4` and with `X86_V3 X86_V4`; test_pell 20, test_hero_clips + test_hero_battle_clips + test_hero_locomotion 42
  (every other hero's library byte-identical), test_blender_builds + TestRigIntegrityPell OK; rig_probe OK; Godot
  `post_import` 21/0, `hero_stage` 11/0, `pell` 3/0; validate_data, taskboard, dlgc, gdlint, gdformat clean.
  `pell_review.md` is rewritten with before/after notes and what still does not read (the almond human lids, the small
  human ears, the uniform fur at full figure, the open right hand, a ridge at the nape).

- 2026-10-29 (claude/characters, new Lead's session): **second look-dev pass @ 2c2acb54** on pell_review.md's five open
  items (the review's new section has the before/after): rounder lids, a dark eye ring and a dark lid margin; round flat
  ears; a flat right hand in storm_call and cast (hero_clips FLAT_HAND, Pell's library only: every other library
  rebuilds byte-identical, test_hero_clips); a stronger saddle pattern, body clumps and a soft throat stripe; a thicker
  upper neck under the skull. pell.glb 4.79 MB, LOD1 1.32 MB. Checks are in the live log's MERGE-READY line.

## Review log
