"""Blender entry point for the Tamsule Bell kit (M3-ENV-01; docs/kb/art/environments/tamsule_bell.md).

    blender --background --factory-startup --python assets_src/environments/kits/tamsule_bell/build.py -- \
        --all --out-dir assets/environments/kits/tamsule_bell [--manifest .../kit_manifest.json]
    blender ... build.py -- --target tamsule_bell --out /tmp/tamsule_bell.glb
    python3 assets_src/environments/kits/tamsule_bell/build.py --dry-run --all      # geometry + budgets only

The same contract as the Haluna kit (whose kit_common.py this kit imports read-only): each target is one
.glb holding `<name>` and `<name>-lod1`; textures are not embedded (the materials reference the Haluna
kit's texture set); pieces in PLACEHOLDERS carry glTF node extras {"placeholder": "PLACEHOLDER: ..."}
and the manifest repeats the tag. Ring pieces have their origin on the arena axis (tamsule_bell.md §0).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import b_column  # noqa: E402  (env-art-b, M3-ENV-1321)
import bell  # noqa: E402
import gallery  # noqa: E402
import gantry  # noqa: E402
import market  # noqa: E402
import port  # noqa: E402
import tb_common as tb  # noqa: E402
import waterline  # noqa: E402

kc = tb.kc
MAX_GLB_BYTES = 5 * 1024 * 1024  # ADR 0005
MODULES = (bell, gantry, gallery, waterline, port, market,  # market: M3-C07-04 the port
           b_column)  # env-art-b, M3-ENV-1321


def targets() -> dict:
    """target stem -> (budget key, module, zero-arg builder returning list[MeshBuilder])."""
    out = {}
    for module in MODULES:
        keys = getattr(module, "BUDGET_KEY", {})
        for name, fn in sorted(module.TARGETS.items()):
            out[name] = (keys.get(name, name), module, fn)
    return dict(sorted(out.items()))


PLACEHOLDERS = dict(bell.PLACEHOLDER_REASONS)


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
    ap = argparse.ArgumentParser(description="Build the Tamsule Bell kit .glb files")
    ap.add_argument("--target", action="append", help="target stem (repeatable); see --list")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", help="output .glb (single --target)")
    ap.add_argument("--out-dir", default="assets/environments/kits/tamsule_bell")
    ap.add_argument("--stats", help="write triangle/vertex/byte stats JSON here")
    ap.add_argument("--manifest", help="write the kit manifest (pieces, LODs, budgets, placeholder tags)")
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
        builders = fn()
        errors += check_budget(module, key, builders)
        stats[name] = kc.summary(builders)
        extras = {"placeholder": f"PLACEHOLDER: {PLACEHOLDERS[name]}"} if name in PLACEHOLDERS else None
        if not args.dry_run:
            out = Path(args.out) if (args.out and len(names) == 1) else Path(args.out_dir) / f"{name}.glb"
            out.parent.mkdir(parents=True, exist_ok=True)
            kc.export_glb(builders, str(out.resolve()), extras)
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
            "kit": "tamsule_bell",
            "generator": "assets_src/environments/kits/tamsule_bell/build.py",
            "drop_contract": {
                "anchor": list(bell.DROP_CENTER),
                "radius_h_m": bell.DROP_RADIUS_H,
                "radius_v_m": bell.DROP_RADIUS_V,
                "weep_point_y": bell.DROP_BOTTOM_Y,
                "surface_y": bell.DROP_TOP_Y,
                "min_clearance_m": bell.MIN_CLEARANCE_M,
            },
            "pieces": {
                n: {
                    "lods": {k: v["triangles"] for k, v in stats[n].items() if not k.startswith("_")},
                    "budget": list(table[n][1].TRI_BUDGET[table[n][0]]),
                    **({"bytes": stats[n]["_bytes"]} if "_bytes" in stats[n] else {}),
                    **({"tags": ["PLACEHOLDER"], "placeholder": PLACEHOLDERS[n]} if n in PLACEHOLDERS else {}),
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
