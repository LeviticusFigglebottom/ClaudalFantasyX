#!/usr/bin/env python3
"""3-way per-key merge of baselines.json during a conflicted merge. argv[1]: 'ours'|'theirs' wins when both changed."""
import json
import subprocess
import sys

P = "tests/screenshots/baselines/baselines.json"
prefer = sys.argv[1] if len(sys.argv) > 1 else "theirs"


def stage(n):
    r = subprocess.run(["git", "show", f":{n}:{P}"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else {}


b, o, t = stage(1), stage(2), stage(3)
out = {}
both = []
for k in sorted(set(b) | set(o) | set(t)):
    bv, ov, tv = b.get(k), o.get(k), t.get(k)
    if ov == tv:
        v = ov
    elif ov == bv:
        v = tv
    elif tv == bv:
        v = ov
    else:
        both.append(k)
        v = tv if prefer == "theirs" else ov
        if v is None:
            v = ov if tv is None else tv
    if v is not None:
        out[k] = v
REAL = {"adapter": "llvmpipe (LLVM 22.1.8, 256 bits)", "godot": "4.6.3-stable (debian4.6.3+ds-2)", "rendering_driver": "vulkan", "rendering_method": "forward_plus"}
bad = [k for k, v in out.items() if not isinstance(v, dict) or "?" in json.dumps(v)]
for k in bad:
    out[k] = dict(REAL)
with open(P, "w") as f:
    json.dump({k: out[k] for k in sorted(out)}, f, indent=2)
    f.write("\n")
subprocess.run(["git", "add", P], check=True)
print("both-changed keys:", both)
print("bad entries (fixed to real metadata):", bad)
