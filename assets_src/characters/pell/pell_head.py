"""The Kirru head warp (pell.md §9, M3-CHR-506). No bpy.

Pell keeps the MakeHuman donor's head topology (ADR 0021) and the whole face pipeline by adding one step between the
face sculpt and the face shapes: `kirru_warp`. Since the look-dev review (the RBF push of the donor face into a muzzle
read as a deformed human with a snout) the warp no longer starts from the donor face's landmarks; it reshapes the
head onto a Kirru head surface (`KirruWarp.sdf`, from pell_params.json's `_kirru.otter_head`):

* a broad, low cranium; a short, broad muzzle flowing straight out of the skull line, with the nose pad and the two
  whisker pads on it; full jowls and a small chin under the mouth; a thick neck (`thicken_neck`, every vertex below
  the jaw, so the seam stays welded);
* the skin goes there along rays from a centre in the skull (one-to-one: nothing folds), the move smoothed over the
  head, with only `detail_keep` of the donor's own relief kept (the human brow, cheekbones and nose do not show);
* three regions ride rigidly so the face pipeline keeps working: each eye with its lids (set high and wide on the
  cranium's front, the eye frames moved with them), the mouth with its bag, teeth and tongue (drawn in to a short line
  under the muzzle), and each ear (scaled to `ear_scale`, set low and back, the old notch in the left one).

The warp is a function of position (plus the donor's ear weights), so the same call carries the mouth interior built
on the donor face and the donor's expression units (`warp_units`). After it, `reread_landmarks` reads the face points
back off the warped skin, so the eyes, teeth, lashes and the 40 shapes are built on the Kirru face under the same
names. The move fades to nothing at the head/neck seam, so the Head stays welded to the Body.

Deterministic: no random terms; numpy only.
"""
from __future__ import annotations

import numpy as np

import bb_donor
import mpfb_data as md

SEAM_FADE = 0.06  # m (at s = 1): the warp fades in over this distance from the head/neck seam
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


def _ellipsoid(P: np.ndarray, c, r) -> np.ndarray:
    """An ellipsoid's approximate signed distance (exact on the surface, scaled by its smallest radius)."""
    r = np.asarray(r, dtype=float)
    return (np.linalg.norm((P - np.asarray(c, dtype=float)) / r, axis=1) - 1.0) * float(r.min())


def _capsule(P: np.ndarray, a, b, r: float) -> np.ndarray:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    ab = b - a
    t = np.clip(((P - a) @ ab) / float(ab @ ab), 0.0, 1.0)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1) - r


def _smin(a: np.ndarray, b: np.ndarray, k: float) -> np.ndarray:
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b + (a - b) * h - k * h * (1.0 - h)


