"""Coilspire's flue-trial story pieces the greybox still stood in for (env-art-b; M3-ENV-1222's Coilspire half;
act1_ch08.md B05). Pure numpy. Each sits on its block's footprint in the zone (ch08/coilspire's layout), origin as
stated, the block's local axes (its thin side along X unless stated).

  flue_gate    a wright's grille across a flight at its third tread, which the trial opens (the block hides): an iron
               frame 1.6 m wide (Z) and 2.8 m tall in two leaves, square bars and two flat bands riveted across them,
               copper finials, hinge straps on one jamb and a hasp on the other. Origin at the foot's centre.
  niche_seal   the tier-2 side flue's sealed lamp-niche: a plug of fitted laterite 1 m square in a dressed surround,
               the joints mortared fresh and a clay seal stamped across the middle joint. 0.6 m deep (X). Origin at
               the foot's centre.
  lamp_niche   what the seal hides: the niche's sooted back and shelf and, on it, the oilcloth bundle (Wenna's needle
               inside; the item is the zone's pickup). 0.2 x 0.8 x 0.8. Origin at the foot's centre.
  wright_mark  the Saltwright mark scratched by the seized flue (tier 3): a patch of re-dressed stone 0.5 m square, a
               finger thin (Z), with the mark cut into both faces: a circle crossed by a wavy line and three ticks.
               Origin at its centre.
  wall_lamp    the keepers' lamp on the well's wall (the 10-29 audit: the tiers' wall-wash lights had no source): an
               iron back plate pinned to the stone, a forged arm reaching 0.32 m out and down to a copper oil dish with
               its ember flame. Origin on the wall's face at the plate's centre; +Z out of the wall.
"""

from __future__ import annotations

import math

import numpy as np

import cs_common as cs
from cs_common import kc

TRI_BUDGET = {"flue_gate": (6000, 400), "niche_seal": (3000, 200), "lamp_niche": (1600, 120),
              "wright_mark": (1200, 60), "wall_lamp": (1500, 120)}

GATE_W, GATE_H, GATE_T = 1.6, 2.8, 0.3
SEAL_D, SEAL_H, SEAL_W = 0.6, 1.0, 1.0
NICHE_D, NICHE_H, NICHE_W = 0.2, 0.8, 0.8
MARK_S, MARK_T = 0.5, 0.02
LAMP_REACH, LAMP_DROP = 0.32, 0.1  # the dish's centre: out from the wall, below the plate's centre
M_CLOTH = "cs_timber"  # oilcloth reads as dark waxed timber at this size; no new slot


def build_flue_gate(seed: int = 1101) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("flue_gate", seed)
        mb = kc.MeshBuilder("flue_gate" + (cs.LOD if lod else ""))
        iron, cu = mb.material(cs.M_IRON), mb.material(cs.M_COPPER)
        hz, t = GATE_W * 0.5, GATE_T * 0.25
        # The frame: two jambs, a head and a sill, then the leaves' meeting stile.
        for z in (-hz + 0.05, hz - 0.05):
            kc.rounded_block(mb, (0.0, GATE_H * 0.5, z), (t, GATE_H * 0.5, 0.05), iron, radius=0.012, seg=1,
                             weather=cs.IRON_W)
        for y in (0.05, GATE_H - 0.06):
            kc.rounded_block(mb, (0.0, y, 0.0), (t, 0.05, hz), iron, radius=0.012, seg=1, weather=cs.IRON_W)
        if lod:
            kc.rounded_block(mb, (0.0, GATE_H * 0.5, 0.0), (0.01, GATE_H * 0.45, hz - 0.1), iron, radius=0.005, seg=1)
            out.append(mb)
            continue
        kc.rounded_block(mb, (0.0, GATE_H * 0.5, 0.0), (t * 0.8, GATE_H * 0.5 - 0.1, 0.03), iron, radius=0.01, seg=1,
                         weather=cs.IRON_W)
        # Square bars every 0.13 m in each leaf, and two flat bands riveted across.
        n = 5
        for side in (-1.0, 1.0):
            for k in range(n):
                z = side * (0.11 + k * (hz - 0.2) / n)
                kc.rounded_block(mb, (0.0, GATE_H * 0.5, z), (0.018, GATE_H * 0.5 - 0.1, 0.018), iron, radius=0.004,
                                 seg=1, weather=cs.IRON_W, variation=float(rng.random()))
                kc.tube(mb, np.array([[0.0, GATE_H - 0.1, z], [0.0, GATE_H + 0.06, z]]), [0.02, 0.0], 6, cu,
                        weather=cs.COPPER_W)
        for y in (0.7, 2.0):
            kc.rounded_block(mb, (0.0, y, 0.0), (0.03, 0.04, hz - 0.08), iron, radius=0.006, seg=1, weather=cs.IRON_W)
            for k in range(2 * n + 1):
                z = -hz + 0.12 + k * (GATE_W - 0.24) / (2 * n)
                for sx in (-1.0, 1.0):
                    kc.rounded_block(mb, (sx * 0.035, y, z), (0.008, 0.012, 0.012), iron, radius=0.006, seg=1)
        # Hinge straps on the -Z jamb, a hasp and staple at the meeting stile.
        for y in (0.45, GATE_H - 0.5):
            kc.rounded_block(mb, (0.03, y, -hz + 0.25), (0.01, 0.03, 0.22), iron, radius=0.004, seg=1)
            kc.tube(mb, np.array([[0.0, y - 0.06, -hz + 0.05], [0.0, y + 0.06, -hz + 0.05]]), 0.03, 8, iron)
        kc.rounded_block(mb, (0.04, 1.35, 0.05), (0.01, 0.025, 0.12), iron, radius=0.004, seg=1)
        a = np.linspace(0.0, math.pi, 7)
        staple = np.stack([np.full_like(a, 0.07), 1.35 + np.sin(a) * 0.04, -0.06 + np.cos(a) * 0.03], -1)
        kc.tube(mb, staple, 0.006, 4, iron)
        out.append(mb)
    return out


