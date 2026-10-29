"""Shared helpers for the Brightwater ferry kit (M3-ENV-08; docs/kb/art/environments/brightwater_ferry.md).

The geometry core is the Haluna kit's (assets_src/environments/kits/haluna/kit_common.py: MeshBuilder, the
weathering channels, the primitives, the glTF export), imported read-only, as is the Brine Shoals kit's
heightfield helper (bs_common.heightfield, for the reef). Coordinates are Godot's (metres, +Y up, +X east,
-Z north); a ship's frame has its bow to -Z and its origin on the centre line at main-deck level amidships.
Vertex colours follow haluna.md §4: R moss, G salt, B wet, A erosion.

What this module adds:
* `HullForm` and `hull_shell`: one parametric plank-built hull (sections, sheer, deck heights, bulwark with
  its stanchions, three inner strakes, cap rail and covering board, deck planks over dark seams) used for the
  ferry *and* the drowned hulls, so the ferry and the derelicts (and M3-ENV-06's `arena_derelict_deck`, whose
  plank, seam and bulwark proportions it repeats) read as ships of one sea;
* `cloth`: a double-sided cloth sheet (sails, the awning, tarpaulins; the shaders cull back faces);
* `rope`: a sagging line; `lathe`: a surface of revolution (jars, the lantern's glass, posts);
* the slot renaming that gives every piece this kit's own `bf_*` material slots.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
for _p in (HERE.parent / "haluna", HERE.parent / "brine_shoals"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import bs_common as bsc  # noqa: E402,F401  (the Brine Shoals kit's heightfield, read-only)
import kit_common as kc  # noqa: E402  (the Haluna kit's core, read-only)

# ---------------------------------------------------------------------------------------------
# Material slots (bf_materials.py writes one .tres per slot)
# ---------------------------------------------------------------------------------------------
M_DECK = "bf_deck"
M_TIMBER = "bf_timber"
M_TAR = "bf_timber_tar"
M_BLUE = "bf_paint_blue"
M_LIME = "bf_limewash"
M_RED = "bf_lacquer_red"
M_CARVED = "bf_carved"
M_CANVAS = "bf_canvas"
M_CANVAS_BLUE = "bf_canvas_blue"
M_AWNING = "bf_canvas_awning"
M_TARP = "bf_tarpaulin"
M_ROPE = "bf_rope"
M_IRON = "bf_iron"
M_BRASS = "bf_brass"
M_GLASS = "bf_lamp_glass"
M_WINDOW = "bf_window_glow"
M_DARK = "bf_interior_dark"
M_MARBLE = "bf_marble"
M_INDIGO = "bf_cloth_indigo"
M_SAND = "bf_cloth_sand"
M_CLOTH_RED = "bf_cloth_red"
M_BASKET = "bf_basket"
M_CLAY = "bf_earthenware"
M_WRECK = "bf_wreck_timber"
M_WRECK_TAR = "bf_wreck_tar"
M_WRECK_CANVAS = "bf_wreck_canvas"
M_REEF = "bf_reef"
M_ISLET = "bf_islet_rock"

# Haluna generator slots reused (the lintel-gull carving) -> this kit's slots.
RENAME = {"kit_carved_wood": M_CARVED, "kit_timber": M_TIMBER, "kit_lashing": M_ROPE}

# Slots that emit light (only the lanterns' glass and the deckhouse windows; never on a drowned hull), and the
# Spar-Wraith's membrane seams on the Seventh Terrace (M3-ENV-08B: spawn_wound, Ch4 only).
EMISSIVE = (M_GLASS, M_WINDOW, "bf_spawn_wound")

# Weathering presets (vertex-colour multipliers, kit_common.Weathering). No moss at sea.
DECK_W = kc.Weathering(moss=0.0, salt=0.35, wet=0.04, erosion=0.45, noise_scale_m=0.9)
RAIL_W = kc.Weathering(moss=0.0, salt=0.3, wet=0.05, erosion=0.6)
HULL_W = kc.Weathering(moss=0.0, salt=0.4, wet=0.25, erosion=0.5)
CLOTH_W = kc.Weathering(moss=0.0, salt=0.25, wet=0.0, erosion=0.3)
IRON_W = kc.Weathering(moss=0.0, salt=0.3, wet=0.3, erosion=0.3)
WRECK_W = kc.Weathering(moss=0.0, salt=0.8, wet=0.4, erosion=0.9, noise_scale_m=0.8)

LOD = "-lod1"

# ---------------------------------------------------------------------------------------------
# The ferry's frame (brightwater_ferry.md §0)
# ---------------------------------------------------------------------------------------------
WATERLINE_Y = -1.6  # in the ship's frame; the preview floats her with the main deck at world y +1.6
FOREMAST_Z = -8.0
MAINMAST_Z = 2.4
FOREMAST_H = 11.5
MAINMAST_H = 14.5
GANGWAY_Z = (-2.6, -1.6)
BOWSPRIT_X = 0.32  # the bowsprit lies beside the stem head (to starboard), clear of the stem-gull
POOP_Z = 7.6
POOP_Y = 0.9
POOP_SWEEP_M = 2.4  # the sheer's sweep up to the poop's rail
RAIL_H = 0.95
PLANK_W_M = 0.2
PLANK_GAP_M = 0.014
PLANK_T_M = 0.07
STANCHION_STEP_M = 1.2
SHROUD_LEAD_M = (0.0, 0.7, 1.4)  # the shrouds' chain-plates, aft of their mast
CHAIN_OUT_M = 0.3  # chain-plates outside the bulwark's inner face
MAIN_HATCH = (0.0, 0.2, 1.1, 0.9, 0.45)  # x, z, half x, half z, coaming height
FORE_HATCH = (0.0, -10.2, 0.6, 0.6, 0.35)
DECKHOUSE = (-1.9, 1.9, 3.4, 7.4, 2.1)  # x0, x1, z0, z1, wall height


@dataclass(frozen=True)
class HullForm:
    """One plank-built hull. z runs from the stem (forward, -Z) to the transom; the main deck is y 0."""

    stem_z: float = -14.0
    transom_z: float = 12.6
    half_beam: float = 3.4  # the bulwark's inner face, amidships
    taper_fwd_z: float = -5.0
    taper_aft_z: float = 7.0
    transom_half: float = 2.7
    keel_y: float = -2.4
    poop_z: float | None = POOP_Z
    poop_y: float = POOP_Y
    rail_h: float = RAIL_H
    bow_rise: float = 1.05  # the sheer's rise at the stem
    sheer_sag: float = 0.22  # the sheer's sweep: lowest amidships, rising this much at either end
    forefoot_m: float = 2.2  # the forefoot cut away: the stem rakes aft this far from the sheer to the keel
    wale_y: float = -0.35  # tar below, paint above
    gangways: tuple = (GANGWAY_Z,)
    bulwark_t: float = 0.22  # inner face to the outer planking
    poop_planking_h: float = 0.35  # on the poop the planking stops this high; an open quarter rail stands above

    def half_beam_at(self, z) -> np.ndarray:
        z = np.asarray(z, float)
        fwd = np.clip((z - self.taper_fwd_z) / (self.stem_z - self.taper_fwd_z), 0.0, 1.0)
        aft = np.clip((z - self.taper_aft_z) / (self.transom_z - self.taper_aft_z), 0.0, 1.0)
        hb = self.half_beam * np.sqrt(np.maximum(1.0 - fwd ** 2.2, 0.0))
        hb = hb - (self.half_beam - self.transom_half) * aft ** 2
        return np.maximum(hb, 0.06)

    def deck_y(self, z) -> np.ndarray:
        z = np.asarray(z, float)
        if self.poop_z is None:
            return np.zeros_like(z)
        return np.where(z >= self.poop_z, self.poop_y, 0.0)

    def sheer_y(self, z) -> np.ndarray:
        """The hull planking's top edge: lowest amidships (the sag), rising toward the stem, and sweeping up over the
        last POOP_SWEEP_M before the poop's break to the poop's planking (poop_planking_h above the poop deck)."""
        z = np.asarray(z, float)
        fwd = np.clip((self.taper_fwd_z - z) / (self.taper_fwd_z - self.stem_z), 0.0, 1.0)
        aft = 0.0
        if self.poop_z is not None:
            lift = self.poop_y + self.poop_planking_h - self.rail_h
            aft = lift * kc.smoothstep(self.poop_z - POOP_SWEEP_M, self.poop_z, z)
        return self.rail_h + self.bow_rise * fwd ** 2 + aft + self._sag(z)

    def _sag(self, z) -> np.ndarray:
        mid = 0.5 * (self.stem_z + self.transom_z)
        return self.sheer_sag * ((np.asarray(z, float) - mid) / (0.5 * (self.transom_z - self.stem_z))) ** 2

    def rail_y(self, z) -> np.ndarray:
        """The cap rail's top: the planking's top on the main deck; on the poop an open quarter rail at rail_h."""
        z = np.asarray(z, float)
        if self.poop_z is None:
            return self.sheer_y(z)
        return np.where(z >= self.poop_z, self.poop_y + self.rail_h + self._sag(z), self.sheer_y(z))

    def forefoot_dz(self, z: float, y) -> np.ndarray:
        """How far aft the hull's surface at station z, height y, is moved so the stem rakes: nothing at the
        sheer, most at the keel, only forward of the taper (the deck and bulwarks keep their stations)."""
        fwd = float(np.clip((self.taper_fwd_z - z) / (self.taper_fwd_z - self.stem_z), 0.0, 1.0))
        top = float(self.sheer_y(z))
        s = np.clip((np.asarray(y, float) - self.keel_y) / (top - self.keel_y), 0.0, 1.0)
        return self.forefoot_m * fwd ** 2 * (1.0 - s) ** 1.6

    def in_gangway(self, z: float) -> bool:
        return any(a <= z <= b for a, b in self.gangways)

    def section_x(self, z: float, y: np.ndarray) -> np.ndarray:
        """The hull's outer half-width at heights y (from the keel to the sheer) at station z: a round bilge, a
        firm side and a little tumblehome near the rail; fine toward the stem."""
        w = float(self.half_beam_at(z)) + self.bulwark_t
        top = float(self.sheer_y(z))
        s = np.clip((np.asarray(y, float) - self.keel_y) / (top - self.keel_y), 0.0, 1.0)
        f = np.sqrt(np.maximum(1.0 - (1.0 - s) ** 3, 0.0))
        f = f * (1.0 - 0.04 * kc.smoothstep(0.82, 1.0, s))
        return w * f


def rows_between(z0: float, z1: float, step: float) -> np.ndarray:
    n = max(2, int(math.ceil((z1 - z0) / step)) + 1)
    return np.linspace(z0, z1, n)


def hull_spans(form: HullForm) -> list[tuple[float, float, bool]]:
    """(z0, z1, is_gangway) spans of the hull side, split at the gangways and the poop break so each span's top
    edge is continuous."""
    cuts = [form.stem_z + 0.02, form.transom_z]
    for a, b in form.gangways:
        cuts += [a, b]
    if form.poop_z is not None:
        cuts.append(form.poop_z)
    cuts = sorted(set(round(c, 6) for c in cuts))
    out = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        out.append((a, b, form.in_gangway(0.5 * (a + b))))
    return out


def hull_sides(mb: kc.MeshBuilder, form: HullForm, *, lod: bool, tar: str, paint: str, ragged=None,
               noise: kc.Noise3 | None = None, weather: kc.Weathering = HULL_W, inner: str | None = None) -> None:
    """Both hull sides from the keel to the sheer (tar below the wale, `paint` above), span by span; the
    gangways drop the top edge to a low sill. `ragged(z, side) -> metres` lowers the top edge (a stove-in
    bulwark). `inner` adds the planking's inside face in that slot (a hull broken open, seen from within)."""
    step = 1.6 if lod else 0.42
    i_tar, i_paint = mb.material(tar), mb.material(paint)
    for z0, z1, gang in hull_spans(form):
        zs = rows_between(z0, z1, step)
        for side in (-1.0, 1.0):
            for lo_frac, hi_frac, mat in ((0.0, None, i_tar), (None, 1.0, i_paint)):
                rows = []
                for z in zs:
                    z = float(z)
                    top = float(form.deck_y(z)) + 0.14 if gang else float(form.sheer_y(z))
                    if ragged is not None:
                        top -= float(ragged(z, side))
                    wale = min(form.wale_y, top - 0.05)
                    y0 = form.keel_y if lo_frac is not None else wale
                    y1 = wale if hi_frac is None else top
                    ys = np.linspace(y0, y1, 3 if lod else (9 if lo_frac is not None else 6))
                    # x is the section's width at the true sheer, so a gangway's sill keeps the hull's line.
                    xs = form.section_x(z, ys) if not gang else _sill_x(form, z, ys)
                    rows.append(np.stack([side * xs, ys, z + form.forefoot_dz(z, ys)], axis=-1))
                grid = np.asarray(rows)
                if noise is not None and not lod:
                    grid[..., 0] += side * (noise.fbm(grid / 0.7, 2) - 0.5) * 0.02
                rr, cc = grid.shape[:2]
                br = noise.fbm(grid / weather.noise_scale_m, 2) if noise is not None else np.full((rr, cc), 0.5)
                wet = np.clip((form.wale_y + 0.6 - grid[..., 1]) / 1.2, 0.0, 1.0) * weather.wet * (0.6 + 0.8 * br)
                col = np.stack([np.zeros((rr, cc)), weather.salt * (0.3 + 0.7 * br), np.clip(wet, 0, 1),
                                weather.erosion * (0.4 + 0.6 * br)], axis=-1)
                uv = np.stack([grid[..., 2], grid[..., 1]], axis=-1)
                ao = np.clip(0.7 + 0.3 * (grid[..., 1] - form.keel_y) / 3.0, 0.4, 1.0)
                uv2 = np.stack([ao, np.full((rr, cc), 0.5)], axis=-1)
                _surface(mb, grid, mat, outward=np.array([side, 0.0, 0.0]), uv=uv, col=col, uv2=uv2)
                if inner is not None:
                    skin = grid.copy()
                    skin[..., 0] *= 0.95
                    _surface(mb, skin, mb.material(inner), outward=np.array([-side, 0.0, 0.0]), uv=uv, col=col,
                             uv2=uv2 * np.array([0.6, 1.0]))


