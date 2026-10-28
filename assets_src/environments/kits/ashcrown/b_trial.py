"""The Ashcrown trial's story pieces (env-art-b; act1_ch05.md B08-B10, ashcrown.md §0.2), which the greybox stood in
for. Pure numpy. Origins at the foot's centre on the floor unless stated; the front is +Z.

  catch_rod      a tier's catch-rod: a dressed stone foot and a 3.6 m copper rod ending in a cupped fork, its lead
                 coiled down to the floor toward the bowl (-X).
  strike_bowl    the tier's copper bowl on a stone drum (1.4 m across, 1.0 m tall), its rim ringed with the eight
                 copper studs that count the strike down (the zone lights the bowl while it holds a charge).
  vein_gate      a vein-gate: a bronze disc 1.2 m across set flush in the paving, a copper channel bar across it
                 (1.6 m along X, the way it conducts) and a pivot boss; the zone turns it about Y in 90° steps.
  release_lever  the tier's release: a bronze lever (1.1 m) in a slotted stone socket, a copper lead to the floor.
  floor_plate    a tier-4 floor plate on a Tender's grave: 1.2 m square of bronze, the grave's name-lines cut in it.
  ash_drift      the ash drift a dead-end vein grounds into: a soft heap 3 x 0.6 x 2 m with a vein end buried in it.
  quench_seal    the plug sealing the side vein's alcove (1.2 x 2 x 4 m): fitted blocks in a dressed frame, a copper
                 vein running into it under a bronze plate.
  quench_trough  the smiths' quench trough in the alcove: a stone trough 2 x 0.8 x 1.2 m of black water, an iron hook
                 on its lip.
  matron_alcove  the Cinder Matron's alcove in the hall wall (2 x 3.2 x 3 m): a sooted arch, a slag-crusted floor and
                 a ledge of cooled cinder where she was tended.
  chamber_door   Kahre's chamber door (3 x 2.8 x 0.6 m): two black-lacquer leaves under a red lintel, copper studs, a
                 bronze anvil-boss on each leaf.
  stair_chain    the Tenders' chain across a vein stair's head until the strike reaches the tier: two bronze posts
                 1.0 m apart (X) and a sagging chain with a lacquered tablet.
"""

from __future__ import annotations

import math

import numpy as np

import ac_common as ac
from ac_common import kc

TRI_BUDGET = {
    "catch_rod": (2500, 200), "strike_bowl": (4000, 300), "vein_gate": (2500, 200), "release_lever": (1500, 150),
    "floor_plate": (1200, 60), "ash_drift": (2000, 200), "quench_seal": (4000, 200), "quench_trough": (2500, 200),
    "matron_alcove": (5000, 300), "chamber_door": (4000, 300), "stair_chain": (1500, 150),
}


def _mb(name: str, lod: bool) -> kc.MeshBuilder:
    return kc.MeshBuilder(ac.lod_name(name, lod))


def build_catch_rod(seed: int = 1201) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("catch_rod", seed)
        noise = kc.Noise3(rng)
        mb = _mb("catch_rod", lod)
        st, cu = mb.material(ac.M_DRESSED), mb.material(ac.M_COPPER)
        kc.rounded_block(mb, (0.0, 0.25, 0.0), (0.32, 0.25, 0.32), st, radius=0.04, seg=1 if lod else 2,
                         noise=None if lod else noise, disp_m=0.006, weather=ac.DRESSED_W)
        s = 5 if lod else 10
        kc.tube(mb, np.array([[0.0, 0.5, 0.0], [0.0, 3.6, 0.0]]), [0.06, 0.04], s, cu, weather=ac.METAL_W)
        for side in (-1.0, 1.0):  # the cupped fork
            a = np.linspace(0.0, 1.0, 5 if lod else 9)
            fork = np.stack([side * 0.22 * np.sin(a * 1.4), 3.6 + a * 0.5, 0.06 * np.sin(a * 3.0)], -1)
            kc.tube(mb, np.vstack([[[0.0, 3.55, 0.0]], fork]), 0.03, 4 if lod else 8, cu, weather=ac.METAL_W,
                    cap_end=True)
        if not lod:
            for k in range(3):
                kc.tube(mb, np.array([[0.0, 0.6 + k * 0.9, 0.0], [0.0, 0.66 + k * 0.9, 0.0]]), 0.075, 10,
                        mb.material(ac.M_COPPER_NEW))
            t = np.linspace(0.0, 1.0, 12)
            lead = np.stack([-0.12 - t * 0.7, 0.5 - t * 0.48 + 0.1 * np.sin(t * math.pi), np.sin(t * 9.0) * 0.08], -1)
            kc.tube(mb, lead, 0.02, 6, cu, weather=ac.METAL_W)
        ac.ash(mb, 0, noise)
        out.append(mb)
    return out


