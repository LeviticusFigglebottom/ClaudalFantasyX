"""Pell's costume as procedural pieces (no bpy), pell.md §3-§4 and §9.

Same method as the other heroes' (asha_costume, rhen_costume, kerrid_costume): every garment is a pattern grid whose
rows are ray-cast onto the body field plus a fitting offset, and the grid is also the piece's island in the 2K costume
atlas (pell_textures paints the same charts). The Kirru dislike clothing, so there is little of it, and every piece is
torso-only, on the forearms, on the neck or at the hips (pell.md §4.2: nothing hangs below the hips, no footwear, nothing
on the head). Pieces (pell.md §4.1):

1. **The reed mantle** over the right shoulder (`Mantle`): one torso sheet from just left of the sternum round the right
   side to just right of the spine. Its front and back falls reach the right hip; over the arm its edge is a band
   `mantle_arm_drop_m` (12 cm) below the shoulder joint, cast onto the shoulder cap and the top of the upper arm (the
   mantle field: the torso plus the right arm within `mantle_cap_m` of the shoulder joint). The neck edge stays
   `mantle_neck_clear_m` off the neck (the neck's skin is probed by build_pell). Stiff reed: a thick back layer.
2. **The mantle cord and the bone toggle**: a 5 mm cord from the mantle's front corner across the chest, under the left
   arm `cord_underarm_drop_m` (13 cm) below the shoulder joint, round the back to the mantle's back corner; the 7 cm
   toggle bar at the left of the sternum.
3. The **belt cord** at the hips, the woven-reed **pouch** at the left hip and the **line coil** (8 turns) at the right,
   `hip_gear_off_m` off the hip.
4. The **shell-tile wraps** (`Wraps`, both forearms): a plaited cord wound `wrap_turns` times from `wrap_above_wrist_m`
   above the wrist crease to mid-forearm, carrying runs of square shell tiles in the motif sequence (motifs/
   pell_tiles.json: the left wrap the call, the right the response).
5. The **ankle cord**: one turn round the right shin `ankle_cord_above_m` above the ankle bone, three tiles on it.

Vertex colour = wind (none here: reed, cord and shell do not flutter). `coverage()` says which body vertices are hidden
under the mantle (deleted, asha.md §8.1), well inside its edges. Deterministic.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import bb_anatomy
import rhen_costume as RC
from asha_costume import TAG_CLOTH, Fields, TorsoChart, _panel, cast_last, dir_theta
from asha_mesh import Part, catmull_rom, frames_along, tube

HERE = Path(__file__).resolve().parent
MOTIFS = HERE / "motifs"
# costume and props atlas islands (u0, v0, u1, v1), the shader's UV convention (v down); pell_textures paints them
ATLAS = {
    "mantle": (0.0, 0.0, 0.5, 0.5),
    "mantle_cord": (0.5, 0.0, 0.75, 0.03),
    "toggle": (0.75, 0.0, 0.82, 0.03),
    "belt": (0.5, 0.03, 0.75, 0.06),
    "pouch": (0.5, 0.06, 0.62, 0.16),
    "line": (0.62, 0.06, 0.75, 0.10),
    "wrap_cord": (0.75, 0.03, 1.0, 0.06),
    "tile_bone": (0.75, 0.06, 0.8125, 0.10),
    "tile_reed": (0.8125, 0.06, 0.875, 0.10),
    "tile_dark": (0.875, 0.06, 0.9375, 0.10),
    "tile_nacre": (0.9375, 0.06, 1.0, 0.10),
    "shell_blank": (0.5, 0.16, 0.62, 0.28),
    "shell_carved": (0.62, 0.16, 0.74, 0.28),
    "shell_cord": (0.74, 0.16, 1.0, 0.19),
    "staff_shaft": (0.0, 0.5, 0.03, 1.0),
    "staff_tip": (0.03, 0.5, 0.08, 0.6),
    "staff_stone": (0.08, 0.5, 0.18, 0.6),
    "staff_net": (0.18, 0.5, 0.28, 0.55),
    "staff_lash": (0.28, 0.5, 0.38, 0.53),
    "web": (0.38, 0.5, 0.43, 0.55),
}
TILE_TONES = ("bone", "reed", "dark", "nacre")
MANTLE_COLS = 36
MANTLE_ROWS = 16
MANTLE_BACK = 0.004  # m (at s = 1): the reed's thickness (the back layer's inset)
CORD_SEG = 5
TILE_SEG_INSET = 0.25  # of a tile's half-size: its top face's chamfer (the rounded corners)


def load_motifs() -> dict:
    """motifs/pell_tiles.json (the call and response sequences) and motifs/pell_name.json (the name spiral)."""
    return {"tiles": json.loads((MOTIFS / "pell_tiles.json").read_text(encoding="utf-8")),
            "name": json.loads((MOTIFS / "pell_name.json").read_text(encoding="utf-8"))}


def smooth01(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def angle_deg(th_deg: np.ndarray) -> np.ndarray:
    """Azimuth wrapped to (-180, 180]: 0 the front, +90 his left, -90 his right."""
    return ((np.asarray(th_deg, dtype=float) + 180.0) % 360.0) - 180.0


# ---------------------------------------------------------------------------------------------
# 1. the reed mantle
# ---------------------------------------------------------------------------------------------
def mantle_field(fields: Fields, cp: dict):
    """The torso plus the right arm within `mantle_cap_m` of its shoulder joint: the mantle's side band drapes over the
    shoulder cap and the top of the upper arm."""
    lm = fields.lm
    S = lm.S
    sh = lm.side_pt("shoulder", "R")
    cap = float(cp["mantle_cap_m"])
    torso = fields.body.regions["torso"].sdf
    arm = fields.body.regions["arm_R"].sdf

    def f(P: np.ndarray) -> np.ndarray:
        a = np.maximum(arm(P), np.linalg.norm(P - sh, axis=1) - cap)
        return bb_anatomy.smin(torso(P), a, 0.02 * S)

    return f


def mantle_lines(lm, chart: TorsoChart, cp: dict, th_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(H_top, H_bot) per column: the neck edge (low at the front and back edges, up over the shoulder top) and the
    hem (the right hip in the falls, the arm band over the arm)."""
    S = lm.S
    a = angle_deg(th_deg)
    z_w, z_h = float(lm.P("waist")[2]), float(lm.side_pt("hip", "R")[2])
    hem = z_w + (z_h - z_w) * float(cp["mantle_hem_at"])  # above the belt cord: the hip gear hangs free below it
    arm = float(lm.side_pt("shoulder", "R")[2]) - float(cp["mantle_arm_drop_m"])
    f0, f1, b0, b1 = (float(x) for x in cp["mantle_arm_band_deg"])  # where the falls hand over to the arm band
    H_bot = np.interp(-a, [-10.0, f0, f1, b0, b1, 190.0], [hem, hem, arm, arm, hem, hem])
    e_edge, e_top = (math.radians(float(x)) for x in cp["mantle_neck_elev_deg"])
    side = smooth01(np.sin(np.radians(-a)) ** 2)  # 0 at the front and back, 1 over the shoulder
    H_top = chart.z_sh + chart.k * (e_edge + (e_top - e_edge) * side)
    return H_top, H_bot


