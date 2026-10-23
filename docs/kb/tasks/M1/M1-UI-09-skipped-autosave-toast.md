---
id: M1-UI-09
title: Toast when the chapter autosave keeps a further-along journey
role: ui
status: doing
owner_session: "worktree-agent-aa764c62452184711"
depends_on: [M1-ARC-08]
milestone: M1
request-from: "architect"
---
## Goal
ADR 0018 Amendment 1 skips the chapter autosave when slot 0 holds a journey further along than the
live run (`EventBus.autosave_finished(reason, ERR_ALREADY_EXISTS)`). Today that is only a log
warning, so the player is not told that this boundary was not autosaved (pillar 4). QA asked for a
UI task in M1-ARC-08 review-sweep-F.

## Acceptance criteria
- [ ] On `autosave_finished` with `ERR_ALREADY_EXISTS`, a short non-blocking toast says the autosave
      keeps a journey further along and that shrine records still save this one (new loc key,
      appended to the UI's loc file)
- [ ] It never shows for `OK`, for `ERR_UNAVAILABLE` (autosave off), or during a cutscene hold
- [ ] Test: emit the signal with each error and check when the toast appears

## Notes
Wording is UI and Narrative's call. Filed from M1-ARC-11 (architect); see ADR 0018 Amendment 2.

## Review log
