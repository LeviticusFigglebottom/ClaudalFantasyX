"""The islet's landing and the ferry's boarding gear (M3-ENV-746; brightwater_ferry.md §2; the Ch4 zone's last greybox
blocks: IsletRock, Gangplank, SternGate, NameBoardWrapped). Pure numpy; see bf_common.py.

  islet_landing   the islet's seaward landing, 10 x 18 m (origin at the middle of its top): a level shelf of worn
                  reef rock at y 0 (the walk) with a few millimetres of grain, its edges breaking down 1.6 m into
                  the water over 2 m of tumbled rock; two timber mooring posts and a rope at the gangway's edge (-X).
  gangplank       the boarding plank, GANGPLANK_L long and 1.6 m wide (origin at its landward end, on its top; it
                  runs along -X to the ferry's rail): two stringers, cross planks with cleats, rope rails on
                  stanchions each side.
  stern_gate      the 1 m gate in the ferry's rail that closes the gangway (origin at its foot's middle; it spans
                  Z, hinged at -Z): a timber frame, a diagonal brace, iron straps.
  terrace_name_board_wrapped  the *Seventh Terrace*'s name-board carried away (D08): 2 m in sailcloth, bound with
                  cord at four places, lying on the deck (origin on the deck at its middle), a corner of red lacquer
                  showing at one end.
"""

from __future__ import annotations

import math

import numpy as np

import bf_common as bf
from bf_common import kc

TRI_BUDGET = {"islet_landing": (20000, 1500), "gangplank": (4000, 300), "stern_gate": (1200, 100),
              "terrace_name_board_wrapped": (3000, 200)}
LANDING_HALF = (5.0, 9.0)  # x, z: the walk on top (the greybox's IsletRock)
LANDING_SKIRT_M = 2.0  # the broken edge, top to the sea floor
LANDING_FOOT_Y = -1.6
WALK_CLEAR_M = 1.8  # the walk kept level: a band this wide either side of the gangway's line (z 0), all along the top
LEDGE_M = 0.09  # the reef shelf's ledges, off the walk
GANGPLANK_L = 3.6  # the islet's edge to the ferry's rail at the gangway (the zone's ISLET_AT less the half beam)
GANGPLANK_W = 1.6
RAIL_H = 0.9
GATE = (1.0, 1.0, 0.08)  # width (Z), height, thickness
BOARD_WRAPPED = (2.0, 0.26, 0.58)  # length, height, depth


def landing_height(noise: kc.Noise3):
    hx, hz = LANDING_HALF

    def h(X, Z):
        out = np.maximum(np.abs(X) - hx, 0.0)
        out = np.maximum(out, np.maximum(np.abs(Z) - hz, 0.0))
        p = np.stack([X / 0.9, np.zeros_like(X), Z / 0.9], axis=-1)
        grain = (noise.fbm(p, 3) - 0.5) * 0.02
        # Low ledges of reef rock across the top, away from the walk (the audit, 2026-10-29: the shelf read as one
        # smooth dark slab at night): a few centimetres, so the walk's collision box still meets the feet.
        walk = kc.smoothstep(WALK_CLEAR_M, WALK_CLEAR_M + 1.5, np.minimum(np.abs(Z), np.maximum(X + hx, 0.0) + 9.0))
        ledge = (noise.fbm(np.stack([X / 2.6, np.full_like(X, 9.0), Z / 2.6], axis=-1), 2) - 0.5)
        grain = grain + np.round(ledge * 3.0) / 3.0 * LEDGE_M * walk
        lump = (noise.fbm(np.stack([X / 1.7, np.full_like(X, 4.0), Z / 1.7], axis=-1), 3) - 0.5) * 0.7
        drop = LANDING_FOOT_Y * kc.smoothstep(0.0, LANDING_SKIRT_M, out)
        return grain * (1.0 - kc.smoothstep(0.0, 0.3, out)) + drop + lump * kc.smoothstep(0.1, 1.2, out)

    return h


