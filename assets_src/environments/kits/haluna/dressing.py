"""Haluna set dressing (M3-ENV-701, the human's playtest "parts look primitive"). Pure numpy.

The lived-in clutter between the houses, along the tide-walls, on the dock and at the shrine:

  crate_stack       three slatted timber crates (two on the sand, one on top, turned), rope-bound
  rope_coil         a flat coil of hemp rope on the ground with its tail run out
  laundry_line      two forked poles 4 m apart, a sagging line, five cloths pegged on it (each cloth its
                    own dye slot, so a placement can re-dye them: kit_cloth / _indigo / _sea_blue)
  net_heap          a heaped fishing net drying on the sand, two floats caught in it
  shrine_offering   a low coral-stone step with frangipani heads, shells, two clay bowls and leaf-boats,
                    under a carved tide-post with a fan-shell disc and two swags of blooms
  tide_debris       a bleached driftwood log, a split plank, a kelp wrack line and shells, as the tide
                    leaves them at the strand line
  cargo_sacks       four woven sacks slumped against each other on a pallet of planks
  woodpile          split firewood stacked between stakes under a lean-to of planks
  pot_plants        three clay pots with fans of strap leaves, by a doorstep
  yard_fence        a 2 m run of low fence: two lashed posts, rails and a woven reed panel (front +Z)
  village_litter    the ground scatter's meshes, one material each, no LODs (the dresser's `scatter`
                    MultiMeshes): frond_dry, coconut_husk, shell_scatter, pebble_cluster

Origins on the ground plane, +Y up; the front of a piece faces +Z. LOD1 keeps the silhouette only
(these are seen up close: the dresser's `prop_lod_end_m` culls them at 60-120 m).
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc
import props

M_TIMBER = "kit_timber"
M_LASHING = "kit_lashing"
M_WOVEN = "kit_woven_panel"
M_NET = "kit_net"
M_GLASS = "kit_salt_glass"
M_STONE = "kit_coral_stone"
M_CLAY = "kit_earthenware"
M_GARLAND = "kit_garland"
M_GARLAND_THROAT = "kit_garland_throat"
M_NACRE = "kit_nacre"
M_LEAF = "kit_leaf_boat"
M_DRIFT = "kit_driftwood"
M_KELP = "kit_kelp"
M_CARVED = "kit_carved_wood"
M_FROND = "kit_dry_frond"
# Five cloth slots: the dresser maps each to its own .tres, so one placement can re-dye any of them.
CLOTHS = ("kit_cloth_sand", "kit_cloth_indigo", "kit_cloth_sea_blue", "kit_cloth_sand", "kit_cloth_indigo")

TRI_BUDGET = {
    "crate_stack": (2600, 160),
    "rope_coil": (2200, 120),
    "laundry_line": (3600, 300),
    "net_heap": (2400, 200),
    "shrine_offering": (4200, 300),
    "tide_debris": (3200, 240),
    "cargo_sacks": (3200, 300),
    "woodpile": (4000, 200),
    "pot_plants": (3000, 250),
    "yard_fence": (1400, 120),
    "village_litter": (900, 60),
}


def _crate(mb: kc.MeshBuilder, center, half, yaw: float, rng, noise, lod: bool) -> None:
    """A slatted crate: a dark core, horizontal slats on four sides, corner battens, a lid of boards."""
    rot = kc.rot_y(yaw)
    c = np.asarray(center, float)
    tm = mb.material(M_TIMBER)
    hx, hy, hz = half
    if lod:
        kc.rounded_block(mb, c, half, tm, rot=rot, seg=1, radius=0.01, variation=float(rng.random()))
        return
    kc.rounded_block(mb, c, (hx - 0.012, hy - 0.012, hz - 0.012), tm, rot=rot, seg=1, radius=0.01,
                     variation=float(rng.random()), wet_bias=0.2)
    slats = 3
    for side in range(4):
        a = side * math.pi * 0.5
        n = np.array([math.sin(a), 0.0, math.cos(a)])
        t = np.array([math.cos(a), 0.0, -math.sin(a)])
        ext_n = hz if side % 2 == 0 else hx
        ext_t = hx if side % 2 == 0 else hz
        for k in range(slats):
            y = -hy + (k + 0.5) * (2 * hy / slats)
            p0 = n * (ext_n + 0.004) - t * (ext_t - 0.03) + np.array([0, y, 0])
            p1 = n * (ext_n + 0.004) + t * (ext_t - 0.03) + np.array([0, y, 0])
            kc.plank(mb, c + rot @ p0, c + rot @ p1, 2 * hy / slats - 0.025, 0.018, tm, up=rot @ n,
                     variation=float(rng.random()), noise=noise)
        # Corner battens on this face's left edge.
        e = n * (ext_n + 0.012) - t * (ext_t - 0.02)
        kc.plank(mb, c + rot @ (e - [0, hy, 0]), c + rot @ (e + [0, hy, 0]), 0.045, 0.02, tm,
                 up=rot @ n, variation=float(rng.random()))
    for k in range(3):
        z = -hz + (k + 0.5) * (2 * hz / 3)
        kc.plank(mb, c + rot @ np.array([-hx, hy + 0.01, z]), c + rot @ np.array([hx, hy + 0.01, z]),
                 2 * hz / 3 - 0.02, 0.02, tm, variation=float(rng.random()), noise=noise)


def build_crate_stack(seed: int = 701) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("crate_stack", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("crate_stack" + ("-lod1" if lod else ""))
        _crate(mb, (-0.36, 0.3, 0.0), (0.32, 0.3, 0.3), 0.06, rng, noise, lod)
        _crate(mb, (0.34, 0.25, 0.04), (0.3, 0.25, 0.27), -0.12, rng, noise, lod)
        _crate(mb, (-0.2, 0.84, 0.02), (0.27, 0.24, 0.25), 0.42, rng, noise, lod)
        if not lod:
            # A rope binding the lower pair, and a coil thrown on the right crate's lid.
            band = np.array([[-0.7, 0.32, 0.31], [0.66, 0.28, 0.33], [0.66, 0.28, -0.25], [-0.7, 0.32, -0.32]])
            kc.tube(mb, np.vstack([band, band[:1]]), 0.012, 5, mb.material(M_LASHING), variation=0.4)
            _coil(mb, (0.36, 0.515, 0.04), 0.07, 0.16, 3, rng, lod=False)
        out.append(mb)
    return out


def _coil(mb: kc.MeshBuilder, at, r_in: float, r_out: float, turns_per_layer: int, rng, *, lod: bool,
          layers: int = 1, rope_r: float = 0.014) -> None:
    """A flat spiral of rope (and further layers stacked on it), around +Y at `at`."""
    at = np.asarray(at, float)
    steps = (14 if not lod else 6) * turns_per_layer
    pts = []
    for layer in range(layers):
        t = np.linspace(0.0, 1.0, steps)
        ang = t * turns_per_layer * 2 * math.pi + layer * 0.7
        r = r_in + (r_out - r_in) * (t if layer % 2 == 0 else 1.0 - t)
        y = rope_r + layer * rope_r * 1.8 + 0.002 * np.sin(ang * 3.0)
        pts.append(np.stack([np.cos(ang) * r, y, np.sin(ang) * r], axis=-1))
    kc.tube(mb, np.vstack(pts) + at, rope_r, 6 if not lod else 3, mb.material(M_LASHING),
            variation=float(rng.random()), u_repeat=4.0)


def build_rope_coil(seed: int = 702) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("rope_coil", seed)
        mb = kc.MeshBuilder("rope_coil" + ("-lod1" if lod else ""))
        _coil(mb, (0.0, 0.0, 0.0), 0.08, 0.3, 6 if not lod else 3, rng, lod=lod, layers=2 if not lod else 1,
              rope_r=0.018)
        if not lod:
            # The tail run out across the sand in a lazy S.
            t = np.linspace(0.0, 1.0, 14)
            tail = np.stack([0.3 + t * 1.1, np.full_like(t, 0.016), 0.25 * np.sin(t * math.pi * 1.6)], axis=-1)
            kc.tube(mb, tail, 0.018, 6, mb.material(M_LASHING), variation=0.6, u_repeat=4.0, cap_end=True)
        out.append(mb)
    return out


def _cloth(mb: kc.MeshBuilder, mat_name: str, x0: float, w: float, h: float, top_y, rng, noise, lod: bool) -> None:
    """One cloth pegged at its top edge (which follows the sagging line), hanging with a breeze ripple."""
    nu, nv = (3, 2) if lod else (7, 6)
    U, V = np.meshgrid(np.linspace(0.0, 1.0, nu), np.linspace(0.0, 1.0, nv))
    x = x0 + U * w
    y = top_y(x) - V * h
    z = 0.06 * V * np.sin(U * math.pi * 2.0 + rng.uniform(0, 6.28)) + 0.04 * V * V
    p = np.stack([x, y, z], axis=-1)
    if not lod:
        p[..., 2] += (noise.fbm(p / 0.4, 2) - 0.5) * 0.05 * V
    uv = np.stack([U * w, V * h], axis=-1)
    col = np.array([0.0, 0.0, 0.0, 0.15])
    uv2 = np.stack([np.full(U.shape, 0.92), np.full(U.shape, float(rng.random()))], axis=-1)
    m = mb.material(mat_name)
    kc.quad_strip(mb, p, m, uv=uv, col=col, uv2=uv2)
    kc.quad_strip(mb, p + np.array([0.0, 0.0, -0.004]), m, uv=uv, col=col, uv2=uv2 * np.array([0.7, 1.0]), flip=True)


def build_laundry_line(seed: int = 703, *, span: float = 4.0, h: float = 2.1, sag: float = 0.22) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("laundry_line", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("laundry_line" + ("-lod1" if lod else ""))
        lm = mb.material(M_LASHING)
        for sx in (-0.5, 0.5):
            x = sx * span
            kc.tube(mb, np.array([[x, -0.3, 0.0], [x + sx * 0.05, h + 0.12, 0.0]]), 0.04, 5 if lod else 7,
                    mb.material(M_TIMBER), variation=0.3 + sx, cap_end=True)
            if not lod:
                # The fork at the top the line rests in.
                for f in (-1, 1):
                    kc.tube(mb, np.array([[x + sx * 0.05, h + 0.05, 0.0], [x + sx * 0.05, h + 0.24, f * 0.08]]),
                            0.015, 4, mb.material(M_TIMBER), cap_end=True)

        def top_y(x):
            s = np.asarray(x) / span + 0.5
            return h - sag * 4.0 * s * (1.0 - s)

        t = np.linspace(-0.5, 0.5, 13 if not lod else 5) * span
        kc.tube(mb, np.stack([t, top_y(t), np.zeros_like(t)], axis=-1), 0.006, 3 if lod else 4, lm, variation=0.5)
        x = -span * 0.5 + 0.25
        for k, mat_name in enumerate(CLOTHS):
            w = rng.uniform(0.45, 0.75)
            hh = rng.uniform(0.55, 0.95) if k != 2 else 0.4
            _cloth(mb, mat_name, x, w, hh, top_y, rng, noise, lod)
            if not lod:
                for px in (x + 0.06, x + w - 0.06):
                    py = float(top_y(px))
                    kc.rounded_block(mb, (px, py - 0.02, 0.0), (0.008, 0.035, 0.012), mb.material(M_TIMBER),
                                     seg=1, radius=0.003, variation=0.7)
            x += w + rng.uniform(0.08, 0.2)
            if x > span * 0.5 - 0.5:
                break
        out.append(mb)
    return out


def build_net_heap(seed: int = 704) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("net_heap", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("net_heap" + ("-lod1" if lod else ""))
        n = 15 if not lod else 6
        U, V = np.meshgrid(np.linspace(-1.0, 1.0, n), np.linspace(-1.0, 1.0, n))
        rr = np.sqrt(U * U + V * V)
        x, z = U * 1.0, V * 0.75
        # A lumpy mound of folds, flattening into a skirt that lies on the sand.
        fold = 0.08 * np.sin(U * 7.0 + V * 2.0) * np.clip(1.0 - rr, 0.0, 1.0)
        y = 0.38 * np.clip(1.0 - rr, 0.0, 1.0) ** 1.6 + fold + 0.015
        p = np.stack([x, y, z], axis=-1)
        if not lod:
            p[..., 1] += (noise.fbm(p / 0.3, 2) - 0.5) * 0.06 * np.clip(1.0 - rr, 0.0, 1.0)
        uv = np.stack([x, z], axis=-1) * 1.4
        col = np.array([0.0, 0.0, 0.0, 0.3])
        uv2 = np.stack([np.full(U.shape, 0.8), np.full(U.shape, float(rng.random()))], axis=-1)
        nm = mb.material(M_NET)
        kc.quad_strip(mb, p, nm, uv=uv, col=col, uv2=uv2)
        # A second, smaller fold laid over (the net reads thick, not one sheet).
        kc.quad_strip(mb, p * np.array([0.7, 1.12, 0.65]) + np.array([0.12, 0.0, 0.05]), nm, uv=uv * 1.1, col=col,
                      uv2=uv2)
        if not lod:
            for c in ((0.35, 0.22, 0.2), (-0.45, 0.12, -0.3)):
                r = 0.07
                ang = np.linspace(-math.pi * 0.5, math.pi * 0.5, 7)
                prof = np.stack([np.maximum(np.cos(ang) * r, 0.002), np.sin(ang) * r], axis=-1)
                props.lathe(mb, prof, M_GLASS, rng, sides=12, at=c, cap_start=False)
            _coil(mb, (0.95, 0.0, 0.55), 0.05, 0.18, 3, rng, lod=False)
        out.append(mb)
    return out


def _bloom(mb: kc.MeshBuilder, c, nrm, r: float, rng, petals: int = 5) -> None:
    """A frangipani head: five petals in a star, a warm throat."""
    t1 = kc.any_perpendicular(nrm)
    t2 = np.cross(nrm, t1)
    ring = []
    for j in range(petals * 2):
        a = 2 * math.pi * j / (petals * 2) + rng.uniform(0, 0.2)
        rr = r if j % 2 == 0 else r * 0.42
        ring.append(c + (t1 * math.cos(a) + t2 * math.sin(a)) * rr + nrm * (0.006 if j % 2 == 0 else 0.0))
    ring = np.asarray(ring)
    base = mb.add_vertices(np.vstack([c + nrm * 0.004, ring]), np.tile(nrm, (len(ring) + 1, 1)),
                           np.vstack([[0.5, 0.5], (ring[:, [0, 2]] - c[[0, 2]]) / (2 * r) + 0.5]),
                           np.tile([0.9, 0.5], (len(ring) + 1, 1)), np.tile([0.0, 0.0, 0.0, 0.0], (len(ring) + 1, 1)))
    throat = mb.material(M_GARLAND_THROAT)
    petal = mb.material(M_GARLAND)
    m = len(ring)
    for j in range(m):
        mb.add_tri(base, base + 1 + j, base + 1 + (j + 1) % m, throat if j % 2 else petal)


def _shell(mb: kc.MeshBuilder, c, r: float, yaw: float, rng, lod: bool) -> None:
    """A cowrie-ish shell: a squashed half-ellipsoid."""
    sides = 10 if not lod else 5
    ang = np.linspace(0.0, math.pi * 0.5, 4 if not lod else 2)
    prof = np.stack([np.maximum(np.cos(ang) * r, 0.002), np.sin(ang) * r * 0.6], axis=-1)
    tmp = kc.MeshBuilder("shell")
    props.lathe(tmp, prof, M_NACRE, rng, sides=sides, cap_start=False)
    mb.merge(tmp, kc.rot_y(yaw) @ np.diag([1.0, 1.0, 0.62]), offset=c)


def build_shrine_offering(seed: int = 705) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_offering", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_offering" + ("-lod1" if lod else ""))
        sm = mb.material(M_STONE)
        # The step: two dressed coral blocks, the upper set back.
        kc.rounded_block(mb, (0.0, 0.11, 0.0), (0.6, 0.11, 0.32), sm, seg=1 if lod else 3, radius=0.03,
                         noise=None if lod else noise, disp_m=0.01, variation=0.3)
        kc.rounded_block(mb, (0.0, 0.3, -0.1), (0.42, 0.08, 0.2), sm, seg=1 if lod else 3, radius=0.03,
                         noise=None if lod else noise, disp_m=0.01, variation=0.6)
        top = 0.38
        # Two clay bowls of water on the upper step; leaf-boats with blooms on the lower.
        for bx in (-0.22, 0.2):
            props.lathe(mb, [(0.05, 0.0), (0.1, 0.03), (0.12, 0.07), (0.115, 0.075)], M_CLAY, rng,
                        sides=14 if not lod else 6, at=(bx, top, -0.1))
        blooms = 0 if lod else 9
        for k in range(blooms):
            c = np.array([rng.uniform(-0.5, 0.5), 0.225, rng.uniform(0.05, 0.27)])
            _bloom(mb, c, kc.normalize(np.array([rng.normal(0, 0.25), 1.0, rng.normal(0, 0.25)])),
                   rng.uniform(0.035, 0.045), rng)
        for k in range(3 if not lod else 1):
            # A leaf-boat: a folded leaf as a shallow V-trough, pointed at both ends.
            cx = -0.35 + 0.35 * k
            t = np.linspace(-1.0, 1.0, 7 if not lod else 3)
            w = 0.07 * np.sqrt(np.clip(1 - t * t, 0, 1)) + 0.004
            spine = np.stack([cx + t * 0.14, np.full_like(t, 0.228) + 0.02 * t * t, np.full_like(t, 0.16)], axis=-1)
            grid = np.stack([spine + np.stack([np.zeros_like(t), 0.04 * w / 0.07, -w], -1), spine,
                             spine + np.stack([np.zeros_like(t), 0.04 * w / 0.07, w], -1)], axis=1)
            uv = np.stack([np.tile([0.0, 0.5, 1.0], (len(t), 1)), np.tile((t[:, None] + 1) * 0.5, (1, 3))], axis=-1)
            for flip in (False, True):
                kc.quad_strip(mb, grid, mb.material(M_LEAF), uv=uv, col=np.array([0.0, 0.1, 0.0, 0.2]),
                              uv2=np.array([0.9, float(rng.random())]), flip=flip)
            if not lod:
                _bloom(mb, spine[len(t) // 2] + [0, 0.02, 0], np.array([0.0, 1.0, 0.0]), 0.04, rng)
        for k in range(6 if not lod else 0):
            _shell(mb, (rng.uniform(-0.38, 0.38), top, rng.uniform(-0.22, 0.05)), rng.uniform(0.025, 0.04),
                   rng.uniform(0, 6.28), rng, lod)
        # The tide-post behind it (the silhouette that reads from the lane): a carved post with a fan-shell
        # disc at its head facing the step, and two strings of blooms swagged from it to the step's ends.
        post_top = np.array([0.0, 1.75, -0.24])
        kc.tube(mb, np.array([[0.0, 0.3, -0.24], [0.0, 1.0, -0.24], post_top]), np.array([0.075, 0.065, 0.055]),
                8 if not lod else 5, mb.material(M_CARVED), noise=None if lod else noise, disp_m=0.006,
                cap_end=True, variation=0.4)
        # A scallop fan (the wake-shell's sign): ribbed, cupped towards the step, hinged at the post's head.
        na, nr = (17, 5) if not lod else (7, 2)
        A, R = np.meshgrid(np.linspace(-1.25, 1.25, na), np.linspace(0.03, 0.34, nr))
        ribs = 0.016 * np.abs(np.sin(A * 6.0)) * (R / 0.34) if not lod else 0.0
        fan = np.stack([np.sin(A) * R, np.cos(A) * R - 0.06, 0.05 + 0.06 * (R / 0.34) ** 2 + ribs], axis=-1)
        fan = fan + post_top
        uv = np.stack([A * 0.3 + 0.5, R / 0.34], axis=-1)
        for flip in (False, True):
            kc.quad_strip(mb, fan + (np.array([0.0, 0.0, -0.006]) if flip else 0.0), mb.material(M_NACRE), uv=uv,
                          col=np.array([0.0, 0.3, 0.0, 0.3]), uv2=np.array([0.9, 0.5]), flip=not flip)
        if not lod:
            for sx in (-1.0, 1.0):
                t = np.linspace(0.0, 1.0, 9)
                a = post_top + np.array([0.0, -0.32, 0.05])
                b = np.array([sx * 0.56, 0.24, 0.2])
                cord = a[None, :] * (1 - t)[:, None] + b[None, :] * t[:, None]
                cord[:, 1] -= 0.22 * np.sin(t * math.pi)
                kc.tube(mb, cord, 0.008, 4, mb.material(M_LASHING), variation=0.5)
                for c in cord[1:-1]:
                    for _ in range(2):
                        _bloom(mb, c + rng.normal(0, 0.015, 3),
                               kc.normalize(rng.normal(0, 1, 3) + np.array([0.0, 0.0, 0.8])), 0.034, rng)
        out.append(mb)
    return out


def build_woodpile(seed: int = 708) -> list[kc.MeshBuilder]:
    """Split firewood stacked between two pairs of stakes, a short lean-to plank roof over it."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("woodpile", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("woodpile" + ("-lod1" if lod else ""))
        tm = mb.material(M_TIMBER)
        dm = mb.material(M_DRIFT)
        w, depth = 1.6, 0.55
        if lod:
            kc.rounded_block(mb, (0.0, 0.42, 0.0), (w * 0.5, 0.42, depth * 0.5), dm, seg=1, radius=0.05)
        else:
            rows = 6
            for r in range(rows):
                n = 9 - (r % 2)
                for k in range(n):
                    x = -w * 0.5 + 0.09 + (k + 0.5 * (r % 2)) * (w - 0.18) / 8.0
                    rad = rng.uniform(0.055, 0.075)
                    y = 0.07 + r * 0.135 + rng.normal(0, 0.008)
                    z0, z1 = -depth * 0.5 + rng.normal(0, 0.03), depth * 0.5 + rng.normal(0, 0.03)
                    kc.tube(mb, np.array([[x, y, z0], [x, y, z1]]), rad, 6, dm, cap_start=True, cap_end=True,
                            variation=float(rng.random()), first_normal=np.array([0.0, 1.0, 0.0]))
        for sx in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                kc.tube(mb, np.array([[sx * (w * 0.5 + 0.05), -0.2, sz * depth * 0.4],
                                      [sx * (w * 0.5 + 0.05), 1.0 + 0.25 * (sz < 0), sz * depth * 0.4]]),
                        0.035, 5 if not lod else 4, tm, cap_end=True, variation=0.5)
        for k in range(4 if not lod else 1):
            z = -depth * 0.55 + k * (depth * 1.1 / 3.0) if not lod else 0.0
            kc.plank(mb, (-w * 0.5 - 0.2, 1.2 - 0.25 * (z + depth * 0.55) / (depth * 1.1), z),
                     (w * 0.5 + 0.2, 1.2 - 0.25 * (z + depth * 0.55) / (depth * 1.1), z),
                     0.2 if not lod else 0.8, 0.025, tm, variation=float(rng.random()), noise=None if lod else noise)
        out.append(mb)
    return out


