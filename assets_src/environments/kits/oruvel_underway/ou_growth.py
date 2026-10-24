"""The reef that grows on the drowned city (oruvel_underway.md §2, §3). Pure numpy; see ou_common.py.

  coral_head_a   a 2.4 m bommie on a slab of rubble: a brain-coral boulder (ochre), branching coral (a third bleached
                 bone-white), a plate coral, two sea fans and tube sponges
  coral_head_b   a lower 1.6 m head grown over a fallen block: rose boulder, plates, more of it bleached
  seagrass_patch a 3 x 3 m clump of ~240 strap blades (0.4-1.1 m) leaning with the current (+X), tips browned
  coral_curtain  a 3.0 x 2.8 m hanging mass across an opening (origin at the floor, centre; it hangs from y 2.8):
                 soft-coral ropes, fans, weed and sponges. The open shutter shows what is behind it
The reds go first under water: these colours read grey-teal past 3 m and come back inside the lantern's pool.
"""

from __future__ import annotations

import math

import numpy as np

import ou_common as oc

kc = oc.kc

TRI_BUDGET = {
    "coral_head_a": (9000, 700),
    "coral_head_b": (9000, 700),
    "seagrass_patch": (5000, 400),
    "coral_curtain": (6000, 400),
}
CURRENT = np.array([1.0, 0.0, 0.25])  # the set across the terrace: toward the east (seagrass leans with it)


def _boulder(mb: kc.MeshBuilder, center, radius, slot: str, rng, noise, *, squash: float = 0.75, seg: int = 7) -> None:
    """A massive coral: a displaced, squashed sphere (the texture carries the brain ridges)."""
    r = np.asarray(radius, float) * np.array([1.0, squash, 1.0])
    kc.rounded_block(mb, center, r, mb.material(slot), radius=float(r.min()), seg=seg, noise=noise,
                     disp_m=float(r.min()) * 0.28, disp_period_m=float(r.min()) * 0.7, weather=oc.REEF,
                     variation=float(rng.random()), rot=kc.rot_y(rng.uniform(0, 6.28)))


def _plate(mb: kc.MeshBuilder, center, radius: float, slot: str, rng, *, tilt: float = 0.12, tiers: int = 2) -> None:
    """Plate (table) coral: thin wavy discs in tiers on a short stem."""
    mat = mb.material(slot)
    c = np.asarray(center, float)
    kc.tube(mb, np.array([c - np.array([0, 0.25, 0]), c]), radius * 0.12, 6, mat, weather=oc.REEF)
    for k in range(tiers):
        rr = radius * (1.0 - 0.3 * k)
        y = c[1] + 0.06 * k
        rot = kc.rot_x(rng.uniform(-tilt, tilt)) @ kc.rot_z(rng.uniform(-tilt, tilt))
        rings, sectors = 4, 18
        a = np.linspace(0, 2 * math.pi, sectors + 1)
        rad = np.linspace(0.02, rr, rings)
        R, A = np.meshgrid(rad, a, indexing="ij")
        wav = 0.012 * np.sin(A * 5 + k) * (R / rr) + 0.025 * (R / rr) ** 2
        local = np.stack([R * np.cos(A), wav, R * np.sin(A)], axis=-1) @ rot.T
        grid = local + np.array([c[0], y, c[2]])
        oc.sheet(mb, grid, mat, variation=float(rng.random()))


def _sponges(mb: kc.MeshBuilder, at, rng, count: int) -> None:
    mat = mb.material(oc.M_SPONGE)
    for _k in range(count):
        p = np.asarray(at, float) + np.array([rng.uniform(-0.12, 0.12), 0.0, rng.uniform(-0.12, 0.12)])
        h = rng.uniform(0.12, 0.3)
        lean = np.array([rng.normal(0, 0.05), h, rng.normal(0, 0.05)])
        kc.tube(mb, np.array([p, p + lean * 0.5, p + lean]), np.array([0.035, 0.04, 0.045]), 8, mat, weather=oc.REEF,
                variation=float(rng.random()))
        oc.ring(mb, p + lean, 0.038, 0.009, mat, segs=10, sides=4)


def _rubble(mb: kc.MeshBuilder, rng, noise, extent: float, count: int) -> None:
    for _k in range(count):
        x, z = rng.uniform(-extent, extent, 2)
        s = rng.uniform(0.15, 0.4)
        oc.block(mb, (x, s * 0.25, z), (s, s * 0.5, s * rng.uniform(0.6, 1.0)), mb.material(oc.M_CONCRETE), rng=rng,
                 noise=noise, rot=kc.rot_y(rng.uniform(0, 3)) @ kc.rot_x(rng.uniform(-0.3, 0.3)), seg=2, disp_m=0.03)


