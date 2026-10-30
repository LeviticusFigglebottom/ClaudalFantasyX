# 0205 — Ship the game, not the gate: fast batches, a 2 s hitch bar, Act II starts per track

- **Status:** accepted (the human's directive, 2026-10-30)
- **Date:** 2026-10-30
- **Roles affected:** all
- **Author role:** lead
- **Supersedes:** ADR 0042 §4's 1 s target and §5's "full gate" wording; ADR 0203's criteria 3 and 5, and its "Act II starts all at once" rule.

## Context
The human, 2026-10-30: "Hours? That's ridiculous, and the ui thing is nitpicky; 2 seconds is fine. The super long screenshots and suites seem unproductive and needlessly barring... this is a game we're building above all. Don't half ass anything, but we need act 1 to be completed here soon, so prioritize that, and move onto act 2 whenever ready (certain tracks/envs can begin to if they're ready)."

A batch was taking 10–12 hours, mostly a 6–8 h full screenshot capture on lavapipe and a 2 h full Godot suite. Those checks almost never catch anything the tracks' own scoped checks and self-renders miss.

## Decision
1. **Hitch bar: ≤ 2 s hidden per scene change, ≤ 50 ms visible.** Today's numbers (1.3–1.8 s) already pass.
2. **A batch gate is fast, about 1 h:**
   - **Blocking:** validate_data, taskboard --check, gdlint and gdformat, the tools suite, and the **Godot tests filtered to the areas the batch touches** (run in parallel), plus the boot smoke.
   - **Screenshots:** **only the shots the batch's diff can affect**, meaning the shots the tracks self-rendered plus any whose scene or assets changed. The Lead views every one. Never the full manifest per batch.
   - **Non-blocking, in the background after the merge:** the full Godot suite, Blender for the touched jobs, and a full-manifest capture at most once a day. Any red they find becomes a FAST-TRACK for its owner. It never blocks a merge.
   - **Merge:** when the blocking checks pass, the Lead merges into the integration branch at once and approves the viewed shots. `main` fast-forwards at the same time.
3. **Act I is complete (replaces ADR 0203's criteria) when:**
   - the placeholder audit is at zero;
   - the continuous playthrough passes;
   - the last fast gate is green;
   - the PC's newest pass has no open Act I row that a track can fix;
   - hitches are ≤ 2 s.
   Quality is not lowered: every open row still gets fixed properly.
4. **Act II starts per track, not all at once.** A track starts Act II content (not just docs) as soon as it has **no open Act I row**. Its Act I rows always come first if new ones appear. Ownership rows and briefs from act2_tracks.md apply per track as each one starts. Act III stays paused.

## Amendment (2026-10-30 02:55)
big19's "shots the batch can affect" came to 254: one shared model (Asha's glb) reaches 45 shots. Capturing them blocked the merge for hours again, which is what the human ruled out.
- **Screenshots never block a merge.** The batch merges once its blocking checks pass.
- The affected shots are captured after the merge, in parallel, and the Lead views every one.
- A visual regression found there becomes a FAST-TRACK for its owner.

## Consequences
- A batch takes about an hour instead of half a day.
- Rare visual regressions outside a batch's touched shots are caught by the daily full capture or by the PC's passes, and fixed as FAST-TRACKs.
