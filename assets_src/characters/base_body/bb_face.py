"""Head and face sculpt field (M1-CHR-02 head rebuild). Pure numpy, no bpy.

Three layers, all deterministic and driven by the sliders in bb_params.DEFAULTS:

1. **HeadLoft**: the head's base solid as a stack of horizontal cross-sections from the chin
   (z = 0) to the vertex (z = 1, in head heights h). Each section is a four-part superellipse:
   front depth, back depth, half-width, the depth of the widest point, and a front squareness.
   The tables are a face *profile* you can read: chin, mouth base, nose base, nasion, glabella,
   forehead, vertex. The jaw line, the under-chin and the cheek planes come out of the section
   tables, not out of blended ellipsoids, so they stay clean in 3/4 and profile.
2. **Heightfield terms** (`Face.disp`): forward displacement in face space (u = x / h,
   v = height above the chin / h), faded out toward the back of the head. Soft forms: orbits,
   brow, temples, cheekbones, the dental arch, nasolabial fold, lips (vermilion volume, white
   roll, cupid's bow, philtrum), mentolabial sulcus, chin pad.
3. **Primitive terms** (`Face.nose_spec`): signed-distance primitives blended after the
   heightfield for forms that undercut: the nose (dorsum, tip lobule, columella, alae), with the
   nostrils subtracted.

Sliders: `eye_tilt_deg`, `canthus_offset_m`, `jaw_width`, `cheekbone_height`, `cheekbone_width`,
`chin_size`, `nose_bridge_width`, `nose_tip_projection`, `lip_fullness`, `mouth_corner_lift`,
`brow_ridge`, plus `femininity` for the masculine/feminine differences. The face blendshapes
(assets_src/characters/asha/asha_face_shapes.py) read the same landmarks and EyeFrame.
"""
from __future__ import annotations

import math

import numpy as np

Arr = np.ndarray


def smoothstep(e0: float, e1: float, x: Arr) -> Arr:
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def gauss2(u: Arr, v: Arr, u0: float, v0: float, su: float, sv: float) -> Arr:
    return np.exp(-(((u - u0) / su) ** 2) - ((v - v0) / sv) ** 2)


def mirrored(u: Arr, v: Arr, u0: float, v0: float, su: float, sv: float) -> Arr:
    return gauss2(u, v, u0, v0, su, sv) + gauss2(u, v, -u0, v0, su, sv)


def pchip(xs: Arr, ys: Arr, x: Arr) -> Arr:
    """Monotone cubic (Fritsch-Carlson) interpolation; clamps outside [xs[0], xs[-1]]."""
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    x = np.clip(np.asarray(x, dtype=float), xs[0], xs[-1])
    hk = np.diff(xs)
    dk = np.diff(ys) / hk
    m = np.zeros_like(ys)
    for k in range(1, len(xs) - 1):
        if dk[k - 1] * dk[k] > 0:
            w1 = 2 * hk[k] + hk[k - 1]
            w2 = hk[k] + 2 * hk[k - 1]
            m[k] = (w1 + w2) / (w1 / dk[k - 1] + w2 / dk[k])
    m[0], m[-1] = dk[0], dk[-1]
    i = np.clip(np.searchsorted(xs, x) - 1, 0, len(xs) - 2)
    t = (x - xs[i]) / hk[i]
    t2, t3 = t * t, t * t * t
    return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * hk[i] * m[i] + (-2 * t3 + 3 * t2) * ys[i + 1]
            + (t3 - t2) * hk[i] * m[i + 1])


# ---------------------------------------------------------------------------------------------
# 1. Lofted head solid
# ---------------------------------------------------------------------------------------------
# Section tables in head heights h. z: height above the chin. front: forward depth of the base face
# at the midline (no nose, no lips) in front of the head centre. back: depth behind the centre.
# width: half-width. y_w: depth of the widest point (+ = behind the centre). p_f: front squareness
# (2 = elliptical, larger = a flatter facial plane).
LOFT_Z = [-0.08, 0.00, 0.06, 0.12, 0.20, 0.26, 0.32, 0.40, 0.48, 0.56, 0.64, 0.72, 0.80, 0.88, 0.94, 0.98, 1.00]
LOFT_FRONT = [0.320, 0.338, 0.362, 0.352, 0.366, 0.378, 0.382, 0.372, 0.360, 0.396, 0.403, 0.390, 0.355, 0.285, 0.195,
              0.105, 0.030]
