---
id: M1-UI-09
title: Toast when the chapter autosave keeps a further-along journey
role: ui
status: done
owner_session: "worktree-agent-aa764c62452184711"
depends_on: [M1-ARC-08]
milestone: M1
reviewer: architect
request-from: "architect"
---
## Goal
ADR 0018 Amendment 1 skips the chapter autosave when slot 0 holds a journey further along than the
live run (`EventBus.autosave_finished(reason, ERR_ALREADY_EXISTS)`). Today that is only a log
warning, so the player is not told that this boundary was not autosaved (pillar 4). QA asked for a
UI task in M1-ARC-08 review-sweep-F.

## Acceptance criteria
- [x] On `autosave_finished` with `ERR_ALREADY_EXISTS`, a short non-blocking toast says the autosave
      keeps a journey further along and that shrine records still save this one (new loc key,
      appended to the UI's loc file)
- [x] It never shows for `OK`, for `ERR_UNAVAILABLE` (autosave off), or during a cutscene hold
- [x] Test: emit the signal with each error and check when the toast appears

## Notes
Wording is UI and Narrative's call. Filed from M1-ARC-11 (architect); see ADR 0018 Amendment 2.

- 2026-10-23 ui (worktree-agent-aa764c62452184711), to review (architect):
  - `AutosaveToast` (game/ui/toast/autosave_toast.gd), a CanvasLayer that boot.gd installs under the tree root
    (deferred), so it outlives the title and zone changes. It listens on `EventBus.autosave_finished` and shows
    only for `ERR_ALREADY_EXISTS`: a top-right panel, fade 0.18 s, hold 4.5 s, fade 0.6 s
    (game/data/ui/toast.json), mouse-transparent, `PROCESS_MODE_ALWAYS`.
  - While `SaveSystem.autosave_holders()` is non-empty (a cutscene sequencer, the camera director) the notice waits
    and shows once the hold is released. (The skip is only emitted at a safe point today, so this guards future
    direct callers.)
  - Text: `AUTOSAVE_SKIPPED_TOAST` appended to game/data/loc/strings.csv: "The autosave still holds a journey
    further along, so it was kept. Rest at a shrine to record this one." Narrative may want to reword it.
  - tests/unit/test_autosave_toast.gd (7 tests: each error, the hold, the fade, input, the real EventBus, install).
  - boot.gd's change sits at the end of `_ready` plus one new function, away from M1-ARC-15's boot.gd hunk.

## Review log
- 2026-10-23 architect (review-sweep-L, fresh reviewer): **approve.** No blockers.
  - **What I read:** `git show` ac901e7 and 28a2f8e: autosave_toast.gd, toast.json, the boot.gd hunk and the loc row (strings.csv:456).
  - **Checks:** Godot `--filter=autosave_toast` 7/0 failed and `--filter=save` 168/0.
  - **Criteria met:**
    - It shows for `ERR_ALREADY_EXISTS` only (:104-106).
    - A hold defers it to pending, and it shows once released (:78-80, :107-110).
    - It is `PROCESS_MODE_ALWAYS` and mouse-transparent.
    - It is installed once under root, deferred.
    - Timings are data, and the loc key is appended.
    - The project stretch is `canvas_items`, so the 1920×1080 reference rect scales.
  - **Nits:**
    - `tr()` runs once at `_show` (:115), so a language change during the 5.3 s notice keeps the old text. Harmless.
    - A second skip during the notice restarts the fade-in from 0 (:114-118), so the panel blinks. Keep the alpha if it is already showing.
    - Narrative should confirm the wording ("still holds a journey further along"), as the task says.
- 2026-10-23 lead: closing on review-sweep-L approve; the should-fixes are in M1-NIT-02.
