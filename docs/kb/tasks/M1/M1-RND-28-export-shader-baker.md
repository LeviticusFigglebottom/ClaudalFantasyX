---
id: M1-RND-28
title: Export shader baker on a Windows release build; measure boot and zone entries against ADR 0029
role: rendering
status: doing
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
- [ ] The templates are installed as above, with the SHA-512 recorded in the task notes.
- [ ] `export_presets.cfg` enables the shader baker for the Windows preset, and a release build exports.
- [ ] The release build's boot worst frame, and its zone entries' worst hidden and visible frames, are measured
      against ADR 0029 / SPEC v1.3 §4.2: visible ≤ 50 ms, hidden ≤ 1 s, entry ≤ 3 s. Visible frames come from
      `SceneRouter.last_swap_stats["max_visible_frame_ms"]` (M1-ARC-16).

## Review log
