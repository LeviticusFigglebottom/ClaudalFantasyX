# Live log: characters environment

**This environment owns this file** (CLAUDE.md §7a). Cloud session `session_01JqzzxgJU9Dmu7fRhmCG9aQ`, branch
`claude/characters` (cut from `claude/undertow-lead-handoff-423ixt` at 952ef7c). The Lead reads it hourly.

## Now
- **M3-CHR-02 Sefir → review (rendering), worktree subagent, not pushed.** Hero build on the shared modules: LOD0 58,426,
  LOD1 27,118, sefir.glb 4.42 MB; rig probe all ok with no ratchet; `verify --job sefir` 32 identical (also on the AVX2
  numpy path). Mantle gold lowered to 14% so a waist-up frame is <= 5% (front 4.96%); chest-up close-ups are 8-9%
  (the crown). 7 sefir_* baselines. Requests M3-CIN-01, M3-RND-03, M3-ENV-01. Handoff 2026-10-24-character-11.md,
  review `docs/kb/art/characters/sefir_review.md`.
- **M3-CHR-01 Ysolde → review (reviewer: rendering).** Worktree subagent off cd01d151, commits aa4cc74b, cb9c3ade +
  docs; not pushed. Handoff 2026-10-24-character-10.md, review ysolde_review.md.
  - LOD0 58,918 / LOD1 27,894; 4.31 / 1.27 MB. `verify --job ysolde` 37 identical, also under the AVX2-only numpy path.
  - Probe: props and collar 0 mm, seams 0; ratchets costume 31/6 (run knee fold), body 45/70 (armpit), 4 exposed.
  - hero_clips.py edits are self-contained (persona, clips, a Ysolde block after `pose_at`; `.get()` branches);
    Asha's, Rhen's and Toma's libraries byte-identical. Merging with e32848cc touches only the append-only lists.
- **MERGE-READY @ e253f302 (CHR-14 braid and clipping, villagers, Rhen and Toma, host determinism).**
  - **Full `tools/ci_local.sh` at ad6e232:** merged with the integration branch, run with `taskset -c 0-3`, HYMN_BLENDER_REQUIRED=1, every shot and its own HYMN_LOG_DIR. It exited 0:
    - 580 tool tests, 1459 Godot tests;
    - 120 shots compared, 0 failed;
    - Blender identical: asha 44, rhen 31, toma 38, and the 7 villager jobs (34 + 6×30).
  - **What changed between ad6e232 and e253f302:** your 1-ULP head UV fix only. `quantize_uvs` puts Asha's head and body UVs on a 2^-16 grid right after the unwrap, before the bake dump and the export.
  - **Scoped re-check for that delta:**
    - `verify --job asha` under taskset (4 CPUs): 44 identical;
    - the GLBs are identical with numpy's AVX-512 and AVX2 paths;
    - the 18 asha_* shots pass unchanged (max RMSE 0.00797, asha_front, the same as before);
    - test_asha and test_rig_integrity: OK.
  - **Threads:** pinned at 4 on every character and villager job (ad6e232).
- **Later heads (docs plus your branch only):** the M3 design sheets merge (Ysolde, Sefir, Liss, Tavi Orse, Mother Kell; M3-CHR-01 to 04) and an integration-branch merge that touches no character file.
  - Per the new gate rules I stopped the second full `ci_local`. Scoped checks: `character_shading` 17/17, validate_data and taskboard OK.
- **MERGE-READY @ (this commit): M2-CHR-07, the hero battle clip set** (review: combat). Handoff: 2026-10-24-character-12.md.
  - Asha, Rhen and Toma each have the battle track's 12 contract clips: in place, with a `contact` Animation marker at contact_at.
  - **Scoped gates:**
    - tools/tests 590 OK;
    - test_rig_integrity 34 OK;
    - hero_stage 6/6 and post_import 19/19;
    - verify asha 44, rhen 31, toma 38 identical (the existing clip sub-resources are byte-identical);
    - asha_clip_*, rhen_clip_*, toma_clip_* and the battle_idle shots pass;
    - 3 new shots (`<hero>_battle_attack`), viewed and approved.
  - **Ratchet:** Asha's VerseSleeve count limit rose 4 → 6 (sleeve-top vertices under the sleeve at hit and defend; viewed). The depth limit is unchanged.
  - **Requests sent to the battle track:** read the `contact` marker (contact currently lands late), finisher and support per-style timing, and ko revive.
  - **The battle track has wired all three:** strikes land on the `contact` marker, the shared finisher and cast clips are fine, and a revive returns a hero to idle. **To do:** review M2-BPR-10 (their placeholder battle poses; reviewer: character) once claude/battle-presentation and this branch meet on the integration branch.
