"""M2-ENV-10: the Shell Shrine's shipped VoxelGI states (assets/levels/ch03/shell_shrine/shrine_gi_*.res,
made by tools/shrine/bake_shrine_gi.tscn) are a function of these inputs. `--write` records their hash next
to the baked data after a rebake; `--check` (and tools/tests/test_shrine_gi_bake.py) fails when an input
changed since, i.e. the shipped lighting is stale.
Run: python3 tools/shrine/gi_inputs.py --write | --check"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SIDECAR = ROOT / "assets/levels/ch03/shell_shrine/shrine_gi_inputs.json"
INPUT_GLOBS = [
    "game/levels/ch03/shell_shrine/*.tscn",
    "game/levels/ch03/shell_shrine/*.tres",
    "game/levels/ch03/shell_shrine/shell_shrine_level.gd",
    "game/data/trials/shell_shrine.json",
    "assets/environments/kits/haluna/shrine_*.glb",
    "assets/environments/kits/haluna/materials/*.tres",
    "tools/shrine/bake_shrine_gi.gd",
]


def inputs() -> list[Path]:
    out: set[Path] = set()
    for g in INPUT_GLOBS:
        out.update(p for p in ROOT.glob(g) if p.is_file())
    return sorted(out)


def digest() -> str:
    h = hashlib.sha256()
    for p in inputs():
        h.update(p.relative_to(ROOT).as_posix().encode())
        h.update(b"\0")
        h.update(p.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()


def main(argv: list[str]) -> int:
    if "--write" in argv:
        SIDECAR.write_text(json.dumps({"inputs_sha256": digest(), "files": len(inputs())}, indent=2) + "\n")
        print(f"gi_inputs: wrote {SIDECAR.relative_to(ROOT)}")
        return 0
    want = json.loads(SIDECAR.read_text())["inputs_sha256"]
    if want != digest():
        print("gi_inputs: the shrine's GI inputs changed since the last bake: rebake (see assets/PROVENANCE.md)")
        return 1
    print("gi_inputs: up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
