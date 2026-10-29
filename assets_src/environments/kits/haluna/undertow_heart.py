"""The Heart of the Undertow (Ch21; undertow_layers.md §3; M3-ENV-728): the storm's centre, where Imra holds it
together with Dace beside her, and Sefir is fought. Pure numpy.

  heart_floor    the floor of held light the party walks to the centre on (act3_ending H01): a disc (r 11) of salt-glass
                 plates over held glimmer, the seams between them lit, a step down at its rim to the still water (-0.3).
                 Flat at y 0 round the battle slots.
  heart_column   Imra's light: a column of held glimmer rising out of the water at the centre, three nested
                 translucent sleeves round a bright core, a ring of light on the water at its foot. 40 m.
  heart_eyewall  the storm's eyewall round the centre (r 160, 220 m high): its inner face dark, banded with held light
                 spiralling down and in (everything drifts toward the heart).
"""

from __future__ import annotations

import math

import numpy as np

import iskarra as isk
import kit_common as kc

M_GLASS = "kit_salt_glass"
M_HELD = "kit_glimmer_held"
M_DARK = "kit_interior_dark"

TRI_BUDGET = {"heart_floor": (9000, 600), "heart_column": (3000, 400), "heart_eyewall": (6000, 1200)}

FLOOR_R = 11.0
WATER_Y = -0.3
COLUMN_AT = (-9.5, -12.0)  # behind the enemy line, the frame's centre-left
EYEWALL_R = 160.0


def build_floor(seed: int = 2801) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("heart_floor", seed)
        mb = kc.MeshBuilder("heart_floor" + ("-lod1" if lod else ""))
        glass, held = mb.material(M_GLASS), mb.material(M_HELD)
        # The held light under the plates: a lit disc just beneath them.
        a = np.linspace(0.0, 2 * math.pi, (16 if lod else 48) + 1)
        under = np.stack([np.zeros((len(a), 3)) + [0.0, -0.08, 0.0],
                          np.stack([np.cos(a) * FLOOR_R, np.full_like(a, -0.08), np.sin(a) * FLOOR_R], -1)])
        isk._strip(mb, under, held, (0.0, 1.0, 0.0), uv=under[..., [0, 2]], col=np.array([0.0, 0.0, 0.0, 0.5]),
                   uv2=np.array([1.0, 0.5]), smooth=False)
        if lod:
            top = under + np.array([0.0, 0.08, 0.0])
            isk._strip(mb, top, glass, (0.0, 1.0, 0.0), uv=top[..., [0, 2]], col=np.array([0.0, 0.0, 0.0, 0.5]),
                       uv2=np.array([1.0, 0.5]), smooth=False)
        else:  # salt-glass plates in rings, each a thin slab, the seams between them showing the light beneath
            for r0 in np.arange(0.0, FLOOR_R - 0.5, 1.4):
                r1 = min(r0 + 1.4, FLOOR_R)
                n = max(6, int(2 * math.pi * (r0 + r1) * 0.5 / 1.4))
                off = float(rng.uniform(0, 1))
                for k in range(n):
                    am = 2 * math.pi * (k + 0.5 + off) / n
                    rm = (r0 + r1) * 0.5
                    half_t = max(rm * math.pi / n - 0.04, 0.12)
                    kc.rounded_block(mb, (math.cos(am) * rm, -0.03, math.sin(am) * rm),
                                     ((r1 - r0) * 0.5 - 0.04, 0.03, half_t), glass, rot=kc.rot_y(-am), radius=0.01,
                                     seg=1)
        # The rim: a step down to the water, its edge lit.
        rim = np.stack([np.stack([np.cos(a) * FLOOR_R, np.full_like(a, -0.08), np.sin(a) * FLOOR_R], -1),
                        np.stack([np.cos(a) * FLOOR_R, np.full_like(a, WATER_Y - 0.2), np.sin(a) * FLOOR_R], -1)])
        isk._strip(mb, rim, glass, lambda c: np.array([c[0], 0.0, c[2]]), uv=rim[..., [0, 1]],
                   col=np.array([0.0, 0.0, 0.0, 0.5]), uv2=np.array([1.0, 0.5]), smooth=False)
        kc.tube(mb, isk._ring(FLOOR_R + 0.03, -0.06, a), 0.04, 4, held)
        out.append(mb)
    return out


def build_column(seed: int = 2802) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("heart_column" + ("-lod1" if lod else ""))
        held, glass = mb.material(M_HELD), mb.material(M_GLASS)
        sides = 10 if lod else 24
        kc.tube(mb, np.array([[0.0, WATER_Y, 0.0], [0.0, 40.0, 0.0]]), np.array([0.9, 0.5]), sides, held,
                cap_end=True)
        for k, r in enumerate((1.6, 2.4) if lod else (1.5, 2.2, 3.1)):
            kc.tube(mb, np.array([[0.0, WATER_Y, 0.0], [0.0, 40.0 - 6.0 * k, 0.0]]), np.array([r, r * 0.55]), sides,
                    glass)
        a = np.linspace(0.0, 2 * math.pi, sides + 1)
        kc.tube(mb, isk._ring(4.2, WATER_Y + 0.02, a), 0.12, 4, held)
        out.append(mb)
    return out


def build_eyewall(seed: int = 2803) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("heart_eyewall", seed)
        mb = kc.MeshBuilder("heart_eyewall" + ("-lod1" if lod else ""))
        dark, held = mb.material(M_DARK), mb.material(M_HELD)
        n = 24 if lod else 72
        a = np.linspace(0.0, 2 * math.pi, n + 1)
        rows = []
        for y in np.linspace(-40.0, 220.0, 5 if lod else 13):
            r = EYEWALL_R * (1.0 + 0.002 * (y + 40.0))  # flaring a little outward as it rises
            rows.append(np.stack([np.cos(a) * r, np.full_like(a, y), np.sin(a) * r], -1))
        wall = np.stack(rows)
        isk._strip(mb, wall, dark, lambda c: np.array([-c[0], 0.0, -c[2]]),  # faces in, toward the heart
                   uv=np.stack([np.broadcast_to(a * EYEWALL_R / 20.0, wall.shape[:2]), wall[..., 1] / 20.0], -1),
                   col=np.array([0.0, 0.0, 0.0, 0.5]), uv2=np.array([0.6, 0.5]))
        # Bands of held light spiralling down and in along the inner face.
        for k in range(4 if lod else 10):
            t = np.linspace(0.0, 1.0, 12 if lod else 40)
            th0 = 2 * math.pi * k / (4 if lod else 10)
            th = th0 + t * 2.4
            y = 200.0 - t * 230.0 + float(rng.uniform(-10, 10))
            r = EYEWALL_R * 0.985
            pts = np.stack([np.cos(th) * r, y, np.sin(th) * r], -1)
            kc.tube(mb, pts, 0.9, 4, held)
        out.append(mb)
    return out


TARGETS = {"heart_floor": build_floor, "heart_column": build_column, "heart_eyewall": build_eyewall}
