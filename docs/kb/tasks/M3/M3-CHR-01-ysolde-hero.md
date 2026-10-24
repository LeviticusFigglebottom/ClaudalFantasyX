---
id: M3-CHR-01
title: "Ysolde, the fourth hero, on the MPFB2 hero path (design, build, face poses, clips, shots)"
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
depends_on: [M2-CHR-01, M2-CHR-02, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Ysolde Ysel joins at the Ch4 ferry and fights from Ch4 (the Spar-Wraith introduces her magic). Her Swell input, Glyph
Trace, already exists in the engine (M2-CMB-01, M2-UI-03). Build her as the fourth hero on the pipeline.md §12 layout
(MPFB2 donor, ADR 0021) from the design sheet [`docs/kb/art/characters/ysolde.md`](../../art/characters/ysolde.md), in
order: design (done in the sheet) → build → face poses → clips → shots.

## Acceptance criteria
- [ ] **Design:** ysolde.md is reviewed by Rendering, and by the Art Director for the five proposed swatches. The open
      questions in §12 are answered by Narrative, or carried with their default.
- [ ] **Build:** `assets_src/characters/ysolde/` imports Asha's, Rhen's, Toma's and the villager modules, with nothing
      copied. `ysolde_params.json` holds every number in ysolde.md §1 and §9. M1-CHR-14 lessons apply:
      - the robe is four leg-following panels with panel bones, not a floor-length tube;
      - the sleeves are dropped-shoulder, with the seam at least 11.5 cm below the shoulder joint;
      - the collar rides the upper torso with at least 25 mm of head clearance;
      - the book sits 1.2 cm off the grip;
      - the ink-guards are rigid to the distal finger bones.
- [ ] **Reproducible:** job `ysolde` in `tools/dev/blender_builds.json` with `"threads": 4`. Its sources include
      `asha/**`, `rhen/**`, `toma/**`, `villagers/**`, `base_body/**` and `third_party/mpfb2/**`. Two runs give
      byte-identical outputs (sha256). The texture run sets `asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS`. Any change to
      a shared module re-verifies the `asha`, `rhen`, `toma` and `villager_*` jobs.
- [ ] **Budgets:** LOD0 at most 60k triangles (ceiling 70k) and LOD1 about 28k. `ysolde.glb` is under 5 MB,
      `ysolde_lod1.glb` under 1.5 MB, and every texture PNG under 5 MB.
- [ ] **Rig guards:** a `ysolde` entry in `tools/dev/rig_checks.json` (garments `Costume` and `Collar`; props `Book`,
      `InkGuards` and `Pin`). `python3 tools/dev/rig_probe.py --hero ysolde --report` passes the defaults, or each
      ratchet is pinned with a viewed reason in `_allowances`. `tools/tests/test_rig_integrity.py` covers her.
- [ ] **Face poses:** all 40 shapes, and `game/levels/_tests/characters/ysolde/ysolde_face_poses.json` with the 15 tags of
      ysolde.md §6.2, including her rest `brow_outer_up_L` 0.08. A `face_poses` entry for `sequencer.json` is requested
      from Cinematics.
- [ ] **Clips:** `hero_clips.py --hero ysolde` writes `assets/characters/ysolde/anim/ysolde_clips.tres` with the clips of
      ysolde.md §10. The new persona keys `book` and `breath` leave Asha's, Rhen's and Toma's libraries byte-identical.
      `tools/tests/test_hero_clips.py` checks the book at the hip and the five-stroke order of `cast_glyph`.
- [ ] **Battle scale:** `game/characters/heroes/ysolde_battle.tscn` on `ysolde_lod1.glb` (pipeline.md §14).
- [ ] **PROVENANCE:** a row for every new output: GLBs, textures, materials, clips, face poses and the motif data.
- [ ] **Shots:** a review stage at `game/levels/_tests/characters/ysolde/` on `asha_stage.gd`, with shots `ysolde_front`,
      `ysolde_back`, `ysolde_three_quarter`, `ysolde_face`, `ysolde_face_stylized`, `ysolde_silhouette_lineup`,
      `ysolde_clip_cast_glyph`, `ysolde_clip_reink_shell` and `ysolde_night_ch4`. Baselines are **viewed** and approved.
      Run with `HYMN_SHOTS` set to these ids only.
- [ ] `docs/kb/art/characters/ysolde_review.md` (a strict SPEC §14 assessment), an update to the live log
      (`docs/kb/handoffs/live/characters.md`), and a session handoff.

## Notes
- Gate scope (CLAUDE.md §3): the Blender rebuild for the `ysolde` job, plus the shared jobs only if a shared module
  changed; the rig probe and the hero-clip tests; `HYMN_SHOTS` limited to the shots above.
- The costume motif is Glyph Trace's five strokes written as **brush calligraphy** (ysolde.md §3). It must not reproduce
  the M2-UI-03 panel art. If UI wants the brush look, they read the same `motifs/` stroke data.
- The Act II hair variant (`HairDown`, with the pin removed) is designed in ysolde.md §5 and built with the Ch13 content,
  not here.

## Review log
