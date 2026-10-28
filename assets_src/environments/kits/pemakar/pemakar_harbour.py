"""Pemakar's harbour and crown pieces the kit lacked (M3-ENV-1214, act1_ch05.md §10 item 1). Pure numpy.

  harbour_quay    the town's quay at the mountain's foot, 32 m along the shore: a fitted volcanic front wall from a
                  metre under the sea to the deck, coping, a paved deck back 4.3 m to the slope, stone bollards,
                  iron mooring rings and timber rubbing posts on the face, and a sea stair down to the water at the
                  west end. Origin at the front edge's centre on the deck (y 0 = the deck; the zone puts it at the
                  sea + 1.2 m); the sea is +Z.
  sea_cut_weir    the hero mesh: the last stone lip where the terrace channels spill into the sea (B05, P11/P12).
                  The cut arrives from -Z between two cheek walls, a dressed crest 6.4 m wide, an ogee face falling to
                  the sea in three dressed courses with the spill sheet over it, and the weir step on the east cheek
                  where the child leans out. Origin at the crest's centre, its top (the zone puts it at sea + 0.4).
  wake_wall       the wall at the quay's back where ships' name-boards are hung (the Low Reaches sea-law): 5 m of
                  fitted stone 2 m high under a coping, two rows of timber pegs, name-boards old and new hanging on
                  them (black-lacquered letters on the fresh ones), a lamp niche, frangipani at the foot. Origin at
                  its foot's centre, the boards' face toward +Z.
  crown_bell      the top tier's single bell (B04): a bronze bell under a little fibre-thatch roof on two dark posts
                  on stone pads, its striker log hung on fibre ropes. Origin at the foot's centre, front +Z.
  flank_rocks     (M3-ENV-705, P04/P11 read the massif's lower flank as a bare smooth slope) a 14 x 10 m patch of
                  the flank: basalt boulders half sunk in the ash, a fan of loose scree, dry scrub tufts in the
                  hollows. Origin at its centre on the ground; the layout scatters it over the flank round the
                  harbour, tilted to the slope.
"""

from __future__ import annotations

import math

import numpy as np

import pemakar_common as pc
import pemakar_terraces as pt
import props  # Haluna's props, read-only: lathe
from pemakar_common import kc

TRI_BUDGET = {"harbour_quay": (26000, 1500), "sea_cut_weir": (14000, 1000), "wake_wall": (12000, 900),
              "crown_bell": (5000, 500), "flank_rocks": (5000, 300)}

QUAY_HALF_M = 16.0
QUAY_DEPTH_M = 4.3  # front edge to the slope (act1-chapters' QUAY_BACK_Z 22.7 against the front at 27)
QUAY_FOOT_M = 2.4  # the face's foot under the deck (the sea at -1.2, so a metre and more under water)
SEA_BELOW_DECK_M = 1.2
SEA_STAIR_X = -12.0  # the stair's top step, west end; it descends to the east along the face
WEIR_HALF_M = 3.2
WEIR_DROP_M = 0.4  # the crest stands this far over the sea
WAKE_HALF_M = 2.5
WAKE_H_M = 2.0
BELL_H_M = 2.6
HARBOUR = kc.Weathering(moss=0.45, salt=0.2, wet=0.15, erosion=0.6, noise_scale_m=0.6)


def _paving(mb, x0, x1, z0, z1, rng, noise, *, mat=pc.M_DRESSED, flag=(0.7, 1.2), depth=0.18) -> None:
    """Flags across z0..z1 in courses along x, tops at y 0 (joints a few mm down)."""
    z = z0
    while z < z1 - 0.1:
        w = min(rng.uniform(0.5, 0.8), z1 - z)
        x = x0 + rng.uniform(0.0, 0.4)
        while x < x1 - 0.1:
            ln = min(rng.uniform(*flag), x1 - x)
            kc.rounded_block(mb, (x + ln * 0.5, -depth * 0.5 + rng.uniform(-0.006, 0.004), z + w * 0.5),
                             (ln * 0.5 - 0.012, depth * 0.5, w * 0.5 - 0.012), mb.material(mat),
                             rot=kc.rot_y(rng.normal(0.0, 0.006)), radius=0.02, seg=1, noise=noise, disp_m=0.006,
                             disp_period_m=0.3, weather=pc.DRESSED, variation=float(rng.random()))
            x += ln
        z += w