def _sill_x(form: HullForm, z: float, ys: np.ndarray) -> np.ndarray:
    top = float(form.sheer_y(z))
    w = float(form.half_beam_at(z)) + form.bulwark_t
    s = np.clip((ys - form.keel_y) / (top - form.keel_y), 0.0, 1.0)
    return w * np.sqrt(np.maximum(1.0 - (1.0 - s) ** 3, 0.0))


def _surface(mb: kc.MeshBuilder, grid: np.ndarray, mat: int, *, outward, uv, col, uv2, smooth: bool = True) -> None:
    """A (rows, cols, 3) grid whose normals face `outward` (the winding chosen from the grid itself)."""
    g = np.asarray(grid, float)
    nrm = np.cross(np.gradient(g, axis=1), np.gradient(g, axis=0))
    flip = float(np.sum(nrm * np.broadcast_to(np.asarray(outward, float), g.shape))) < 0.0
    kc.quad_strip(mb, g, mat, uv=uv, col=col, uv2=uv2, flip=flip, smooth=smooth)


def transom(mb: kc.MeshBuilder, form: HullForm, mat: str, *, lod: bool) -> None:
    """The flat transom closing the stern: a fan over the section outline at z = transom_z."""
    z = form.transom_z
    ys = np.linspace(form.keel_y, float(form.sheer_y(z)), 4 if lod else 10)
    xs = form.section_x(z, ys)
    pts = [np.array([-x, y, z]) for x, y in zip(xs[::-1], ys[::-1])] + [np.array([x, y, z]) for x, y in zip(xs, ys)]
    c = np.mean(pts, axis=0)
    i = mb.material(mat)
    base = mb.add_vertices(np.vstack([pts, c[None]]), np.tile([0.0, 0.0, 1.0], (len(pts) + 1, 1)),
                           np.asarray([[p[0], p[1]] for p in pts] + [[c[0], c[1]]]), (0.8, 0.5), (0.0, 0.4, 0.1, 0.5))
    n = len(pts)
    for k in range(n - 1):
        mb.add_tri(base + k, base + k + 1, base + n, i)  # wound to face +z (astern), with its normals


