"""Shared helpers for the Pemakar procedural kit (M3-ENV-03, pemakar.md). Pure numpy, like the Haluna kit.

The geometry primitives, the deterministic rng and the Blender export are the Haluna kit's
(`assets_src/environments/kits/haluna/kit_common.py`), imported read-only. Every Pemakar module is
named `pemakar_*` so it never shadows a Haluna module of the same name in one Python process (the
unit tests load both kits).

Coordinates are Godot's (metres, +Y up, +X east, -Z north). Vertex colours keep the cross-role
convention (haluna.md §4: R moss, G salt, B wet, A erosion), but in Pemakar the salt channel is
written as **ash fall** (pemakar.md §4): `ash_pass` repaints G after a piece is built, from the
upward-facing normal times noise, so ash lies on every top, ledge and lintel and thins on verticals.

The terrace anchor (pemakar.md §0): a tier module's origin is the front edge of its tread at tread
height. The retaining wall hangs below it (y 0 .. -WALL_H_M, battered out towards +Z), the tread runs
back to z = -TREAD_D_M, and the channel runs along the tread's front at z = -CHANNEL_Z_M.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
HALUNA = HERE.parent / "haluna"
if str(HALUNA) not in sys.path:
    sys.path.append(str(HALUNA))  # appended, so a Pemakar module always wins a name lookup

import kit_common as kc  # noqa: E402  (Haluna's shared helpers, read-only)

# --- Material slots (pemakar_materials.py writes one .tres per name) --------------------------------
M_STONE = "kit_volcanic_stone"
M_DRESSED = "kit_volcanic_dressed"
M_FAR = "kit_volcanic_far"
M_BRICK = "kit_laterite_brick"
M_SOIL = "kit_ash_soil"
M_THATCH = "kit_fibre_thatch"
M_TIMBER = "kit_timber_dark"
M_RIDGE = "kit_laterite_tile"
M_COPPER = "kit_copper_vein"
M_COPPER_RAW = "kit_copper_raw"
M_IRON = "kit_iron"
M_LACQUER_RED = "kit_lacquer_red"
M_LACQUER_BLACK = "kit_lacquer_black"
M_GOLD = "kit_gold_leaf"
M_WATER = "kit_channel_water"
M_PADDY = "kit_paddy_water"
M_SPILL = "kit_water_spill"
M_LEAF = "kit_leaf_boat"
M_RICE = "kit_rice"
M_STUBBLE = "kit_rice_stubble"
M_FLAME = "kit_wick_flame"
M_FORGE = "kit_forge_glow"
M_SOOT = "kit_soot"
M_DARK = "kit_interior_dark"
M_PLUME = "kit_plume"
M_FLOWER = "kit_frangipani_offering"

# Haluna slot names that re-used Haluna builders write, and the Pemakar slot each becomes.
HALUNA_SLOTS = {
    "kit_thatch": M_THATCH,
    "kit_timber": M_TIMBER,
    "kit_mortar_white": M_RIDGE,
    "kit_roof_tile": M_RIDGE,
    "kit_leaf_boat": M_LEAF,
    "kit_garland": M_FLOWER,
    "kit_garland_throat": M_FLOWER,
    "kit_shrine_stone": M_DRESSED,
    "kit_coral_stone": M_STONE,
    "kit_lashing": M_TIMBER,
}

# --- Terrace module (pemakar.md §0, §2.1) --------------------------------------------------------
MODULE_M = 4.0  # length of a wall / tread / channel module along the contour
WALL_H_M = 2.4  # one tier's rise
BATTER_DEG = 6.0
TREAD_D_M = 7.0  # tread depth, front edge to the next wall's foot
COPING_D_M = 0.42
COPING_H_M = 0.22
CHANNEL_Z_M = 0.69  # channel centre line behind the tread's front edge
CHANNEL_IN_M = 0.36  # inside width
CHANNEL_KERB_M = 0.15  # kerb width
CHANNEL_TOP_M = 0.15  # kerb top above the tread
CHANNEL_WATER_M = 0.10  # water surface above the tread
CROSS_LEN_M = 4.8  # the cross channel from a spill's catch basin to the next channel's inlet
SPILL_BASIN_Z_M = 0.8  # catch-basin centre in front of the wall, in the upper tier's frame

# --- Weathering presets ---------------------------------------------------------------------------
# Ash lives in G (written by ash_pass); these only scale the generator's other channels.
TERRACE = kc.Weathering(moss=0.35, salt=0.0, wet=0.0, erosion=0.55, noise_scale_m=0.7)
DRESSED = kc.Weathering(moss=0.25, salt=0.0, wet=0.0, erosion=0.35, noise_scale_m=0.5)
WASHED = kc.Weathering(moss=0.15, salt=0.0, wet=0.05, erosion=0.45, noise_scale_m=0.4)  # channel kerbs
TOWN = kc.Weathering(moss=0.15, salt=0.0, wet=0.0, erosion=0.4, noise_scale_m=0.6)
OLD = kc.Weathering(moss=0.55, salt=0.0, wet=0.0, erosion=0.85, noise_scale_m=0.6)  # old graves
FAR = kc.Weathering(moss=0.7, salt=0.0, wet=0.0, erosion=0.5, noise_scale_m=18.0)


def ash_pass(mb: kc.MeshBuilder, start_v: int, noise: kc.Noise3, amount: float, *, period_m: float = 0.6,
             floor: float = 0.0, vertical: float = 0.12) -> None:
    """Repaints COLOR_0.g (ash) over vertices [start_v:]: heavy on up-facing surfaces, a thin dusting on
    verticals (`vertical`), none on undersides; broken up by fbm so drifts and bare patches alternate."""
    if start_v >= mb.vertex_count:
        return
    pos = np.asarray(mb.pos[start_v:], dtype=float)
    nrm = np.asarray(mb.nrm[start_v:], dtype=float)
    col = np.asarray(mb.col[start_v:], dtype=float)
    up = nrm[:, 1]
    lie = kc.smoothstep(0.25, 0.85, up) + vertical * kc.smoothstep(-0.15, 0.2, up) * (1.0 - kc.smoothstep(0.25, 0.85, up))
    breakup = noise.fbm(pos / period_m, 3)
    ash = np.clip(amount * lie * (0.35 + 1.1 * breakup) + floor * (up > -0.2), 0.0, 1.0)
    col[:, 1] = ash
    mb.col[start_v:] = col.tolist()


def wet_pass(mb: kc.MeshBuilder, start_v: int, mask_fn, amount: float = 1.0) -> None:
    """Adds wetness (COLOR_0.b) where mask_fn(positions) > 0 (channel kerbs, spill lips, splash)."""
    if start_v >= mb.vertex_count:
        return
    pos = np.asarray(mb.pos[start_v:], dtype=float)
    col = np.asarray(mb.col[start_v:], dtype=float)
    col[:, 2] = np.clip(col[:, 2] + amount * np.clip(mask_fn(pos), 0.0, 1.0), 0.0, 1.0)
    mb.col[start_v:] = col.tolist()


def remap_slots(mb: kc.MeshBuilder, mapping: dict[str, str] | None = None) -> kc.MeshBuilder:
    """Renames material slots in place (Haluna builders write Haluna slot names). Two slots that map to
    one name are merged."""
    mapping = HALUNA_SLOTS if mapping is None else mapping
    new_names: list[str] = []
    remap: list[int] = []
    for name in mb.materials:
        target = mapping.get(name, name)
        if target not in new_names:
            new_names.append(target)
        remap.append(new_names.index(target))
    mb.materials = new_names
    mb.tri_mat = [remap[m] for m in mb.tri_mat]
    return mb


def prune_slots(mb: kc.MeshBuilder) -> kc.MeshBuilder:
    """Drops material slots no triangle uses (a merged Haluna builder can bring one along), in place."""
    used = sorted(set(mb.tri_mat))
    remap = {old: new for new, old in enumerate(used)}
    mb.materials = [mb.materials[i] for i in used]
    mb.tri_mat = [remap[m] for m in mb.tri_mat]
    return mb


def batter_z(y: float) -> float:
    """Front face of a retaining wall at height y (0 at the coping top, -WALL_H_M at the foot)."""
    return -y * np.tan(np.radians(BATTER_DEG))


def lod_name(name: str, lod: bool) -> str:
    return name + ("-lod1" if lod else "")


def flame(mb: kc.MeshBuilder, base, height: float, radius: float, *, sides: int = 6) -> None:
    """A wick flame: a teardrop of emissive `kit_wick_flame` standing on `base`."""
    base = np.asarray(base, float)
    t = np.linspace(0.0, 1.0, 5)
    centers = base + np.outer(t, [0.0, height, 0.0])
    radii = radius * np.sin(np.pi * np.clip(t * 0.85 + 0.08, 0, 1)) ** 0.8 * (1.0 - 0.55 * t)
    radii = np.maximum(radii, radius * 0.05)
    kc.tube(mb, centers, radii, sides, mb.material(M_FLAME), cap_start=True, cap_end=True,
            weather=kc.Weathering(moss=0, salt=0, wet=0, erosion=0))


def water_plane(mb: kc.MeshBuilder, x0: float, x1: float, z0: float, z1: float, y: float, mat_name: str, *,
                nx: int = 2, nz: int = 2) -> None:
    """A flat water surface (up-facing) over a rectangle. UV in metres."""
    xs = np.linspace(x0, x1, nx)
    zs = np.linspace(z0, z1, nz)
    X, Z = np.meshgrid(xs, zs)
    grid = np.stack([X, np.full(X.shape, y), Z], axis=-1)
    kc.quad_strip(mb, grid, mb.material(mat_name), uv=np.stack([X, Z], axis=-1), col=(0.0, 0.0, 1.0, 0.0),
                  uv2=(1.0, 0.5), flip=True, smooth=False)
    # quad_strip writes +Y normals; flip=True winds the triangles counter-clockwise seen from above.


def mirror_x(mb: kc.MeshBuilder, name: str) -> kc.MeshBuilder:
    """A copy of `mb` mirrored across x = 0 (windings reversed so it still faces out), renamed."""
    out = kc.MeshBuilder(name)
    out.materials = list(mb.materials)
    p = np.asarray(mb.pos, float) * np.array([-1.0, 1.0, 1.0])
    n = np.asarray(mb.nrm, float) * np.array([-1.0, 1.0, 1.0])
    out.pos, out.nrm = p.tolist(), n.tolist()
    out.uv = [list(u) for u in mb.uv]
    out.uv2 = [list(u) for u in mb.uv2]
    out.col = [list(c) for c in mb.col]
    out.tris = [(a, c, b) for a, b, c in mb.tris]
    out.tri_mat = list(mb.tri_mat)
    return out


def deformed_block(mb: kc.MeshBuilder, center, half, mat_name: str, deform, *, radius: float = 0.03,
                   seg: int = 3, noise: kc.Noise3 | None = None, disp_m: float = 0.0, disp_period_m: float = 0.25,
                   weather: kc.Weathering = TERRACE, variation: float = 0.5) -> None:
    """A rounded block built at the origin, bent by `deform(local_points) -> points` (shear a joint,
    swell a face, lean with the batter), then moved to `center`. Normals are recomputed after."""
    tmp = kc.MeshBuilder("tmp")
    kc.rounded_block(tmp, (0.0, 0.0, 0.0), half, tmp.material(mat_name), radius=radius, seg=seg, noise=None,
                     weather=weather, variation=variation)
    p = deform(np.asarray(tmp.pos, float))
    if noise is not None and disp_m > 0.0:
        n = np.asarray(tmp.nrm, float)
        world = p + np.asarray(center, float)
        p = p + n * ((noise.fbm(world / disp_period_m, 3) - 0.5) * disp_m)[:, None]
    tmp.pos = p.tolist()
    kc.recompute_normals(tmp)
    mb.merge(tmp, offset=center)


# --- The town's terrace geometry (pemakar.md §0), shared by the massif and the preview layout ------
# Tier t's tread front is an arc of radius TOWN_R0_M - t * TREAD_D_M about TOWN_CENTRE (x, z); its
# tread stands at TOWN_Y0_M + t * WALL_H_M. The sea is at y = 0; the crown and caldera are north.
TOWN_CENTRE = (0.0, -150.0)
TOWN_R0_M = 150.0
TOWN_Y0_M = 8.0
TOWN_TIERS = 10
CROWN = (0.0, -760.0)  # caldera centre (x, z)
CROWN_Y_M = 335.0
CROWN_FOOT_R_M = 790.0  # where the cone meets the sea
CALDERA_R_M = 70.0


def town_tier_at(x, z):
    """Tier index (float, may be < 0 or > 9) of a point by its radius about TOWN_CENTRE."""
    r = np.hypot(np.asarray(x, float) - TOWN_CENTRE[0], np.asarray(z, float) - TOWN_CENTRE[1])
    return (TOWN_R0_M - r) / TREAD_D_M


def tier_tread_y(t):
    return TOWN_Y0_M + WALL_H_M * np.asarray(t, float)