def build_strike_bowl(seed: int = 1202) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("strike_bowl", seed)
        noise = kc.Noise3(rng)
        mb = _mb("strike_bowl", lod)
        st, cu = mb.material(ac.M_DRESSED), mb.material(ac.M_COPPER)
        sides = 8 if lod else 20
        kc.tube(mb, np.array([[0.0, 0.0, 0.0], [0.0, 0.62, 0.0]]), [0.55, 0.5], sides, st, weather=ac.DRESSED_W,
                cap_end=True)
        # The bowl: a lathe of copper from its foot to a rolled lip at 1.0 m, open (inner wall to a shallow floor).
        prof = [(0.18, 0.62), (0.45, 0.7), (0.66, 0.86), (0.7, 1.0), (0.64, 0.99), (0.52, 0.86), (0.0, 0.8)]
        P = np.array(prof)
        ang = np.linspace(0.0, 2 * math.pi, sides + 1)
        grid = np.stack([np.outer(np.cos(ang), P[:, 0]), np.tile(P[:, 1], (sides + 1, 1)),
                         np.outer(np.sin(ang), P[:, 0])], -1)
        uv = np.stack([np.tile(np.linspace(0, 4, sides + 1)[:, None], (1, len(prof))),
                       np.tile(np.arange(len(prof))[None, :] * 0.2, (sides + 1, 1))], -1)
        kc.quad_strip(mb, grid, cu, uv=uv, col=np.array([0.0, 0.2, 0.0, 0.3]), uv2=np.array([0.9, 0.5]),
                      smooth=True)
        if not lod:
            for k in range(8):  # the stud ring on the drum's top
                a = k * math.pi / 4.0
                kc.rounded_block(mb, (0.47 * math.cos(a), 0.64, 0.47 * math.sin(a)), (0.04, 0.025, 0.04),
                                 mb.material(ac.M_COPPER_NEW), radius=0.02, seg=2)
        ac.ash(mb, 0, noise)
        out.append(mb)
    return out


def build_vein_gate(seed: int = 1203) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("vein_gate", seed)
        mb = _mb("vein_gate", lod)
        br, cu = mb.material(ac.M_COPPER_NEW), mb.material(ac.M_COPPER)
        sides = 10 if lod else 28
        kc.tube(mb, np.array([[0.0, -0.06, 0.0], [0.0, 0.02, 0.0]]), 0.6, sides, br, weather=ac.METAL_W,
                cap_end=True)
        kc.rounded_block(mb, (0.0, 0.035, 0.0), (0.8, 0.02, 0.09), cu, radius=0.015, seg=1, weather=ac.METAL_W)
        if not lod:
            kc.tube(mb, np.array([[0.0, 0.02, 0.0], [0.0, 0.09, 0.0]]), 0.11, 12, br, cap_end=True)
            for k in range(12):  # the rim's step notches
                a = k * math.pi / 6.0
                kc.rounded_block(mb, (0.56 * math.cos(a), 0.022, 0.56 * math.sin(a)), (0.03, 0.006, 0.012), cu,
                                 rot=kc.rot_y(-a), radius=0.004, seg=1)
            # Arrow heads at both ends of the channel: which way the strike runs.
            for sx in (-1.0, 1.0):
                kc.rounded_block(mb, (sx * 0.62, 0.05, 0.0), (0.06, 0.012, 0.06), cu, rot=kc.rot_y(math.pi / 4),
                                 radius=0.008, seg=1)
        out.append(mb)
    return out