- **MERGE-READY @ e32848cc: M3-CHR-02 Sefir Aurane** (review: rendering). Handoff: 2026-10-24-character-11.md; review: sefir_review.md.
  - **Build:** LOD0 58,426 tris, sefir.glb 4.42 MB.
  - **Probe:** passes at the default limits, with no ratchet.
  - **Reproducibility:** `verify --job sefir` 32 identical, on both numpy SIMD paths.
  - **Gold:** the mantle's gold is cut to 14%, which gives a waist-up frame of 4.96% (under the 5% limit). Chest-up close-ups are still 8–9%, from the crown. That needs a Cinematics framing rule or an Art Director ruling; no exception claimed.
  - **New shots:** 7, viewed and approved. Request tasks: M3-CIN-01 (slow blink), M3-RND-03, M3-ENV-01.
  - **Gates after merging with M2-CHR-07:**
    - hero_clips merged as the union of both blocks; all four clip libraries regenerate byte-identical;
    - test_hero_clips, test_hero_battle_clips, test_sefir and test_rig_integrity: OK;
    - post_import 19/19.
- **MERGE-READY @ (this commit): M3-CHR-01 Ysolde (review: rendering) and M3-CHR-03, villager half: Tavi Orse and Mother Kell.**
  - **Ysolde:** LOD0 58,918, ysolde.glb 4.31 MB. `verify --job ysolde` 37 identical, on both numpy SIMD paths. Collar, book and ink-guards 0 mm.
    - Ratchets: costume 31/6 (a run knee fold under the robe), body 45/70 (armpit), 4 exposed.
    - 9 shots, viewed. Handoff 2026-10-24-character-10.md; review ysolde_review.md.
  - **Tavi and Kell:** LOD0 30,198 and 33,596. Opt-in params keep the seven M2 villagers byte-identical. The wick props are a new job, `props_wick`.
    - `verify` on the 9 villager jobs plus props_wick: identical.
    - Ratchets: the armpit only.
    - 9 shots, viewed. Handoff 2026-10-24-character-13.md.
    - Neither has a level slot yet (there is no Ch1 or Ch7 scene); the actor scenes are listed in the handoff.
  - **Gates on the merged head (075838e6):**
    - validate_data, taskboard, a manifest of 148 shots;
    - test_villagers, test_rig_integrity (7 characters), test_blender_builds, test_hero_clips, test_hero_battle_clips: OK;
    - post_import 19/19, hero_stage 9/9;
    - all five hero clip libraries regenerate byte-identical.