def mantle_columns(cp: dict, t: float) -> np.ndarray:
    """A row's column azimuths (degrees): its front and back edges run diagonally from near the sternum and the spine
    at the neck down to the right hip (the falls narrow toward the hem: a mat laid over one shoulder)."""
    f = float(cp["mantle_front_deg"]) + (float(cp["mantle_front_hem_deg"]) - float(cp["mantle_front_deg"])) * t
    b = float(cp["mantle_back_deg"]) + (float(cp["mantle_back_hem_deg"]) - float(cp["mantle_back_deg"])) * t
    return np.linspace(f, b, MANTLE_COLS)


def mantle(fields: Fields, chart: TorsoChart, cp: dict) -> Part:
    """The reed mantle (pell.md §3, §4.1 #1): one sheet over the right shoulder, rows from the neck edge down. Stiff
    reed: below the shoulders each column hangs plumb from where it last touched the body (it can come in toward the
    body no faster than `mantle_hang_slope` of its drop), and each row is smoothed round the body."""
    lm = fields.lm
    S = lm.S
    part = Part("Mantle")
    part._mat = "cloth"
    field = mantle_field(fields, cp)
    off = float(cp["mantle_off_m"])
    P = np.zeros((MANTLE_ROWS, MANTLE_COLS, 3))
    TH = np.zeros((MANTLE_ROWS, MANTLE_COLS))
    fn = lambda Q: field(Q) - off  # noqa: E731
    for j in range(MANTLE_ROWS):
        t = j / (MANTLE_ROWS - 1)
        th_deg = mantle_columns(cp, t)
        H_top, H_bot = mantle_lines(lm, chart, cp, th_deg)
        th = np.radians(th_deg)
        O, D = chart.rays(th, H_top + (H_bot - H_top) * t)
        r = cast_last(fn, O, D, 0.5 * S)
        P[j] = O + D * r[:, None]
        TH[j] = th_deg
    c = np.array([0.0, chart.y_axis, 0.0])
    slope = float(cp["mantle_hang_slope"])
    # stiff reed over the shoulder too: the radii off the chart's axis relaxed over the grid (no dent of the body
    # shows through the mat; it only moves outward)
    for _ in range(int(cp["mantle_relax"])):
        q = P - c
        rad = np.linalg.norm(q, axis=2)
        avg = rad.copy()
        avg[1:-1, 1:-1] = 0.25 * (rad[:-2, 1:-1] + rad[2:, 1:-1] + rad[1:-1, :-2] + rad[1:-1, 2:])
        new = np.maximum(rad, avg)
        P = c + q * (new / np.maximum(rad, 1e-9))[..., None]
    for j in range(MANTLE_ROWS):
        q = P[j] - c
        rad = np.hypot(q[:, 0], q[:, 1])
        if j > 0:  # the plumb hang (horizontal rays only: below the chart's shoulder pivot)
            qa = P[j - 1] - c
            ra = np.hypot(qa[:, 0], qa[:, 1])
            drop = np.maximum(P[j - 1][:, 2] - P[j][:, 2], 0.0)
            low = P[j][:, 2] < chart.z_sh
            rad = np.where(low, np.maximum(rad, ra - slope * drop), rad)
        sm = rad.copy()
        for _ in range(3):
            sm = np.maximum(sm, 0.5 * sm + 0.25 * (np.roll(sm, 1) + np.roll(sm, -1)))
        sm[0], sm[-1] = rad[0], rad[-1]
        P[j, :, :2] = c[:2] + q[:, :2] * (sm / np.maximum(np.hypot(q[:, 0], q[:, 1]), 1e-9))[:, None]
    _panel(part, P, ATLAS["mantle"], None, False, MANTLE_BACK * S, c)
    part.grid_P = P
    part.th_deg = TH
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part


