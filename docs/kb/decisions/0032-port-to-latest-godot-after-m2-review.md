# 0032 — Port to the latest stable Godot (4.7.2) after the M2 slice review

- **Status:** accepted (the human, 2026-10-24). It supersedes ADR 0001 **when the port lands**; until then, 4.6.3-stable stays pinned.
- **Date:** 2026-10-24
- **Roles affected:** all (Lead, Rendering/PC GPU, Architect, QA, every track)
- **Author role:** Lead

## Context
- The human directed that the game ship on the latest Godot rather than the pinned 4.6.3 (ADR 0001).
- The PC GPU session ran a throwaway port check on 4.7.2 (docs/kb/qa/gpu/2026-10-24-godot-472-port-check.md, branch gpu/godot-472-port-check):
  - it imports, and the tests pass (1449/0);
  - GPU costs match 4.6.3 within 2%;
  - the re-import adds 4.7 default keys to 45 .import files;
  - **Haluna's zone entry regresses from 3.1 to 5.4 s.** The worker-thread instance takes 3.36 s, against 1.5–1.75 s on 4.6.3.
- The cloud toolchain fetches Godot from the Ubuntu archive, which only carries up to 4.6.3. GitHub release downloads are now reachable from the cloud containers, so the official 4.7.2 Linux build can replace the archive build.
- Porting re-imports every environment and changes the lavapipe renderer, so every screenshot baseline must be re-approved. Doing it mid-slice would churn every track while the human's blocking M2 review (SPEC §16 Q7) is close.

## Options
1. Port now, mid-slice.
2. Port after the M2 slice review, as the first M3 task.
3. Stay on 4.6.3.

## Decision
**Option 2** (the human's choice). The vertical slice is finished and reviewed on 4.6.3. The port to the latest stable Godot is the first M3 task, and it supersedes ADR 0001 when it lands.

## Consequences
- **Before the port** (allowed now, no commits to the engine pin): the PC root-causes the 4.7.2 Haluna regression, and fixes that also help 4.6.3 can land early.
- **The port task (M3)** covers:
  - tools/dev/fetch_godot.py fetches the official 4.7.2 build plus its SHA-512 check, and the lavapipe wrapper is kept;
  - the PC installs the 4.7.2 export templates (checksum-verified);
  - the re-import, with the .import key churn committed in one commit;
  - re-checks of the 4.6.3 workarounds (FSR2 dither, the prewarm staging, the delta cap that M1-RND-29 noted);
  - the full gate, re-approving every baseline after viewing;
  - CLAUDE.md §3 and docs/kb/tech/engine.md updated.
- **Watch:** the Haluna entry against ADR 0029's 3 s, and any 4.7 shader-compile or pipeline-cache changes against M1-RND-28/29.
