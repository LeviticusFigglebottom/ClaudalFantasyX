"""The Ending's grades (M3-ENV-729; colour script `ending_unbinding`, `ending_dock`, `post_credits`;
act3_ending.md E1-E7): the Environment and the key row for each of the three frames the game closes on.

    python3 assets_src/environments/kits/haluna/ending_grades.py

Writes assets/environments/zones/ending/<frame>_environment.tres (the battle arenas' sky, fog, tonemap and LUT
writer, arena_scenes.write_environment, read-only), the three LUTs (zone_lut.py `ending_lift`, `ending_dock`,
`post_credits`) and ending_grades.json: per frame the Environment, its key row ({"pitch_deg", "yaw_deg", "color",
"energy"}, as Ch17's), its rim row ({"color", "energy"}, the stager's to place per shot) and its sea-glow.
`ending_unbinding` also carries the sea-glow steps E1-E5 (act3_ending.md §0 rule 4).
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

OUT = ROOT / "assets" / "environments" / "zones" / "ending"
RES = "res://assets/environments/zones/ending/"
NIGHT_SKY = "res://game/shaders/environment/env_sky_night.gdshader"

GRADES = {
    # The lifting, 23:00 over the open sea: no sun; the key is the leaving person's rising motes #FFDCBF 0.8 (placed
    # high, as their light climbs), fill #0B1630 0.15, rim #FFE9B8 1.2, sky #050A14 / #0B1630, fog #0B1630 thin,
    # exposure 1.15. The Kite's lamps are dark from H09 on; no moon.
    "ending_unbinding": {
        "lut_name": "lut_ending_lift",
        "sun": {"elev": 40.0, "az": 0.0, "color": "#FFDCBF", "energy": 0.8},
        "rim": {"color": "#FFE9B8", "energy": 1.2},
        "fill": {"color": "#0B1630", "energy": 0.15},
        "exposure": 1.15,
        "glow": (0.7, 0.1, 0.9),
        "fog": {"color": "#0B1630", "density": 0.004, "sky_affect": 0.4, "height": 0.0, "height_density": 0.0},
        "sky_shader": NIGHT_SKY,
        "sky": {"col_zenith": "#050A14", "col_horizon": "#0B1630", "col_ground": "#061A2B", "moon_disc_energy": 0.0,
                "moon_halo": 0.0, "star_density": 0.08, "star_energy": 1.6},
        "sea_glow": 0.15,
        "sea_glow_steps": {"E1": 0.15, "E2": 0.11, "E3": 0.08, "E4": 0.07, "E5": 0.06},
    },
    # The final image, Haluna's dock at 01:00, moonless and clear: starlight key #D2DFFF 0.25, fill #0B1630 0.1, rim
    # #DCE6FF 0.3; sky #050A14 / #0B1428, no fog, exposure 1.2. The sea-glow is 0.0, the first time in the game:
    # stars above and stars below.
    "ending_dock": {
        "lut_name": "lut_ending_dock",
        "sun": {"elev": 60.0, "az": 200.0, "color": "#D2DFFF", "energy": 0.25},
        "rim": {"color": "#DCE6FF", "energy": 0.3},
        "fill": {"color": "#0B1630", "energy": 0.1},
        "exposure": 1.2,
        "glow": (0.6, 0.08, 1.0),
        "fog": {"color": "#050A14", "density": 0.0, "sky_affect": 0.0, "height": 0.0, "height_density": 0.0},
        "sky_shader": NIGHT_SKY,
        "sky": {"col_zenith": "#050A14", "col_horizon": "#0B1428", "col_ground": "#050A14", "moon_disc_energy": 0.0,
                "moon_halo": 0.0, "star_density": 0.2, "star_energy": 3.0, "star_horizon_fade": 0.08},
        "sea_glow": 0.0,
    },
    # Post-credits, Oruvel rebuilt at 05:10, blue hour: the sun 6 deg below the east horizon; the key #FFAE67 1.4 is
    # Mother Kell's oil lamp (the stager places it; the row is its colour and energy), fill #3A5A8A 0.35, rim
    # #9DB4D9 0.4, sky #1A2E58 over #6E7FA8, fog #3A4A6A 0.006, exposure 1.05. No glimmer anywhere.
    "post_credits": {
        "lut_name": "lut_post_credits",
        "sun": {"elev": 12.0, "az": 90.0, "color": "#9DB4D9", "energy": 0.4},
        "lamp": {"color": "#FFAE67", "energy": 1.4},
        "rim": {"color": "#9DB4D9", "energy": 0.4},
        "fill": {"color": "#3A5A8A", "energy": 0.35},
        "exposure": 1.05,
        "fog": {"color": "#3A4A6A", "aerial": 0.5, "density": 0.006, "sky_affect": 0.3, "height": 0.0,
                "height_density": 0.0},
        "sky_shader": ar.LOW_SUN_SKY,
        "sky": dict(ar.CORROW_SKY, col_zenith="#1A2E58", col_horizon_sun="#8A8FB8", col_horizon_away="#6E7FA8",
                    col_ground="#1E2A40", sky_energy=0.8, sun_disc_energy=0.0, halo_energy=0.3, glow_energy=0.3,
                    cloud_coverage=0.2, col_cloud_lit="#9AA6C8", col_cloud_shadow="#3A4A6A"),
        "sea_glow": 0.0,
    },
}
LUT_JOBS = {"lut_ending_lift": "ending_lift", "lut_ending_dock": "ending_dock", "lut_post_credits": "post_credits"}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, grade in LUT_JOBS.items():
        subprocess.run([sys.executable, str(HERE / "zone_lut.py"), "--grade", grade, "--out", str(OUT / f"{name}.png")],
                       check=True)
    rows = {"_doc": __doc__.split("\n\n")[0].replace("\n", " ")}
    for name, g in GRADES.items():
        spec = dict(g, sub_frame=name, lut=RES + g["lut_name"] + ".png")
        out = ar.write_environment(spec, OUT / f"{name}_environment.tres")
        s = g["sun"]
        rows[name] = {"environment": RES + out.name,
                      "sun": {"pitch_deg": -s["elev"], "yaw_deg": sun_yaw(s["az"]), "color": s["color"],
                              "energy": s["energy"]},
                      "rim": g["rim"], "sea_glow": g["sea_glow"]}
        for k in ("lamp", "sea_glow_steps"):
            if k in g:
                rows[name][k] = g[k]
        print(f"GRADE {out.relative_to(ROOT)}")
    (OUT / "ending_grades.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