class KirruWarp:
    """The warp (see the module doc). Built once on the sculpted donor head; called on any points.

    M3-CHR-506 look-dev (review): the head is no longer the donor's face pushed into a muzzle. The donor head's skin is
    projected onto a Kirru head surface built from `_kirru.otter_head` (a broad, low cranium; a short, broad muzzle
    flowing out of the skull line with the nose pad and the whisker pads on it; full jowls; a thick neck), while three
    regions ride along rigidly so the face pipeline keeps working: each eye (its lids and socket, moved high and wide
    onto the cranium's front), the mouth (its lips narrowed to a short line on the muzzle's underside, with the
    teeth and tongue inside) and each ear (scaled, set low and back on the skull). Every point's move fades to nothing
    at the head/neck seam, so the Head stays welded to the Body."""

    def __init__(self, V: np.ndarray, head: np.ndarray, seam: np.ndarray, lm, face, kp: dict,
                 inner: np.ndarray | None = None) -> None:
        self.lm, self.kp = lm, kp
        s = lm.h / 0.222
        self.s = s
        self.seam = V[seam]
        self.fade = SEAM_FADE * s
        oh = kp["otter_head"]
        self.oh = oh
        self.yc = float(lm.P("head_c")[1])
        E = lm.P("eye")
        self.E0 = E.copy()
        self.origin = np.array([0.0, float(E[1]), float(E[2])])  # the shapes are placed relative to the eyes' plane
        o = self.origin
        sh = V[seam]
        # the neck: a capsule through the seam's centre, as thick as the body's neck there
        nc = np.array([0.0, float(np.median(sh[:, 1])), float(sh[:, 2].min())])
        self.neck_r = float(np.median(np.hypot(sh[:, 0], sh[:, 1] - nc[1]))) * float(oh["neck_fill"])
        self.neck = (nc - np.array([0.0, 0.0, 0.25 * s]), nc + np.array([0.0, -0.01 * s, float(oh["neck_top_m"])]))
        self.parts = [(o + np.asarray(c, dtype=float), r) for c, r in
                      (oh["cranium"], oh["muzzle"], oh["jowls"], oh["chin"])]
        self.pad = (o + np.asarray(oh["nose_pad"][0], dtype=float), oh["nose_pad"][1])
        self.wpads = [(o + np.asarray(oh["whisker_pad"][0], dtype=float) * np.array([sg, 1.0, 1.0]),
                       oh["whisker_pad"][1]) for sg in (1.0, -1.0)]
        # the rigid regions' targets
        self.eye0 = {sd: lm.side_pt("eye", sd).copy() for sd in ("L", "R")}
        self.eye_d = self._eye_shift(lm, face)
        m0 = lm.P("mouth")
        self.mouth0 = m0.copy()
        mt = self.project((o + np.asarray(oh["mouth_at"], dtype=float))[None, :])[0]
        self.mouth_d = mt - m0
        self.mouth_x = float(oh["mouth_width"])
        self.mouth_r = np.asarray(oh["mouth_region_m"], dtype=float)
        # each eye set so the skin at its region's rim lands on the surface (no step into the cranium)
        Hv = V[head]
        for sd in ("L", "R"):
            Ec = self.eye0[sd]
            r0 = float(oh["eye_region_m"][0])
            dist = np.linalg.norm(Hv - Ec, axis=1)
            rim = Hv[(dist > r0) & (dist < r0 + 0.004)] + self.eye_d[sd]
            if len(rim):
                n = self.normal(rim.mean(axis=0)[None, :])[0]
                self.eye_d[sd] = self.eye_d[sd] - n * float(np.median(self.sdf(rim)))
        # the move is smoothed over the head (a Gaussian average of the raw move at the donor head's vertices), so
        # the projection's converging normals and the rigid regions' rims never fold the skin
        stride = int(oh["sample_stride"])
        smp = Hv[::stride]
        raw = self.raw_move(smp)
        if inner is not None:  # the mouth's bag (its inner walls, back to the throat) rides with the mouth
            ins = inner[head][::stride]
            raw[ins] = self.mouth_move(smp[ins]) - smp[ins]
        # the donor's interior skin (the nose's and the mouth's inner walls) points back through the centre: its rays
        # find the far side of the skull, so those samples are left out (the points there take their neighbours' move)
        ok = np.linalg.norm(raw, axis=1) < float(oh["max_move_m"])
        self.samples, self.raw = smp[ok], raw[ok]
        self.sigma = float(oh["smooth_m"])

    # ---- the Kirru head surface -------------------------------------------------------------------------------
    def sdf(self, P: np.ndarray) -> np.ndarray:
        k = float(self.oh["blend_m"])
        d = _ellipsoid(P, *self.parts[0])
        for c, r in self.parts[1:]:
            d = _smin(d, _ellipsoid(P, c, r), k)
        if float(self.oh["neck_fill"]) > 0.0:
            d = _smin(d, _capsule(P, self.neck[0], self.neck[1], self.neck_r), k)
        d = _smin(d, _ellipsoid(P, *self.pad), 0.3 * k)
        for c, r in self.wpads:
            d = _smin(d, _ellipsoid(P, c, r), 0.5 * k)
        return d

    def project(self, P: np.ndarray, steps: int = 6) -> np.ndarray:
        """Each point moved onto the surface along the field's gradient (Newton steps)."""
        Q = np.asarray(P, dtype=float).copy()
        e = 1e-4
        for _ in range(steps):
            d = self.sdf(Q)
            g = np.stack([(self.sdf(Q + np.array(v) * e) - self.sdf(Q - np.array(v) * e)) / (2 * e)
                          for v in ((1, 0, 0), (0, 1, 0), (0, 0, 1))], axis=1)
            g2 = np.maximum((g * g).sum(axis=1), 1e-12)
            Q = Q - (d / g2)[:, None] * g
        return Q

    def normal(self, P: np.ndarray) -> np.ndarray:
        e = 1e-4
        g = np.stack([(self.sdf(P + np.array(v) * e) - self.sdf(P - np.array(v) * e)) / (2 * e)
                      for v in ((1, 0, 0), (0, 1, 0), (0, 0, 1))], axis=1)
        return g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)

    def _eye_shift(self, lm, face) -> dict:
        """Each eye's move: its globe's front set into the cranium's front at `eye_at` (high and wide), the globe
        sunk `eye_sink` of its radius below the surface so the lids close over it."""
        oh = self.oh
        out = {}
        for sd in ("L", "R"):
            sg = 1.0 if sd == "L" else -1.0
            E = face.eyes[sd].E
            ax, az = float(oh["eye_at"][0]), float(oh["eye_at"][1])
            P = np.array([[sg * ax, self.origin[1] - 0.3, self.origin[2] + az]])
            # march back from in front of the face to the surface
            for t in np.linspace(0.0, 0.5, 501):
                q = P + np.array([[0.0, t, 0.0]])
                if self.sdf(q)[0] < 0.0:
                    break
            Sx = self.project(q)[0]
            n = self.normal(Sx[None, :])[0]
            tgt = Sx - n * float(face.eyes[sd].R) * float(oh["eye_sink"])
            out[sd] = tgt - E
        return out

    # ---- the move -----------------------------------------------------------------------------------------
    def seam_weight(self, P: np.ndarray) -> np.ndarray:
        d = np.full(len(P), np.inf)
        for a in range(0, len(P), 2048):
            q = P[a:a + 2048]
            d[a:a + 2048] = np.sqrt(((q[:, None, :] - self.seam[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
        return smoothstep(0.0, self.fade, d)

    def eye_weight(self, P: np.ndarray, sd: str) -> np.ndarray:
        r0, r1 = (float(x) for x in self.oh["eye_region_m"])
        return 1.0 - smoothstep(r0, r1, np.linalg.norm(P - self.eye0[sd], axis=1))

    def mouth_weight(self, P: np.ndarray) -> np.ndarray:
        q = (P - self.mouth0) / self.mouth_r
        return 1.0 - smoothstep(1.0, 1.8, np.linalg.norm(q, axis=1))

    def ears(self, P: np.ndarray, ear_w: dict) -> tuple[np.ndarray, np.ndarray]:
        """Each ear's points scaled about its centre and set on the skull's side, low and back (`ear_at`); the old
        notch bitten out of the left ear's rim. Returns (the moved points, the ear weight)."""
        out = P.copy()
        wsum = np.zeros(len(P))
        sc = float(self.kp["ear_scale"])
        oh = self.oh
        for sd, w in ear_w.items():
            m = w > 0.5
            if not m.any():
                continue
            sg = 1.0 if sd == "L" else -1.0
            c = (P[m] * w[m, None]).sum(axis=0) / w[m].sum()
            at = self.origin + np.array([sg * 0.3, float(oh["ear_at"][0]), float(oh["ear_at"][1])])
            # out along x from the skull's mid-plane to its side
            for t in np.linspace(0.0, 0.3, 301):
                q = (at + np.array([sg * t, 0.0, 0.0]))[None, :]
                if self.sdf(q)[0] > 0.0:
                    break
            c2 = self.project(q)[0] + self.normal(q)[0] * 0.004 * self.s
            tgt = c2 + (P - c) * sc
            nt = self.kp.get("ear_notch", {})
            if nt and str(nt.get("side", "L")).upper() == sd:
                Q = tgt[m]
                score = (Q[:, 0] - c2[0]) * sg * 0.3 + (Q[:, 2] - c2[2]) + 0.4 * (Q[:, 1] - c2[1])
                rim = Q[int(np.argmax(score))]
                d = np.linalg.norm(tgt - rim, axis=1)
                pull = (1.0 - smoothstep(0.0, EAR_NOTCH_RADIUS * self.s, d)) * float(nt["depth_m"])
                to_c = c2 - tgt
                to_c /= np.maximum(np.linalg.norm(to_c, axis=1, keepdims=True), 1e-9)
                tgt = tgt + to_c * pull[:, None]
            out = out + (tgt - out) * w[:, None]
            wsum = np.maximum(wsum, w)
        return out, wsum

    def radial(self, P: np.ndarray) -> np.ndarray:
        """Each point moved along its ray from the head's centre (`centre`) to the surface: one-to-one, so the
        skin never folds (the Kirru head is star-shaped about that point)."""
        C = self.origin + np.asarray(self.oh["centre"], dtype=float)
        D = np.asarray(P, dtype=float) - C
        L = np.maximum(np.linalg.norm(D, axis=1, keepdims=True), 1e-9)
        U = D / L
        lo, hi = np.zeros(len(P)), np.full(len(P), 0.5)
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            inside = self.sdf(C + U * mid[:, None]) < 0.0
            lo, hi = np.where(inside, mid, lo), np.where(inside, hi, mid)
        return C + U * (0.5 * (lo + hi))[:, None]

    def raw_move(self, P: np.ndarray) -> np.ndarray:
        """The unsmoothed move: onto the surface along the rays, with the eyes and the mouth carried rigidly."""
        P = np.asarray(P, dtype=float)
        Q = self.radial(P)
        for sd in ("L", "R"):
            w = self.eye_weight(P, sd)
            Q = Q + ((P + self.eye_d[sd]) - Q) * w[:, None]
        wm = self.mouth_weight(P)
        Q = Q + (self.mouth_move(P) - Q) * wm[:, None]
        return Q - P

    def mouth_move(self, P: np.ndarray) -> np.ndarray:
        """The mouth's rigid move, its width drawn in to a short line."""
        M = P + self.mouth_d
        M[:, 0] = (P[:, 0] - self.mouth0[0]) * self.mouth_x + self.mouth0[0] + self.mouth_d[0]
        return M

    def move(self, P: np.ndarray) -> np.ndarray:
        """The smoothed move. Away from the eyes and the mouth only `detail_keep` of the donor's own relief (its
        offset from the local average) is kept: the human brow, cheekbones and nose do not show through the skull."""
        out = np.zeros((len(P), 3))
        k = -0.5 / (self.sigma * self.sigma)
        keep0 = float(self.oh["detail_keep"])
        keep = np.maximum(np.maximum(self.eye_weight(P, "L"), self.eye_weight(P, "R")), self.mouth_weight(P))
        keep = keep0 + (1.0 - keep0) * keep
        for a in range(0, len(P), 1024):
            q = P[a:a + 1024]
            d2 = ((q[:, None, :] - self.samples[None, :, :]) ** 2).sum(axis=2)
            w = np.exp(k * d2)
            ws = np.maximum(w.sum(axis=1, keepdims=True), 1e-30)
            mv = (w @ self.raw) / ws
            avg = (w @ self.samples) / ws
            out[a:a + 1024] = mv - (1.0 - keep[a:a + 1024, None]) * (q - avg)
        return out

    def __call__(self, P: np.ndarray, ear_w: dict | None = None) -> np.ndarray:
        P = thicken_neck(np.asarray(P, dtype=float), self.lm, self.kp)
        Q = P + self.move(P)
        if ear_w is not None:
            E, we = self.ears(P, ear_w)
            Q = Q + (E - Q) * we[:, None]
        w = self.seam_weight(P)
        return P + (Q - P) * w[:, None]


def head_vertices(F: np.ndarray, freg: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray]:
    """(head, seam) vertex masks: a head vertex is used by a head, scalp or mouth face; the seam is shared."""
    hf = np.isin(freg, ["head", "scalp", "mouth"])
    vh, vb = np.zeros(n, bool), np.zeros(n, bool)
    vh[np.unique(F[hf][F[hf] >= 0])] = True
    vb[np.unique(F[~hf][F[~hf] >= 0])] = True
    return vh, vh & vb


def thicken_neck(V: np.ndarray, lm, kp: dict) -> np.ndarray:
    """The neck thickened round its own axis (`neck_scale`: at the sternal notch, and at the skull's base), fading
    out above the jaw: the thick otter neck that merges into the head (look-dev review). Every vertex, head and body
    alike, so the seam stays welded."""
    a, b = (float(x) for x in kp["otter_head"]["neck_scale"])
    nb, hc = lm.P("notch"), lm.P("head_c")
    z0, z1 = float(nb[2]) + 0.02 * lm.S, float(lm.P("chin")[2])
    z = V[:, 2]
    t = np.clip((z - z0) / (z1 - z0), 0.0, 1.0)
    k = (a + (b - a) * smoothstep(0.0, 0.8, t)) * (1.0 - smoothstep(0.85, 1.0, t)) + smoothstep(0.85, 1.0, t)
    on = smoothstep(z0 - 0.06 * lm.S, z0, z)  # nothing below the notch
    k = 1.0 + (k - 1.0) * on
    yc = float(nb[1]) + 0.03 * lm.S + (float(hc[1]) - float(nb[1]) - 0.03 * lm.S) * t
    out = V.copy()
    out[:, 0] = V[:, 0] * k
    out[:, 1] = yc + (V[:, 1] - yc) * k
    return out


def kirru_warp(V: np.ndarray, F: np.ndarray, freg: np.ndarray, lm, face, kp: dict) -> tuple[np.ndarray, KirruWarp]:
    """The donor body with its head warped (body vertices unchanged), and the warp itself."""
    Vt = thicken_neck(V, lm, kp)
    head, seam = head_vertices(F, freg, len(V))
    mf = freg == "mouth"
    inner = np.zeros(len(V), bool)
    inner[np.unique(F[mf][F[mf] >= 0])] = True
    warp = KirruWarp(Vt, head, seam, lm, face, kp, inner)
    ew = ear_weights(len(V))
    out = Vt.copy()
    ids = np.nonzero(head & ~seam)[0]
    out[ids] = warp(V[ids], {k: w[ids] for k, w in ew.items()})
    for sd in ("L", "R"):  # the eye frames ride with their regions (the lids, lashes and globes are built on them)
        face.eyes[sd].E = face.eyes[sd].E + warp.eye_d[sd]
    lm.pts["eye"] = face.eyes["L"].E.copy()
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
    # the pad's front: the most forward midline skin within a centimetre of the nose pad's centre
    zt = float(warp.pad[0][2])
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