# ---------------------------------------------------------------------------------------------
# 2. the mantle cord and the bone toggle
# ---------------------------------------------------------------------------------------------
def mantle_cord(fields: Fields, chart: TorsoChart, cp: dict, mantle_part: Part) -> tuple[Part, np.ndarray]:
    """From the mantle's front corner across the chest to the toggle at the left of the sternum, under the left arm
    `cord_underarm_drop_m` below the shoulder joint, round the back to the mantle's back corner (on the cord's own
    offset over the torso). Returns (part with the cord and the toggle, the cord's centre line)."""
    lm = fields.lm
    S = lm.S
    part = Part("MantleCord")
    part._mat = "cloth"
    rc = 0.5 * float(cp["mantle_cord_m"])
    G = mantle_part.grid_P
    k = int(round(float(cp["mantle_corner_row"]) * (G.shape[0] - 1)))
    front, back = G[k, 1], G[k, -2]
    sh_z = float(lm.side_pt("shoulder", "L")[2])
    under = sh_z - float(cp["cord_underarm_drop_m"])
    tog_deg = float(cp["toggle_deg"])
    torso = fields.body.regions["torso"].sdf
    off = rc + float(cp["cord_off_m"]) + float(cp["mantle_off_m"]) * 0.5
    fn = lambda Q: torso(Q) - off  # noqa: E731
    # control points round the left side: (azimuth, height)
    z_f, z_b = float(front[2]), float(back[2])
    ctrl = [(tog_deg, 0.55 * z_f + 0.45 * under), (50.0, under + 0.012 * S), (90.0, under),
            (130.0, under + 0.012 * S), (170.0, 0.5 * (under + z_b))]
    th = np.radians(np.array([c[0] for c in ctrl]))
    H = np.array([c[1] for c in ctrl])
    O, D = chart.rays(th, H)
    pts = O + D * cast_last(fn, O, D, 0.5 * S)[:, None]
    line = catmull_rom(np.concatenate([[front], pts, [back]]), 72)
    # pulled tight round the ribs: points that sank toward the body are pushed back out to the offset
    for _ in range(2):
        q = line - np.array([0.0, chart.y_axis, 0.0])
        ang = np.arctan2(q[:, 0], -q[:, 1])
        O2 = np.stack([np.zeros(len(line)), np.full(len(line), chart.y_axis), line[:, 2]], axis=1)
        r = cast_last(fn, O2, dir_theta(ang), 0.5 * S)
        rad = np.hypot(q[:, 0], q[:, 1])
        mid = np.arange(len(line))
        keep = (mid > 2) & (mid < len(line) - 3)
        scale = np.where(keep & (rad < r), r / np.maximum(rad, 1e-9), 1.0)
        line[:, :2] = np.array([0.0, chart.y_axis]) + q[:, :2] * scale[:, None]
    tube(part, line, rc, CORD_SEG, "cloth", np.array([0.0, 0.0, 1.0]), ATLAS["mantle_cord"], tags=TAG_CLOTH)
    # the toggle: a 7 cm bar of pale bone across the cord at the left of the sternum, lying on the chest
    i = int(np.argmin(np.abs(np.degrees(np.arctan2(line[:, 0], -(line[:, 1] - chart.y_axis))) - tog_deg)))
    c = line[i]
    tdir = line[min(i + 2, len(line) - 1)] - line[max(i - 2, 0)]
    tdir /= np.linalg.norm(tdir)
    nrm = dir_theta(np.array([math.radians(tog_deg)]))[0]
    bar = np.cross(nrm, tdir)
    bar = 0.35 * bar + 0.65 * np.array([0.0, 0.0, 1.0])  # a bar set across the cord, near upright
    bar /= np.linalg.norm(bar)
    L = float(cp["toggle_m"])
    C = np.array([c + nrm * rc * 1.6 + bar * L * (t - 0.5) for t in np.linspace(0.0, 1.0, 6)])
    tube(part, C, np.array([0.55, 0.85, 1.0, 1.0, 0.85, 0.55]) * float(cp["toggle_r_m"]), 8, "cloth", nrm,
         ATLAS["toggle"], tags=TAG_CLOTH, cap_end=True)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part, line