def deck_planks(mb: kc.MeshBuilder, form: HullForm, rng, noise, z_from: float, z_to: float, y_top: float, *, mat: str,
                holes: float = 0.0, keep_out=(), weather: kc.Weathering = DECK_W, ragged_end: bool = False) -> None:
    """Deck planks fore and aft between z_from and z_to, butts staggered, clipped to the hull's outline (inside the
    covering board). `holes` is the fraction of lengths left out (a wreck); `keep_out` are (x0, x1, z0, z1)
    rectangles with no planks (hatches)."""
    i_mat = mb.material(mat)
    pitch = PLANK_W_M + PLANK_GAP_M
    half = float(form.half_beam) - 0.34
    n = int(half * 2.0 / pitch)
    x0 = -n * pitch * 0.5 + pitch * 0.5
    for k in range(n):
        x = x0 + k * pitch
        z_a = z_from
        while z_a < z_to and float(form.half_beam_at(z_a)) - 0.34 < abs(x) + PLANK_W_M * 0.5:
            z_a += 0.2
        z_b = z_to
        while z_b > z_a and float(form.half_beam_at(z_b)) - 0.34 < abs(x) + PLANK_W_M * 0.5:
            z_b -= 0.2
        if z_b - z_a < 0.3:
            continue
        cuts = [z_a]
        z = z_a + float(rng.uniform(0.6, 5.0))
        while z < z_b - 0.5:
            cuts.append(z)
            z += float(rng.uniform(4.0, 6.5))
        cuts.append(z_b)
        segs = []
        for a, b in zip(cuts[:-1], cuts[1:]):
            # Split around keep-out rectangles.
            pieces = [(a, b)]
            for kx0, kx1, kz0, kz1 in keep_out:
                if kx0 - PLANK_W_M * 0.5 < x < kx1 + PLANK_W_M * 0.5:
                    nxt = []
                    for pa, pb in pieces:
                        if pb <= kz0 or pa >= kz1:
                            nxt.append((pa, pb))
                            continue
                        if pa < kz0:
                            nxt.append((pa, kz0))
                        if pb > kz1:
                            nxt.append((kz1, pb))
                    pieces = nxt
            segs += pieces
        for a, b in segs:
            if ragged_end and b >= z_to - 0.01:
                b -= float(rng.uniform(0.0, 1.8))
            if b - a < 0.25:
                continue
            roll = float(rng.random())
            if holes > 0.0 and roll < holes:
                continue
            dy = float(rng.uniform(-0.004, 0.0))
            ya = y_top - PLANK_T_M * 0.5 + dy
            kc.plank(mb, (x, ya, b - 0.006), (x, ya, a + 0.006), PLANK_W_M, PLANK_T_M, i_mat, weather=weather,
                     variation=float(rng.random()), noise=noise)


