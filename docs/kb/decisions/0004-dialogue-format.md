# 0004 — Dialogue format: `.dlg` (Yarn-like, custom), compiled to JSON

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** Narrative, Cinematics, Systems, UI, QA
- **Author role:** Lead

## Context
SPEC §5.6 calls for a writer-friendly plain-text format supporting speaker, emotion tag, camera cue, animation cue, branching on flags, and localization keys, compiled to resources by a tool. Code-only dialogue addons are allowed, but each one imposes its own syntax and editor workflow, and our validator needs to see flags and line keys.

## Options
1. Adopt an existing Yarn or dialogue addon (vendored code-only).
2. A custom `.dlg` format with a small Python compiler and a GDScript runner.

## Decision
Use a **custom `.dlg` format**. Files live in `game/data/dialogue/<chapter>/<scene>.dlg`. The compiler is `tools/dlgc.py` (task M1-NAR-03). It writes `game/data/dialogue/compiled/<scene>.json`, and it writes the English strings to `game/data/loc/dialogue.csv` (Godot CSV translation format, key `DLG_<LINE_ID>`).

```
title: ch1_dock_farewell
---
@camera dock_wide blend=1.5           // cue lines start with @ (camera, anim, mark, fade, music, vfx, wait, letterbox)
@anim asha look_at rhen
Rhen [worried]: I don't think the boat is coming back. #line:ch1_dock_001
<<if $ch1_met_asha>>
Asha [soft_smile]: Then we walk. #line:ch1_dock_002
<<else>>
Asha [neutral]: You're the one from the water. #line:ch1_dock_003
<<endif>>
-> Wait for it. #line:ch1_dock_004
    <<jump ch1_dock_wait>>
-> Walk. #line:ch1_dock_005
    <<set $ch1_walked = true>>
===
```

- `Speaker [emotion]: text #line:<id>`. The emotion drives the expression blends (SPEC §8.3). Every line **must** carry a unique `#line:` id.
- `$flag` names must be declared in `game/data/flags.tres`. `tools/validate_data.py` already enforces this for `.dlg` files.
- `->` options, `<<if>>/<<elseif>>/<<else>>/<<endif>>`, `<<set>>`, `<<jump>>`, `<<event name args>>` (emitted on `EventBus.dialogue_event`).
- **Lip-flap** comes procedurally from the displayed text at runtime, not from data.
- **Voice (SPEC §16 Q4 default):** no voice acting. The typewriter reveal plays a per-speaker blip (`assets/audio/sfx/text_blip.ogg` pitched per character). Each compiled line keeps an optional `voice` field, empty for now, so voice files can be added later without a format change.

## Consequences
We own the parser, which is small and testable. Writers get Yarn-like ergonomics, and the validator sees every flag and loc key. The cutscene sequencer (Cinematics) consumes the same `@` cue vocabulary, so the cue names are documented in `docs/kb/tech/dialogue_format.md` as they grow.
