"""Blender entry point for the Haluna procedural kit (M1-ENV-01, SPEC §7.4, ADR 0005).

    blender --background --factory-startup --python assets_src/environments/kits/haluna/build.py -- \
        --all --out-dir assets/environments/kits/haluna [--stats stats.json]
    blender ... build.py -- --target ruin_column_broken --out /tmp/ruin_column_broken.glb
    python3 assets_src/environments/kits/haluna/build.py --dry-run --all      # geometry + budgets only

Each target is one .glb holding its LOD meshes as separate objects (`<name>`, `<name>-lod1`).
Textures are not embedded (kit_textures.py writes them; the Godot materials reference the PNGs).
Pieces listed in PLACEHOLDERS carry glTF node extras {"placeholder": "<reason>"}, which Godot imports
as node metadata; the SPEC §8.4 "no visible placeholders" check greps for the PLACEHOLDER tag
(assets/environments/kits/haluna/kit_manifest.json repeats it per piece).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import arenas  # noqa: E402
import causeway  # noqa: E402
import causeway_zone  # noqa: E402
import dressing  # noqa: E402
import festival  # noqa: E402
import iskarra  # noqa: E402
import keth  # noqa: E402
import lowlight  # noqa: E402
import ossa_fen  # noqa: E402
import save_shrine  # noqa: E402
import bridal_barge  # noqa: E402
import ansedra  # noqa: E402
import drowned_choir  # noqa: E402
import hollowmere  # noqa: E402
import kite  # noqa: E402
import iskarra_spire  # noqa: E402
import undertow_layers  # noqa: E402
import undertow_heart  # noqa: E402
import reedhollow  # noqa: E402
import fen_zones  # noqa: E402
import vey_zones  # noqa: E402
import kit_common as kc  # noqa: E402
import props  # noqa: E402
import ruins  # noqa: E402
import shrine  # noqa: E402
import shrine_interior  # noqa: E402
import trees  # noqa: E402
import village  # noqa: E402
import wake_ground  # noqa: E402
import walls  # noqa: E402
import waterfront  # noqa: E402

MAX_GLB_BYTES = 5 * 1024 * 1024  # ADR 0005


def targets() -> dict:
    """target stem -> (budget key, module, zero-arg builder returning list[MeshBuilder])."""
    v = village
    out = {
        "timber_stilt_post": ("timber_stilt_post", v, v.build_stilt_post),
        "timber_deck_2m": ("timber_deck_2m", v, v.build_deck_module),
        "timber_railing_2m": ("timber_railing_2m", v, v.build_railing_module),
        "roof_thatch_hip": ("roof_thatch_hip", v, v.build_roof_thatch),
        "roof_tile_hip": ("roof_tile_hip", v, v.build_roof_tile),
        "storehouse_stilt": ("storehouse_stilt", v, v.build_storehouse),
        "stilt_house": ("stilt_house", v, v.build_stilt_house),
    }
    for name in sorted(v.HOUSES) + sorted(v.LANE_HOUSES):
        out[name] = ("house_tile", v, lambda name=name: v.build_house(name))
    for name in sorted(v.GULLS):
        out[name] = ("lintel_gull", v, lambda name=name: v.build_gull(name))
    for name, fn in sorted(festival.TARGETS.items()):
        out[name] = (name, festival, fn)
    for name, fn in sorted(ruins.TARGETS.items()):
        out[name] = (name, ruins, fn)
    for name, fn in sorted(walls.TARGETS.items()):
        out[name] = (walls.BUDGET_KEY.get(name, name), walls, fn)
    for name, fn in sorted(waterfront.TARGETS.items()):
        out[name] = (name, waterfront, fn)
    for name, fn in sorted(shrine.TARGETS.items()):
        out[name] = (name, shrine, fn)
    for name, fn in sorted(shrine_interior.TARGETS.items()):
        out[name] = (name, shrine_interior, fn)
    for name, fn in sorted(trees.TARGETS.items()):
        out[name] = (name, trees, fn)
    for name, fn in sorted(props.TARGETS.items()):
        out[name] = (name, props, fn)
    for name, fn in sorted(causeway.TARGETS.items()):
        out[name] = (causeway.BUDGET_KEY.get(name, name), causeway, fn)
    for name, fn in sorted(causeway_zone.TARGETS.items()):
        out[name] = (name, causeway_zone, fn)
    for name, fn in sorted(arenas.TARGETS.items()):  # M2-ENV-11 battle arenas
        out[name] = (name, arenas, fn)
    for name, fn in sorted(dressing.TARGETS.items()):  # M3-ENV-701 set dressing
        out[name] = (name, dressing, fn)
    for name, fn in sorted(iskarra.TARGETS.items()):  # M3-ENV-710 the Prologue's Iskarra
        out[name] = (iskarra.BUDGET_KEY.get(name, name), iskarra, fn)
    for name, fn in sorted(keth.TARGETS.items()):  # M3-ENV-717 Keth Pass (Ch12)
        out[name] = (name, keth, fn)
    for name, fn in sorted(lowlight.TARGETS.items()):  # M3-ENV-716 Lowlight's engine hall (Ch11)
        out[name] = (lowlight.BUDGET_KEY.get(name, name), lowlight, fn)
    for name, fn in sorted(ossa_fen.TARGETS.items()):  # M3-ENV-718 Ossa Fen (Ch10)
        out[name] = (name, ossa_fen, fn)
    for name, fn in sorted(save_shrine.TARGETS.items()):  # M3-ENV-101 the save shrine
        out[name] = (name, save_shrine, fn)
    for name, fn in sorted(bridal_barge.TARGETS.items()):  # M3-ENV-720 the Ch15 bridal barge
        out[name] = (name, bridal_barge, fn)
    for name, fn in sorted(ansedra.TARGETS.items()):  # M3-ENV-721 Ansedra (Ch13-14)
        out[name] = (ansedra.BUDGET_KEY.get(name, name), ansedra, fn)
    for name, fn in sorted(drowned_choir.TARGETS.items()):  # M3-ENV-722 the Pale Rim and the Drowned Choir (Ch16)
        out[name] = (name, drowned_choir, fn)
    for name, fn in sorted(hollowmere.TARGETS.items()):  # M3-ENV-723 Hollowmere, the Saltwright raft-city (Ch17)
        out[name] = (name, hollowmere, fn)
    for name, fn in sorted(kite.TARGETS.items()):  # M3-ENV-725 the Kite, the party's hub from Ch18
        out[name] = (name, kite, fn)
    for name, fn in sorted(iskarra_spire.TARGETS.items()):  # M3-ENV-726 the Iskarra Lamp Spire's crown (Ch19)
        out[name] = (name, iskarra_spire, fn)
    for name, fn in sorted(wake_ground.TARGETS.items()):  # M3-ENV-743 Ch4's wake-night ground
        out[name] = (name, wake_ground, fn)
    for name, fn in sorted(undertow_layers.TARGETS.items()):  # M3-ENV-727 the Undertow's layers (Ch20)
        out[name] = (name, undertow_layers, fn)
    for name, fn in sorted(undertow_heart.TARGETS.items()):  # M3-ENV-728 the Heart of the Undertow (Ch21)
        out[name] = (name, undertow_heart, fn)
    for name, fn in sorted(reedhollow.TARGETS.items()):  # M3-ENV-733 Ossa Fen's root-walks and Reedhollow's reed walks
        out[name] = (name, reedhollow, fn)
    for name, fn in sorted(fen_zones.TARGETS.items()):  # M4-A2P-040 the Ch10 zones' ground, from their greybox
        out[name] = (name, fen_zones, fn)
    for name, fn in sorted(vey_zones.TARGETS.items()):  # M4-A2P-041 the Sunken Vey's walks and bed, from its greybox
        out[name] = (name, vey_zones, fn)
    return out


PLACEHOLDERS = dict(shrine.PLACEHOLDER_REASONS)  # M2-ENV-07: the two trees are real now (trees.py)


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
    ap = argparse.ArgumentParser(description="Build the Haluna kit .glb files")
    ap.add_argument("--target", action="append", help="target stem (repeatable); see --list")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", help="output .glb (single --target)")
    ap.add_argument("--out-dir", default="assets/environments/kits/haluna")
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
            "kit": "haluna",
            "generator": "assets_src/environments/kits/haluna/build.py",
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