def build_landing(seed: int = 905) -> list[kc.MeshBuilder]:
    out = []
    hx, hz = LANDING_HALF
    ex, ez = hx + LANDING_SKIRT_M + 0.6, hz + LANDING_SKIRT_M + 0.6
    for lod in (False, True):
        rng = kc.rng_for("islet_landing", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("islet_landing" + (bf.LOD if lod else ""))
        nx, nz = (15, 23) if lod else (63, 99)
        xs, zs = np.linspace(-ex, ex, nx), np.linspace(-ez, ez, nz)
        bf.bsc.heightfield(mb, xs, zs, landing_height(noise), mb.material(bf.M_ISLET),
                           wet=lambda X, Z, Y: np.clip(-Y * 0.9, 0.0, 1.0),
                           salt=lambda X, Z, Y: np.clip(0.35 + Y * 0.2, 0.0, 0.6), erosion=0.75, variation=0.4,
                           ao=lambda X, Z, Y: 0.55 + 0.45 * np.clip(Y + 1.2, 0.0, 1.0))
        if not lod:
            _dress_landing(mb, rng, noise, landing_height(noise))
            # The mooring posts either side of the gangway's landing, a rope slack between them.
            posts = [(-hx + 0.35, -GANGPLANK_W * 0.5 - 0.5), (-hx + 0.35, GANGPLANK_W * 0.5 + 0.5)]
            for x, z in posts:
                bf.lathe(mb, (x, -0.1, z), [(0.13, 0.0), (0.12, 0.7), (0.1, 0.95), (0.06, 1.0), (0.0, 1.0)], 8,
                         bf.M_TIMBER, weather=bf.RAIL_W)
                bf.rope(mb, (x - 0.13, 0.7, z), (x + 0.13, 0.7, z), 0.03, bf.M_ROPE, segs=1)
            bf.rope(mb, (posts[0][0], 0.72, posts[0][1]), (posts[1][0], 0.72, posts[1][1]), 0.022, bf.M_ROPE,
                    sag=0.35, segs=10)
        del rng
        out.append(mb)
    return out


def _dress_landing(mb: kc.MeshBuilder, rng, noise: kc.Noise3, h) -> None:
    """Tumbled reef boulders round the shelf's rim and down its broken edge, rubble in the hollows, tide pools in the
    top's low spots and wrack along the tide line; nothing on the walk's band."""
    hx, hz = LANDING_HALF
    rock = mb.material(bf.M_ISLET)
    reef = mb.material(bf.M_REEF)
    wet_w = kc.Weathering(moss=0.25, salt=0.35, wet=0.55, erosion=0.6)
    for _ in range(46):  # boulders: on the rim and the skirt, never on the walk's band
        side = int(rng.integers(0, 4))
        t = float(rng.uniform(-1.0, 1.0))
        out = float(rng.uniform(-0.6, 1.4))
        x, z = ((hx + out) * (1 if side == 0 else -1), t * hz) if side < 2 else (t * hx, (hz + out) * (1 if side == 2 else -1))
        if abs(z) < WALK_CLEAR_M + 0.6 and x < 0.0:
            continue  # the gangway's landing
        r = float(rng.uniform(0.25, 0.75))
        y = float(h(np.array([x]), np.array([z]))[0])
        kc.rounded_block(mb, (x, y + r * 0.35, z), (r * float(rng.uniform(0.8, 1.3)), r * float(rng.uniform(0.5, 0.8)),
                                                   r * float(rng.uniform(0.8, 1.2))), rock,
                         rot=kc.rot_y(float(rng.uniform(0, math.pi))), radius=r * 0.45, seg=2, noise=noise,
                         disp_m=r * 0.18, disp_period_m=0.3, weather=wet_w, variation=float(rng.random()))
    for _ in range(140):  # rubble and cobbles in the top's hollows and along the rim
        x, z = float(rng.uniform(-hx - 0.5, hx + 0.5)), float(rng.uniform(-hz - 0.5, hz + 0.5))
        if abs(z) < WALK_CLEAR_M:
            continue
        r = float(rng.uniform(0.05, 0.16))
        y = float(h(np.array([x]), np.array([z]))[0])
        kc.rounded_block(mb, (x, y + r * 0.3, z), (r, r * 0.6, r * float(rng.uniform(0.7, 1.2))),
                         rock if rng.random() < 0.7 else reef, rot=kc.rot_y(float(rng.uniform(0, math.pi))),
                         radius=r * 0.5, seg=1, noise=noise, disp_m=r * 0.2, weather=wet_w,
                         variation=float(rng.random()))
    for _ in range(7):  # tide pools: still water's dark sheen in the low ledges, a rim of weed
        x, z = float(rng.uniform(-hx + 0.8, hx - 0.8)), float(rng.choice([-1.0, 1.0])) * float(rng.uniform(WALK_CLEAR_M + 1.0, hz - 0.8))
        y = float(h(np.array([x]), np.array([z]))[0])
        a = np.linspace(0.0, 2.0 * math.pi, 15)
        rr = float(rng.uniform(0.35, 0.8)) * (1.0 + 0.18 * np.sin(a * 3.0 + float(rng.uniform(0, 6))))
        ring = np.stack([x + np.cos(a) * rr, np.full_like(a, y + 0.012), z + np.sin(a) * rr * 0.7], axis=-1)
        centre = np.array([[x, y + 0.012, z]])
        base = mb.add_vertices(np.vstack([centre, ring]), np.tile([0, 1, 0], (16, 1)), np.zeros((16, 2)),
                               np.tile([0.15, 0.5], (16, 1)), np.tile([0.0, 0.0, 1.0, 0.0], (16, 1)))
        pool = mb.material(bf.M_TAR)
        for i in range(14):
            mb.add_tri(base, base + 2 + i, base + 1 + i, pool)
        kc.tube(mb, ring + np.array([0.0, 0.01, 0.0]), 0.035, 4, reef, weather=wet_w)
    for k in range(3):  # wrack: dark weed and drift along the tide line on the rim
        zs = np.linspace(-hz + 1.0, hz - 1.0, 9)
        x0 = hx - 0.4 + k * 0.25
        pts = np.stack([x0 + (noise.fbm(np.stack([zs, np.full_like(zs, 3.0 + k), zs], -1), 2) - 0.5) * 0.9,
                        np.array([float(h(np.array([x0]), np.array([z]))[0]) for z in zs]) + 0.03, zs], axis=-1)
        kc.tube(mb, pts, 0.045, 5, mb.material(bf.M_TAR), weather=wet_w)


def build_gangplank(seed: int = 906) -> list[kc.MeshBuilder]:
    out = []
    L, hw = GANGPLANK_L, GANGPLANK_W * 0.5
    for lod in (False, True):
        rng = kc.rng_for("gangplank", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("gangplank" + (bf.LOD if lod else ""))
        if lod:
            kc.rounded_block(mb, (-L * 0.5, -0.06, 0.0), (L * 0.5, 0.06, hw), mb.material(bf.M_DECK), seg=1, radius=0.01)
            out.append(mb)
            continue
        deck = mb.material(bf.M_DECK)
        for z in (-hw + 0.12, hw - 0.12):
            kc.rounded_block(mb, (-L * 0.5, -0.11, z), (L * 0.5, 0.06, 0.06), mb.material(bf.M_TIMBER), seg=1,
                             radius=0.01, noise=noise, disp_m=0.004, weather=bf.DECK_W, variation=float(rng.random()))
        n = int(L / 0.26)
        for k in range(n):
            x = -L * (k + 0.5) / n
            kc.rounded_block(mb, (x, -0.025, 0.0), (L / n * 0.5 - 0.012, 0.025, hw), deck, seg=1, radius=0.008,
                             noise=noise, disp_m=0.003, weather=bf.DECK_W, variation=float(rng.random()))
            if k % 2:
                kc.rounded_block(mb, (x, 0.012, 0.0), (0.02, 0.012, hw - 0.2), mb.material(bf.M_TIMBER), seg=1,
                                 radius=0.004, weather=bf.DECK_W)
        for z in (-hw - 0.05, hw + 0.05):
            tops = []
            for x in (-0.1, -L * 0.5, -L + 0.1):
                kc.tube(mb, np.array([[x, -0.05, z], [x, RAIL_H, z]]), 0.025, 6, mb.material(bf.M_TIMBER),
                        weather=bf.RAIL_W, cap_end=True)
                tops.append((x, RAIL_H - 0.05, z))
            for a, b in zip(tops[:-1], tops[1:]):
                bf.rope(mb, a, b, 0.018, bf.M_ROPE, sag=0.08, segs=6)
        out.append(mb)
    return out


def build_stern_gate(seed: int = 907) -> list[kc.MeshBuilder]:
    out = []
    w, h, t = GATE
    for lod in (False, True):
        rng = kc.rng_for("stern_gate", seed)
        mb = kc.MeshBuilder("stern_gate" + (bf.LOD if lod else ""))
        tm = mb.material(bf.M_TIMBER)
        if lod:
            kc.rounded_block(mb, (0.0, h * 0.5, 0.0), (t * 0.5, h * 0.5, w * 0.5), tm, seg=1, radius=0.01)
            out.append(mb)
            continue
        kw = dict(seg=1, radius=0.008, weather=bf.RAIL_W)
        for z in (-w * 0.5 + 0.04, w * 0.5 - 0.04):
            kc.rounded_block(mb, (0.0, h * 0.5, z), (t * 0.5, h * 0.5, 0.04), tm, variation=float(rng.random()), **kw)
        for y in (0.08, h * 0.55, h - 0.05):
            kc.rounded_block(mb, (0.0, y, 0.0), (t * 0.5, 0.04, w * 0.5 - 0.08), tm, variation=float(rng.random()), **kw)
        brace = math.atan2(h * 0.55 - 0.16, w - 0.16)
        kc.rounded_block(mb, (0.0, (0.08 + h * 0.55) * 0.5, 0.0), (t * 0.4, 0.035, math.hypot(w - 0.16, h * 0.55) * 0.5),
                         tm, rot=kc.rot_x(brace), **kw)
        for y in (0.15, h - 0.15):
            kc.rounded_block(mb, (t * 0.5 + 0.004, y, -w * 0.5 + 0.2), (0.004, 0.025, 0.2), mb.material(bf.M_IRON),
                             seg=1, radius=0.002, weather=bf.IRON_W)
        out.append(mb)
    return out


def build_board_wrapped(seed: int = 908) -> list[kc.MeshBuilder]:
    out = []
    L, H, D = BOARD_WRAPPED
    for lod in (False, True):
        rng = kc.rng_for("terrace_name_board_wrapped", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("terrace_name_board_wrapped" + (bf.LOD if lod else ""))
        canvas = mb.material(bf.M_CANVAS)
        if lod:
            kc.rounded_block(mb, (0.0, H * 0.5, 0.0), (L * 0.5, H * 0.5, D * 0.5), canvas, seg=1, radius=0.06)
            out.append(mb)
            continue
        # The sailcloth over the board, soft at the edges and pulled in at the cords; the lacquer at the +X end.
        kc.rounded_block(mb, (-0.05, H * 0.5, 0.0), (L * 0.5 - 0.05, H * 0.5, D * 0.5), canvas, seg=4, radius=0.08,
                         noise=noise, disp_m=0.018, disp_period_m=0.18, weather=bf.CLOTH_W)
        kc.rounded_block(mb, (L * 0.5 - 0.06, H * 0.45, 0.04), (0.08, H * 0.38, D * 0.42), mb.material(bf.M_RED),
                         seg=1, radius=0.01, weather=bf.RAIL_W)
        for x in (-0.75, -0.25, 0.25, 0.75):
            ring = [(x + rng.uniform(-0.02, 0.02), y, z) for y, z in
                    ((H + 0.012, -D * 0.5), (H + 0.012, D * 0.5), (0.01, D * 0.5 + 0.012), (0.01, -D * 0.5 - 0.012),
                     (H + 0.012, -D * 0.5))]
            kc.tube(mb, np.array(ring), 0.009, 4, mb.material(bf.M_ROPE), weather=bf.CLOTH_W)
        out.append(mb)
    return out


TARGETS = {"islet_landing": build_landing, "gangplank": build_gangplank, "stern_gate": build_stern_gate,
           "terrace_name_board_wrapped": build_board_wrapped}