# ---------------------------------------------------------------------------------------------
# 3. the belt cord, the pouch and the line coil
# ---------------------------------------------------------------------------------------------
def belt_cord(fields: Fields, cp: dict) -> tuple[Part, np.ndarray, float]:
    """A plaited cord round the hips (a ring on the lower field plus the hip gear's offset). Returns (part, the ring,
    its height)."""
    lm = fields.lm
    S = lm.S
    part = Part("BeltCord")
    part._mat = "cloth"
    rc = 0.5 * float(cp["belt_cord_m"])
    z = float(lm.P("waist")[2]) + (float(lm.side_pt("hip", "L")[2]) - float(lm.P("waist")[2])) * float(cp["belt_at"])
    n = 40
    th = np.radians(np.linspace(0.0, 360.0, n, endpoint=False))
    O = np.stack([np.zeros(n), np.full(n, 0.01 * S), np.full(n, z)], axis=-1)
    D = dir_theta(th)
    fn = lambda Q: fields.lower(Q) - (rc + float(cp["cord_off_m"]))  # noqa: E731
    r = cast_last(fn, O, D, 0.4 * S)
    for _ in range(3):
        r = np.maximum(r, 0.5 * r + 0.25 * (np.roll(r, 1) + np.roll(r, -1)))
    C = O + D * r[:, None]
    tube(part, np.concatenate([C, C[:1]]), rc, CORD_SEG, "cloth", np.array([0.0, 0.0, 1.0]), ATLAS["belt"],
         tags=TAG_CLOTH)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part, C, z


