#!/bin/bash
# gaterun.sh <ref> <blender-base>: gate.sh with Blender skipped in ci_local, then Blender for the changed jobs.
N=$(basename "$1")
HYMN_SKIP_BLENDER=1 bash /root/gate.sh "$1" "$2" 2 > /root/gate_summary_$N.txt 2>&1
R=/root/gate_$(echo $1 | tr / _)
K=/root/keep_$N; rm -rf $K; mkdir -p $K; cp -r $R $K/run1; cp -r /root/hymn/tests/screenshots/out $K/out
mkdir -p $K/blender; cd /root/hymn
b0=$(date +%s)
HYMN_BLENDER_BASE=$2 HYMN_BLENDER=$HOME/.cache/hymn/blender-5.0.1+dfsg-5/blender \
  python3 tools/dev/verify_blender_builds.py --log-dir $K/blender --report $K/blender/blender_builds.json > $K/blender.log 2>&1
echo "blender exit $? in $(( $(date +%s) - b0 )) s" >> $K/blender.log
echo ALLDONE >> /root/gate_summary_$N.txt