def sub_deck(mb: kc.MeshBuilder, form: HullForm, z_from: float, z_to: float, y: float, mat: str) -> None:
    """The dark caulking under the planks (what the seams show), one strip across the beam."""
    zs = rows_between(z_from, z_to, 1.0)
    rows = []
    for z in zs:
        hw = max(float(form.half_beam_at(float(z))) - 0.05, 0.05)
        rows.append([[x, y, float(z)] for x in np.linspace(-hw, hw, 3)])
    grid = np.asarray(rows, float)
    _surface(mb, grid, mb.material(mat), outward=kc.UP, uv=grid[..., [0, 2]], col=(0.0, 0.2, 0.0, 0.3),
             uv2=(0.4, 0.5), smooth=False)


def covering_board(mb: kc.MeshBuilder, form: HullForm, rng, noise, side: float, z_from: float, z_to: float, *,
                   mat: str, weather: kc.Weathering = RAIL_W) -> None:
    i = mb.material(mat)
    zs = rows_between(z_from, z_to, 1.4)
    for a, b in zip(zs[:-1], zs[1:]):
        ya, yb = float(form.deck_y(float(a))), float(form.deck_y(float(b)))
        if ya != yb:
            continue
        xa = side * (float(form.half_beam_at(float(a))) - 0.17)
        xb = side * (float(form.half_beam_at(float(b))) - 0.17)
        kc.plank(mb, (xb, ya - 0.03, float(b)), (xa, ya - 0.03, float(a)), 0.36, 0.09, i, weather=weather,
                 variation=float(rng.random()), noise=noise)


