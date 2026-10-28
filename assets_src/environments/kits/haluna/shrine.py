"""Shell Shrine roof and the Order chapel (haluna.md §1.2, §3.2). Pure numpy; see kit_common.py.

  roof_fan_shell        the Shell Shrine's tiered roof of stone fan-shells (scallop fans of 5, 3 and
                        1.5 m radius, ribbed, set in three tiers, hinge to the centre) rising to an
                        oculus ring; white mortar ribs at the joints tie it to Haluna. ~14 m across.
  shell_shrine_massing  the islet shrine as a distant massing: a curved drum (R = 7 m) with the west
                        entrance and steps, under roof_fan_shell. PLACEHOLDER for views > 150 m only:
                        the shrine's wall/column/channel kit is M2 work (haluna.md §3.2).
  order_chapel          the 6 x 9 m Order chapel (M3-ENV-102: a bare coral-stone base course, weathered lime-wash, a
                        lamp niche over the door, a bell-cote on the front parapet, the dome on a taller drum):
                        whitewashed coral, order_marble plinth, cornice and
                        door surround, a gilded bowl-dome cupola (1.6 m), a red lacquer door with the
                        gold Level emblem. Deliberately crisp (low erosion): it must look imported.
                        M3-ENV-705 (H07 read it as a plain box): the Order's articulation, still crisp and
                        straight: marble corner and bay pilasters, a dentil course under the cornice, arched marble
                        heads on the windows, two marble steps to the door, and four arched openings round the
                        cupola's drum.

The fan-shell form is original: a shrine roof built from the village's own symbol (the wake-shell).
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_STONE = "kit_coral_stone"
M_MORTAR = "kit_mortar_white"
M_WHITEWASH = "kit_whitewash"
M_MARBLE = "kit_order_marble"
M_GOLD = "kit_gold_leaf"
M_LACQUER = "kit_lacquer_red"
M_DARK = "kit_interior_dark"

TRI_BUDGET = {
    "roof_fan_shell": (18000, 2500),
    "shell_shrine_massing": (22000, 3500),
    "order_chapel": (9000, 900),
}
PLACEHOLDER_REASONS = {
    "shell_shrine_massing": "distant massing of the Shell Shrine (drum and steps); the shrine wall, "
                            "column and channel kit is M2 (haluna.md 3.2)",
}

TENDED = kc.Weathering(moss=0.2, salt=0.35, wet=0.0, erosion=0.3)  # the shrine is swept and loved


def fan_shell(mb: kc.MeshBuilder, hinge, outward, radius: float, rng, noise, *, span_deg: float = 150.0,
              ribs: int = 9, lift: float = 0.35, droop_deg: float = 22.0, lod: bool = False,
              weather: kc.Weathering = TENDED) -> None:
    """A ribbed stone fan: hinge at `hinge`, opening towards `outward` (horizontal unit), its surface
    domed (`lift` x radius at mid-radius) and pitched down by droop_deg so rain runs off the rim."""
    out = kc.normalize(np.asarray(outward, float) * np.array([1.0, 0.0, 1.0]))
    side = np.cross(np.array([0.0, 1.0, 0.0]), out)
    droop = math.radians(droop_deg)
    nr, na = (2, 6) if lod else (5, ribs * 2 + 1)
    span = math.radians(span_deg)
    grid = np.zeros((nr + 1, na + 1, 3))
    for i in range(nr + 1):
        f = i / nr
        r = radius * (0.05 + 0.95 * f)
        for j in range(na + 1):
            a = -span * 0.5 + span * j / na
            flute = 0.0 if lod else 0.045 * radius * (0.5 - 0.5 * math.cos(a * ribs * 2.0 * math.pi / span)) * f
            dome = lift * radius * math.sin(math.pi * min(f, 1.0)) * math.cos(a / span * math.pi) ** 0.5
            horiz = out * math.cos(a) + side * math.sin(a)
            grid[i, j] = (np.asarray(hinge, float) + horiz * r * math.cos(droop)
                          + np.array([0.0, -r * math.sin(droop) + dome + flute, 0.0]))
    breakup = noise.fbm(grid / 1.2, 2)
    col = np.stack([weather.moss * breakup * 0.6, weather.salt * breakup, np.zeros(grid.shape[:2]),
                    weather.erosion * (0.4 + 0.6 * breakup)], axis=-1)
    F = np.linspace(0, 1, nr + 1)[:, None] * np.ones((1, na + 1))
    uv2 = np.stack([0.55 + 0.45 * F, np.full(F.shape, float(rng.random()))], axis=-1)
    uv = np.stack([grid[..., 0], grid[..., 2]], axis=-1)
    flip = np.dot(np.cross(grid[nr // 2, na // 2 + 1] - grid[nr // 2, na // 2 - 1],
                           grid[nr // 2 + 1, na // 2] - grid[nr // 2 - 1, na // 2]), [0, 1, 0]) < 0
    kc.quad_strip(mb, grid, mb.material(M_STONE), uv=uv, col=col, uv2=uv2, flip=bool(flip))
    if lod:
        return
    # Underside (thickness 0.18 m) and the rolled rim in mortar.
    under = grid - np.array([0.0, 0.18, 0.0])
    kc.quad_strip(mb, under, mb.material(M_STONE), uv=uv, col=col * np.array([0, 0, 0, 1]),
                  uv2=uv2 * np.array([0.5, 1.0]), flip=not flip)
    rim = np.vstack([grid[-1], under[-1][::-1][:1]])
    kc.tube(mb, grid[-1] + np.array([0.0, -0.06, 0.0]), 0.09 if not lod else 0.08, 5 if lod else 7,
            mb.material(M_MORTAR), weather=weather, variation=float(rng.random()))
    del rim


def roof_fan_shell(mb: kc.MeshBuilder, rng, noise, *, base_y: float = 0.0, lod: bool = False,
                   tiers=((7.0, 5.0, 8, 0.0), (4.6, 3.0, 8, 0.5), (2.4, 1.5, 8, 0.0))) -> float:
    """Three tiers of fan-shells around a vertical axis; returns the oculus ring height."""
    y = base_y
    top = base_y
    for k, (ring_r, shell_r, count, phase) in enumerate(tiers):
        tier_y = base_y + 0.9 + k * 1.25
        for i in range(count):
            a = 2 * math.pi * (i + phase) / count
            out = np.array([math.cos(a), 0.0, math.sin(a)])
            hinge = out * (ring_r - shell_r * 0.85) + np.array([0.0, tier_y, 0.0])
            fan_shell(mb, hinge, out, shell_r, rng, noise, lod=lod, span_deg=360.0 / count * 1.35)
        # Mortar rib ring under each tier.
        ang = np.linspace(0, 2 * math.pi, 33 if not lod else 13)
        ring = np.stack([np.cos(ang) * (ring_r - shell_r * 0.85), np.full_like(ang, tier_y - 0.05),
                         np.sin(ang) * (ring_r - shell_r * 0.85)], axis=-1)
        kc.tube(mb, ring, 0.14, 6 if not lod else 4, mb.material(M_MORTAR), variation=float(rng.random()))
        top = tier_y
    # Oculus ring.
    ang = np.linspace(0, 2 * math.pi, 41 if not lod else 13)
    ring = np.stack([np.cos(ang) * 1.0, np.full_like(ang, top + 0.55), np.sin(ang) * 1.0], axis=-1)
    kc.tube(mb, ring, 0.22, 10 if not lod else 5, mb.material(M_STONE), weather=TENDED, noise=None if lod else noise,
            disp_m=0.03, variation=0.6)
    del y
    return top + 0.55


def build_roof_fan_shell(seed: int = 81) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("roof_fan_shell", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("roof_fan_shell")
    roof_fan_shell(mb, rng, noise)
    lod = kc.MeshBuilder("roof_fan_shell-lod1")
    roof_fan_shell(lod, rng, noise, lod=True)
    return [mb, lod]


def build_shrine_massing(seed: int = 82) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("shell_shrine_massing", seed)
    noise = kc.Noise3(rng)
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("shell_shrine_massing" + ("-lod1" if lod else ""))
        drum_r, drum_h = 7.0, 3.6
        n = 28 if not lod else 12
        door_a = math.pi  # west (-X)
        for k in range(n):
            a = 2 * math.pi * (k + 0.5) / n
            if abs(((a - door_a + math.pi) % (2 * math.pi)) - math.pi) < 0.22:
                continue
            p = np.array([math.cos(a) * drum_r, drum_h * 0.5, math.sin(a) * drum_r])
            kc.rounded_block(mb, p, (math.pi * drum_r / n + 0.03, drum_h * 0.5, 0.35), mb.material(M_STONE),
                             rot=kc.rot_y(-a + math.pi * 0.5), radius=0.06, seg=1 if lod else 3,
                             noise=None if lod else noise, disp_m=0.04, weather=TENDED, variation=float(rng.random()))
        # Shell-whorl columns either side of the door, steps down to the landing (west).
        for s in (-1.0, 1.0):
            a = door_a + s * 0.3
            c = np.array([math.cos(a) * (drum_r + 0.6), 0.0, math.sin(a) * (drum_r + 0.6)])
            pts = np.array([c, c + [0, 4.0, 0]])
            kc.tube(mb, np.linspace(pts[0], pts[1], 9), 0.25 + 0.03 * np.sin(np.linspace(0, 12, 9)), 10,
                    mb.material(M_STONE), weather=TENDED, variation=0.3, cap_end=True)
        for k in range(4):
            kc.rounded_block(mb, (-drum_r - 1.0 - k * 0.45, 0.15 - k * 0.3 + 0.6, 0.0), (0.4, 0.15, 2.2 + k * 0.3),
                             mb.material(M_STONE), radius=0.05, seg=1 if lod else 2, weather=TENDED,
                             variation=float(rng.random()))
        roof_fan_shell(mb, rng, noise, base_y=drum_h - 0.6, lod=lod)
        out.append(mb)
    return out


def build_chapel(seed: int = 83, *, w: float = 6.0, d: float = 9.0, wall_h: float = 4.2) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("order_chapel", seed)
    noise = kc.Noise3(rng)
    crisp = kc.Weathering(moss=0.05, salt=0.15, wet=0.0, erosion=0.08)
    # M3-ENV-102: the whitewash kept up but not new: salt and damp low on the walls, the lime-wash streaked.
    washed = kc.Weathering(moss=0.12, salt=0.35, wet=0.25, erosion=0.3, noise_scale_m=0.6)
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("order_chapel" + ("-lod1" if lod else ""))
        ww = mb.material(M_WHITEWASH)
        marble = mb.material(M_MARBLE)
        seg = 1 if lod else 4
        hw, hd = w * 0.5, d * 0.5
        door_w, door_h = 1.3, 2.4
        # Walls (front split around the door), whitewashed coral, sharp edges.
        t = 0.45
        walls = [((0.0, wall_h * 0.5, -hd + t * 0.5), (hw, wall_h * 0.5, t * 0.5)),
                 ((-hw + t * 0.5, wall_h * 0.5, 0.0), (t * 0.5, wall_h * 0.5, hd)),
                 ((hw - t * 0.5, wall_h * 0.5, 0.0), (t * 0.5, wall_h * 0.5, hd)),
                 ((-(hw + door_w * 0.5) * 0.5, wall_h * 0.5, hd - t * 0.5), ((hw - door_w * 0.5) * 0.5, wall_h * 0.5,
                                                                              t * 0.5)),
                 (((hw + door_w * 0.5) * 0.5, wall_h * 0.5, hd - t * 0.5), ((hw - door_w * 0.5) * 0.5, wall_h * 0.5,
                                                                             t * 0.5)),
                 ((0.0, (door_h + wall_h) * 0.5, hd - t * 0.5), (door_w * 0.5, (wall_h - door_h) * 0.5, t * 0.5))]
        for c, half in walls:
            kc.rounded_block(mb, c, half, ww, radius=0.02, seg=seg, noise=None if lod else noise, disp_m=0.006,
                             weather=washed, variation=float(rng.random()), wet_bias=0.15)
        # The stepped base: a course of bare coral stone under the marble plinth, where the whitewash never held.
        kc.rounded_block(mb, (0.0, 0.09, 0.0), (hw + 0.2, 0.09, hd + 0.2), mb.material(M_STONE), radius=0.02,
                         seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.01, weather=washed,
                         variation=0.6)
        # Marble plinth band, cornice and parapet; door surround.
        for y, hh, grow in ((0.22, 0.22, 0.06), (wall_h - 0.1, 0.14, 0.12)):
            kc.rounded_block(mb, (0.0, y, 0.0), (hw + grow, hh, hd + grow), marble, radius=0.015, seg=seg,
                             weather=crisp, variation=0.2)
        # Parapet: four thin walls around the flat roof (not a solid block: the cupola rises inside).
        pt, ph = 0.2, 0.55
        for c, half in (((0.0, hd - pt * 0.5), (hw, pt * 0.5)), ((0.0, -hd + pt * 0.5), (hw, pt * 0.5)),
                        ((hw - pt * 0.5, 0.0), (pt * 0.5, hd)), ((-hw + pt * 0.5, 0.0), (pt * 0.5, hd))):
            kc.rounded_block(mb, (c[0], wall_h + ph * 0.5, c[1]), (half[0], ph * 0.5, half[1]), ww, radius=0.015,
                             seg=1 if lod else 2, weather=crisp, variation=0.25)
        for x in (-door_w * 0.5 - 0.12, door_w * 0.5 + 0.12):
            kc.rounded_block(mb, (x, door_h * 0.5 + 0.1, hd + 0.04), (0.12, door_h * 0.5 + 0.1, 0.06), marble,
                             radius=0.01, seg=seg, weather=crisp, variation=0.3)
        kc.rounded_block(mb, (0.0, door_h + 0.22, hd + 0.05), (door_w * 0.5 + 0.26, 0.14, 0.08), marble, radius=0.01,
                         seg=seg, weather=crisp, variation=0.35)
        # The red lacquer door (two leaves) with the gold Level emblem: a bar with a disc above it.
        lac = mb.material(M_LACQUER)
        for s in (-1.0, 1.0):
            kc.rounded_block(mb, (s * door_w * 0.25, door_h * 0.5 + 0.1, hd - 0.12), (door_w * 0.25 - 0.01,
                             door_h * 0.5 - 0.02, 0.04), lac, radius=0.008, seg=1, weather=crisp, variation=0.5)
        gold = mb.material(M_GOLD)
        kc.rounded_block(mb, (0.0, door_h * 0.62, hd - 0.07), (0.36, 0.025, 0.012), gold, radius=0.005, seg=1)
        disc = np.array([[0.0, door_h * 0.62 + 0.14, hd - 0.075], [0.0, door_h * 0.62 + 0.14, hd - 0.06]])
        kc.tube(mb, disc, 0.08, 16 if not lod else 6, gold, cap_end=True, cap_start=True)
        # Tall windows on the sides: dark recess in a marble frame.
        if not lod:
            for s in (-1.0, 1.0):
                for z in (-hd * 0.45, hd * 0.1):
                    x = s * (hw + 0.005)
                    kc.rounded_block(mb, (x, 2.3, z), (0.01, 0.75, 0.32), mb.material(M_DARK), radius=0.005, seg=1)
                    kc.rounded_block(mb, (x + s * 0.03, 2.3, z), (0.03, 0.86, 0.06), marble, radius=0.005, seg=1)
                    kc.rounded_block(mb, (x + s * 0.03, 3.12, z), (0.04, 0.06, 0.42), marble, radius=0.005, seg=1)
                    kc.rounded_block(mb, (x + s * 0.03, 1.5, z), (0.05, 0.05, 0.42), marble, radius=0.005, seg=1)
        if not lod:
            _chapel_order(mb, rng, hw, hd, wall_h, door_w, marble, crisp)
        # Flat roof slab and the cupola: a drum and an inverted-bowl dome (with a lip), gilded.
        kc.rounded_block(mb, (0.0, wall_h + 0.05, 0.0), (hw - 0.05, 0.08, hd - 0.05), ww, radius=0.01, seg=1,
                         weather=crisp)
        cz = 0.0
        base = wall_h + 0.12
        ang_n = 24 if not lod else 10
        drum_h = CHAPEL_DRUM_H
        drum = np.array([[0.0, base, cz], [0.0, base + drum_h, cz]])
        kc.tube(mb, drum, 0.72 * CHAPEL_DOME_SCALE, ang_n, marble, cap_end=False, weather=crisp, variation=0.2)
        if not lod:  # four arched openings round the drum (dark, framed in the drum's marble)
            for k in range(4):
                th = k * math.pi * 0.5 + math.pi * 0.25
                n = np.array([math.cos(th), 0.0, math.sin(th)])
                c = np.array([0.0, base + drum_h * 0.5, cz]) + n * 0.7 * CHAPEL_DOME_SCALE
                kc.rounded_block(mb, c, (0.04, 0.22, 0.14), mb.material(M_DARK), rot=kc.rot_y(-th), radius=0.0,
                                 seg=1)
                arc = np.linspace(0.0, math.pi, 7)
                t = np.array([-math.sin(th), 0.0, math.cos(th)])
                pts = [c + n * 0.05 + t * math.cos(a) * 0.17 + np.array([0.0, 0.22 + math.sin(a) * 0.17, 0.0])
                       for a in arc]
                kc.tube(mb, np.array(pts), 0.03, 4, marble)
        prof_t = np.linspace(0.0, 1.0, 12 if not lod else 5)
        k = CHAPEL_DOME_SCALE
        bowl_r = k * (0.8 * (np.cos(prof_t * math.pi * 0.5) ** 0.85) + 0.05 * np.sin(prof_t * math.pi) * (1 - prof_t))
        base = base + drum_h - 0.55
        bowl_y = base + 0.55 + k * 0.95 * np.sin(prof_t * math.pi * 0.5)
        centers = np.stack([np.zeros_like(prof_t), bowl_y, np.full_like(prof_t, cz)], axis=-1)
        kc.tube(mb, centers, np.maximum(bowl_r, 0.01), ang_n, gold, first_normal=np.array([1.0, 0.0, 0.0]))
        kc.tube(mb, np.array([[0.0, base + 0.5, cz], [0.0, base + 0.6, cz]]), 0.86 * k, ang_n, gold, cap_start=True)
        top = base + 0.55 + k * 0.95
        kc.tube(mb, np.array([[0.0, top - 0.02, cz], [0.0, top + 0.4, cz]]), np.array([0.06, 0.015]), 8, gold,
                cap_end=True)
        if not lod:
            _chapel_front(mb, rng, hw, hd, wall_h, door_w, door_h, marble, gold, crisp)
        out.append(mb)
    return out


CHAPEL_DRUM_H = 1.35  # M3-ENV-102: the drum clears the parapet, so the gilt dome reads from the court (H07)
CHAPEL_DOME_SCALE = 1.25
BELL_COTE_H = 1.3


def _chapel_front(mb, rng, hw: float, hd: float, wall_h: float, door_w: float, door_h: float, marble: int, gold: int,
                  crisp) -> None:
    """M3-ENV-102: the Order's face over the door: an arched lamp niche above the lintel with the Level emblem in
    gold, and a bell-cote on the front parapet (two marble piers under an arch, a bronze-gilt bell hung in it)."""
    dark = mb.material(M_DARK)
    ny = door_h + 0.95
    kc.rounded_block(mb, (0.0, ny, hd + 0.005), (0.28, 0.32, 0.01), dark, radius=0.0, seg=1)
    arc = np.linspace(0.0, math.pi, 9)
    pts = np.stack([np.cos(arc) * 0.36, ny + 0.32 + np.sin(arc) * 0.36, np.full_like(arc, hd + 0.05)], -1)
    kc.tube(mb, pts, 0.05, 4, marble)
    for x in (-0.36, 0.36):
        kc.rounded_block(mb, (x, ny, hd + 0.05), (0.05, 0.34, 0.05), marble, radius=0.005, seg=1)
    kc.rounded_block(mb, (0.0, ny - 0.36, hd + 0.08), (0.42, 0.04, 0.1), marble, radius=0.005, seg=1)  # its sill
    kc.tube(mb, np.array([[0.0, ny - 0.02, hd + 0.03], [0.0, ny - 0.02, hd + 0.05]]), 0.12, 14, gold, cap_end=True)
    kc.rounded_block(mb, (0.0, ny - 0.2, hd + 0.04), (0.2, 0.02, 0.01), gold, radius=0.003, seg=1)
    # The bell-cote, standing on the front parapet.
    y0 = wall_h + 0.55
    for x in (-0.55, 0.55):
        kc.rounded_block(mb, (x, y0 + BELL_COTE_H * 0.5, hd - 0.1), (0.13, BELL_COTE_H * 0.5, 0.13), marble,
                         radius=0.01, seg=1, weather=crisp, variation=0.3)
    arc = np.linspace(0.0, math.pi, 11)
    pts = np.stack([np.cos(arc) * 0.55, y0 + BELL_COTE_H + np.sin(arc) * 0.55, np.full_like(arc, hd - 0.1)], -1)
    kc.tube(mb, pts, 0.11, 6, marble)
    kc.rounded_block(mb, (0.0, y0 + BELL_COTE_H + 0.62, hd - 0.1), (0.08, 0.1, 0.08), marble, radius=0.01, seg=1)
    # The bell on its yoke.
    yoke = y0 + BELL_COTE_H + 0.1
    kc.tube(mb, np.array([[-0.42, yoke, hd - 0.1], [0.42, yoke, hd - 0.1]]), 0.025, 6, mb.material(M_DARK))
    prof = [(0.03, 0.0), (0.12, -0.04), (0.16, -0.22), (0.24, -0.4), (0.25, -0.44), (0.0, -0.44)]
    bell = np.array([[0.0, yoke + y, hd - 0.1] for _, y in prof])
    kc.tube(mb, bell, np.array([r for r, _ in prof]), 14, gold, cap_end=True)


def _chapel_order(mb, rng, hw: float, hd: float, wall_h: float, door_w: float, marble: int, crisp) -> None:
    """The chapel's crisp Order articulation (M3-ENV-705): pilasters, dentils, window heads, the door's steps."""
    # Pilasters at the corners and one bay pilaster mid-side, standing proud of the whitewash.
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * (hw + 0.02), wall_h * 0.5, sz * (hd + 0.02)), (0.2, wall_h * 0.5 - 0.1, 0.2),
                             marble, radius=0.01, seg=1, weather=crisp, variation=0.25)
        kc.rounded_block(mb, (sx * (hw + 0.04), wall_h * 0.5, -hd * 0.175), (0.06, wall_h * 0.5 - 0.1, 0.16),
                         marble, radius=0.01, seg=1, weather=crisp, variation=0.25)
    # The dentil course under the cornice, all round.
    y = wall_h - 0.32
    for (axis, half, fixed) in (("x", hw, hd + 0.05), ("x", hw, -hd - 0.05), ("z", hd, hw + 0.05), ("z", hd, -hw - 0.05)):
        n = int(half * 2 / 0.22)
        for k in range(n):
            a = -half + (k + 0.5) * 2 * half / n
            c = (a, y, fixed) if axis == "x" else (fixed, y, a)
            hs = (0.05, 0.06, 0.05)
            kc.rounded_block(mb, c, hs, marble, radius=0.0, seg=1)
    # Arched marble heads over the side windows (the windows stand at z -0.45 hd and 0.1 hd, 2.3 m centre).
    for s in (-1.0, 1.0):
        for z in (-hd * 0.45, hd * 0.1):
            x = s * (hw + 0.04)
            arc = np.linspace(0.0, math.pi, 9)
            pts = np.stack([np.full_like(arc, x), 3.12 + np.sin(arc) * 0.42, z + np.cos(arc) * 0.42], -1)
            kc.tube(mb, pts, 0.05, 4, marble)
            kc.rounded_block(mb, (x - s * 0.02, 3.3, z), (0.012, 0.18, 0.3), mb.material(M_DARK), radius=0.0, seg=1)
    # Two marble steps up to the door (the floor inside is the plinth's top).
    for k, (dz, hgt) in enumerate(((0.55, 0.15), (0.3, 0.3))):
        kc.rounded_block(mb, (0.0, hgt * 0.5, hd + dz), (door_w * 0.5 + 0.5 - 0.15 * k, hgt * 0.5, 0.25 if k == 0
                                                                                              else 0.3),
                         marble, radius=0.01, seg=1, weather=crisp, variation=0.3)


TARGETS = {"roof_fan_shell": build_roof_fan_shell, "shell_shrine_massing": build_shrine_massing,
           "order_chapel": build_chapel}
