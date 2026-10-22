"""Blender entry point for the procedural vegetation (M1-ENV-02, ADR 0005).

    blender --background --factory-startup --python assets_src/environments/vegetation/build.py -- \
        --target palm_coconut_a --out assets/environments/vegetation/palm_coconut_a.glb
    blender --background --factory-startup --python assets_src/environments/vegetation/build.py -- \
        --all --out-dir assets/environments/vegetation [--stats stats.json]

Each target is one .glb holding its LOD meshes as separate objects: `<name>`, `<name>-lod1`, ...
Textures are not embedded (textures.py writes them; the Godot materials reference the PNGs).
Without Blender, `python3 build.py --dry-run --all` builds the geometry and prints the stats only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import beach_vine  # noqa: E402
import frangipani  # noqa: E402
import palm  # noqa: E402
import saltgrass  # noqa: E402
import veg_common as vc  # noqa: E402

SPECIES = {"palm": palm, "frangipani": frangipani, "saltgrass": saltgrass, "beach_vine": beach_vine}


def targets() -> dict:
    """target stem -> (species module, zero-arg builder returning list[MeshBuilder])."""
    out = {}
    for v in sorted(palm.VARIANTS):
        out[f"palm_coconut_{v}"] = (palm, lambda v=v: palm.build(v))
    for v in sorted(frangipani.VARIANTS):
        out[f"frangipani_{v}"] = (frangipani, lambda v=v: frangipani.build(v))
    out["saltgrass_clumps"] = (saltgrass, saltgrass.build)
    out["beach_vine_patch"] = (beach_vine, beach_vine.build)
    return out


def check_budget(module, builders) -> list[str]:
    errs = []
    for mb in builders:
        lod = int(mb.name.rsplit("-lod", 1)[1]) if "-lod" in mb.name else 0
        budget = module.TRI_BUDGET[min(lod, len(module.TRI_BUDGET) - 1)]
        if mb.triangle_count > budget:
            errs.append(f"{mb.name}: {mb.triangle_count} triangles > budget {budget}")
    return errs


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser(description="Build procedural vegetation .glb files")
    ap.add_argument("--target", action="append", help="target stem (repeatable); see --list")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", help="output .glb (single --target)")
    ap.add_argument("--out-dir", default="assets/environments/vegetation")
    ap.add_argument("--stats", help="write triangle/vertex stats JSON here")
    ap.add_argument("--dry-run", action="store_true", help="build geometry only (no Blender needed)")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)
    table = targets()
    if args.list:
        print("\n".join(table))
        return 0
    names = sorted(table) if args.all else (args.target or [])
    if not names:
        ap.error("give --target NAME or --all")
    stats = {}
    errors = []
    for name in names:
        module, fn = table[name]
        builders = fn()
        errors += check_budget(module, builders)
        stats[name] = vc.summary(builders)
        if not args.dry_run:
            out = Path(args.out) if (args.out and len(names) == 1) else Path(args.out_dir) / f"{name}.glb"
            out.parent.mkdir(parents=True, exist_ok=True)
            vc.export_glb(builders, str(out.resolve()))
            stats[name]["_bytes"] = out.stat().st_size
        print(f"VEG {name}: " + ", ".join(f"{k} {v['triangles']} tris" for k, v in stats[name].items()
                                          if not k.startswith("_")))
    if args.stats:
        Path(args.stats).write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n")
    for e in errors:
        print(f"VEG BUDGET FAIL {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    code = main()
    if "bpy" in sys.modules:
        import bpy  # noqa: PLC0415

        if code:
            sys.stderr.write("vegetation build failed\n")
            bpy.ops.wm.quit_blender()
    sys.exit(code)
