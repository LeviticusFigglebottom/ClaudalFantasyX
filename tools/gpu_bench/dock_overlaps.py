#!/usr/bin/env python3
"""Human playtest check (b), cloud QA pass 6: moored boats whose mesh AABB intersects a dock, pier or post.

Reads dock_probe's meshes.json (tools/gpu_bench/dock_probe.gd) and prints every boat/dock pair whose world AABBs
overlap, with the overlap's extent on each axis (metres). LOD1 copies are left out (the LOD0 mesh stands for both).
Usage: python3 tools/gpu_bench/dock_overlaps.py <meshes.json> [--min=0.05]
"""
from __future__ import annotations

import json
import sys

BOATS = ("scale_hull", "cookboat", "hull_outrigger", "terrace_hull", "terrace_hold", "keel_hull", "dive_raft", "low_hull")
DOCKS = ("plank_bridge", "raft_deck", "gull_post", "net_pen", "net_frame", "pier", "dock", "post", "pile", "jetty")


def kind(name: str) -> str:
    if any(b in name for b in BOATS):
        return "boat"
    if any(d in name for d in DOCKS):
        return "dock"
    return ""


def main(argv: list[str]) -> int:
    path = argv[1]
    min_m = 0.05
    for a in argv[2:]:
        if a.startswith("--min="):
            min_m = float(a.split("=", 1)[1])
    rows = [r for r in json.load(open(path)) if not r["path"].endswith("-lod1")]
    items = []
    for r in rows:
        name = r["mesh"].split("/")[-1].split("::")[0]
        k = kind(name)
        if k:
            items.append((k, name, r["path"], r["aabb"]))
    boats = [i for i in items if i[0] == "boat"]
    docks = [i for i in items if i[0] == "dock"]
    hits = 0
    for _, bn, bp, ba in boats:
        for _, dn, dp, da in docks:
            ov = [min(ba[3 + k], da[3 + k]) - max(ba[k], da[k]) for k in range(3)]
            if all(o > min_m for o in ov):
                hits += 1
                print(f"OVERLAP {bn:22s} {bp:40s} x {dn:24s} {dp:40s} dx {ov[0]:.2f} dy {ov[1]:.2f} dz {ov[2]:.2f}")
    print(f"{len(boats)} boats, {len(docks)} docks/piers/posts, {hits} overlapping pairs (> {min_m} m on every axis)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
