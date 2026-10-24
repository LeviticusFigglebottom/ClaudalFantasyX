---
id: M1-CHR-03
title: Rebuild the hero head and base body on the MPFB2 CC0 topology (SPEC §16 Q2 = yes)
role: character
status: done
reviewer: rendering
owner_session: "character-stream-4 (worktree-agent-ab3226d3af8f7c29e)"
depends_on: [M1-CHR-02]
milestone: M1
request-from: "lead"
---
## Goal
The human answered SPEC §16 Q2 on 2026-10-23: MPFB/MakeHuman may be used **as a tool, with heavy modification, logged in an ADR**. Asha's from-scratch face failed the §14 dialogue-range review twice (CHR-01, CHR-02; ADR 0010's trigger, ADR 0019).

## Acceptance criteria
- [x] ADR (next free number) records the Q2 answer, what is vendored, and the license split: only the **CC0 data** (base mesh, targets, proxies, weights) is vendored; **no GPL code** from MPFB2 enters the repo (CLAUDE.md §2: code-only addons must be permissive)
- [x] A fetch script under tools/ pins an exact MPFB2 commit and its data paths, so the vendored subset is reproducible; the vendored files sit under assets_src/third_party/mpfb2/ with the license text; assets/PROVENANCE.md rows for everything derived from them
- [x] The base body and Asha's head are rebuilt on the donor topology behind the existing interfaces (parameters JSON, landmarks, DEF-* skeleton, asha.md §6.2 shape names); heavy modification (proportions per SPEC §7.3, our own sculpt and detail passes)
- [x] Face shapes and visemes re-targeted; LOD1; GLB under 5 MB
- [x] §14 dialogue-range face review passes (asha_face_* shots, side by side with the CHR-02 version); base_body_* and asha_* baselines re-approved with the reasons recorded
- [x] ADR 0019 updated with an append-only note saying whether the close-range stylisation is still needed

## Notes
2026-10-23 character-stream-4: done on branch `worktree-agent-ab3226d3af8f7c29e` (not pushed).
- ADR 0021 (0020 was taken): only the CC0 data is vendored; no GPL code; our own readers in `mpfb_data.py`.
- `tools/fetch_mpfb2.py` pins `b1a2dc98776da9d1eea751b159d42cf61778fe2e` (71 files, 4.4 MB, `--check` offline). PROVENANCE rows for every vendored file and the derived assets.
- `bb_donor.py`: macro mix, an RBF fit to our landmarks, a girth fit to the anatomy field, the eye/lid conformance to EyeFrame, lip closure, our face sliders, a field re-seated on the skin, donor weights onto `DEF-*`, adaptive Catmull-Clark on the hero face, re-targeted expression units.
- Asha: LOD0 62,200 tris, LOD1 29,242, `asha.glb` 3.94 MB (morph normals dropped), same 23 textures. Base bodies 26,756 tris each.
- **Verdict (asha_review.md §6): passes at dialogue range with the ADR 0019 close-range look; borderline as built** (the mouth's rest shape and the skin surface). All 10 `asha_*` and 11 `base_body_*` baselines re-approved (reasons in asha_review.md §6 and the handoff).
- Follow-ups: a lip pass; skin colour zones and creases; hair; a GPU and motion review; Rhen and Toma `donor_mix` and face sliders.

## Review log
- 2026-10-24 review-sweep-O (rendering): **approve with fixes.** The donor pipeline is sound and its guardrails hold. The §14 "passes" in criterion 5 has since been overtaken: rounds 4-6 (M1-CHR-04 to 11) and M1-QA-05c judged Asha **not** to pass strict §14 at dialogue range, and M1-CHR-12 carries that now. I'm closing CHR-03 as the topology round it was.
  - **Checks:**
    - `tools/fetch_mpfb2.py --check`: "mpfb2 vendored data: OK" (pinned b1a2dc9).
    - assets_src/third_party/mpfb2/ holds only data (68 .gz targets and weights, 1 .obj, 1 .json manifest, 3 licence and readme .md). There is **no MPFB2 code**, so no GPL enters the repo. LICENSE.md and LICENSE.ASSETS.md are vendored with it.
    - PROVENANCE has 86 `third_party/mpfb2` rows. ADR 0021 records the Q2 answer and the CC0/GPL split. ADR 0019 has its append-only note. SPEC v1.1 records Q2.
    - `asha.glb` is now 4.60 MB (rounds 5 and 6 added to CHR-03's 3.94 MB). It's under 5 MB, but with only 0.4 MB of headroom; M1-CHR-12 watches it.
  - **Filed:** M2-CHR-01, for Rhen's and Toma's `donor_mix` and face sliders. This item from the follow-up list never became a task. The lip, skin, hair and GPU follow-ups were covered by CHR-04 to 11, and the rest are in M1-CHR-12.
  - **For the Lead:** CLAUDE.md §2 still says "CC0 meshes are off-limits" with no pointer to the ADR 0021 exception. A one-line note there would keep the next agent from flagging the vendored data as a guardrail breach.
