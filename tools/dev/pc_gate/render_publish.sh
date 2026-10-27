#!/bin/bash
# render_publish.sh <track> <sha>: push a finished WSL render (/root/renders/<track>-<sha7>) to gpu/render-<track>-<sha7>,
# based on <sha>, under docs/kb/qa/renders/<track>-<sha7>/: out + diff PNGs of every shot that isn't PASS, compare.txt.
# Prints the RENDERED line. Run in Git Bash; uses the worktree C:/Users/Aaron/hymn_render.
set -eu
track=$1; sha=$2; s7=${sha:0:7}
W=/c/Users/Aaron/hymn_render; SRC=//wsl.localhost/hymn/root/renders/$track-$s7
br=gpu/render-$track-$s7; D=docs/kb/qa/renders/$track-$s7
[ -d $W ] || git -C /c/Users/Aaron/hymn_gpu worktree add -q --detach C:/Users/Aaron/hymn_render "$sha"
cd $W
git checkout -q -f --detach "$sha"
git switch -q -C "$br"
mkdir -p $D
cp "$SRC/compare.txt" $D/compare.txt
for id in $(sed -n 's/^FAIL \([^:]*\):.*/\1/p' $D/compare.txt); do
  [ -f "$SRC/out/$id.png" ] && cp "$SRC/out/$id.png" $D/${id}_out.png
  [ -f "$SRC/diff/$id.png" ] && cp "$SRC/diff/$id.png" $D/${id}_diff.png
done
npass=$(grep -c '^PASS' $D/compare.txt || true); ndrift=$(grep -c '^FAIL' $D/compare.txt || true)
echo "$track $sha $npass $ndrift"
# The RENDERED line goes into the running pc-gpu.md copy ($HYMN_PC_GPU_MD), which this branch carries.
P=${HYMN_PC_GPU_MD:-$HOME/hymn_pc_gpu.md}  # the running copy; seed it from the newest gpu/* branch
miss=$(sed -n 's/^#missing //p' $D/compare.txt)
line="- RENDERED @ $sha: $br; $npass pass, $ndrift drift${miss:+ (not in shots.json at this sha: $miss)}"
python - "$P" "$line" "$br" <<'PY'
import sys
p, line, br = sys.argv[1:]
s = open(p, encoding="utf-8", newline="").read()
s = s.replace("(none yet)\n", "", 1)
h = "## Renders for the tracks (RENDERED lines, newest first)\n\n"
s = s.replace(h, h + line + "\n", 1)
import re
s = re.sub(r"\*\*This copy, on `[^`]+`, is the newest.\*\*", f"**This copy, on `{br}`, is the newest.**", s)
open(p, "w", encoding="utf-8", newline="").write(s)
PY
mkdir -p docs/kb/handoffs/live; cp "$P" docs/kb/handoffs/live/pc-gpu.md
git add -A docs/kb/qa/renders docs/kb/handoffs/live/pc-gpu.md
git commit -q -F - <<MSG
RENDERED @ $s7 for $track: $npass pass, $ndrift drift (PC lavapipe, WSL2)

Out and diff PNGs of every shot that isn't PASS, plus compare.txt, under $D.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01DKdurcvrzq9PEvuSu5L2nA
MSG
git push -q -u origin "$br" 2>&1 | tail -1
echo "$line"
