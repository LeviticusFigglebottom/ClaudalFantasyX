#!/usr/bin/env python3
"""Lead tool: after VIEWING every sheet, copy a gate's out PNGs over the baselines and write the REAL lavapipe
metadata (compare.py --update-baselines writes "?", which is wrong). Usage, from the batch worktree root:
python3 tools/dev/lead/approve_shots.py <gate-run dir with *_out.png>"""
import glob
import json
import os
import shutil
import sys

REAL = {"adapter": "llvmpipe (LLVM 22.1.8, 256 bits)", "godot": "4.6.3-stable (debian4.6.3+ds-2)",
        "rendering_driver": "vulkan", "rendering_method": "forward_plus"}
B = "tests/screenshots/baselines"
P = B + "/baselines.json"
meta = json.load(open(P))
n = 0
for p in sorted(glob.glob(os.path.join(sys.argv[1], "*_out.png"))):
    sid = os.path.basename(p)[: -len("_out.png")]
    shutil.copy(p, f"{B}/{sid}.png")
    meta[sid] = dict(REAL)
    n += 1
with open(P, "w") as f:
    json.dump({k: meta[k] for k in sorted(meta)}, f, indent=2)
    f.write("\n")
print(n, "shots approved")