def bulwark(mb: kc.MeshBuilder, form: HullForm, rng, noise, side: float, z_from: float, z_to: float, *, lod: bool,
            timber: str, lining: str, gone=None, weather: kc.Weathering = RAIL_W) -> None:
    """The bulwark's inside along one side between z_from and z_to: the lining (the planking's inner face),
    stanchions every STANCHION_STEP_M, three inner strakes and the cap rail, skipping the gangways. `gone(z)`
    True leaves a stretch out (a wreck's stove-in bulwark; stumps stand)."""
    i_t, i_l = mb.material(timber), mb.material(lining)

    def missing(z: float) -> bool:
        return form.in_gangway(z) or (gone is not None and gone(z))

    # Lining: one strip per continuous stretch.
    zs = rows_between(z_from, z_to, 1.6 if lod else 0.6)
    run: list[float] = []
    stretches: list[list[float]] = []
    for z in zs:
        if missing(float(z)):
            if len(run) > 1:
                stretches.append(run)
            run = []
        else:
            run.append(float(z))
    if len(run) > 1:
        stretches.append(run)
    for st in stretches:
        rows = []
        for z in st:
            d = float(form.deck_y(z))
            top = float(form.sheer_y(z)) - 0.06
            x = side * (float(form.half_beam_at(z)) + 0.03)
            rows.append([[x, y, z] for y in np.linspace(d, top, 2 if lod else 3)])
        grid = np.asarray(rows, float)
        _surface(mb, grid, i_l, outward=np.array([-side, 0.0, 0.0]), uv=grid[..., [2, 1]],
                 col=(0.0, weather.salt * 0.5, 0.0, weather.erosion * 0.5), uv2=(0.85, float(rng.random())))
    # Stanchions.
    z = z_from + 0.3
    while z < z_to - 0.2:
        if not missing(z):
            d = float(form.deck_y(z))
            top = float(form.rail_y(z))
            x = side * (float(form.half_beam_at(z)) - 0.02)
            if lod:
                kc.rounded_block(mb, (x, (d + top) * 0.5, z), (0.06, (top - d) * 0.5, 0.06), i_t, seg=1, radius=0.01)
            else:
                kc.tube(mb, np.array([[x, d - 0.04, z], [x, top, z]]), 0.065, 4, i_t, weather=weather, noise=noise,
                        disp_m=0.006, variation=float(rng.random()), cap_end=True)
        elif gone is not None and gone(z) and not form.in_gangway(z) and not lod:
            d = float(form.deck_y(z))
            x = side * (float(form.half_beam_at(z)) - 0.02)
            kc.tube(mb, np.array([[x, d - 0.04, z], [x, d + float(rng.uniform(0.2, 0.55)), z]]), 0.065, 4, i_t,
                    weather=weather, variation=float(rng.random()), cap_end=True)
        z += STANCHION_STEP_M
    # Cap rail and strakes, metre by metre.
    zs = rows_between(z_from, z_to, 1.6 if lod else 0.8)
    for a, b in zip(zs[:-1], zs[1:]):
        a, b = float(a), float(b)
        if missing(0.5 * (a + b)) or missing(a + 0.05) or missing(b - 0.05):
            continue
        if float(form.deck_y(a)) != float(form.deck_y(b)):
            continue
        xa = side * (float(form.half_beam_at(a)) + 0.09)
        xb = side * (float(form.half_beam_at(b)) + 0.09)
        kc.plank(mb, (xb, float(form.rail_y(b)) + 0.03, b), (xa, float(form.rail_y(a)) + 0.03, a), 0.3, 0.07, i_t,
                 weather=weather, variation=float(rng.random()), noise=None if lod else noise)
        if lod:
            continue
        d = float(form.deck_y(a))
        plank_top = float(min(form.sheer_y(a), form.sheer_y(b)))
        xa = side * float(form.half_beam_at(a))
        xb = side * float(form.half_beam_at(b))
        for h in (0.16, 0.42, 0.68):
            if d + h < plank_top - 0.08:
                kc.plank(mb, (xb, d + h, b), (xa, d + h, a), 0.16, 0.035, i_t, up=(side, 0.0, 0.0), weather=weather,
                         variation=float(rng.random()))
        open_h = float(form.rail_y(a)) - plank_top
        if open_h > 0.3:  # the open quarter rail: a capping on the planking and a mid rail
            for y in (plank_top + 0.02, plank_top + open_h * 0.5):
                kc.plank(mb, (xb, y, b), (xa, y, a), 0.1, 0.05, i_t, weather=weather, variation=float(rng.random()))