def build_niche_seal(seed: int = 1102) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("niche_seal", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("niche_seal" + (cs.LOD if lod else ""))
        lat, carved, dark = mb.material(cs.M_LATERITE), mb.material(cs.M_CARVED), mb.material(cs.M_DARK)
        hd, hw = SEAL_D * 0.5, SEAL_W * 0.5
        if lod:
            kc.rounded_block(mb, (0.0, SEAL_H * 0.5, 0.0), (hd, SEAL_H * 0.5, hw), lat, radius=0.03, seg=1)
            out.append(mb)
            continue
        # The dressed surround: lintel, sill and jambs proud of the wall face (+X is the tier's side).
        for y, h in ((0.06, 0.06), (SEAL_H - 0.07, 0.07)):
            kc.rounded_block(mb, (hd - 0.06, y, 0.0), (0.06, h, hw), carved, radius=0.02, seg=2, noise=noise,
                             disp_m=0.004, weather=cs.INNER_W)
        for z in (-hw + 0.07, hw - 0.07):
            kc.rounded_block(mb, (hd - 0.06, SEAL_H * 0.5, z), (0.06, SEAL_H * 0.5 - 0.12, 0.07), carved, radius=0.02,
                             seg=2, noise=noise, disp_m=0.004, weather=cs.INNER_W)
        # The plug: four fitted blocks, set a finger back, fresh mortar in the joints.
        for (y0, y1), (z0, z1) in (((0.12, 0.5), (-0.36, 0.02)), ((0.12, 0.5), (0.02, 0.36)),
                                   ((0.5, 0.86), (-0.36, -0.06)), ((0.5, 0.86), (-0.06, 0.36))):
            kc.rounded_block(mb, (-0.02, (y0 + y1) * 0.5, (z0 + z1) * 0.5), (hd - 0.06, (y1 - y0) * 0.5 - 0.008,
                                                                            (z1 - z0) * 0.5 - 0.008),
                             lat, radius=0.02, seg=2, noise=noise, disp_m=0.006, weather=cs.INNER_W,
                             variation=float(rng.random()))
        kc.rounded_block(mb, (-0.03, 0.49, 0.0), (hd - 0.07, 0.012, 0.36), dark, radius=0.004, seg=1)
        # The clay seal across the middle joint: a round cake, stamped.
        kc.tube(mb, np.array([[hd - 0.08, 0.5, 0.0], [hd - 0.045, 0.5, 0.0]]), 0.075, 14, carved, cap_end=True)
        for k in range(3):
            kc.rounded_block(mb, (hd - 0.043, 0.48 + k * 0.02, 0.0), (0.004, 0.003, 0.035 - k * 0.008), dark,
                             radius=0.002, seg=1)
        out.append(mb)
    return out


def build_lamp_niche(seed: int = 1103) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lamp_niche", seed)
        mb = kc.MeshBuilder("lamp_niche" + (cs.LOD if lod else ""))
        soot, cloth, iron = mb.material(cs.M_SOOT), mb.material(M_CLOTH), mb.material(cs.M_IRON)
        hd, hw = NICHE_D * 0.5, NICHE_W * 0.5
        # The niche's back and its shelf, black with old lamp smoke.
        kc.rounded_block(mb, (-hd + 0.02, NICHE_H * 0.5, 0.0), (0.02, NICHE_H * 0.5, hw), soot, radius=0.01, seg=1)
        kc.rounded_block(mb, (0.0, 0.03, 0.0), (hd, 0.03, hw), soot, radius=0.01, seg=1)
        if not lod:
            # The oilcloth bundle: a long roll tied twice, a corner of cord left out.
            roll = np.array([[0.0, 0.11, -0.22], [0.0, 0.11, 0.22]])
            kc.tube(mb, roll, 0.045, 10, cloth, cap_start=True, cap_end=True, variation=float(rng.random()))
            for z in (-0.12, 0.12):
                a = np.linspace(0.0, 2 * math.pi, 11)
                tie = np.stack([np.cos(a) * 0.048, 0.11 + np.sin(a) * 0.048, np.full_like(a, z)], -1)
                kc.tube(mb, tie, 0.005, 4, iron)
            cord = np.array([[0.0, 0.11, 0.22], [0.02, 0.08, 0.27], [0.05, 0.065, 0.3]])
            kc.tube(mb, cord, 0.004, 4, iron)
        out.append(mb)
    return out


def build_wright_mark(seed: int = 1104) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("wright_mark", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("wright_mark" + (cs.LOD if lod else ""))
        inner, dark = mb.material(cs.M_INNER), mb.material(cs.M_DARK)
        h = MARK_S * 0.5
        kc.rounded_block(mb, (0.0, 0.0, 0.0), (h, h, MARK_T * 0.5), inner, radius=0.004, seg=1 if lod else 3,
                         noise=None if lod else noise, disp_m=0.002, weather=cs.INNER_W)
        if lod:
            out.append(mb)
            continue
        # The mark, scratched (dark strokes standing a hair proud of each face): a circle, a wave across it, ticks.
        for face in (-1.0, 1.0):
            z = face * (MARK_T * 0.5 + 0.0015)
            a = np.linspace(0.0, 2 * math.pi, 25)
            ring = np.stack([np.cos(a) * 0.13, np.sin(a) * 0.13, np.full_like(a, z)], -1)
            kc.tube(mb, ring, 0.004, 3, dark)
            x = np.linspace(-0.2, 0.2, 13)
            wave = np.stack([x, np.sin(x * 22.0) * 0.03, np.full_like(x, z)], -1)
            kc.tube(mb, wave, 0.004, 3, dark)
            for k in range(3):
                x0 = -0.06 + k * 0.06
                kc.tube(mb, np.array([[x0, -0.17, z], [x0 + rng.normal(0, 0.006), -0.22, z]]), 0.004, 3, dark)
        out.append(mb)
    return out


def build_wall_lamp(seed: int = 1105) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("wall_lamp", seed)
        mb = kc.MeshBuilder("wall_lamp" + (cs.LOD if lod else ""))
        iron, copper, ember = mb.material(cs.M_IRON), mb.material(cs.M_COPPER), mb.material(cs.M_EMBER)
        sides = 5 if lod else 10
        # The back plate, pinned at top and bottom.
        kc.rounded_block(mb, (0.0, 0.0, 0.012), (0.045, 0.12, 0.012), iron, radius=0.006, seg=1,
                         variation=float(rng.random()))
        if not lod:
            for y in (-0.09, 0.09):
                kc.tube(mb, np.array([[0.0, y, 0.02], [0.0, y, 0.035]]), 0.012, 6, iron, cap_end=True)
        # The arm: out from the plate's top, curving down to the dish's rim.
        t = np.linspace(0.0, 1.0, 4 if lod else 8)
        arm = np.stack([np.zeros_like(t), 0.06 - (0.06 + LAMP_DROP - 0.02) * t ** 2, 0.024 + (LAMP_REACH - 0.024) * t],
                       -1)
        kc.tube(mb, arm, 0.011, 4 if lod else 6, iron)
        # The dish (a shallow copper bowl on a short foot) and its flame.
        cy = -LAMP_DROP
        dish = np.array([[0.0, cy - 0.05, LAMP_REACH], [0.0, cy - 0.04, LAMP_REACH], [0.0, cy - 0.01, LAMP_REACH],
                         [0.0, cy, LAMP_REACH]])
        kc.tube(mb, dish, [0.025, 0.06, 0.09, 0.095], sides, copper, cap_start=True, variation=float(rng.random()))
        flame = np.array([[0.0, cy - 0.005, LAMP_REACH], [0.0, cy + 0.03, LAMP_REACH], [0.0, cy + 0.075, LAMP_REACH]])
        kc.tube(mb, flame, [0.022, 0.018, 0.002], 4 if lod else 8, ember, cap_start=True, cap_end=True)
        out.append(mb)
    return out


TARGETS = {
    "flue_gate": build_flue_gate,
    "niche_seal": build_niche_seal,
    "lamp_niche": build_lamp_niche,
    "wright_mark": build_wright_mark,
    "wall_lamp": build_wall_lamp,
}
