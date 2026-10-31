#!/usr/bin/env python3
"""M2-FP-108: the Saltgrass Causeway's gameplay layout on env-art's final route (M2-ENV-10).

Reads env-art's generated assets/environments/zones/saltgrass_causeway/causeway_layout.json (the walked path
polyline and the anchors) and writes game/levels/ch03/saltgrass_causeway/saltgrass_causeway_layout.json for
GreyboxZone: the dressing scene, an invisible walk floor and rails along the path, the spawns, the story
triggers (placed by distance along the path or at an anchor), the side-on dolly and the beat cameras, and the
encounter table. Run it again whenever env-art regenerates the route; --check fails when the file is stale.

    python3 tools/causeway/build_causeway_gameplay.py [--check]
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE = ROOT / "assets/environments/zones/saltgrass_causeway/causeway_layout.json"
OUT = ROOT / "game/levels/ch03/saltgrass_causeway/saltgrass_causeway_layout.json"
WILDLIFE_OUT = ROOT / "game/data/world/wildlife/ch03_saltgrass_causeway.json"
POST_TOP_M = 2.4  # assets_src/environments/kits/haluna/causeway.py POST_H_M: a post's top above its piece y
# saltgrass_causeway.tscn's Harrier node (CausewayHarrier's circle centre); C07 aims at it (row 18).
HARRIER_NODE_AT = (90.96, 5.06, -57.36)
POOL_WATER_Y = -0.85  # the tide pools dip under the zone's sea (-0.7), which fills them
DRESSING = "res://assets/environments/zones/saltgrass_causeway/saltgrass_causeway_dressing.tscn"
ADOPT = "res://game/levels/ch03/saltgrass_causeway/causeway_zone_dresser.gd"

PATH_LIFT_M = 0.32  # env-art: the polyline rides this far above the walked surface
FLOOR_W = 3.4
FLOOR_T = 0.4
FLOOR_OVERLAP_M = 0.8
RAIL_H = 1.6
RAIL_T = 0.3
TRIGGER_DEPTH = 1.5
TRIGGER_W = 8.0
DOLLY_SIDE_M = 9.0
DOLLY_UP_M = 1.5
TRACK_UP_M = 1.0
BEAT_BOX = [16.0, 6.0, 16.0]
SPAWN_STEP_M = 6.0
# Random fights after the harrier: a gap is drawn between these shares of the walk left to the islet, so the
# final route (about 215 m after C07) meets two or three, as the greybox's 70 m did with its 25-45 m gaps,
# never the six to eight its old fixed gaps would give over the longer walk (the playtest's back-to-back fights).
ENCOUNTER_MIN_SHARE = 0.32
ENCOUNTER_MAX_SHARE = 0.45
# The Lead's encounter-pacing FAST-TRACK (10-30, the human's playtest): every zone's gap is 95-145 m, a 31-44 s breather
# at the run (game/data/world/greybox_defaults.json min_gap_m; tools/act1/encounter_pacing.py). The shares above
# would give 68-95 m on this route, so the floor wins: about one fight per walk after the Harrier.
ENCOUNTER_MIN_M = 95.0
ENCOUNTER_MAX_M = 145.0


def seg_len(a, b):
    return math.dist((a[0], a[2]), (b[0], b[2]))


def at_distance(path, s):
    """(point, heading unit (dx, dz)) at distance s along the path (clamped)."""
    s = max(0.0, s)
    for a, b in itertools.pairwise(path):
        L = seg_len(a, b)
        if L <= 0:
            continue
        if s <= L:
            t = s / L
            p = [a[i] + (b[i] - a[i]) * t for i in range(3)]
            return p, ((b[0] - a[0]) / L, (b[2] - a[2]) / L)
        s -= L
    a, b = path[-2], path[-1]
    L = seg_len(a, b)
    return list(b), ((b[0] - a[0]) / L, (b[2] - a[2]) / L)


def nearest_s(path, x, z):
    best, best_s, acc = 1e9, 0.0, 0.0
    for a, b in itertools.pairwise(path):
        L = seg_len(a, b)
        if L <= 0:
            continue
        ux, uz = (b[0] - a[0]) / L, (b[2] - a[2]) / L
        t = max(0.0, min(L, (x - a[0]) * ux + (z - a[2]) * uz))
        d = math.dist((a[0] + ux * t, a[2] + uz * t), (x, z))
        if d < best:
            best, best_s = d, acc + t
        acc += L
    return best_s


def yaw_deg(dx, dz):
    """GreyboxZone yaw: rotation.y, the -Z forward convention."""
    return round(math.degrees(math.atan2(-dx, -dz)), 2)


def r(v, n=3):
    return [round(x, n) for x in v]


def surface(p):
    return [p[0], p[1] - PATH_LIFT_M, p[2]]


def build(route):
    path = [list(map(float, p)) for p in route["path"]]
    anchors = route["anchors"]
    total = sum(seg_len(a, b) for a, b in itertools.pairwise(path))
    blocks = []
    for i, (a, b) in enumerate(itertools.pairwise(path)):
        L = seg_len(a, b)
        if L <= 0:
            continue
        sa, sb = surface(a), surface(b)
        mid = [(sa[k] + sb[k]) / 2 for k in range(3)]
        dx, dz = (b[0] - a[0]) / L, (b[2] - a[2]) / L
        yaw = yaw_deg(dx, dz)
        pitch = round(math.degrees(math.atan2(sb[1] - sa[1], L)), 2)
        blocks.append({"id": f"Walk{i:02d}", "pos": r([mid[0], mid[1] - FLOOR_T / 2, mid[2]]),
                       "size": [FLOOR_W, FLOOR_T, round(L + FLOOR_OVERLAP_M, 3)], "yaw": yaw, "pitch": pitch,
                       "visible": False})
        for side, name in ((1, "R"), (-1, "L")):
            off = side * (FLOOR_W / 2 + RAIL_T / 2)
            rx, rz = -dz, dx  # right of the heading
            blocks.append({"id": f"Rail{name}{i:02d}",
                           "pos": r([mid[0] + rx * off, mid[1] + RAIL_H / 2, mid[2] + rz * off]),
                           "size": [RAIL_T, RAIL_H, round(L + FLOOR_OVERLAP_M, 3)], "yaw": yaw, "visible": False})
    # Caps at both ends so nobody walks off the head or past the steps.
    for name, s, back in (("CapHead", 0.0, -1), ("CapSteps", total, 1)):
        p, (dx, dz) = at_distance(path, s)
        q = surface(p)
        blocks.append({"id": name, "pos": r([q[0] + dx * back * 0.6, q[1] + RAIL_H / 2, q[2] + dz * back * 0.6]),
                       "size": [FLOOR_W + 2 * RAIL_T, RAIL_H, RAIL_T], "yaw": yaw_deg(dx, dz), "visible": False})

    def spawn(s, back=False):
        p, (dx, dz) = at_distance(path, s)
        q = surface(p)
        return r([q[0], q[1], q[2]]) + [yaw_deg(-dx, -dz) if back else yaw_deg(dx, dz)]

    harrier_s = nearest_s(path, 75.97, -47.42)  # env-art's C07 (the flier against the cumulus)
    tidepool = anchors["tide_pools"][0]
    ring = anchors["lit_age_ring"]
    spawns = {
        "FromHaluna": spawn(1.5),
        "BeforeHarrier": spawn(harrier_s - SPAWN_STEP_M),
        "AfterHarrier": spawn(harrier_s + SPAWN_STEP_M),
        "ShrineSteps": spawn(total - SPAWN_STEP_M, back=True),
    }

    def trigger(tid, s, **extra):
        p, (dx, dz) = at_distance(path, s)
        q = surface(p)
        t = {"id": tid, "at": r(q), "size": [TRIGGER_W, 0, TRIGGER_DEPTH], "yaw": yaw_deg(dx, dz)}
        t.update(extra)
        return t

    triggers = [
        # M3-NAR-01: the Tide-Readers' Notice nailed to the first marker post past the head (C02), read before the
        # first banter post. A record: CodexNotice marks codex_causeway_notice_found and shows its card.
        trigger("causeway_notice", nearest_s(path, *anchors["marker_posts"][0]), activation="interact",
                prompt_key="FIELD_PROMPT_DEFAULT", once=True, payload={"record": "causeway_notice"}),
        trigger("banter_posts", nearest_s(path, *anchors["marker_posts"][1]), once=True,
                sets_flag="ch03_banter_posts",
                payload={"dialogue": "ch03_bark_causeway_posts", "overheard": True}),
        trigger("harrier", harrier_s, blocked_by_flag="ch03_harrier_won", payload={"beat": "harrier"}),
        trigger("banter_tidepool", nearest_s(path, tidepool[0], tidepool[1]) + 4.0, once=True,
                sets_flag="ch03_banter_tidepool",
                payload={"dialogue": "ch03_bark_causeway_tidepool", "overheard": True}),
        trigger("banter_ring", nearest_s(path, ring[0], ring[1]), once=True, sets_flag="ch03_banter_ring",
                payload={"dialogue": "ch03_bark_causeway_ring", "overheard": True}),
        trigger("to_shrine", total - 1.5, payload={"beat": "to_shrine"}),
    ]

    # The side-on dolly (C02) over the whole route: the camera rides the path offset to its right, smoothed.
    dolly, track = [], []
    n = len(path)
    for i in range(n):
        a, b = path[max(0, i - 2)], path[min(n - 1, i + 2)]
        L = seg_len(a, b) or 1.0
        dx, dz = (b[0] - a[0]) / L, (b[2] - a[2]) / L
        q = surface(path[i])
        dolly.append(r([q[0] - dz * DOLLY_SIDE_M, q[1] + DOLLY_UP_M, q[2] + dx * DOLLY_SIDE_M]))
        track.append(r([q[0], q[1] + TRACK_UP_M, q[2]]))
    xs = [p[0] for p in path]
    zs = [p[2] for p in path]
    pad = 24.0
    cams = [{"id": "C02", "at": r([(min(xs) + max(xs)) / 2, 1.5, (min(zs) + max(zs)) / 2]),
             "size": r([max(xs) - min(xs) + pad, 12.0, max(zs) - min(zs) + pad]), "priority": 0, "mode": "dolly",
             "dolly": dolly, "track": track, "fov": 27.0}]
    # Beat frames from env-art's C01-C07 previews (haluna.md §5.3), each over a box around where it plays.
    beats = {
        "C01": ([-3.62, 1.84, 1.70], [129.76, 1.08, -98.68], 67.4, [0.0, 0.0], "pan_follow"),
        "C04": ([39.72, 1.30, -27.52], [95.44, 0.95, -57.62], 37.8, anchors["broken_post"], "pan_follow"),
        # C07 levelled (the Lead's 10-27 review: the preview's 22-degree tilt left a sliver of ground): the causeway
        # runs on toward the harrier's flats with the cumulus over it.
        "C07": ([75.97, 1.2, -47.42], [85.05, 1.6, -51.63], 53.1, None, "fixed"),
        "C03": ([67.20, -0.35, -19.65], [63.92, -0.70, -23.98], 13.7, tidepool[:2], "pan_follow"),
        "C05": ([102.70, 0.66, -79.49], [106.09, 0.57, -75.68], 46.4, ring, "pan_follow"),
        "C06": ([104.87, 0.39, -44.99], [193.11, 1.34, -147.18], 20.9, None, "pan_follow"),
    }
    for cid, (pos, look, fov, near, mode) in beats.items():
        if cid == "C07":
            centre = at_distance(path, harrier_s)[0]
        elif cid == "C06":
            centre = at_distance(path, total - 40.0)[0]
        else:
            centre = at_distance(path, nearest_s(path, near[0], near[1]))[0]
        cam = {"id": cid, "at": r([centre[0], 1.5, centre[2]]), "size": BEAT_BOX, "priority": 1,
               "mode": mode, "pos": pos, "look_at": look, "fov": fov}
        if cid == "C07":
            # PC pass 7 row 18: the frame is about the flier, not the party behind the camera; with the harrier as its
            # subject the field camera never turns it to the leader. The offset puts the aim back on look_at.
            cam["aim_node"] = "Harrier"
            cam["aim_offset"] = [round(a - h, 2) for a, h in zip(look, HARRIER_NODE_AT)]
        cams.append(cam)
    return {
        "doc": "M2-FP-108: GENERATED by tools/causeway/build_causeway_gameplay.py from env-art's final route "
               "(assets/environments/zones/saltgrass_causeway/causeway_layout.json, M2-ENV-10); do not edit by "
               "hand. The Saltgrass Causeway (vertical_slice.md B06; haluna.md C01-C07): GreyboxZone instances the "
               "dressing (its own sky, sun and sea) and adds an invisible walk floor and rails along the path, the "
               "spawns, the story triggers, the side-on C02 dolly and the beat frames.",
        "dressing": {"scene": DRESSING, "adopt": ADOPT},
        "blocks": blocks,
        "spawns": spawns,
        "triggers": triggers,
        "camera_volumes": cams,
        "encounters": {"table": [{"encounter": "ch03_causeway_shore", "weight": 1}],
                       "min_m": max(round(ENCOUNTER_MIN_SHARE * (total - harrier_s), 1), ENCOUNTER_MIN_M),
                       "max_m": max(round(ENCOUNTER_MAX_SHARE * (total - harrier_s), 1), ENCOUNTER_MAX_M),
                       "when": {"set": ["ch03_harrier_won"]}, "seed": 3},
    }


def build_wildlife(route):
    """M3-CRE-611's causeway wildlife moved onto the final route (creatures asked for this at the swap)."""
    path = [list(map(float, p)) for p in route["path"]]
    posts = [pc for pc in route["pieces"] if pc["piece"] == "pilgrim_marker_post"]

    def perch(pc):
        return [round(pc["at"][0], 2), round(pc["y"] + POST_TOP_M, 3), round(pc["at"][1], 2), round(pc["yaw_deg"], 1)]

    def centre(pcs):
        return [round(sum(pc["at"][0] for pc in pcs) / len(pcs), 2), round(sum(pc["at"][1] for pc in pcs) / len(pcs), 2)]

    near, far = posts[:4], posts[-4:]

    def reach(pcs):
        c = centre(pcs)
        return round(max(math.dist(c, pc["at"]) for pc in pcs) + 4.0, 1)

    def beach(bid, s, count):
        q, (dx, dz) = at_distance(path, s)
        return {"id": bid, "center": [round(q[0], 2), round(q[2], 2)], "half_extents": [0.9, 6.0],
                "yaw_deg": yaw_deg(dx, dz), "y": round(q[1] - PATH_LIFT_M, 3), "count": count}

    pool = route["anchors"]["tide_pools"][0]
    return {
        "_doc": "M3-CRE-611 placement on the final Saltgrass Causeway route (M2-FP-108). GENERATED by "
                "tools/causeway/build_causeway_gameplay.py from env-art's causeway_layout.json: gulls work the head "
                "and the islet end and stand on the plain marker posts' tops; crabs keep to the path's slabs; fry "
                "hang in the first tide pool under the sea level that fills it.",
        "zone": "ch03/saltgrass_causeway",
        "flocks": [
            {"id": "head", "center": centre(near), "radius_m": max(28.0, reach(near)), "altitude_m": [5.5, 11.0], "count": 4,
             "perched_at_start": 2, "perches": [perch(pc) for pc in near]},
            {"id": "islet", "center": centre(far), "radius_m": max(24.0, reach(far)), "altitude_m": [6.0, 12.0], "count": 3,
             "perched_at_start": 1, "perches": [perch(pc) for pc in far]},
        ],
        "beaches": [beach("path_head", 22.0, 4), beach("path_pool", nearest_s(path, pool[0], pool[1]) - 6.0, 3)],
        "shoals": [{"id": "tidepool", "center": [pool[0], POOL_WATER_Y, pool[1]], "radius_m": round(pool[2] * 0.4, 2),
                    "count": 5, "scale": 0.55, "spread_m": [0.6, 0.0, 0.5]}],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    route = json.loads(ROUTE.read_text(encoding="utf-8"))
    outputs = {OUT: build(route), WILDLIFE_OUT: build_wildlife(route)}
    stale = 0
    for path, data in outputs.items():
        text = json.dumps(data, indent=1) + "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                print(f"{path.relative_to(ROOT)} is stale: run tools/causeway/build_causeway_gameplay.py")
                stale += 1
            continue
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    if args.check and not stale:
        print("causeway gameplay layout and wildlife: up to date")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