def build_coral_head(name: str, seed: int, *, scale: float, boulder_slot: str, bleached: float) -> list[kc.MeshBuilder]:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name)
    s = scale
    # The rubble it grew on: a tilted slab end and blocks, mostly buried.
    oc.block(mb, (0.1 * s, 0.1 * s, -0.05 * s), (0.75 * s, 0.18 * s, 0.55 * s), mb.material(oc.M_CONCRETE), rng=rng,
             noise=noise, rot=kc.rot_z(0.18) @ kc.rot_y(0.4), seg=3, disp_m=0.04)
    _rubble(mb, rng, noise, 0.9 * s, 5)
    _boulder(mb, (0.0, 0.42 * s, 0.0), 0.62 * s, boulder_slot, rng, noise)
    for k in range(3):  # lobes: a massive coral grows in knuckles, not as one dome
        a = 2 * math.pi * k / 3 + rng.uniform(-0.4, 0.4)
        _boulder(mb, (math.cos(a) * 0.42 * s, 0.32 * s, math.sin(a) * 0.42 * s), rng.uniform(0.28, 0.4) * s,
                 boulder_slot, rng, noise, squash=0.8, seg=5)
    _boulder(mb, (0.55 * s, 0.2 * s, 0.35 * s), 0.3 * s, oc.M_CORAL_OCHRE if boulder_slot != oc.M_CORAL_OCHRE else
             oc.M_CORAL_ROSE, rng, noise, seg=5)
    # Branching coral thickets round the top and flanks, some bleached.
    for k in range(12):
        a = 2 * math.pi * k / 12 + rng.uniform(-0.25, 0.25)
        r = rng.uniform(0.15, 0.58) * s
        y = 0.42 * s + math.sqrt(max((0.62 * s) ** 2 - r ** 2, 0.0)) * 0.75 - 0.03
        slot = oc.M_CORAL_BONE if rng.random() < bleached else (oc.M_CORAL_ROSE if k % 2 else oc.M_CORAL_OCHRE)
        oc.branch_coral(mb, (math.cos(a) * r, y, math.sin(a) * r), rng, slot, height=rng.uniform(0.2, 0.34) * s,
                        depth=4 if k % 3 == 0 else 3, radius=0.024 * s)
    _plate(mb, (-0.55 * s, 0.55 * s, 0.25 * s), 0.38 * s, oc.M_CORAL_OCHRE if rng.random() > bleached else
           oc.M_CORAL_BONE, rng)
    for k in range(4):
        a = rng.uniform(0, 2 * math.pi)
        oc.sea_fan(mb, (math.cos(a) * 0.7 * s, 0.12 * s, math.sin(a) * 0.7 * s), rng, oc.M_CORAL_TEAL,
                   height=rng.uniform(0.5, 0.75) * s, width=rng.uniform(0.45, 0.6) * s, yaw=math.pi / 2 + 0.3 * k)
    _sponges(mb, (0.45 * s, 0.25 * s, -0.45 * s), rng, 3)
    for _k in range(8):
        a, r = rng.uniform(0, 2 * math.pi), rng.uniform(0.5, 0.9) * s
        oc.coral_knob(mb, (math.cos(a) * r, 0.1 * s, math.sin(a) * r), rng.uniform(0.05, 0.1) * s, rng, noise,
                      oc.CORALS[int(rng.integers(0, 5))])
    lod = kc.MeshBuilder(name + oc.LOD)
    kc.rounded_block(lod, (0, 0.42 * s, 0), (0.7 * s, 0.5 * s, 0.7 * s), lod.material(boulder_slot), radius=0.45 * s,
                     seg=2)
    kc.rounded_block(lod, (0.1 * s, 0.1 * s, 0), (0.8 * s, 0.15 * s, 0.6 * s), lod.material(oc.M_CONCRETE), seg=1,
                     radius=0.05)
    return [mb, lod]


