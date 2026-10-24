---
id: M2-NIT-04
title: capture.sh logs the non-zero exit line in shared mode too (review-sweep-R on M1-QA-10)
role: qa
status: doing
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
- [ ] Shared mode also writes `CAPTURE PROCESS EXIT <rc>: <shot list>` to the log.
- [ ] A small test in `tools/tests/` runs capture.sh against a stub renderer that exits non-zero, in both modes,
      and checks the log line, the closing list and the exit code.

## Notes
- Source: review-sweep-R (2026-10-24).

## Review log
