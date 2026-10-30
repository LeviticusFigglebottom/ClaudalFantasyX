#!/usr/bin/env python3
"""Ch11, Lowlight: env-art's Lowlight kit (lowlight.py, vey_zones.py; M3-ENV-716/735) on the two greybox zones
`ch11/sunken_vey` and `ch11/lowlight` (M4-A2P-041; lowlight.md §5's swap map; ADR 0200).

The greybox keeps the gameplay (collision, spawns, marks, triggers, the story): every walk, rail, pillar and wall stays
as it is and only its look is swapped. The walks are built from the same greybox (vey_zones.py), so their slabs, rails
and edges stand where the collision does.

Writes, per zone (game/levels/ch11/<zone>/):
  <zone>_dressing.json         ZoneKitDressing's layout
  <zone>_environment.tres      the zone's grade: colour script ch11 (12:30 overcast noon, lut_ch11_vey), the arena's sky
  <zone>_water_material.tres   the overcast_lagoon water (still turquoise)
and env-art's preview of each zone (game/levels/_tests/ch11_zones/<zone>_dressed.tscn): the zone's own script and
greybox with the Water, the Tide and this Dressing mounted, and ten composed cameras, until the zone mounts it.

    python3 tools/act2/ch11_lowlight_dressing.py
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
sys.path.insert(0, str(KIT_SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import arena_scenes as ar  # noqa: E402
import ch10_fen_dressing as fen  # noqa: E402  (the shared helpers: _put, _axes, _look_xform, write_water_material)
import lowlight as ll  # noqa: E402
import vey_zones as vz  # noqa: E402

KIT = "res://assets/environments/kits/haluna/"
ZONES = ROOT / "game" / "levels" / "ch11"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "ch11_zones"
LUT = "res://assets/environments/arenas/lowlight_engine_hall/lut_ch11_vey.png"
SEED = 11
NEVER_LOD_M = 5000.0  # a zone-built piece spans the zone: its origin's distance means nothing, keep LOD0
BOUND_TEAL = ar.BOUND_TEAL
DATUM_Y = vz.WATER_Y  # the arcades stand on the lagoon's surface
ARCADE_HALF = (3.0, 2.0)  # vey_arcade_bay's footprint (x, z half)
ARCADE_PIER_X = ll.ARCADE_BAY / 2 - 0.55
COLUMN_Y = -0.7  # ruin_column_broken's foot, sunk under the water

r3 = fen.r3
_put = fen._put


def _layout(zone: str) -> dict:
    return json.loads((ZONES / zone / f"{zone}_layout.json").read_text(encoding="utf-8"))


def _rot(x: float, z: float, yaw: float) -> tuple[float, float]:
    a = math.radians(yaw)
    return x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)


def _footprint_clear(lay: dict, x: float, z: float, yaw: float, half: tuple[float, float], gap: float) -> bool:
    """A footprint (centre, yaw, half extents) clear of every greybox block by `gap` (bar the water and the bed)."""
    hx, hz = half
    pts = [(x + dx, z + dz) for dx, dz in (_rot(sx * hx, sz * hz, yaw) for sx in (-1, 0, 1) for sz in (-1, 0, 1))]
    for b in lay["blocks"]:
        if b["id"] in ("Water", "Bed"):
            continue
        for px, pz in pts:
            if vz._covers(b, px, pz, gap):
                return False
    return True


# vey_arcade_bay rows: the drowned arcades that stand round the walks out of reach, (x, z, yaw, figs on its piers).
# The court's square of arcades (L03), the rows receding east from the landing (L01), the fig end's split bay.
VEY_ARCADES = [
    # south of the inbound gallery, framing the landing's view east
    *[(x, 9.5, 0.0, x in (12.0, 30.0)) for x in (0.0, 6.0, 12.0, 18.0, 24.0, 30.0, 36.0, 42.0)],
    # north of it, before the bend
    *[(x, -10.5, 0.0, x == 9.0) for x in (3.0, 9.0, 15.0)],
    # the court's square: west, north and south of its parapets
    (27.4, -26.5, 90.0, True), (27.4, -20.5, 90.0, False),
    (28.0, -32.6, 0.0, False), (48.2, -32.6, 0.0, True),
    (42.2, -11.4, 0.0, False),
    # east of the court, beyond the outbound gallery
    *[(x, -32.0, 0.0, x == 66.0) for x in (54.0, 60.0, 66.0, 72.0)],
    *[(x, -5.0, 0.0, x in (75.0,)) for x in (63.0, 69.0, 75.0, 81.0, 87.0)],
    *[(x, -27.5, 0.0, False) for x in (78.0, 84.0, 90.0)],
    # the side gallery's flanks
    (27.0, -42.0, 90.0, True), (49.0, -44.0, 90.0, False),
    # the fig end: the split bay behind the fig (its arch blocked by a fallen wall)
    (38.0, -59.2, 0.0, True),
]


def vey() -> dict:
    lay = _layout("sunken_vey")
    bl = {b["id"]: b for b in lay["blocks"]}
    rng = random.Random(SEED)
    pieces = [_put(n, 0.0, 0.0, 0.0, 0.0, lod1_from_m=NEVER_LOD_M) for n in vz.TARGETS]
    # The greybox's pillars beside the walks: the broken cast columns of the drowned arcades.
    for b in lay["blocks"]:
        if "Pillar" in b["id"]:
            pieces.append(_put("ruin_column_broken", b["pos"][0], COLUMN_Y, b["pos"][2], rng.uniform(0, 360)))
    # The conduit court: the housing with the mark on the stand's face (conduit_mark looks at it).
    c = bl["Conduit"]
    pieces.append(_put("conduit_housing", c["pos"][0], 1.35, c["pos"][2] + c["size"][2] / 2, 0.0))
    figs = []
    for x, z, yaw, fig in VEY_ARCADES:
        pieces.append(_put("vey_arcade_bay", x, DATUM_Y, z, yaw))
        if fig:
            side = rng.choice((-1.0, 1.0))
            px, pz = _rot(side * ARCADE_PIER_X, 0.0, yaw)
            figs.append(_put("strangler_fig", x + px, DATUM_Y, z + pz, rng.uniform(0, 360), scale=r3(rng.uniform(1.2, 1.35))))
    # The fig end (fig_end): the fig that split the gallery, a hollow lattice where its host pier fell, the fallen wall
    # blocking the bay's arch behind it; and a fig on each of the bay's piers.
    fg = bl["Fig"]
    figs.append(_put("strangler_fig", fg["pos"][0], DATUM_Y, fg["pos"][2] + 0.1, 25.0, scale=1.15))
    figs.append(_put("strangler_fig", fg["pos"][0] - ARCADE_PIER_X, DATUM_Y, -59.2, 140.0, scale=1.3))
    pieces.append(_put("ruin_wall_sunk", fg["pos"][0], -1.6, fg["pos"][2] - 0.9, 0.0))
    # Figs on a few of the columns too (the host broke; the roots held on and grew over the break).
    for b in lay["blocks"]:
        if "Pillar" in b["id"] and b["id"] in ("GalleryIn1PillarR1", "GallerySidePillarL2", "GalleryOut0PillarR2",
                                                 "GalleryOut1PillarL1", "GalleryIn0PillarL2"):
            figs.append(_put("strangler_fig", b["pos"][0], COLUMN_Y, b["pos"][2], rng.uniform(0, 360), scale=0.78))
    pieces += figs
    # Lowlight beyond its gate: the nave's broken vault over the facade (L01: "at the end, the temple's broken vault").
    g = bl["GateBound"]
    for k, x in enumerate((g["pos"][0] + 6.5, g["pos"][0] + 14.5)):
        pieces.append(_put("lowlight_nave_bay_broken" if k == 0 else "lowlight_nave_bay", x, DATUM_Y + 0.45, g["pos"][2],
                           90.0))
    return {
        "pieces": pieces,
        "fire_light_color": BOUND_TEAL,
        # The conduit's bound light on the court's flags and the housing (steady; never flickers).
        "fire_lights": [{"at": [c["pos"][0], 1.6, c["pos"][2] + 1.2], "energy": 1.4, "range": 4.5}],
    }


def layout(zone: str) -> dict:
    body = {"sunken_vey": vey}[zone]()
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": f"Generated by tools/act2/ch11_lowlight_dressing.py from env-art's Lowlight kit on ch11/{zone}'s "
                  "greybox (M4-A2P-041; lowlight.md §5). Do not edit by hand.",
        "seed": SEED,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 60.0,
        "lod_end_m": 700.0,
        "lod_margin_m": 3.0,
        "greybox": {"hide_all": True, "keep": []},
        "environment": f"res://game/levels/ch11/{zone}/{zone}_environment.tres",
        "time_of_day_h": 12.5,
        **body,
    }


# The arena's sky is Corrow's with a grey horizon; its warm cloud deck and band hide behind the hall's vault, but over the
# open lagoon they read as a sunset. Colour script ch11 is a grey noon: the deck goes to the overcast's greys, no band.
OVERCAST_NOON = {"col_cloud_lit": "#C9D0D0", "col_cloud_shadow": "#7C878C", "col_band": "#B8C2C4", "band_energy": 0.0,
                 "col_glow": "#D8DEDE", "cloud_sun_energy": 1.6, "cloud_ambient_energy": 1.2, "col_zenith": "#8A98A4",
                 "col_ground": "#5E6A70"}


def _zone_grade() -> dict:
    a = ar.LOWLIGHT_ARENA
    return dict(a, sub_frame="ch11", lut=LUT, sky=dict(a["sky"], **OVERCAST_NOON))


WATER_OVERRIDES = {"foam_crest_threshold": 0.15}  # still water: no crest foam (lagoon waves crest at the default 0.9)


def write_waves(out: Path) -> None:
    """The arena's still water (no wind reaches the Vey, lowlight.md §0) as the zone's WaveSet."""
    waves = ar.LOWLIGHT_ARENA["sea"]["waves"]
    lines = [f'[gd_resource type="Resource" script_class="WaveSet" load_steps={len(waves) + 3} format=3]', "",
             '[ext_resource type="Script" path="res://game/world/water/wave_set.gd" id="1_set"]',
             '[ext_resource type="Script" path="res://game/world/water/wave_component.gd" id="2_comp"]', ""]
    for k, (d, wl, amp, st) in enumerate(waves):
        lines += [f'[sub_resource type="Resource" id="Wave_{k}"]', 'script = ExtResource("2_comp")',
                  f"direction_deg = {d}", f"wavelength_m = {wl}", f"amplitude_m = {amp}", f"steepness = {st}",
                  "phase_rad = 0.0", ""]
    ids = ", ".join(f'SubResource("Wave_{k}")' for k in range(len(waves)))
    lines += ["[resource]", 'script = ExtResource("1_set")', f'components = Array[ExtResource("2_comp")]([{ids}])',
              "amplitude_scale = 1.0"]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_water_material(out: Path) -> None:
    m = ar.OVERCAST_LAGOON
    lines = ['[gd_resource type="ShaderMaterial" load_steps=2 format=3]', "",
             f'[ext_resource type="Shader" path="{m["shader"]}" id="1_ocean"]', "", "[resource]",
             f'resource_name = "{m["name"].replace("arena_", "")}"', "render_priority = 0",
             'shader = ExtResource("1_ocean")']
    for k, v in [(k, WATER_OVERRIDES.get(k, v)) for k, v in m["params"]]:
        if isinstance(v, str) and v.startswith("#"):
            c = [int(v[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            v = f"Color({c[0]:.4f}, {c[1]:.4f}, {c[2]:.4f}, 1)"
        lines.append(f"shader_parameter/{k} = {v}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


# Ten composed cameras per zone (the beat sheet's L/V/T/N frames among them; SPEC §8.4): (name, pos, look_at, fov)
CAMERAS = {
    "sunken_vey": [
        ("V01_landing", (-8.0, 3.0, 4.0), (30.0, 1.0, -14.0), 45.0),
        ("L01_mouth", (-10.0, 1.2, 2.0), (40.0, 3.0, -6.0), 50.0),
        ("V02_gallery", (6.0, 1.7, 0.5), (24.0, 1.0, -2.0), 50.0),
        ("V03_bend", (24.0, 1.7, -1.5), (33.0, 1.2, -14.0), 50.0),
        ("L03_court", (40.0, 1.7, -18.0), (34.0, 1.3, -29.0), 50.0),
        ("V04_mark", (34.6, 1.55, -27.3), (34.0, 1.35, -29.0), 40.0),
        ("Side_fig_end", (38.0, 1.7, -36.0), (38.0, 3.0, -57.0), 50.0),
        ("Out_gallery", (50.0, 1.7, -20.5), (80.0, 2.0, -16.0), 50.0),
        ("Gate_lowlight", (82.0, 1.7, -16.0), (96.0, 4.0, -16.0), 55.0),
        ("Overhead", (45.0, 45.0, 30.0), (45.0, 0.0, -22.0), 55.0),
    ],
}
CLS = {"sunken_vey": "SunkenVey", "lowlight": "Lowlight"}


def write_preview(zone: str) -> Path:
    lines = ["[gd_scene format=3]", "",
             '[ext_resource type="Script" path="res://game/levels/ch11/ch11_zone.gd" id="1_zone"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_kit_dressing.gd" id="2_dressing"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/weathering_tide.gd" id="3_tide"]',
             '[ext_resource type="Script" path="res://game/world/water/water_surface.gd" id="4_water"]',
             f'[ext_resource type="Resource" path="res://game/levels/ch11/{zone}/{zone}_waves.tres" id="5_waves"]',
             f'[ext_resource type="Material" path="res://game/levels/ch11/{zone}/{zone}_water_material.tres" id="6_mat"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="7_cast"]', "",
             f'[node name="{CLS[zone]}" type="Node3D"]', 'script = ExtResource("1_zone")', f'location_id = &"ch11/{zone}"',
             f'layout_path = "res://game/levels/ch11/{zone}/{zone}_layout.json"', "",
             '[node name="Cast" type="Node" parent="."]', 'script = ExtResource("7_cast")', "",
             '[node name="Water" type="Node3D" parent="."]',
             f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {vz.WATER_Y}, 0)", 'script = ExtResource("4_water")',
             "publishes_water_level = true", 'wave_set = ExtResource("5_waves")', 'material = ExtResource("6_mat")',
             "amplitude_scale = 1.0", "",
             '[node name="Tide" type="Node" parent="." node_paths=PackedStringArray("water")]',
             'script = ExtResource("3_tide")', f"tide_line_y = {vz.WATER_Y}", f"water_height_y = {vz.WATER_Y}",
             'water = NodePath("../Water")', "",
             '[node name="Dressing" type="Node3D" parent="." node_paths=PackedStringArray("tide")]',
             'script = ExtResource("2_dressing")', f'layout_path = "res://game/levels/ch11/{zone}/{zone}_dressing.json"',
             'tide = NodePath("../Tide")', "", '[node name="Cameras" type="Node3D" parent="."]', ""]
    for name, pos, look, fov in CAMERAS[zone]:
        lines += [f'[node name="{name}" type="Camera3D" parent="Cameras"]', f"fov = {fov}", "near = 0.1", "far = 1500.0",
                  f"transform = {fen._look_xform(pos, look)}", ""]
    out = PREVIEW / f"{zone}_dressed.tscn"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    return out


def main() -> int:
    for zone in ("sunken_vey",):
        out = ZONES / zone
        ar.write_environment(_zone_grade(), out / f"{zone}_environment.tres")
        write_water_material(out / f"{zone}_water_material.tres")
        write_waves(out / f"{zone}_waves.tres")
        lay = layout(zone)
        (out / f"{zone}_dressing.json").write_text(json.dumps(lay, indent=1) + "\n", encoding="utf-8")
        write_preview(zone)
        print(f"DRESSING {zone}: {len(lay['pieces'])} pieces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
