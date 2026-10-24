---
id: M3-CHR-02
title: "High Warden Sefir Aurane on the hero path (the antagonist, first seen at the end of Ch6)"
role: character
status: review
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
depends_on: [M2-CHR-01, M2-CHR-02, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Sefir first appears at the end of the Ch6 Brine Shoals raid (ADR 0017) and carries close-ups through Act II and into the
final boss fight. Build him on the pipeline.md §12 hero layout from
[`act1_npcs.md`](../../art/characters/act1_npcs.md) §1.

## Acceptance criteria
- [ ] **Design:** act1_npcs.md §1 is reviewed. The Art Director decides the close-up gold budget (§1.4: a written
      exception, or 40% mantle coverage) before the shots are approved.
- [x] **Build:** `assets_src/characters/sefir/` on the shared modules, with nothing copied. `sefir_params.json` holds
      every number in §1.1 and §1.10.
      - The face is fully symmetric: no asymmetric slider and no asymmetric pose.
      - The over-robe is four leg-following panels with 4 panel bones each, and its hem sits 1.5 cm off the floor. No
        floor-length tube.
      - The mantle is on a hinge bone, with 25 mm of shoulder clearance.
      - The crown is head-rigid, with at least 30 mm of mantle clearance across a head pitch of −20° and a yaw of ±40°.
      - The long hair is on bone chains, with a 0.1× wind response.
- [x] **Reproducible:** job `sefir` in `tools/dev/blender_builds.json` with `"threads": 4`. Its sources include
      `asha/**`, `rhen/**`, `toma/**`, `base_body/**` and `third_party/mpfb2/**`. Two runs are byte-identical, and the
      texture run sets `PRE_ROUND`.
- [x] **Budgets:** LOD0 at most 62k (ceiling 70k). LOD1 about 28k, and it keeps the crown disc, the mantle outline and
      the front hair falls. `sefir.glb` is under 5 MB, and every PNG under 5 MB.
- [x] **Rig guards:** a `sefir` entry in `tools/dev/rig_checks.json` (garments `Costume`, `Mantle` and `HairBack`; props
      `Crown`). `rig_probe.py --hero sefir --report` passes, or each ratchet is pinned with a viewed reason.
      `test_rig_integrity.py` covers him.
- [x] **Face poses:** all 40 shapes, and `game/levels/_tests/characters/sefir/sefir_face_poses.json` with the 15
      symmetric rows of §1.6. The `sefir_eye_still` material variant exists for Act II. Cinematics is asked to set his
      slow blink interval (10–14 s) in `sequencer.json`.
- [x] **Clips:** the Act I clips of §1.8: `idle` (no motion: `sway` 0, `breath` 0), `talk`, `raise_palm`, `incline_head`,
      `glance` and `pivot`. `walk_glide` is specified for Ch13. The persona keys `breath` and `hands_joined` leave the
      other heroes' libraries byte-identical. `test_hero_clips.py` asserts that his idle is still (zero rotation delta
      across its keys).
- [x] **PROVENANCE:** rows for every output, including the Level-scale motif data.
- [x] **Shots:** `sefir_front`, `sefir_three_quarter`, `sefir_back`, `sefir_face`, `sefir_face_stylized`,
      `sefir_silhouette_lineup` (beside Ysolde: the white figure and the black one) and `sefir_clip_raise_palm`.
      Baselines are viewed and approved, with `HYMN_SHOTS` set to these ids.
- [x] Request tasks are filed for Rendering and Environment: his reflection never ripples, and his shadow is too sharp
      (§1.10).
- [x] `docs/kb/art/characters/sefir_review.md`, an update to the live log, and a handoff.

## Notes
- **2026-10-24, build (worktree subagent; review: rendering).** Full write-up: `docs/kb/art/characters/sefir_review.md`;
  handoff `docs/kb/handoffs/2026-10-24-character-11.md`.
  - Built: `assets_src/characters/sefir/` (build_sefir, sefir_costume, sefir_hair, sefir_props, sefir_textures,
    write_materials, motifs/level_scale.json, build.sh); job `sefir` (threads 4) in blender_builds.json.
  - LOD0 58,426 tris, LOD1 27,118; sefir.glb 4.42 MB, sefir_lod1.glb 1.29 MB; 12 PNGs, largest 3.04 MB.
  - Rig guards: every check passes at the default limits, no ratchet (worst: Costume 2.98 mm, skin through cloth
    0.37 mm, 0 exposed boundary, seams 0). Crown-to-mantle clearance 39.7 mm at pitch -20 / yaw +-40; hair outside the
    mantle at rest and through his clips (both in test_sefir).
  - **Gold budget decided (no exception):** measured by geometry, the sheet's 40% mantle option gives 6.0% in a waist-up
    frame (the crown alone is 3.7-4.4%), so the mantle's gold is lowered to **14%**: front waist-up 4.96%, hero
    three-quarter 4.45% (tested). Chest-up close-ups are 8-9%, mostly the crown: frame his close-ups waist-up or wider,
    or the Art Director rules on the crown.
  - Clips: a `sefir` persona and clip list in hero_clips.py (breath 0, hands_joined); the other heroes' libraries are
    byte-identical. `walk_glide` is built as well as specified.
  - Requests filed: M3-CIN-01 (slow blink, face poses, blend), M3-RND-03 (still reflection, sharp shadow), M3-ENV-01
    (no wake). `sefir_silhouette_lineup` is with Toma, Asha and Rhen: Ysolde is not on this branch yet.
- Echo watch (act1_npcs.md §1.2): plain loose hair, a clean face, and no markings. Keep it that way in every revision.
- The barge belongs to Environment. The final boss's battle actor is Act III work; it will use the LOD1 built here.

## Review log