def build_release_lever(seed: int = 1204) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("release_lever", seed)
        noise = kc.Noise3(rng)
        mb = _mb("release_lever", lod)
        st, br = mb.material(ac.M_DRESSED), mb.material(ac.M_COPPER_NEW)
        kc.rounded_block(mb, (0.0, 0.3, 0.0), (0.28, 0.3, 0.2), st, radius=0.04, seg=1 if lod else 2,
                         noise=None if lod else noise, disp_m=0.005, weather=ac.DRESSED_W)
        kc.tube(mb, np.array([[0.0, 0.55, 0.0], [0.0, 1.35, 0.38]]), 0.035, 4 if lod else 8, br, cap_end=True)
        kc.tube(mb, np.array([[-0.12, 1.35, 0.38], [0.12, 1.35, 0.38]]), 0.04, 4 if lod else 8, br, cap_start=True,
                cap_end=True)
        if not lod:
            kc.rounded_block(mb, (0.0, 0.6, 0.0), (0.05, 0.01, 0.16), mb.material(ac.M_DARK), radius=0.005, seg=1)
            t = np.linspace(0.0, 1.0, 8)
            kc.tube(mb, np.stack([np.zeros_like(t), 0.3 - t * 0.29, -0.2 - t * 0.6], -1), 0.02, 6,
                    mb.material(ac.M_COPPER))
        ac.ash(mb, 0, noise)
        out.append(mb)
    return out


def build_floor_plate(seed: int = 1205) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("floor_plate", seed)
        mb = _mb("floor_plate", lod)
        br, dk = mb.material(ac.M_COPPER_NEW), mb.material(ac.M_DARK)
        kc.rounded_block(mb, (0.0, 0.03, 0.0), (0.6, 0.03, 0.6), br, radius=0.01, seg=1, weather=ac.METAL_W)
        if not lod:
            for k in range(5):  # the grave's name-lines
                w = 0.35 - 0.05 * (k % 2) - rng.uniform(0.0, 0.08)
                kc.rounded_block(mb, (0.0, 0.061, -0.3 + k * 0.15), (w, 0.002, 0.012), dk, radius=0.002, seg=1)
        out.append(mb)
    return out


def build_ash_drift(seed: int = 1206) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ash_drift", seed)
        noise = kc.Noise3(rng)
        mb = _mb("ash_drift", lod)
        n = 6 if lod else 19
        X, Z = np.meshgrid(np.linspace(-1.6, 1.6, n), np.linspace(-1.1, 1.1, n))
        r = np.sqrt((X / 1.5) ** 2 + (Z / 1.0) ** 2)
        Y = 0.6 * np.clip(1.0 - r ** 2, 0.0, 1.0) ** 0.8 - 0.02
        if not lod:
            Y += (noise.fbm(np.stack([X * 1.5, np.zeros_like(X), Z * 1.5], -1), 3) - 0.5) * 0.12 * (Y > 0.02)
        P = np.stack([X, Y, Z], -1)
        col = np.stack([np.zeros_like(Y), np.full_like(Y, 1.0), np.zeros_like(Y), np.full_like(Y, 0.6)], -1)
        ac.grid_surface(mb, P, mb.material(ac.M_CINDER), outward=kc.UP, uv=np.stack([X, Z], -1), col=col,
                        uv2=np.array([0.8, 0.5]))
        kc.rounded_block(mb, (-1.5, 0.02, 0.0), (0.4, 0.015, 0.09), mb.material(ac.M_COPPER), radius=0.01, seg=1)
        out.append(mb)
    return out