- **RE-PRIORITISED (the Lead, after the human's playtest): the M3 heroes are PAUSED** (Liss and Kerrid stop after their current commit; Ysolde and Sefir are already merged). Top of the queue:
  1. **M2-CHR-07, the battle clip set:** DONE and merge-ready (see its line above). Its clips are idle, ready, attack, cast, item, read, defend, finisher (= "special"), hit, dodge, ko and victory, for Asha, Rhen and Toma.
  2. **M2-CHR-12, field locomotion** (new): idle variants, walk and run with starts and stops, turns in place. Worktree sub-agent.
  3. **M2-CHR-11, host snaps** (new): rhen and toma are folded into M1-CHR-15, which is rebuilding them anyway; base_body and the seven villagers go to a worktree sub-agent.
  - The hero-integration track's live log is read each cycle. The branch didn't exist at 2026-10-24 ~20:00.
- **Un-pushed paused WIP (local worktree branches; not merged on purpose):**
  - **Kerrid, M3-CHR-05:** branch `worktree-agent-a163619bbd2d21786` @ e67e6aba. The build runs end to end, but the GLB is 5.30 MB (cap 5) and LOD1 is 35k (budget ~28k). His hero_clips block makes a no-argument `hero_clips.py` run fail until kerrid.glb exists, so he isn't merged. The next step is in the task's Notes.
  - **Liss, M3-CHR-03 hero half:** branch `worktree-agent-a61329e979970a83f` @ c5e3a320. LOD0 55,820, about 4.1 MB, with the 10 story clips and 11 battle clips. Not merged: two source edits (`TAIL_ROOT_H`, `SLEEVE_KEEP_NEAR_TORSO`) aren't built into the committed files yet, and the probe, Godot tests, shots and verify are still to run. The next step is in the task's Notes.
- **Kerrid and Pell design sheets merged** (kerrid.md, pell.md; M3-CHR-05 and 06).
  - Pell (M3-CHR-06) waits on **M3-NAR-01**: in outline, Pell's arc is close to the inspiring series' beast-folk guardian; the costume avoids every visual cue, but Narrative must rule on the arc. That task also carries the sheets' story questions and the stale ADR 0020 and glossary rows.
- **From the M3 sheets:**
  - Liss is a party member, so she is on the hero path; she stays in M3-CHR-03.
  - Mother Kell is Oruvel's chandler, not the diver. The story corrected this; glossary rows 195 and 254 are stale.
  - Ysolde's Swell input is Glyph Trace.
- **Blocker cleared (d523d43):** Toma's mouth/teeth/tongue are on `character_mouth`; the integration branch is merged;
  `--filter=character_shading` 17/17, hero_stage 6/6, post_import 19/19; `verify --job toma` 38 identical. Ready to merge.
  (send_message to the Lead was refused: "needs a trusted device", so this log is the channel.)
- **To the Lead: the asha reproducibility gate (your two messages; send_message back to you is refused for "needs a trusted device").**
  - **Threads aren't the cause.** `default_threads` is 4 in blender_builds.json, and verify applies it to every job without its own pin. This container is 4 vCPU, and my asha verify was 44 identical at ddc5eb2, 47b36c5 and again now.
  - **The cause is the host CPU's SIMD level**, which numpy dispatches at runtime. I reproduced it here with `NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4"`:
    - (a) the face solve leaves midline coordinates at 0 or ~1e-16;
    - (b) float32 rounding of tiny morph deltas flips;
    - (c) `asha_textures.write` rounds a few float texels that sit exactly on an 8-bit .5 boundary either way: 6 head-normal texels.
  - **Fixed in the commit after this note:**
    - Asha's head coordinates below 1e-9 snap to 0 (`MIDLINE_SNAP`).
    - Shape-key deltas go on a 1 µm grid (`snap_shape_noise`).
    - Asha's texture run pre-rounds to 6 decimals before the 8-bit rounding (`PRE_ROUND`).
  - **Result:**
    - Asha's GLBs, LOD1 and all 20 textures are byte-identical between the AVX-512 and AVX2-only numpy paths.
    - `verify --job asha` is 44 identical.
    - The asha_* shots are unchanged (RMSE ≤ 0.0003; no re-approval needed).
  - **Other jobs:** rhen, toma and the villagers keep their bytes (they don't opt in to `PRE_ROUND` yet; see M1-CHR-15). They are identical on both our hosts.
  - **Still to confirm:** your report also showed a Head `TEXCOORD_0` diff, which I couldn't reproduce on this host. The midline snap removes the likeliest trigger. Please re-run your gate at my latest head. If it still differs, push your rebuilt asha outputs to a scratch branch and I'll diff the UVs.
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
  - Verify, with the host-determinism fix in the tree: asha 44, rhen 31, toma 38, and all seven villager jobs (34/30/30/30/30/30/30) identical.
  - Shots: the 37 rhen_/toma_/villager_ shots and the 18 asha_ shots all pass their baselines unchanged.
  - Full `tools/tests`: 580 OK (4 skipped).

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
