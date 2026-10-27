"""Writes assets/environments/zones/iskarra/iskarra_city.tscn: the Prologue's Iskarra from the iskarra.py kit pieces
(M3-ENV-710). Each piece stands where the Prologue's primitive city put its box or cylinder (game/levels/prologue/
prologue.tscn, City), so the shots keep their composition: a drop-in for the City's Terrace, Rise, Towers, Arches and
LampColumns. The level keeps its own Water and Vigils. Sea at y 0; the towers' feet at y -3 (their waterline band).

Run: python3 assets_src/environments/kits/haluna/iskarra_city.py [--out PATH]
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT_DEFAULT = ROOT / "assets" / "environments" / "zones" / "iskarra" / "iskarra_city.tscn"
KIT = "res://assets/environments/kits/haluna/"

TOWER_FOOT_Y = -3.0
# (node, piece, x, y, z, yaw_deg, scale_xz, scale_y). Towers keep the primitive's foot radius and top height (cap
# included): A 6/59.8, B 5/46, C 4/22 broken, D 7/67.6, E 4.5/35.4, F 6/52.6, G 5.5/40.6, H 3/14 broken, I 3.5/20.7.
PIECES = (
    ("Plaza", "iskarra_plaza", 0.0, 0.4, 2.0, 0.0, 1.0, 1.0),
    ("Rise", "iskarra_plaza_rise", -3.0, 0.2, -2.0, 0.0, 1.0, 1.0),
    ("TowerA", "iskarra_tower_spire", -46.0, TOWER_FOOT_Y, -70.0, 20.0, 1.0, 1.0),
    ("TowerB", "iskarra_tower_stepped", -24.0, TOWER_FOOT_Y, -92.0, 0.0, 0.91, 1.0),
    ("TowerC", "iskarra_tower_broken", -8.0, TOWER_FOOT_Y, -60.0, 140.0, 0.8, 0.6),
    ("TowerCCrown", "iskarra_crown_fallen", -1.6, 0.0, -56.0, -25.0, 1.0, 1.0),
    ("TowerD", "iskarra_tower_spire", 14.0, TOWER_FOOT_Y, -84.0, -35.0, 1.17, 1.12),
    ("TowerE", "iskarra_tower_stepped", 34.0, TOWER_FOOT_Y, -66.0, 60.0, 0.82, 0.77),
    ("TowerF", "iskarra_tower_spire", 58.0, TOWER_FOOT_Y, -100.0, 75.0, 1.0, 0.88),
    ("TowerG", "iskarra_tower_spire", -70.0, TOWER_FOOT_Y, -110.0, -60.0, 0.92, 0.68),
    ("TowerH", "iskarra_tower_small_broken", 26.0, TOWER_FOOT_Y, -40.0, 200.0, 1.0, 1.0),
    ("TowerHCrown", "iskarra_crown_fallen", 30.8, 0.0, -37.0, 155.0, 0.8, 0.8),
    ("TowerI", "iskarra_tower_small", -34.0, TOWER_FOOT_Y, -44.0, 10.0, 1.0, 1.0),
    ("Arch", "iskarra_arch", -14.2, -0.5, -18.0, 0.0, 1.0, 1.0),
    ("ArchFallen", "iskarra_arch_fallen", 19.8, -0.5, -22.0, 0.0, 1.0, 1.0),
    ("Lamp0", "iskarra_lamp_column", -15.0, 0.4, -6.2, 0.0, 1.0, 1.0),
    ("Lamp1", "iskarra_lamp_column", -5.0, 0.4, -6.2, 90.0, 1.0, 1.0),
    ("Lamp2", "iskarra_lamp_column", 5.0, 0.4, -6.2, 180.0, 1.0, 1.0),
    ("Lamp3", "iskarra_lamp_column", 15.0, 0.4, -6.2, 270.0, 1.0, 1.0),
    # M3-ENV-724: the drowned midground between the plaza and the towers (the sea at y 0), so the water between them
    # reads as a flooded city, not an empty plane: two buildings' top storeys, two domed blocks, a sunk arcade.
    ("DrownedBlockA", "iskarra_drowned_block", -30.0, 0.0, -30.0, 12.0, 1.0, 1.0),
    ("DrownedBlockB", "iskarra_drowned_block", 44.0, 0.0, -46.0, -25.0, 1.1, 1.0),
    ("DrownedDomeA", "iskarra_drowned_dome", -58.0, 0.0, -52.0, 30.0, 1.0, 1.0),
    ("DrownedDomeB", "iskarra_drowned_dome", 38.0, 0.0, -24.0, 8.0, 0.9, 0.9),
    ("ArcadeSunk", "iskarra_arcade_sunk", -40.0, 0.0, -20.0, 75.0, 1.0, 1.0),
)


def _xform(x: float, y: float, z: float, yaw_deg: float, sxz: float, sy: float) -> str:
    """Transform3D(basis rows..., origin): Basis(UP, yaw) scaled by (sxz, sy, sxz)."""
    c, s = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    rows = ((c * sxz, 0.0, s * sxz), (0.0, sy, 0.0), (-s * sxz, 0.0, c * sxz))
    vals = [v for r in rows for v in r] + [x, y, z]
    return "Transform3D(" + ", ".join(f"{round(v, 5):g}" for v in vals) + ")"


def scene_text() -> str:
    glbs = sorted({p[1] for p in PIECES})
    ids = {g: f"{i + 1}_{g}" for i, g in enumerate(glbs)}
    lines = [f"[gd_scene load_steps={len(glbs) + 1} format=3]", ""]
    for g in glbs:
        lines.append(f'[ext_resource type="PackedScene" path="{KIT}{g}.glb" id="{ids[g]}"]')
    lines += ["", '[node name="IskarraCity" type="Node3D"]']
    for node, piece, x, y, z, yaw, sxz, sy in PIECES:
        lines += ["", f'[node name="{node}" parent="." instance=ExtResource("{ids[piece]}")]',
                  f"transform = {_xform(x, y, z, yaw, sxz, sy)}"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--check", action="store_true", help="fail if the committed scene differs")
    args = ap.parse_args(argv)
    out = Path(args.out)
    text = scene_text()
    if args.check:
        ok = out.is_file() and out.read_text() == text
        print("ISKARRA_CITY " + ("OK" if ok else f"STALE {out}"))
        return 0 if ok else 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"ISKARRA_CITY {len(PIECES)} pieces -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
