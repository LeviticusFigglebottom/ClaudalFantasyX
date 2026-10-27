# 0039 — Git LFS is enabled for large binaries (supersedes ADR 0005 item 7)

- **Status:** accepted (the human approved it, 2026-10-27). Activation waits on the cloud network allowing `lfs.github.com`.
- **Date:** 2026-10-27
- **Roles affected:** all (audio first), lead, tech
- **Author role:** lead

## Context
ADR 0005 deferred Git LFS: the proxy was unverified, and quota is the human's call. ADR 0171 raised the shipped-audio budget to 72 MiB to finish Act I in plain git, and noted that Act II's final cues need a storage decision first. The human approved Git LFS on 2026-10-27.

The Lead probed LFS from a cloud session (staging branch `lead/gate-lfs-probe`, since deleted):
- the LFS batch API on github.com works;
- the object upload to GitHub's storage (S3) works;
- the final `verify` call to `https://lfs.github.com/...` is refused by the cloud environment's egress proxy (CONNECT 403), so the push fails.

Cloud containers also set `filter.lfs.smudge = git-lfs smudge --skip` globally, so a checkout there holds pointer files until it runs `git lfs pull`. The PC (Windows and WSL) has direct internet and full credentials.

## Options
1. Track every binary type in `.gitattributes` and run `git lfs migrate import` over history. That rewrites history every branch depends on (CLAUDE.md §8 forbids it), and it moves screenshot baselines out of reach of plain-git diffs.
2. Track LFS by path, for **new** large content only. Existing blobs stay plain; there is no history rewrite.
3. Keep plain git and render large audio at build time (ADR 0172, proposed by audio).

## Decision
Option 2.
- **What goes in LFS** (`.gitattributes`, added once activation is possible):
  - `assets/audio/music/act2/**`, `assets/audio/music/act3/**` and later acts' final cues;
  - any new binary asset over **5 MB** (the validator keeps failing a plain blob over 5 MB, and its message now points here).
- **What stays plain git:** screenshot baselines (always), code, data, and every existing asset. History is never migrated.
- **Pushing LFS content:**
  - from cloud sessions, only once `lfs.github.com` is allowed in the environment's network settings;
  - until then, LFS commits are pushed from the PC (`pc-gpu`), which already does all rendering.
- **Reading LFS content:** every cloud session that needs it runs `git lfs pull --include=<paths>` after checkout, because smudge is skipped by default there. Gates (the PC runner, `ci_local.sh`) run `git lfs pull` before import.
- ADR 0172's build-time render stays a fallback study, not the plan.

## Consequences
- Act II and later final audio can land without bloating the plain-git history.
- **Quota:** GitHub LFS storage and bandwidth count against the owner's account. The audio total is about 72 MiB today, so the free tier's 1 GiB covers several acts, but every clone that pulls LFS uses bandwidth. Pull with `--include` to limit it.
- **Watch:** a cloud session that forgets `git lfs pull` imports pointer files, and Godot's import then fails on them. `tools/validate_data.py` should flag an LFS pointer under `assets/` that isn't in the working tree (follow-up task for tech).
