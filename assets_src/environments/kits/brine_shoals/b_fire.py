"""The raid's fires (env-art-b, M3-ENV-1313; act1_ch06.md B04 "by the burning hulk"). Pure numpy.

  camp_fire_large   a bed of charred timbers and embers 3 m across with eleven flame tongues up to 2.6 m, leaning
                    downwind (-X), the camp's main burning (the tide-wheel's foot, the hulk)
  camp_fire_small   the same at 1.6 m across with six tongues up to 1.2 m (a tent's ash bed, the salvage pile)

Sculpted flames over `bs_char` timbers, an ember bed (`bs_ember`) and an ash ring, so the burning reads at battle and
story distance. The tongues take this module's own two materials (`bs_fire_outer`, a deep ember_orange, and
`bs_fire_core`, a yellow heart), since `bs_ember`'s emission blooms to white in the ch06 daylight: ShaderMaterials on
`game/vfx/fire/flame_tongue.gdshader` (M3-RND-1315), which licks, tears and flickers the tongues on the held weather
clock. Origin at the bed's centre on the ground.

    python3 assets_src/environments/kits/brine_shoals/b_fire.py     # writes the two materials
"""

from __future__ import annotations

import math

import numpy as np

import bs_common as bc
from bs_common import kc

M_OUTER = "bs_fire_outer"
M_CORE = "bs_fire_core"
SHADER = "res://game/vfx/fire/flame_tongue.gdshader"
# Unshaded: the flame is its own light. Palette swatches: the tongues dusk_gold at the foot to ember_orange at the tip,
# the heart sun_gold to dusk_gold (an ember_orange foot went flat red under the ch06 grade, an oil_lamp one peach). The
# heart is short, so it tears less.
MATERIALS = {
    M_OUTER: {"base_color": (0.949, 0.651, 0.29), "tip_color": (0.878, 0.439, 0.18), "emission": 0.0, "tear": 0.55,
              "heart_gain": 1.2},
    M_CORE: {"base_color": (1.0, 0.824, 0.478), "tip_color": (0.949, 0.651, 0.29), "emission": 0.0, "tear": 0.3,
             "heart_gain": 0.95},  # sun_gold already: a heart gain over it went cream up close
}
TRI_BUDGET = {"camp_fire_large": (9000, 1200), "camp_fire_small": (5000, 700)}

LEAN = np.array([-0.35, 0.0, 0.08])  # downwind (the preview's wind is toward 240 deg: -X, a little +Z)
STILL = kc.Weathering(moss=0.0, salt=0.0, wet=0.0, erosion=0.0)


def _tongue(mb: kc.MeshBuilder, base, height: float, radius: float, rng, *, lod: bool, mat: str = M_OUTER) -> None:
    """A flame tongue: a twisting, tapering tube from a wide foot to a point, leaning downwind (each its own way)."""
    n = 5 if lod else 9
    t = np.linspace(0.0, 1.0, n)
    phase = float(rng.uniform(0.0, 2.0 * math.pi))
    wob = rng.uniform(0.15, 0.45) * radius * np.sin(t * rng.uniform(3.0, 6.0) + phase)
    lean = LEAN * rng.uniform(0.3, 1.6) + np.array([rng.uniform(-0.15, 0.15), 0.0, rng.uniform(-0.15, 0.15)])
    bend = t ** rng.uniform(1.3, 2.2)
    centers = (np.asarray(base, float) + np.outer(t, [0.0, height, 0.0]) + np.outer(bend, lean * height)
               + np.stack([wob, np.zeros(n), np.cos(t * 4.0 + phase) * 0.12 * radius], axis=-1))
    radii = radius * np.sin(np.pi * np.clip(t * 0.8 + 0.12, 0.0, 1.0)) ** 0.7 * (1.0 - 0.85 * t)
    kc.tube(mb, centers, np.maximum(radii, radius * 0.02), 5 if lod else 7, mb.material(mat),
            cap_start=True, cap_end=True, weather=STILL)


