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
git clean -qfdx -e .godot -e .cache
git log --oneline -1
