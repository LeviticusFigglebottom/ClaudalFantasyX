"""The Kirru head warp (pell.md §9, M3-CHR-506). No bpy.

Pell keeps the MakeHuman donor's head topology (ADR 0021) and the whole face pipeline by adding one step between the
face sculpt and the face shapes: `kirru_warp`, a polyharmonic RBF warp (bb_donor.RBF, the kind the donor fit uses)
from a set of donor face landmarks onto a Kirru landmark set built from pell_params.json's `_kirru` block:

* the nose tip, the upper lip and the mouth pushed forward to the muzzle (`muzzle_m`, 5.5 cm), the bridge filled in
  between the brow and the nose pad (a shallow stop, not a human nose), the nose pad broadened to `nose_pad_width_m`;
* the whisker pads filled (pushed out and forward beside the pad, `whisker_pad`);
* the mouth line drawn back toward the cheek (the corners come forward less than the centre) and the chin reduced;
* the cranium lengthened (`cranium_length`) and rounded behind;
* the ears scaled to `ear_scale` about their own centre and moved up and back (`ear_offset_m`, in the stage's frame:
  x left, y up, z forward), with the old notch (`ear_notch`) bitten out of the left ear's rim.

The eyes, the brow and the forehead are anchored (zero displacement), so the eye frames, lids and lashes keep their
fit; the displacement fades to nothing over SEAM_FADE at the head/neck seam, so the Head stays welded to the Body. The
warp is a function of position (plus the donor's ear weights), so the same call carries the teeth and tongue built
on the donor face, and the donor's expression units (`warp_units`: each unit's delta is taken through the warp).
After it, `reread_landmarks` reads the face points back off the warped skin (as bb_donor's fit reads them off the
placed donor), so the eyes, teeth, lashes and the 40 shapes are built on the Kirru face under the same names.

Deterministic: no random terms; numpy only.
"""
from __future__ import annotations

import numpy as np

import bb_donor
import mpfb_data as md

SEAM_FADE = 0.035  # m (at s = 1): the warp fades in over this distance from the head/neck seam
FRONT_BAND = 0.004  # m: a midline sample takes the front-most skin vertex within this of its x
# The Kirru midline profile: (height as a fraction from the chin (0) to the brow (1), forward displacement as a
# fraction of the muzzle, lift as a fraction of the muzzle). The pad (the nose tip) comes forward a little less than
# the upper lip below it, so the muzzle's front is a flat pad and not a human nose on a block.
PROFILE = ((-0.25, 0.25, 0.0), (0.0, 0.42, 0.16), (0.15, 0.80, 0.06), (0.31, 1.0, 0.0), (0.42, 1.0, 0.0),
           (0.516, 0.60, -0.03), (0.62, 0.62, 0.0), (0.72, 0.52, 0.0), (0.83, 0.32, 0.0), (0.95, 0.08, 0.0),
           (1.05, 0.0, 0.0))
# Lateral columns (x as a fraction of the mouth's half-width, the share of the midline's forward push, the whisker
# pad's outward push as a fraction of the muzzle) for the lower face: the muzzle's sides fall away under the eyes
COLUMNS = ((0.45, 0.97, 0.10, 0.95), (0.9, 0.80, 0.16, 0.6), (1.35, 0.46, 0.08, 0.3), (1.8, 0.16, 0.0, 0.1))
MOUTH_BACK_BELOW = 0.40  # below this height (fraction chin -> brow) the columns take their last share: the mouth's
# corners stay back under the whisker pads (the mouth line drawn back toward the cheek)
FOREHEAD = ((1.25, 0.004), (1.6, 0.012), (2.0, 0.016))  # (height fraction, m back): the forehead's slope
COLUMN_TOP = 0.62  # the lateral columns reach this high (fraction chin -> brow): below the lower lid
PAD_SCALE_Z = 0.82  # the nose pad's height against its width: broad and low
EAR_NOTCH_RADIUS = 0.006  # m: the notch's reach round its point on the rim (at s = 1)


def smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((np.asarray(x, dtype=float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def ear_weights(n: int) -> dict:
    """{side: (n,) 0..1}: the donor's own ear groups (its vertex ids survive the face subdivision unchanged)."""
    dn = bb_donor.donor()
    out = {}
    for sd in ("L", "R"):
        w = np.zeros(n)
        acc = np.zeros(md.N_BODY)
        for g, v in dn.W.items():
            if g.startswith(f"ear.{sd}"):
                acc += v
        w[:md.N_BODY] = np.clip(acc, 0.0, 1.0)
        out[sd] = w
    return out


def front_point(V: np.ndarray, cand: np.ndarray, x: float, z: float, yc: float) -> np.ndarray:
    """The front-most skin point of the candidate vertices near (x, z) (the face looks down -Y)."""
    P = V[cand]
    d = np.abs(P[:, 0] - x) + 0.5 * np.abs(P[:, 2] - z)
    near = P[(d < np.sort(d)[min(24, len(d) - 1)] + 1e-12) & (P[:, 1] < yc)]
    return near[int(np.argmin(near[:, 1]))].copy()


class KirruWarp:
    """The warp (see the module doc). Built once on the sculpted donor head; called on any points."""

    def __init__(self, V: np.ndarray, head: np.ndarray, seam: np.ndarray, lm, face, kp: dict) -> None:
        self.lm, self.kp = lm, kp
        s = lm.h / 0.222
        self.s = s
        self.seam = V[seam]
        self.fade = SEAM_FADE * s
        mu = float(kp["muzzle_m"])  # his own measure (pell.md §1), not scaled
        yc = float(lm.P("head_c")[1])
        self.yc = yc
        z0, z1 = float(lm.P("chin")[2]), float(lm.P("brow")[2])
        W = float(face.mouth_half)
        cand = np.nonzero(head & (V[:, 1] < yc - 0.02 * s))[0]
        C, D = [], []

        def add(src: np.ndarray, d: np.ndarray) -> None:
            C.append(np.asarray(src, dtype=float))
            D.append(np.asarray(d, dtype=float))

        # the midline profile and the lateral columns of the lower face
        for f, fwd, lift in PROFILE:
            z = z0 + f * (z1 - z0)
            add(front_point(V, cand, 0.0, z, yc), (0.0, -fwd * mu, lift * mu))
            if f > COLUMN_TOP or f < -0.1:
                continue
            for cx, share_up, out, share_lo in COLUMNS:
                share = share_lo if f < MOUTH_BACK_BELOW else share_up
                for sg in (1.0, -1.0):
                    pad = out * mu * (1.0 if 0.1 <= f <= 0.5 else 0.5) * float(kp["whisker_pad"])
                    add(front_point(V, cand, sg * cx * W, z, yc), (sg * pad, -fwd * share * mu, lift * mu * share))
        # the nose pad: the alae come out to the pad's half-width, the pad lower and broader than the donor's
        tip = lm.P("nose_tip")
        half = 0.5 * float(kp["nose_pad_width_m"])
        zt = float(tip[2])
        for sg in (1.0, -1.0):
            ala = front_point(V, cand, sg * 0.55 * half, zt - 0.006 * s, yc)
            fwd_t = float(np.interp((zt - z0) / (z1 - z0), [p[0] for p in PROFILE], [p[1] for p in PROFILE]))
            add(ala, (sg * (half - abs(float(ala[0]))) * 0.6, -fwd_t * mu * 0.97, -(1.0 - PAD_SCALE_Z) * 0.004 * s))
        # anchors: the eyes (two rings round each globe), the brow and forehead, the crown, the ears' neighbourhood
        ang = np.linspace(0.0, 2.0 * np.pi, 12, endpoint=False)
        for sd in ("L", "R"):
            fr = face.eyes[sd]
            for rr in (0.018, 0.026):
                ring = fr.E + np.stack([np.cos(ang) * rr * 1.15, np.full(12, -0.004), np.sin(ang) * rr], axis=1) * s
                ring = ring[ring[:, 2] > fr.E[2] - 0.012 * s]  # the lower lid's cheek is free (it joins the muzzle)
                for p in ring:
                    add(p, (0.0, 0.0, 0.0))
            add(fr.E, (0.0, 0.0, 0.0))
        for f, back in FOREHEAD:  # the forehead slopes back from the brow (no human vertical brow)
            for cx in (0.0, 0.25, -0.25, 0.5, -0.5):
                z = z0 + f * (z1 - z0)
                if z < float(lm.P("crown")[2]) - 0.01 * s:
                    add(front_point(V, cand, cx * lm.head_w, z, yc), (0.0, back * (1.0 - abs(cx)), -0.5 * back))
        hc = lm.P("head_c")
        far = np.linspace(0.0, 2.0 * np.pi, 16, endpoint=False)
        for zz in (-0.05, 0.03, 0.10):
            ring = hc + np.stack([np.cos(far) * 0.13, np.sin(far) * 0.15 + 0.03, np.full(16, zz)], axis=1) * s
            for p in ring:
                if p[1] > yc:  # the back half only: the front is the face's
                    add(p, (0.0, 0.0, 0.0))
        self.C, self.D = np.array(C), np.array(D)
        self.rbf = bb_donor.RBF(self.C, self.D)

    # -------------------------------------------------------------------------------------------
    def seam_weight(self, P: np.ndarray) -> np.ndarray:
        d = np.full(len(P), np.inf)
        for a in range(0, len(P), 2048):
            q = P[a:a + 2048]
            d[a:a + 2048] = np.sqrt(((q[:, None, :] - self.seam[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
        return smoothstep(0.0, self.fade, d)

    def cranium(self, P: np.ndarray) -> np.ndarray:
        """The skull lengthened behind the ears and rounded (a pure y stretch behind the head centre)."""
        k = float(self.kp["cranium_length"]) - 1.0
        dy = np.maximum(P[:, 1] - self.yc, 0.0)
        out = P.copy()
        out[:, 1] = out[:, 1] + dy * k * smoothstep(self.yc - 0.01 * self.s, self.yc + 0.05 * self.s, P[:, 1])
        return out

    def ears(self, P: np.ndarray, ear_w: dict) -> np.ndarray:
        """Each ear scaled about its centre and moved up and back; the old notch in the left ear's rim."""
        out = P.copy()
        sc = float(self.kp["ear_scale"])
        ox, oy, oz = (float(v) for v in self.kp["ear_offset_m"])  # the stage's frame: x left, y up, z forward
        off = np.array([ox, -oz, oy])  # -> Blender's: x left, y back, z up
        for sd, w in ear_w.items():
            m = w > 0.5
            if not m.any():
                continue
            c = (P[m] * w[m, None]).sum(axis=0) / w[m].sum()
            tgt = c + off + (P - c) * sc
            out = out + (tgt - P) * w[:, None]
            nt = self.kp.get("ear_notch", {})
            if nt and str(nt.get("side", "L")).upper() == sd:
                Q = out[m]
                sgn = 1.0 if sd == "L" else -1.0
                # the rim's top-back: the point of the ear farthest out and up from its centre
                c2 = c + off
                score = (Q[:, 0] - c2[0]) * sgn * 0.3 + (Q[:, 2] - c2[2]) + 0.4 * (Q[:, 1] - c2[1])
                rim = Q[int(np.argmax(score))]
                r = EAR_NOTCH_RADIUS * self.s
                d = np.linalg.norm(out - rim, axis=1)
                pull = (1.0 - smoothstep(0.0, r, d)) * m * float(nt["depth_m"])
                to_c = c2 - out
                to_c /= np.maximum(np.linalg.norm(to_c, axis=1, keepdims=True), 1e-9)
                out = out + to_c * pull[:, None]
        return out

    def __call__(self, P: np.ndarray, ear_w: dict | None = None) -> np.ndarray:
        P = np.asarray(P, dtype=float)
        Q = self.cranium(P)
        if ear_w is not None:
            Q = self.ears(Q, ear_w)
        Q = self.rbf(Q)
        w = self.seam_weight(P)
        return P + (Q - P) * w[:, None]


def head_vertices(F: np.ndarray, freg: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray]:
    """(head, seam) vertex masks: a head vertex is used by a head, scalp or mouth face; the seam is shared."""
    hf = np.isin(freg, ["head", "scalp", "mouth"])
    vh, vb = np.zeros(n, bool), np.zeros(n, bool)
    vh[np.unique(F[hf][F[hf] >= 0])] = True
    vb[np.unique(F[~hf][F[~hf] >= 0])] = True
    return vh, vh & vb


def kirru_warp(V: np.ndarray, F: np.ndarray, freg: np.ndarray, lm, face, kp: dict) -> tuple[np.ndarray, KirruWarp]:
    """The donor body with its head warped (body vertices unchanged), and the warp itself."""
    head, seam = head_vertices(F, freg, len(V))
    warp = KirruWarp(V, head, seam, lm, face, kp)
    ew = ear_weights(len(V))
    out = V.copy()
    ids = np.nonzero(head & ~seam)[0]
    out[ids] = warp(V[ids], {k: w[ids] for k, w in ew.items()})
    return out, warp


def warp_units(unit_delta, V0: np.ndarray, V1: np.ndarray, warp: KirruWarp, ids: np.ndarray):
    """The donor's expression units carried through the warp: delta' = warp(V0 + delta) - warp(V0), on `ids` (the
    head's vertices; elsewhere the units are zero on the face anyway)."""
    ew = ear_weights(len(V0))
    sub = {k: w[ids] for k, w in ew.items()}

    def fn(unit: str) -> np.ndarray:
        d = unit_delta(unit)
        out = np.zeros_like(d)
        moved = np.linalg.norm(d[ids], axis=1) > 0.0
        if moved.any():
            k = ids[moved]
            out[k] = warp(V0[k] + d[k], {s: w[moved] for s, w in sub.items()}) - V1[k]
        return out

    return fn


def reread_landmarks(lm, face, V: np.ndarray, head: np.ndarray, warp: KirruWarp, commissure: float) -> dict:
    """The face points read back off the warped skin (bb_donor._override_landmarks' rules on the Kirru face); the
    mouth's half-width from the warped commissures. Returns the points before and after, for the report."""
    before = {k: lm.P(k).copy() for k in ("nose_tip", "subnasale", "mouth", "chin", "brow")}
    s = warp.s
    E = lm.P("eye")
    mid = head & (np.abs(V[:, 0]) < 0.003 * s)
    for k in ("subnasale", "mouth", "chin", "brow"):
        lm.pts[k] = warp(before[k][None, :])[0]
    # the pad's front: the most forward midline skin within a centimetre of where the warp took the nose tip
    zt = float(warp(before["nose_tip"][None, :])[0][2])
    band = mid & (np.abs(V[:, 2] - zt) < 0.01 * s) & (V[:, 2] < E[2] - 0.01 * s) & (V[:, 1] < warp.yc)
    lm.pts["nose_tip"] = V[np.nonzero(band)[0][np.argmin(V[band, 1])]].copy()
    corner = warp(np.array([[commissure, before["mouth"][1] + 0.006 * s, before["mouth"][2]]]))[0]
    lm.mouth_w = 2.0 * abs(float(corner[0]))
    face.mouth_half = lm.mouth_w / 2
    zc = float(lm.P("chin")[2])
    face.zc = zc
    face.vm = (lm.P("mouth")[2] - zc) / lm.h
    face.vs = (lm.P("subnasale")[2] - zc) / lm.h
    face.vt = (lm.P("nose_tip")[2] - zc) / lm.h
    return {k: (before[k].round(4).tolist(), lm.P(k).round(4).tolist()) for k in before}
