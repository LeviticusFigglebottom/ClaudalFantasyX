"""Ch6's two battle arenas' grounds (M3-ENV-706; contract docs/kb/tech/battle_arenas.md). Pure numpy.

  arena_shoals_ground  `brine_shoals_afternoon`: the wreck-ridge flats. A flat battle floor of firm silt at y 0
                       (the slots' ellipse), easing out into the tidal mud with its rivulets, two low ridges of
                       shell grit where wrecks lie stranded (north-west and north-east), the mud sloping to the
                       channels beyond.
  arena_camp_ground    `salvage_camp_burning`: the Saltwrights' hard. The battle floor is the hard's shingle top
                       at y 0; its flanks fall 1.15 m to the mud on every side; the channel runs past to the west.

Coordinates are the battle's (origin at the slot layout, north -Z, the BattleCamera looking north from about
(0.6, 2.8, 8.4)). `shoals_height` and `camp_height` are what arena_scenes.py stands its dressing on.
"""

from __future__ import annotations

import numpy as np

import bs_common as bc
import bs_ground as bg
from bs_common import kc

TRI_BUDGET = {"arena_shoals_ground": (24000, 3000), "arena_camp_ground": (24000, 3000)}

FLOOR_HALF = (11.0, 8.0)  # the battle floor's flat ellipse (x, z) about FLOOR_CENTER
FLOOR_CENTER = (0.0, -1.5)
FLOOR_EASE_M = 5.0
EXTENT = (-90.0, 90.0, -160.0, 24.0)  # x0, x1, z0, z1
CAMP_DROP_M = 1.15  # the hard's top over the mud (bs_ground.HARD_TOP_Y + its foot's 0.05)
CAMP_CORE_HALF = (13.0, 9.0)  # the hard's flat top; wider than the camp preview's, the slots need it
CAMP_FLANK_M = 6.0
RIDGES = ((-26.0, -24.0, 9.0, 0.9), (30.0, -34.0, 11.0, 1.1))  # x, z, radius, height: wreck ridges


def _mud(noise: kc.Noise3, X, Z):
    """bs_ground._mud_height's tidal mud without its 24 m cell's edge fade (one surface across the arena)."""
    relief = (bg._n2(noise, X, Z, 9.0, 4) - 0.5) * 0.08 + (bg._n2(noise, X, Z, 2.2, 2, 3.0) - 0.5) * 0.02 + 0.02
    groove = np.zeros_like(X)
    for k in range(2):
        f = bg._n2(noise, X, Z, 15.0 + 6.0 * k, 3, 7.0 + 5.0 * k)
        w = 0.03 + 0.03 * bg._n2(noise, X, Z, 6.0, 2, 11.0 + k)
        groove = np.maximum(groove, 1.0 - kc.smoothstep(0.0, w, np.abs(f - 0.5)))
    pool = kc.smoothstep(0.66, 0.71, bg._n2(noise, X, Z, 9.0, 3, 31.0))
    return (relief * (1.0 - np.maximum(groove, pool)) + (bg.WATER_Y - 0.05) * groove
            + (bg.WATER_Y - 0.03) * pool * (1.0 - groove))


def _floor_weight(X, Z):
    """1 on the battle floor's ellipse, 0 beyond its ease."""
    cx, cz = FLOOR_CENTER
    hx, hz = FLOOR_HALF
    d = np.sqrt(((X - cx) / hx) ** 2 + ((Z - cz) / hz) ** 2)
    return 1.0 - kc.smoothstep(1.0, 1.0 + FLOOR_EASE_M / min(hx, hz), d)


def shoals_height(noise: kc.Noise3):
    def h(X, Z):
        X, Z = np.asarray(X, float), np.asarray(Z, float)
        mud = _mud(noise, X, Z)
        ridge = np.zeros_like(X)
        for rx, rz, r, top in RIDGES:
            d = np.hypot(X - rx, Z - rz) / r
            ridge = np.maximum(ridge, top * (1.0 - kc.smoothstep(0.3, 1.0, d)))
        far = -0.35 * kc.smoothstep(45.0, 90.0, np.hypot(X, Z + 30.0))  # down to the channels
        w = _floor_weight(X, Z)
        return (mud + ridge + far) * (1.0 - w) + 0.0 * w
    return h