def _box(part: Part, c: np.ndarray, ex: np.ndarray, ey: np.ndarray, ez: np.ndarray, half: np.ndarray, rect,
         inset: float = 0.0) -> None:
    """A box (8 corners) with its outer face (+ez) chamfered in by `inset` of its half-sizes."""
    corners = []
    for sz in (-1.0, 1.0):
        k = (1.0 - inset) if sz > 0 else 1.0
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            corners.append(c + ex * half[0] * sx * k + ey * half[1] * sy * k + ez * half[2] * sz)
    ids = [part.add_v(p, tag=TAG_CLOTH) for p in corners]
    u0, v0, u1, v1 = rect
    quad = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    faces = [(4, 5, 6, 7), (3, 2, 1, 0), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    for f in faces:
        part.add_f([ids[i] for i in f], quad, "cloth")


def pouch(fields: Fields, cp: dict, ring: np.ndarray, z_belt: float) -> tuple[Part, dict]:
    """The woven-reed pouch at the left hip, hung on the belt cord, `hip_gear_off_m` off the hip (pell.md §4.1 #6)."""
    lm = fields.lm
    S = lm.S
    part = Part("Pouch")
    part._mat = "cloth"
    w, h, d = (float(x) for x in cp["pouch_m"])
    a = math.radians(float(cp["pouch_deg"]))
    out = np.array([math.sin(a), -math.cos(a), 0.0])
    up = np.array([0.0, 0.0, 1.0])
    side = np.cross(up, out)
    # where the hip's surface is under the pouch: the lower field along `out` at the pouch's middle height
    zc = z_belt - 0.5 * h - 0.01 * S
    O = np.array([[0.0, 0.01 * S, zc]])
    r = float(cast_last(fields.lower, O, out[None, :], 0.4 * S)[0])
    c = O[0] + out * (r + float(cp["hip_gear_off_m"]) + 0.5 * d)
    _box(part, c, side, up, out, np.array([0.5 * w, 0.5 * h, 0.5 * d]), ATLAS["pouch"], TILE_SEG_INSET * 0.3)
    # its flap's tie to the belt cord
    k = int(np.argmin(np.linalg.norm(ring - (c + up * 0.5 * h), axis=1)))
    tie = np.array([c + up * 0.5 * h + out * 0.25 * d, 0.5 * (c + up * 0.5 * h + ring[k]) + out * 0.006 * S, ring[k]])
    tube(part, catmull_rom(tie, 6), 0.0022 * S, 5, "cloth", out, ATLAS["belt"], tags=TAG_CLOTH)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part, {"centre": c, "out": out}


def line_coil(fields: Fields, cp: dict, ring: np.ndarray, z_belt: float) -> tuple[Part, dict]:
    """The coil of spare line at the right hip: `coil_turns` turns, `coil_m` across, its axis out from the hip
    (rhen_costume.tether_coil's form on the other side), hung from the belt cord."""
    lm = fields.lm
    S = lm.S
    part = Part("LineCoil")
    part._mat = "cloth"
    turns = int(cp["coil_turns"])
    R = 0.5 * float(cp["coil_m"])
    rl = 0.5 * float(cp["coil_line_m"])
    a = math.radians(float(cp["coil_deg"]))
    ax = np.array([math.sin(a), -math.cos(a), 0.0])
    zc = z_belt - R - 0.012 * S
    O = np.array([[0.0, 0.01 * S, zc]])
    r = float(max(cast_last(fields.lower, O + np.array([[0.0, 0.0, dz]]), ax[None, :], 0.4 * S)[0]
                  for dz in (-R, 0.0, R)))
    c = O[0] + ax * (r + float(cp["hip_gear_off_m"]) + turns * rl * 0.5)
    e1 = np.array([0.0, 0.0, 1.0])
    e2 = np.cross(ax, e1)
    n = turns * 10
    t = np.linspace(0.0, turns * 2 * math.pi, n)
    rr = R - rl * 1.4 * ((t / (2 * math.pi)) % 3)
    off = rl * 1.9 * (t / (2 * math.pi) - turns / 2) * 0.3
    C = c[None, :] + np.outer(np.cos(t) * rr, e1) + np.outer(np.sin(t) * rr, e2) + np.outer(off, ax)
    tube(part, C, rl, 4, "cloth", ax, ATLAS["line"], tags=TAG_CLOTH)
    k = int(np.argmin(np.linalg.norm(ring - (c + e1 * R), axis=1)))
    tie = np.array([c + e1 * (R - rl), c + e1 * (R + 0.008 * S) + ax * 0.004 * S, ring[k]])
    tube(part, catmull_rom(tie, 6), rl * 0.9, 5, "cloth", ax, ATLAS["belt"], tags=TAG_CLOTH)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part, {"centre": c, "out": ax}


# ---------------------------------------------------------------------------------------------
# 4-5. the shell-tile wraps and the ankle cord
# ---------------------------------------------------------------------------------------------
def tile_sequence(motifs: dict, side: str) -> list:
    """The tile tones of a wrap, turn by turn (the left wrap the call, the right the response: the same tones
    mirrored, pell.md §3)."""
    seq = [list(turn) for turn in motifs["tiles"]["call"]]
    if side == "R":
        seq = [list(reversed(turn)) for turn in reversed(seq)]
    return seq


def _surface_ring(fn, c: np.ndarray, ax: np.ndarray, n: int, tmax: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ref = np.array([0.0, 0.0, 1.0]) if abs(ax[2]) < 0.9 else np.array([0.0, -1.0, 0.0])
    e1 = ref - (ref @ ax) * ax
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    ang = 2 * math.pi * np.arange(n) / n
    D = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
    r = cast_last(fn, np.repeat(c[None, :], n, axis=0), D, tmax)
    return r, e1, e2


def forearm_wrap(fields: Fields, cp: dict, side: str, motifs: dict) -> tuple[Part, np.ndarray]:
    """One shell-tile wrap: the plaited cord as a helix over the forearm (`wrap_turns` turns from `wrap_above_wrist_m`
    above the wrist crease to mid-forearm, `tile_off_m` off the skin) and the tiles on it, each a chamfered box facing
    out. Returns (part, per-vertex position along the forearm 0 (elbow) .. 1 (wrist))."""
    lm = fields.lm
    S = lm.S
    part = Part(f"Wrap{side}")
    part._mat = "cloth"
    el, wr = lm.side_pt("elbow", side), lm.side_pt("wrist", side)
    fl = float(np.linalg.norm(wr - el))
    ax = (wr - el) / fl
    t1 = 1.0 - float(cp["wrap_above_wrist_m"]) / fl
    t0 = float(cp["wrap_from"])
    turns = int(cp["wrap_turns"])
    rc = 0.5 * float(cp["wrap_cord_m"])
    tile = float(cp["tile_m"])
    thick = float(cp["tile_thick_m"])
    off = float(cp["tile_off_m"])
    reg = fields.region(f"arm_{side}")
    n_h = turns * 12
    tt = np.linspace(t0, t1, n_h)
    ang = np.linspace(0.0, turns * 2 * math.pi, n_h) * (1.0 if side == "L" else -1.0)
    C, Nout = [], []
    for t, a in zip(tt, ang):
        c = el + (wr - el) * t
        r, e1, e2 = _surface_ring(reg, c, ax, 24, 0.2 * S)
        d = math.cos(a) * e1 + math.sin(a) * e2
        k = int(round((a % (2 * math.pi)) / (2 * math.pi) * 24)) % 24
        rr = float(np.max(r[[(k - 1) % 24, k, (k + 1) % 24]]))
        C.append(c + d * (rr + off + rc))
        Nout.append(d)
    C, Nout = np.array(C), np.array(Nout)
    tube(part, C, rc, 3, "cloth", ax, ATLAS["wrap_cord"], tags=TAG_CLOTH)
    along = list(np.repeat(tt, 3))
    seq = tile_sequence(motifs, side)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))])
    per_turn = s[-1] / turns
    for k, run in enumerate(seq[:turns]):
        n = len(run)
        mid = per_turn * (k + 0.5)
        for i, tone in enumerate(run):
            at = mid + (i - 0.5 * (n - 1)) * tile * 1.12
            j = int(np.clip(np.searchsorted(s, at), 1, len(C) - 1))
            f = (at - s[j - 1]) / max(s[j] - s[j - 1], 1e-9)
            p = C[j - 1] + (C[j] - C[j - 1]) * f
            out = Nout[j - 1] + (Nout[j] - Nout[j - 1]) * f
            out /= np.linalg.norm(out)
            tan = C[j] - C[j - 1]
            tan = tan - (tan @ out) * out
            tan /= np.linalg.norm(tan)
            bi = np.cross(out, tan)
            # a little uneven: worn tiles sit a degree or two off the cord's line
            wob = math.radians(4.0) * math.sin(1.7 * k + 2.3 * i)
            tan2 = tan * math.cos(wob) + bi * math.sin(wob)
            bi2 = np.cross(out, tan2)
            first = len(part.V)
            _box(part, p + out * (rc * 0.2 + 0.5 * thick), tan2, bi2, out, np.array([0.5 * tile, 0.5 * tile,
                                                                                    0.5 * thick]),
                 ATLAS[f"tile_{tone}"], TILE_SEG_INSET)
            q = float(np.clip((p - el) @ ax / fl, 0.0, 1.0))
            along += [q] * (len(part.V) - first)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part, np.array(along)


