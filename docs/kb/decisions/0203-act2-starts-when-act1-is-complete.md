# 0203 — Act II starts the moment Act I is complete

- **Status:** accepted (the human's directive, 2026-10-30: "get everything ready to move on to act 2 once act 1 is fully complete")
- **Date:** 2026-10-30
- **Roles affected:** all
- **Author role:** lead
- **Supersedes:** ADR 0041 §2 (the pause) and §5, **from the moment the gate below passes**. Until then ADR 0041 stands unchanged.

## Context
ADR 0041 paused Act II and later until Act I reached final quality, and said the pause lifts when the human says so. The human has now said so, conditionally: move on to Act II once Act I is fully complete. That condition needs to be exact, so no track starts Act II early and none waits after Act I is done.

## Decision
### The Act I completion gate (all must hold, on one integration commit)
1. **Audit:** `tools/placeholder_audit.py` reports **zero** items for the title through Ch9 (ADR 0041 §4).
2. **Playthrough:** a full headless New Game → Ch9 → credits → title playthrough passes, with the continuous flow (M3-CIN-1233): every chapter thread, every encounter entry, and save and load at every save point. Zero SCRIPT ERRORs.
3. **Batch gate:** the batch carrying that commit is fully green. That means:
   - the Godot suite has no reds outside a listed known-red set, and that set holds no Act I bug;
   - coverage is OK;
   - Blender is identical;
   - every drifted shot has been viewed and approved by the Lead.
   `main` is fast-forwarded to it (ADR 0042 §5).
4. **Real GPU:** the PC's newest Act I QA pass (`act1_gpu_qa.md`) has no open row owned by an Act I track, except rows only the human can judge (listening and taste).
5. **Hitches:** Act I scene changes are ≤ 1 s of hidden frames and ≤ 50 ms visible on the PC (ADR 0042 §4).

The Lead records the commit and the evidence in `docs/kb/qa/act1_complete.md` and tags the commit `act1-complete`. Act II then starts at once, with no further sign-off.

### What happens at the gate
- ADR 0041's pause is lifted for **Act II** (Ch10 onward through the end of Act II, SPEC §3 and milestone M4). Act III stays paused until Act II passes the same gate. That applies the same rule one act at a time.
- The Act II plan (`docs/kb/plan/act2_plan.md`, prepared beforehand) becomes the work list. Its ADR-0041-blocked tasks move from `blocked` to `todo`.
- **Act I stays protected:** an Act I regression found later is a FAST-TRACK, and no Act II change may break an Act I test or shot without the owner's fix in the same batch.
- **The human's playtest of Act I is not a gate,** but every note from it is a FAST-TRACK ahead of Act II work (ADR 0042 §1).

### Preparation now (allowed under ADR 0041, docs and tools only)
- **A planning session** writes the Act II plan: chapters, zones, cast, enemies, bosses, Vowbound, set pieces (the wedding trap, the heresy, Kerrid's reveal, the Drowned Choir), music, menus, the existing Act II work on branches and its state, a per-role task list, the track split, ownership globs, and SESSION-BRIEFS rows.
  - It changes no game content, scene or asset.
- **integration-qa** extends `placeholder_audit.py` with a `--act 2` scope, report-only, so the Act II inventory exists on day one.

## Consequences
- No idle gap between Act I and Act II, and no early start.
- Act I's bar becomes the standing bar for every later act.
