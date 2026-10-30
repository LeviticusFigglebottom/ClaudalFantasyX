---
id: M3-CHR-03
title: "Act I named characters: Liss Varrow (hero path), Tavi Orse and Mother Kell (villager path)"
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
depends_on: [M2-CHR-03, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Build the Act I named characters from [`act1_npcs.md`](../../art/characters/act1_npcs.md) §2-§4.

**Path change from the brief:** Liss is built on the **hero** path (act1_npcs.md §0), because she is a party member. She
joins in Ch6, has a battle niche, a Swell input and a `speakers.json` portrait, and she carries the game's rawest grief
scenes. Tavi (Ch7) and Kell (Ch1) are villagers on pipeline.md §15. The Lead may split Liss into her own task; her
criteria below are already separate.

## Acceptance criteria
### Liss (hero path, act1_npcs.md §2)
- [ ] `assets_src/characters/liss/` on the shared modules. `liss_params.json` holds every number in §2.1 and §2.10.
      `liss_textures.py` has the **line-mark generator** (11 marks, right side only, the eleventh on the cheek), and
      later Saltwright builds can import it.
- [ ] M1-CHR-14 lessons apply:
      - the coat's long back is two leg-following tails with bones, not a tube;
      - the armholes sit at least 11.5 cm below the shoulder joint;
      - the launcher sits 2 cm off the thigh, on its own prop bone;
      - the hair tail's root is seated on the head SDF, and the scalp cards stop 12 mm short of it.
- [ ] Job `liss` with `"threads": 4`, byte-identical across two runs, with `PRE_ROUND` set. LOD0 at most 60k, LOD1
      about 28k, and the GLB under 5 MB.
- [ ] A `liss` entry in `tools/dev/rig_checks.json` (garments `Costume` and `WorkSleeve`; props `Launcher`; the `braid`
      entry for `HairTail:hair`). `rig_probe.py --hero liss --report` passes, or each ratchet is pinned with a viewed
      reason.
- [ ] Face poses (all 15 tags, §2.6) and clips (§2.8) through `hero_clips.py --hero liss`, with the other heroes'
      libraries byte-identical. A battle actor, `liss_battle.tscn`, on the LOD1.
- [ ] Shots `liss_front`, `liss_back`, `liss_face`, `liss_face_stylized`, `liss_silhouette_vs_rhen` and
      `liss_clip_haul_rope`. Baselines are viewed and approved.

### Tavi Orse and Mother Kell (villager path, act1_npcs.md §3-§4)
- [x] `params/tavi.json` and `params/kell.json` from the drafts in §3.3 and §4.3, tuned against the face shots. Jobs
      `villager_tavi` and `villager_kell` with `"threads": 4`, byte-identical. LOD0 inside `test_villagers.py`'s 20–36k
      range, each GLB under 3 MB, and an `<npc>_actor.tscn` for each.
- [x] `villager_hair` accepts a `female` hairline on the `short` kind (for Kell), if it doesn't already. If that module
      changes, every `villager_*` job is re-verified.
- [x] Face poses `game/levels/_tests/characters/villagers/{tavi,kell}_face_poses.json`: all 15 tags, with the overrides
      in §3.4 and §4.5.
- [x] The wick, the wick bundle and the trimming shears come from one source (`assets_src/characters/props/wick.py`, or
      wherever the build settles), with PROVENANCE rows. The same wick serves Rhen's tin and the E7 post-credits lamp.
- [x] Shots `villager_tavi_front`, `villager_tavi_face`, `villager_kell_front` and `villager_kell_face`, plus a lineup
      with the Haluna villagers. Baselines are viewed and approved.

### All
- [ ] PROVENANCE rows for every output. `villagers_review.md` updated for Tavi and Kell, `liss_review.md` written, the
      live log updated, and a handoff.

## Notes
- Mother Kell is Oruvel's **chandler**, who never learned to swim (N-25 S1, ADR 0022 sweep-H S1). She is not "the old
  Oruvel diver": those glossary rows are superseded. She is never drawn as a mentor, or as a keeper Dace charged with
  his son (sweep-H B1).
- Echo watch for Liss (act1_npcs.md §2.2): no goggles, no yellow, no swirl patterns, and trousers rather than a skirt.
- Tavi's and Kell's extra clips belong to M3-CHR-04, because they need per-NPC clip lists in `villager_clips.py`.
- **2026-10-24, villager half (character-13, worktree subagent; handoff 2026-10-24-character-13.md).** Tavi and Kell
  are done; Liss's criteria and the "All" row's `liss_review.md` remain, so the task stays `doing`.
  - **Pipeline (shared villager modules, every change opt-in):** `_build.host_snaps` applies M1-CHR-14's MIDLINE_SNAP,
    quantize_uvs, snap_shape_noise and PRE_ROUND. `_build.garment_fit` puts the top on the torso only, makes the skirt
    and apron follow the legs (build_asha.skirt_weights), puts the sandals on the feet and keeps the trousers off the
    arms. Also new: top `armhole_drop_m` (Tavi 0.115) and `cover_margin_m`, skirt `keep_above_knee_m` (Kell 1.0: whole
    legs under the calf skirt), `_skin.fingertip_oil` (Kell 0.25) and `villager_clips.EXTRA_CLIPS`. The seven M2
    villagers carry none of these, so their outputs stay byte-identical (verify below).
  - The M3-CHR-04 clips came along, because the per-NPC list was needed anyway. Tavi has `hand_on_shoulder`,
    `hear_news` and `name_rite`; Kell has `press_wick`, `trim_wick` (a loop) and `haggle_laugh`. Hand heights and palm
    directions were checked numerically against the rig: Kell's left palm faces up at 1.02 m, the right palm faces
    down over it, and the slap lands at 0.99 m. Tavi's hand rests at 1.40 m, and his float hands are 15 cm apart at
    1.29 m.
  - `villager_hair` already took `hairline: "female"` on `short` (the table is looked up by name), so it was not
    changed.
  - Numbers: Tavi LOD0 30,198 (LOD1 14,258), GLB 1.85 MB. Kell LOD0 33,596 (LOD1 15,958), GLB 2.03 MB. Props: wick 580
    triangles, bundle 2,456, shears 772.
  - Rig probe (`rig_probe.py --hero tavi --hero kell`, now villager-aware). Tavi: Costume 29.9 mm (6 vertices, talk),
    Body 66.4 mm (1 vertex, walk), 2 exposed vertices at 5 mm. Kell: Costume 31.5 mm (6, haggle_laugh), Body 4.8 mm (2),
    6 exposed vertices at 4.6 mm under the sleeve (walk). Before `keep_above_knee_m`, Kell's thigh edge was exposed by
    110 mm in the walk; now 0. Seams and weights are clean. What remains is the hanging upper arm in the torso
    garment's side, the linear-skinning limit the heroes also carry. It was viewed in clip frames and pinned as
    ratchets in rig_checks.json with reasons. Changing `arms_down` (41 to 37, 38 to 34) did not move it, so it was
    reverted to the sheet's values.
  - Known limits: the mourning band reads a little like a soft visor at the face camera (the same band as the
    fisher's). Kell's short grey crop is still card-flaky up close (villagers_review.md §4). Kell's face reads broad and
    a little masculine (the donor's adult face, age in the textures). No props sit in the GLBs; the wick, bundle and
    shears are scene props for BoneAttachment3Ds.
- **2026-10-24, Liss WIP (character-15, worktree subagent; paused by the Lead for the playtest).** Committed as a
  WIP, task stays `doing`. **In:** `assets_src/characters/liss/` (build_liss, liss_params with every §2.1/§2.10
  number, liss_costume: top + coat with two leg-following tails on 2x3 bones + harness X with 6 pouches + trousers +
  boots + sleeve strap; liss_hair: crop + two-strand beaded tail on a 6-bone chain, root seated, cards stop 12 mm;
  liss_props: launcher on DEF-launcher 20.5 mm off the thigh with a sling; liss_textures with the shared
  `line_marks`/`paint_marks` generator, 11 marks right side only, PRE_ROUND; write_materials; build.sh). The
  work-sleeve and glove are an offset shell of the shipped left arm/hand skin with the skin's weights. Outputs in
  `assets/characters/liss/` (LOD0 55,820, LOD1 ~25.6k, GLB ~4.1 MB), job `liss` (threads 4), import rule,
  `liss` in rig_checks.json (garments Costume+WorkSleeve, props Launcher, braid HairTail:hair; **no ratchets yet**),
  the hero_clips Liss block (persona + `launcher` dispatch key, 10 clips + the 11 battle-contract clips; one
  `elif hero == "liss"` line in `_victory`); other heroes' libraries regenerate byte-identical. Stage scenes, face
  poses (15 tags), battle actor, `tools/tests/test_liss.py`.
  - **Not in sync:** the last two source edits (tail root raised to 0.40 h: `TAIL_ROOT_H`; armpit-crease arm skin
    kept under the sleeve: `SLEEVE_KEEP_NEAR_TORSO`) are **not yet built** into the committed GLB/textures.
  - **Probe at the committed GLB (p5):** launcher 0, drift 0, seams 0, weights clean. Open: braid gap 4.1 mm
    (point_up; the root-height edit targets it), boundary_exposed 5 verts ~5 mm at the left armpit (the keep edit
    targets it), garment_in_body WorkSleeve ~25 mm and Body-through-cloth ~35-46 mm at both armpits (LBS armpit:
    to pin as ratchets after viewing), trouser knee fold 26 mm (run) / 39 mm (crouch_shelter, 112-degree squat).
  - **Exact next step:** run `assets_src/characters/liss/build.sh` (Blender ~45 s + textures ~6 min), then
    `python3 tools/dev/rig_probe.py --hero liss --report`; view the armpit/knee poses, pin the ratchets with
    reasons in rig_checks.json; add `TestRigIntegrityLiss` to test_rig_integrity.py, `TestLissClips` to
    test_hero_clips.py, liss to test_hero_battle_clips.py HEROES/EXISTING; add the 7 `liss_*` shots to shots.json
    (front, back, three_quarter, face, face_stylized, silhouette_vs_rhen, clip_haul_rope: removed from this WIP
    because they have no baselines yet), capture, view, approve; PROVENANCE rows; verify_blender_builds `--job liss`
    twice (plain and NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4"); liss_review.md and the handoff. Visual notes from
    the first renders: the coat now carries a rust binding so it separates from the top; launcher sling added; side
    hairline lowered for the crop; freckles strengthened (all built into the committed files except the two edits
    above).

- **2026-10-27, Liss's hero half resumed and built (characters, new account).** The saved WIP patch is applied onto
  M1-CHR-15, M2-CHR-513 and M3-CHR-05.
  - **Build brought up to date:** M1-CHR-15's conventions (the donor, head and every part on the 1 µm grid; the
    shoulder correctives `DEF-armpit.L/.R`), on top of the WIP's M1-CHR-14 snaps and PRE_ROUND. The two unbuilt
    edits (`TAIL_ROOT_H`, `SLEEVE_KEEP_NEAR_TORSO`) are now built. LOD0 GLB 4.19 MB, LOD1 26,076 tris / 1.19 MB.
    `verify --job liss` identical natively, with X86_V4 off and with X86_V3+V4 off.
  - **Clips:** her 10 own clips, the battle contract and `revive`. The WIP's ko called `_ko_kneel`, which M2-CHR-513
    removed, so she now takes the shared fall and rise, with her own rows in the KO tables (her mid-calf trousers
    leave the ankle free, so she kneels with the toes half tucked). Victory is her own loop on top of the shared sway.
    Her 10 dialogue calls (Ch6-Ch8: collide, dig_sand, flatten_sand, hand_over, set_in_hole, stand,
    charcoal_rubbing, coil_rope, drive_pin, ease_key) are built from requested_clips.json. Her right hand works and
    talks; nothing crosses the launcher at her right hip.
  - **Probe ratchets** (rig_checks.json, with reasons): Costume 43/6 (trouser knee folds in the 112-degree squat and
    the kneel), WorkSleeve 12/6 (the sleeve shell at the armpit crease), Body 70/32 (both arms raised past 90
    degrees in haul_rope and point_up), max_exposed 2, braid gap 2.6 (the WIP measured 4.1; the raised tail root
    brought it to 2.55).
  - **Tests:** TestRigIntegrityLiss; Liss in test_hero_battle_clips' HEROES (ko and revive stay above the floor);
    her dialogue calls in test_hero_clips; test_liss (77 standard bones with the correctives).
  - **Shots:** the 7 liss_* shots are in shots.json, requested from the PC; not seen yet.
  - **Remaining for review:** view the PC render, approve the baselines, write liss_review.md and the handoff.
- Dialogue polish, Tavi (chr-npc-polish): before, his mourning band stood about a centimetre off the brow, high and wide, with hair poking through it and yellow-brown highlight chips on the black hair. After: the band's edges drawn in to the skin and its face rounder (`headwrap.edge_off_m`, `off_m`), the hair under it pressed inside the band (`headwrap.press_hair`), and a dimmer, cooler hair specular (`_hair.spec`); the band now grips the head and the hair reads as dark strands.

## Review log
- 2026-10-27 characters: viewed the render lead/gate-render-characters-ee3bd33 (cloud lavapipe). Approved liss_front, liss_back, liss_three_quarter, liss_face, liss_face_stylized, liss_silhouette_vs_rhen and liss_clip_haul_rope as baselines. Notes in docs/kb/art/characters/liss_review.md (hair fringe follow-up). Over to Rendering for the review.
