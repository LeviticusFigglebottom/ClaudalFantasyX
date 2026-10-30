"""Pell's props (no bpy), pell.md §3, §4.1 #3 and #7, §9: the fishing-staff and the name-shell (both states).

* **The fishing-staff** (`Staff`): a long, light pole of seasoned grey cane, `staff_m` (2.60 m), 2.4 cm thick at the
  foot tapering to 1.5 cm at the tip, with five darker growth nodes (none inside the grip span); at the top a barbed
  bone tip (14 cm, three small backward barbs on one side) lashed on with cord over 6 cm; near the foot a dark river
  stone 9 cm across in a cord net, lashed 30 cm above the foot. Held in the **left** hand like Asha's staff (asha_staff
  `held_frame` / `to_held` on the left hand: built upright through the fist's hole, then turned into the hanging rest
  hand's line), rigid on its own prop bone `DEF-staff` under `DEF-hand.L` (build_pell). The grip span (the fist and
  `grip_clear_m` either side) carries no node and no lashing (Toma's spear lesson).
* **The name-shell** (`NameShell`): a plaited cord close round the lower neck, `shell_cord_clear_m` off the neck all
  round at rest, and the shell on its front, rigid to the cord, sitting on the throat stripe with `shell_clear_m`
  clearance. Two meshes for the two states (pell.md §3): `NameShellBlank` (Acts I-II, ground smooth, matte) and
  `NameShellCarved` (Act III, the same shape, the spiral of notches from motifs/pell_name.json painted on its own
  island); never both visible (the scene toggles them, pell_name_shell.gd). All rigid on DEF-spine.004.

Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, catmull_rom, tube, uv_sphere
from asha_staff import held_frame, to_held
from pell_costume import ATLAS

TAG_PROP = 63
SHAFT_SEG = 10
SHAFT_ROWS = 26


def _rect_sub(rect, a: float, b: float) -> tuple:
    u0, v0, u1, v1 = rect
    return (u0 + (u1 - u0) * a, v0, u0 + (u1 - u0) * b, v1)


def staff_line(lm, sp: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """(grip, R, base, length): the fist's hole and its held rotation (asha_staff.held_frame on the left hand), the
    staff's foot (built upright under the grip, on the floor) and its length."""
    S = lm.S
    r_grip = 0.5 * float(np.interp(0.5, [0.0, 1.0], [float(sp["foot_m"]), float(sp["tip_m"])])) * S
    grip, R = held_frame(lm, "L", r_grip)
    base = np.array([grip[0], grip[1], float(sp["floor_m"])])
    return grip, R, base, float(sp["staff_m"])


