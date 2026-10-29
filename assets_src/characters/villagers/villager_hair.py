"""Haluna villagers' hair as card layers (no bpy), M2-CHR-03, on the heroes' card machinery.

One `HairStyle` per villager (the `_hair` block of params/<npc>.json). It is also the hairline and
flow interface asha_textures reads to paint the scalp (`hairline_v`, `in_hair`, `_gather`,
`_flow_dir`), so the skin maps agree with the cards. Kinds:

* `short`: men's and the child's short hair (2-5 cm), multi-segment cards lying along a flow that
  leaves a crown whorl (forward over the top, down at the sides and the nape), slightly lifted tips.
* `cropped`: close-cropped (8-14 mm, single-segment cards as toma_hair), optionally receding.
* `bun`: hair drawn back from the hairline to a low knot at the back of the head: scalp cards traced
  toward the gather point (they stop there), and the knot itself as coiled ribbons round a ball.
* `wrap`: the hair is under a head wrap (villager_costume.build_headwrap); only a row of hairline
  cards shows below its edge.

Cards use Asha's 2K hair atlas (asha_hair columns: full, sparse, hairline). `grey_share` sends a
share of the cards to the `hair_grey` material. Vertex colour = wind; short and tied hair is pinned
(`_emit`, the card emitter toma_hair had before M2-CHR-04). Seeded, deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_hair import ROOT_CAST_H, SLOTS_FULL, SLOTS_HAIRLINE, SLOTS_SPARSE, _ribbon
from asha_mesh import Part

STILL = (0.0, 0.0, 0.0, 0.0)  # no wind on short or tied hair
# M3-CHR-592 `tufts`: toma_hair.scalp_cards' three layers (lift off the scalp, tip rise, root margin inside the
# hairline in head heights) and its card widths (m, at s = 1)
TUFT_LIFT_M = (0.0008, 0.0022, 0.0036)
TUFT_RISE_M = (0.0008, 0.0013, 0.0018)
TUFT_MARGIN_H = (0.002, 0.008, 0.014)
TUFT_WIDTH_M = (0.006, 0.009)
# cards sample the tip zone and dense middle of the atlas columns (a short card over a whole column
# reads as a square chip up close)
CARD_V = (0.62, 0.96)
CARD_U = (0.22, 0.78)
GREY_U = (0.0, 1.0)  # `grey_strands`: a grey card takes its whole sparse column, feathered edges and all
GREY_WIDTH_K = 0.7
GREY_V_CROPPED = (0.30, 0.92)  # `grey_strands` on cropped hair: the strand samples more than the tip zone (CARD_V)  # `grey_strands`: a grey card's width against a dark one's


def _still(t: float) -> tuple:
    return STILL


def _emit(part: Part, surface, paths: np.ndarray, widths, slots, rng, taper: float, v_range, mats=None,
          twist: float = 0.3, u_range=(0.0, 1.0)) -> None:
    """One ribbon card per path, rolled a random amount about its length, normals from `surface`."""
    for c in range(len(paths)):
        pts = paths[c]
        nrm = surface.normal(pts)
        T = np.gradient(pts, axis=0)
        T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
        side = np.cross(T, nrm)
        a = rng.uniform(-twist, twist)
        nrm = nrm * math.cos(a) - side * math.sin(a)
        _ribbon(part, pts, nrm, float(widths[c]), int(slots[c]), _still, taper=taper,
                v_range=v_range[c] if isinstance(v_range, list) else v_range,
                mat="hair" if mats is None else mats[c], u_range=u_range[c] if isinstance(u_range, list) else u_range)


# hairline tables (head heights above the chin) by |azimuth| (0 front, 90 the side, 180 the back)
HAIRLINES = {
    # a man's: square at the front, short sideburns, low nape (rhen_hair / toma_hair)
    "male": ([0, 20, 34, 46, 58, 70, 80, 90, 104, 118, 140, 162, 180],
             [0.722, 0.722, 0.714, 0.704, 0.672, 0.600, 0.540, 0.540, 0.575, 0.46, 0.30, 0.235, 0.225]),
    # a woman's: rounded and a little higher at the front, the temples framed (asha_hair, no part)
    "female": ([0, 30, 50, 66, 76, 84, 96, 112, 135, 160, 180],
               [0.735, 0.728, 0.690, 0.635, 0.592, 0.586, 0.635, 0.50, 0.32, 0.25, 0.24]),
}


class HairStyle:
    def __init__(self, params: dict) -> None:
        self.p = params
        self.kind = params["kind"]
        self.table = HAIRLINES[params.get("hairline", "female" if self.kind in ("bun", "wrap") else "male")]
        self.recede = float(params.get("recede", 0.0))  # head heights the temples sit back
        self.seed = int(params.get("seed", 1))

    # ---- the interface asha_textures reads --------------------------------------------------
    def hairline_v(self, lm, P: np.ndarray) -> np.ndarray:
        yc = lm.P("head_c")[1]
        phi = np.degrees(np.arctan2(P[:, 0], -(P[:, 1] - yc)))
        a = np.abs(phi)
        t = np.radians(phi)
        wander = 0.004 * np.sin(9.0 * t + 0.3 * self.seed) + 0.0025 * np.sin(17.0 * t + 1.1) + \
            0.0015 * np.sin(31.0 * t + 0.6)
        temple = self.recede * np.exp(-((a - 45.0) / 16.0) ** 2) + 0.4 * self.recede * np.exp(-(a / 18.0) ** 2)
        return np.interp(a, *self.table) + wander + temple

    def in_hair(self, lm, P: np.ndarray, margin_h: float = 0.0) -> np.ndarray:
        zc = lm.P("chin")[2]
        return (P[:, 2] - zc) / lm.h > self.hairline_v(lm, P) + margin_h

    def _gather(self, lm) -> np.ndarray:
        yc = lm.P("head_c")[1]
        zc = lm.P("chin")[2]
        if self.kind in ("bun", "wrap"):  # the knot at the back of the head
            return np.array([0.0, yc + float(self.p.get("bun_back_h", 0.50)) * lm.h,
                             zc + float(self.p.get("bun_height_h", 0.60)) * lm.h])
        return np.array([-0.05 * lm.head_w, yc + 0.22 * lm.h, zc + 1.0 * lm.h])  # the crown whorl

    def _flow_dir(self, lm, P: np.ndarray, N: np.ndarray, G: np.ndarray) -> np.ndarray:
        zc = lm.P("chin")[2]
        yc = lm.P("head_c")[1]
        v = (P[:, 2] - zc) / lm.h
        if self.kind == "wrap":  # combed straight up and back under the wrap
            d = np.tile(np.array([0.0, 0.7, 1.0]), (len(P), 1))
        elif self.kind == "bun":
            to_g = G - P
            d = to_g / np.maximum(np.linalg.norm(to_g, axis=1, keepdims=True), 1e-9)
            front = np.clip(-(P[:, 1] - yc) / (0.4 * lm.h), 0.0, 1.0)
            lift = np.clip((self.hairline_v(lm, P) + 0.12 - v) / 0.12, 0.0, 1.0) * front
            d = d + np.outer(1.2 * lift, np.array([0.0, 0.6, 1.0])) + np.array([0.0, 0.3, 0.0])
        else:
            away = P - G
            away /= np.maximum(np.linalg.norm(away, axis=1, keepdims=True), 1e-9)
            top = np.clip((v - 0.70) / 0.18, 0.0, 1.0)
            fwd = np.array([0.0, -1.0, 0.0])
            down = np.array([0.0, 0.15, -1.0])
            d = away * (0.6 + 0.4 * top)[:, None] + fwd[None, :] * (0.5 * top)[:, None] + \
                down[None, :] * (0.8 * (1 - top))[:, None]
        d = d - np.sum(d * N, axis=1, keepdims=True) * N
        return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)

    # ---- cards ------------------------------------------------------------------------------
    def _roots_inside(self, scalp, lm, rng, n: int, margin: float, max_v: float = 9.0) -> np.ndarray:
        yc = lm.P("head_c")[1]
        zc = lm.P("chin")[2]
        hc = np.array([0.0, yc, zc + 0.55 * lm.h])
        d_in = rng.normal(size=(n * 8, 3))
        d_in[:, 2] = np.abs(d_in[:, 2]) * 1.2 + 0.05
        d_in /= np.linalg.norm(d_in, axis=1, keepdims=True)
        p_in = scalp.project(hc + d_in * ROOT_CAST_H * lm.h)
        v = (p_in[:, 2] - zc) / lm.h
        ok = self.in_hair(lm, p_in, margin) & (v < self.hairline_v(lm, p_in) + max_v)
        return p_in[ok][:n]

    def _hairline_roots(self, scalp, lm, phi: np.ndarray, inside_h: np.ndarray) -> np.ndarray:
        yc = lm.P("head_c")[1]
        zc = lm.P("chin")[2]
        hc = np.array([0.0, yc, zc + 0.55 * lm.h])
        d = np.stack([np.sin(phi), -np.cos(phi), np.zeros(len(phi))], axis=1)
        p = scalp.project(hc + d * ROOT_CAST_H * lm.h)
        for _ in range(10):
            dz = (zc + (self.hairline_v(lm, p) + inside_h) * lm.h) - p[:, 2]
            p = scalp.project(p + np.stack([np.zeros(len(p)), np.zeros(len(p)), dz], axis=1))
        return p

    def _mats(self, rng, n: int) -> list:
        share = float(self.p.get("grey_share", 0.0))
        return list(np.where(rng.random(n) < share, "hair_grey", "hair"))

    def _grey_strands(self, widths: np.ndarray, slots: np.ndarray, mats: list, u_range) -> tuple:
        """M3-CHR-538 (optional `grey_strands`): a grey card samples a sparse atlas column over its whole width and is
        `grey_width_k` as wide, so salt-and-pepper reads as single grey strands through the dark hair, not as solid
        light chips. Draws nothing from the rng, so the cards' layout is unchanged; without the key it is a no-op."""
        mode = self.p.get("grey_strands", False)
        if not mode:
            return widths, slots, u_range
        # "all": every card is a strand (thin white hair over a bare scalp, M3-CHR-536), not only the grey share
        g = np.ones(len(mats), dtype=bool) if mode == "all" else np.array(mats) == "hair_grey"
        k = float(self.p.get("grey_width_k", GREY_WIDTH_K))
        sparse = np.array([SLOTS_SPARSE[i % len(SLOTS_SPARSE)] for i in range(len(mats))])
        return (np.where(g, widths * k, widths), np.where(g, sparse, slots),
                [GREY_U if gi else u_range for gi in g])

    def _trace_to(self, scalp, lm, roots, length, lift, G, seg, stop_r):
        """Paths over the scalp along the flow toward G; a path stops within `stop_r` of G."""
        step = length / seg
        paths = [scalp.project(roots, lift)]
        alive = np.ones(len(roots), dtype=bool)
        for _ in range(seg):
            cur = paths[-1]
            N = scalp.normal(cur)
            nxt = scalp.project(cur + self._flow_dir(lm, cur, N, G) * step[:, None], lift)
            near = np.linalg.norm(nxt - G, axis=1) < stop_r
            nxt = np.where(alive[:, None], nxt, cur)
            alive &= ~near
            paths.append(nxt)
        return np.stack(paths, axis=1)

    def _trace_clamped(self, scalp, lm, roots, length, lift, seg, rise, G) -> np.ndarray:
        """Paths along the flow that never run more than `fringe_spill` head heights past the
        hairline (the front only; elsewhere they stop at it), as rhen_hair._trace; the tips rise by
        `rise` off the scalp."""
        yc = lm.P("head_c")[1]
        zc = lm.P("chin")[2]
        spill = float(self.p.get("fringe_spill", 0.02))
        step = length / seg
        paths = [scalp.project(roots, lift)]
        for _ in range(seg):
            cur = paths[-1]
            N = scalp.normal(cur)
            nxt = scalp.project(cur + self._flow_dir(lm, cur, N, G) * step[:, None], lift)
            front = np.clip(-(nxt[:, 1] - yc) / (0.3 * lm.h), 0.0, 1.0) ** 2
            ok = (nxt[:, 2] - zc) / lm.h > self.hairline_v(lm, nxt) - spill * front - 0.008
            paths.append(np.where(ok[:, None], nxt, cur))
        out = np.stack(paths, axis=1)
        tt = (np.arange(seg + 1) / seg) ** 1.5
        Nn = scalp.normal(out.reshape(-1, 3)).reshape(out.shape)
        return out + Nn * (rise[:, None] * tt[None, :])[..., None]

    def hairline_row(self, part: Part, scalp, lm, rng, n_hl: int, length, inside=(0.002, 0.008)) -> None:
        """A row of soft-rooted cards at the hairline, lying back into the hair."""
        if not n_hl:
            return
        G = self._gather(lm)
        s = lm.h / 0.222
        lim = math.pi * 0.97
        phi = np.sort(np.linspace(-lim, lim, n_hl) + rng.uniform(-0.4, 0.4, n_hl) * (2 * lim / n_hl))
        roots = self._hairline_roots(scalp, lm, phi, rng.uniform(*inside, n_hl))
        seg = 2
        paths = self._trace_clamped(scalp, lm, roots, rng.uniform(*length, n_hl) * s, 0.0008 * s, seg,
                                    rng.uniform(0.0, 0.0008, n_hl) * s, G)
        widths = rng.uniform(0.004, 0.006, n_hl) * s
        slots = rng.choice(SLOTS_HAIRLINE, n_hl)
        mats = self._mats(rng, n_hl)
        widths, slots, u_rng = self._grey_strands(widths, slots, mats, CARD_U)
        _emit(part, scalp, paths, widths, slots, rng, 0.3, (0.0, 0.6), mats, 0.3, u_rng)

    def tuft_layers(self, part: Part, scalp, lm, rng, G, s: float) -> None:
        """M3-CHR-592 (optional `tufts`): short and cropped hair on Toma's short-hair atlas (toma_hair's tufts of
        tapered strands with ragged tips, M2-CHR-524), not the tip zone of Asha's long-strand columns (square chips
        at dialogue range). Toma's three lifted layers, rooted inside this style's own hairline and traced along its
        flow (`_trace_clamped`: the front may spill a little past the hairline); the cards nearest the hairline take
        the short "edge" column, the outer layer mixes in the sparse ones. The hairline row uses the edge column too.
        write_materials gives `hair` and `hair_grey` the short atlas."""
        import toma_hair as th

        p = self.p
        lo, hi = p.get("length_m", [0.02, 0.04])
        wlo, whi = p.get("card_width_m", TUFT_WIDTH_M)
        seg = 1 if self.kind == "cropped" else 2
        zc = lm.P("chin")[2]
        rise_k = float(p.get("rise", 1.0))
        n_hl = int(p.get("hairline_cards", 0))
        if n_hl:
            lim = math.pi * 0.97
            phi = np.sort(np.linspace(-lim, lim, n_hl) + rng.uniform(-0.4, 0.4, n_hl) * (2 * lim / n_hl))
            roots = self._hairline_roots(scalp, lm, phi, rng.uniform(0.002, 0.008, n_hl))
            paths = self._trace_clamped(scalp, lm, roots, rng.uniform(0.5 * lo, 0.8 * lo, n_hl) * s, 0.0008 * s, seg,
                                        rng.uniform(0.0, 0.0008, n_hl) * s, G)
            th._emit(part, scalp, paths, rng.uniform(wlo, whi, n_hl) * s, rng.choice(th.SH_EDGE, n_hl), rng, 0.25,
                     self._mats(rng, n_hl))
        for li, (lift, count, rise, margin) in enumerate(zip(TUFT_LIFT_M, p["scalp_cards"], TUFT_RISE_M,
                                                             TUFT_MARGIN_H)):
            roots = self._roots_inside(scalp, lm, rng, int(count), margin)
            n = len(roots)
            if not n:
                continue
            edge = (roots[:, 2] - zc) / lm.h < self.hairline_v(lm, roots) + th.EDGE_BAND
            paths = self._trace_clamped(scalp, lm, roots, rng.uniform(lo, hi, n) * s, lift * s, seg,
                                        rng.uniform(0.4, 1.0, n) * rise * rise_k * s, G)
            th._emit(part, scalp, paths, rng.uniform(wlo, whi, n) * s * (1.0 - 0.1 * li), th._columns(rng, n, edge,
                                                                                                    li == 2),
                     rng, 0.25, self._mats(rng, n))

    def build(self, lm, scalp) -> Part:
        part = Part("HairHead")
        rng = np.random.default_rng([self.seed, 0])
        s = lm.h / 0.222
        p = self.p
        G = self._gather(lm)
        lo, hi = p.get("length_m", [0.02, 0.04])
        if self.kind == "wrap":
            self.hairline_row(part, scalp, lm, rng, int(p.get("hairline_cards", 60)), tuple(p.get("hairline_m", (0.02, 0.035))))
        elif self.kind in ("short", "cropped") and p.get("tufts"):
            self.tuft_layers(part, scalp, lm, rng, G, s)
        elif self.kind in ("short", "cropped"):
            seg = 1 if self.kind == "cropped" else 3
            self.hairline_row(part, scalp, lm, rng, int(p.get("hairline_cards", 0)), (0.5 * lo, 0.8 * lo))
            layers = [(0.0010, p["scalp_cards"][0], (0.0035, 0.006), 0.0010),
                      (0.0026, p["scalp_cards"][1], (0.0035, 0.006), 0.0018),
                      (0.0042, p["scalp_cards"][2], (0.003, 0.005), 0.0030)]
            for li, (lift, count, wr, rise) in enumerate(layers):
                roots = self._roots_inside(scalp, lm, rng, int(count), 0.008 + 0.006 * li)
                n = len(roots)
                if not n:
                    continue
                rise_k = float(p.get("rise", 1.0))
                paths = self._trace_clamped(scalp, lm, roots, rng.uniform(lo, hi, n) * s * (1.0 + 0.15 * li), lift * s,
                                            seg, rng.uniform(0.4, 1.0, n) * rise * rise_k * s, G)
                slots = rng.integers(SLOTS_FULL, size=n) if li < 2 else rng.choice(SLOTS_SPARSE, n)
                v_rng = CARD_V if self.kind == "cropped" else (0.15, 0.95)
                widths = rng.uniform(*wr, n) * s
                mats = self._mats(rng, n)
                widths, slots, u_rng = self._grey_strands(widths, slots, mats,
                                                          CARD_U if self.kind == "cropped" else (0.1, 0.9))
                if isinstance(u_rng, list) and self.kind == "cropped":  # a cropped strand: more of the column
                    v_rng = [GREY_V_CROPPED if u == GREY_U else v_rng for u in u_rng]
                _emit(part, scalp, paths, widths, slots, rng, 0.45, v_rng, mats, 0.3, u_rng)
        elif self.kind == "bun":
            self.hairline_row(part, scalp, lm, rng, int(p.get("hairline_cards", 70)), (0.03, 0.05))
            bun_r = float(p.get("bun_r_m", 0.034)) * s
            layers = [(0.0012, p["scalp_cards"][0], (0.007, 0.011)), (0.0030, p["scalp_cards"][1], (0.006, 0.010)),
                      (0.0048, p["scalp_cards"][2], (0.004, 0.007))]
            for li, (lift, count, wr) in enumerate(layers):
                roots = self._roots_inside(scalp, lm, rng, int(count), 0.006 + 0.008 * li)
                n = len(roots)
                if not n:
                    continue
                dist = np.linalg.norm(roots - G, axis=1)
                paths = self._trace_to(scalp, lm, roots, dist * 1.3, lift * s, G, 7, bun_r * 0.8)
                slots = rng.integers(SLOTS_FULL, size=n) if li < 2 else rng.choice(SLOTS_SPARSE, n)
                widths = rng.uniform(*wr, n) * s
                mats = self._mats(rng, n)
                widths, slots, u_rng = self._grey_strands(widths, slots, mats, (0.05, 0.95))
                _emit(part, scalp, paths, widths, slots, rng, 0.25, (0.0, 0.9), mats, 0.15, u_rng)
            part.extend(self.bun(lm, scalp, rng, G, bun_r))
        part.C = [STILL] * len(part.V)
        return part

    def bun(self, lm, scalp, rng, G: np.ndarray, r: float) -> Part:
        """The knot: coiled ribbons wound round a ball sitting on the back of the head at G."""
        part = Part("HairBun")
        s = lm.h / 0.222
        n0 = scalp.normal(scalp.project(G[None, :]))[0]
        c = scalp.project(G[None, :])[0] + n0 * r * 0.75
        n_rib = int(self.p.get("bun_ribbons", 30))
        pts_n = 18
        for k in range(n_rib):
            # a great-ish circle on the ball, tilted at random, a little inside at its ends (tucked)
            ax = rng.normal(size=3)
            ax /= np.linalg.norm(ax)
            e1 = np.cross(ax, n0)
            if np.linalg.norm(e1) < 1e-3:
                e1 = np.cross(ax, np.array([1.0, 0.0, 0.0]))
            e1 /= np.linalg.norm(e1)
            e2 = np.cross(ax, e1)
            a0 = rng.uniform(0, 2 * math.pi)
            span = rng.uniform(1.3, 2.0) * math.pi
            t = np.linspace(0.0, 1.0, pts_n)
            ang = a0 + span * t
            lat = rng.uniform(-0.55, 0.55) + 0.15 * np.sin(2 * math.pi * t)
            dirs = (np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2) * np.cos(lat)[:, None] + \
                ax * np.sin(lat)[:, None]
            rr = r * (1.0 + 0.06 * (k % 3) / 2.0) * (1.0 - 0.15 * np.sin(math.pi * t) ** 8)
            pts = c + dirs * rr[:, None]
            nrm = dirs
            mat = self._mats(rng, 1)[0]
            _ribbon(part, pts, nrm, float(rng.uniform(0.012, 0.018) * s), int(rng.integers(SLOTS_FULL)), _still,
                    taper=0.2, v_range=(0.1, 0.9), mat=mat, u_range=(0.05, 0.95))
        return part


def style(params: dict) -> HairStyle:
    return HairStyle(params)
