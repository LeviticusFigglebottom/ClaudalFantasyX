---
id: M2-RND-16
title: "'130 resources still in use' at exit in release builds after Haluna (root cause, then fix)"
role: rendering
status: doing
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: architect
depends_on: []
milestone: M2
request-from: "lead"
---
## Goal
Every release quit after a real session logs "130 resources still in use at exit" (M2-ARC-08 re-measure). Root-cause
it and fix it.

## Acceptance criteria
- [ ] Root cause.
- [ ] Fix: a release run through Haluna quits with nothing in use.

## Notes (PC GPU, 2026-10-24): established so far
**What leaks (`--verbose`).** 120 GDScripts (the battle, progression, UI and core class graph: `formulas.gd`,
`combatant.gd`, `game_state_data.gd`, `flag_registry.gd` and so on), 6 Shaders and 4 ShaderIncludes (glimmer, the
battle ring, two UI shaders). Leaked objects: 121 GDScript, 73 GDScriptNativeClass, 1 RefCounted, 1 WeakRef, and
**no nodes**. GDScript refcounts run up to 262.

**When.**

| Build | Run | Leak |
|---|---|---|
| Editor binary | launch | none |
| Release (`Windows Perf`) | launch only; launch + title; launch + tideline battle | none (1–2 resources) |
| Release | **launch + Haluna Beach** | **130**, deterministic (5/5) |

So the trigger is Haluna in a release build. The battle scripts leak when Haluna loads them, not when a battle loads
them directly.

**Ruled out:**
- **Object-holding static variables.** I cleared every one at exit from SceneRouter's predelete (an `ExitRelease`
  experiment, not committed): still 130.
- **Threaded instancing.** With `SceneRouter.instantiate_on_thread = false`: still 130.
- **Engine-singleton signal connections** that might outlive the scene. The only one in the game is UndertowHalfRes's
  `RenderingServer.frame_pre_draw`, and Haluna has no storm.

**Next.** One live RefCounted (plus a WeakRef) pins the class graph. Bisect Haluna's subtrees (the mood scene, the
cutscene stage and cast, the villagers, the triggers, the save shrine) with one release export per step, to find
the object. It's exit-time only, so it costs nothing in play.
