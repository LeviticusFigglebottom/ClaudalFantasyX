"""Ch6's sub-frame grades (M3-C06-03 item 7; colour script `ch06_hold`, `ch06_dusk`, `ch06_dawn`): an Environment
each, and the sun each wants, for Ch06Zone's light rows.

    python3 assets_src/environments/kits/brine_shoals/bs_grades.py

Writes assets/environments/zones/brine_shoals/ch06_<grade>_environment.tres (the battle arenas' sky, fog, tonemap and
LUT writer, arena_scenes.write_environment, read-only) and ch06_grades.json: per grade, its Environment and its sun
row ({"pitch_deg", "yaw_deg", "color", "energy"}, Ch06Zone's `sun` row fields: pitch = -elevation,
yaw = 180 - azimuth). The LUTs are bs_zone_lut.py's
(`--grade hold|dusk|dawn`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "haluna"))
import arena_scenes as ar  # noqa: E402  (write_environment, CORROW_SKY, LOW_SUN_SKY; read-only)

OUT = ROOT / "assets" / "environments" / "zones" / "brine_shoals"
RES = "res://assets/environments/zones/brine_shoals/"

GRADES = {
    # The dark hold (B03, W08): keyed only by Rhen's oil lamp (the cutscene's lantern light, palette oil_lamp
    # #FFB16E); the afternoon comes in as slivers through the planks; smoke hangs in it.
    "ch06_hold": {
        "sun": {"elev": 35.0, "az": 240.0, "color": "#FFD5B3", "energy": 0.6},
        "fill": {"color": "#3A3028", "energy": 0.25},
        "exposure": 1.35,
        "fog": {"color": "#4A3C30", "aerial": 0.0, "density": 0.04, "sky_affect": 0.0, "height": 0.0,
                "height_density": 0.0},
        "sky": dict(ar.CORROW_SKY, col_zenith="#5A5048", col_horizon_sun="#8A6A50", col_horizon_away="#6A5A4E",
                    col_ground="#2A2420", sky_energy=0.3, sun_disc_energy=0.0, halo_energy=0.0, glow_energy=0.0,
                    cloud_coverage=0.9),
    },
    # Dusk on the wreck-ridge and the tideline (B08-B09, W15-W16, 18:30-18:45): the sun at 2 degrees through smoke,
    # smoke-red; slate-violet shadows.
    "ch06_dusk": {
        "sun": {"elev": 2.0, "az": 280.0, "color": "#FF8A4A", "energy": 1.2},
        "fill": {"color": "#5A6E80", "energy": 0.45},
        "exposure": 0.85,
        "fog": {"color": "#9A7A64", "aerial": 0.5, "density": 0.02, "sky_affect": 0.3, "height": 0.0,
                "height_density": 0.0},
        "sky": dict(ar.CORROW_SKY, col_zenith="#4A5A78", col_horizon_sun="#E07A48", col_horizon_away="#8A7A80",
                    col_ground="#3A3430", sky_energy=1.0, sun_disc_energy=6.0, halo_energy=1.0, glow_energy=0.8,
                    cloud_coverage=0.6, col_cloud_lit="#F0A070", col_cloud_shadow="#5A4A58"),
    },
    # The channel at dawn (B10, day 4 06:00): ash lying flat on the water; Tamsule's gilt catching the sun on the
    # horizon; a clean, cool morning after.
    "ch06_dawn": {
        "sun": {"elev": 4.0, "az": 75.0, "color": "#FFE2C2", "energy": 1.6},
        "fill": {"color": "#8FA6BC", "energy": 0.6},
        "exposure": 0.8,
        "fog": {"color": "#C8C4B8", "aerial": 0.5, "density": 0.012, "sky_affect": 0.2, "height": 0.0,
                "height_density": 0.0},
        "sky": dict(ar.CORROW_SKY, col_zenith="#6E8CB0", col_horizon_sun="#F2D4B0", col_horizon_away="#B8C0C8",
                    col_ground="#4A4A48", sky_energy=1.1, sun_disc_energy=6.0, halo_energy=0.8, glow_energy=0.5,
                    cloud_coverage=0.4, col_cloud_lit="#FFE8CC", col_cloud_shadow="#8A90A0"),
    },
}


def sun_yaw(az_deg: float) -> float:
    """Ch06Zone's sun yaw for an azimuth (clockwise from north = -Z): the light's +Z points at the sun, so
    yaw = 180 - azimuth (the layout's own row: azimuth 240 is yaw -60), folded into (-180, 180]."""
    y = (180.0 - az_deg) % 360.0
    return y - 360.0 if y > 180.0 else y


def main() -> int:
    rows = {"_doc": __doc__.split("\n\n")[0].replace("\n", " ")}
    for name, g in GRADES.items():
        short = name.removeprefix("ch06_")
        spec = dict(g, sub_frame=name, lut=RES + f"lut_ch06_{short}.png", sky_shader=ar.LOW_SUN_SKY)
        out = ar.write_environment(spec, OUT / f"{name}_environment.tres")
        s = g["sun"]
        rows[name] = {"environment": RES + out.name,
                      "sun": {"pitch_deg": -s["elev"], "yaw_deg": sun_yaw(s["az"]), "color": s["color"],
                              "energy": s["energy"]}}
        print(f"GRADE {out.relative_to(ROOT)}")
    (OUT / "ch06_grades.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