# ---------------------------------------------------------------------------------------------
# Cloth, rope, lathe
# ---------------------------------------------------------------------------------------------
def cloth(mb: kc.MeshBuilder, grid: np.ndarray, mat: str, *, uv: np.ndarray, weather: kc.Weathering = CLOTH_W,
          noise: kc.Noise3 | None = None, variation: float = 0.5, thick: float = 0.008, back: str | None = None,
          ao: float = 0.95) -> None:
    """A cloth sheet seen from both sides: the front grid and a back copy `thick` behind it with the winding
    reversed (the weathering shaders cull back faces). `back` gives the back face another slot."""
    g = np.asarray(grid, float)
    rr, cc = g.shape[:2]
    br = noise.fbm(g / weather.noise_scale_m, 2) if noise is not None else np.full((rr, cc), 0.5)
    low = np.clip(1.0 - (g[..., 1] - g[..., 1].min()) / max(float(np.ptp(g[..., 1])), 1e-6), 0.0, 1.0)
    col = np.stack([np.zeros((rr, cc)), np.clip(weather.salt * (0.2 + 0.8 * low) * (0.5 + br), 0, 1),
                    np.clip(weather.wet * br, 0, 1), np.clip(weather.erosion * (0.4 + 0.6 * br), 0, 1)], axis=-1)
    uv2 = np.stack([np.full((rr, cc), ao), np.full((rr, cc), variation)], axis=-1)
    i_f = mb.material(mat)
    i_b = mb.material(back or mat)
    start_v, start_t = mb.vertex_count, mb.triangle_count
    kc.quad_strip(mb, g, i_f, uv=uv, col=col, uv2=uv2, flip=False)
    nrm = np.asarray(mb.nrm[start_v:], float).reshape(rr, cc, 3)
    del start_t
    kc.quad_strip(mb, g - nrm * thick, i_b, uv=uv, col=col, uv2=uv2, flip=True)


