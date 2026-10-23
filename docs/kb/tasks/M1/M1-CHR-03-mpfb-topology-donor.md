---
id: M1-CHR-03
title: Rebuild the hero head and base body on the MPFB2 CC0 topology (SPEC §16 Q2 = yes)
role: character
status: doing
owner_session: "character-stream-4 (worktree-agent-ab3226d3af8f7c29e)"
depends_on: [M1-CHR-02]
milestone: M1
request-from: "lead"
---
## Goal
The human answered SPEC §16 Q2 on 2026-10-23: MPFB/MakeHuman may be used **as a tool, with heavy modification, logged in an ADR**. Asha's from-scratch face failed the §14 dialogue-range review twice (CHR-01, CHR-02; ADR 0010's trigger, ADR 0019).

## Acceptance criteria
- [ ] ADR (next free number) records the Q2 answer, what is vendored, and the license split: only the **CC0 data** (base mesh, targets, proxies, weights) is vendored; **no GPL code** from MPFB2 enters the repo (CLAUDE.md §2: code-only addons must be permissive)
- [ ] A fetch script under tools/ pins an exact MPFB2 commit and its data paths, so the vendored subset is reproducible; the vendored files sit under assets_src/third_party/mpfb2/ with the license text; assets/PROVENANCE.md rows for everything derived from them
- [ ] The base body and Asha's head are rebuilt on the donor topology behind the existing interfaces (parameters JSON, landmarks, DEF-* skeleton, asha.md §6.2 shape names); heavy modification (proportions per SPEC §7.3, our own sculpt and detail passes)
- [ ] Face shapes and visemes re-targeted; LOD1; GLB under 5 MB
- [ ] §14 dialogue-range face review passes (asha_face_* shots, side by side with the CHR-02 version); base_body_* and asha_* baselines re-approved with the reasons recorded
- [ ] ADR 0019 updated with an append-only note saying whether the close-range stylisation is still needed

## Review log
