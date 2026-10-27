#!/bin/bash
# render_batch.sh <queue-file>: answer track RENDER-REQUESTs on lavapipe in WSL (TRACK-RULES "RENDERING GOES TO THE PC").
# Each queue line: <track> <sha> <comma-separated ids>. Per request: sync to <sha> (fresh .godot), import, capture the
# ids in 2 shards (LP_NUM_THREADS=3), compare those ids. Results: /root/renders/<track>-<sha7>/{out,diff,compare.txt}.
set -u
import_ok() {  # Godot 4.6.3's --import sometimes aborts (double free); retry up to 3 times on a fresh .godot
  local log=$1 n
  for n in 1 2 3; do
    rm -rf .godot; "$G4bin" --headless --path . --import > "$log" 2>&1
    grep -qE "double free|Aborted|core dumped|Segmentation" "$log" || return 0
    echo "import crashed (try $n)" >> "$log.retries"
  done; return 1
}
Q=$1
G4=$HOME/.cache/hymn/godot-4.6.3+ds-2/godot
while read -r track sha ids; do
  [ -z "$track" ] && continue
  s7=${sha:0:7}; D=/root/renders/$track-$s7
  if [ -f $D/compare.txt ]; then echo "skip $track $s7 (done)"; continue; fi
  rm -rf $D; mkdir -p $D/out $D/diff; t0=$(date +%s)
  bash /root/sync.sh "$sha" > $D/sync.log 2>&1
  cd /root/hymn
  G4bin=$G4; import_ok $D/import.log || echo "IMPORT FAILED 3x" >> $D/import.log
  rm -rf tests/screenshots/out
  # 2 shards over the requested ids, in the manifest's order.
  python3 - "$ids" <<'PY' > $D/shards.txt
import json, sys
want = set(sys.argv[1].split(","))
ids = [s["id"] for s in json.load(open("tests/screenshots/shots.json"))["shots"] if s["id"] in want]
missing = sorted(want - set(ids))
if missing: print("#missing " + ",".join(missing))
for k in range(2):
    part = ids[k::2]
    if part: print(",".join(part))
PY
  k=0; pids=()
  while read -r list; do
    case "$list" in \#*) continue ;; esac
    mkdir -p $D/shard_$k
    ( export TMPDIR=$D/shard_$k LP_NUM_THREADS=3; tools/screenshots/capture.sh --shots "$list" > $D/shard_$k/out.txt 2>&1; echo "exit $?" >> $D/shard_$k/out.txt ) &
    pids+=($!); k=$((k+1))
  done < $D/shards.txt
  for p in "${pids[@]}"; do wait $p; done
  python3 tools/screenshots/compare.py --shots "$ids" > $D/compare.txt 2>&1; echo "compare exit $?" >> $D/compare.txt
  grep "^#missing" $D/shards.txt >> $D/compare.txt
  cp tests/screenshots/out/*.png $D/out/ 2>/dev/null; cp tests/screenshots/out/diff/*.png $D/diff/ 2>/dev/null
  echo "$track $s7 done in $(( $(date +%s) - t0 )) s: $(grep -c '^PASS' $D/compare.txt) pass, $(grep -c '^FAIL' $D/compare.txt) fail" | tee -a /root/renders/batch.log
  cd /root
done < "$Q"
echo BATCHDONE >> /root/renders/batch.log
