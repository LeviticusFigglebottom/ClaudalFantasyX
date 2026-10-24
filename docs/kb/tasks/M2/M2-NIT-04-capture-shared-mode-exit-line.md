---
id: M2-NIT-04
title: capture.sh logs the non-zero exit line in shared mode too (review-sweep-R on M1-QA-10)
role: qa
status: review
owner_session: "worktree-agent-a23fdd18373ec5031"
reviewer: lead
depends_on: [M1-QA-10]
milestone: M2
request-from: "lead"
---
## Goal
M1-QA-10 made `tools/screenshots/capture.sh` name the shot whose Godot process exited non-zero. In per-shot mode it
writes `CAPTURE PROCESS EXIT <rc>: <id>` to the log. In `HYMN_CAPTURE_SHARED=1` mode it only adds to the closing
list and writes no log line. So a gate that greps the log for the signature that docs/kb/qa/screenshots.md
("Engine race") describes misses it in shared mode.

## Acceptance criteria
- [x] Shared mode also writes `CAPTURE PROCESS EXIT <rc>: <shot list>` to the log.
- [x] A small test in `tools/tests/` runs capture.sh against a stub renderer that exits non-zero, in both modes,
      and checks the log line, the closing list and the exit code.

## Notes
- Source: review-sweep-R (2026-10-24).

### Notes (worktree-agent-a23fdd18373ec5031, 2026-10-24)
- `tools/screenshots/capture.sh`: shared mode now writes `CAPTURE PROCESS EXIT <rc>: <shot list>` to the log, the
  same signature as per-shot mode, so the closing grep echoes it and a log-grepping gate sees it.
- `tools/tests/test_capture_sh.py` (3): a stub renderer (`HYMN_GODOT_RENDER`, `TMPDIR` for the log) exits 134 for
  one shot; per-shot and shared mode each check the log line, the closing "exited non-zero" list and the exit code;
  a clean run writes no exit line in either mode.
- docs/kb/qa/screenshots.md ("Engine race") names the shared-mode form.

## Review log