def _ragged_disc(radius: float, n: int, rng) -> np.ndarray:
    """A round outline (x, z) with a little ragged edge, kept convex (polygon_prism's outline)."""
    a = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    rr = radius * (1.0 - 0.06 * rng.uniform(0.0, 1.0, n))
    return np.stack([np.cos(a) * rr, np.sin(a) * rr], axis=-1)


def fire(name: str, seed: int, *, size: float, tongues: int, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
    r = size * 0.5
    # The ash ring and the char bed: crossed timbers burned black, embers between them. The ash is a low, ragged
    # round bed (a square block read as a tray under the fire up close).
    kc.polygon_prism(mb, _ragged_disc(r * 1.1, 10 if lod else 18, rng), 0.0, 0.04, mb.material(bc.M_ASH),
                     col=np.zeros(4), uv2=np.zeros(2))
    for k in range(3 if lod else 6):
        a = rng.uniform(0.0, math.pi)
        ln = r * rng.uniform(1.2, 1.9)
        kc.rounded_block(mb, (rng.uniform(-r, r) * 0.3, 0.09 + 0.05 * k, rng.uniform(-r, r) * 0.3),
                         (ln * 0.5, 0.07, 0.09), mb.material(bc.M_CHAR), rot=kc.rot_y(a), radius=0.04, seg=1,
                         weather=STILL)
    kc.polygon_prism(mb, _ragged_disc(r * 0.7, 8 if lod else 14, rng), 0.06, 0.16, mb.material(bc.M_EMBER),
                     col=np.zeros(4), uv2=np.zeros(2))
    # The tongues: tallest at the heart, shorter to the rim.
    for k in range(tongues):
        a = 2.0 * math.pi * k / tongues + rng.uniform(-0.3, 0.3)
        d = r * (0.15 + 0.6 * math.sqrt(rng.uniform(0.0, 1.0)))
        tall = size * 0.85 * (1.0 - 0.55 * d / r) * rng.uniform(0.7, 1.05)
        _tongue(mb, (d * math.cos(a), 0.12, d * math.sin(a)), tall, size * rng.uniform(0.09, 0.14), rng, lod=lod)
    # The yellow heart: shorter tongues inside the ring.
    for k in range(max(2, tongues // 3)):
        a = rng.uniform(0.0, 2.0 * math.pi)
        d = r * 0.2 * rng.uniform(0.0, 1.0)
        _tongue(mb, (d * math.cos(a), 0.14, d * math.sin(a)), size * rng.uniform(0.3, 0.5), size * 0.08, rng,
                lod=lod, mat=M_CORE)
    return mb


def write_materials() -> None:
    from pathlib import Path

    out = Path(__file__).resolve().parents[4] / "assets" / "environments" / "kits" / "brine_shoals" / "materials"
    for name, m in MATERIALS.items():
        lines = ['[gd_resource type="ShaderMaterial" load_steps=2 format=3]', "",
                 f'[ext_resource type="Shader" path="{SHADER}" id="1_flame"]', "", "[resource]",
                 f'resource_name = "{name}"', 'shader = ExtResource("1_flame")']
        for key in ("base_color", "tip_color"):
            r, g, b = m[key]
            lines.append(f"shader_parameter/{key} = Color({r}, {g}, {b}, 1)")
        for key in ("emission", "tear", "heart_gain"):
            lines.append(f"shader_parameter/{key} = {m[key]}")
        (out / f"{name}.tres").write_text("\n".join(lines) + "\n", encoding="utf-8")


TARGETS = {
    "camp_fire_large": lambda: [fire("camp_fire_large", 771, size=3.0, tongues=11),
                                fire("camp_fire_large", 771, size=3.0, tongues=7, lod=True)],
    "camp_fire_small": lambda: [fire("camp_fire_small", 772, size=1.6, tongues=6),
                                fire("camp_fire_small", 772, size=1.6, tongues=4, lod=True)],
}


if __name__ == "__main__":
    write_materials()
