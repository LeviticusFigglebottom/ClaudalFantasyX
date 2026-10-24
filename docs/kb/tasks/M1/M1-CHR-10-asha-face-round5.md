---
id: M1-CHR-10
title: Asha round 5: hair black and strand-broken, lashes, lid band, brows, teeth, mouth normals
role: character
status: done
reviewer: rendering
owner_session: "worktree-agent-a109a5ba219573018"
depends_on: [M1-CHR-09]
milestone: M1
request-from: "rendering"
---
## Goal
From the review-sweep-L entries (file:line references there).

## Acceptance criteria
- [ ] Hair reads black (asha.md:121), not auburn: check albedo, the hair shader primary tint and anisotropic highlight colour; the crown is no longer a smooth shell. **Partial:** black is done, but the crown is still a sleek shell. The cause was the base colour, not the shader, so no shader change was needed (ADR 0024, proposed). The card geometry is unchanged. **→ The crown shell moved to M1-CHR-12 (review-sweep-O).**
- [ ] Lashes: tapered clumps, not comb teeth; the pale upper-lid band is gone (albedo, AO, or lid geometry). **Partial:** the lashes are tapered clumps; the band is reduced, not gone: a tan strip still shows between the lashes and the crease (asha_review.md §10.4). **→ The lid band was reduced again in M1-CHR-11; the rest moved to M1-CHR-12 (review-sweep-O).**
- [x] Brows: soft edges, hair-stroke density falloff
- [x] Grief: no blue-grey tooth slab (teeth albedo and occlusion; mouth-interior AO). The hard inner lower-lip edge remains.
- [x] Morph normals on the mouth surface as well as skin_head (88 vertices); no diagonal striations at the smiling mouth corner. **Split:** the mouth normals are done (16 shapes). The striations are a key-light shadow terminator, not normals, and they remain. Handed to M1-RND-20 (§10.3). **Done:** M1-RND-20 fixed the striations (key and rim `shadow_normal_bias` 4.5, merged and re-approved on lavapipe).
- [ ] Evenly lit skin: work with the shading (cavity, roughness breakup, the painterly close-range look per ADR 0019). **Partial:** the material levers are used (roughness range, cavity, micro-roughness, a head mottle). At 1× the skin still reads smooth and evenly lit. **→ Moved to M1-CHR-12, judged on the M1-QA-08 GPU capture (review-sweep-O).**
- [x] Blender gate byte-identical; under 5 MB; §14 review strict in asha_review.md §10; then a 2x High GPU capture by the PC session (M1-QA-05c) as final judge. **Done except the GPU capture:** the gate passes (see Notes), every file is under 5 MB, and the review is written. The GPU capture is still to come. **Done:** M1-QA-05c delivered the GPU capture.

## Notes
- **Verdict** (asha_review.md §10.4):
  - Five of the six named faults are fixed or clearly reduced at the asset.
  - **Strict SPEC §14 at dialogue range: FAIL as built**; borderline with the ADR 0019 look.
  - What still fails, in order:
    1. skin evenness;
    2. the crown shell;
    3. the smile-corner striations (M1-RND-20);
    4. the grief inner-lip edge;
    5. the lid strip;
    6. brows a touch thin;
    7. the hair's slight warm cast.
- **Diagnostics** (lavapipe, one override per render):
  - With every hair lobe off, the crown still rendered auburn, so the fault was the base colour.
  - The grief slab was the teeth's sky specular: the teeth turned pure red with specular 0 went dark.
  - The corner striations vanish with the key shadow off and sharpen with finer shadow texels.
- **Gates** (scoped, CLAUDE.md "Gate scope"):
  - `verify_blender_builds.py --job asha`: **44 identical**, rc 0, 288 s (Blender 5.0.1, --threads 4) on commit e863a98; the later write_materials.py edit is comment-only (re-running it leaves every .tres byte-identical)
  - asha_* shots: the 4 face shots re-approved after viewing; the 6 field shots pass within their limits, baselines kept; re-compare 10/10 PASS.
  - tools unittest 415 OK; validate_data 0 errors; taskboard pass; manifest 60 valid.
  - **Skipped:** gdlint/gdformat and the Godot character filter (no `.gd` or shader touched; materials are `.tres` generated from Python), coverage (no battle or progression code), and the other Blender jobs and screenshots.
