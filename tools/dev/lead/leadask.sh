#!/bin/bash
# Lead tool: list every LEAD-ASK line in the tracks' live logs (and the PC's newest gpu/ branch).
# Usage: tools/dev/lead/leadask.sh   (run from the repo root; it fetches first)
# Track branch : live-log name pairs. Edit when the roster changes.
TRACKS="hero-integration:integration-qa characters:characters env-art:env-art env-art-b:env-art-b act1-chapters:act1-chapters creatures:creatures creatures-b:creatures-b battle-presentation:battle-presentation ui:ui-menus audio:audio m2-slice:slice-polish"
git fetch -q origin 2>/dev/null
for p in $TRACKS; do
  b=${p%%:*}; f=${p##*:}
  git show "origin/claude/$b:docs/kb/handoffs/live/$f.md" 2>/dev/null | grep -n 'LEAD-ASK:' | sed "s/^/[$f] /"
done
# The cloud gate session (from 2026-10-29) logs to gate.md on its newest lead/gate-big* branch.
gb=$(git branch -r --sort=-committerdate | grep -E 'origin/lead/gate-big[0-9]+$' | head -1 | tr -d ' ')
[ -n "$gb" ] && git show "$gb:docs/kb/handoffs/live/gate.md" 2>/dev/null | grep -n -E 'LEAD-ASK:|GATE-BUILT|GATE-DONE' | sed 's/^/[gate] /'
g=$(git branch -r --sort=-committerdate | grep 'origin/gpu/' | head -1 | tr -d ' ')
[ -n "$g" ] && git show "$g:docs/kb/handoffs/live/pc-gpu.md" 2>/dev/null | grep -n 'LEAD-ASK:' | sed 's/^/[pc-gpu] /'
