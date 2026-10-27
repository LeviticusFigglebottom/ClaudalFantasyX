#!/bin/bash
# gate.sh <ref> <blender-base> [shards]: a full Lead gate in WSL (tools/dev/gate_runner.md). Lane A: ci_local.sh
# with its screenshot step skipped (Blender for the jobs changed since <blender-base>, required); lane B: the whole
# screenshot manifest in parallel shards (LP_NUM_THREADS=3 each: llvmpipe's output doesn't depend on it), then one
# compare. Both lanes run at once; HYMN_GATE_LANES=A or B runs one. No venv: Blender honours VIRTUAL_ENV and then
# can't import its own numpy, so tools/requirements.txt (and Pillow) go into the distro's Python. Results under $HYMN_GATE_DIR/gate_<ref>/ (default /root).
set -u
import_ok() {  # Godot 4.6.3's --import sometimes aborts (double free); retry up to 3 times on a fresh .godot
  local log=$1 n
  for n in 1 2 3; do
    rm -rf .godot; "$G4bin" --headless --path . --import > "$log" 2>&1; local rc=$?
    # A SIGABRT can leave nothing in the log (the shell prints "Aborted", not Godot): trust the exit code
    # and the editor-layout DONE line that a finished import prints, not only the log's crash text.
    if [ $rc -eq 0 ] && grep -q "DONE.*loading_editor_layout" "$log"       && ! grep -qE "double free|Aborted|core dumped|Segmentation" "$log"; then return 0; fi
    echo "import crashed (try $n, exit $rc)" >> "$log.retries"
  done; return 1
}
ref=$1; base=$2; shards=${3:-3}
name=$(echo "$ref" | tr '/' '_')
HERE=$(cd "$(dirname "$0")" && pwd)
bash "$HERE/sync.sh" "$ref" > /dev/null
cd "${HYMN_WSL_REPO:-/root/hymn}"
sha=$(git rev-parse --short HEAD)
R=${HYMN_GATE_DIR:-/root}/gate_$name; rm -rf $R; mkdir -p $R
t0=$(date +%s)
G4=$HOME/.cache/hymn/godot-4.6.3+ds-2
# Import once up front so both lanes start on a warm .godot/.
G4bin=$G4/godot; import_ok $R/import0.log || echo "IMPORT FAILED 3x" >> $R/import0.log
lanes=${HYMN_GATE_LANES:-AB}
pa=""; pb=""
[[ $lanes == *A* ]] && (
  export GODOT=$G4/godot HYMN_GODOT_RENDER=/nonexistent HYMN_LOG_DIR=$R/ci HYMN_BLENDER_BASE=$base HYMN_BLENDER_REQUIRED=1
  export HYMN_BLENDER=$HOME/.cache/hymn/blender-5.0.1+dfsg-5/blender HYMN_STEP_TIMEOUT=2400
  mkdir -p $R/ci; a0=$(date +%s)
  bash tools/ci_local.sh > $R/laneA.log 2>&1; echo "laneA exit $? in $(( $(date +%s) - a0 )) s" >> $R/laneA.log
) &
[[ $lanes == *A* ]] && pa=$!
[[ $lanes == *B* ]] && (
  b0=$(date +%s)
  rm -rf tests/screenshots/out
  python3 - "$shards" <<'PY' > $R/shards.txt
import json, sys
ids = [s["id"] for s in json.load(open("tests/screenshots/shots.json"))["shots"]]
n = int(sys.argv[1])
for k in range(n):
    print(",".join(ids[k::n]))
PY
  k=0; pids=()
  while read -r list; do
    mkdir -p $R/shard_$k
    ( export TMPDIR=$R/shard_$k LP_NUM_THREADS=3; tools/screenshots/capture.sh --shots "$list" > $R/shard_$k/out.txt 2>&1; echo "exit $?" >> $R/shard_$k/out.txt ) &
    pids+=($!); k=$((k+1))
  done < $R/shards.txt
  rc=0; for p in "${pids[@]}"; do wait $p || rc=1; done
  grep -h "^exit\|SCRIPT ERROR\|CAPTURE PROCESS EXIT" $R/shard_*/out.txt | sort | uniq -c > $R/laneB_capture.txt
  python3 tools/screenshots/compare.py > $R/compare.txt 2>&1; echo "compare exit $?" >> $R/compare.txt
  echo "laneB in $(( $(date +%s) - b0 )) s" >> $R/compare.txt
) &
[[ $lanes == *B* ]] && pb=$!
[ -n "$pa" ] && wait $pa; [ -n "$pb" ] && wait $pb
echo "GATE $ref@$sha wall $(( $(date +%s) - t0 )) s"
grep -E "^== |Tests:|coverage step|blender step|identical|DIFF|SKIP|All local|laneA exit|FAIL" $R/laneA.log | tail -40
[ -f $R/compare.txt ] && { cat $R/laneB_capture.txt; grep -v "^PASS" $R/compare.txt | tail -8; }