GIRDLE_PANELS = ("FL", "FR", "BL", "BR")


def girdle(fields: Fields, cp: dict, z_belt: float) -> tuple[Part, list]:
    """The short reed-fibre girdle (pell.md §4.2's fallback, taken on review: the bare lower body read as nudity). Four
    panels hung from the belt cord, split at the front, the back and both sides, so each one follows one thigh
    (M1-CHR-14: nothing tube-like below the hips): front-left, front-right, back-left, back-right. Each panel's rows
    run from the belt down `girdle_len_m`, on the hips' and thighs' surface `girdle_off_m` out, flaring to
    `girdle_flare_m` at the hem and hanging plumb where the body falls away (between the legs). Returns (the part,
    per vertex: (panel, row fraction))."""
    lm = fields.lm
    S = lm.S
    part = Part("Girdle")
    part._mat = "cloth"
    L = float(cp["girdle_len_m"])
    off = float(cp["girdle_off_m"])
    flare = float(cp["girdle_flare_m"])
    rows, cols = int(cp["girdle_rows"]), int(cp["girdle_cols"])
    slope = float(cp["girdle_hang_slope"])
    z0 = z_belt - float(cp["girdle_top_below_belt_m"])
    u0, v0, u1, v1 = ATLAS["mantle"]
    tags = []
    for name in GIRDLE_PANELS:
        a0, a1 = (float(x) for x in cp["girdle_front_deg" if name[0] == "F" else "girdle_back_deg"])
        sg = 1.0 if name[1] == "L" else -1.0
        th = np.radians(sg * np.linspace(a0, a1, cols))
        D = dir_theta(th)
        P = np.zeros((rows, cols, 3))
        prev = None
        for j in range(rows):
            t = j / (rows - 1)
            z = z0 - L * t
            O = np.stack([np.zeros(cols), np.full(cols, 0.01 * S), np.full(cols, z)], axis=-1)
            o = off + flare * t * t
            r = cast_last(lambda Q: fields.lower(Q) - o, O, D, 0.5 * S)  # noqa: B023
            if prev is not None:  # it hangs: it comes in toward the body no faster than `slope` of its drop
                r = np.maximum(r, prev - slope * (L / (rows - 1)))
            prev = r
            P[j] = O + D * r[:, None]
        rect = (u0 + (u1 - u0) * (0.5 if name[1] == "R" else 0.0), v0 + (v1 - v0) * (0.5 if name[0] == "B" else 0.0),
                u0 + (u1 - u0) * (1.0 if name[1] == "R" else 0.5), v0 + (v1 - v0) * (1.0 if name[0] == "B" else 0.5))
        n0 = len(part.V)
        _panel(part, P, rect, None, False, MANTLE_BACK * S, np.array([0.0, 0.01 * S, z0 - 0.5 * L]))
        tt = np.tile(np.repeat(np.linspace(0.0, 1.0, rows), cols), 2)
        tags += [(name, float(x)) for x in tt[:len(part.V) - n0]]
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part, tags