LOFT_BACK = [0.00, 0.00, 0.02, 0.06, 0.12, 0.20, 0.28, 0.35, 0.39, 0.405, 0.41, 0.40, 0.372, 0.315, 0.235, 0.135, 0.05]
LOFT_WIDTH = [0.180, 0.186, 0.202, 0.222, 0.238, 0.242, 0.262, 0.286, 0.298, 0.300, 0.315, 0.326, 0.313, 0.262, 0.192,
              0.115, 0.030]
LOFT_YW = [0.00, 0.00, 0.00, 0.00, 0.01, 0.02, 0.03, 0.035, 0.035, 0.04, 0.05, 0.06, 0.06, 0.05, 0.045, 0.04, 0.04]
LOFT_PF = [2.15, 2.15, 2.05, 2.0, 2.0, 2.08, 2.22, 2.35, 2.42, 2.4, 2.3, 2.15, 2.05, 2.0, 2.0, 2.0, 2.0]
LOFT_PB = [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.05, 2.1, 2.1, 2.05, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
# The mandible's lower border: a plane through the chin bottom rising toward the jaw angle. It
# closes the loft underneath (degenerate bottom sections would under-estimate distances and web
# into the neck through the wide head/neck fillet).
JAW_CUT_FRONT = 0.31  # forward depth (h) where the plane meets the chin bottom (z = 0)
JAW_CUT_SLOPE = 0.32  # rise per unit of depth toward the back
JAW_CUT_K = 0.085  # rounding of the jaw line (h)


class HeadLoft:
    """Approximate signed distance to the lofted head (metres). Distances are (rho - 1) / |grad
    rho| of the superellipse section function, which is within a few percent near the surface."""

    def __init__(self, lm, femininity: float, jaw_width: float, chin_size: float) -> None:
        self.h = lm.h
        self.yc = float(lm.P("head_c")[1])
        self.z0 = float(lm.P("chin")[2])
        masc = 1.0 - femininity
        hw_scale = lm.head_w / (0.66 * lm.h)  # head_width_ratio relative to Asha's 0.66
        z = np.array(LOFT_Z)
        # masculine / jaw_width: a wider, squarer jaw below the cheekbones
        jaw = (1.0 + 0.10 * masc) * jaw_width
        jaw_mix = 1.0 - smoothstep(0.24, 0.42, z)
        self.width = np.array(LOFT_WIDTH) * hw_scale * (1.0 + (jaw - 1.0) * jaw_mix)
        cs = 1.0 + 0.35 * (chin_size - 1.0) + 0.04 * masc
        chin_mix = 1.0 - smoothstep(0.10, 0.22, z)
        self.front = np.array(LOFT_FRONT) * (1.0 + (cs - 1.0) * 0.12 * chin_mix)
        self.back = np.array(LOFT_BACK)
        self.yw = np.array(LOFT_YW)
        self.pf = np.array(LOFT_PF) - 0.12 * masc * jaw_mix
        self.pb = np.array(LOFT_PB)
        self.z = z

    def params(self, zn: Arr) -> tuple[Arr, Arr, Arr, Arr, Arr, Arr]:
        z = self.z
        return (pchip(z, self.front, zn), pchip(z, self.back, zn), pchip(z, self.width, zn), pchip(z, self.yw, zn),
                pchip(z, self.pf, zn), pchip(z, self.pb, zn))

    def rho(self, x: Arr, yn: Arr, zn: Arr) -> tuple[Arr, Arr, Arr]:
        """Section function rho (1 on the surface) and its x / y partials, in h units."""
        fr, bk, w, yw, pf, pb = self.params(zn)
        front = yn < yw
        b = np.where(front, yw + fr, bk - yw)
        b = np.maximum(b, 1e-4)
        # blend the exponent across the widest point: a jump there is a curvature crease
        p = pb + (pf - pb) * smoothstep(-0.06, 0.06, yw - yn)
        ax = np.abs(x) / np.maximum(w, 1e-4)
        by = np.abs(yn - yw) / b
        s = ax**p + by**p
        r = np.power(np.maximum(s, 1e-12), 1.0 / p)
        common = np.power(np.maximum(r, 1e-9), 1.0 - p)
        drx = common * np.power(ax, p - 1.0) / np.maximum(w, 1e-4) * np.sign(x)
        dry = common * np.power(by, p - 1.0) / b * np.sign(yn - yw)
        return r, drx, dry

    def sdf(self, P: Arr) -> Arr:
        h = self.h
        x = P[:, 0] / h
        yn = (P[:, 1] - self.yc) / h
        zr = (P[:, 2] - self.z0) / h
        zn = np.clip(zr, self.z[0], 1.0)
        r, drx, dry = self.rho(x, yn, zn)
        dz = 2e-3
        r_up, _, _ = self.rho(x, yn, np.clip(zn + dz, self.z[0], 1.0))
        r_dn, _, _ = self.rho(x, yn, np.clip(zn - dz, self.z[0], 1.0))
        drz = (r_up - r_dn) / (2 * dz)
        g = np.sqrt(drx * drx + dry * dry + drz * drz)
        d = (r - 1.0) / np.maximum(g, 1e-3)
        # beyond the end sections: add the vertical distance (the caps are already nearly closed)
        out = np.maximum(zr - 1.0, 0.0)
        d = np.where(out > 0, np.sqrt(np.maximum(d, 0.0) ** 2 + out * out), d)
        # jaw underside
        zcut = JAW_CUT_SLOPE * (yn + JAW_CUT_FRONT)
        dcut = (zcut - zr) / math.sqrt(1.0 + JAW_CUT_SLOPE**2)
        k = JAW_CUT_K
        hh = np.maximum(k - np.abs(d - dcut), 0.0) / k
        d = np.maximum(d, dcut) + hh * hh * k * 0.25
        return d * h


# ---------------------------------------------------------------------------------------------
# 2. The eye opening
# ---------------------------------------------------------------------------------------------
class EyeFrame:
    """Face-space almond of one eye opening (the lid margin), shared with the cage builder and the
    blendshapes.

    Local coordinates: a = along the fissure (+ toward the outer canthus), b = up, both metres in
    the frontal plane around the eye centre. `contour(t)` gives the margin for an angle t
    (0 = outer canthus, pi/2 = top, pi = inner canthus)."""

    def __init__(self, lm, side: str) -> None:
        p = lm.p
        self.side = side
        self.sgn = 1.0 if side == "L" else -1.0
        self.E = lm.side_pt("eye", side)
        self.R = lm.eye_r
        # projected half-width: the commissures sit just outside the globe's silhouette
        self.half_w = 0.47 * lm.fissure_w
        self.inner_extra = float(p["canthus_offset_m"]) + 0.0015 * lm.h / 0.222  # medial canthus, caruncle
        self.tilt = math.radians(float(p["eye_tilt_deg"]))
        self.up = 0.37 * self.half_w  # upper lid arc height at its peak (covers ~1 mm of iris)
        self.lo = 0.26 * self.half_w  # lower lid just over the iris: no scleral show

    def contour(self, t: Arr) -> tuple[Arr, Arr]:
        t = np.asarray(t, dtype=float)
        c, s = np.cos(t), np.sin(t)
        a = np.where(c >= 0, self.half_w * c, (self.half_w + self.inner_extra) * c)
        upper = s > 0
        b = np.where(upper, self.up, self.lo) * s
        # upper lid peak sits a little toward the inner third, lower lid low point lateral
        b = b * (1.0 + np.where(upper, -0.16, 0.12) * c)
        # almond: the inner corner is a sharper point than the outer
        b = b * (1.0 - 0.18 * np.clip(-c, 0, 1) ** 3)
        # canthal tilt: the outer corner is higher
        b = b + a * math.tan(self.tilt)
        return a, b

    def margin_point(self, t: Arr, lift: float = 0.0) -> Arr:
        """3D lid-margin point for contour angle t, resting on the globe (+ lift) where the globe is
        behind it and receding to the commissure depth at the corners."""
        a, b = self.contour(t)
        R = self.R + lift
        s = np.sqrt(a * a + b * b)
        sc = np.minimum(s, 0.985 * R)
        depth_ball = np.sqrt(np.maximum(R * R - sc * sc, 0.0))
        # beyond the globe silhouette: the outer commissure sits near the globe's equator, the
        # inner one a little in front of it (medial canthus is more anterior)
        k = smoothstep(0.80 * self.R, 1.06 * self.R, s)
        inner = (a < 0).astype(float)
        depth_corner = self.R * (0.10 + 0.22 * inner) + lift
        depth = depth_ball * (1 - k) + depth_corner * k
        x = self.E[0] + self.sgn * a
        z = self.E[2] + b
        y = self.E[1] - depth
        return np.stack([x, y, z], axis=-1)

    def lid_solid(self, P: Arr, thickness: float) -> Arr:
        """The lids' volume: an ellipsoid around the globe, R + thickness deep, wider along the
        fissure so the commissures lie on it."""
        q = P - self.E
        a = q[:, 0] * self.sgn
        rx = max(self.half_w + self.inner_extra, self.R) * 1.06 + thickness
        ry = self.R + thickness
        rz = self.R + thickness
        k0 = np.sqrt((a / rx) ** 2 + (q[:, 1] / ry) ** 2 + (q[:, 2] / rz) ** 2)
        return (k0 - 1.0) * ry

    def cutter(self, P: Arr) -> Arr:
        """Negative inside the almond aperture prism, in front of the globe and outside it."""
        q = P - self.E
        r, _t = self.field(P[:, 0], P[:, 2])
        ap = (r - 1.0) * self.up
        ball = np.linalg.norm(q, axis=1) - (self.R - 0.0003)
        return np.maximum(np.maximum(ap, -ball), q[:, 1] - 0.1 * self.R)

    def eye_skin(self, P: Arr, d_face: Arr, thickness: float, round_k: float, blend=(1.2, 3.0)) -> Arr:
        """Skin around the eye. Inside the fissure's neighbourhood the lid solid with the almond
        aperture cut through it (the cut walls are the margins, `thickness` deep); cross-faded into
        the face field by distance from the fissure, so the lids flow into brow and cheek without a
        tunnel or a bulge. A thin shell over the globe (with the same aperture) is unioned last so
        the eyeball can never poke through the skin."""
        cut = self.cutter(P)
        lid = self.lid_solid(P, thickness)
        hh = np.maximum(round_k - np.abs(lid + cut), 0.0) / round_k
        lid_cut = np.maximum(lid, -cut) + hh * hh * round_k * 0.25
        r, _t = self.field(P[:, 0], P[:, 2])
        a, _b = self.local(P[:, 0], P[:, 2])
        r = r * (1.0 + 0.35 * smoothstep(-0.2 * self.half_w, -1.3 * self.half_w, a))  # medially the face takes over before the bridge
        w = smoothstep(blend[0], blend[1], r)
        front = smoothstep(0.35 * self.R, -0.2 * self.R, P[:, 1] - self.E[1])
        w = 1.0 - (1.0 - w) * front
        d = (1.0 - w) * lid_cut + w * d_face
        guard = np.maximum(np.linalg.norm(P - self.E, axis=1) - (self.R + 0.0005), -cut)
        return np.minimum(d, guard)

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


# ---------------------------------------------------------------------------------------------
# 3. Feature terms
# ---------------------------------------------------------------------------------------------
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
        self.loft = HeadLoft(lm, self.f, float(p["jaw_width"]), float(p["chin_size"]))
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
        f = np.clip((self.yc - 0.02 * h - P[:, 1]) / (0.22 * h), 0.0, 1.0)
        return f * f * (3 - 2 * f)

    def disp(self, P: Arr) -> Arr:
        h = self.h
        p = self.p
        x, z = P[:, 0], P[:, 2]
        u = x / h
        v = (z - self.zc) / h
        ue, ve, vm = self.ue, self.ve, self.vm
        masc = self.masc
        d = np.zeros(len(P))
        au = np.abs(u)
        # ---- forehead, brow, temples (h units, scaled at the end) ----
        br = float(p["brow_ridge"]) * (0.003 + 0.018 * masc)
        d += br * gauss2(au, v, ue * 0.92, ve + 0.085, 0.11, 0.035)  # superciliary arch
        d += (0.003 + 0.012 * masc) * gauss2(u, v, 0.0, ve + 0.07, 0.05, 0.04)  # glabella
        d -= 0.010 * mirrored(u, v, 0.30, ve + 0.10, 0.05, 0.08)  # temples
        # ---- orbits: the eyeball union fills the centre; the hollow shapes the socket ----
        d -= 0.004 * mirrored(u, v, ue * 1.02, ve + 0.0, 0.06, 0.04)
        # bring the face up to the lid solid below and beside the eye, so lids flow into the cheek
        # and the orbit rim instead of standing proud as a ring
        d += 0.022 * mirrored(u, v, ue + 0.004, ve - 0.050, 0.065, 0.032)
        d += 0.014 * mirrored(u, v, ue + 0.072, ve - 0.006, 0.030, 0.045)
        # nasal sidewall falling into the medial canthus (the base face is flat across the eyes)
        d -= 0.016 * mirrored(u, v, ue - 0.072, ve - 0.004, 0.048, 0.05)
        d -= 0.010 * mirrored(u, v, ue - 0.045, ve - 0.07, 0.04, 0.05)
        d += 0.004 * mirrored(u, v, ue + 0.065, ve + 0.05, 0.05, 0.025)  # lateral brow
        # ---- cheekbones (malar eminence) and the zygomatic body ----
        cw = float(p["cheekbone_width"])
        ch = float(p["cheekbone_height"])
        d += 0.020 * mirrored(u, v, 0.205 * cw, ve - 0.105 + ch, 0.075, 0.06)
        d += 0.010 * mirrored(u, v, 0.115, ve - 0.105 + ch, 0.05, 0.035)  # infraorbital fill
        d -= 0.008 * masc * mirrored(u, v, 0.235, vm + 0.01, 0.05, 0.06)  # buccal hollow (masculine)
        d += 0.022 * self.f * mirrored(u, v, 0.175, vm + 0.075, 0.08, 0.08)  # young malar / cheek fat
        d += 0.010 * self.f * mirrored(u, v, 0.20, vm - 0.01, 0.06, 0.06)  # lower cheek, rounding the jaw
        # ---- the dental arch: the mouth sits on a cylinder, not a plane ----
        d += 0.012 * gauss2(u, v, 0.0, vm + 0.02, 0.13, 0.09)
        d += 0.006 * mirrored(u, v, 0.15, vm + 0.04, 0.05, 0.06)  # cheek fat over the fold
        d = d * h
        d += self._eye_terms(P)
        d += self._nasolabial(u, v)
        d += self._lips(x, z)
        d += self._chin(u, v)
        d += self._dorsum(u, v)
        return d * self.front_fade(P)

    def _dorsum(self, u: Arr, v: Arr) -> Arr:
        """The bony and cartilaginous bridge as a heightfield ridge (it never undercuts): from the
        nasion to the supratip, where the tip primitives take over (metres)."""
        h = self.h
        bw = float(self.p["nose_bridge_width"])
        v_n = self.ve + 0.010
        v_st = self.vt + 0.028
        t = np.clip((v_n - v) / (v_n - v_st), 0.0, 1.0)  # 0 at the nasion .. 1 at the supratip
        inside = smoothstep(-0.10, 0.02, (v_n - v) / (v_n - v_st)) * smoothstep(1.25, 0.95, t + (v_st - v) * 0.0)
        height = (0.004 + 0.072 * t**1.25) * h  # ridge height above the base face
        half = (0.044 + 0.016 * t) * h * bw  # half-width at the base (a soft, broad root)
        xr = np.abs(u * h) / half
        prof = np.clip(1.0 - xr * xr, 0.0, 1.0) ** 2.4
        below = smoothstep(v_st - 0.005, v_st - 0.040, v)  # hand over to the tip lobule
        return height * prof * inside * (1.0 - below)

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
            crease = np.exp(-(((r - 1.55) / 0.13) ** 2)) * upper * (1.0 - 0.7 * inner)
            out -= 0.0006 * s * crease
            fold = np.exp(-(((r - 1.9) / 0.3) ** 2)) * upper  # the fold of skin above the crease
            out += 0.0006 * s * fold
            pretarsal = np.exp(-(((r - 1.3) / 0.18) ** 2)) * lower  # lower-lid orbicularis roll
            out += 0.0006 * s * pretarsal
            trough = np.exp(-(((r - 2.0) / 0.25) ** 2)) * lower * (0.4 + 0.6 * inner)
            out -= 0.0006 * s * trough
        return out

    def _nasolabial(self, u: Arr, v: Arr) -> Arr:
        """A soft fold from the alar crease down and out past the mouth corner (metres). Young
        face: a shallow groove with the cheek fat rounding over it, never a line."""
        s = self.s
        a = np.array([0.085, self.vs + 0.03])  # top (beside the ala), in (u, v)
        b = np.array([0.165, self.vm - 0.035])  # bottom (lateral to the mouth corner)
        out = np.zeros(len(u))
        ab = b - a
        L = float(np.linalg.norm(ab))
        for sg in (1.0, -1.0):
            q = np.stack([u * sg - a[0], v - a[1]], axis=1)
            t = np.clip(q @ ab / (ab @ ab), 0.0, 1.0)
            side = (q[:, 0] * ab[1] - q[:, 1] * ab[0]) / L  # + lateral
            along = np.sin(np.pi * t) ** 0.8
            out += -0.0006 * s * np.exp(-((side / 0.010) ** 2)) * along
            out += 0.0012 * s * np.exp(-(((side - 0.022) / 0.018) ** 2)) * along
        return out

    def _lips(self, x: Arr, z: Arr) -> Arr:
        """Vermilion volume, white roll, cupid's bow, philtrum, mouth corners (metres).

        tu / tl: height above / below the contact line in units of each lip's vermilion height
        (1 = the vermilion border). Each vermilion is a forward bulge peaking mid-lip; the
        upper-lip skin ramps back from the border to the subnasale; the lower lip's skin hands
        over to the mentolabial sulcus (`_chin`)."""
        s = self.s
        p = self.p
        fl = float(p["lip_fullness"])
        W = self.mouth_half
        zm = self.lm.P("mouth")[2]
        xr = np.abs(x) / W
        lift = float(p["mouth_corner_lift"]) * xr * xr
        dz = z - zm - lift
        taper = smoothstep(1.04, 0.35, xr)  # vermilion volume dies out at the corners
        out = np.zeros(len(x))
        # upper lip: border height above the contact line, with the cupid's bow (two peaks, a dip)
        bow = 0.0012 * s * np.exp(-(((xr - 0.21) / 0.11) ** 2)) - 0.0006 * s * np.exp(-((xr / 0.08) ** 2))
        ub = (0.0068 * s * fl) * (1.0 - 0.70 * xr * xr) + bow
        tu = dz / np.maximum(ub, 1e-4)
        upper = tu > 0
        verm_u = np.exp(-(((tu - 0.5) / 0.42) ** 2))
        skin_u = smoothstep(2.7, 0.7, tu) * smoothstep(1.25, 0.3, xr)
        out += np.where(upper, (0.0040 * s * fl * verm_u) * taper + 0.0017 * s * skin_u, 0.0)
        out += 0.00035 * s * np.exp(-(((tu - 1.0) / 0.10) ** 2)) * taper  # white roll at the border
        # philtrum: columns from the bow peaks up to the nostril sill, a groove between
        zs = self.lm.P("subnasale")[2]
        tp = np.clip((z - zm - ub) / np.maximum(zs - zm - ub, 1e-4), 0.0, 1.0)
        phil_band = smoothstep(-0.05, 0.15, tp) * smoothstep(1.05, 0.75, tp) * (dz > 0)
        col_x = W * (0.21 - 0.07 * tp)
        out += 0.0005 * s * phil_band * np.exp(-(((np.abs(x) - col_x) / (0.0024 * s)) ** 2))
        out -= 0.0004 * s * phil_band * np.exp(-((x / (0.0030 * s)) ** 2))
        # lower lip: fuller (asha.md §6.1) and rounder
        lb = (0.0090 * s * fl) * (1.0 - 0.62 * xr * xr)
        tl = -dz / np.maximum(lb, 1e-4)
        verm_l = np.exp(-(((tl - 0.48) / 0.46) ** 2))
        out += np.where(~upper, 0.0050 * s * fl * verm_l * taper, 0.0)
        # contact line crevice and recessed corners (modiolus)
        out -= 0.0009 * s * np.exp(-((dz / (0.0007 * s)) ** 2)) * smoothstep(1.1, 0.8, xr)
        corner = np.exp(-(((xr - 1.0) / 0.12) ** 2) - ((dz / (0.0030 * s)) ** 2))
        out -= 0.0012 * s * corner
        out += 0.0008 * s * np.exp(-(((xr - 1.22) / 0.16) ** 2) - ((dz / (0.006 * s)) ** 2))  # modiolus
        return out

    def _chin(self, u: Arr, v: Arr) -> Arr:
        h = self.h
        cs = float(self.p["chin_size"])
        vm = self.vm
        d = np.zeros(len(u))
        d -= 0.008 * gauss2(u, v, 0.0, vm - 0.075, 0.08, 0.02)  # mentolabial sulcus
        d += 0.010 * cs * gauss2(u, v, 0.0, 0.075, 0.07, 0.045)  # chin pad (mentalis)
        return d * h

    # ------------------------------------------------------------------------------------------
    # Primitives (applied after the heightfield)
    # ------------------------------------------------------------------------------------------
    def nose_spec(self, surface_y) -> list[tuple[str, dict]]:
        """Tip, columella, alae and nostrils as primitives, anchored to the underlying face
        surface (the dorsum is a heightfield ridge, `_dorsum`). surface_y(x, z) -> y of the head
        region (loft + heightfield) in front of (x, z)."""
        s = self.s
        p = self.p
        tp = float(p["nose_tip_projection"])
        h = self.h
        z = lambda vv: self.zc + vv * h  # noqa: E731
        v_tip = self.vt
        v_sub = self.vs
        y_sub = surface_y(0.0, z(v_sub))
        y_tip = self.lm.P("nose_tip")[1] + (1.0 - tp) * 0.006 * s  # pronasale (front of the tip)
        spec: list[tuple[str, dict]] = []
        # tip lobule: soft and rounded (asha.md §6.1), two domal halves merged
        tip = np.array([0.0, y_tip + 0.0054 * s, z(v_tip)])
        spec.append(("ell", dict(c=tip, r=np.array([0.0060, 0.0054, 0.0056]) * s, k=0.0050 * s)))
        for sg in (1.0, -1.0):
            spec.append(("ell", dict(c=tip + np.array([sg * 0.0030 * s, 0.0006 * s, -0.0006 * s]),
                                     r=np.array([0.0040, 0.0048, 0.0046]) * s, k=0.0028 * s)))
        # columella: from under the tip back to the subnasale, rising slightly (nasolabial ~100 deg)
        col_a = tip + np.array([0.0, 0.0020 * s, -0.0050 * s])
        col_b = np.array([0.0, y_sub + 0.0012 * s, z(v_sub + 0.003)])
        spec.append(("cone", dict(a=col_a, b=col_b, r1=0.0030 * s, r2=0.0032 * s, k=0.0022 * s)))
        # alae: the wings, with a crisp crease into the cheek (small k)
        for sg in (1.0, -1.0):
            zal = z(v_sub + 0.016)
            yb = surface_y(sg * 0.0135 * s, zal)
            al = np.array([sg * 0.0104 * s, yb - 0.0040 * s, zal])
            spec.append(("ell", dict(c=al, r=np.array([0.0042, 0.0085, 0.0055]) * s, k=0.0024 * s,
                                     rot_z=sg * 30.0)))
            # lateral crus: fills between the ala and the tip lobule
            spec.append(("cone", dict(a=al + np.array([-sg * 0.002 * s, -0.004 * s, 0.002 * s]),
                                      b=tip + np.array([sg * 0.0045 * s, 0.0025 * s, 0.0005 * s]),
                                      r1=0.0042 * s, r2=0.0044 * s, k=0.0065 * s)))
        # nostrils: pockets under the tip, between the columella and each ala, opening downward
        for sg in (1.0, -1.0):
            c = np.array([sg * 0.0054 * s, (y_tip + y_sub) * 0.5 + 0.0016 * s, z(v_sub + 0.0064)])
            spec.append(("hole", dict(c=c, r=np.array([0.0021, 0.0044, 0.0018]) * s, k=0.0012 * s,
                                      rot_z=-sg * 18.0, rot_x=-8.0)))
        return spec
