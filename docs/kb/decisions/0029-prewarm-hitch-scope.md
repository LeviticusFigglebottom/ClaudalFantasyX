# 0029 — What SPEC §4.2's 50 ms hitch limit covers, and how loading-screen frames are budgeted

- **Status:** proposed (Rendering, M1-RND-22; for the Lead, who edits SPEC)
- **Date:** 2026-10-24
- **Roles affected:** Rendering, Tech (SceneRouter, boot), Environment (zones), Cinematics
- **Author role:** Rendering (PC GPU session)

## Context
SPEC §4.2: "No hitch over 50 ms during battle transitions or dialogue. Prewarm shaders with a shader-cache warmup
scene." Measured by M1-RND-22 on an RX 9070 XT (`docs/kb/qa/gpu/2026-10-24-rnd-22-prewarm.md`), after its fixes
(tier filtering, the test material out of the registry, a boot warm-up of the resident shaders):
- **Battle transitions:** 34–46 ms worst frame on Low, High and Ultra, cold and warm. **Met.**
- **Zone entries and the storm scene:** 142–312 ms. These happen behind SceneRouter's full fade.
- **The boot warm-up:** 1.3–3.1 s, worst frame 0.5–1.7 s, once per session.

SPEC doesn't say whether frames hidden by a full-screen fade or loading screen count as hitches. Read that way,
it's an unbounded promise for zone loads.

## Options
1. **Count every frame everywhere** (50 ms during zone loads and boot too). That needs export-time shader baking
   *and* main-thread-free zone instancing; Godot 4.6's threaded resource loading crashed on Haluna when the
   prewarm used it.
2. **Count the frames the player sees** (battle transitions, dialogue, cuts, and the first frames after a fade
   lifts), and give the hidden frames a loading budget. *(Proposed.)*
3. Leave SPEC as it is. Each reviewer then reads it differently, as review-sweeps J, N and O did.

## Decision (proposed)
Option 2. Proposed SPEC §4.2 wording for the Lead:

> No visible hitch over 50 ms: battle transitions, dialogue and cutscene cuts, and the first 60 frames after any
> fade lifts. Frames hidden behind a full-screen fade or loading screen are loading time: no single hidden frame
> over 1 s (a stall that long reads as a freeze through the fade's audio and animation), and zone entries under
> 3 s. The shader warm-up (prewarm stage plus the boot warm-up of resident shaders) is what keeps the visible
> frames in budget.

How the build meets it today:
- Battle transitions are in budget.
- Zone entries and storm loads: hidden worst frames are 0.14–0.31 s, under 1 s.
- Boot: the warm-up's worst frame is 0.53–1.66 s, over 1 s in 9 of the 18 measured runs (6 cold, 3 warm).
  **The boot warm-up is the one item over the proposed hidden-frame limit.** It runs under the boot screen before
  the title. Slicing it further (`materials_per_frame` for the resident run) is follow-up work.

## Consequences
- The review question becomes "is it visible?", which the router can measure (its `frame_ms` after the fade).
- **Follow-ups (Rendering):**
  1. Enable Godot's export shader baker in `export_presets.cfg` and measure a release build: it removes the
     shader compiles behind most of the remaining cost. This needs export templates; none are installed on the PC.
  2. Harvest a zone's materials from its `SceneState`, without instancing it: Haluna's 0.3 s.
  3. Slice the boot warm-up under 1 s a frame.
- If the Lead prefers Option 1, the follow-ups become blockers instead.
