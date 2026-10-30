"""Merges tools/creatures/wildlife_snap.gd's output back into the committed wildlife files, keeping integers (Godot's
JSON writes every number as a float) and the files' 2-space layout.
python3 tools/creatures/wildlife_apply.py <snap output dir>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WILDLIFE = ROOT / "game" / "data" / "world" / "wildlife"


def merged(old, new):
    if isinstance(old, dict) and isinstance(new, dict):
        return {k: merged(old[k], new[k]) if k in old else new[k] for k in new}
    if isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
        return [merged(a, b) for a, b in zip(old, new)]
    if isinstance(old, int) and not isinstance(old, bool) and isinstance(new, float) and new.is_integer():
        return int(new)
    return new


def main(out_dir: str) -> None:
    for snapped in sorted(Path(out_dir).glob("*.json")):
        target = WILDLIFE / snapped.name
        old = json.loads(target.read_text(encoding="utf-8"))
        new = merged(old, json.loads(snapped.read_text(encoding="utf-8")))
        if new != old:
            target.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"updated {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1])
