# Live log: characters environment

**This environment owns this file** (CLAUDE.md §7a). Cloud session `session_01JqzzxgJU9Dmu7fRhmCG9aQ`, branch
`claude/characters` (cut from `claude/undertow-lead-handoff-423ixt` at 952ef7c). The Lead reads it hourly.

## Now
- **Blocker cleared (d523d43):** Toma's mouth/teeth/tongue are on `character_mouth`; the integration branch is merged;
  `--filter=character_shading` 17/17, hero_stage 6/6, post_import 19/19; `verify --job toma` 38 identical. Ready to merge.
  (send_message to the Lead was refused: "needs a trusted device", so this log is the channel.)
- **M1-CHR-14 → review (reviewer: rendering). Ready to merge.** Handoff: 2026-10-24-character-8.md.
  - **Braid (ddc5eb2):** seated on the scalp; scalp cards run to within 12 mm of the root; scalp_cards 122. Probe gap 1.9 mm, drift 0.
  - **Guards:** `tools/dev/rig_probe.py`, `rig_checks.json`, `tools/tests/test_rig_integrity.py` (34 tests, passing). Docs: pipeline.md §16.
  - **Asha (47b36c5):**
    - Skirts follow the legs; the shins stay under the skirts, so there is no floating foot.
    - Sandals ride the feet; the vest, bodice and collar ride the torso, with deeper armholes; the staff sits 1 cm out.
    - LOD0 64,624 (target now 65k).
  - **Toma (0e2f769):** the tunic armhole drops; the shield clears his head; the spear's offset, splay and binding are fixed; the spear clips are staggered.
  - **Rhen:** clean in two new clip shots.
  - **Probe, worst mm before → after:**
    - Asha skin through cloth: 264 → 47 (armpit only).
    - Asha exposed boundary: 51 vertices → 2.
    - Asha staff: 6.7 → 0.
    - Toma shield: 26 → 0.
    - Toma spear: 27 → 15.
    - What remains is linear-skinning limits, pinned per hero as ratchets in rig_checks.json.
  - **Follow-up M1-CHR-15 (todo):** skirt and corrective bones. The deepest lunge still stretches Asha's tube skirts (asha_clip_offer_hand).
  - **RMSE of the re-approved shots (all viewed side by side):**
    - Braid round, 18 shots: face_neutral .0311, face_smile .0316, face_grief .0314, stylized_compare .0269, smile_variant .0270, sleeve_s0 .0138, sleeve_s4 .0138, profile .0110, q34 .0108, clip_run .0107, clip_face_west .0104, clip_walk .0103, front .0100, extreme_pose .0092, battle_idle .0078, clip_laugh .0077, kneel .0075, offer_hand .0065. This round includes the CHR-10 to 13 drift.
    - Clipping round, 13 shots: offer_hand .0558, kneel .0453, laugh .0448, run .0309, extreme_pose .0221, walk .0188, stylized .0158, smile_variant .0158, battle_idle .0141, face_west .0120, sleeve_s0 .0100, sleeve_s4 .0100, q34 .0098.
    - Toma: face_neutral .0212, face_smile .0212, back .0181, profile .0179, battle_idle .0132, front .0122, q34 .0098.
    - New baselines: rhen_clip_take_hand, rhen_clip_kneel, toma_clip_walk, toma_clip_talk.
- **M2-CHR-03 villagers → review:**
  - Merged (6b39760) and rebuilt on the shared costume and mouth changes (8e57be6).
  - 9 villager shots re-approved after viewing: osu_face .0222, child_face .0215, reed_face .0191, fisher_face .0145, neme_face .0134, reed_front .0120, vendor_face .0112, netmender_front .0103, lineup .0088.
  - The capsule → actor scene table for m2-slice is in 2026-10-24-character-7.md.
- **Gates run:**
  - `verify --job asha`: 44 identical.
  - Godot `hero_stage` 6/6, `post_import` 19/19.
  - validate_data and taskboard: OK.
  - `test_rig_integrity` 34 OK; `test_asha` OK.
  - Still running: verify for rhen, toma and the villager jobs, and the full tools/tests run. The next entry records the result.

## Queue
1. ~~M2-CHR-01 Rhen~~ (review) → 2. ~~M2-CHR-02 Toma~~ (review) → 3. ~~M2-FP-07 clips~~ (review) → 4. ~~M1-CHR-12~~ (review;
   fault A after RND-24) → 5. ~~M1-ART-06~~ (review).

## Done
- **M1-CHR-13 → review:** the costume normals and winding fix (`asha_costume._outward` / `_panel`), all three heroes rebuilt
  (asha 44 / rhen 31 / toma 38 identical); drift viewed and re-approved, RMSE listed in the task file.
- **M1-RND-25 → review:** the lips' inner roll is on the mouth family (by facing), for every hero; the grief rim is softened.
- **M2-CHR-04 Toma follow-ups → review** (worktree subagent, merged and rebuilt): hair and beard, sash tails, reinforced
  sandals, 11 rig-extra bones, 10 clips. Re-approved toma_* after viewing.
- **M2-CHR-05 smile variant → review:** `variants.duchenne_open` in asha_face_poses.json, plus the `asha_smile_variant_compare`
  shot, for the human with ADR 0019.
- **M2-CHR-06 battle-scale heroes → review:** `game/characters/heroes/{asha,rhen,toma}_battle.tscn` (LOD1 + clips via the
  import rule). **Hook: M2-UI-07** (UI+Combat: FighterStandIn instances a `"scene"` spec).
