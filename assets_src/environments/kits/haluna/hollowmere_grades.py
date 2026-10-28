"""Hollowmere's grade (M3-ENV-723; colour script `ch17`, hollowmere.md §0): the Environment and the sun row for the
Ch17 zone's light, at dusk over the raft-city.

    python3 assets_src/environments/kits/haluna/hollowmere_grades.py

Writes assets/environments/zones/ch17/ch17_hollowmere_dusk_environment.tres (the battle arenas' sky, fog, tonemap and
LUT writer, arena_scenes.write_environment, read-only), lut_act3_dusk.png (zone_lut.py `act3_dusk`) and
ch17_grades.json: the Environment and its sun row ({"pitch_deg", "yaw_deg", "color", "energy"}: pitch = -elevation,
yaw = 180 - azimuth, as Ch5's and Ch6's).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "brine_shoals"))
import arena_scenes as ar  # noqa: E402  (write_environment, CORROW_SKY, LOW_SUN_SKY; read-only)
from bs_grades import sun_yaw  # noqa: E402  (the zones' sun-row convention; read-only)

OUT = ROOT / "assets" / "environments" / "zones" / "ch17"
RES = "res://assets/environments/zones/ch17/"

GRADES = {
    # Dusk, 18:10, long gold light over the raft-city: sun 8 deg at 280 deg, key #FFB16E 2.4, fill #5A7FA8 0.45, sky
    # #3E5A86 over a #F2A64A horizon, the warm fog thin (0.008), exposure 0.85.
    "ch17_hollowmere_dusk": {
        "lut_name": "lut_act3_dusk",
        "sun": {"elev": 8.0, "az": 280.0, "color": "#FFB16E", "energy": 2.4},
        "fill": {"color": "#5A7FA8", "energy": 0.45},
        "exposure": 0.85,
        "fog": {"color": "#C8986A", "aerial": 0.5, "density": 0.008, "sky_affect": 0.2, "height": 0.0,
                "height_density": 0.0},
        "sky": dict(ar.CORROW_SKY, col_zenith="#3E5A86", col_horizon_sun="#F2A64A", col_horizon_away="#8A8FA0",
                    col_ground="#2A2E36", sky_energy=1.0, sun_disc_energy=3.0, halo_energy=0.9, glow_energy=0.6,
                    cloud_coverage=0.35, col_cloud_lit="#F6C08A", col_cloud_shadow="#5A6078"),
    },
}
LUT_JOBS = {"lut_act3_dusk": [str(HERE / "zone_lut.py"), "--grade", "act3_dusk"]}


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
    (OUT / "ch17_grades.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