def build_quench_seal(seed: int = 1207) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("quench_seal", seed)
        noise = kc.Noise3(rng)
        mb = _mb("quench_seal", lod)
        st, dr = mb.material(ac.M_ASHLAR), mb.material(ac.M_DRESSED)
        if lod:
            kc.rounded_block(mb, (0.0, 1.0, 0.0), (0.6, 1.0, 2.0), st, radius=0.03, seg=1)
            out.append(mb)
            continue
        for z in (-1.85, 1.85):
            kc.rounded_block(mb, (0.0, 1.0, z), (0.6, 1.0, 0.15), dr, radius=0.03, seg=2, noise=noise, disp_m=0.004,
                             weather=ac.DRESSED_W)
        kc.rounded_block(mb, (0.0, 1.9, 0.0), (0.6, 0.1, 2.0), dr, radius=0.03, seg=2, weather=ac.DRESSED_W)
        for i in range(3):
            for j in range(4):
                y0, z0 = i * 0.6, -1.7 + j * 0.85 + (0.42 if i % 2 else 0.0)
                z1 = min(z0 + 0.84, 1.7)
                if z1 - z0 < 0.2:
                    continue
                kc.rounded_block(mb, (-0.03, y0 + 0.3, (z0 + z1) * 0.5), (0.55, 0.29, (z1 - z0) * 0.5 - 0.01), st,
                                 radius=0.03, seg=2, noise=noise, disp_m=0.008, weather=ac.STONE_W,
                                 variation=float(rng.random()))
        kc.rounded_block(mb, (0.6, 0.02, 0.0), (0.4, 0.015, 0.09), mb.material(ac.M_COPPER), radius=0.01, seg=1)
        kc.rounded_block(mb, (0.58, 0.9, 0.0), (0.02, 0.18, 0.22), mb.material(ac.M_COPPER_NEW), radius=0.01, seg=1)
        ac.ash(mb, 0, noise)
        out.append(mb)
    return out


def build_quench_trough(seed: int = 1208) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("quench_trough", seed)
        noise = kc.Noise3(rng)
        mb = _mb("quench_trough", lod)
        st = mb.material(ac.M_DRESSED)
        for z in (-0.5, 0.5):
            kc.rounded_block(mb, (0.0, 0.4, z), (1.0, 0.4, 0.1), st, radius=0.03, seg=1 if lod else 2,
                             noise=None if lod else noise, disp_m=0.005, weather=ac.DRESSED_W)
        for x in (-0.9, 0.9):
            kc.rounded_block(mb, (x, 0.4, 0.0), (0.1, 0.4, 0.4), st, radius=0.03, seg=1 if lod else 2,
                             weather=ac.DRESSED_W)
        kc.rounded_block(mb, (0.0, 0.05, 0.0), (0.8, 0.05, 0.4), st, radius=0.02, seg=1)
        kc.rounded_block(mb, (0.0, 0.62, 0.0), (0.8, 0.005, 0.4), mb.material(ac.M_LACQUER_BLACK), radius=0.002,
                         seg=1)
        if not lod:
            hook = np.array([[0.6, 0.8, -0.5], [0.6, 0.95, -0.5], [0.6, 0.95, -0.36], [0.6, 0.82, -0.32]])
            kc.tube(mb, hook, 0.012, 6, mb.material(ac.M_COPPER), cap_start=True, cap_end=True)
            ac.ash(mb, 0, noise, 0.5)
        out.append(mb)
    return out


def build_matron_alcove(seed: int = 1209) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("matron_alcove", seed)
        noise = kc.Noise3(rng)
        mb = _mb("matron_alcove", lod)
        dr, soot, cin = mb.material(ac.M_DRESSED), mb.material(ac.M_SOOT), mb.material(ac.M_CINDER)
        # Jambs and an arch (+Z is the hall), the back sooted, a cinder ledge, slag on the floor.
        for x in (-0.9, 0.9):
            kc.rounded_block(mb, (x, 1.1, 1.3), (0.15, 1.1, 0.2), dr, radius=0.03, seg=1 if lod else 2,
                             noise=None if lod else noise, disp_m=0.006, weather=ac.DRESSED_W)
        n = 4 if lod else 9
        for k in range(n):
            a = math.pi * (k + 0.5) / n
            kc.rounded_block(mb, (-0.9 * math.cos(a), 2.2 + 0.9 * math.sin(a), 1.3), (0.16, 0.12, 0.2), dr,
                             rot=kc.rot_z(a - math.pi / 2), radius=0.02, seg=1, weather=ac.DRESSED_W)
        kc.rounded_block(mb, (0.0, 1.6, -1.4), (1.0, 1.6, 0.1), soot, radius=0.02, seg=1)
        for x in (-1.0, 1.0):
            kc.rounded_block(mb, (x, 1.6, 0.0), (0.1, 1.6, 1.4), soot, radius=0.02, seg=1)
        kc.rounded_block(mb, (0.0, 0.03, 0.0), (1.0, 0.03, 1.4), cin, radius=0.02, seg=1)
        if not lod:
            kc.rounded_block(mb, (0.0, 0.35, -1.0), (0.85, 0.35, 0.35), cin, radius=0.12, seg=3, noise=noise,
                             disp_m=0.05, disp_period_m=0.3, weather=ac.STONE_W)
            for _k in range(9):
                s = rng.uniform(0.08, 0.22)
                kc.rounded_block(mb, (rng.uniform(-0.8, 0.8), s * 0.4, rng.uniform(-0.6, 1.2)), (s, s * 0.5, s * 0.8),
                                 cin, rot=kc.rot_y(rng.uniform(0, math.pi)), radius=s * 0.4, seg=2, noise=noise,
                                 disp_m=s * 0.2, weather=ac.STONE_W)
        out.append(mb)
    return out


