"""Blender entry point for the Corrow seawall procedural kit (M3-ENV-04; corrow.md; ADR 0005).

    blender --background --factory-startup --python assets_src/environments/kits/corrow/build.py -- \
        --all --out-dir assets/environments/kits/corrow --manifest assets/environments/kits/corrow/kit_manifest.json
    blender ... build.py -- --target watcher_head --out /tmp/watcher_head.glb
    python3 assets_src/environments/kits/corrow/build.py --dry-run --all      # geometry + budgets only

Each target is one .glb holding its LOD chain as separate objects (`<name>`, `<name>-lod1`). Geometry is
built with the Haluna kit's core (kit_common.py, imported read-only through cw_common); every material
slot is this kit's own (`cw_*`, written by cw_materials.py). Textures are not embedded.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import b_cargo  # noqa: E402
import b_strand  # noqa: E402
import cw_breach  # noqa: E402
import cw_common as cw  # noqa: E402
import cw_fallen  # noqa: E402
import cw_far  # noqa: E402
import cw_night  # noqa: E402
import cw_stair  # noqa: E402
import cw_story  # noqa: E402
import cw_town  # noqa: E402
import cw_wall  # noqa: E402
import cw_watchers  # noqa: E402

kc = cw.kc
MAX_GLB_BYTES = 5 * 1024 * 1024  # ADR 0005
# cw_breach, cw_fallen: M3-ENV-04B; cw_story: M3-ENV-707; cw_night: M3-ENV-708; b_strand: env-art-b (Ch9's strand);
# b_cargo: env-art-b (the trader's lashed bales, M3-ENV-1326)
MODULES = (cw_wall, cw_watchers, cw_stair, cw_town, cw_far, cw_breach, cw_fallen, cw_story, cw_night, b_strand,
           b_cargo)


def targets() -> dict:
    """target stem -> (budget key, module, zero-arg builder returning list[MeshBuilder])."""
    out = {}
    for module in MODULES:
        keys = getattr(module, "BUDGET_KEY", {})
        for name, fn in sorted(module.TARGETS.items()):
            out[name] = (keys.get(name, name), module, fn)
    return out


def build_target(fn) -> list:
    """Runs a generator and gives every mesh this kit's slots (cw_common.finalize)."""
    return [cw.finalize(mb) for mb in fn()]


def check_budget(module, key: str, builders) -> list[str]:
    errs = []
    budget = module.TRI_BUDGET[key]
    for mb in builders:
        lod = int(mb.name.rsplit("-lod", 1)[1]) if "-lod" in mb.name else 0
        limit = budget[min(lod, len(budget) - 1)]
        if mb.triangle_count > limit:
            errs.append(f"{mb.name}: {mb.triangle_count} triangles > budget {limit}")
    return errs


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser(description="Build the Corrow seawall kit .glb files")
    ap.add_argument("--target", action="append", help="target stem (repeatable); see --list")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", help="output .glb (single --target)")
    ap.add_argument("--out-dir", default="assets/environments/kits/corrow")
    ap.add_argument("--stats", help="write triangle/vertex/byte stats JSON here")
    ap.add_argument("--manifest", help="write the kit manifest (pieces, LODs, budgets)")
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
    unknown = [n for n in names if n not in table]
    if unknown:
        ap.error(f"unknown target(s): {', '.join(unknown)}")
    stats = {}
    errors = []
    for name in names:
        key, module, fn = table[name]
        builders = build_target(fn)
        errors += check_budget(module, key, builders)
        stats[name] = kc.summary(builders)
        if not args.dry_run:
            out = Path(args.out) if (args.out and len(names) == 1) else Path(args.out_dir) / f"{name}.glb"
            out.parent.mkdir(parents=True, exist_ok=True)
            kc.export_glb(builders, str(out.resolve()))
            size = out.stat().st_size
            stats[name]["_bytes"] = size
            if size > MAX_GLB_BYTES:
                errors.append(f"{name}: {size} bytes > {MAX_GLB_BYTES}")
        print(f"KIT {name}: " + ", ".join(f"{k} {v['triangles']} tris" for k, v in stats[name].items()
                                          if not k.startswith("_")))
    if args.stats:
        Path(args.stats).write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n")
    if args.manifest:
        manifest = {
            "schema": "hymn-kit/1",
            "kit": "corrow",
            "generator": "assets_src/environments/kits/corrow/build.py",
            "pieces": {
                n: {
                    "lods": {k: v["triangles"] for k, v in stats[n].items() if not k.startswith("_")},
                    "budget": list(table[n][1].TRI_BUDGET[table[n][0]]),
                    **({"bytes": stats[n]["_bytes"]} if "_bytes" in stats[n] else {}),
                }
                for n in names
            },
        }
        Path(args.manifest).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    for e in errors:
        print(f"KIT BUDGET FAIL {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    code = main()
    if "bpy" in sys.modules:
        import bpy  # noqa: PLC0415

        if code:
            sys.stderr.write("kit build failed\n")
            bpy.ops.wm.quit_blender()
    sys.exit(code)