def build_pot_plants(seed: int = 709) -> list[kc.MeshBuilder]:
    """Three clay pots by a doorstep, each with a fan of strap leaves (a young pandanus, two lilies)."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("pot_plants", seed)
        mb = kc.MeshBuilder("pot_plants" + ("-lod1" if lod else ""))
        lm = mb.material(M_LEAF)
        for (px, pz, h, leaves, leaf_len) in ((-0.32, 0.0, 0.42, 9, 0.75), (0.18, 0.1, 0.3, 7, 0.5),
                                               (0.42, -0.22, 0.24, 6, 0.4)):
            props.lathe(mb, [(h * 0.32, 0.0), (h * 0.42, h * 0.55), (h * 0.5, h * 0.92), (h * 0.53, h)], M_CLAY, rng,
                        sides=14 if not lod else 6, at=(px, 0.0, pz))
            for k in range(leaves if not lod else 3):
                a = 2 * math.pi * k / leaves + rng.uniform(-0.2, 0.2)
                tilt = rng.uniform(0.25, 0.9)
                ln = leaf_len * rng.uniform(0.75, 1.1)
                d = np.array([math.cos(a) * math.sin(tilt), math.cos(tilt), math.sin(a) * math.sin(tilt)])
                side = kc.normalize(np.cross(d, np.array([0.0, 1.0, 0.0])) + 1e-6)
                t = np.linspace(0.0, 1.0, 5 if not lod else 2)
                spine = np.array([px, h * 0.9, pz]) + np.outer(t * ln, d)
                spine[:, 1] -= 0.25 * ln * t ** 2 * math.sin(tilt)  # the leaf arches over under its weight
                wdt = (0.035 * (1.0 - t ** 2) + 0.004)[:, None]
                grid = np.stack([spine - side * wdt, spine + np.array([0.0, 0.01, 0.0]), spine + side * wdt], axis=1)
                uv = np.stack([np.tile([0.0, 0.5, 1.0], (len(t), 1)), np.tile(t[:, None], (1, 3))], axis=-1)
                for flip in (False, True):
                    kc.quad_strip(mb, grid, lm, uv=uv, col=np.array([0.0, 0.25, 0.0, 0.1]),
                                  uv2=np.array([0.9, float(rng.random())]), flip=flip)
        out.append(mb)
    return out


def build_tide_debris(seed: int = 706) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("tide_debris", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("tide_debris" + ("-lod1" if lod else ""))
        # The log: a bent, tapering trunk half-sunk in the sand, a root stub at the thick end.
        t = np.linspace(0.0, 1.0, 9 if not lod else 3)
        log = np.stack([-1.3 + t * 2.4, 0.09 + 0.05 * np.sin(t * math.pi), 0.18 * np.sin(t * 2.2)], axis=-1)
        kc.tube(mb, log, 0.16 - 0.08 * t, 9 if not lod else 5, mb.material(M_DRIFT), noise=None if lod else noise,
                disp_m=0.02, cap_start=True, cap_end=True, variation=0.4, weather=kc.DROWNED)
        if not lod:
            for a in (0.4, 2.0, 3.6, 5.0):
                root = np.array([[-1.3, 0.1, 0.0], [-1.45, 0.1 + 0.18 * math.sin(a), 0.18 * math.cos(a)],
                                 [-1.55, 0.05 + 0.25 * math.sin(a), 0.3 * math.cos(a)]])
                kc.tube(mb, root, np.array([0.06, 0.035, 0.012]), 5, mb.material(M_DRIFT), cap_end=True,
                        variation=0.5, weather=kc.DROWNED)
        # A split plank thrown up beside it.
        kc.plank(mb, (-0.4, 0.03, 0.55), (0.6, 0.05, 0.75), 0.16, 0.03, mb.material(M_DRIFT), variation=0.8,
                 noise=None if lod else noise, weather=kc.DROWNED)
        # The wrack line: kelp ribbons lying in a wavering band in front.
        km = mb.material(M_KELP)
        strands = 10 if not lod else 3
        for k in range(strands):
            x0 = rng.uniform(-1.6, 1.4)
            z0 = rng.uniform(-0.55, -0.2)
            ang = rng.uniform(-0.6, 0.6)
            ln = rng.uniform(0.5, 1.0)
            s = np.linspace(0.0, 1.0, 6 if not lod else 2)
            d = np.array([math.cos(ang), 0.0, math.sin(ang)])
            side = np.array([-d[2], 0.0, d[0]])
            spine = np.array([x0, 0.012, z0]) + np.outer(s * ln, d) + np.outer(0.06 * np.sin(s * 9.0 + k), side)
            w = (0.05 + 0.03 * np.sin(s * math.pi))[:, None]
            grid = np.stack([spine - side * w, spine + side * w], axis=1)
            grid[:, :, 1] += 0.01 * np.sin(s * 7.0)[:, None]
            uv = np.stack([np.tile([0.0, 1.0], (len(s), 1)), np.tile(s[:, None] * ln, (1, 2))], axis=-1)
            kc.quad_strip(mb, grid, km, uv=uv, col=np.array([0.0, 0.0, 0.6, 0.3]),
                          uv2=np.array([0.7, float(rng.random())]))
        for k in range(7 if not lod else 0):
            _shell(mb, (rng.uniform(-1.4, 1.2), 0.0, rng.uniform(-0.7, 0.9)), rng.uniform(0.02, 0.045),
                   rng.uniform(0, 6.28), rng, lod)
        out.append(mb)
    return out


def _sack(mb: kc.MeshBuilder, at, yaw: float, tilt: float, h: float, rng, noise, lod: bool) -> None:
    """A woven sack: a slumped, squarish lathe with a tied neck."""
    sides = 10 if not lod else 5
    tmp = kc.MeshBuilder("sack")
    prof = [(0.2, 0.0), (0.27, h * 0.15), (0.28, h * 0.55), (0.2, h * 0.85), (0.06, h * 0.97), (0.07, h * 1.08)]
    props.lathe(tmp, prof if not lod else prof[::2] + [prof[-1]], M_WOVEN, rng, sides=sides,
                noise=None if lod else noise, disp_m=0.015 if not lod else 0.0, cap_end=True)
    xf = kc.rot_y(yaw) @ kc.rot_z(tilt) @ np.diag([1.0, 1.0, 0.72])
    mb.merge(tmp, xf, offset=at)
    if not lod:
        neck = np.asarray(at, float) + xf @ np.array([0.0, h * 0.95, 0.0])
        ring = np.stack([np.cos(np.linspace(0, 2 * math.pi, 9)) * 0.07, np.zeros(9),
                         np.sin(np.linspace(0, 2 * math.pi, 9)) * 0.07], axis=-1)
        kc.tube(mb, ring @ xf.T + neck, 0.01, 4, mb.material(M_LASHING), variation=0.4)


def build_cargo_sacks(seed: int = 707) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("cargo_sacks", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("cargo_sacks" + ("-lod1" if lod else ""))
        tm = mb.material(M_TIMBER)
        # The pallet: three bearers and five deck boards.
        for z in (-0.4, 0.0, 0.4):
            kc.plank(mb, (-0.6, 0.04, z), (0.6, 0.04, z), 0.08, 0.08, tm, variation=float(rng.random()))
        for k in range(5 if not lod else 1):
            x = -0.48 + 0.24 * k
            kc.plank(mb, (x, 0.09, -0.48), (x, 0.09, 0.48), 0.2 if not lod else 1.2, 0.025, tm,
                     variation=float(rng.random()), noise=None if lod else noise)
        top = 0.1
        for at, yaw, tilt, h in (((-0.28, top, -0.2), 0.3, 0.06, 0.62), ((0.28, top, -0.22), -0.4, -0.1, 0.58),
                                 ((-0.25, top, 0.24), 1.2, 0.15, 0.5), ((0.3, top, 0.22), 2.0, -0.28, 0.55)):
            _sack(mb, at, yaw, tilt, h, rng, noise, lod)
        out.append(mb)
    return out


def build_yard_fence(seed: int = 710, *, length: float = 2.0, h: float = 0.95) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("yard_fence", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("yard_fence" + ("-lod1" if lod else ""))
        tm = mb.material(M_TIMBER)
        for x in (-length * 0.5, length * 0.5):
            kc.tube(mb, np.array([[x, -0.2, 0.0], [x + rng.normal(0, 0.01), h + 0.12, rng.normal(0, 0.01)]]),
                    0.04, 6 if not lod else 4, tm, cap_end=True, variation=float(rng.random()))
        for y in ((0.25, h - 0.08) if not lod else (h - 0.08,)):
            kc.plank(mb, (-length * 0.5 - 0.06, y, 0.03), (length * 0.5 + 0.06, y + rng.normal(0, 0.02), 0.03),
                     0.05, 0.035, tm, variation=float(rng.random()), noise=None if lod else noise, sag_m=0.01)
        # The woven reed panel, slightly bellied, with a ragged top edge.
        nu, nv = (9, 4) if not lod else (2, 2)
        U, V = np.meshgrid(np.linspace(0.0, 1.0, nu), np.linspace(0.0, 1.0, nv))
        x = (U - 0.5) * (length - 0.1)
        top = h - 0.04 + (0.03 * np.sin(U * 23.0) if not lod else 0.0)
        y = 0.08 + V * (top - 0.08)
        z = 0.012 * np.sin(U * math.pi) * np.sin(V * math.pi)
        p = np.stack([x, y, z], axis=-1)
        uv = np.stack([x, y], axis=-1) * 2.5  # a finer weave than the house infill (it is seen close)
        col = np.array([0.0, 0.0, 0.0, 0.25])
        uv2 = np.stack([np.full(U.shape, 0.9), np.full(U.shape, float(rng.random()))], axis=-1)
        wm = mb.material(M_WOVEN)
        kc.quad_strip(mb, p, wm, uv=uv, col=col, uv2=uv2)
        kc.quad_strip(mb, p - np.array([0.0, 0.0, 0.02]), wm, uv=uv, col=col, uv2=uv2, flip=True)
        if not lod:
            for x in (-length * 0.5, length * 0.5):
                for y in (0.25, h - 0.08):
                    ring = np.stack([np.cos(np.linspace(0, 2 * math.pi, 7)) * 0.05 + x, np.full(7, y),
                                     np.sin(np.linspace(0, 2 * math.pi, 7)) * 0.05], axis=-1)
                    kc.tube(mb, ring, 0.008, 3, mb.material(M_LASHING), variation=0.4)
        out.append(mb)
    return out


def _frond(mb: kc.MeshBuilder, rng, lod: bool = False) -> None:
    """A fallen, sun-browned palm frond lying on the sand: a curved rachis and two rows of leaflets."""
    fm = mb.material(M_FROND)
    t = np.linspace(0.0, 1.0, 9 if not lod else 3)
    ln = 2.2
    spine = np.stack([t * ln, 0.03 + 0.06 * np.sin(t * math.pi), 0.25 * np.sin(t * 1.3)], axis=-1)
    kc.tube(mb, spine, 0.035 * (1.0 - 0.8 * t) + 0.006, 4, fm, variation=0.5)
    n = 15 if not lod else 5
    for k in range(1, n):
        s = k / float(n)
        c = spine[0] * (1 - s) + spine[-1] * s
        c[2] = 0.25 * math.sin(s * 1.3)
        lf = 0.55 * math.sin(math.pi * (0.15 + 0.85 * s)) + 0.1
        for side in (-1.0, 1.0):
            a = side * (1.0 + rng.normal(0, 0.15))
            d = np.array([math.cos(a) * 0.45, 0.0, math.sin(a)])
            d = d / np.linalg.norm(d)
            tip = c + d * lf
            tip[1] = 0.01 + rng.uniform(0.0, 0.04)
            perp = np.array([-d[2], 0.0, d[0]]) * 0.025
            base = mb.add_vertices(np.array([c + perp, c - perp, tip]), np.tile([0.0, 1.0, 0.0], (3, 1)),
                                   np.array([[0, 0], [1, 0], [0.5, 1]]), np.tile([0.8, float(rng.random())], (3, 1)),
                                   np.tile([0.0, 0.0, 0.0, 0.2], (3, 1)))
            mb.add_tri(base, base + 2, base + 1, fm)  # kit_dry_frond is double-sided


def build_village_litter(seed: int = 711) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("village_litter", seed)
    noise = kc.Noise3(rng)
    frond = kc.MeshBuilder("frond_dry")
    _frond(frond, rng)
    # The kit's LOD1 rule wants one; the scatter draws only the LOD0 meshes and culls at its own range.
    frond_lod = kc.MeshBuilder("frond_dry-lod1")
    _frond(frond_lod, kc.rng_for("village_litter_lod", seed), lod=True)
    husk = kc.MeshBuilder("coconut_husk")
    # Two husk halves and a whole nut, lying where they fell.
    for (x, z, r, cut) in ((0.0, 0.0, 0.12, False), (0.3, 0.12, 0.11, True), (0.18, -0.25, 0.1, True)):
        ang = np.linspace(-math.pi * 0.5, (0.0 if cut else math.pi * 0.5), 6)
        prof = np.stack([np.maximum(np.cos(ang) * r, 0.002), np.sin(ang) * r * 1.1 + r], axis=-1)
        tmp = kc.MeshBuilder("h")
        props.lathe(tmp, prof, M_LASHING, rng, sides=10, cap_start=False, cap_end=cut, noise=noise, disp_m=0.008)
        rot = kc.rot_z(rng.uniform(1.2, 1.9)) if not cut else kc.rot_x(math.pi)
        off = (x, r * 0.9, z) if not cut else (x, r * 1.1 + 0.005, z)
        husk.merge(tmp, kc.rot_y(rng.uniform(0, 6.28)) @ rot, offset=off)
    shells = kc.MeshBuilder("shell_scatter")
    for k in range(9):
        _shell(shells, (rng.normal(0, 0.25), 0.0, rng.normal(0, 0.25)), rng.uniform(0.018, 0.04),
               rng.uniform(0, 6.28), rng, False)
    pebbles = kc.MeshBuilder("pebble_cluster")
    for k in range(6):
        r = rng.uniform(0.04, 0.11)
        kc.rounded_block(pebbles, (rng.normal(0, 0.22), r * 0.45, rng.normal(0, 0.22)), (r, r * 0.6, r * 0.8),
                         pebbles.material(M_STONE), rot=kc.rot_y(rng.uniform(0, 6.28)), seg=2, radius=r * 0.5,
                         noise=noise, disp_m=0.01, variation=float(rng.random()))
    return [frond, husk, shells, pebbles, frond_lod]


TARGETS = {
    "crate_stack": build_crate_stack,
    "rope_coil": build_rope_coil,
    "laundry_line": build_laundry_line,
    "net_heap": build_net_heap,
    "shrine_offering": build_shrine_offering,
    "tide_debris": build_tide_debris,
    "cargo_sacks": build_cargo_sacks,
    "woodpile": build_woodpile,
    "pot_plants": build_pot_plants,
    "yard_fence": build_yard_fence,
    "village_litter": build_village_litter,
}