def build_seagrass(seed: int = 803, *, blades: int = 240, half: float = 1.5) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("seagrass_patch", seed)
    out = []
    for suffix, n, segs in (("", blades, 5), (oc.LOD, 24, 2)):
        r = kc.rng_for("seagrass_patch" + suffix, seed)
        mb = kc.MeshBuilder("seagrass_patch" + suffix)
        grass, tip = mb.material(oc.M_SEAGRASS), mb.material(oc.M_SEAGRASS_TIP)
        lean_dir = kc.normalize(CURRENT)
        for _k in range(n):
            # Clumped: rhizome clusters, denser toward the middle, none at the patch edge.
            a = r.uniform(0, 2 * math.pi)
            rad = half * math.sqrt(r.random()) * 0.92
            x, z = math.cos(a) * rad, math.sin(a) * rad
            L = r.uniform(0.4, 1.1) * (1.0 - 0.35 * rad / half)
            w = r.uniform(0.014, 0.024) * (3.0 if suffix else 1.0)
            lean = r.uniform(0.25, 0.6)
            ldir = kc.normalize(lean_dir + np.array([r.normal(0, 0.25), 0.0, r.normal(0, 0.25)]))
            t = np.linspace(0.0, 1.0, segs + 1)
            pts = np.stack([x + ldir[0] * L * lean * t ** 1.6, L * t * (1.0 - 0.25 * lean * t),
                            z + ldir[2] * L * lean * t ** 1.6], axis=-1)
            side = kc.normalize(np.cross(ldir, kc.UP) + np.array([r.normal(0, 0.4), 0.0, r.normal(0, 0.4)]))
            mats = [grass] * (segs - 1) + [tip]
            oc.ribbon(mb, pts, w * (1.0 - 0.3 * t), side, mats, variation=float(r.random()))
        out.append(mb)
    del rng
    return out


def build_coral_curtain(seed: int = 804, *, width: float = 3.0, height: float = 2.8) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("coral_curtain", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("coral_curtain")
    top = height
    # Soft-coral ropes hanging from the lintel line, drooping and swaying with the current.
    for k in range(26):
        x = -width * 0.5 + width * (k + rng.uniform(0.1, 0.9)) / 26
        L = rng.uniform(0.9, 2.5)
        n = 7
        t = np.linspace(0.0, 1.0, n)
        sway = 0.12 * np.sin(t * 3.0 + k) * t
        pts = np.stack([x + sway, top - L * t, 0.05 * np.sin(t * 2.0 + k * 0.7) + rng.normal(0, 0.04)], axis=-1)
        slot = (oc.M_CORAL_TEAL, oc.M_WEED, oc.M_CORAL_ROSE, oc.M_WEED)[k % 4]
        kc.tube(mb, pts, np.linspace(0.026, 0.008, n), 5, mb.material(slot), weather=oc.REEF, noise=noise, disp_m=0.008,
                variation=float(rng.random()), cap_end=True)
    # Fans grown hanging down from the top and out of the jambs.
    for k in range(9):
        x = rng.uniform(-width * 0.45, width * 0.45)
        root = np.array([x, top - rng.uniform(0.0, 0.5), rng.uniform(-0.08, 0.08)])
        sv, st = mb.vertex_count, mb.triangle_count
        oc.sea_fan(mb, (0, 0, 0), rng, oc.M_CORAL_TEAL, height=rng.uniform(0.5, 0.9), width=rng.uniform(0.4, 0.7))
        p = np.asarray(mb.pos[sv:])
        rot = kc.rot_z(math.pi + rng.normal(0, 0.3))
        mb.pos[sv:] = (p @ rot.T + root).tolist()
        mb.nrm[sv:] = (np.asarray(mb.nrm[sv:]) @ rot.T).tolist()
        del st
    # Weed streamers.
    weed = mb.material(oc.M_WEED)
    for _k in range(18):
        x = rng.uniform(-width * 0.5, width * 0.5)
        L = rng.uniform(0.6, 1.8)
        t = np.linspace(0, 1, 6)
        pts = np.stack([x + 0.2 * t ** 2, top - L * t, 0.1 + 0.15 * t], axis=-1)
        oc.ribbon(mb, pts, np.linspace(0.07, 0.03, 6), np.array([1.0, 0.0, 0.3]), [weed], variation=float(rng.random()))
    # Sponges and knobs along the top.
    for _k in range(10):
        oc.coral_knob(mb, (rng.uniform(-width * 0.5, width * 0.5), top - 0.05, rng.uniform(-0.1, 0.1)),
                      rng.uniform(0.06, 0.12), rng, noise, oc.CORALS[int(rng.integers(0, 5))], squash=0.8)
    lod = kc.MeshBuilder("coral_curtain" + oc.LOD)
    grid = np.array([[[-width * 0.5, top, 0], [width * 0.5, top, 0]],
                     [[-width * 0.5, top - 1.8, 0.05], [width * 0.5, top - 1.8, 0.05]]])
    oc.sheet(lod, grid, lod.material(oc.M_CORAL_ROSE))
    return [mb, lod]


TARGETS = {
    "coral_head_a": lambda: build_coral_head("coral_head_a", 801, scale=1.0, boulder_slot=oc.M_CORAL_OCHRE, bleached=0.35),
    "coral_head_b": lambda: build_coral_head("coral_head_b", 802, scale=0.7, boulder_slot=oc.M_CORAL_ROSE, bleached=0.5),
    "seagrass_patch": build_seagrass,
    "coral_curtain": build_coral_curtain,
}