def build_chamber_door(seed: int = 1210) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("chamber_door", seed)
        mb = _mb("chamber_door", lod)
        blk, red = mb.material(ac.M_LACQUER_BLACK), mb.material(ac.M_LACQUER_RED)
        br = mb.material(ac.M_COPPER_NEW)
        for x in (-0.72, 0.72):
            kc.rounded_block(mb, (x, 1.25, 0.0), (0.7, 1.25, 0.08), blk, radius=0.02, seg=1, weather=ac.LACQUER_W,
                             variation=float(rng.random()))
        kc.rounded_block(mb, (0.0, 2.65, 0.0), (1.5, 0.15, 0.3), red, radius=0.03, seg=1, weather=ac.LACQUER_W)
        for x in (-1.45, 1.45):
            kc.rounded_block(mb, (x, 1.25, 0.0), (0.05, 1.25, 0.3), red, radius=0.02, seg=1, weather=ac.LACQUER_W)
        if not lod:
            for x0 in (-0.72, 0.72):
                for i in range(4):
                    for j in range(3):
                        kc.rounded_block(mb, (x0 - 0.45 + j * 0.45, 0.4 + i * 0.6, 0.09), (0.025, 0.025, 0.012), br,
                                         radius=0.012, seg=2)
                kc.rounded_block(mb, (x0 * 0.85, 1.25, 0.1), (0.16, 0.09, 0.03), br, radius=0.03, seg=2)
                kc.rounded_block(mb, (x0 * 0.85, 1.34, 0.1), (0.07, 0.04, 0.03), br, radius=0.02, seg=1)
        out.append(mb)
    return out


def build_stair_chain(seed: int = 1211) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("stair_chain", seed)
        mb = _mb("stair_chain", lod)
        br, cu = mb.material(ac.M_COPPER_NEW), mb.material(ac.M_COPPER)
        for x in (-0.5, 0.5):
            kc.tube(mb, np.array([[x, 0.0, 0.0], [x, 1.0, 0.0]]), 0.045, 5 if lod else 10, br, cap_end=True)
            kc.rounded_block(mb, (x, 1.04, 0.0), (0.06, 0.04, 0.06), br, radius=0.02, seg=1)
        t = np.linspace(-0.5, 0.5, 6 if lod else 15)
        chain = np.stack([t, 0.92 - 0.18 * (1.0 - (2 * t) ** 2), np.zeros_like(t)], -1)
        kc.tube(mb, chain, 0.015, 4 if lod else 6, cu)
        if not lod:
            kc.rounded_block(mb, (0.0, 0.62, 0.02), (0.13, 0.09, 0.01), mb.material(ac.M_LACQUER_RED), radius=0.01,
                             seg=1, variation=float(rng.random()))
        out.append(mb)
    return out


TARGETS = {
    "catch_rod": build_catch_rod, "strike_bowl": build_strike_bowl, "vein_gate": build_vein_gate,
    "release_lever": build_release_lever, "floor_plate": build_floor_plate, "ash_drift": build_ash_drift,
    "quench_seal": build_quench_seal, "quench_trough": build_quench_trough, "matron_alcove": build_matron_alcove,
    "chamber_door": build_chamber_door, "stair_chain": build_stair_chain,
}
