# 0001 — Engine version: Godot 4.6.3-stable

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** all
- **Author role:** Lead

## Context
SPEC §4.1 asks for the "latest stable" Godot 4.x, pinned in this KB and in CI. At bootstrap, the most recent stable release confirmed on the official Godot blog was **4.6.3** (a maintenance release, May 2026). A third-party mirror also lists 4.7.x builds, but we could not confirm from an official source that 4.7 is stable. The bootstrap container could not reach godotengine.org or GitHub releases to check directly.

## Options
1. Pin 4.6.3-stable, the newest version confirmed stable.
2. Pin 4.7.x on the strength of the mirror listing.

## Decision
Pin **Godot 4.6.3-stable**. Set `config/features` in `project.godot` to `"4.6"`, `GODOT_RELEASE` in `.github/workflows/ci.yml` to `4.6.3-stable`, and record the version in `docs/kb/tech/engine.md`.

## Consequences
- We rely on 4.5+ features that exist in 4.6: the `Logger` class (used by the test runner) and typed dictionaries if we need them.
- **Follow-up (M1-ARC-04):** the first agent with network access to godotengine.org should check whether 4.7 is officially stable. If it is, write an ADR that supersedes this one before M1 content work grows, because upgrading gets more expensive over time. Never upgrade mid-milestone without an ADR.
