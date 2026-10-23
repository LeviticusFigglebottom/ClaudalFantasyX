"""Face sculpt field (M1-CHR-02 head rebuild). Pure numpy, no bpy.

The head region of bb_anatomy is a smooth cranium/lower-face "egg" plus jaw, chin and zygoma
primitives. This module adds the sculpt on top of it, in two kinds of named terms:

* **Heightfield terms** (`Face.disp`): forward displacement in face space, u = x / h and
  v = (z - z_chin) / h (h = head height), faded out toward the back of the head. Soft forms live
  here: orbits, brow ridge, lid crease and lid folds, tear trough, cheekbones, nasolabial fold,
  the lips (vermilion volume, white roll, cupid's bow, philtrum), the mentolabial sulcus, chin.
* **Primitive terms** (`Face.prims`): signed-distance primitives blended *after* the heightfield,
  for forms a heightfield can't hold because they undercut: the nose (dorsum, tip lobule,
  columella, alae) with the nostrils subtracted.

Every term reads the face sliders in bb_params.DEFAULTS (`eye_tilt_deg`, `canthus_offset_m`,
`jaw_width`, `cheekbone_height`, `cheekbone_width`, `chin_size`, `nose_bridge_width`,
`nose_tip_projection`, `lip_fullness`, `mouth_corner_lift`, `brow_ridge`). The face blendshapes
(assets_src/characters/asha/face_shapes.py) are written against the same landmarks, so a slider
change re-flows the sculpt and the shapes together. Deterministic, no randomness.
"""
from __future__ import annotations

import math

import numpy as np

Arr = np.ndarray


def smoothstep(e0: float, e1: float, x: Arr) -> Arr:
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def bump(x: Arr) -> Arr:
    """Smooth compact bump: (1 - x^2)^2 on |x| < 1, 0 outside."""
    t = np.clip(1.0 - x * x, 0.0, 1.0)
    return t * t


def gauss2(u: Arr, v: Arr, u0: float, v0: float, su: float, sv: float) -> Arr:
    return np.exp(-(((u - u0) / su) ** 2) - ((v - v0) / sv) ** 2)


def mirrored(u: Arr, v: Arr, u0: float, v0: float, su: float, sv: float) -> Arr:
    return gauss2(u, v, u0, v0, su, sv) + gauss2(u, v, -u0, v0, su, sv)


class EyeFrame:
    """Face-space almond of one eye opening (the lid margin), shared with the cage builder.

    Local coordinates: a = along the fissure (+ toward the outer canthus), b = up, both metres in
    the frontal plane around the eye centre. `contour(t)` gives the margin for an angle t
    (0 = outer canthus, pi/2 = top, pi = inner canthus)."""

    def __init__(self, lm, side: str) -> None:
        p = lm.p
        self.side = side
        self.sgn = 1.0 if side == "L" else -1.0
        self.E = lm.side_pt("eye", side)
        self.half_w = lm.fissure_w / 2
        self.inner_extra = float(p["canthus_offset_m"])  # inner canthus moved toward the midline
        self.tilt = math.radians(float(p["eye_tilt_deg"]))
        self.up = 0.33 * self.half_w  # upper lid arc height at its peak
        self.lo = 0.27 * self.half_w

    def contour(self, t: Arr) -> tuple[Arr, Arr]:
        t = np.asarray(t, dtype=float)
        c, s = np.cos(t), np.sin(t)
        a = np.where(c >= 0, self.half_w * c, (self.half_w + self.inner_extra) * c)
        upper = s > 0
        b = np.where(upper, self.up, self.lo) * s
        # upper lid peak sits a little toward the inner third, lower lid low point lateral
        b = b * (1.0 + np.where(upper, -0.14, 0.12) * c)
        # canthal tilt: the outer corner is higher
        b = b + a * math.tan(self.tilt)
        return a, b

    def to_world_xz(self, a: Arr, b: Arr) -> tuple[Arr, Arr]:
        return self.E[0] + self.sgn * a, self.E[2] + b

    def local(self, x: Arr, z: Arr) -> tuple[Arr, Arr]:
        return (x - self.E[0]) * self.sgn, z - self.E[2]

    def field(self, x: Arr, z: Arr) -> tuple[Arr, Arr]:
        """(r, t): r = 1 on the margin, < 1 inside; t = angle as in `contour`."""
        a, b = self.local(x, z)
        b0 = b - a * math.tan(self.tilt)
        hw = np.where(a >= 0, self.half_w, self.half_w + self.inner_extra)
        hh = np.where(b0 >= 0, self.up, self.lo)
        t = np.arctan2(b0 / hh, a / hw)
        r = np.sqrt((a / hw) ** 2 + (b0 / hh) ** 2)
        return r, t


