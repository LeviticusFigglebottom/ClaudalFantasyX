"""Oruvel's zone dressing (M3-ENV-738; ADR 0041, ADR 0200): the raft-town kit (M3-ENV-07, 07B) and the *Seventh
Terrace* (M3-ENV-08B) laid over slice-polish's Ch1 greybox (`game/levels/ch01/oruvel/oruvel_layout.json`, M3-C01-02),
in the greybox's own frame, as a ZoneKitDressing layout.

    python3 assets_src/environments/kits/oruvel/ov_zone_dressing.py

Writes assets/environments/zones/ch01/oruvel_dressing.json. The zone mounts it with a `Dressing` child
(game/levels/act1/zone_kit_dressing.gd, layout_path = that file), plus a `Water` WaterSurface at WATER_Y.

The greybox keeps the gameplay (ADR 0200): every walkable block's top is y 0, so each raft, hull and pen is sunk until
its deck is at 0 and scaled until its deck covers the block. That puts the sea at WATER_Y (the raft decks' own height
over the water). Bridges span the greybox's gaps. The story's blocks keep their pieces in step: the Terrace and its
name-board follow `SeventhTerrace`/`NameBoard`, the dive bridge `DiveBridge` and the run's low hull `LowHull`, so the
storm state hides them with the blocks. Decor on the decks takes a box collider and stands clear of every actor,
mark, spawn and trigger (tested in tools/tests/test_zone_dressing_ch01.py).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import ov_cabins as ocab  # noqa: E402
import ov_common as oc  # noqa: E402
import ov_heroes as oh  # noqa: E402
import ov_hulls as ohl  # noqa: E402
import ov_preview_layout as pl  # noqa: E402  (put, local, bridge, gull; read-only)

GREYBOX = ROOT / "game" / "levels" / "ch01" / "oruvel" / "oruvel_layout.json"
OUT = ROOT / "assets" / "environments" / "zones" / "ch01" / "oruvel_dressing.json"
ENV_SRC = ROOT / "game" / "levels" / "_tests" / "oruvel_kit" / "oruvel_ch01_environment.tres"  # ov_preview_layout's
ENV_OUT = OUT.parent / "oruvel_ch01_environment.tres"  # the zone's copy (a shipped zone never reads _tests/)
ENV_RES = "res://assets/environments/zones/ch01/oruvel_ch01_environment.tres"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "oruvel_zone_dressing" / "oruvel_dressed.tscn"
PREVIEW_SHOTS = ("O01", "O07", "O09", "O12", "O16")
KIT = "res://assets/environments/kits/oruvel/"
FERRY_KIT = "res://assets/environments/kits/brightwater_ferry/"

WATER_Y = -ohl.RAFT_DECK_Y  # the raft decks stand 0.8 m over the sea; the greybox's decks are at 0
RAFT_DECK = (9.0, 7.0)  # raft_deck's deck, x by z, at scale 1
CLEAR_M = 1.2  # decor keeps this far from every actor, mark and spawn, and out of every trigger
STORM_BLOCK = "StormWall"  # shown only in the storm: the storm's pieces and lights follow it
STORM_ENV_SRC = ROOT / "game" / "levels" / "_tests" / "oruvel_kit" / "oruvel_storm_environment.tres"
STORM_ENV_OUT = OUT.parent / "oruvel_ch01_storm_environment.tres"  # the stand-in ch01_storm frame (lut_ch01_storm)
STORM_ENV_RES = "res://assets/environments/zones/ch01/oruvel_ch01_storm_environment.tres"
PREVIEW_STORM = PREVIEW.parent / "oruvel_dressed_storm.tscn"
PREVIEW_STORM_SHOTS = ("O12", "O16")
STORM_FAR_M = pl.STORM_FAR_M
CHANDLERY_GULL_Z = 0.9  # the chandlery's ridge gull, in the hull's frame (ov_preview_layout's)
CHANDLERY_EAVE_M = 2.22  # its eave over its deck (ov_heroes.build_chandlery)
CHANDLERY_BEACON_Z = -1.8  # its beacon lantern's post, off the keel-roof's fore end (the hull's frame)
CHANDLERY_BEACON_UP_M = 0.12 + 1.2 + 0.3  # the post's foot over the roof, its height, the lantern's middle
GULL_PERCH_M = 0.08  # a gull's feet over the ridge line
LOW_HULL_LOAD_Y = -0.05  # the salvage on the run's planks over LowHull (the bridge sags 0.15 m mid-span)
LOW_HULL_LOAD_SCALE = 0.65  # 2.0 x 1.5 m: inside LowHull's 2 x 3 m footprint, turned across the run


def _blocks() -> dict[str, dict]:
    return {b["id"]: b for b in json.loads(GREYBOX.read_text(encoding="utf-8"))["blocks"]}


def raft_over(block: dict, *, cx: float | None = None, cz: float | None = None, dx: float = 0.0,
              dz: float = 0.0) -> dict:
    """A raft_deck, scaled so its deck covers (size_x + dx) by (size_z + dz), sunk so its deck is at y 0."""
    sx, sz = block["size"][0] + dx, block["size"][2] + dz
    s = max(sx / RAFT_DECK[0], sz / RAFT_DECK[1], 1.0)
    x = block["pos"][0] if cx is None else cx
    z = block["pos"][2] if cz is None else cz
    d = pl.put("raft_deck", x, -ohl.RAFT_DECK_Y * s, z, 0.0)
    if s > 1.0:
        d["scale"] = round(s, 3)
    return d


def span(a: tuple[float, float], b: tuple[float, float], **kw) -> dict:
    """A plank bridge from a to b (deck at 0); stretched when the gap is longer than its 6 m span."""
    d = pl.bridge(a, b, 0.0)
    n = math.hypot(b[0] - a[0], b[1] - a[1])
    if n > ohl.BRIDGE_SPAN:
        s = n / ohl.BRIDGE_SPAN
        d = pl.put("plank_bridge", (a[0] + b[0]) * 0.5 - (b[0] - a[0]) / n * ohl.BRIDGE_SPAN * s * 0.5, 0.0,
                   (a[1] + b[1]) * 0.5 - (b[1] - a[1]) / n * ohl.BRIDGE_SPAN * s * 0.5, d["yaw_deg"], scale=round(s, 3))
    d.update(kw)
    return d


def decor(piece: str, x: float, y: float, z: float, yaw: float = 0.0, **kw) -> dict:
    return pl.put(piece, x, y, z, yaw, collide=True, **kw)


def pieces() -> list[dict]:
    b = _blocks()
    out: list[dict] = []
    # The scale-hull (the spawn; the diver surfaces at its south edge), its bridge, and the scale booth's hull moored
    # alongside it to the west, its counter facing the deck.
    out.append(raft_over(b["ScaleHull"]))
    out.append(pl.put("scale_hull", -7.4, WATER_Y, 10.5, 0.0))
    out.append(span((0.0, 0.0), (0.0, 5.0)))
    # The commons (36 x 24): raft decks lashed edge to edge, four across and three deep, a row of small rafts on its
    # north edge; the cabin with the child on its roof, the cook's boat, the menders' nets.
    for i, x in enumerate((-13.5, -4.5, 4.5, 13.5)):
        for j, z in enumerate((-3.5, -10.5, -17.5)):
            # Every other deck turned end for end (the same footprint), so the deck props don't repeat in rows. The
            # tucked decks keep their hulls under their own planks: an open raft's bows would rise through the next
            # deck (the walk-through, 2026-10-29).
            out.append(pl.put("raft_deck_tucked", x, WATER_Y + 0.004 * ((i + j) % 2), z, 180.0 * ((i + j) % 2)))
        out.append(pl.put("raft_deck_small_tucked", x - 1.5, -ohl.RAFT_SMALL_Y + 0.008, -22.6, 0.0))
        out.append(pl.put("raft_deck_small_tucked", x + 3.0, -ohl.RAFT_SMALL_Y + 0.012, -22.6, 0.0))
    roof = b["CabinRoof"]
    # Its ridge under the roof child's feet (the cast stands her on it; the greybox block's top is 1 m lower).
    s = round(_actor("roof_child")[1] / ocab.KEELROOF_RIDGE_Y, 3)
    cab = decor("cabin_keelroof", roof["pos"][0], 0.0, roof["pos"][2], 90.0, scale=s)
    out.append(cab)
    out.append(ridge_gull(cab, s))
    out.append(pl.put("cookboat", -19.6, WATER_Y, -6.0, 0.0))
    out.append(decor("net_frame", 15.4, 0.0, -7.0, 0.0))
    out.append(decor("salvage_heap", 16.0, 0.0, -18.5, 30.0))
    out.append(decor("salvage_heap", -16.5, 0.0, -13.0, 200.0))
    out.append(pl.put("hull_outrigger", 19.6, WATER_Y + 0.3, -17.0, 0.0))
    # The outer mooring and the *Seventh Terrace* west of it: her name-board where the greybox's NameBoard is (O07).
    out.append(span((-18.0, -12.0), (-21.0, -12.0)))
    om = b["OuterMooring"]
    out.append(raft_over(om, cx=om["pos"][0] + 0.5))
    nb = b["NameBoard"]
    tz = nb["pos"][2] - 10.035  # the Terrace's centre: her transom 10 m aft of it, the board 0.035 m off the transom
    ty = nb["pos"][1] - 0.95  # her main deck: the board's centre is 0.95 m over it
    tx = nb["pos"][0] - 0.5
    for p in ("terrace_hull", "terrace_galley", "terrace_hold", "terrace_rig", "terrace_sails_furled"):
        out.append(pl.put(p, tx, ty, tz, 0.0, kit_dir=FERRY_KIT, block="SeventhTerrace"))
    out.append(pl.put("terrace_wheel", tx, ty + 2.02, tz + 7.0, 0.0, kit_dir=FERRY_KIT, block="SeventhTerrace"))
    out.append(pl.put("terrace_name_board", tx, ty + 0.95, tz + 10.035, 0.0, kit_dir=FERRY_KIT, block="NameBoard"))
    # The keel-hull (north): the town's oldest hull across the block, rafts lashed to its south side; Sabe's place.
    out.append(span((0.0, -24.0), (0.0, -28.0)))
    kh = b["KeelHull"]
    kz = kh["pos"][2] - kh["size"][2] * 0.5 + oh.KEEL_HULL[1] * 0.5 + 0.2
    out.append(pl.put("keel_hull", 0.0, -oh.KEEL_DECK_Y, kz, 90.0))
    gx, gz = pl.local(0.0, kz, 90.0, 0.0, 6.7)
    out.append(pl.gull(gx, oh.KEEL_HULL_RIDGE - oh.KEEL_DECK_Y, gz, 1.35))
    for x in (-4.5, 4.5):
        out.append(pl.put("raft_deck", x, WATER_Y + 0.006, -30.0, 0.0))
    # Kell's mooring (east): the chandlery's hull with its counter where the greybox's stall is (Kell, O09), the
    # mooring's raft south of it, the bridges.
    out.append(span((18.0, -6.0), (25.0, -6.0)))
    sm = b["SecondMooring"]
    out.append(raft_over({"pos": [sm["pos"][0], 0.0, sm["pos"][2] + 1.0], "size": [10.0, 1.0, 8.0]}))
    st = b["KellStall"]
    ch = _chandlery(b)
    out.append(ch)
    # Her roof's gull (C1-11: every carved gull cries at once), where the preview sets it on the ridge.
    gx, gz = pl.local(ch["at"][0], ch["at"][1], ch["yaw_deg"], 0.0, CHANDLERY_GULL_Z)
    out.append(pl.gull(gx, ch["y"] + oh.CHANDLERY_DECK_Y + CHANDLERY_EAVE_M + oh.CHANDLERY_ROOF[2] + GULL_PERCH_M,
                       gz))
    out.append(span((35.0, -6.0), (41.0, -6.0), block="DiveBridge"))
    # The dive mooring (the run's start) and the run's planks to the net-pen; the low hull the lashings hold.
    dm = b["DiveMooring"]
    s = round(dm["size"][0] / 6.0, 3)
    out.append(pl.put("dive_raft", dm["pos"][0], -oh.DIVE_DECK_Y * s, dm["pos"][2], 0.0, scale=s))
    dg = b["DiveGull"]
    out.append(pl.gull(dg["pos"][0], dg["pos"][1] - 0.5, dg["pos"][2]))
    out.append(span((45.0, -10.0), (45.0, -16.0)))
    out.append(span((46.0, -17.0), (40.0, -17.0)))
    out.append(span((40.0, -17.0), (34.0, -17.0)))
    lh = b["LowHull"]
    out.append(pl.put("hull_outrigger", lh["pos"][0] - 1.0, WATER_Y + 0.3, lh["pos"][2], 0.0, block="LowHull"))
    # Its load (C1-13 cuts it loose across the run's planks): salvage piled over the block, so it reads as cargo
    # blocking the way, not a canoe; it drifts clear with the block.
    out.append(pl.put("salvage_heap", lh["pos"][0], LOW_HULL_LOAD_Y, lh["pos"][2], 90.0, scale=LOW_HULL_LOAD_SCALE,
                      block="LowHull"))
    # The net-pen (Hullgnaw's arena, O16) and its bridge.
    np_ = b["NetPen"]
    out.append(pl.put("net_pen", np_["pos"][0], -ohl.NET_PEN_Y, np_["pos"][2], 0.0))
    out.append(span((18.0, -22.0), (24.0, -22.0)))
    # The rest of the raft-town round the zone, at 90-120 m (the far town's low hulls and roofs).
    for x, z, yaw in ((10.0, -110.0, 0.0), (-95.0, -30.0, 90.0), (115.0, -35.0, -90.0)):
        out.append(pl.put("town_far", x, WATER_Y, z, yaw, lod1_from_m=600.0))
    return out + storm_pieces()


def ridge_gull(cab: dict, s: float) -> dict:
    """The open-throat gull on a keel-roof cabin's ridge (ov_preview_layout.keelroof_cabin's rule, at scale s)."""
    L, _B, D, eave, sheer = ocab.KEELROOF
    gz = ocab.KEELROOF_GULL_Z if abs(((cab["yaw_deg"] + 180.0) % 360.0) - 180.0) < 90.0 else -ocab.KEELROOF_GULL_Z
    gx, gzw = pl.local(cab["at"][0], cab["at"][1], cab["yaw_deg"], 0.0, gz * s)
    return pl.gull(gx, cab["y"] + oc.keel_roof_ridge(gz, L, D, eave, sheer) * s, gzw)


def storm_pieces() -> list[dict]:
    """The storm (C1-11 to C1-15; M3-ENV-07B's pieces): what the swell tears loose, afloat round the town. They follow
    `StormWall`, which the zone shows only in the storm (oruvel_zone.gd's layout "storm" "show")."""
    out = [pl.put("storm_debris", x, WATER_Y, z, yaw, block=STORM_BLOCK)
           for x, z, yaw in ((-21.5, -17.0, 35.0), (21.0, 1.5, -70.0), (7.0, 7.5, 150.0), (-24.0, -1.5, 200.0))]
    out.append(pl.put("hull_capsized", -33.0, WATER_Y, -24.0, 60.0, block=STORM_BLOCK))
    # The dive bridge (gone in the storm) adrift south of where it was.
    out.append(pl.put("plank_bridge_broken", 38.5, WATER_Y + ohl.RAFT_DECK_Y - 0.65, -10.0, 20.0, block=STORM_BLOCK))
    return out


def _chandlery(b: dict) -> dict:
    st = b["KellStall"]
    return pl.put("chandlery", st["pos"][0], -oh.CHANDLERY_DECK_Y, st["pos"][2] - st["size"][2] * 0.5 - 1.7, -90.0)


def _actor(name: str) -> list[float]:
    a = json.loads(GREYBOX.read_text(encoding="utf-8"))["actors"]
    r = a[name] if isinstance(a, dict) else next(r for r in a if r.get("id") == name)
    return r.get("at") or r.get("pos")


def storm_lights() -> list[dict]:
    """Kell's beacon (C1-12, O12): lit in the storm, in the chandlery's own beacon lantern (the post off its keel-roof's
    fore end, ov_heroes.build_chandlery), not the greybox's KellBeacon block beside it."""
    ch = _chandlery(_blocks())
    rl, rb, rd, rs = oh.CHANDLERY_ROOF
    eave = oh.CHANDLERY_DECK_Y + CHANDLERY_EAVE_M
    lamp_y = oc.keel_roof_underside(0.0, CHANDLERY_BEACON_Z, rl, rb, rd, eave, rs) + CHANDLERY_BEACON_UP_M
    x, z = pl.local(ch["at"][0], ch["at"][1], ch["yaw_deg"], 0.0, CHANDLERY_BEACON_Z)
    return [{"at": [round(x, 3), round(ch["y"] + lamp_y, 3), round(z, 3)], "energy": 3.0, "range": 9.0,
             "block": STORM_BLOCK}]


def clearance_points() -> list[tuple[str, float, float, float]]:
    """(what, x, z, radius) every decor piece must keep clear of: the actors, marks and spawns, and the triggers."""
    d = json.loads(GREYBOX.read_text(encoding="utf-8"))
    pts = []
    for k in ("actors", "marks", "spawns"):
        rows = d[k].items() if isinstance(d[k], dict) else ((r.get("id"), r) for r in d[k])
        for name, r in rows:
            p = (r.get("pos") or r.get("at")) if isinstance(r, dict) else r
            pts.append((f"{k}:{name}", float(p[0]), float(p[2]), CLEAR_M))
    for name, r in (d["triggers"].items() if isinstance(d["triggers"], dict) else ((t["id"], t) for t in d["triggers"])):
        p = r.get("at") or r.get("pos")
        pts.append((f"trigger:{name}", float(p[0]), float(p[2]), max(r["size"][0], r["size"][2]) * 0.5))
    return pts


def layout() -> dict:
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by assets_src/environments/kits/oruvel/ov_zone_dressing.py from env-art's raft-town kit "
                  "(M3-ENV-07, 07B) and the Seventh Terrace (M3-ENV-08B), in ch01/oruvel's greybox frame (M3-ENV-738); "
                  f"do not edit by hand. The zone's Water goes at y {WATER_Y}.",
        "seed": 1,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 60.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "water_y": WATER_Y,
        "time_of_day_h": 10.5,
        "environment": ENV_RES,
        # The storm variant's frame: the zone swaps its WorldEnvironment to this in set_storm (M3-ENV-751).
        "storm_environment": STORM_ENV_RES,
        "fire_light_color": "#FFB466",
        "fire_lights": storm_lights(),
        "greybox": {"hide_all": True, "keep": []},  # StormWall: the zone stands the UndertowStorm there (M3-ENV-751)
        "pieces": pieces(),
    }


def write_preview(storm: bool = False) -> None:
    """The zone as slice-polish's .tscn has it (its script and greybox layout), with the Water, the Tide and this
    Dressing mounted, and the zone's own shot cameras: env-art's render rig for the swap, until the zone mounts it.
    `storm`: the same brought up in its storm variant (oruvel_storm_preview.gd), as M3-ENV-751 asks of the zone."""
    script = ("res://game/levels/_tests/oruvel_zone_dressing/oruvel_storm_preview.gd" if storm
              else "res://game/levels/ch01/oruvel/oruvel_zone.gd")
    shot_ids = PREVIEW_STORM_SHOTS if storm else PREVIEW_SHOTS
    shots = json.loads(GREYBOX.read_text(encoding="utf-8"))["shots"]
    lines = ["[gd_scene format=3]", "",
             f'[ext_resource type="Script" path="{script}" id="1_zone"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_kit_dressing.gd" id="2_dressing"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/weathering_tide.gd" id="3_tide"]',
             '[ext_resource type="Script" path="res://game/world/water/water_surface.gd" id="4_water"]',
             '[ext_resource type="Resource" path="res://game/world/water/lagoon_waves.tres" id="5_waves"]',
             '[ext_resource type="Material" path="res://game/levels/_tests/oruvel_kit/oruvel_water_material.tres" '
             'id="6_water_mat"]',
             '[ext_resource type="Script" path="res://game/world/camera_shot.gd" id="7_shot"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/haluna_shot_camera.gd" id="8_cam"]', ""]
    for sid in shot_ids:
        sh = shots[sid]
        e, la = sh["pos"], sh["look_at"]
        lines += [f'[sub_resource type="Resource" id="Shot{sid}"]', 'script = ExtResource("7_shot")', f'id = &"{sid}"',
                  f"position = Vector3({e[0]:g}, {e[1]:g}, {e[2]:g})", f"look_at = Vector3({la[0]:g}, {la[1]:g}, {la[2]:g})",
                  f"fov_deg = {sh['fov']:g}", ""]
    lines += ['[node name="Oruvel" type="Node3D"]', 'script = ExtResource("1_zone")', 'location_id = &"ch01/oruvel"',
              'layout_path = "res://game/levels/ch01/oruvel/oruvel_layout.json"', "",
              '[node name="Water" type="Node3D" parent="."]',
              f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {WATER_Y}, 0)", 'script = ExtResource("4_water")',
              "publishes_water_level = true", 'wave_set = ExtResource("5_waves")', 'material = ExtResource("6_water_mat")',
              "", '[node name="Tide" type="Node" parent="." node_paths=PackedStringArray("water")]',
              'script = ExtResource("3_tide")', f"tide_line_y = {WATER_Y}", f"water_height_y = {WATER_Y}",
              'water = NodePath("../Water")', "",
              '[node name="Dressing" type="Node3D" parent="." node_paths=PackedStringArray("tide")]',
              'script = ExtResource("2_dressing")', 'layout_path = "res://assets/environments/zones/ch01/oruvel_dressing.json"',
              'tide = NodePath("../Tide")', "", '[node name="Cameras" type="Node3D" parent="."]', ""]
    far = STORM_FAR_M if storm else 2000.0  # the storm views reach the Undertow, 18 km out (ov_preview_layout's)
    for sid in shot_ids:
        lines += [f'[node name="{sid}" type="Camera3D" parent="Cameras"]', "near = 0.1", f"far = {far:.1f}",
                  'script = ExtResource("8_cam")', f'shot = SubResource("Shot{sid}")', ""]
    out = PREVIEW_STORM if storm else PREVIEW
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ENV_OUT.write_bytes(ENV_SRC.read_bytes())
    STORM_ENV_OUT.write_bytes(STORM_ENV_SRC.read_bytes())
    OUT.write_text(json.dumps(layout(), indent=1) + "\n", encoding="utf-8")
    write_preview()
    write_preview(storm=True)
    print(f"DRESSING {OUT.relative_to(ROOT)} ({len(layout()['pieces'])} pieces)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
