"""Stand-in trees for the Haluna mood test (PLACEHOLDER: the vegetation stream builds the real ones).

haluna.md §1.3 lists a hero banyan at the chapel court and windbreak-tree rows behind the houses,
but neither exists yet (vegetation.md: "Not built: windbreak tree, ... hero banyan"). H07 is framed by
the banyan's aerial roots, and H01/H02 need the windbreak rows' dark value masses, so these two are
made here as honest stand-ins: real geometry and real shading (the vegetation foliage and bark
shaders), but a cluster-card crown, not leaf-level geometry. Both are tagged PLACEHOLDER in their
.glb node extras and in kit_manifest.json, and they are listed in haluna_mood_review.md.

  banyan_placeholder     14 m, a fused multi-stem trunk with buttresses, six spreading limbs, ~50
                         aerial roots (some reaching the ground and thickening into props), a 24 m
                         wide crown of foliage cluster cards
  windbreak_placeholder  8 m, a short trunk under a dense columnar crown (foliage_shadow-heavy)

Mesh channels follow the vegetation wind convention (vegetation.md): COLOR.r primary sway, .g
secondary, .b phase, .a flutter; UV2.x occlusion; UV2.y tint variation.
Cards map into the 2 x 2 `canopy_cluster` atlas painted by kit_textures.py.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_BARK = "kit_canopy_bark"
M_LEAF = "kit_canopy_leaf"
M_LEAF_DARK = "kit_canopy_leaf_dark"

TRI_BUDGET = {
    "banyan_placeholder": (16000, 2400),
    "windbreak_placeholder": (2600, 500),
}
REASONS = {
    "banyan_placeholder": "stand-in hero banyan (cluster-card crown); the vegetation stream builds the "
                          "real tree (haluna.md 1.3, vegetation.md 'Not built')",
    "windbreak_placeholder": "stand-in windbreak tree (cluster-card crown); the vegetation stream builds "
                             "the real tree (haluna.md 1.3)",
}

ATLAS_CELLS = 2


def _wind_col(n: int, primary: float, secondary: float, phase: float, flutter: float) -> np.ndarray:
    return np.tile(np.array([primary, secondary, phase, flutter]), (n, 1))


def _limb(mb: kc.MeshBuilder, pts: np.ndarray, r0: float, r1: float, sides: int, height: float, rng) -> None:
    pts = np.asarray(pts, float)
    radii = np.linspace(r0, r1, len(pts))
    start = mb.vertex_count
    kc.tube(mb, pts, radii, sides, mb.material(M_BARK), variation=float(rng.random()), v_scale=1.0 / 0.9,
            u_repeat=max(1.0, r0 * 6.0), cap_end=True)
    p = np.asarray(mb.pos[start:])
    # Wind: the trunk does not sway; limbs bend a little by height; occlusion darker low down.
    frac = np.clip(p[:, 1] / height, 0, 1)
    col = np.column_stack([0.25 * frac ** 1.6, 0.15 * frac, np.full(len(p), rng.random()), np.zeros(len(p))])
    mb.col[start:] = col.tolist()
    uv2 = np.column_stack([0.55 + 0.45 * frac, frac])
    mb.uv2[start:] = uv2.tolist()


def _cards(mb: kc.MeshBuilder, centers: np.ndarray, crown_c: np.ndarray, sizes: np.ndarray, height: float, rng,
           mat_name: str) -> None:
    mat = mb.material(mat_name)
    for c, s in zip(centers, sizes):
        out = kc.normalize(c - crown_c + np.array([0.0, 0.6, 0.0]))
        # Card plane faces roughly outward, randomly rolled and tilted.
        n = kc.normalize(out + rng.normal(0, 0.45, 3))
        t = kc.any_perpendicular(n)
        b = np.cross(n, t)
        roll = rng.uniform(0, 2 * math.pi)
        t, b = t * math.cos(roll) + b * math.sin(roll), b * math.cos(roll) - t * math.sin(roll)
        corners = np.array([c - t * s - b * s, c + t * s - b * s, c + t * s + b * s, c - t * s + b * s])
        cell = int(rng.integers(0, ATLAS_CELLS * ATLAS_CELLS))
        cu, cv = (cell % ATLAS_CELLS) / ATLAS_CELLS, (cell // ATLAS_CELLS) / ATLAS_CELLS
        k = 1.0 / ATLAS_CELLS
        uv = np.array([[cu, cv + k], [cu + k, cv + k], [cu + k, cv], [cu, cv]])
        # Shading normal: out of the crown (the clump shades as one mass, vegetation.md).
        sn = kc.normalize(out * 0.75 + n * 0.25)
        depth = np.linalg.norm((c - crown_c) / np.array([1.0, 0.7, 1.0]))
        ao = float(np.clip(0.35 + depth / max(np.linalg.norm(crown_c), 1.0) * 0.5, 0.3, 1.0))
        frac = float(np.clip(c[1] / height, 0, 1))
        col = _wind_col(4, 0.25 * frac ** 1.6, 0.6, float(rng.random()), 0.7)
        uv2 = np.tile(np.array([ao, rng.random()]), (4, 1))
        base = mb.add_vertices(corners, np.tile(sn, (4, 1)), uv, uv2, col)
        mb.add_tri(base, base + 1, base + 2, mat)
        mb.add_tri(base, base + 2, base + 3, mat)


def build_banyan(seed: int = 91, *, height: float = 14.0, crown_radius: float = 12.0, limbs: int = 6,
                 roots: int = 96, cards: int = 700) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("banyan_placeholder", seed)
    out = []
    for lod in (False, True):
        r = kc.rng_for("banyan_placeholder", seed)  # same tree for both LODs
        mb = kc.MeshBuilder("banyan_placeholder" + ("-lod1" if lod else ""))
        sides = 6 if lod else 10
        # Fused stems twisting up to 4.5 m.
        for k in range(5 if not lod else 3):
            a0 = 2 * math.pi * k / 5 + r.uniform(-0.3, 0.3)
            t = np.linspace(0, 1, 7)
            rr = 0.9 * (1 - t) + 0.35
            pts = np.stack([np.cos(a0 + t * 1.2) * rr, t * 4.8, np.sin(a0 + t * 1.2) * rr], axis=-1)
            pts[0] += np.array([math.cos(a0) * 0.6, -0.3, math.sin(a0) * 0.6])  # buttress flare
            _limb(mb, pts, 0.75, 0.45, sides, height, r)
        # Limbs and their tips (crown anchor points).
        tips = []
        for k in range(limbs):
            a = 2 * math.pi * (k + r.uniform(-0.2, 0.2)) / limbs
            reach = crown_radius * r.uniform(0.6, 0.85)
            t = np.linspace(0, 1, 8)
            pts = np.stack([np.cos(a) * reach * t ** 0.9, 4.6 + (height - 6.5) * (t ** 0.6) * (1 - 0.45 * t),
                            np.sin(a) * reach * t ** 0.9], axis=-1)
            pts += r.normal(0, 0.25, pts.shape) * t[:, None]
            _limb(mb, pts, 0.42, 0.08, sides, height, r)
            tips.append(pts)
        limb_pts = np.concatenate(tips)
        # Aerial roots hanging from the limbs; long ones reach the ground and thicken (prop roots).
        n_roots = roots if not lod else roots // 3
        for k in range(n_roots):
            src = limb_pts[r.integers(2, len(limb_pts))]
            top = src + np.array([0.0, -0.2, 0.0])
            reach_ground = r.random() < 0.3
            length = top[1] if reach_ground else top[1] * r.uniform(0.25, 0.8)
            m = 4 if lod else 6
            yy = np.linspace(0, 1, m)
            sway = r.normal(0, 0.08, (m, 3)) * yy[:, None]
            sway[:, 1] = 0.0
            pts = top + np.stack([np.zeros(m), -length * yy, np.zeros(m)], axis=-1) + sway
            r0 = r.uniform(0.025, 0.07)
            r1 = r0 * (2.0 if reach_ground else 0.5)
            _limb(mb, pts, r0, r1, 4 if lod else 5, height, r)
        # Crown cards around limb ends, in a flattened dome.
        crown_c = np.array([0.0, height - 3.0, 0.0])
        n_cards = cards if not lod else cards // 4
        cen = []
        for _k in range(n_cards):
            a = r.uniform(0, 2 * math.pi)
            rad = crown_radius * math.sqrt(r.random())
            y = height - 1.5 - 4.0 * (rad / crown_radius) ** 2 + r.normal(0, 0.9)
            cen.append([math.cos(a) * rad, y, math.sin(a) * rad])
        cen = np.asarray(cen)
        sizes = r.uniform(1.1, 1.9, n_cards) * (1.0 if not lod else 1.7)
        _cards(mb, cen, crown_c, sizes, height, r, M_LEAF)
        out.append(mb)
    del rng
    return out


def build_windbreak(seed: int = 92, *, height: float = 8.0, radius: float = 1.6, cards: int = 260) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        r = kc.rng_for("windbreak_placeholder", seed)
        mb = kc.MeshBuilder("windbreak_placeholder" + ("-lod1" if lod else ""))
        t = np.linspace(0, 1, 5)
        trunk = np.stack([r.normal(0, 0.05, 5), t * height * 0.55, r.normal(0, 0.05, 5)], axis=-1)
        _limb(mb, trunk, 0.18, 0.08, 5 if lod else 7, height, r)
        n_cards = cards if not lod else cards // 4
        cen = []
        for _k in range(n_cards):
            y = r.uniform(1.6, height - 0.3)
            prof = math.sin(math.pi * min(1.0, (y - 1.2) / (height - 1.0))) ** 0.7
            a = r.uniform(0, 2 * math.pi)
            rad = radius * prof * math.sqrt(r.uniform(0.15, 1.0))
            cen.append([math.cos(a) * rad, y, math.sin(a) * rad])
        cen = np.asarray(cen)
        sizes = r.uniform(0.8, 1.3, n_cards) * (1.0 if not lod else 1.6)
        _cards(mb, cen, np.array([0.0, height * 0.55, 0.0]), sizes, height, r, M_LEAF_DARK)
        out.append(mb)
    return out


TARGETS = {"banyan_placeholder": build_banyan, "windbreak_placeholder": build_windbreak}