class Face:
    def __init__(self, lm) -> None:
        self.lm = lm
        p = lm.p
        self.p = p
        h = lm.h
        self.h = h
        self.s = h / 0.222  # absolute (mm) terms scale with the head
        self.zc = lm.P("chin")[2]
        self.yc = lm.P("head_c")[1]
        self.f = float(p["femininity"])
        self.masc = 1.0 - self.f
        self.eyes = {sd: EyeFrame(lm, sd) for sd in ("L", "R")}
        self.ve = (lm.P("eye")[2] - self.zc) / h
        self.ue = lm.P("eye")[0] / h
        self.vm = (lm.P("mouth")[2] - self.zc) / h
        self.vs = (lm.P("subnasale")[2] - self.zc) / h
        self.vt = (lm.P("nose_tip")[2] - self.zc) / h
        self.mouth_half = lm.mouth_w / 2

    # ------------------------------------------------------------------------------------------
    # Heightfield (forward displacement, metres)
    # ------------------------------------------------------------------------------------------
    def front_fade(self, P: Arr) -> Arr:
        h = self.h
        f = np.clip((self.yc + 0.02 * h - P[:, 1]) / (0.30 * h), 0.0, 1.0)
        return f * f * (3 - 2 * f)

    def disp(self, P: Arr) -> Arr:
        h, s = self.h, self.s
        p = self.p
        x, z = P[:, 0], P[:, 2]
        u = x / h
        v = (z - self.zc) / h
        ue, ve, vm = self.ue, self.ve, self.vm
        masc = self.masc
        d = np.zeros(len(P))
        # ---- forehead, brow, temples (h units, scaled at the end) ----
        br = float(p["brow_ridge"]) * (0.016 + 0.014 * masc)
        d += br * gauss2(np.abs(u), v, ue * 0.95, ve + 0.10, 0.14, 0.04)
        d += (0.012 + 0.008 * masc) * gauss2(u, v, 0.0, ve + 0.075, 0.06, 0.045)  # glabella
        d += 0.010 * gauss2(u, v, 0.0, ve + 0.24, 0.20, 0.12)  # frontal eminence
        d -= 0.010 * mirrored(u, v, 0.33, ve + 0.10, 0.06, 0.09)  # temples
        # ---- orbits: the eyeball union fills the centre; the hollow shapes the socket rim ----
        d -= 0.030 * mirrored(u, v, ue, ve + 0.004, 0.085, 0.058)
        d += 0.006 * mirrored(u, v, ue + 0.05, ve + 0.055, 0.07, 0.03)  # lateral brow fat pad
        # ---- cheekbones (malar eminence) and the zygomatic body ----
        cw = float(p["cheekbone_width"])
        ch = float(p["cheekbone_height"])
        d += 0.030 * mirrored(u, v, 0.215 * cw, ve - 0.085 + ch, 0.085, 0.065)
        d += 0.012 * mirrored(u, v, 0.12, ve - 0.115 + ch, 0.06, 0.04)  # infraorbital fill
        d -= (0.004 + 0.006 * masc) * mirrored(u, v, 0.25, vm + 0.0, 0.06, 0.06)  # buccal hollow
        # ---- maxilla and the dental arch: the mouth sits on a cylinder, not a plane ----
        d += 0.022 * gauss2(u, v, 0.0, vm + 0.03, 0.17, 0.12)
        d += 0.010 * mirrored(u, v, 0.11, vm + 0.12, 0.07, 0.07)  # maxilla beside the nose
        d += 0.010 * mirrored(u, v, 0.17, vm + 0.04, 0.06, 0.07)  # cheek fat over the fold
        d -= 0.004 * gauss2(u, v, 0.0, ve + 0.03, 0.05, 0.03)  # nasion (the bridge prim fills it)
        d = d * h
        d += self._eye_terms(P)
        d += self._nasolabial(u, v)
        d += self._lips(x, z)
        d += self._chin(u, v)
        return d * self.front_fade(P)

    def _eye_terms(self, P: Arr) -> Arr:
        """Lid crease, upper-lid fold, pretarsal lower lid and the tear trough (metres)."""
        s = self.s
        out = np.zeros(len(P))
        for e in self.eyes.values():
            r, t = e.field(P[:, 0], P[:, 2])
            upper = smoothstep(-0.25, 0.25, np.sin(t))
            lower = 1.0 - upper
            inner = smoothstep(0.2, -0.75, np.cos(t))  # 1 at the inner third
            # Asha: a low single crease, partly hidden at the inner third (asha.md §6.1)
            crease = np.exp(-(((r - 1.42) / 0.12) ** 2)) * upper * (1.0 - 0.75 * inner)
            out -= 0.0011 * s * crease
            fold = np.exp(-(((r - 1.75) / 0.25) ** 2)) * upper  # the fold of skin above the crease
            out += 0.0010 * s * fold
            pretarsal = np.exp(-(((r - 1.22) / 0.15) ** 2)) * lower  # lower-lid orbicularis roll
            out += 0.0006 * s * pretarsal
            trough = np.exp(-(((r - 1.95) / 0.22) ** 2)) * lower * (0.5 + 0.5 * inner)
            out -= 0.0008 * s * trough
            # inner canthus: a small pit and the caruncle shadow (skin recedes toward the nose)
            cant = np.exp(-(((r - 1.05) / 0.12) ** 2)) * smoothstep(-0.7, -0.98, np.cos(t))
            out -= 0.0006 * s * cant
        return out

    def _nasolabial(self, u: Arr, v: Arr) -> Arr:
        """A soft fold from the alar crease down and out past the mouth corner (metres)."""
        h, s = self.h, self.s
        a = np.array([0.095, self.vs + 0.035])  # top (beside the ala), in (u, v)
        b = np.array([0.185, self.vm - 0.03])  # bottom (lateral to the mouth corner)
        out = np.zeros(len(u))
        for sg in (1.0, -1.0):
            q = np.stack([u * sg - a[0], v - a[1]], axis=1)
            ab = b - a
            t = np.clip(q @ ab / (ab @ ab), 0.0, 1.0)
            dist = np.linalg.norm(q - t[:, None] * ab[None, :], axis=1)
            w = np.sin(np.pi * np.clip(t, 0, 1)) ** 0.6
            # the groove itself, plus the cheek fat bulging just lateral of it
            side = (q[:, 0] * ab[1] - q[:, 1] * ab[0]) / np.linalg.norm(ab)  # + lateral
            out += -0.0012 * s * np.exp(-((dist / (0.012)) ** 2)) * w
            out += 0.0016 * s * np.exp(-(((side + 0.022) / 0.02) ** 2)) * (dist < 0.06) * w * (side < 0.0)
        _ = h
        return out

    def _lips(self, x: Arr, z: Arr) -> Arr:
        """Vermilion volume, white roll, cupid's bow, philtrum, mouth corners (metres)."""
        s = self.s
        p = self.p
        fl = float(p["lip_fullness"])
        W = self.mouth_half
        zm = self.lm.P("mouth")[2]
        xr = np.abs(x) / W
        lift = float(p["mouth_corner_lift"]) * xr * xr
        dz = z - zm - lift
        taper = np.sqrt(np.clip(1.0 - xr**2, 0.0, 1.0))
        taper_s = smoothstep(1.08, 0.55, xr)
        out = np.zeros(len(x))
        # upper lip: border height above the contact line, with the cupid's bow
        bow = 0.0009 * s * np.exp(-(((xr - 0.27) / 0.13) ** 2)) - 0.0004 * s * np.exp(-((xr / 0.1) ** 2))
        ub = (0.0058 * s * fl) * (1.0 - 0.7 * xr * xr) + bow
        tu = dz / np.maximum(ub, 1e-4)
        upper_v = np.where((tu > 0) & (tu < 1.35), np.sin(np.clip(tu, 0, 1) * math.pi * 0.62) ** 0.8, 0.0)
        upper_v = np.where(tu > 1.0, np.sin(math.pi * 0.62) ** 0.8 * smoothstep(1.35, 1.0, tu), upper_v)
        out += 0.0034 * s * fl * upper_v * taper_s
        out += 0.0005 * s * np.exp(-(((tu - 1.0) / 0.10) ** 2)) * taper_s  # white roll
        # philtrum: columns from the bow peaks up to the nostril sill, a groove between
        zs = self.lm.P("subnasale")[2]
        tp = np.clip((z - zm - ub) / np.maximum(zs - zm - ub, 1e-4), 0.0, 1.0)
        phil_band = smoothstep(-0.05, 0.1, tp) * smoothstep(1.05, 0.8, tp)
        col_x = W * (0.25 - 0.08 * tp)
        out += 0.0007 * s * phil_band * (np.exp(-(((np.abs(x) - col_x) / (0.0022 * s)) ** 2)))
        out -= 0.0005 * s * phil_band * np.exp(-((x / (0.0028 * s)) ** 2))
        # the skin of the upper lip slopes back toward the subnasale
        out += 0.0012 * s * phil_band * (1.0 - tp) * smoothstep(1.2, 0.3, xr)
        # lower lip: fuller (asha.md §6.1), its border lower and its bulge rounder
        lb = (0.0080 * s * fl) * (1.0 - 0.6 * xr * xr)
        tl = -dz / np.maximum(lb, 1e-4)
        lower_v = np.where((tl > 0) & (tl < 1.4), np.sin(np.clip(tl / 1.25, 0, 1) * math.pi) ** 0.7, 0.0)
        out += 0.0042 * s * fl * lower_v * taper_s
        # contact line crevice and recessed corners (modiolus)
        out -= 0.0012 * s * np.exp(-((dz / (0.0009 * s)) ** 2)) * taper
        corner = np.exp(-(((xr - 1.0) / 0.16) ** 2) - ((dz / (0.004 * s)) ** 2))
        out -= 0.0020 * s * corner
        out += 0.0010 * s * np.exp(-(((xr - 1.25) / 0.2) ** 2) - ((dz / (0.007 * s)) ** 2))  # modiolus
        return out

    def _chin(self, u: Arr, v: Arr) -> Arr:  # noqa: D401
        h = self.h
        cs = float(self.p["chin_size"])
        vm = self.vm
        d = np.zeros(len(u))
        d -= 0.012 * gauss2(u, v, 0.0, vm - 0.085, 0.09, 0.022)  # mentolabial sulcus
        d += 0.020 * cs * gauss2(u, v, 0.0, 0.075, 0.075, 0.05)  # chin pad (mentalis)
        d += 0.006 * cs * gauss2(u, v, 0.0, 0.025, 0.05, 0.03)  # chin point, rounded
        return d * h

    # ------------------------------------------------------------------------------------------
    # Primitives (applied after the heightfield)
    # ------------------------------------------------------------------------------------------
    def nose_spec(self, surface_y) -> list[tuple[str, dict]]:
        """Nose primitives, anchored to the underlying face surface. surface_y(x, z) -> y of the
        head region (egg + heightfield) in front of (x, z)."""
        lm, s = self.lm, self.s
        p = self.p
        bw = float(p["nose_bridge_width"])
        tp = float(p["nose_tip_projection"])
        h = self.h
        z = lambda vv: self.zc + vv * h  # noqa: E731
        v_nasion = self.ve + 0.035
        v_tip = self.vt
        v_sub = self.vs
        y_n = surface_y(0.0, z(v_nasion)) + 0.0006 * s
        y_sub = surface_y(0.0, z(v_sub))
        y_tip = y_sub - 0.0185 * s * tp
        spec: list[tuple[str, dict]] = []
        # dorsum: nasion -> rhinion -> supratip, a narrow ridge
        rh = np.array([0.0, (y_n * 0.55 + y_tip * 0.45) - 0.0012 * s, z(v_nasion - 0.105)])
        st = np.array([0.0, y_tip + 0.0042 * s, z(v_tip + 0.032)])
        nas = np.array([0.0, y_n + 0.0052 * s, z(v_nasion)])
        spec.append(("cone", dict(a=nas, b=rh, r1=0.0060 * s * bw, r2=0.0050 * s * bw, k=0.0060 * s)))
        spec.append(("cone", dict(a=rh, b=st, r1=0.0050 * s * bw, r2=0.0055 * s * bw, k=0.0035 * s)))
        # tip lobule: two domes merged, slightly wider than tall
        tip = np.array([0.0, y_tip + 0.0058 * s, z(v_tip)])
        spec.append(("ell", dict(c=tip, r=np.array([0.0078, 0.0062, 0.0062]) * s, k=0.0030 * s)))
        for sg in (1.0, -1.0):
            spec.append(("ell", dict(c=tip + np.array([sg * 0.0034 * s, -0.0006 * s, -0.0004 * s]),
                                     r=np.array([0.0042, 0.0052, 0.0050]) * s, k=0.0020 * s)))
        # columella down to the subnasale
        col_a = tip + np.array([0.0, 0.0030 * s, -0.0042 * s])
        col_b = np.array([0.0, y_sub + 0.0004 * s, z(v_sub + 0.004)])
        spec.append(("cone", dict(a=col_a, b=col_b, r1=0.0030 * s, r2=0.0032 * s, k=0.0022 * s)))
        # alae: the wings flare beside the tip, with a crisp crease into the cheek
        for sg in (1.0, -1.0):
            yb = surface_y(sg * 0.0125 * s, z(v_sub + 0.016))
            al = np.array([sg * 0.0118 * s, yb - 0.0034 * s, z(v_sub + 0.016)])
            spec.append(("ell", dict(c=al, r=np.array([0.0058, 0.0080, 0.0058]) * s, k=0.0018 * s,
                                     rot_z=sg * 22.0)))
            # nose sidewall between the dorsum and the ala
            spec.append(("cone", dict(a=rh + np.array([sg * 0.0025 * s, 0.002 * s, 0.0]), b=al,
                                      r1=0.0040 * s, r2=0.0042 * s, k=0.0050 * s)))
        # nostrils: pockets under the tip, long axis forward-medial, opening downward
        for sg in (1.0, -1.0):
            c = np.array([sg * 0.0060 * s, y_tip + 0.0105 * s, z(v_sub + 0.0045)])
            spec.append(("hole", dict(c=c, r=np.array([0.0026, 0.0052, 0.0022]) * s, k=0.0012 * s,
                                      rot_z=-sg * 18.0, rot_x=-14.0)))
        _ = lm
        return spec
