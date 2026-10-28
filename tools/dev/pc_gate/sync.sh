#!/bin/bash
# sync.sh <ref>: updates the WSL clone ($HYMN_WSL_REPO, default /root/hymn) from the Windows checkout
# ($HYMN_WIN_REPO, whose origin/* refs it copies: fetch there first) and checks out <ref>. tools/dev/gate_runner.md.
set -euo pipefail
REPO=${HYMN_WSL_REPO:-/root/hymn}
WIN=${HYMN_WIN_REPO:-/mnt/c/Users/Aaron/hymn_gpu}
if [ ! -d "$REPO/.git" ]; then git init -q "$REPO"; fi
cd "$REPO"
git fetch -q --prune "$WIN" "+refs/remotes/origin/*:refs/remotes/origin/*"
git checkout -q -f --detach "${1:-origin/claude/undertow-lead-handoff-423ixt}"
# Never keep .godot: Godot does not reimport a model when only its post-import script changed, so a kept cache
# fails test_post_import with stale LOD ranges (2026-10-24). A fresh import costs about 30 s.
git clean -qfdx -e .cache
git log --oneline -1