def staff(lm, sp: dict) -> tuple[Part, dict]:
    """The fishing-staff, upright through the left fist's hole, then turned into the held line (asha_staff.to_held)."""
    S = lm.S
    part = Part("Staff")
    grip, R, base, L = staff_line(lm, sp)
    up = np.array([0.0, 0.0, 1.0])
    fwd = np.array([0.0, -1.0, 0.0])
    side = np.array([1.0, 0.0, 0.0])
    tip_L = float(sp["bone_tip_m"])
    shaft_L = L - tip_L + float(sp["tip_socket_m"])  # the bone tip's socket runs into the shaft's end
    g = float(grip[2] - base[2])  # the grip's height up the shaft
    clear = float(sp["grip_clear_m"])
    # growth nodes: evenly up the shaft, each moved off the grip span
    nodes = []
    for k in range(int(sp["nodes"])):
        h = shaft_L * (k + 0.8) / (int(sp["nodes"]) + 0.6)
        if abs(h - g) < clear + 0.03 * S:
            h = g + math.copysign(clear + 0.03 * S, h - g)
        nodes.append(h)
    h = np.linspace(0.0, shaft_L, SHAFT_ROWS)
    h = np.unique(np.concatenate([h, [n + d for n in nodes for d in (-0.012 * S, 0.0, 0.012 * S)]]))
    h = h[(h >= 0.0) & (h <= shaft_L)]
    rad = 0.5 * S * np.interp(h / shaft_L, [0.0, 1.0], [float(sp["foot_m"]), float(sp["tip_m"])])
    for n in nodes:
        rad = rad * (1.0 + 0.10 * np.exp(-(((h - n) / (0.006 * S)) ** 2)))
    C = base[None, :] + np.outer(h, up)
    # V along the shaft (0 foot .. 1 top); the node bands are painted from `nodes` (pell_textures)
    u0, v0, u1, v1 = ATLAS["staff_shaft"]
    tube(part, C, rad, SHAFT_SEG, "cloth", fwd, (u0, v0, u1, v1), tags=TAG_PROP, cap_end=True)
    # the foot's cap
    c0 = part.add_v(base - up * 0.002 * S, tag=TAG_PROP)
    for i in range(SHAFT_SEG):
        a, b = i, (i + 1) % SHAFT_SEG
        part.add_f((b, a, c0), [(u0, v0)] * 3, "cloth")
    # the barbed bone tip: a slim cone with three backward barbs on its fwd side, lashed over its socket
    top = base + up * shaft_L
    t = np.linspace(0.0, 1.0, 9)
    rtip = float(sp["tip_m"]) * 0.5 * S * (1.0 - t) ** 0.8 + 0.0008 * S
    Ct = top[None, :] - up * float(sp["tip_socket_m"]) + np.outer(t * tip_L, up)
    tube(part, Ct, rtip, 8, "cloth", fwd, ATLAS["staff_tip"], tags=TAG_PROP, cap_end=True)
    for k in range(int(sp["barbs"])):
        hb = top + up * tip_L * (0.35 + 0.18 * k) - up * float(sp["tip_socket_m"])
        root = hb + fwd * float(np.interp(0.35 + 0.18 * k, t, rtip)) * 0.8
        barb = np.array([root, root + fwd * 0.006 * S - up * 0.004 * S, root + fwd * 0.010 * S - up * 0.012 * S])
        tube(part, barb, np.array([0.0022, 0.0014, 0.0004]) * S, 5, "cloth", side, ATLAS["staff_tip"], tags=TAG_PROP)
    lash_lo = top[2] - float(sp["tip_socket_m"])
    for z0, z1 in ((lash_lo, lash_lo + float(sp["lash_m"])),):
        n_t = 6
        for i in range(n_t):
            zz = z0 + (z1 - z0) * (i + 0.5) / n_t
            r0 = float(np.interp(zz - base[2], h, rad)) if zz - base[2] <= shaft_L else float(sp["tip_m"]) * 0.5 * S
            ring = np.array([base[0], base[1], zz])
            ang = np.linspace(0.0, 2 * math.pi, 9)
            Cr = ring[None, :] + (r0 + 0.0016 * S) * (np.outer(np.cos(ang), side) + np.outer(np.sin(ang), fwd))
            tube(part, Cr, 0.0016 * S, 3, "cloth", up, ATLAS["staff_lash"], tags=TAG_PROP)
    # the counterweight stone in its cord net, lashed 30 cm above the foot, on the shaft's outer side (his left)
    zs = base[2] + float(sp["stone_above_m"])
    rs = 0.5 * float(sp["stone_m"])
    r_at = float(np.interp(zs - base[2], h, rad))
    cs = np.array([base[0], base[1], zs]) + side * (r_at + rs * 0.92)
    uv_sphere(part, cs, np.array([rs, rs * 0.8, rs * 1.15]), 10, 7, "cloth", axis_fwd=side,
              uv_rect=ATLAS["staff_stone"], tags=TAG_PROP)
    for k in range(3):  # the net's cords over the stone
        a = math.pi * k / 3
        d1 = math.cos(a) * fwd + math.sin(a) * up
        ang = np.linspace(0.0, 2 * math.pi, 11)
        Cn = cs[None, :] + np.outer(np.cos(ang), d1 * rs * 1.04) + np.outer(np.sin(ang), side * rs * 0.96)
        tube(part, Cn, 0.0014 * S, 3, "cloth", d1, ATLAS["staff_net"], tags=TAG_PROP)
    for dz in (-0.5 * rs, 0.5 * rs):  # the lashing to the shaft
        zz = zs + dz
        ring = np.array([base[0], base[1], zz])
        ang = np.linspace(0.0, 2 * math.pi, 9)
        Cr = ring[None, :] + (r_at + 0.0015 * S) * (np.outer(np.cos(ang), side) + np.outer(np.sin(ang), fwd))
        tube(part, Cr, 0.0015 * S, 3, "cloth", up, ATLAS["staff_net"], tags=TAG_PROP)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    rows = len(h)
    node_v = [float(np.argmin(np.abs(h - n_))) / (rows - 1) for n_ in nodes]  # the node rows' V on the shaft's island
    info = {"grip": grip, "R": R, "base": base, "length": L, "nodes": [float(n) for n in nodes], "node_v": node_v,
            "grip_height": g, "shaft_length": shaft_L, "stone_above": float(sp["stone_above_m"])}
    return to_held(part, grip, R), info


