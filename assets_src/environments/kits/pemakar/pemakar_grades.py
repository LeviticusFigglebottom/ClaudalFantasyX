"""Ch5's sub-frame grades (M3-C05-03; act1_ch05.md §9.4; colour script `ch05_harbour_dusk`, `ch05_ashcrown_day`): an
Environment each, and the sun each wants, for the Ch5 zones' light rows.

    python3 assets_src/environments/kits/pemakar/pemakar_grades.py

Writes assets/environments/zones/ch05/ch05_<grade>_environment.tres (the battle arenas' sky, fog, tonemap and LUT
writer, haluna/arena_scenes.write_environment, read-only) and ch05_grades.json: per grade, its Environment and its sun
row ({"pitch_deg", "yaw_deg", "color", "energy"}: pitch = -elevation, yaw = 180 - azimuth, as Ch6's). The LUTs:
`lut_ch05_harbour_dusk` from haluna/zone_lut.py, `lut_ch05_ashcrown` from ashcrown/ac_zone_lut.py (both written here).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "haluna"))
sys.path.insert(0, str(HERE.parent / "brine_shoals"))
import arena_scenes as ar  # noqa: E402  (write_environment, CORROW_SKY, LOW_SUN_SKY; read-only)
from bs_grades import sun_yaw  # noqa: E402  (the zones' sun-row convention; read-only)

OUT = ROOT / "assets" / "environments" / "zones" / "ch05"
RES = "res://assets/environments/zones/ch05/"

GRADES = {
    # Pemakar's harbour at dusk (B01, about 19:15): the sun 3 degrees down, so the key is the afterglow low in the
    # west; the blue hour overhead; the town's first lanterns are the zone's own lamps.
    "ch05_harbour_dusk": {
        "lut_name": "lut_ch05_harbour_dusk",
        "sun": {"elev": 2.0, "az": 290.0, "color": "#E08A5A", "energy": 0.35},
        "fill": {"color": "#5A6A8A", "energy": 0.45},
        "exposure": 0.95,
        "fog": {"color": "#4A4458", "aerial": 0.5, "density": 0.008, "sky_affect": 0.2, "height": 0.0,
                "height_density": 0.0},
        "sky": dict(ar.CORROW_SKY, col_zenith="#1E2E52", col_horizon_sun="#E89A6A", col_horizon_away="#4A4E6E",
                    col_ground="#1A1E28", sky_energy=0.8, sun_disc_energy=0.0, halo_energy=0.6, glow_energy=0.5,
                    cloud_coverage=0.45, col_cloud_lit="#E8A07A", col_cloud_shadow="#3A3A52"),
    },
    # Ashcrown by day (11:30-14:00): ashcrown.md's `ch05_temple` frame (13:00), the sun through the ash veil.
    "ch05_ashcrown_day": {
        "lut_name": "lut_ch05_ashcrown",
        "sun": {"elev": 58.0, "az": 225.0, "color": "#FFF0DC", "energy": 2.8},
        "fill": {"color": "#8E959C", "energy": 0.45},
        "exposure": 0.72,
        "fog": {"color": "#8C8882", "aerial": 0.5, "density": 0.0018, "sky_affect": 0.15, "height": 0.0,
                "height_density": 0.0},
        "sky": dict(ar.CORROW_SKY, col_zenith="#5F6E80", col_horizon_sun="#D6C8B2", col_horizon_away="#C9BCA7",
                    col_ground="#4A4846", sky_energy=1.2, sun_disc_energy=4.0, halo_energy=0.8, glow_energy=0.4,
                    cloud_coverage=0.55, col_cloud_lit="#E6E0D6", col_cloud_shadow="#8A8C90"),
    },
}
LUT_JOBS = {
    "lut_ch05_harbour_dusk": [str(HERE.parent / "haluna" / "zone_lut.py"), "--grade", "ch05_harbour_dusk"],
    "lut_ch05_ashcrown": [str(HERE.parent / "ashcrown" / "ac_zone_lut.py")],
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, cmd in LUT_JOBS.items():
        subprocess.run([sys.executable, *cmd, "--out", str(OUT / f"{name}.png")], check=True)
    rows = {"_doc": __doc__.split("\n\n")[0].replace("\n", " ")}
    for name, g in GRADES.items():
        spec = dict(g, sub_frame=name, lut=RES + g["lut_name"] + ".png", sky_shader=ar.LOW_SUN_SKY)
        out = ar.write_environment(spec, OUT / f"{name}_environment.tres")
        s = g["sun"]
        rows[name] = {"environment": RES + out.name,
                      "sun": {"pitch_deg": -s["elev"], "yaw_deg": sun_yaw(s["az"]), "color": s["color"],
                              "energy": s["energy"]}}
        print(f"GRADE {out.relative_to(ROOT)}")
    (OUT / "ch05_grades.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