- **Numbers:** LOD0 62,290; LOD1 29,378; `asha.glb` 4,487,948 B; largest file the head skinmask, 3.28 MB.
- **For the reviewer (Rendering):**
  - ADR 0024's hair values. Watch the cool tint under a non-warm key.
  - M1-RND-20.
  - The skin's evenness, which is now shading.
  - The GPU 2× High capture of asha_face_* (M1-QA-05c).

## Review log
- 2026-10-23 rendering, fresh reviewer (review-sweep-M): **approve the round as delivered. Strict SPEC §14 verdict at dialogue range: FAIL. The task must not move to `done` with four criteria unticked.** Close it as a partial round only once the follow-ups below are filed. No merge blockers: the asset, the gate and the baselines are consistent.
  - **Checks:**
    - Tools unittest 431 OK, including test_asha and test_asha_face_drive. validate_data 0/0, taskboard --check OK.
    - Godot `--filter=character_shading` 14/0 and `--filter=post_import` 15/0, which covers the asha `.tres` slot mapping.
    - The four re-approved baselines are consistent with the materials diff in 3907e54.
    - **Not run:** the Blender asha job (the author reports 44 identical on e863a98, and nothing has changed since) and the asha_* shots, because no scene or shader changed after the re-approval.
  - **What I viewed:** `asha_face_neutral`, `smile`, `grief` and `stylized_compare` at full size, plus 4× crops of the eyes (neutral), the mouth (grief) and the right figure's temple (stylized_compare).
  - **Confirmed fixed:** the hair and braid now read near-black, not auburn. The lashes are dark clumps on a lash line, not a comb. The brows have soft edges. The blue-grey tooth slab of CHR-09 is mostly gone.
  - **Strict §14 faults I see, in order of cost.** These are in addition to, or sharper than, §10.4's list:
    1. **Skin, and the hard nose shadow.** The face is evenly lit and smooth: §10.4 item 1, agreed. On top of that, the key casts a hard-edged dark wedge from the nose bridge over the inner corner of screen-right's eye and onto the cheek, in all three face shots. At 1× it reads as a bruise. It is the same shadow-terminator and hardness family as M1-RND-20, so add it to that task.
    2. **Grief mouth.** At 4× the upper teeth read as a dark grey, faceted strip with hard polygon edges and a specular sheen. A saw-tooth shadow edge sits under the lower lip at the screen-right corner. "Slab gone" (§10.4) is too generous: it is reduced. With the hard inner lower-lip edge, this is still the most uncanny frame.
    3. **The crown and hairline.** The crown is a sleek shell (agreed, criterion 1). The hairline is also one hard, even arc over a very tall forehead, with no wisps or fringe. Fold this into the crown geometry follow-up.
    4. **The lid strip.** The tan band between the lash clumps and the crease is clearly visible at 1×, so the clumps read as a strip lash on a light eyeshadow. That is more than "reduced".
    5. **Expression.** In `smile` the eyes, lids and cheeks do not move, so it reads as a smirk with dead eyes. In `grief` the brows barely lift at the inner ends. This is outside the named criteria, but §14 judges the expression set.
    6. **A blue-grey hair lock** in `asha_face_stylized_compare` (right figure). The temple lock card reads silver-blue over a dark red-brown contact streak on the skin. That is ADR 0024 watch item 1, already visible under this warm key on the stylized skin.
  - **Follow-ups to file before closing** (Character, unless noted):
    - crown and hairline geometry;
    - the lid strip and lash shadow;
    - the grief mouth interior (teeth facets and specular, the inner lip edge);
    - expression: eye and cheek participation in `smile`, inner-brow lift in `grief`;
    - the nose cast shadow, added to M1-RND-20 (Rendering);
    - the skin evenness on the GPU (Rendering, M1-QA-05c).
  - **ADR 0024 opinion: accept the direction, but not yet the numbers. Keep it `proposed` until two checks are done.**
    - The diagnosis is sound and well isolated. With every lobe off the crown was still auburn, so the base colour is the fault. Option 3 is the right physical fix, with no shader change and no light change.
    - The neutral near-black base (#141417) and the dark-pigment secondary and transmission are the right choice, and I would accept them now.
    - The primary tint `Color(0.76, 0.85, 1.0)` at 0.45 is strongly blue. The stylized_compare lock already reads silver-blue under the warm key, so under a neutral or cool key it will read blue-black. Try a near-neutral cool such as `Color(0.88, 0.90, 0.95)` before accepting.
    - **Check 1, on lavapipe now, no GPU needed:** one render of `asha_face_neutral` under a neutral white key, to measure the crown's R:B and the lock's hue.
    - **Check 2:** the M1-QA-05c GPU capture.
    - Two smaller points:
      - The table does not say which way `root_occlusion` and `depth_occlusion` run. Raising them "so the sky fill reaches the mass" implies that higher means less occlusion. State it.
      - `spec_shift_jitter` sits at the shader's cap (0.3). That says the cap is binding: Rendering should consider raising it rather than tuning against it.
    - Art must amend asha.md §5 to match, or supersede the ADR, before it moves to accepted. The Lead accepts it after both checks.
- 2026-10-23 lead: stays in review until M1-QA-05c (the PC's 2x GPU capture). The sweep-M faults are recorded for the next round. ADR 0024 stays proposed: test a neutral cool highlight tint (about 0.88, 0.90, 0.95) first.
- 2026-10-23 rendering (review-sweep-N, fresh reviewer, applying M1-QA-05c): **still review; don't close.** QA-05c, the GPU judgement the Lead was waiting for, has landed: neutral passes, grief fails, and smile needed RND-20, which is now merged and clean on lavapipe.
  - **What CHR-10 needs before closing:**
    - Criterion 2 (the lid band) is still visible on the GPU: QA-05c fault 5, "orange, like make-up". Criterion 1's crown shell is still partial. Either finish them, or move them explicitly to a round-6 task, and tick or strike them here.
    - Criterion 5's striation half is done by M1-RND-20 (bias 4.5). Mark it done, with that reference.
  - **To file now** (Character, round 6):
    - the grief teeth: cooler albedo, more roughness, tooth separation and smoother normals (QA-05c fault 3);
    - the lash density and irregularity (fault 4);
    - the notch at the inner corner of the grief brow (fault 6);
    - the smile expression: eyes and cheeks;
    - the ragged upper-lip border.
  - **To file now** (Rendering): the cavity fill or AO floor for the grief mouth interior (QA-05c fault 2).
  - **ADR 0024:** QA-05c confirms near-black with a dark-brown sheen on the GPU, which is check 2 of sweep-M. Check 1, the neutral-key R:B and the lock hue on lavapipe, plus the neutral cool tint trial, is still owed before the ADR is accepted.
- 2026-10-24 review-sweep-O (rendering): **approve with fixes, accepted as a round. The strict §14 judgement stays with the GPU (M1-QA-08) and the human.** Every follow-up sweeps M and N asked for now has a home:
  - **Round 6, M1-CHR-11:** the grief teeth, the lashes, the brow notch, the smile's eyes and cheeks, and the upper-lip border.
  - **M1-RND-21:** the cavity fill for the mouth interior.
  - **M1-RND-20:** the striations and the nose wedge. Criterion 5 is now ticked against it.
  - **M1-CHR-12 (new):** the crown shell (criterion 1), the residue of the lid band (criterion 2), skin evenness (criterion 6) and ADR 0024 check 1.
  - **M1-QA-08 (new):** the GPU re-capture.
  - Criterion 7's GPU capture was M1-QA-05c, which has landed, so criterion 7 is ticked too.
  - **What I viewed:** the current `asha_face_smile` and `asha_face_grief` baselines, which now carry round 6, at full size. The crown is still a sleek shell with a hard, even hairline arc. The nose wedge on screen-right's cheek is softer than at sweep-M, but still a hard-edged shadow.
  - **Not re-run:** the Blender gate and the asha shots. Nothing in CHR-10's scope changed after round 6's re-approval.
  - **ADR 0024:** it stays `proposed` until M1-CHR-12 records check 1.