def staff_bone(lm, sp: dict, length: float) -> tuple[np.ndarray, np.ndarray]:
    """(head, tail) of DEF-staff: from the grip along the held shaft, towards its top."""
    grip, R, _base, _L = staff_line(lm, sp)
    return grip, grip + R @ np.array([0.0, 0.0, length])


# ---------------------------------------------------------------------------------------------
# the name-shell
# ---------------------------------------------------------------------------------------------
def neck_ring(neck_P: np.ndarray, z: float, centre: np.ndarray, n: int, band: float) -> tuple[np.ndarray, np.ndarray]:
    """(radius per direction, direction) of the neck's skin at height z round `centre` (the skin's outermost point in
    each of n directions within `band` of z)."""
    ang = 2 * math.pi * np.arange(n) / n
    D = np.stack([np.sin(ang), -np.cos(ang), np.zeros(n)], axis=1)
    near = neck_P[np.abs(neck_P[:, 2] - z) < band]
    q = near[:, :2] - centre[:2]
    a = np.arctan2(q[:, 0], -q[:, 1])
    rr = np.hypot(q[:, 0], q[:, 1])
    r = np.zeros(n)
    for i in range(n):
        m = np.abs(np.angle(np.exp(1j * (a - ang[i])))) < 0.35
        r[i] = rr[m].max() if m.any() else float(rr.max())
    return r, D


def name_shell(lm, shp: dict, neck_P: np.ndarray, motifs: dict) -> tuple[dict, dict]:
    """The throat cord and the two shells ({mesh name: Part}). `neck_P`: the neck's skin vertices (build_pell: the
    shipped torso skin above the sternal notch, below the head seam)."""
    S = lm.S
    z = float(lm.P("notch")[2]) + float(shp["cord_above_notch_m"])
    centre = np.array([0.0, float(np.median(neck_P[np.abs(neck_P[:, 2] - z) < 0.01 * S][:, 1])), z])
    n = 24
    r, D = neck_ring(neck_P, z, centre, n, 0.012 * S)
    for _ in range(3):  # a cord pulled round the neck: no dents
        r = np.maximum(r, 0.5 * r + 0.25 * (np.roll(r, 1) + np.roll(r, -1)))
    rc = 0.5 * float(shp["cord_m"])
    clear = float(shp["cord_clear_m"])
    C = centre[None, :] + D * (r + clear + rc)[:, None]
    # the cord sags a little at the front, where the shell's weight pulls it
    C[:, 2] -= float(shp["cord_sag_m"]) * np.clip(-D[:, 1], 0.0, 1.0) ** 2
    cord = Part("NameShellCord")
    tube(cord, np.concatenate([C, C[:1]]), rc, 3, "cloth", np.array([0.0, 0.0, 1.0]), ATLAS["shell_cord"],
         tags=TAG_PROP)
    front = C[0]  # D[0] = -Y: the front
    radius = 0.5 * float(shp["shell_m"])
    out = np.array([0.0, -1.0, 0.0])
    # the shell hangs below the cord's front: its pierced top at the cord, its back `shell_clear_m` off the throat
    neck_front = centre + D[0] * r[0]
    sc = np.array([0.0, 0.0, front[2] - radius - 0.004 * S])
    rs, Ds = neck_ring(neck_P, float(sc[2]), centre, n, 0.012 * S)
    sc[1] = float(centre[1] - rs[0]) - float(shp["shell_clear_m"]) - float(shp["shell_depth_m"])
    parts = {"NameShellCord": cord}
    for name, rect in (("NameShellBlank", ATLAS["shell_blank"]), ("NameShellCarved", ATLAS["shell_carved"])):
        p = Part(name)
        _shell_disc(p, sc, radius, float(shp["shell_depth_m"]), out, rect)
        # the cord through its pierced top
        loop = np.array([front, sc + np.array([0.0, -0.002 * S, radius * 0.82]), sc + np.array([0.0, 0.003 * S,
                                                                                            radius * 0.82])])
        tube(p, catmull_rom(loop, 5), rc * 0.8, 3, "cloth", out, ATLAS["shell_cord"], tags=TAG_PROP)
        p.C = [(0.0, 0.0, 0.0, 0.0)] * len(p.V)
        parts[name] = p
    cord.C = [(0.0, 0.0, 0.0, 0.0)] * len(cord.V)
    info = {"cord_z": z, "neck_r": r, "cord_line": C, "shell_centre": sc, "neck_front": neck_front,
            "carving": motifs["name"]}
    return parts, info


