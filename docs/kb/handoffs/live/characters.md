# Live log: characters environment

**This environment owns this file** (CLAUDE.md §7a). Cloud session `session_01JqzzxgJU9Dmu7fRhmCG9aQ`, branch
`claude/characters` (cut from `claude/undertow-lead-handoff-423ixt` at 952ef7c). The Lead reads it hourly.

## STATE AT HANDOVER (2026-10-25)

Branch `claude/characters` (this environment; cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ). Everything below is pushed. Unmerged sub-agent work is saved as **source-only patches** in `docs/kb/handoffs/wip/`. Apply one with `git apply`, then rebuild the outputs with the build.sh named below; binaries are reproducible and left out of the patches.

### Done and merge-ready on claude/characters (merge in this order; each was gated as noted above)
1. **M1-CHR-14:** Asha's braid seated, clipping fixes, rig guards and host determinism. Already on the integration branch via big7.
2. **M2-CHR-03:** the Haluna villagers.
3. **M2-CHR-07:** hero battle clips (Asha, Rhen, Toma; 12 contract clips with `contact` markers). Battle-presentation consumes the markers.
4. **M3-CHR-02 Sefir** and **M3-CHR-01 Ysolde:** hero builds (review: rendering). Design sheets for Liss, Tavi, Kell (act1_npcs.md), Kerrid (kerrid.md) and Pell (pell.md).
5. **M3-CHR-03 villager half:** Tavi Orse and Mother Kell, plus the `props_wick` job.
6. **M2-CHR-12:** field locomotion. Hero-integration has wired it in (M2-HER-1107).
7. **M2-CHR-11, base_body and villager half:** identical on three numpy paths (@ 5ed6193d).
- **HANDOVER DONE @ 54f1376e** (plus this note's own commit).

### In progress (exact next steps)
- **M1-CHR-15, skirt panels, shoulder correctives, spear turn, and Rhen/Toma host snaps:** COMPLETE on its branch and gated there, but NOT merged.
  - Merging conflicts with M2-CHR-12 in `hero_clips.py` (both add blocks; keep both). The three clip `.tres` files and the asha_clip_walk/run and toma_clip_walk baselines also conflict; regenerate and re-approve them.
  - Patch: `wip/M1-CHR-15.patch`, base becc8ca3.
  - Steps: apply it, or merge branch `worktree-agent-a564dfb7f69dc1687` @ 9821853a if it still exists. Resolve hero_clips by keeping both blocks. Run `assets_src/characters/{asha,rhen,toma}/build.sh`, then `python3 assets_src/characters/asha/hero_clips.py --hero <h>` for every hero. Re-capture the asha_*, rhen_* and toma_* shots and view them. Then run `verify_blender_builds.py --job asha --job rhen --job toma`, natively and with `NPY_DISABLE_CPU_FEATURES="X86_V4"` and `"X86_V3 X86_V4"`, and the rig probe.
  - That also completes M2-CHR-11 (rhen and toma).
  - Its judgement call: in deep poses (offer_hand, kneel, extreme_pose) Asha's skirts now read as a stiff bell; the rendering reviewer should confirm.
  - Request task M2-ENV-14: the Haluna kneel needs the helper-bone call.
- **M2-CHR-513, battle clip fixes for hero-integration:** a livelier victory, a lying-down ko, a ~0.8 s revive, Rhen's run arm lowered, and Rhen's hooks in hand (not started; needs a hook bone).
  - Patch: `wip/M2-CHR-513.patch`, base ceed1ff9. WIP, unverified, stopped by the usage limit.
  - Next: apply it on top of M1-CHR-15. Finish the poses, then run the rig probe (Toma's Body count is near its ratchet), test_hero_battle_clips, and the shots `<hero>_battle_ko` and `_victory`.
- **M3-CHR-05 (the Lead's big8 id: the 32 Asha/Toma clips for the Ch4–Ch9 greybox):** not started. Fold it into the clip work.
- **Paused M3 heroes** (the Lead paused them after the playtest; resume only after the items above):
  - Liss: `wip/M3-CHR-03-liss.patch`, base 075838e6. Next steps are in M3-CHR-03's Notes.
  - Kerrid: `wip/M3-CHR-505-kerrid.patch`, base 358e4794. The GLB is 5.3 MB (cap 5) and LOD1 is 35k; rename the task file M3-CHR-05 → 505 when applying. Next steps are in M3-CHR-505's Notes.
  - Pell: M3-CHR-506 is blocked on **M3-NAR-01** (Narrative must rule on whether his arc echoes the inspiring series' beast-folk guardian).

### Open questions (none for the human)
- **Narrative:** M3-NAR-01 (Pell's arc echo; the Kerrid and Pell sheet questions; stale ADR 0020 and glossary rows); Ysolde's ring, streak and re-ink staging (ysolde.md §12).
- **Art Director:**
  - Sefir's chest-up close-ups are 8–9% gold (the crown), and Cinematics may frame him waist-up instead;
  - Sefir's blue swatch;
  - the proposed swatches in the sheets.
- **Rendering:** confirm the M1-CHR-15 skirt look.
- **Cinematics:** M3-CIN-01 (Sefir's slow blink, face poses).

### Known issues
- Asha's tube skirts can't drape in deep lunges under linear skinning; M1-CHR-15 improves this.
- Armpit ratchets on every hero.
- Ysolde's robe reads mauve-brown under warm light.
- Villager faces are adult donor faces (the child and Kell).
- The M2 villager baselines are already about 6e-3 off (threshold 8e-3); re-approve them in a render batch.

### Gotchas (read before any character build)
- **Host determinism:** numpy dispatches SIMD paths at runtime (AVX-512, AVX2, baseline), and the last bits change the Blender outputs.
  - Every build must snap: donor and part positions to a 1 µm grid; head midline; shape-key deltas on a 1 µm grid (`snap_shape_noise`); UVs on 2^-16 (`quantize_uvs`); `asha_textures.PRE_ROUND` before 8-bit rounding; hair and LOD1-decimate inputs on the grid.
  - Verify with `NPY_DISABLE_CPU_FEATURES="X86_V4"` (the i9-12900K's AVX2) and `"X86_V3 X86_V4"`, not just natively.
  - Pin `"threads": 4` per job.
- **Garments under linear skinning:** no floor-length tubes; armholes at least 11.5 cm below the shoulder joint; torso garments on the torso only; props offset from the grip; keep the shins under skirts.
- **hero_clips.py is shared:** add self-contained blocks. Every other hero's library must regenerate byte-identical.
- **Ids:** characters uses the 500–599 block, ADRs 0140–0149, and handoffs named `<date>-character-characters-<n>.md`.
- **send_message to the Lead's session** is refused ("trusted device"), so this file is the channel. The battle-presentation and hero-integration sessions do accept messages.

## Now (2026-10-28)
- **Act I inventory scope (M3-HER-1144, the Lead's split, 10-28 01:54).** Mine: the named story NPCs, in story order:
  - Ch1: sabe, scaleman, skipper_sadi.
  - Ch4: ferrymaster, purser.
  - Ch5: tender, elder, garo.
  - Ch6: clerk, stillguard_a, stillguard_b, stillguard_c.
  - Ch7: ione, poolkeeper.
  - Ch8/9: fenn, gatekeeper, hobb, ivo, marra.
  - Agents are on them: one on the villager pipeline (the NPCs), one on Moll's kit (the Stillguard).
  - neme, osu, reed and tavi already have models; their capsules are the level owners' swap (M3-CHR-519).
  - Kerrid's battle actor is mine and done; it now holds the cleaver (b815df60).
  - Liss's battle actor and the party capsules are integration-qa's; generic villagers are the creatures track's.
- **The Lead's big12 review:**
  - (1) "Asha's staff is gone from her static views" does not reproduce. In `gpu/gate-big12-shots`, asha_front,
    asha_q34 and asha_sleeve_s0 all show the staff (beside the open hand: the grip is M2-CHR-515, not in big12). Headless
    on the current head, DEF-staff stands upright at the hand with its foot on the floor, and the Staff mesh is visible.
  - (2) The stiff bell is real. Measured: the front panel's lower bone stands 40-70 degrees out through walk and run.
    The two-bone panel can't hang from the knee; tuning the gait and the leg clearances changed nothing. Fix in
    progress: M2-CHR-522, a third panel bone per panel (agent in `/home/user/skirt-wt`).
- **Pushed, MERGE-READY (see the NEW ACCOUNT section):** M2-CHR-515 grip + guards @ 1b5277f6 (with the big11+ merge and
  Rhen's lie_in_shallows); M2-CHR-520, the staff set down in the kneels, @ 70efe4f1. M2-CHR-11 done (pc-gpu).
- **Renders:** Liss approved (ee3bd33). 038d565 and 7f56d64 were viewed but not approved; the 1b5277f6 and 70efe4f1
  requests supersede them.
- **In flight (local worktrees, not pushed):**
  - Kerrid (M3-CHR-505), `/home/user/chr-wt`, branch `chr-kerrid-wip`:
    - built: GLB 4.96 MB, LOD1 28.6k, textures, materials, 34 clips;
    - the yoke clears the jaw; probe ratchets pinned;
    - an agent is wiring the stage, shots, tests, verify job, import files and PROVENANCE.
  - Moll (M3-CHR-507): design sheet pushed (`docs/kb/art/characters/hadric_moll.md`). An agent is building him in
    `/home/user/moll-wt` (branch `chr-moll-wip`).
- **Next:**
  - Merge `chr-kerrid-wip`, then `chr-moll-wip`, into claude/characters; gate; MERGE-READY; render requests.
  - Liss and Rhen hair fringe (liss_review.md).
  - Toma's beard edge, once the toma_face render is back.
  - Pell stays blocked on M3-NAR-01.
- **Pell (M3-CHR-506), 2026-10-28, worktree `/home/user/pell-wt`, branch `chr-pell-wip` (local, not pushed):** built
  and in `review` (reviewer rendering), the sheet's §12 questions carried with their defaults (M3-NAR-1000 still todo).
  LOD0 47.0k / 4.09 MB, LOD1 27.3k / 1.33 MB; 21 clips (story + contract + revive), other libraries byte-identical;
  battle actor, name-shell toggle, 14 shots self-rendered and viewed (no baselines); rig probe passes with pinned
  allowances; job `pell` verified natively and on the two numpy paths (see the task notes). Not final art: the face reads
  as a muzzled human and the fur as a carving at full figure (`docs/kb/art/characters/pell_review.md`). Next: merge it,
  render the 14 `pell_*` shots, Rendering decides the face/fur pass. Handoff `2026-10-28-character-pell-1.md`.
  **Look-dev pass done (same branch, 4 commits after the coordinator's review):** an otter-like head (the warp now
  reshapes the donor head onto a Kirru head surface; no ADR needed), short soft fur with standing outline fur, the split
  reed girdle (§12 Q3's default overridden: it read as nudity), the crest skinned (it floated), stronger face shapes,
  storm_call's palm on the throat. Verified on three numpy paths, rig probe and tests green. Left: the almond lids,
  human ears, uniform fur at full figure (pell_review.md).

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

## NEW ACCOUNT (from 2026-10-25)
- Integration branch merged in (e86d7080).
- MERGE-READY @ dc93a5de: M1-CHR-15 (skirt panels with the stiff bell fixed by floor and overhang gathers, shoulder correctives, spear turn, Rhen/Toma host snaps; also M2-CHR-11's rhen and toma half). Checks run: verify asha 44 / rhen 31 / toma 38 identical on native, X86_V4-off and X86_V3+V4-off numpy paths; test_hero_clips (all libraries rebuild byte-identical), test_hero_battle_clips, test_hero_locomotion, test_asha, test_toma, test_rig_integrity 71 OK; Godot hero_stage 10/10, post_import 21/21, character_shading 17/17; gdlint/gdformat, validate_data, taskboard. Shots viewed on the cloud before the render move, but NOT approved: re-approval waits on the PC render below. Checks skipped: none that can catch this diff. Known red, not mine: test_hero_clips TestSefirClips (ch06_barge.dlg calls `@anim sefir bow_from_barge`, new on the integration branch); I take it in M3-CHR-05.

- MERGE-READY @ 038d5651 (+ a20267b1 render request): M2-CHR-513 (livelier victory, lying-down ko, 0.8 s revive, Rhen's sprinter run arm, Rhen's reef-hooks on DEF-hook bones keyed into his fists for attack and finisher). Checks run: verify rhen + the 9 villager jobs identical on native, X86_V4-off and X86_V3+V4-off (the villagers needed game/data/characters in verify's sandbox: hero_clips reads helper_bones.json since M1-CHR-15; fixed in blender_builds.json); test_hero_battle_clips (+ TestRhenHooks), test_hero_clips, test_hero_locomotion, test_rig_integrity 71 OK; every-frame probe on Rhen (hooks 0 mm in body); probe asha/rhen/toma clean, no ratchet raised; Godot hero_stage 10/10, post_import 21/21, character_shading 17/17; blender manifest tests 28 OK. Shots requested (7 new). Skipped: none that can catch this diff. For battle-presentation and hero-integration: `revive` now exists for Asha/Rhen/Toma; `ko` lies down and holds; Rhen's hooks are in the clip itself.
- MERGE-READY @ (this commit): M2-CHR-11 (host determinism): all 43 character-owned Blender jobs (asha, rhen, toma, 9 villagers, base_body, props_wick, sefir, ysolde, 27 creatures) identical natively, with NPY_DISABLE_CPU_FEATURES="X86_V4" (AVX2) and "X86_V3 X86_V4" (baseline). Also fixes verify's sandbox for the villager jobs (they import hero_clips, which reads game/data/characters/helper_bones.json). Jobs for the PC to re-verify on hardware: `--all`, or at least asha rhen toma villager_neme villager_osu villager_child villager_vendor villager_reed villager_netmender villager_fisher villager_tavi villager_kell base_body props_wick sefir ysolde. Checks skipped: none.
- MERGE-READY @ 7f56d643: M3-CHR-05 (every `@anim` call in the dialogue now has a clip: Asha 20, Toma 12, Rhen 46, Ysolde 9, Sefir 1 incl. `bow_from_barge`, which fixes the integration branch's red TestSefirClips) and M2-CHR-514 (field life: idle_look_around, idle_fidget, talk_explain, talk_emphatic, listen_nod, look_left/right/up/down for Asha, Rhen, Toma, Ysolde). Built from data, `assets_src/characters/requested_clips.json` (act1-chapters can add clips there). Checks run: test_hero_clips (every chapter's calls exist; libraries byte-identical; cap now 3 MB), test_hero_battle_clips, test_hero_locomotion, test_rig_integrity 71 OK, test_asha/toma/sefir/ysolde OK; rig probe clean at the existing ratchets (13 overruns found and fixed in the poses, none raised); Godot hero_stage 10/10, post_import 21/21, cutscene 37/37. No Blender source touched (verify not needed). For hero-integration: see M2-CHR-514's Notes (the look poses are neck-only for a look-at blend).
- Integration branch (big10) merged @ ecb657b8: M3-CHR-1000's requested_clips.json pending list combined with my specs; the 8 new Ch8-Ch9 calls for Asha and Toma built (pending now only Kerrid 8, Liss 11). Re-approved 27 asha_*/toma_* shots from the PC render gpu/render-characters-dc93a5d @ 265bbcf0. Checks: test_hero_clips/battle/locomotion/rig_integrity/sefir/ysolde/asha/toma/blender_builds OK; Godot hero_stage 10, post_import 21, cutscene 51, character_shading 17 OK. Pell (M3-CHR-506) still blocked on M3-NAR-01 (pell-arc-echo request task, todo). Next: Liss (M3-CHR-03 hero half), then Kerrid.
- MERGE-READY @ ee3bd335: M3-CHR-03 Liss hero half (review: rendering after the PC render). GLB 4.19 MB, LOD1 26k. Checks: verify --job liss identical on native / X86_V4-off / X86_V3+V4-off; test_liss, test_hero_clips, test_hero_battle_clips (Liss in HEROES), test_hero_locomotion, test_rig_integrity (TestRigIntegrityLiss) OK; Godot hero_stage 10, post_import 21 (liss .glb.import files carry the characters script), character_shading 17, cutscene 51 OK; validate_data, taskboard, gdlint. Ratchets pinned with reasons. PC confirmed M2-CHR-11 on AVX2 hardware (12/12). Filed M2-CHR-515 from M1-QA-09: props not gripped (next item).
- MERGE-READY @ 1b5277f6 (FAST-TRACK, M1-QA-09): M2-CHR-515, the grip, plus the integration merge (big11+) and Rhen's new lie_in_shallows (M2-FP-103). Asha's staff and Toma's spear are built through the fist, ride their own bones (DEF-staff, DEF-spear) under the right hand, and are held by an exact hold with the fingers closed round them. They slide to rest on the floor, and pivot in the fist clear of the skirt and legs (prop_pivot). **New rig-probe guards, as asked:** `prop grip` (the shaft stays through the fist) and `prop through_garment` (no line along the shaft crosses a garment), with tests. Walk, run and the stands are clean for Asha, and every clip is clean for Toma. **Not fixed, and tracked:** Asha's kneel, sit and bow clips (including kneel_over_rhen, laugh and offer_hand) still cross the pooled skirt. They are documented allowances for M2-CHR-520 (set the staff down); M2-CHR-515's ⚠3 is unticked. Checks run (on the merged tree): verify asha and toma identical on native, X86_V4-off and X86_V3+V4-off (before the clip-only changes; clips aren't job outputs); test_hero_clips, test_hero_battle_clips, test_hero_locomotion, test_rig_integrity (new prop tests), test_asha, test_toma, test_blender_builds OK; Godot hero_stage 10, post_import 21, character_shading 17, cutscene 67 OK; gdlint, gdformat, validate_data, taskboard OK. Skipped: none that can catch this diff. Also: M2-CHR-11 is done (pc-gpu review logged). Filed M3-CHR-507 (Inquisitor Hadric Moll), 508 to 512 and 516 to 518 (the Act I people still capsules), and 519 (a request to swap capsules whose characters already exist).

- MERGE-READY @ 70efe4f1 (FAST-TRACK, M1-QA-09 ⚠2/⚠3): M2-CHR-520. Asha sets the staff down on the floor beside her where she kneels, sits or crouches (kneel_over_rhen, laugh, offer_hand, rise_to_stand, sit, sit_beside, bow_palms_flat, kneel_hum, kneel_touch_ring, feed_fire, float_boat), and takes it up again when she rises. Held, it crossed her pooled skirt; the guard proved neither pivot clears that. The rig-probe allowance list is now only pole_in, pole_out and one attack sleeve line. Checks: test_hero_clips, test_hero_battle_clips, test_hero_locomotion, test_rig_integrity, test_asha, test_toma OK; Godot hero_stage 10, post_import 21, cutscene 67 OK; validate_data, taskboard OK. Verify not needed: clips only, no Blender source changed.

- MERGE-READY @ (this commit): M2-CHR-521, Liss's and Rhen's fringe ends stagger (the helmet edge in liss_review.md). Checks: verify --job liss and --job rhen identical natively, X86_V4-off and X86_V3+V4-off; test_liss, test_hero_clips, test_hero_battle_clips, TestRigIntegrityLiss and TestRigIntegrityRhen OK. Merged with the integration head (big12+), which is clean. Its shots are in the one open render request.

- MERGE-READY @ (this commit): M3-CHR-505 Kerrid, for M3-HER-100's prologue vigils too.
  - Budgets: kerrid.glb 4.96 MB (no LFS needed), LOD1 28.6k and 1.48 MB, LOD0 58k.
  - The yoke clears the jaw (48 mm below the chin); the chest rope sits 141 mm under the shoulder. Textures and materials are in; 34 clips cover every dialogue call; the battle clips pass the contract.
  - kerrid_battle.tscn: the back cleaver is hidden and the hand cleaver is on DEF-hand.R.
  - Checks: verify --job kerrid identical on all three numpy paths. On the merged tree, test_kerrid, test_hero_clips, test_hero_battle_clips, test_hero_locomotion, test_rig_integrity (Kerrid ratchets documented), test_asha, test_toma, test_liss and test_blender_builds pass. Godot hero_stage 10, post_import 21, character_shading 17 and cutscene 67 OK; gdlint, gdformat, validate_data and taskboard OK. Every other hero's library is byte-identical after the merge.
  - Known: his battle idle has the hands at his sides (the sheet wants both hands on the haft). This needs a battle idle pass after the render.

- MERGE-READY @ 9053b9cf: M2-CHR-522 and M3-CHR-507.
  - **M2-CHR-522**, Asha's skirt hangs from the knee. A third panel bone, DEF-skirt_<k>.002, runs below the knee. The front panel's lowest bone stays within 2 degrees of vertical in walk and run; the old lower bone stood up to 69 degrees out. The stage port (hero_helper_bones.gd) matches.
  - **M3-CHR-507**, Inquisitor Hadric Moll: LOD0 54.4k, moll.glb 4.15 MB, 16 clips. ko is his yield, held kneeling. The brine-iron is gripped. Battle actor at game/characters/foes/moll_battle.tscn. M3-CHR-523 asks Combat to point stillguard_inquisitor at it.
  - Checks: verify --job asha and --job moll identical on all three numpy paths (and --job toma for the builder hooks). On the merged tree: test_hero_clips, test_hero_battle_clips, test_hero_locomotion, test_kerrid, test_moll, test_asha, test_toma, test_liss, test_blender_builds and test_rig_integrity OK; Godot hero_stage 10, post_import 21, character_shading 17 and cutscene 67 OK; gdlint, gdformat, validate_data and taskboard OK.
  - Self-render of the affected shots is running; a SELF-RENDERED line follows.
- **ADR 0041 refocus (Act I final):** in order, (1) Moll's battle actor (done; the enemies.json pointer is Combat's, M3-CHR-523), (2) the skirt (done) and the staff in every view (self-render checks it), (3) the Act I NPC capsules (agents building them now: villager-path townsfolk, clerk, Reeds and wrights; Stillguard on Moll's kit), (4) party outfits and faces at dialogue range (next). Paused: Kerrid's later-act looks.

- MERGE-READY @ (this commit): M3-CHR-505, Kerrid's battle stance (b815df60 + the PROVENANCE row). His battle actor plays anim/kerrid_battle_clips.tres: the idle holds the cleaver low with both hands on the haft. The field library is unchanged. rig_probe also samples the battle library. Checks: test_hero_clips, test_hero_battle_clips, test_kerrid and test_rig_integrity (all heroes) OK; Godot hero_stage 10 and post_import 21 OK; validate_data OK. Self-rendered kerrid_battle_idle (reads right) and kerrid_battle_attack (reads as a thrust: M3-CHR-525).

- MERGE-READY @ (this commit) **FAST-TRACK** (the human's playtest: Asha's run "flops"): a grounded run for Asha, Toma and Rhen, who share the run base (`_RUN` in hero_clips.py). The free arm stays bent near the body and folds more as it comes forward (no straight-arm reach). It barely moves out from the side (abduction 12° to 6–7°) and lags less. The hip and chest counter-turn is smaller (7°/7° to 4.5°/4°), the swing-foot lift is lower (0.12 to 0.09 m, bump 10° to 6°) and the staff and spear follow is steadier (5° to 2.5°). Rhen keeps his sprinter arm, a little smaller (36° to 30°, lift 0.14 to 0.12 m). Foot plants unchanged in kind (test_hero_locomotion green). Checks: test_hero_locomotion 8, test_hero_clips 19, test_rig_integrity 184 OK (44 skipped); Godot `--filter=hero` 98 run, 0 failed. Verify not needed: clips only, no Blender source changed.

- MERGE-READY @ 68ca13c9: M3-CHR-508, the Stillguard soldiers (stillguard_a, _b, _c on Moll's kit, worn and unmarked, with field and battle clips), plus M3-CHR-590 filed for their dialogue clips. The level owners swap the capsules (M3-CHR-519). Checks on the merged tree: validate_data, taskboard, gdlint, gdformat; test_hero_clips, test_hero_battle_clips, test_stillguard, test_moll, test_kerrid, test_blender_builds and test_rig_integrity OK (44 skipped); Godot hero_stage 10 and post_import 21 OK. The clip regen left the tree unchanged.

- MERGE-READY @ 9ea8d3d7: the named Act I NPCs, M3-CHR-526..539 (sabe, scaleman, skipper_sadi, ferrymaster, purser, elder, garo, tender, ione, poolkeeper, fenn, gatekeeper, hobb, marra), plus the generic villagers built before the re-split (shopkeeper 512, smith 516, innkeeper 517, the clerk 509, four Reed polers 510, the Saltwright girl and two children 511). All are on the villager pipeline: 27–36k triangles, LOD1 13.6–17k, under 2.2 MB, and every job is byte-identical on native, X86_V4-off and X86_V3+V4-off. It also fixes build_villager.clear_teeth_strip (the teeth texture showed on seven heads' temples). Not built: Ivo, who is in Stillguard armour (M3-CHR-540, mine next), and the ferryman and mate (another track's). The level owners' swaps are listed by actor path in M3-CHR-519. M3-CHR-518 is blocked: the Prologue vigil is the seven party members, not strangers. Checks on the merged tree: validate_data, taskboard, gdlint, gdformat; test_villagers, test_blender_builds, test_hero_clips, test_rig_integrity OK (the 169 skips are villagers with no braid or prop); Godot post_import 21 and villager 23 OK. 45 new shots, no baselines.
- MERGE-READY @ 95489b3d: M2-CHR-521, Liss's fringe (big13's review: blocky teeth at dialogue range). Every card ends on the atlas's fading tip and tapers to a point. The cards gather in clumps of five whose tips draw together, and the stagger is wider, so the ends fall at different depths over the brow. Checks: verify --job liss identical on all three numpy paths; test_liss, test_hero_clips and TestRigIntegrityLiss OK. Self-rendered liss_face and liss_face_stylized before and after: the orange square-ended cards are gone and the edge is broken. A darker band still follows the hairline (the painted scalp under the cards); that is the next look-dev step if the Lead still sees it.
- Done: Asha's stand_at_pool (efe1447d, big13's request for the First Verse S08), rendered and viewed.

- MERGE-READY @ (this commit): M2-CHR-522 follow-up, big13's review that Asha's skirt was still a stiff white bell in asha_clip_bow_palms_flat. Pooling cloth now drapes onto the floor: where a lowest panel bone would gather shorter than drape_below_gather (0.75), it first swings out, by the least swing up to drape_max_deg (70), that lays its full cloth on the floor, and gathers only the rest. Both are new keys in helper_bones.json, and the change is in both hero_clips.skirt_solve and HeroHelperBones. Walk and run are unchanged: their gathers are all at or above 0.92. Only asha_clips.tres changed. Checks: validate_data, gdlint, gdformat; test_hero_clips, test_hero_locomotion, test_asha and TestRigIntegrityAsha OK; Godot hero_stage 10 (the stage solve matches the baked clips), post_import 21 and cutscene 77 OK. Self-rendered bow_palms_flat and kneel_over_rhen before and after. In the kneel the white underskirt now spreads on the floor beside her. In the bow the vertical white wall is lower and slopes out. **Partial:** the overskirt is still a smooth panelled bell with no folds. Folds need more panel bones or a cloth pass, which I propose as the next skirt step if the Lead still reads it as stiff.

- MERGE-READY @ (this commit): big14's test_hero_clips failures (gpu/gate-big14-shots merged here). big14 took claude/characters at 441bebe3, before efe1447d built stand_at_pool and struck it from the pending list, and before the later clip regens. With big14 merged on this head, test_hero_clips runs 19 OK: asha's library rebuilds byte for byte and the pending list is empty. validate_data OK. Merge this head, not 441bebe3; it also carries the NPCs, Liss's fringe and the skirt drape (their MERGE-READY lines above).

- MERGE-READY @ (this commit): M2-CHR-524, short hair and beards at dialogue range (Toma, Kerrid, Moll and the netmender; cause and changes in the task file), with the six Stillguard soldiers rebuilt on the same hair code, and M3-CHR-540, Ivo Brannick: a named Stillguard with his face uncovered, the shield on his left arm and no spear, plus hug_lift and kneel_palms_flat. His output is assets/characters/ivo/ (the speaker id); the level owners' swap notes are in M3-CHR-519. Checks: toma, kerrid, moll, villager_netmender, stillguard and ivo identical on native, X86_V4-off and X86_V3+V4-off (moll re-verified after Ivo's spear opt-out); test_short_hair_dialogue, test_toma, test_kerrid, test_moll, test_stillguard, test_villagers, test_hero_clips, test_blender_builds, TestRigIntegrityIvo OK; Godot post_import 21 OK. Self-rendered toma_face_neutral, kerrid_face, moll_face, ivo_face and ivo_front: the beards read short and dense, the crops fine, with no notch round Kerrid's mouth. Left: faint mottling on Toma's crown up close; Kerrid's grey is quiet (Art's call); Moll's fringe ends in a straight line; toma_lod1 is 1.55 MB (pipeline.md §14 says under 1.5, not enforced). In Ivo's test stages the shield stays on his arm, so it juts out in the hug (the scene drops it first). The helmeted soldiers' scalp keeps its old paint (Moll's scalp shade is Moll-only). Also filed M3-CHR-541: validate_creatures only accepts game/creatures/ models, so the Inquisitor's pointer to moll_battle.tscn waits on the creatures track.

- Asha's skirt as cloth (the Lead's queue): **not merge-ready, needs a decision.** A 16-panel prototype (fluting pooled hems) makes the kneels' hem fold visibly, but asha_clips.tres grows to 4.94 MB (over test_hero_clips' 4 MB text bound), the staff's skirt-clearing pivot regresses in pole_out and walk, and turn_in_place is 2 mm worse. Filed as M2-CHR-542 with the patch (docs/kb/art/characters/asha_skirt16.patch) and three options for the size: (a) binary .res libraries, (b) no baked skirt tracks (runtime HeroHelperBones everywhere), (c) sparser skirt keys. **Lead: which?** Until then the merged 8-panel floor drape (8e7d5f67) stands.

- MERGE-READY @ (this commit): M2-CHR-542, Asha's skirt as cloth, per the Lead's decision. It was option (b), but measured: HeroHelperBones.drive costs about 107 ms per hero in GDScript (the budget is 0.2), and the (c) fallback, sparser keys, was still 4.62 MB. So it is ADR 0140:
  - 16 panels. The 8 odd panels lie over the legs; they are solved and baked as before.
  - The 8 even panels are derived each frame by HeroSkirtFolds, a SkeletonModifier3D that the characters import adds to every Asha GLB. A derived panel takes the larger of its neighbours' swings, their mean at the hem and in gathers, and a 6° fold where the hem drapes out. It costs 0.037 ms per hero.
  - asha_clips.tres is 3.82 MB.
  - The staff pivot is fixed: it keeps 50 mm from the cloth and stays clear of the head. Neither pole_out nor walk regresses.
  - Self-rendered and viewed: in kneel_over_rhen, bow_palms_flat and float_boat the pooled hem rolls in soft folds (the first try made spikes and was toned down). walk_cycle and run read as before.
  - Checks: test_asha, test_hero_clips, test_hero_locomotion, test_hero_battle_clips, test_blender_builds, TestRigIntegrityAsha OK (Body count ratchet 24 -> 25, reasoned); Godot hero_stage 11 (including the new test_skirt_folds_are_derived_at_runtime: the modifier is there, no clip bakes a derived panel, under budget), post_import 21, character_shading 17; cutscene 84/1, the known failure in test_act1_cutscene_walks (Toma's dock_shore, a level's floor, in big14's gate too); asha identical on all three numpy paths.
  - Note for gates: Asha's GLB changed, so stale import caches re-import it and pick up the modifier.

- MERGE-READY @ 6ee094df: the Act I NPCs polished at dialogue range, in the Lead's story order (M3-CHR-526..539 plus tavi, neme, osu and reed):
  - Grey hair is fine strands, not white chips.
  - Stubble has a soft shadow.
  - Head wraps and headbands sit on the skin, with no dark band and no floating.
  - Hobb's cord has its three knots, Marra has her netting shawl and wrist cord, Garo his forearm burns, and the pool-keeper chalky fingertips.
  - Eight committed head textures that predated M2-CHR-524 were rebuilt, so every villager job verifies again.
  - All are optional data keys: the other villagers are byte-identical. All 34 villager jobs are identical natively, and every changed one on all three numpy paths.
  - Checks on the merged tree: validate_data, taskboard, test_villagers (with TestDialoguePolish), test_blender_builds, test_hero_clips and test_rig_integrity OK (173 skips: no braid or prop); Godot post_import 21. `--filter=villager`: 3 failures in test_villager_routines, the same ones big14's gate lists (not models).
  - Self-rendered and viewed (marra, tavi, osu, garo before and after): they read right.
  - **Left:** Sabe's and Ione's sleeveless tops still cut like a halter (a cap sleeve and broader straps both broke the rig limits, so they need a garment-fit pass). The cropped hair ends bluntly at the forehead (the shared painted scalp). The old villagers' brows are a flat smear up close.
- Act I GPU QA row 31 (big15: Asha's skirt over Rhen on the beach) is staging, not the skirt. She kneels with her knees at his chest; the kneeling skirt reaches 0.67 m forward and 0.85 m to each side. Filed M3-CHR-543 to cinematics / m2-slice: kneel her beside him. The skirt itself is also reworked since big14 (8e7d5f67 drape, 67a1b2a0 folds).

- MERGE-READY @ (this commit): M2-CHR-544, real closed-hand grips (the PC's M1-QA-09 on big15: open hands on the staff and spear).
  - **Cause:** the GLBs build the shaft through the open rest hand's fingers (joints 6–36 mm from a 19.6 mm shaft's axis), so no curl could wrap it.
  - **Fix:** the fingers first close to a fist, and the prop's bone moves in the hand's frame so its shaft runs through the fist's hole (Asha 13 mm, Toma 24 mm). Each finger joint is then solved on its own, kept level with its knuckle, and the thumb's search is wider. The offset is in every clip's prop keys, in grips.json for the stages, and in rig_probe.
  - **Who:** Asha, Toma, Moll and the six Stillguard soldiers; Rhen's hooks get the per-joint solve.
  - **Checks:** test_hero_clips, test_hero_battle_clips, test_hero_locomotion, test_asha, test_toma, test_moll, test_stillguard, test_villagers OK; rig probe Asha, Toma, Rhen, Moll and Stillguard A–F OK (grip offset under 2 mm on every posed frame); Godot hero_stage 11, post_import 21. Clips and data only, no Blender source changed.
  - **Seen:** self-rendered at 1920×1080 and viewed zoomed in: Toma's and Moll's hands are closed fists round the shaft. Asha's fingers wrap the staff, a looser grip on her small hand.
  - The staff in the kneels was already set down beside her (M2-CHR-520), so nothing crosses the skirt there.

- MERGE-READY @ (this commit): the NPC polish's leftovers.
  - **Sleeveless tops:** Sabe's and Ione's tops are ordinary tank tops with straps over the shoulders, not halters (new `_costume.top.armhole_cut: "tank"`). Their rig limits went down, not up.
  - **Hairline:** the painted hairline under cropped hair is feathered into a broken edge for Sabe, Ione and Hobb (opt-in `HAIRLINE_FEATHER`; the heroes are byte-identical, asha verified).
  - **Brows:** the old villagers' brows (Fenn, Marra, Osu, and Sabe) are wiry painted strands under lighter cards, not a flat smear.
  - **Checks:** the six changed jobs identical on all three numpy paths; a native verify of the other 28 villager jobs and 10 hero jobs, 38/38 identical; test_villagers 45 (with TestDialoguePolish2), test_blender_builds, test_hero_clips, test_asha, and rig probes Sabe, Ione, Hobb, Fenn and Marra OK; validate_data and taskboard OK.
  - **Seen:** self-rendered and viewed before and after.
  - **Left:** Ione's top stands out under the arms like short cap sleeves (it did before); a faint edge where each strap lies over the panel; Ione's fringe shows the card tips as short dark dashes.
  - **Shots to re-approve:** these six NPCs' face and front shots.

- MERGE-READY @ 787211f1: **Pell (M3-CHR-506)**, the Kirru hero. ui-menus can bake his portrait from pell_face.
  - **Head:** the MPFB2 donor head warped onto an otter-like head (broad low skull, short muzzle, nose pad, whisker pads, thick neck). It reads as otter or weasel in profile and three-quarter. All 40 face shapes, no ADR needed.
  - **Build:** short soft fur with 4,200 outline fur cards; the reed mantle, name-shell (blank and carved), the staff in a closed left fist; pell.md §4.2's reed girdle (the §12 Q3 default overridden on review: it read as nudity).
  - **Clips and actor:** 21 clips (9 story, the 12-clip battle contract, revive) and pell_battle.tscn. LOD0 52.3k, 4.72 MB; LOD1 27.2k, 1.31 MB.
  - **Checks:** verify --job pell 37/37 identical on all three numpy paths; test_pell 20, test_hero_clips, test_hero_battle_clips, test_blender_builds and TestRigIntegrityPell OK (ratchets reasoned in rig_checks.json: ko squat, arm across the chest); Godot post_import 21, hero_stage 11, pell 3; validate_data, taskboard, gdlint and gdformat OK.
  - **Seen:** self-rendered all 14 pell_* shots and viewed them.
  - **Not yet Kerrid's bar** (a second look-dev pass is running): the eyes are human almond lids with whites, the ears small human ears, the face's fur smooth up close, the body thin and smooth between the fur cards; the right hand is open in storm_call.
  - **Requests:** M3-BPR-1340 (battle framing for his height), M3-CIN-1240 (crest values with face tags). Narrative's pell.md §12 questions are carried with their defaults.

### Render requests
RENDERED+APPROVED (gpu/render-characters-dc93a5d) RENDER-REQUEST @ dc93a5de: asha_front,asha_q34,asha_profile,asha_face_neutral,asha_face_smile,asha_face_grief,asha_sleeve_s0,asha_sleeve_s4,asha_extreme_pose,asha_face_stylized_compare,asha_clip_kneel_over_rhen,asha_clip_walk,asha_clip_offer_hand,asha_clip_face_west,asha_clip_laugh,asha_clip_run,asha_smile_variant_compare,asha_battle_idle,rhen_battle_idle,toma_battle_idle,rhen_front,rhen_q34,rhen_profile,rhen_back,rhen_face_neutral,rhen_face_smile,toma_front,toma_q34,toma_profile,toma_back,toma_face_neutral,toma_face_smile,rhen_clip_take_hand,rhen_clip_kneel,toma_clip_walk,toma_clip_talk,asha_battle_attack,rhen_battle_attack,toma_battle_attack,asha_clip_walk_cycle,asha_clip_turn,rhen_clip_walk_cycle,rhen_clip_turn,toma_clip_walk_cycle,toma_clip_turn; why: M1-CHR-15 rebuilt Asha, Rhen and Toma (skirt gathers, shoulder correctives, spear) on top of M2-CHR-12's clips
SUPERSEDED (by the request @ f5f509ac) RENDER-REQUEST @ 038d5651: rhen_battle_idle,rhen_front,rhen_q34,rhen_profile,rhen_back,rhen_face_neutral,rhen_face_smile,rhen_clip_take_hand,rhen_clip_kneel,rhen_battle_attack,rhen_clip_walk_cycle,rhen_clip_turn,rhen_battle_ko,rhen_battle_victory,rhen_battle_finisher,asha_battle_ko,asha_battle_victory,toma_battle_ko,toma_battle_victory; why: M2-CHR-513 (new ko/victory/revive clips, Rhen rebuilt with hook bones and his hooks in hand in attack and finisher; 7 new shots)
SUPERSEDED (by the request @ f5f509ac) RENDER-REQUEST @ 7f56d643: asha_clip_bow_palms_flat,rhen_clip_lift_housing,toma_clip_stack_bowls,ysolde_clip_read_letter,rhen_clip_talk_explain; why: M3-CHR-05 story clips and M2-CHR-514 field-life samples (new shots, never rendered)
RENDERED+APPROVED (lead/gate-render-characters-ee3bd33) RENDER-REQUEST @ ee3bd335: liss_front,liss_back,liss_three_quarter,liss_face,liss_face_stylized,liss_silhouette_vs_rhen,liss_clip_haul_rope,toma_clip_walk_cycle; why: M3-CHR-03 Liss built (7 new shots, no baselines); toma_clip_walk_cycle only as a control
SUPERSEDED (by the request @ f5f509ac) RENDER-REQUEST @ 1b5277f6: asha_front,asha_q34,asha_profile,asha_face_neutral,asha_face_smile,asha_face_grief,asha_sleeve_s0,asha_sleeve_s4,asha_extreme_pose,asha_face_stylized_compare,asha_clip_kneel_over_rhen,asha_clip_walk,asha_clip_offer_hand,asha_clip_face_west,asha_clip_laugh,asha_clip_run,asha_smile_variant_compare,asha_battle_idle,rhen_battle_idle,toma_battle_idle,rhen_front,rhen_q34,rhen_profile,rhen_back,rhen_face_neutral,rhen_face_smile,toma_front,toma_q34,toma_profile,toma_back,toma_face_neutral,toma_face_smile,rhen_clip_take_hand,rhen_clip_kneel,toma_clip_walk,toma_clip_talk,asha_battle_attack,rhen_battle_attack,toma_battle_attack,asha_clip_walk_cycle,asha_clip_turn,rhen_clip_walk_cycle,rhen_clip_turn,toma_clip_walk_cycle,toma_clip_turn,asha_battle_ko,asha_battle_victory,rhen_battle_ko,rhen_battle_victory,rhen_battle_finisher,toma_battle_ko,toma_battle_victory,asha_clip_bow_palms_flat,rhen_clip_lift_housing,toma_clip_stack_bowls,rhen_clip_talk_explain,ysolde_clip_read_letter; why: M2-CHR-515. The staff and spear are gripped, slide and pivot in the fist, which changes every Asha and Toma clip and Rhen's hook fingers. Rhen's lie_in_shallows is new. This supersedes the unapproved renders 038d565 and 7f56d64.
- Viewed 038d565 (M2-CHR-513) and 7f56d64 (story samples). The poses read right: the kneel drift is the arm change, Rhen's ko and victory are good, and his hooks are in hand in the finisher. Not approved, because they show the ungripped staff and spear (Asha's victory, her bow_palms_flat, Toma's stack_bowls) that M2-CHR-515 replaces. Approve from the render above.
SUPERSEDED (by the request @ f5f509ac) RENDER-REQUEST @ 70efe4f1: asha_clip_kneel_over_rhen,asha_clip_laugh,asha_clip_offer_hand,asha_clip_bow_palms_flat,asha_clip_walk,asha_clip_run,asha_battle_idle,asha_battle_ko; why: M2-CHR-520, the staff set down beside her in the kneels (view whether the lowering reads as deliberate). If the 1b5277f6 request hasn't run yet, run this one in its place for these ids.
RENDER-REQUEST @ f5f509ac: toma_battle_idle,toma_battle_attack,toma_battle_ko,toma_battle_victory,toma_clip_walk_cycle,toma_clip_stack_bowls,rhen_front,rhen_face_neutral,rhen_battle_ko,rhen_battle_victory,rhen_battle_finisher,rhen_clip_kneel,rhen_clip_take_hand,liss_face,liss_face_stylized; why: the shots changed since my last approvals. They cover M2-CHR-515 (Toma's spear gripped), M2-CHR-513 (Rhen's ko, victory and finisher, plus the kneel drift), and M2-CHR-521 (Liss's and Rhen's fringe ends stagger). 15 shots. Asha's shots wait for M2-CHR-522 (the skirt rework), so they render once, with the grip, the set-down and the new skirt together.
SELF-RENDERED @ 9053b9cf: asha_clip_run, asha_clip_walk_cycle, asha_clip_turn, asha_extreme_pose, asha_front, asha_clip_kneel_over_rhen, asha_clip_offer_hand, asha_clip_laugh, asha_battle_idle, kerrid_front, kerrid_face, kerrid_clip_collar_haul, moll_front, moll_face, moll_clip_yield. All drift or are new, as expected; no baselines written. What I saw: the staff is in her fist in every standing view, and laid on the floor beside her in the kneels. The skirt hangs below the knee in walk and run, with no flat disc. extreme_pose still has the flat raised-knee front (stress stage, M2-CHR-515 item 5). Kerrid and Moll read well at full figure. **At dialogue range the short-hair cards and the beards are blotchy** (Toma's too, the M1-QA-09 beard finding). Kerrid's beard has a hard notch round the mouth and white flecks in the hair. Look-dev task M2-CHR-524 is next.
SELF-RENDERED @ (this commit): a temporary strip, not committed: Asha's run at 4 phases from the side and the 3/4 front, her walk at 2 phases, and Toma's and Rhen's runs from the side at 2 phases (plus the same Asha run strip before the fix). What I saw: before, the free left arm went near-straight out to chest height on the forward swing and swung wide of the body from behind. After, the elbow stays bent near the body and the hand comes up to the chest, matching the walk's quiet arm. Toma's and Rhen's runs read compact and grounded. The staff still leans in the fist mid-stride (the M2-CHR-515 pivot clearing the skirt), as before. No baselines written; the walk shots are unaffected; asha_clip_run will drift.

## FROM 2026-10-29 (Lead session_01Bg3iP7cPGyjbX4CyniBahc; integration branch claude/new-session-mj8c3c)
- Merged `origin/claude/new-session-mj8c3c` into claude/characters (28ef466f; the only conflict was pc-gpu.md, taken
  from the integration branch: not this track's file).
- MERGE-READY @ 2c2acb54 (+ its docs commit): **Pell's second look-dev pass (M3-CHR-506)**, pell_review.md's five open
  items: rounder lid openings scaled inside the warp (blink and units follow), a dark eye ring and a dark lid margin;
  round flat ears; a flat right hand on the throat in storm_call and cast (hero_clips FLAT_HAND, Pell's library only);
  a stronger saddle pattern, body clumps and a soft-edged throat stripe; a thicker upper neck under the skull. GLB
  4.79 MB, LOD1 1.32 MB. Checks: verify --job pell 37/37 identical natively, X86_V4-off and X86_V3+V4-off; rig_probe
  pell OK; test_pell, test_hero_clips (every other library byte-identical), test_hero_battle_clips,
  test_hero_locomotion, test_blender_builds OK; Godot post_import 21, hero_stage 11, pell 3 OK; validate_data,
  taskboard OK. SELF-RENDERED all 14 pell_* shots and viewed them (before/after in pell_review.md). Left: smooth skin
  up close, a warm-orange face under the warm key, a small knob at the back of the skull in profile.
- MERGE-READY @ 5d52c33e: **the named Act I NPCs cast as themselves (M3-CHR-519; CONSOLIDATED: named-NPC capsules are
  characters')**. Every layout row for a built named NPC cast a generic villager (ferrymaster as fisher, Ione as
  vendor, the Stillguard as fisher/netmender...). Now 28 rows in 9 layouts name their own model; only the `cast` or
  `model` value changed. Actor wrappers for the Stillguard soldiers and Ivo under villagers/ (ZoneCast's path), with
  PROVENANCE rows. Checks: every named model has every clip its dialogue calls except the Stillguard's (M3-CHR-590,
  next) and `look_at` (the sequencer's turn); Godot zone_cast 3 and ch01_stage_models 1 OK; validate_data OK.
  For the Lead: act1-chapters and slice-polish own those layout files; this touches only the cast values, per the
  ownership line. The inventory's neme/osu/reed rows in haluna.tscn are VillagerLayer's at runtime
  (game/data/world/npc/zones/ch02_haluna.json puts the models in the capsules), so a static audit still sees the
  capsule; Pell's Ch9 capsules are the party's (integration-qa), with a swap note in M3-CHR-519.
- MERGE-READY @ c57fa703: **M3-CHR-590, the Stillguard dialogue clips** for all six variants: `walk_torch` (the torch
  carried low in the shield hand's fist; raised, the strapped shield cut into the shoulder), `hold_arm` (the shield
  hand closes on the wright girl's forearm about a metre up; contact point = the left fist at the last frame, in the
  task notes for Cinematics), `let_go` (hold_arm played back), the shared `kneel_palms_flat` (spear set down) and
  `shake_head`. New hand shape: a fist (HAND_SHAPE), on the same solve as Pell's flat hand. Checks: test_stillguard,
  test_hero_clips (every other library byte-identical), test_hero_battle_clips, test_hero_locomotion, test_pell,
  test_moll OK (90); rig_probe stillguard_a..f OK with pinned, reasoned allowances; validate_data, taskboard OK.
  SELF-RENDERED the three new shots (stillguard_a_clip_walk_torch, stillguard_c_clip_hold_arm,
  stillguard_a_clip_kneel_palms_flat; no baselines): fists closed, spear on the floor in the kneel. Also filed
  M3-CHR-591 (request to creatures: Haluna's town trio can wear their own models).
- Tried and reverted: a staggered fringe for Ione. The hard line is the painted scalp hairline and the chips are the
  short-hair cards on Asha's long-hair atlas; filed as M3-CHR-592 with the plan (Moll's square line is toma_hair's
  shared hairline table).
- MERGE-READY @ 2295265c: **M3-CHR-592, Ione's crop** on Toma's short-hair tufts (opt-in `tufts` in villager_hair and
  write_materials; only Ione turns it on). The square chips on her crown are gone at dialogue range; the fringe edge
  is softer. villager_ione identical on the three numpy paths, test_villagers 45 OK; self-rendered villager_ione_face
  before and after. Next in M3-CHR-592: the other named NPCs' crops (gatekeeper, clerk, Kell, Tavi) and Moll's line.
- Merged the integration branch (ADR 0201's banned word: no hits in characters' files).
- MERGE-READY @ 5667eedb: **Pell's field row** (Lead routing: the Prologue City/Vigils/Pell capsule, M3-HER-1140, and
  fp_prologue's failing vigil test). hero_motion.json `pell` (pell_lod1, walk 1.27, run 3.13 m/s, measured with
  HeroClipGait, which reproduces Kerrid's recorded 0.71/1.80), so every Pell vigil takes his body. fp_prologue's test
  expected Liss and Pell to stay capsules: both have bodies now (Liss since her field row). Checks: Godot fp_prologue
  8/0, hero_field_actor 14/0; `--filter=hero_` 111 with 2 failures, test_hero_field_snaps (Rhen in haluna_wake and
  drowned_choir: hero-integration's and act1-chapters', known, not this change). test_qa_capsules still lists
  Haluna's villager capsules (static scan; VillagerLayer swaps them at runtime). The vigil's pose and mark stay
  slice-polish's (`back_to_sea` is Pell's vigil clip).
- MERGE-READY @ 23ee1e74: **M3-CHR-102 (Lead routing; PC QA row 31), Asha's skirt over Rhen on the beach.** The cause
  is the posture, not the cloth settings: on one knee with the left foot planted, the raised knee (0.44 m up, 0.38 m
  forward) carries the floor-length skirt 0.63 m in front of her, and Rhen lies inside that. Asha's kneel is now the
  two-knee kneel with the same lean (persona key `kneel_both`, Asha only): kneel_over_rhen, laugh, offer_hand,
  take_hand and rise_to_stand. The hem now reaches 0.24 m in front (0.66 m to the side). Self-rendered
  slice_beach_h05_asha on lead/gate-big17's marks with the new clips: the skirt lies on the sand beside him, no blue
  mass, and both faces still read. **Slice-polish: the marks can stay.** Their static `world_pose` on
  CutsceneStage/Actors/asha (haluna.tscn) is still the one-knee pose; the clip replaces it when it starts, but they may
  want it on both knees to match (theirs to change). slice_beach_h06_toma hung in capture (600 s) on cloud lavapipe
  on the gate-big17 tree, both before and after; not rendered. Checks: test_hero_clips (every other library
  byte-identical), test_asha, test_hero_battle_clips, test_hero_locomotion (99 with villagers) OK; rig_probe asha OK;
  Godot hero_stage 11 (the stage solve matches the baked kneel), cutscene_pose 5, post_import 21 OK.
- MERGE-READY @ a3efec09: **M3-CHR-592, more crops on the short-hair tufts**: the gatekeeper, the clerk, Kell and
  Tavi. Kell's white crop read as chips and now reads as soft dense hair (before/after viewed); the clerk's too; the
  gatekeeper's and Tavi's sit mostly under their headbands. All four identical on the three numpy paths;
  test_villagers OK. Not changed: the strand-tuned grey crops (Fenn, the ferrymaster, Garo, Hobb, Sabe, the
  scaleman; `grey_strands`), and Moll's square fringe line (toma_hair's shared hairline table).
- MERGE-READY @ e374376b + 21a3f966: **Pell's dialogue portraits** (big17's one new red,
  test_dialogue_box "pell has a model, so a portrait"): his entry in tools/portraits/portraits.json (a closer camera:
  at 2.3 m the default framed his neck), five emotions rendered and viewed, PROVENANCE rows. test_hero_portraits
  counts him (31) and its no-portrait example is now the purser. Godot dialogue_box 26/0, hero_portraits 9/0.
  speakers.json still names `portrait_pell_placeholder` (ui-menus' row; the test passes on the files).
- MERGE-READY @ (the grey crops commit) + 21a3f966: **M3-CHR-592, the grey crops on the tufts** (the ferrymaster,
  Garo, Hobb, Sabe, the scaleman; `grey_strands` now has a tufts form: grey cards take the short atlas's sparse column,
  narrower). Before/after viewed: soft dense crops, no chips. Fenn reverted (on the tufts his thin white hair read as
  a bald dome). All five identical on the three numpy paths; test_villagers OK. Their manifest portraits (and Ione's,
  Kell's, Tavi's) re-rendered to match, viewed.
- Merged the integration branch (big17) @ ba7913e7: kept big17's scaleman mark with his own model, its data-driven
  fp_prologue vigil test, and the union of the portrait manifest (Pell added to ui-menus' 30). Post-merge: Godot
  fp_prologue 8/0, ch01_stage_models 1/0, dialogue_box 26/0, hero_portraits 9/0; zone_cast 3/1 (the fisher idle,
  known since big16); validate_data and taskboard OK.
- MERGE-READY @ fb707070: **M3-CHR-592, Moll's fringe** ends on a broken edge (`_hair.front_break`; toma_hair takes an
  optional hairline, default Toma's). moll_face viewed before and after. Verify: moll 40/40 identical on all three
  numpy paths; toma 38, stillguard 178 and ivo 27 identical natively (unchanged); test_moll, test_toma,
  test_stillguard, test_short_hair_dialogue OK. M3-CHR-592 is in review (rendering).
- Merged lead/gate-big18 into claude/characters (13ea98ef; ui-menus' Pell portraits and camera taken, my duplicate
  PROVENANCE rows dropped, the two rows for big18's deleted Haluna placeholder kit files dropped).
- **The Lead's final-quality audit (party + every named Act I NPC), done on big18 + this branch.** Self-rendered and
  viewed 69 shots in five batches: every face close-up (party, Moll, Ivo, a Stillguard, Sefir, 20 named villagers),
  talk and laugh, walk/run cycles and the gait strip, the story clips (kneels, hauls, grips, the cast), the battle
  heroes (idle, attack, cast, ko, victory, finisher), the field party, and the silhouette line-ups. Rig probes on the
  ten heroes and 17 named villagers: all pass (cloth, props in fists, nothing through the body). Found and fixed:
  - **Bodies:** Ch6's `inquisitor` was a generic vendor: now Moll. The four Reed polers and the two wright children
    wore the Haluna Reed and the lane child: now their own models. Ch8's Stillguard `officer` had no body: built as a
    named Stillguard (M3-CHR-593: helmed, shield, no spear, the hatchet the scene's prop in his fist; idle, walk,
    hatchet_blow; job `officer` identical on the three numpy paths; stillguard 178 and ivo 27 still identical).
  - **Hair:** Tender Ruwen's grey read as light flakes: single strands now (verified on the three paths).
  - Checked and left: Ivo's laugh (an open mouth with his broken tooth, not a stray tongue); Asha's run (the wide
    skirt is M2-CHR-522's accepted look); the Old Ferryman, the boat seller, the wrights and the two unnamed children
    stay on townsfolk bodies (act1_ch05.md §27: roles the generic villagers cover).
  - Checks: Godot zone_cast 5, ch06_thread 5, ch08_thread 6, post_import 21, hero_stage 11 (all 0 failed);
    test_villagers, test_hero_clips, test_stillguard, test_blender_builds OK; validate_data, taskboard OK.
- MERGE-READY @ (this commit): the audit's fixes (ac2cef62, the officer's test and import files, Tender's strands).
- **BACKLOG EMPTY:** every Lead-routed item is merge-ready, the audit is clean, and what remains needs the real GPU
  (PC-QUEUE: Pell's fur read and warm face under the warm key).
- (was) **In progress:** Pell's second look-dev pass (M3-CHR-506, pell_review.md "What still does not read" 1–5): rounder
  lid openings and a dark eye ring, round flat ears, a flat right hand in storm_call and cast, the fur pattern, the
  nape ridge.
- **Queue after Pell:** act1_gpu_qa row 31 (open, but it is staging: M3-CHR-543 to cinematics); the Act I inventory's
  characters rows (neme, osu, reed capsules in haluna.tscn, and Pell's in corrow_night.tscn) are level-owner swaps
  (M3-CHR-519, Pell's swap note added); then my own audit of the named NPCs at dialogue range.

### PC-QUEUE
- Pell (M3-CHR-506) on the real GPU: the fur's read at full figure and the face's warm orange under the warm key
  (lavapipe has no real sheen/SSS balance); pell_front, pell_face, pell_storm_ch8.
- **WIP on the branch head (2026-10-30):** the Lead's big17-review items (Asha's skirt as soft cloth in big poses, the
  villagers' face variety) are rebuilding. **Merge only up to MERGE-READY @ 440c1f9e** until a new MERGE-READY line.

- MERGE-READY @ e151c0f0: **the PC's GPU QA pass 3 rows 31, 46, 54, 55 and 56, Pell's look, and the big17 review items**
  (Asha's skirt as soft cloth, villager face variety). Replaces the WIP note above.
  - **Rows 31 and 56, Asha's skirt:** the knee and shin bend bands widen (0.06/0.08 -> 0.16/0.18 m) and the outer
    skirt is denser (64 x 20), so the 16 panel chains bend the cloth instead of creasing it; the underskirt takes the
    outer skirt's weights (no white wedges), its hem is just above the ankle (her feet show in the run), and it has a
    lawn texture (folds, two pintucks, a drawn-thread band); clear_m 0.085 -> 0.075 (the striding leg shapes the
    front). The kneels are the two-knee kneel (M3-CHR-102). LOD0 64,962 (budget 65,000; the hidden legs under the
    skirt decimate harder). Also fixes a host-determinism edge (a skirt ring column exactly on a sector edge).
  - **Row 46, Moll's face:** the hard edge was his shield's and iron's cast shadow under the stage's low key; the face
    shots (moll_face, stillguard_a/b/c_face) use face-only stage variants without the props, from the lit side.
  - **Row 54, Sefir:** gown folds (14 periods, second harmonic, 16 mm at the hem, 18 columns per panel); a fuller,
    less transparent hair cap (scalp cards 300 -> 420, alpha 1.5); the side strands closer in (lateral 0.12, body
    pull 0.4, cohesion 0.45/0.8); mantle gold 14% -> 13% to hold the 5% waist-up budget. LOD0 61,210 (62,000).
  - **Row 55, villager hair and brows:** Toma's short-hair tufts for the child, Reed, the netmender, the smith (and
    the earlier ten); grey as strands on the netmender; Fenn's crop painted (his cards' tips read as flakes); Sabe
    without the white hairline row; every villager's brows softer (alpha 0.95) and tinted 30% toward the skin (the
    near-black cards read as scribbles); lashes unchanged.
  - **Pell (PC pass 3):** fur value patches and stronger clumps, the face desaturated, muscle 0.3 -> 0.6 and mass
    0.15 with outline fur down the forearms. His arms are still lean: there is no arm-girth slider, and inflating the
    arm skin would push it through the forearm wraps.
  - **Face variety (big17 review):** the 34 villagers' face sliders spread per name and each adult a distinct leading
    ancestry (MPFB2 macro targets); Kell keeps Tavi's nose.
  - Checks: every changed Blender job (asha, sefir, pell, 34 villagers) identical natively, X86_V4-off and
    X86_V3+V4-off; rig probes asha, pell OK (limits pinned with reasons); unit tests test_asha, test_pell, test_sefir,
    test_villagers, test_hero_clips, test_hero_locomotion, test_hero_battle_clips, test_blender_builds OK; Godot
    hero_stage 11, post_import 21, pell 3, cutscene_pose 5, zone_cast 5, villager 38, field_npc 10, hero_portraits
    9, dialogue_box 26 (all 0 failed); portraits of 20 villagers, Pell and Sefir re-rendered and viewed. Every row
    self-rendered and viewed at close-up and field distance.
- **Next (ADR 0205):** Act II, Kerrid's reveal rig (act2_plan's longest lead for this track).

## 2026-10-30, Act II: M4-A2P-054 Kerrid's reveal (ADR 0205)
- `KerridBurnGlow` (game/characters/heroes/kerrid_burn_glow.gd, data game/data/characters/kerrid_glow.json) lights
  the Burns shell per instance (glow 0..1, lift held->gold for H09) and lists the 14 VFX sockets for M4-A2P-049.
  Confession close-ups `kerrid_confession_{grief,guilty,burns}` were self-rendered and viewed: the mouth reads through
  the beard, and the burns glow at the Ch15 peak. Unit test 3/3; lint and data OK. Task -> review (cinematics).
- MERGE-READY @ 09a7928c
- **Next:** M4-A2P-050 (Tobin and Merel), then M4-A2P-051 (Malcor Venn, the Abiding guard).

## 2026-10-30, Act II: M4-A2P-050 Tobin and Merel
- Both are on the villager build with 40 face shapes, face rows, stages and shots. All 7 shots were viewed.
  - **Tobin:** Liss's family face, the Saltwright coat with the Warden's red sash, line-marks; LOD0 27.5k.
  - **Merel:** wedding red, the bridal cloth as a new `solid` shawl, LOD0 35.6k/36k.
  - **The bloodied sleeve:** `_blood` -> villager_textures.blood_atlas -> `cloth_a_blood.tres`. It is swapped in at
    runtime by `CostumeVariant` (game/characters/costume_variant.gd).
  - **Clips:** hold_hands, pole_barge, and the new tobin_falls.
- **Checks:** villager_tobin, villager_merel, villager_marra and villager_skipper_sadi are identical on all 3 numpy
  paths. test_villagers 45 OK, test_costume_variant 2/2, validate_data OK. The task is in review (rendering).
- **Known limit:** the faces are at the villager level, like Skipper Sadi's. A hero-path upgrade is possible if the GPU
  review holds Ch14's close-ups to the hero bar. Portraits are M4-A2P-081 (ui).
- LEAD-ASK: the new shots (kerrid_confession_*, villager_tobin_*, villager_merel_*) are marked pending_baseline.
  test_screenshots still fails on integration for the older unbaselined kerrid_/ivo_/pell_... shots, which carry no
  pending key; that predates these.
- MERGE-READY @ 83b8326c
- **Next:** M4-A2P-051 (Malcor Venn on Moll's kit with a halberd and Moll's battle set; then the Abiding guard).

## 2026-10-30, Act II: M4-A2P-051 part 1, Warden Malcor Venn
- **Build:** a named build on the Stillguard and Moll kit (`stillguard_variants.json` `named.venn`).
  - **Costume:** a Warden's dyes, black lacquer with gold piping, an order_marble tunic and a lacquer_red sash. They
    come from the opt-in `palette` in moll_textures.cloth_atlas and `sg_textures.dyed_cloth`.
  - **Head:** a grey crop.
  - **Weapon:** a heavy **halberd** (`sg_halberd.py`, on the spear's bone) and **no shield** (build_moll `no_shield`).
- **Clips:** Moll's battle contract and yield (B09's "driven back") plus a two-handed parry for `defend`
  (`venn_parry`).
- **Actors:** a battle actor (`game/characters/foes/venn_battle.tscn`), a field actor wrapper
  (`assets/characters/villagers/venn/venn_actor.tscn`), stages and 7 viewed shots (pending_baseline).
- **Checks:**
  - The rig probe passes; limits are pinned with reasons, as Moll's.
  - test_stillguard, test_hero_clips and test_blender_builds pass (63 tests).
  - Godot post_import 21, hero_stage 11, battle_actor 5.
  - venn, moll, the stillguard squad, ivo and the officer are identical on all 3 numpy paths, so the opt-in switches
    leave the existing builds unchanged.
- **Known limits:**
  - His face and crop are at Ivo's level.
  - In the parry the left hand stops at the chest, short of the haft.
- MERGE-READY @ 3f0f5d67
- **Next:** the Abiding guard (veiled gold lacquer: halberdier, Bulwark caster, the Captain of the Veil), in progress.

## 2026-10-30, Lead FAST-TRACKs: the human's run playtest and GPU pass 5
- **The jog (the human's #1 complaint), b344b974.** The default run for Asha, Rhen and Toma is now a brisk, grounded
  jog.
  - **Cause:** the cycle covered 2.6 m/s while the field runs at 3.6 m/s, so playback ran 1.4x fast (about 228 steps
    a minute). Rhen's sprinter arm flung his hands to his face, and the 15 fps keys were linear.
  - **Now:** elbows at 80-100 degrees with the hands between the waist and the chest, a compact counter-swing, a
    slight lean, a soft bob and a heel strike.
  - **Speed:** 164 steps a minute over a 2.6 m stride, so the cycle speed is 3.55-3.61 m/s and playback is about 1.0
    at the field's 3.6 m/s, with no foot slide. integration-qa: locomotion.json's `run.speed_mps` changed to match.
  - **Keys:** the body tracks are cubic.
  - Asha's skirt and the white underskirt move with the legs (row 56 below).
  - **Evidence:** side, front and three-quarter sheets at 6 phases, before and after, in
    `docs/kb/qa/characters/jog_2026-10-30/` (`<hero>_run_before.jpg`, `<hero>_run_after.jpg`), rendered by
    `tools/dev/loco_sheet.gd`.
  - **Checks:** test_hero_clips 19, test_hero_locomotion OK; Godot hero_field_actor 15, locomotion 9, field_motor 9,
    hero_stage 11, follower 13. The rig probes pass. Rhen's Body count is 44 -> 47 with a per-mesh reason: the right
    armpit's inner crease, under the arm in every frame of the sheets.
- **GPU pass 5 rows**, all re-rendered and viewed:
  - **Row 46 (4c706a3f):** moll_face_yield is on the prop-free face stage.
  - **Row 55 (7fbc2da2):** Fenn's and Sabe's white crops sit over a mid underpaint (no white cap).
  - **Row 54 (a3494fea):** Sefir's front locks fall along the cheek and jaw, fuller.
  - **Row 56 (5bb7e0ed):** the underskirt's hem follows the legs, so the stride shows.
  - **Pell (5bb7e0ed):** stronger fur break-up, a calmer face, mass 0.25.
  - **Checks:** asha, pell, sefir, villager_fenn and villager_sabe are identical on all 3 numpy paths.
- **The 13 villagers' rig limits (6154f6d4).** The Lead (10:07) says not to raise limits without a reason per mesh.
  I rendered every re-pinned overrun at its worst pose (front, three-quarter, back three-quarter).
  - **Visible:** the Reeds, the scaleman and the smith showed skin through the top at the back of the shoulders as
    the arms came forward. The fix is in the build: villager_costume hides a sleeved arm's skin from
    `SLEEVE_HIDE_FROM` -0.35, not -0.10. On reed_b, skin-through went from 6.4 mm/10 to 2.0/0 and the exposed boundary
    from 14 to 3, and the render is clean.
  - **In progress:** all 36 villagers are rebuilding with it. I'll then lower each re-pinned limit back to what passes
    and write a per-mesh reason for any that stays above the original.
  - The remaining overruns at full figure (elder: the sandal sole under the foot; fenn, garo, gatekeeper, marra,
    purser, ferrymaster, skipper_sadi) read clean in those renders.
- MERGE-READY @ b344b974 (jog + pass-5 rows; the villager-limit follow-up is next)
- **Rhen's armpit count (the Lead, 14:28: fix the skinning, don't stiffen the arm).** I tried giving the shirt over
  the underarm the corrective's weights (helper_bones.armpit_cloth_weights, a per-hero `mix` and `reach`). It trades
  one failure for another rather than fixing it:
  - mix 0.8: the count is 44 (pass), but throw_sail reaches 67 mm (limit 62);
  - mix 0.65: the count is 44, but throw_sail reaches 69 mm;
  - mix 0.5: the depth is 56 mm, but the count is 46.

  I reverted it, so b344b974 stands: the jog is unchanged with the count at 47 and the per-mesh reason (the right
  armpit's inner crease under the arm, covered in every jog frame of the sheets). The arm was not stiffened.
- LEAD-ASK: a proper fix is a shirt underarm gusset (a cloth patch bridging the armhole and the side, weighted to the
  armpit corrective) in rhen_costume plus a 3-path rebuild, about 2 h. Shall I do it now, or after the villager limit
  pass?
- **For integration-qa (the run speed):** per loop of `run`, the root travels 2.6 m (Asha and Rhen) or 2.65 m (Toma)
  in 0.733 s, two steps, 164 steps a minute, so `speed_mps` is 3.545 / 3.545 / 3.614 in
  game/data/characters/locomotion.json. The field's run_speed_mps 3.6 plays it at 1.00-1.02x.