- **M2-CHR-02 Toma → review** (reviewer: rendering). Built by a worktree subagent, merged at this branch's Toma merge
  commit, then rebuilt for CHR-12's shared modules. 58,168 LOD0 tris (budget 66,000), `toma.glb` 4.86 MB (near the cap:
  each beard vertex carries all 40 morph targets), 16 textures; costume atlas 2K, not toma.md's 4K (5 MB cap).
  - **To merge:** `verify --job toma` 37 identical; **6 new baselines** toma_{front,q34,profile,back,face_neutral,face_smile};
    Godot hero_stage 4, post_import 19, character_shading 16 green; tools test_toma.
  - The scar is one depth field that both cuts the plates and paints red → black → bone; a test checks no lacquer survives
    inside it (no emblem shape can remain).
  - Open (toma_review.md): hair and beard cards read as flakes up close; stiff sash tails; thin sandal soles; rig extras;
    a shared `asha_costume._panel` winding bug (the front layer faces inward; fixing it changes Asha and Rhen).
- **M1-ART-06 → review** (reviewer: rendering): RND-18's survey numbers are recorded as the Art sign-off in color_script.md, and the crest finding is closed (a1cc542).
- **M1-CHR-12 Asha round 7 → review** (reviewer: rendering). Details: asha_review.md §12.
  - Lower and uneven hairline with wisps; looser crown.
  - Lid band: the lit eye's R:B is 2.61 against the cheek's 2.32 (passes); the far eye is still 3.23 against 2.00. The
    root cause is the brow's shadow under the warm key, not the albedo.
  - Grief peg teeth fixed; a stronger AU6 smile-eyes shape; ADR 0024 check 1 appended; asha.glb 4.61 MB (0.39 MB headroom).
  - **To merge:** `verify --job asha --job rhen` 44 and 31 identical. **Re-approved** asha_face_neutral, _smile, _grief and
    _stylized_compare (after viewing). **Drift, not re-approved:** asha_front 0.0025, asha_q34 0.0029, asha_profile 0.0018,
    asha_extreme_pose 0.0025, asha_sleeve_s0/s4 0.0007. The shared modules changed, so Rhen was rebuilt too (his
    baselines and the asha_clip_* baselines are refreshed; they're this branch's own).
  - Open, Art's calls: the smile still reads as a lopsided smirk (ADR 0025 and asha.md §6.3; a proposal is in §12.4).
- **Integration merge** at 6f6d1d3: the finished Rhen supersedes the parked WIP. My duplicate M2-CHR-01 file was folded
  into review-sweep-O's `M2-CHR-01-rhen-toma-donor.md` (Rhen; Toma is M2-CHR-02). Rhen's mouth is now on the
  character_mouth family.
- **M2-FP-07 Asha's clips → review** (reviewer: lead). 11 clips in `assets/characters/asha/anim/asha_clips.tres` (+ Rhen's 7
  incl. take_hand), generated by `assets_src/characters/asha/hero_clips.py`; an import rule gives `asha.glb`/`rhen.glb` an
  `AnimationPlayer`, so the sequencer plays `@anim asha <clip>` with **no level-scene change**. **Asha adopted the
  `characters` import rules** (asset_import.md). Kneeling clips: `laugh`, `offer_hand`; `rise_to_stand` from the kneel.
  - **To merge:** new baselines `asha_clip_{kneel_over_rhen,walk,offer_hand,face_west,laugh,run}`. **Drift (not
    re-approved):** `asha_face_stylized_compare` rmse 0.00000 → 0.00002 (5 sub-pixels ≤ 5/255) after the adoption; all
    other asha_*/rhen_* shots unchanged. Godot `--filter=post_import|hero_stage|character_shading|fp_|haluna|cutscene|first_verse`
    green; `tools/tests/test_hero_clips.py`.
  - **Merge note:** `docs/kb/tasks/M2/M2-FP-07-asha-clips-request.md` was copied from claude/first-playable (it is not on
    the integration branch yet), so merging that branch gives an add/add conflict on it: keep this branch's copy.
  - For m2-slice: face shape names = asha.md §6.2; emotion weights = `asha_face_poses.json` (Rhen: `rhen_face_poses.json`).
- **M2-CHR-01 Rhen → review** (reviewer: rendering or lead; task file `M2-CHR-01-rhen-toma-donor.md`). `assets_src/characters/rhen/` on Asha's MPFB2 pipeline (imports
  her modules; `build_asha` as a helper library). 57,914 LOD0 tris, `rhen.glb` 4.37 MB. Review: docs/kb/art/characters/rhen_review.md.
  - **To merge:** `verify_blender_builds.py --job rhen --job asha` → asha 44 identical, rhen 31 identical. Shots: asha_* (10)
    unchanged; **6 NEW baselines** (rhen_front, rhen_q34, rhen_profile, rhen_back, rhen_face_neutral, rhen_face_smile), approved
    on lavapipe. No existing baseline re-approved. Godot `--filter=hero_stage` and `--filter=character_shading` green.
  - Shared-file edits: assets/PROVENANCE.md (rows appended), tests/screenshots/shots.json (6 entries after the asha block),
    tools/dev/blender_builds.json (job `rhen` after `asha`), asha_textures.py (3 knobs, Asha's defaults), asha_stage.gd
    (`character_name`).
  - Ask the PC GPU session for a capture of the Rhen face and hair shots.
- Setup: branch pushed; Godot 4.6.3, render deps and Blender 5.0.1 fetched.

## Un-pushed state
- None.