def rope(mb: kc.MeshBuilder, a, b, radius: float, mat: str, *, sag: float = 0.0, segs: int = 6, sides: int = 4,
         weather: kc.Weathering = CLOTH_W, variation: float = 0.5) -> None:
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    t = np.linspace(0.0, 1.0, max(segs, 1) + 1)
    pts = a[None, :] + (b - a)[None, :] * t[:, None]
    pts[:, 1] -= 4.0 * sag * t * (1.0 - t)
    kc.tube(mb, pts, radius, sides, mb.material(mat), weather=weather, variation=variation)


def lathe(mb: kc.MeshBuilder, center, profile, sides: int, mat: str, *, axis=None, weather: kc.Weathering = RAIL_W,
          variation: float = 0.5, cap_top: bool = False) -> None:
    """A surface of revolution: `profile` is [(radius, height), ...] from bottom to top about `axis` (default
    +Y) through `center`."""
    prof = np.asarray(profile, float)
    c = np.asarray(center, float)
    ax = kc.UP if axis is None else kc.normalize(np.asarray(axis, float))
    centers = c[None, :] + prof[:, 1:2] * ax[None, :]
    kc.tube(mb, centers, prof[:, 0], sides, mb.material(mat), weather=weather, variation=variation,
            cap_end=cap_top, first_normal=kc.any_perpendicular(ax))


def finalize(mb: kc.MeshBuilder) -> kc.MeshBuilder:
    """Renames reused Haluna slots to this kit's, merges duplicates and drops unused slots."""
    names = [RENAME.get(m, m) for m in mb.materials]
    uniq: list[str] = []
    for n in names:
        if n not in uniq:
            uniq.append(n)
    remap = [uniq.index(n) for n in names]
    mb.tri_mat = [remap[m] for m in mb.tri_mat]
    mb.materials = uniq
    used = sorted(set(mb.tri_mat))
    if len(used) != len(mb.materials):
        keep = {old: new for new, old in enumerate(used)}
        mb.materials = [mb.materials[i] for i in used]
        mb.tri_mat = [keep[m] for m in mb.tri_mat]
    return mb


def chain_points(form: HullForm, mast_z: float, side: float) -> list[np.ndarray]:
    """Where a mast's shrouds come down on one side: the deadeyes just above the cap rail, outside it."""
    out = []
    for dz in SHROUD_LEAD_M:
        z = mast_z + dz
        out.append(np.array([side * (float(form.half_beam_at(z)) + CHAIN_OUT_M), float(form.sheer_y(z)) + 0.12, z]))
    return out


FERRY = HullForm()