def _shell_disc(part: Part, c: np.ndarray, radius: float, depth: float, out: np.ndarray, rect) -> None:
    """A flat half-shell disc facing `out`: a shallow dome (front) over a flat back, its UV the disc's plan in `rect`
    (the carving is painted in the same plan)."""
    up = np.array([0.0, 0.0, 1.0])
    side = np.cross(up, out)
    u0, v0, u1, v1 = rect
    rings, seg = 2, 12

    def uv(x: float, y: float) -> tuple:
        return (u0 + (u1 - u0) * (0.5 + 0.5 * x), v0 + (v1 - v0) * (0.5 - 0.5 * y))

    front_ids, back_ids = [], []
    ang = 2 * math.pi * np.arange(seg) / seg
    for face, sgn in ((front_ids, 1.0), (back_ids, -1.0)):
        centre_id = part.add_v(c + out * depth * (0.5 + 0.5 * sgn), tag=TAG_PROP)
        face.append([centre_id])
        for k in range(1, rings + 1):
            rr = radius * k / rings
            dome = depth * (1.0 - (k / rings) ** 2) if sgn > 0 else 0.0
            ring = [part.add_v(c + side * rr * math.cos(a) + up * rr * math.sin(a) + out * dome, tag=TAG_PROP)
                    for a in ang]
            face.append(ring)
    for face, flip in ((front_ids, False), (back_ids, True)):
        for i in range(seg):
            j = (i + 1) % seg
            q = (face[0][0], face[1][i], face[1][j])
            uvq = [uv(0, 0), uv(math.cos(ang[i]) / rings, math.sin(ang[i]) / rings),
                   uv(math.cos(ang[j]) / rings, math.sin(ang[j]) / rings)]
            if flip:
                q, uvq = q[::-1], uvq[::-1]
            part.add_f(q, uvq, "cloth")
        for k in range(1, rings):
            for i in range(seg):
                j = (i + 1) % seg
                q = (face[k][i], face[k + 1][i], face[k + 1][j], face[k][j])
                f0, f1 = k / rings, (k + 1) / rings
                uvq = [uv(f0 * math.cos(ang[i]), f0 * math.sin(ang[i])), uv(f1 * math.cos(ang[i]), f1 * math.sin(ang[i])),
                       uv(f1 * math.cos(ang[j]), f1 * math.sin(ang[j])), uv(f0 * math.cos(ang[j]), f0 * math.sin(ang[j]))]
                if flip:
                    q, uvq = q[::-1], uvq[::-1]
                part.add_f(q, uvq, "cloth")
    # the rim: front ring to back ring
    for i in range(seg):
        j = (i + 1) % seg
        q = (front_ids[-1][i], back_ids[-1][i], back_ids[-1][j], front_ids[-1][j])
        part.add_f(q, [uv(math.cos(ang[i]), math.sin(ang[i]))] * 2 + [uv(math.cos(ang[j]), math.sin(ang[j]))] * 2,
                   "cloth")
