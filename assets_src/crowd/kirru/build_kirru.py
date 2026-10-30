"""A Kirru crowd body (the Lead, 2026-10-30: Reedhollow's clutch). Headless Blender 5.0:

    blender --background --factory-startup --threads 4 --python assets_src/crowd/kirru/build_kirru.py -- \\
        --body kirru_man --bake-dir DIR

Pell's build (assets_src/characters/pell/build_pell.py, imported as a library: the MPFB2 hero path with the Kirru head
warp, fur, crest, whiskers, mantle, name-shell and staff) run on Pell's pell_params.json with the body's overrides
from kirru_bodies.json deep-merged on top (kirru_params). The full build goes to the bake dir; only its LOD1 ships, as
assets/crowd/<id>/<id>.glb (the crowd bodies are LOD1 builds, as the villager crowd's are). Deterministic: the merged
params are written in a fixed order and build_pell keeps its own host-determinism steps.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "pell"))

import kirru_params  # noqa: E402


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_kirru.py")
    ap.add_argument("--body", required=True)
    ap.add_argument("--bake-dir", required=True)
    args = ap.parse_args(argv)
    bake = Path(args.bake_dir)
    bake.mkdir(parents=True, exist_ok=True)
    params = kirru_params.write_params(args.body, bake)
    import build_pell as bp  # after the params exist: the module reads PARAMS only in main()

    bp.PARAMS = params
    full = bake / f"{args.body}_full.glb"
    sys.argv = [sys.argv[0], "--", "--out", str(full), "--bake-dir", str(bake), "--report", str(bake / "report.json")]
    rc = bp.main()
    if rc:
        return rc
    out = kirru_params.asset_dir(args.body) / f"{args.body}.glb"
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bake / f"{args.body}_full_lod1.glb", out)
    print(f"[kirru] {args.body}: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
