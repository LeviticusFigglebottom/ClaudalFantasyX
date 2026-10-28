---
id: M3-CHR-506
title: "Pell, the Kirru party hero, on the MPFB2 hero path with a Kirru head warp (build, face poses, story and battle clips, shots)"
role: character
status: doing
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

## Review log