def _bollard(mb, at, rng, noise) -> None:
    prof = [(0.26, 0.0), (0.24, 0.35), (0.19, 0.5), (0.24, 0.62), (0.2, 0.7)]
    props.lathe(mb, prof, pc.M_DRESSED, rng, sides=14, at=at, noise=noise, disp_m=0.01, weather=HARBOUR,
                cap_end=True)


def quay(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    hl = QUAY_HALF_M
    top = -pc.COPING_H_M + pt.COPING_TOP_M
    if lod:
        kc.rounded_block(mb, (0.0, -QUAY_FOOT_M * 0.5, -0.3), (hl, QUAY_FOOT_M * 0.5, 0.3), mb.material(pc.M_STONE),
                         radius=0.05, seg=1)
        kc.rounded_block(mb, (0.0, -0.1, -QUAY_DEPTH_M * 0.5), (hl, 0.1, QUAY_DEPTH_M * 0.5), mb.material(pc.M_DRESSED),
                         radius=0.03, seg=1)
        return mb
    pt.fitted_face(mb, -hl, hl, -QUAY_FOOT_M, top, rng, noise, batter=False, thick=0.8, weather=HARBOUR, seg=2)
    pt.coping(mb, -hl, hl, rng, noise, weather=HARBOUR)
    _paving(mb, -hl, hl, -QUAY_DEPTH_M, -pc.COPING_D_M + 0.02, rng, noise)
    # The tide band on the face: wet and weed below the high-water mark (0.5 m over the sea).
    pc.wet_pass(mb, 0, lambda p: (p[:, 1] < -SEA_BELOW_DECK_M + 0.5) & (p[:, 2] > -0.9), 1.0)
    # Bollards along the edge, iron rings on the face between them, timber rubbing posts against the face.
    for x in (-13.5, -6.0, 2.0, 9.5):
        _bollard(mb, (x, 0.0, -0.75), rng, noise)
    for x in (-10.0, -2.0, 6.0, 13.0):
        a = np.linspace(0.0, 2 * math.pi, 13)
        ring = np.stack([x + np.cos(a) * 0.13, -0.55 + np.sin(a) * 0.13, np.full_like(a, 0.07)], -1)
        kc.tube(mb, ring, 0.018, 5, mb.material(pc.M_IRON), weather=pc.TOWN)
        kc.rounded_block(mb, (x, -0.42, 0.03), (0.05, 0.05, 0.04), mb.material(pc.M_IRON), radius=0.01, seg=1)
    for x in np.arange(-hl + 2.0, hl, 4.0):
        if abs(x - SEA_STAIR_X + 1.5) < 2.5:
            continue
        kc.rounded_block(mb, (x, -1.25, 0.12), (0.11, 1.15, 0.1), mb.material(pc.M_TIMBER),
                         rot=kc.rot_z(rng.normal(0.0, 0.02)), radius=0.03, seg=1, noise=noise, disp_m=0.01,
                         weather=HARBOUR, variation=float(rng.random()))
    # The sea stair: steps along the face from the deck at its west end down to the water and under it.
    n = 8
    for k in range(n):
        ytop = -0.2 * (k + 1)
        x = SEA_STAIR_X + 0.42 * k
        kc.rounded_block(mb, (x + 0.21, ytop - 0.11, 0.55), (0.23, 0.11 + 0.05 * k, 0.55), mb.material(pc.M_DRESSED),
                         radius=0.03, seg=1, noise=noise, disp_m=0.008, weather=HARBOUR, variation=float(rng.random()))
    kc.rounded_block(mb, (SEA_STAIR_X + 0.42 * n * 0.5 + 0.2, -1.0, 1.15), (0.42 * n * 0.5 + 0.2, 1.0, 0.07),
                     mb.material(pc.M_STONE), radius=0.03, seg=1, noise=noise, disp_m=0.01, weather=HARBOUR)
    pc.wet_pass(mb, 0, lambda p: p[:, 1] < -SEA_BELOW_DECK_M + 0.5, 0.9)
    pc.ash_pass(mb, 0, noise, 0.6, vertical=0.1)
    return mb


def weir(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    hw = WEIR_HALF_M
    seg = 1 if lod else 2
    dressed = mb.material(pc.M_DRESSED)
    # The cut's bed upstream (the channels' water arriving over it) and the crest stone.
    kc.rounded_block(mb, (0.0, -0.25, -1.6), (hw, 0.2, 1.4), dressed, radius=0.03, seg=1, weather=pc.WASHED)
    pc.water_plane(mb, -hw, hw, -3.0, 0.25, 0.06, pc.M_WATER, nx=2 if lod else 6, nz=2 if lod else 6)
    x = -hw
    while x < hw - 0.05:
        ln = min(rng.uniform(0.7, 1.2), hw - x)
        kc.rounded_block(mb, (x + ln * 0.5, -0.12, 0.0), (ln * 0.5 - 0.01, 0.12, 0.28), dressed,
                         rot=kc.rot_y(rng.normal(0.0, 0.01)), radius=0.06, seg=seg, noise=None if lod else noise,
                         disp_m=0.01, weather=pc.WASHED, variation=float(rng.random()))
        x += ln
    # The ogee face in three courses, each set back under the one above, to the sea.
    for k, (y, z, d) in enumerate(((-0.33, 0.42, 0.22), (-0.6, 0.72, 0.26), (-0.9, 1.05, 0.3))):
        x = -hw + (0.3 if k % 2 else 0.0)
        while x < hw - 0.05:
            ln = min(rng.uniform(0.8, 1.3), hw - x)
            kc.rounded_block(mb, (x + ln * 0.5, y, z), (ln * 0.5 - 0.01, 0.13, d), dressed,
                             rot=kc.rot_y(rng.normal(0.0, 0.01)), radius=0.07, seg=seg, noise=None if lod else noise,
                             disp_m=0.012, weather=HARBOUR, variation=float(rng.random()))
            x += ln
        x = -hw
    # The sheet over the crest and down the courses (UV.y down: env_water_spill).
    rows = 4 if lod else 10
    t = np.linspace(0.0, 1.0, rows)
    zs = 0.28 + 1.0 * t ** 0.8
    ys = 0.03 - (WEIR_DROP_M + 0.75) * t ** 1.3
    xs = np.linspace(-hw + 0.06, hw - 0.06, 2 if lod else 7)
    grid = np.array([[[xx, yy + 0.02, zz] for xx in xs] for yy, zz in zip(ys, zs)])
    uv = np.array([[[u * 2 * hw, tt] for u in np.linspace(0.0, 1.0, len(xs))] for tt in t])
    kc.quad_strip(mb, grid, mb.material(pc.M_SPILL), uv=uv, col=(0, 0, 1, 0), uv2=(1.0, 0.5), smooth=True)
    # The cheek walls, and the weir step on the east cheek: a landing at the crest's height, two steps down.
    for sx in (-1.0, 1.0):
        cx = sx * (hw + 0.4)
        if lod:
            kc.rounded_block(mb, (cx, -0.15, -1.0), (0.4, 0.75, 2.2), mb.material(pc.M_STONE), radius=0.04, seg=1)
            continue
        tmp = kc.MeshBuilder("cheek")
        pt.fitted_face(tmp, -2.2, 2.2, -1.2, 0.5, rng, noise, batter=False, thick=0.8, weather=HARBOUR, seg=2)
        mb.merge(tmp, kc.rot_y(-sx * math.pi * 0.5), (cx, 0.0, -1.0))
    kc.rounded_block(mb, (hw + 1.4, 0.07, 0.3), (0.6, 0.12, 0.8), dressed, radius=0.04, seg=seg,
                     noise=None if lod else noise, disp_m=0.01, weather=HARBOUR)
    for k in range(2):
        kc.rounded_block(mb, (hw + 1.4, -0.18 - 0.22 * k, 1.25 + 0.36 * k), (0.6, 0.11, 0.2), dressed, radius=0.03,
                         seg=seg, noise=None if lod else noise, disp_m=0.01, weather=HARBOUR)
    if not lod:
        pc.wet_pass(mb, 0, lambda p: p[:, 1] < -0.2, 1.0)
        pc.ash_pass(mb, 0, noise, 0.3, vertical=0.05)
    return mb


def wake_wall(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    hl = WAKE_HALF_M
    if lod:
        kc.rounded_block(mb, (0.0, WAKE_H_M * 0.5, 0.0), (hl, WAKE_H_M * 0.5, 0.3), mb.material(pc.M_STONE),
                         radius=0.04, seg=1)
        kc.rounded_block(mb, (0.0, 1.45, 0.33), (hl - 0.3, 0.35, 0.02), mb.material(pc.M_TIMBER), radius=0.01, seg=1)
        return mb
    tmp = kc.MeshBuilder("face")
    top = -pc.COPING_H_M + pt.COPING_TOP_M
    lift = WAKE_H_M - pt.COPING_TOP_M  # the coping's top at WAKE_H_M, the face's foot on the ground
    pt.fitted_face(tmp, -hl, hl, -lift, top, rng, noise, batter=False, thick=0.6, seg=2)
    pt.coping(tmp, -hl, hl, rng, noise)
    mb.merge(tmp, None, (0.0, lift, 0.3))
    # The pegs and the boards: two rows, old boards grey and split, the newest black-lettered and bright.
    timber, black = mb.material(pc.M_TIMBER), mb.material(pc.M_LACQUER_BLACK)
    for row_y in (1.62, 1.08):
        x = -hl + 0.35
        while x < hl - 0.5:
            ln = rng.uniform(0.55, 0.95)
            if x + ln > hl - 0.25:
                break
            cx = x + ln * 0.5
            kc.rounded_block(mb, (cx, row_y + 0.06, 0.37), (0.025, 0.025, 0.07), timber, radius=0.01, seg=1)
            tilt = rng.normal(0.0, 0.05)
            fresh = rng.random() < 0.3
            kc.rounded_block(mb, (cx, row_y - 0.06, 0.33), (ln * 0.5, 0.09, 0.018), timber, rot=kc.rot_z(tilt),
                             radius=0.008, seg=1, noise=noise, disp_m=0.004, weather=pc.OLD if not fresh else pc.TOWN,
                             variation=float(rng.random()))
            # The ship's name: a run of short strokes (cut into the old boards, lacquered black on the fresh).
            nstk = int(ln / 0.07)
            for s in range(nstk):
                sx = cx - ln * 0.4 + s * ln * 0.8 / max(nstk - 1, 1)
                h = rng.uniform(0.03, 0.07)
                kc.rounded_block(mb, (sx, row_y - 0.06 + rng.uniform(-0.02, 0.02), 0.35),
                                 (0.006, h, 0.003), black if fresh else timber, rot=kc.rot_z(tilt + rng.normal(0, 0.3)),
                                 radius=0.002, seg=1)
            x += ln + rng.uniform(0.08, 0.2)
    # The lamp niche low in the middle, and frangipani laid along the foot.
    kc.rounded_block(mb, (0.0, 0.62, 0.29), (0.2, 0.17, 0.02), mb.material(pc.M_DARK), radius=0.01, seg=1)
    pc.flame(mb, (0.0, 0.5, 0.25), 0.05, 0.012)
    for k in range(9):
        x = rng.uniform(-hl + 0.3, hl - 0.3)
        kc.rounded_block(mb, (x, 0.03, 0.45 + rng.uniform(0.0, 0.15)), (0.05, 0.02, 0.05), mb.material(pc.M_FLOWER),
                         rot=kc.rot_y(rng.uniform(0, 3)), radius=0.02, seg=1)
    pc.ash_pass(mb, 0, noise, 0.6, vertical=0.12)
    return mb


def crown_bell(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    timber = mb.material(pc.M_TIMBER)
    span = 0.75
    for sx in (-1.0, 1.0):
        kc.rounded_block(mb, (sx * span, 0.1, 0.0), (0.2, 0.1, 0.2), mb.material(pc.M_DRESSED), radius=0.03, seg=1)
        kc.rounded_block(mb, (sx * span, 0.2 + BELL_H_M * 0.5 - 0.1, 0.0), (0.075, BELL_H_M * 0.5 - 0.1, 0.075), timber,
                         radius=0.02, seg=1, noise=None if lod else noise, disp_m=0.005, weather=pc.TOWN)
    beam_y = BELL_H_M - 0.05
    kc.rounded_block(mb, (0.0, beam_y, 0.0), (span + 0.25, 0.08, 0.09), timber, radius=0.02, seg=1)
    # The little hipped roof of fibre thatch; the beam's ends capped in red lacquer.
    roof = kc.MeshBuilder("roof")  # a four-sided cap, turned so its eaves run square to the frame
    props.lathe(roof, [(1.25, beam_y + 0.06), (1.05, beam_y + 0.2), (0.06, beam_y + 0.85)], pc.M_THATCH, rng, sides=4,
                cap_start=True, weather=pc.TOWN)
    mb.merge(roof, kc.rot_y(math.pi * 0.25))
    for sx in (-1.0, 1.0):
        kc.rounded_block(mb, (sx * (span + 0.3), beam_y, 0.0), (0.06, 0.1, 0.1), mb.material(pc.M_LACQUER_RED),
                         radius=0.02, seg=1)
    # The bell: bronze, mouth 0.38 m, hung from the beam by an iron loop.
    prof = [(0.38, 1.2), (0.36, 1.27), (0.3, 1.5), (0.27, 1.75), (0.22, 1.92), (0.08, 1.98)]
    props.lathe(mb, prof, pc.M_COPPER, rng, sides=10 if lod else 24, noise=None if lod else noise, disp_m=0.003,
                cap_start=False, cap_end=True, weather=kc.Weathering(moss=0.1, salt=0.0, wet=0.0, erosion=0.3))
    if not lod:
        a = np.linspace(0.0, 2 * math.pi, 11)
        loop = np.stack([np.cos(a) * 0.07, 2.12 + np.sin(a) * 0.12, np.zeros_like(a)], -1)
        kc.tube(mb, loop, 0.016, 5, mb.material(pc.M_IRON))
        kc.tube(mb, np.array([[0.0, 1.98, 0.0], [0.0, beam_y - 0.08, 0.0]]), 0.02, 6, mb.material(pc.M_IRON))
        # The striker: a short log hung on two fibre ropes beside the bell, swung against its waist.
        for dx in (-0.25, 0.25):
            kc.tube(mb, np.array([[dx, beam_y - 0.05, 0.42], [dx, 1.55, 0.48]]), 0.012, 4, mb.material(pc.M_THATCH))
        kc.tube(mb, np.array([[-0.45, 1.52, 0.5], [0.45, 1.52, 0.5]]), np.array([0.07, 0.065]), 10, timber,
                cap_start=True, cap_end=True, noise=noise, disp_m=0.006)
        pc.ash_pass(mb, 0, noise, 0.6, vertical=0.1)
    return mb


def flank_rocks(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    stone, soil, scrub = mb.material(pc.M_STONE), mb.material(pc.M_SOIL), mb.material(pc.M_STUBBLE)
    # Boulders: a few big ones, more small, each half sunk.
    for k in range(5 if lod else 18):
        big = k < 4
        r = float(rng.uniform(0.9, 1.8) if big else rng.uniform(0.25, 0.7))
        x, z = float(rng.uniform(-6.0, 6.0)), float(rng.uniform(-4.0, 4.0))
        kc.rounded_block(mb, (x, r * 0.25, z), (r * rng.uniform(0.9, 1.4), r * 0.6, r * rng.uniform(0.8, 1.2)),
                         stone, rot=kc.rot_y(rng.uniform(0, 3.1)) @ kc.rot_z(rng.normal(0, 0.15)),
                         radius=r * 0.35, seg=1 if lod else 2, noise=None if lod else noise, disp_m=r * 0.12,
                         disp_period_m=r * 0.8, variation=float(rng.random()))
    if lod:  # two scrub cards, so LOD1 keeps LOD0's slots
        for x, z in ((-3.0, 1.0), (2.5, -2.0)):
            g = np.array([[[x - 0.3, 0.0, z], [x + 0.3, 0.0, z]], [[x - 0.1, 0.45, z], [x + 0.1, 0.45, z]]])
            kc.quad_strip(mb, g, scrub, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]), col=(0.5, 0.3, 0.5, 0.4),
                          uv2=(0.9, 0.5), smooth=False)
    if not lod:
        # Scree: a fan of fist-to-head stones below the big boulders.
        for k in range(40):
            s_ = float(rng.uniform(0.06, 0.18))
            x, z = float(rng.normal(0.0, 3.0)), float(rng.uniform(0.0, 4.5))
            kc.rounded_block(mb, (x, s_ * 0.4, z), (s_, s_ * 0.6, s_ * 0.8), stone, rot=kc.rot_y(rng.uniform(0, 3)),
                             radius=s_ * 0.4, seg=1, variation=float(rng.random()))
        # Dry scrub: crossed blade cards in the hollows.
        for k in range(22):
            x, z = float(rng.uniform(-6.5, 6.5)), float(rng.uniform(-4.5, 4.5))
            h = float(rng.uniform(0.25, 0.6))
            for j in range(5):
                th = j * math.pi / 5 + float(rng.uniform(0, 0.4))
                d = np.array([math.cos(th), 0.0, math.sin(th)]) * 0.18
                base = np.array([x, 0.0, z])
                lean = np.array([rng.normal(0, 0.08), h, rng.normal(0, 0.08)])
                g = np.array([[base - d, base + d], [base - d * 0.3 + lean, base + d * 0.3 + lean]])
                kc.quad_strip(mb, g, scrub, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]),
                              col=(0.5, 0.3, 0.5, 0.4), uv2=(0.9, float(rng.random())), smooth=False)
                kc.quad_strip(mb, g, scrub, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]),
                              col=(0.5, 0.3, 0.5, 0.4), uv2=(0.9, float(rng.random())), flip=True, smooth=False)
    # Ash patches: low dark lenses where the soil shows through.
    for k in range(2 if lod else 6):
        x, z = float(rng.uniform(-5.0, 5.0)), float(rng.uniform(-3.5, 3.5))
        kc.rounded_block(mb, (x, 0.0, z), (rng.uniform(1.0, 2.2), 0.05, rng.uniform(0.8, 1.6)), soil,
                         rot=kc.rot_y(rng.uniform(0, 3)), radius=0.04, seg=1)
    return mb


TARGETS = {
    "harbour_quay": lambda: [quay("harbour_quay", 741), quay("harbour_quay", 741, lod=True)],
    "sea_cut_weir": lambda: [weir("sea_cut_weir", 742), weir("sea_cut_weir", 742, lod=True)],
    "wake_wall": lambda: [wake_wall("wake_wall", 743), wake_wall("wake_wall", 743, lod=True)],
    "crown_bell": lambda: [crown_bell("crown_bell", 744), crown_bell("crown_bell", 744, lod=True)],
    "flank_rocks": lambda: [flank_rocks("flank_rocks", 745), flank_rocks("flank_rocks", 745, lod=True)],
}
