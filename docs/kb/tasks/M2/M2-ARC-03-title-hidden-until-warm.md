---
id: M2-ARC-03
title: The title shows while the boot warm-up runs (visible frames of 168-265 ms)
role: architect
status: doing
owner_session: "worktree-agent-ab7730349ee425e33"
reviewer: rendering
depends_on: [M1-RND-27]
milestone: M2
request-from: "rendering"
---
## Goal
ADR 0029 counts the boot warm-up (resident shaders, M1-RND-22/27) as hidden time, "under the boot screen before the
title". But the boot screen is the bootstrap title itself (boot.gd, TitleMenu). So while the menu shows, the
player sees:
- the swap frame (330 ms);
- the font warm-up (186 ms);
- the warm-up's frames (up to 0.89 s cold, RND-27).

The slice perf sweep measured the title's visible window at 168–265 ms worst (Low, High, Ultra;
docs/kb/qa/gpu/2026-10-24-slice-perf-sweep.md).

## Acceptance criteria
- [ ] The title menu appears only once the boot warm-up and font warm-up have finished. They run behind an opaque
      boot card or the router's fade, as ADR 0029 assumes.
- [ ] The sweep's `title` segment shows no visible frame over 50 ms (`tools/gpu_bench/slice_sweep.tscn --
      --segments=title`).

## Review log
