# 0008 — Local CI gate while GitHub Actions cannot run; Godot from the Ubuntu archive in the sandbox

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** all
- **Author role:** Lead

## Context
The first three CI runs on this repo stayed `queued` for over 35 minutes and never got a runner. Actions may be disabled, or the account may have no minutes. The human can't currently see the repo's Actions or billing settings. The cloud sandbox also can't reach GitHub releases or godotengine.org, so it can't download the official engine build. "main is always green" (CLAUDE.md §8) needs *some* enforceable gate.

## Options
1. Stop merging until Actions runs.
2. Run the same gates locally, with a Godot binary obtained from a reachable source.

## Decision
- `tools/ci_local.sh` runs every CI gate (validators, tool tests, task board, gdlint/gdformat, screenshot stub, Godot import, Godot tests, and a boot-scene smoke test). **It is the merge gate whenever Actions is not running.** Each merge commit message states `ci_local: pass`.
- In the cloud sandbox, `python3 tools/dev/fetch_godot.py` fetches Ubuntu's `godot 4.6.3+ds-2` package with its full dependency closure into a private sysroot (`~/.cache/hymn/`), and runs it through that sysroot's loader. Same engine version as ADR 0001, distro build.
- `.github/workflows/ci.yml` stays as-is. When Actions starts running again, its result wins over the local gate.

## Consequences
- The distro build vendors some third-party libraries differently. Any behaviour difference from the official build is a bug to report in `docs/kb/tech/engine.md`.
- Local runs are only as honest as the agent running them, so reviewers re-run `tools/ci_local.sh` on the merged head.
- Superseded once Actions runs reliably (write a new ADR that says so).
