---
id: M3-CHR-02
title: "High Warden Sefir Aurane on the hero path (the antagonist, first seen at the end of Ch6)"
role: character
status: doing
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
- [ ] **Build:** `assets_src/characters/sefir/` on the shared modules, with nothing copied. `sefir_params.json` holds
      every number in §1.1 and §1.10.
      - The face is fully symmetric: no asymmetric slider and no asymmetric pose.
      - The over-robe is four leg-following panels with 4 panel bones each, and its hem sits 1.5 cm off the floor. No
        floor-length tube.
      - The mantle is on a hinge bone, with 25 mm of shoulder clearance.
      - The crown is head-rigid, with at least 30 mm of mantle clearance across a head pitch of −20° and a yaw of ±40°.
      - The long hair is on bone chains, with a 0.1× wind response.
- [ ] **Reproducible:** job `sefir` in `tools/dev/blender_builds.json` with `"threads": 4`. Its sources include
      `asha/**`, `rhen/**`, `toma/**`, `base_body/**` and `third_party/mpfb2/**`. Two runs are byte-identical, and the
      texture run sets `PRE_ROUND`.
- [ ] **Budgets:** LOD0 at most 62k (ceiling 70k). LOD1 about 28k, and it keeps the crown disc, the mantle outline and
      the front hair falls. `sefir.glb` is under 5 MB, and every PNG under 5 MB.
- [ ] **Rig guards:** a `sefir` entry in `tools/dev/rig_checks.json` (garments `Costume`, `Mantle` and `HairBack`; props
      `Crown`). `rig_probe.py --hero sefir --report` passes, or each ratchet is pinned with a viewed reason.
      `test_rig_integrity.py` covers him.
- [ ] **Face poses:** all 40 shapes, and `game/levels/_tests/characters/sefir/sefir_face_poses.json` with the 15
      symmetric rows of §1.6. The `sefir_eye_still` material variant exists for Act II. Cinematics is asked to set his
      slow blink interval (10–14 s) in `sequencer.json`.
- [ ] **Clips:** the Act I clips of §1.8: `idle` (no motion: `sway` 0, `breath` 0), `talk`, `raise_palm`, `incline_head`,
      `glance` and `pivot`. `walk_glide` is specified for Ch13. The persona keys `breath` and `hands_joined` leave the
      other heroes' libraries byte-identical. `test_hero_clips.py` asserts that his idle is still (zero rotation delta
      across its keys).
- [ ] **PROVENANCE:** rows for every output, including the Level-scale motif data.
- [ ] **Shots:** `sefir_front`, `sefir_three_quarter`, `sefir_back`, `sefir_face`, `sefir_face_stylized`,
      `sefir_silhouette_lineup` (beside Ysolde: the white figure and the black one) and `sefir_clip_raise_palm`.
      Baselines are viewed and approved, with `HYMN_SHOTS` set to these ids.
- [ ] Request tasks are filed for Rendering and Environment: his reflection never ripples, and his shadow is too sharp
      (§1.10).
- [ ] `docs/kb/art/characters/sefir_review.md`, an update to the live log, and a handoff.

## Notes
- Echo watch (act1_npcs.md §1.2): plain loose hair, a clean face, and no markings. Keep it that way in every revision.
- The barge belongs to Environment. The final boss's battle actor is Act III work; it will use the LOD1 built here.

## Review log