def camp_height(noise: kc.Noise3):
    def h(X, Z):
        X, Z = np.asarray(X, float), np.asarray(Z, float)
        hx, hz = CAMP_CORE_HALF
        qx = np.maximum(np.abs(X - FLOOR_CENTER[0]) - hx, 0.0)
        qz = np.maximum(np.abs(Z - FLOOR_CENTER[1]) - hz, 0.0)
        d = np.sqrt(qx ** 2 + qz ** 2)
        d = np.maximum(d + (bg._n2(noise, X, Z, 6.0, 2, 4.0) - 0.5) * 3.0 * kc.smoothstep(0.0, 1.0, d), 0.0)
        shape = 1.0 - kc.smoothstep(0.0, CAMP_FLANK_M, d)
        top = (bg._n2(noise, X, Z, 2.5, 3) - 0.5) * 0.08 * (1.0 - _floor_weight(X, Z))  # flat where they fight
        mud = _mud(noise, X, Z) - CAMP_DROP_M
        channel = -0.6 * (1.0 - kc.smoothstep(4.0, 9.0, np.abs(X + 34.0 - bg.channel_offset(Z))))
        return (top * shape) + mud * (1.0 - shape) + channel * (1.0 - shape)
    return h


def _axis(lo: float, hi: float, inner: tuple[float, float], step_in: float, step_out: float) -> np.ndarray:
    """Grid lines: `step_in` apart inside `inner`, `step_out` outside it."""
    a, b = inner
    return np.unique(np.concatenate([np.arange(lo, a, step_out), np.arange(a, b, step_in), np.arange(b, hi, step_out),
                                     [hi]]))


def _ground(name: str, seed: int, fn, *, hard: bool) -> list[kc.MeshBuilder]:
    out = []
    x0, x1, z0, z1 = EXTENT
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (bc.LOD if lod else ""))
        if lod:
            xs, zs = np.linspace(x0, x1, 37), np.linspace(z0, z1, 37)
        else:
            xs = _axis(x0, x1, (-30.0, 30.0), 1.0, 4.0)
            zs = _axis(z0, z1, (-40.0, 16.0), 1.0, 4.0)
        height = fn(noise)
        mat = mb.material(bc.M_GRIT if hard else bc.M_MUD)

        def wet(X, Z, Y):
            low = 0.75 + 0.25 * (1.0 - kc.smoothstep(-0.1, 0.1, Y + (1.15 if hard else 0.0)))
            if not hard:
                return np.clip(low, 0, 1)
            # The camp's hard (the PC render at 71f19fbc: one even pebble field): trampled damp tracks and
            # sun-dried patches in a few-metre fbm, so the shingle tile stops reading as one repeat.
            patch = noise.fbm(np.stack([X / 7.0, np.zeros_like(X), Z / 7.0], axis=-1), 3)
            return np.clip(low - 0.55 + 0.6 * kc.smoothstep(0.4, 0.6, patch), 0, 1)

        bc.heightfield(mb, xs, zs, height, mat,
                       wet=wet,
                       salt=lambda X, Z, Y: kc.smoothstep(0.04, 0.12, Y) * 0.35,
                       ao=lambda X, Z, Y: np.clip(0.8 + 0.5 * np.clip(Y, -0.3, 0.3), 0.6, 1.0), erosion=0.3,
                       variation=float(rng.random()))
        if hard and not lod:
            # The hard's shingle stays on its top and flanks; the mud below re-slots to bs_mud.
            pos = np.asarray(mb.pos)
            t = np.asarray(mb.tris)
            cy = pos[t].mean(axis=1)[:, 1]
            i_mud = mb.material(bc.M_MUD)
            mb.tri_mat = [i_mud if y < -0.9 else m for y, m in zip(cy, mb.tri_mat)]
        out.append(mb)
    return out


def build_arena_shoals_ground(seed: int = 741) -> list[kc.MeshBuilder]:
    return _ground("arena_shoals_ground", seed, shoals_height, hard=False)


def build_arena_camp_ground(seed: int = 742) -> list[kc.MeshBuilder]:
    return _ground("arena_camp_ground", seed, camp_height, hard=True)


TARGETS = {"arena_shoals_ground": build_arena_shoals_ground, "arena_camp_ground": build_arena_camp_ground}
