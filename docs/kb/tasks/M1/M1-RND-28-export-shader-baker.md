---
id: M1-RND-28
title: Export shader baker on a Windows release build; measure boot and zone entries against ADR 0029
role: rendering
status: done
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: environment
depends_on: [M1-RND-27, M1-ARC-16]
milestone: M1
request-from: "lead"
---
## Goal
ADR 0029 follow-up 1, split out of M1-RND-27. The Lead approved installing the export templates on the PC (2026-10-24):
- only the official `Godot_v4.6.3-stable_export_templates.tpz` from godotengine.org or the official GitHub release;
- checked against the published SHA-512;
- installed in Godot's standard templates folder, and never committed;
- the 75 % load cap kept throughout.

RND-27 left the boot's plain first frame (0.86 s cold) to Godot's own first-use pipelines, which the baker builds at
export.

## Acceptance criteria
- [x] The templates are installed as above, with the SHA-512 recorded in the task notes.
- [x] `export_presets.cfg` enables the shader baker for the Windows preset, and a release build exports.
- [x] The release build's boot worst frame, and its zone entries' worst hidden and visible frames, are measured
      against ADR 0029 / SPEC v1.3 §4.2: visible ≤ 50 ms, hidden ≤ 1 s, entry ≤ 3 s. Visible frames come from
      `SceneRouter.last_swap_stats["max_visible_frame_ms"]` (M1-ARC-16).

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Report: `docs/kb/qa/gpu/2026-10-24-rnd-28-shader-baker.md`.
- **Templates.** The official `Godot_v4.6.3-stable_export_templates.tpz` from the GitHub release, SHA-512
  `da606b61c10157844f8300172df374472665f95015495cb1a7cd132c40ede404faa96cc1016a4b9662db9909ddea69632c4948b2cd11163438dad4808881fb68`
  (matches SHA512-SUMS.txt). Installed in `%APPDATA%/Godot/export_templates/4.6.3.stable/`, not committed.
- **Baker.** `shader_baker/enabled=true` on `Windows Desktop`, plus a `Windows Perf` preset whose main scene is the
  slice sweep (`run/main_scene.perf_build`).
- **Measured (High 1440p).**
  - **Fresh install (cold):** the baker cuts Haluna's entry from 11.4 to 8.0 s, and the Flood's first frame from
    1024 to 79 ms. It's still over ADR 0029: hidden frames to 2.0 s, Haluna 8 s, the title visible at 1.2 s.
    Filed **M1-RND-29** (first-launch pipelines).
  - **Second launch:** Haluna 2.55 s (within 3 s); visible frames ≤ 8 ms except the title (160, M2-ARC-03) and the
    Flood (42, M2-RND-07).
- **Blocker found.** `Windows Desktop` excludes `game/levels/_tests/*`, but shipped code depends on it, so a release
  build's SceneRouter fails to compile and Haluna can't load. Filed **M2-ARC-04**.
- `max_visible_frame_ms` (M1-ARC-16) isn't merged; the sweep measured visible frames itself.

## Review log
- 2026-10-24 review-sweep-R (environment): **approve.** The templates came from the official release, and the SHA-512 is recorded and was checked with `sha512sum -c`. Nothing is committed. `export_presets.cfg`: `shader_baker/enabled=true` on Windows Desktop, and the new `Windows Perf` preset (feature `perf_build`, `run/main_scene.perf_build`) that shipped builds never see. The measurement is a careful baked/unbaked/editor comparison, cold and warm. It found that editor-binary cold numbers understate a player's first launch, and the M2-ARC-04 blocker (a release build can't compile SceneRouter without `_tests`), so M2-ARC-04 is now the first thing to fix before any shippable build. Criterion 3's "visible frames come from `max_visible_frame_ms`" couldn't be met, because M1-ARC-16 wasn't merged yet. M2-ARC-03's PC review re-measured with the router's own stat, which covers it. One run per cell; the RND-29 re-measure covers three presets. No game code changed, so no Godot run is needed.
