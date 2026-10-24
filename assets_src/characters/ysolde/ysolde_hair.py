"""Ysolde's hair as card layers (no bpy), ysolde.md §5.

Black, very long, drawn straight back from a smooth, severe hairline with no parting and wound into a **high flat
knot** at the crown (a drum 11 cm across and 9 cm tall, a little forward of the crown so it sits over the head in
profile). Built on the villagers' `bun` style (villager_hair.HairStyle: scalp cards traced toward the gather, which
stop under the knot, and a hairline row lying back into the hair), moved to the crown, with its own knot and the
two things only she has:

* **The knot** as 40 coiled ribbons wound round a flattened drum (the villager bun winds them round a ball).
* **The salt-white streak**, a band 2 cm wide from the left temple (her left, +X: the viewer's right from the
  front) back into the knot. It is **ash** worked into the hair, so it is its own card group on its own material
  (`hair_streak`: matte, the highlight off), never a grey hair; no grey card falls inside it.
* 6% of the other cards on `hair_grey` (#8C867D), spread evenly; 20 short flyaways at the knot only (her hair is
  controlled). Nothing moves: the scalp and the knot are head-rigid (build_ysolde), every card is pinned.

It is also the hairline and flow interface asha_textures reads to paint the scalp (`hairline_v`, `in_hair`,
`_gather`, `_flow_dir`), inherited from HairStyle. Seeded, deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_hair import SLOTS_FULL, SLOTS_SPARSE, _ribbon
from asha_mesh import Part
from villager_hair import STILL, HairStyle, _emit, _still

STREAK_MAT = "hair_streak"
STREAK_LIFT = 0.0062  # m at s = 1: the streak's cards ride just over the outer black layer
SCALP_SEGMENTS = 5  # per scalp card (hair is not on the Head object, but the LOD0 budget is)
KNOT_POINTS = 20
FLY_POINTS = 6


class YsoldeHair(HairStyle):
    """The villager bun style at the crown, with Ysolde's knot, streak and flyaways."""

    def __init__(self, params: dict) -> None:
        super().__init__(params)
        self.streak_az = math.radians(float(params["streak_azimuth_deg"]))
        self.streak_w = float(params["streak_width_m"])

    def in_streak(self, lm, P: np.ndarray) -> np.ndarray:
        """True on the scalp under the streak: the band from the left temple back toward the knot."""
        G = self._gather(lm)
        yc = lm.P("head_c")[1]
        root = self._temple(lm)
        d = G - root
        L = float(np.linalg.norm(d))
        d /= L
        t = np.clip((P - root) @ d, 0.0, L)
        off = np.linalg.norm(P - (root + np.outer(t, d)), axis=1)
        s = lm.h / 0.222
        _ = yc
        return (off < 0.5 * self.streak_w * s * (1.0 - 0.35 * t / L)) & (P[:, 0] > 0.0)

    def _temple(self, lm) -> np.ndarray:
        """The streak's root on the hairline at the left temple."""
        yc = lm.P("head_c")[1]
        zc = lm.P("chin")[2]
        phi = self.streak_az
        d = np.array([math.sin(phi), -math.cos(phi), 0.0])
        x = d * 0.45 * lm.head_w / max(abs(d[0]), 0.5)
        P = np.array([[x[0], yc + x[1], zc]])
        P[0, 2] = zc + float(self.hairline_v(lm, P)[0] + 0.004) * lm.h
        return P[0]

    def _mats(self, rng, n: int) -> list:
        share = float(self.p.get("grey_share", 0.0))
        return list(np.where(rng.random(n) < share, "hair_grey", "hair"))

    def build(self, lm, scalp) -> Part:
        part = Part("HairHead")
        rng = np.random.default_rng([self.seed, 0])
        s = lm.h / 0.222
        p = self.p
        G = self._gather(lm)
        self.hairline_row(part, scalp, lm, rng, int(p.get("hairline_cards", 40)), (0.03, 0.05))
        knot_r = 0.5 * float(p["knot_diameter_m"]) * s
        layers = [(0.0012, p["scalp_cards"][0], (0.007, 0.011)), (0.0030, p["scalp_cards"][1], (0.006, 0.010)),
                  (0.0048, p["scalp_cards"][2], (0.004, 0.007))]
        for li, (lift, count, wr) in enumerate(layers):
            roots = self._roots_inside(scalp, lm, rng, int(count) * 2, 0.006 + 0.008 * li)
            roots = roots[~self.in_streak(lm, roots)][:int(count)]  # the streak is its own group
            n = len(roots)
            if not n:
                continue
            dist = np.linalg.norm(roots - G, axis=1)
            paths = self._trace_to(scalp, lm, roots, dist * 1.3, lift * s, G, SCALP_SEGMENTS, knot_r * 0.7)
            slots = rng.integers(SLOTS_FULL, size=n) if li < 2 else rng.choice(SLOTS_SPARSE, n)
            mats = self._mats(rng, n)
            _emit(part, scalp, paths, rng.uniform(*wr, n) * s, slots, rng, 0.25, (0.0, 0.9), mats, 0.15, (0.05, 0.95))
        part.extend(self.streak(lm, scalp, rng, G, knot_r))
        knot, top = self.knot(lm, scalp, rng, G, knot_r)
        part.extend(knot)
        part.extend(self.flyaways(lm, rng, top, knot_r))
        part.C = [STILL] * len(part.V)
        self.knot_info = top
        return part

    def streak(self, lm, scalp, rng, G: np.ndarray, knot_r: float) -> Part:
        """The ash streak: cards rooted across the 2 cm band at the left temple, traced back along the flow into the
        knot, over the black layers."""
        part = Part("HairStreak")
        s = lm.h / 0.222
        n = int(self.p["streak_cards"])
        root = self._temple(lm)
        d = G - root
        d /= np.linalg.norm(d)
        side = np.cross(d, scalp.normal(root[None, :])[0])
        side /= np.linalg.norm(side)
        w = self.streak_w * s
        off = (np.arange(n) / max(n - 1, 1) - 0.5) * w * 0.9 + rng.uniform(-0.1, 0.1, n) * w
        back = rng.uniform(0.0, 0.012, n) * s  # a few start a little behind the hairline
        roots = scalp.project(root[None, :] + np.outer(off, side) + np.outer(back, d))
        dist = np.linalg.norm(roots - G, axis=1)
        paths = self._trace_to(scalp, lm, roots, dist * 1.3, STREAK_LIFT * s, G, 7, knot_r * 0.65)
        _emit(part, scalp, paths, rng.uniform(0.006, 0.009, n) * s, rng.integers(SLOTS_FULL, size=n), rng, 0.2,
              (0.0, 0.9), [STREAK_MAT] * n, 0.1, (0.05, 0.95))
        return part

    def knot(self, lm, scalp, rng, G: np.ndarray, r: float) -> tuple[Part, dict]:
        """The high flat knot: coiled ribbons wound round a drum (11 cm across, 9 cm tall) standing on the crown,
        its axis along the scalp normal there; the last ribbons run in from the streak's side, so the streak ends
        in the knot."""
        part = Part("HairKnot")
        s = lm.h / 0.222
        g = scalp.project(G[None, :])[0]
        up = scalp.normal(g[None, :])[0]
        up = up + np.array([0.0, 0.0, 1.0]) * 1.5
        up /= np.linalg.norm(up)
        H = float(self.p["knot_height_m"]) * s
        c = g + up * (0.5 * H - 0.012 * s)
        e1 = np.cross(up, np.array([1.0, 0.0, 0.0]))
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(up, e1)
        n_rib = int(self.p.get("bun_ribbons", 40))
        for k in range(n_rib):
            zf = (k + 0.5) / n_rib * 1.7 - 0.85 + rng.uniform(-0.06, 0.06)  # stacked up the drum
            a0 = rng.uniform(0.0, 2 * math.pi)
            span = rng.uniform(1.2, 1.9) * math.pi
            tilt = rng.uniform(-0.18, 0.18)
            t = np.linspace(0.0, 1.0, KNOT_POINTS)
            ang = a0 + span * t
            z = (zf + tilt * np.sin(ang - a0) + 0.08 * np.sin(math.pi * t)) * 0.5 * H
            # a drum with rounded shoulders: full radius over the middle, rolling in at the top and the base
            zn = np.clip(np.abs(z) / (0.5 * H), 0.0, 1.0)
            rr = r * (1.0 - 0.45 * zn ** 3.5) * (1.0 + 0.04 * (k % 3)) * (1.0 - 0.12 * np.sin(math.pi * t) ** 8)
            dirs = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
            pts = c + dirs * rr[:, None] + np.outer(z, up)
            nrm = dirs * (1.0 - zn[:, None] ** 2) + np.outer(np.sign(z) * zn ** 2, up)
            nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
            mat = self._mats(rng, 1)[0]
            _ribbon(part, pts, nrm, float(rng.uniform(0.012, 0.018) * s), int(rng.integers(SLOTS_FULL)), _still,
                    taper=0.15, v_range=(0.1, 0.9), mat=mat, u_range=(0.05, 0.95))
        # the top: a flat cap of ribbons spiralling in, so the drum reads closed from above
        for k in range(6):
            t = np.linspace(0.0, 1.0, KNOT_POINTS)
            ang = rng.uniform(0.0, 2 * math.pi) + 1.6 * math.pi * t
            rr = r * (0.85 - 0.6 * t)
            dirs = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
            pts = c + dirs * rr[:, None] + up * (0.5 * H - 0.004 * s * k)
            nrm = np.tile(up, (len(t), 1))
            _ribbon(part, pts, nrm, float(rng.uniform(0.014, 0.02) * s), int(rng.integers(SLOTS_FULL)), _still,
                    taper=0.3, v_range=(0.1, 0.9), mat="hair", u_range=(0.05, 0.95))
        return part, {"centre": c, "up": up, "e1": e1, "e2": e2, "radius": r, "height": H}

    def flyaways(self, lm, rng, top: dict, r: float) -> Part:
        """20 short loose hairs off the knot's surface (and nowhere else)."""
        part = Part("HairFly")
        s = lm.h / 0.222
        n = int(self.p.get("flyaways", 20))
        c, up, e1, e2, H = top["centre"], top["up"], top["e1"], top["e2"], top["height"]
        for k in range(n):
            a = rng.uniform(0.0, 2 * math.pi)
            z = rng.uniform(-0.3, 0.45) * H
            d = math.cos(a) * e1 + math.sin(a) * e2
            root = c + d * r * 0.98 + up * z
            out = d + up * rng.uniform(0.1, 0.6) + np.cross(up, d) * rng.uniform(-0.6, 0.6)
            out /= np.linalg.norm(out)
            L = rng.uniform(0.012, 0.03) * s
            t = np.linspace(0.0, 1.0, FLY_POINTS)
            pts = root + np.outer(t * L, out) + np.outer((t ** 2) * L * 0.3, -up)
            nrm = np.tile(np.cross(out, np.cross(up, out)), (FLY_POINTS, 1))
            nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
            _ribbon(part, pts, nrm, float(rng.uniform(0.0015, 0.0025) * s), int(rng.choice(SLOTS_SPARSE)), _still,
                    taper=0.6, v_range=(0.3, 0.95), mat=self._mats(rng, 1)[0], u_range=(0.3, 0.7))
        return part


def style(params: dict) -> YsoldeHair:
    return YsoldeHair(params)
