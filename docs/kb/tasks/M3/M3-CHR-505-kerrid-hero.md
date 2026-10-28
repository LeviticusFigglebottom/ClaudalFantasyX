---
id: M3-CHR-505
title: "Old Kerrid, the fifth party hero, on the MPFB2 hero path (build, face poses, story and battle clips, shots)"
role: character
status: review
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
depends_on: [M2-CHR-01, M2-CHR-02, M1-CHR-14, M2-CHR-07, M3-CHR-01]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Kerrid joins at Pemakar (Ch5) and fights from Ch5 (the slag tortoises and the Cinder Matron introduce his armour-breaking
niche). He is in Ch5, Ch6, Ch8 (the stair foot, wet) and Ch9 (the Ebbing cutaway, the dawn road, the vigil). Build him as
a hero on the pipeline.md §12 layout (MPFB2 donor, ADR 0021) from the design sheet
[`docs/kb/art/characters/kerrid.md`](../../art/characters/kerrid.md), in order: design (done in the sheet) → build → face
poses → clips → shots. Story constraints: ADR 0020 (c) as amended by ADR 0022 (b) and (g): a bare face, both eyes clear,
the scars on the forearms, the left forearm wrapped, the watch cord in faded watch-red, and no rope-burn glow before Ch10.

## Acceptance criteria
- [ ] **Design:** kerrid.md is reviewed by Rendering, and by the Art Director for the ten proposed swatches. The open
      questions in §12 are answered by Narrative and Combat, or carried with their default.
- [ ] **Build:** `assets_src/characters/kerrid/` imports Asha's, Rhen's, Toma's, Ysolde's and the villager modules, with
      nothing copied. `kerrid_params.json` holds every number in kerrid.md §1 and §9. M1-CHR-14 lessons apply:
      - the cape's back tier is two leg-following halves with panel bones, not a tube;
      - the cape yoke rides the upper torso and clavicles, ≥ 25 mm off the neck across the clips and ≥ 4 cm below the jaw
        (no high collar);
      - the smock's sleeve seam is at least 11.5 cm below the shoulder joint, and the chest rope is torso-only;
      - the cleaver sits 1.2 cm off the grip (and ≥ 12 mm off the cape on the back);
      - the rope sandals take the feet's weights.
- [ ] **Host determinism:** the M1-CHR-14 snaps as `build_ysolde` applies them: `MIDLINE_SNAP` on the head (and the
      midline beard cards), `quantize_uvs` after each unwrap, `snap_shape_noise` on every exported object (including the
      `cape_wet` key), and `asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS` in the texture run.
- [ ] **Reproducible:** job `kerrid` in `tools/dev/blender_builds.json` with `"threads": 4`. Its sources include
      `kerrid/**`, `asha/**`, `rhen/**`, `toma/**`, `villagers/**`, `base_body/**` and `third_party/mpfb2/**` (and
      `ysolde/**` if her sleeve helper is imported). Two runs give byte-identical outputs (sha256), also with
      `NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4"`. Any change to a shared module re-verifies the `asha`, `rhen`, `toma`,
      `ysolde` and `villager_*` jobs.
- [ ] **Budgets:** LOD0 at most 60k triangles (ceiling 70k) and LOD1 about 28k. `kerrid.glb` is under 5 MB,
      `kerrid_lod1.glb` under 1.5 MB, and every texture PNG under 5 MB.
- [ ] **Rig guards:** a `kerrid` entry in `tools/dev/rig_checks.json` (garments `Costume`, `Cape` and `Wrap`; props
      `Cleaver`; the `cape_wet` stage pose). `python3 tools/dev/rig_probe.py --hero kerrid --report` passes the defaults,
      or each ratchet is pinned with a viewed reason in `_allowances`. `tools/tests/test_rig_integrity.py` covers him.
- [ ] **Face poses:** all 40 shapes with the beard in the Head object following them, and
      `game/levels/_tests/characters/kerrid/kerrid_face_poses.json` with the 15 tags of kerrid.md §6.2 (rest squint
      included). A `face_poses` entry for `sequencer.json` is requested from Cinematics.
- [ ] **The rope-burn light:** `burn_glow` defaults to 0 (Ch5-Ch9); at 0.15 it emits `glimmer_held` only; the VFX sockets
      of kerrid.md §9 exist. No gold on him anywhere before H09.
- [ ] **Clips:** `hero_clips.py --hero kerrid` writes `assets/characters/kerrid/anim/kerrid_clips.tres` with the story
      clips of kerrid.md §10.2 and the 12 battle-contract clips of §10.3 (the M2-CHR-07 block: `BATTLE_HEROES`,
      `BATTLE_STRIKER`, `FOOT_FLAT`, `_kerrid_keys`, an explicit `_victory` branch). The new persona key `hunch` and the
      `breath` 0.0 leave every other hero's library byte-identical. `tools/tests/test_hero_clips.py` checks no breath in his
      idle and the level gaze under the hunch; `tools/tests/test_hero_battle_clips.py` checks his contact markers.
- [ ] **Battle scale:** `game/characters/heroes/kerrid_battle.tscn` on `kerrid_lod1.glb` (pipeline.md §14), with the
      cleaver shown in the hand and hidden on the back (kerrid.md §9).
- [ ] **PROVENANCE:** a row in `assets/PROVENANCE.md` for every new output: GLBs, textures (the fibre atlas included),
      materials, clips and face poses.
- [ ] **Shots:** a review stage at `game/levels/_tests/characters/kerrid/` on `asha_stage.gd`, with the shots of
      kerrid.md §11 (`kerrid_front`, `kerrid_back`, `kerrid_three_quarter`, `kerrid_face`, `kerrid_face_stylized`,
      `kerrid_silhouette_lineup`, `kerrid_clip_collar_haul`, `kerrid_clip_push_climber`, `kerrid_battle_attack`,
      `kerrid_storm_ch8`, `kerrid_glow_ch10`). Baselines are **viewed** and approved. Run with `HYMN_SHOTS` set to these
      ids only.
- [ ] `docs/kb/art/characters/kerrid_review.md` (a strict SPEC §14 assessment), an update to the live log
      (`docs/kb/handoffs/live/characters.md`, by the characters session), and a session handoff.

## Notes
- Gate scope (CLAUDE.md §3): the Blender rebuild for the `kerrid` job, plus the shared jobs only if a shared module
  changed; the rig probe and the hero-clip tests; `HYMN_SHOTS` limited to the shots above.
- IP watches (ADR 0020, 0022; kerrid.md §4.2): no hat, no mask or high collar, no eye effect, no eyewear, no coat off one
  arm, no gourd, no Order insignia; the cleaver is never rested on the shoulder in any clip.
- Liss (act1_npcs.md §2) and Pell ([`pell.md`](../../art/characters/pell.md), M3-CHR-506) belong in the silhouette lineup
  once built; until then, use their sheets' proportions as flat stand-ins.
- 2026-10-24: design sheet written (docs-only worktree subagent of the characters session); no build yet.

## Review log