def ankle_cord(fields: Fields, cp: dict, motifs: dict) -> Part:
    """One turn of cord round the right shin, `ankle_cord_above_m` above the ankle bone, with three tiles."""
    lm = fields.lm
    S = lm.S
    part = Part("AnkleCord")
    part._mat = "cloth"
    an, kn = lm.side_pt("ankle", "R"), lm.side_pt("knee", "R")
    ax = (an - kn) / np.linalg.norm(an - kn)
    c = an - ax * float(cp["ankle_cord_above_m"])
    rc = 0.5 * float(cp["wrap_cord_m"])
    off = float(cp["tile_off_m"])
    r, e1, e2 = _surface_ring(fields.region("leg_R"), c, ax, 24, 0.2 * S)
    for _ in range(2):
        r = np.maximum(r, 0.5 * r + 0.25 * (np.roll(r, 1) + np.roll(r, -1)))
    ang = 2 * math.pi * np.arange(24) / 24
    D = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
    C = c + D * (r + off + rc)[:, None]
    tube(part, np.concatenate([C, C[:1]]), rc, 5, "cloth", ax, ATLAS["wrap_cord"], tags=TAG_CLOTH)
    tile = float(cp["tile_m"])
    thick = float(cp["tile_thick_m"])
    tones = motifs["tiles"]["ankle"]
    # the three tiles over the outside of the shin (his right: -X)
    k0 = int(np.argmin(D @ np.array([-1.0, -0.3, 0.0])))
    for i, tone in enumerate(tones):
        k = (k0 + i - 1) % 24
        p, out = C[k], D[k]
        tan = C[(k + 1) % 24] - C[k - 1]
        tan = tan - (tan @ out) * out
        tan /= np.linalg.norm(tan)
        _box(part, p + out * (rc * 0.2 + 0.5 * thick), tan, np.cross(out, tan), out,
             np.array([0.5 * tile, 0.5 * tile, 0.5 * thick]), ATLAS[f"tile_{tone}"], TILE_SEG_INSET)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part


# ---------------------------------------------------------------------------------------------
def build_costume(body, cp: dict) -> tuple[dict[str, Part], dict]:
    """Returns ({name: Part}, info). `Mantle`, `MantleCord`, `BeltCord`, `Pouch`, `LineCoil` and `AnkleCord` go into
    the Costume object; `WrapL` / `WrapR` into Wraps (build_pell)."""
    lm = body.lm
    fields = Fields(body)
    chart = TorsoChart(lm)
    motifs = load_motifs()
    out: dict[str, Part] = {}
    out["Mantle"] = mantle(fields, chart, cp)
    out["MantleCord"], cord_line = mantle_cord(fields, chart, cp, out["Mantle"])
    out["BeltCord"], ring, z_belt = belt_cord(fields, cp)
    out["Pouch"], pouch_info = pouch(fields, cp, ring, z_belt)
    out["LineCoil"], coil_info = line_coil(fields, cp, ring, z_belt)
    out["AnkleCord"] = ankle_cord(fields, cp, motifs)
    out["Girdle"], girdle_tags = girdle(fields, cp, z_belt)
    along = {}
    for sd in ("L", "R"):
        out[f"Wrap{sd}"], along[sd] = forearm_wrap(fields, cp, sd, motifs)
    info = {"chart": chart, "fields": fields, "cord_line": cord_line, "belt_ring": ring, "z_belt": z_belt,
            "pouch": pouch_info, "coil": coil_info, "wrap_along": along, "girdle": girdle_tags}
    return out, info


def _nearest_dist(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    out = np.empty(len(A))
    for a in range(0, len(A), 512):
        q = A[a:a + 512]
        out[a:a + 512] = np.sqrt(((q[:, None, :] - B[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
    return out


def coverage(body, cp: dict, V: np.ndarray, reg: np.ndarray, mantle_part: Part) -> np.ndarray:
    """True for torso vertices hidden under the mantle with a margin: within `mantle_off_m` + 3 cm of its sheet and at
    least `mantle_cut_in_m` from its edges; only in the falls, above the hips (never the neck, the shoulder cap or the
    arm: the mantle's arm band and its edges move off them)."""
    lm = body.lm
    S = lm.S
    G = mantle_part.grid_P
    edge = np.concatenate([G[0], G[-1], G[:, 0], G[:, -1]])
    sheet = G.reshape(-1, 3)
    m = float(cp["mantle_cut_in_m"])
    sh_z = float(lm.side_pt("shoulder", "R")[2])
    cand = (reg == "torso") & (V[:, 2] > float(lm.side_pt("hip", "R")[2]) + 0.05 * S) & (V[:, 2] < sh_z - 0.04 * S)
    cand &= V[:, 0] < 0.0
    out = np.zeros(len(V), dtype=bool)
    ids = np.nonzero(cand)[0]
    if len(ids):
        near = _nearest_dist(V[ids], sheet) < float(cp["mantle_off_m"]) + 0.03 * S
        far = _nearest_dist(V[ids], edge) > m
        out[ids] = near & far
    return out
