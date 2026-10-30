"""Ambient insects (M3-CRE-616): docs/kb/art/wildlife.md.

blender --background --factory-startup --python-exit-code 1 --threads 4 --python \
    assets_src/wildlife/insect/build_insect.py -- --out assets/wildlife/insect/insect.glb

Three small, ordinary insects in one GLB, drawn many at a time through MultiMesh, each with its own material slot:
  insect_moth       a pale dusk moth, about 3 cm across the wings: a soft, furry body, two pairs of broad wings in
                    dusty off-white and grey-brown with faint darker bands, small antennae. Slot `moth` (matte).
  insect_dragonfly  about 7 cm long: a slim, segmented abdomen in a muted blue-green running to bronze, large dark
                    eyes, four narrow clear wings, a pale glassy tint with a darker vein edge and a small dark
                    spot near each tip (there is no alpha: the wings are opaque glass). Slot `dragonfly` (glossy).
  insect_firefly    (Ch10, Ossa Fen at dusk) a slim beetle about 1.4 cm long: dusky brown wing covers with a pale
                    margin held up and out, clear hind wings beating beneath, a faded red shield with a dark spot over
                    the head, and the lantern, the abdomen's last segments in pale yellow-green wax, which the slot
                    `firefly` lights (its glow_* parameters) by the instance's blink. Wildlife, not glimmer.
All are built with the wings spread flat, as in flight. TEXCOORD_1.y = the wing span (0 at the root .. ±1 at the
tip, the sign the wing's side, + on +x), which the wildlife shader's flutter (mode 5) turns about the body's long
axis at the wing root (materials.json `flutter_pivot`); on the dragonfly the hind pair (behind `flutter_split_z`)
beats out of step with the fore pair. The bodies are still. Nothing spawn-touched: no wound light, no glimmer.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import wildlife_kit as wk  # noqa: E402

ck = wk.ck

SEED = 6116
PAL = {k: ck.hexrgb(v) for k, v in {
    "frangipani": "#F0E8D8", "bone": "#E6DAC0", "coral_stone_weathered": "#B9AE98", "timber_weathered": "#7E6A55",
    "sand_cloth": "#C9B48E", "lacquer_black": "#1D1916", "bronze_patina": "#5F8A78", "brass": "#B08D57",
    "tortoiseshell": "#6B3A1E", "salt_glass": "#BFE6E0", "foam_white": "#EEF6F4", "overcast_slate": "#6F7E8E",
    "faded_teal_cloth": "#5E9A96", "sun_gold": "#FFD27A", "palm_green": "#3E7A3A", "lacquer_red_deep": "#7A1712",
}.items()}

# --- moth -----------------------------------------------------------------------------------------------------
MOTH_SLOT = "moth"
MOTH_PALE = ck.mix(PAL["frangipani"], PAL["coral_stone_weathered"], 0.3)  # dusty off-white
MOTH_DUSK = ck.mix(PAL["timber_weathered"], PAL["coral_stone_weathered"], 0.45)  # grey-brown
MOTH_BAND = PAL["timber_weathered"] * 0.8
MOTH_FUR = ck.mix(PAL["bone"], PAL["sand_cloth"], 0.5)
MOTH_WING_ROOT_X = 0.0012  # the shader's flutter pivot (materials.json) sits at the wing root
MOTH_WING_Y = 0.0015
MOTH_SPAN_HALF = 0.0150

# --- dragonfly ------------------------------------------------------------------------------------------------
DF_SLOT = "dragonfly"
DF_TEAL = ck.mix(PAL["bronze_patina"], PAL["faded_teal_cloth"], 0.35)  # muted blue-green
DF_BRONZE = ck.mix(PAL["brass"], PAL["tortoiseshell"], 0.45)
DF_DARK = PAL["lacquer_black"] * 1.1
DF_EYE = ck.mix(PAL["bronze_patina"], PAL["lacquer_black"], 0.6)
# a pale glassy tint, greyed so it never reads as a glimmer light
DF_GLASS = ck.mix(ck.mix(PAL["salt_glass"], PAL["foam_white"], 0.45), PAL["overcast_slate"], 0.12)
DF_VEIN = ck.mix(PAL["timber_weathered"], PAL["lacquer_black"], 0.5)
DF_WING_ROOT_X = 0.0025
DF_WING_Y = 0.0035
DF_SPLIT_Z = 0.015  # fore wings lie wholly in front of this z, hind wings wholly behind it
DF_HEAD_Z = 0.0285
DF_TAIL_Z = -0.038

# --- firefly (Ch10, Ossa Fen at dusk; docs/kb/plan/act2/creatures/fen_firefly.md) ---------------------------------
FF_SLOT = "firefly"
FF_DARK = ck.mix(PAL["lacquer_black"], PAL["timber_weathered"], 0.25)
FF_COVER = ck.mix(PAL["timber_weathered"], PAL["lacquer_black"], 0.55)  # the wing covers, dusky brown
FF_EDGE = PAL["sand_cloth"]  # their pale outer margin
FF_SHIELD = ck.mix(PAL["lacquer_red_deep"], PAL["sand_cloth"], 0.35)  # the pronotum, a faded red
# the lantern's wax by day: a pale yellow-green (sun_gold toward palm_green, never a glimmer swatch); lit, the
# material's glow_color (materials.json) is the same hue
FF_LANTERN = ck.mix(PAL["sun_gold"], PAL["palm_green"], 0.3)
FF_LANTERN_Z = -0.0052  # the abdomen behind this z is the lantern (the material's glow_tail_z)
FF_TAIL_Z = -0.0092
FF_WING_ROOT_X = 0.0008
FF_WING_Y = 0.0016


def _wing(mesh: ck.Mesh, slot: str, side: float, root_x: float, y0: float, span_half: float, le, te, lift: float,
          nu: int, nv: int, shade) -> None:
    """A single-sheet wing (the shader draws both faces) from the root at root_x to the tip at span_half, the
    leading and trailing edges z given as (u, z) breakpoints; `shade(u, v)` -> colours. Mask = side * u."""
    u = np.linspace(0.0, 1.0, nu)
    v = np.linspace(0.0, 1.0, nv)
    lz = np.interp(u, *zip(*le))
    tz = np.interp(u, *zip(*te))
    U, V = np.meshgrid(u, v, indexing="ij")
    Z = lz[:, None] + (tz - lz)[:, None] * V
    X = side * (root_x + (span_half - root_x) * U)
    Y = y0 + lift * U * U
    P = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    uu, vv = U.ravel(), V.ravel()
    T = ck.grid_tris(nu, nv, False)
    if side < 0:
        T = ck.flip(T)
    ck.finish(mesh, P, T, slot, shade(uu, vv), 0, cavity=0.05, emission=side * uu)


def _moth_wing_colour(fore: bool):
    def shade(u: np.ndarray, v: np.ndarray) -> np.ndarray:
        base = ck.mix(MOTH_PALE, MOTH_DUSK, (0.8 * (1.0 - ck.smoothstep(0.0, 0.5, u)))[:, None])
        if fore:
            # two faint bands slanting across the forewing, and a dusky trailing edge
            w = u + 0.35 * v
            band = sum(1.0 - ck.smoothstep(0.06, 0.16, np.abs(w - c)) for c in (0.62, 1.05))
            base = ck.mix(base, MOTH_BAND, (0.7 * np.clip(band, 0.0, 1.0))[:, None])
            base = ck.mix(base, MOTH_DUSK, (0.45 * ck.smoothstep(0.5, 1.0, v))[:, None])
        else:
            base = ck.mix(base, MOTH_DUSK, 0.4)  # the hind wings are a greyer, plainer underlayer
        return base
    return shade


def build_moth() -> ck.Mesh:
    mesh = ck.Mesh("insect_moth")
    # body: thorax and a tapering abdomen, furry (mottled by noise; the material is matte)
    path = ck.bezier([(0, 0.0012, 0.0055), (0, 0.0010, 0.0010), (0, 0.0006, -0.0040), (0, 0.0002, -0.0085)], 6)
    rad = np.array([0.0020, 0.0026, 0.0024, 0.0019, 0.0014, 0.0008])
    P, T = ck.tube(path, rad, 6, squash=0.85, up_hint=(0.0, 1.0, 0.0))
    fur = ck.fbm(P * 1800.0, SEED, 2)
    col = ck.mix(MOTH_FUR, MOTH_DUSK, np.clip(0.35 + 0.5 * fur, 0.0, 1.0)[:, None])
    ck.finish(mesh, P, T, MOTH_SLOT, col, 0, cavity=0.15)
    # head: a small furry dome with two dark eyes
    hc = np.array([0.0, 0.0010, 0.0068])
    P, T = ck.ellipsoid(hc, (0.0017, 0.0016, 0.0015), 4, 6)
    eye = np.zeros(len(P))
    for side in (1.0, -1.0):
        d = np.linalg.norm(P - (hc + np.array([side * 0.0015, 0.0, 0.0006])), axis=1)
        eye = np.maximum(eye, 1.0 - ck.smoothstep(0.0006, 0.0012, d))
    ck.finish(mesh, P, T, MOTH_SLOT, ck.mix(MOTH_FUR, PAL["lacquer_black"], eye[:, None]), 0, cavity=0.1)
    # antennae: two short, fine feelers curving forward and out
    for side in (1.0, -1.0):
        path = ck.bezier([(side * 0.0006, 0.0022, 0.0076), (side * 0.0020, 0.0034, 0.0100),
                          (side * 0.0042, 0.0036, 0.0122)], 3)
        P, T = ck.tube(path, np.array([0.00028, 0.00022, 0.00018]), 3)
        ck.finish(mesh, P, T, MOTH_SLOT, MOTH_DUSK * 0.85, 0, cavity=0.2)
    # wings: broad forewings over rounder hind wings, spread flat with a slight lift toward the tips
    for side in (1.0, -1.0):
        _wing(mesh, MOTH_SLOT, side, MOTH_WING_ROOT_X, MOTH_WING_Y, MOTH_SPAN_HALF,
              le=[(0.0, 0.0042), (0.5, 0.0050), (1.0, 0.0010)], te=[(0.0, -0.0004), (0.5, -0.0035), (1.0, -0.0052)],
              lift=0.0008, nu=6, nv=4, shade=_moth_wing_colour(True))
        _wing(mesh, MOTH_SLOT, side, MOTH_WING_ROOT_X, MOTH_WING_Y - 0.0002, MOTH_SPAN_HALF * 0.72,
              le=[(0.0, -0.0002), (0.5, -0.0022), (1.0, -0.0048)], te=[(0.0, -0.0050), (0.5, -0.0080), (1.0, -0.0072)],
              lift=0.0005, nu=5, nv=3, shade=_moth_wing_colour(False))
    return mesh


def _df_wing_colour(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    edge = np.maximum.reduce([1.0 - ck.smoothstep(0.0, 0.3, v), ck.smoothstep(0.75, 1.0, v),
                              ck.smoothstep(0.85, 1.0, u)])
    col = ck.mix(DF_GLASS, DF_VEIN, (0.75 * edge)[:, None])
    stigma = (1.0 - ck.smoothstep(0.05, 0.12, np.abs(u - 0.85))) * (1.0 - ck.smoothstep(0.1, 0.3, v))
    return ck.mix(col, DF_DARK, (0.8 * stigma)[:, None])


def build_dragonfly() -> ck.Mesh:
    mesh = ck.Mesh("insect_dragonfly")
    # thorax and abdomen in one tube: a stout thorax, then a slim abdomen with darker, narrower segment joints
    zs = [0.0255, 0.0200, 0.0135, 0.0080, 0.0020, -0.0040, -0.0100, -0.0160, -0.0220, -0.0280, -0.0335, DF_TAIL_Z]
    path = np.array([(0.0, 0.0004 if z > 0.01 else 0.0, z) for z in zs])
    rad = np.array([0.0030, 0.0038, 0.0032, 0.0017, 0.0015, 0.0016, 0.0015, 0.0016, 0.0015, 0.0015, 0.0014, 0.0011])
    joint = np.array([0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0], dtype=np.float64)
    rad = rad * (1.0 - 0.1 * joint)
    segs = 6
    P, T = ck.tube(path, rad, segs, squash=0.95, up_hint=(0.0, 1.0, 0.0))
    s = np.clip((DF_HEAD_Z - 0.012 - P[:, 2]) / (DF_HEAD_Z - 0.012 - DF_TAIL_Z), 0.0, 1.0)
    col = ck.mix(DF_TEAL, DF_BRONZE, ck.smoothstep(0.15, 0.9, s)[:, None])
    k = np.concatenate([np.repeat(joint, segs), [0.0, 0.0]])  # the two cap points
    col = ck.mix(col, DF_DARK, (0.75 * k)[:, None])
    top = ck.smoothstep(0.0005, 0.0025, P[:, 1] - np.interp(P[:, 2], path[::-1, 2], path[::-1, 1]))
    stripe = top * (P[:, 2] > 0.012)  # dark shoulder stripes on the thorax
    col = ck.mix(col, DF_DARK, (0.45 * stripe)[:, None])
    ck.finish(mesh, P, T, DF_SLOT, col, 0, wet=0.35, cavity=0.1 + 0.3 * k)
    # head: wide, nearly all eye
    hc = np.array([0.0, 0.0010, DF_HEAD_Z])
    P, T = ck.ellipsoid(hc, (0.0044, 0.0034, 0.0030), 4, 6)
    face = ck.smoothstep(0.0, 0.0015, P[:, 2] - hc[2] - 0.0012) * (P[:, 1] < hc[1] + 0.0005)
    col = ck.mix(DF_EYE, DF_TEAL * 0.9, face[:, None])
    ck.finish(mesh, P, T, DF_SLOT, col, 0, wet=0.8, cavity=0.05)
    # wings: four long narrow blades, the fore pair in front of DF_SPLIT_Z, the hind pair (broader at the root)
    # behind it, held flat and level
    for side in (1.0, -1.0):
        _wing(mesh, DF_SLOT, side, DF_WING_ROOT_X, DF_WING_Y, 0.0340,
              le=[(0.0, 0.0225), (0.5, 0.0238), (1.0, 0.0215)], te=[(0.0, 0.0168), (0.5, 0.0158), (1.0, 0.0190)],
              lift=0.0006, nu=6, nv=3, shade=_df_wing_colour)
        _wing(mesh, DF_SLOT, side, DF_WING_ROOT_X, DF_WING_Y - 0.0003, 0.0325,
              le=[(0.0, 0.0142), (0.5, 0.0138), (1.0, 0.0118)], te=[(0.0, 0.0072), (0.5, 0.0064), (1.0, 0.0094)],
              lift=0.0006, nu=6, nv=3, shade=_df_wing_colour)
    return mesh


def _ff_elytron_colour(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    # dark wing covers with a pale sand_cloth margin down the outer edge (a firefly beetle's), darker toward the tip
    col = ck.mix(FF_DARK, FF_COVER, (0.6 * (1.0 - ck.smoothstep(0.2, 1.0, v)))[:, None])
    return ck.mix(col, FF_EDGE, ck.smoothstep(0.75, 0.95, u)[:, None] * 0.8)


def _ff_hindwing_colour(_u: np.ndarray, v: np.ndarray) -> np.ndarray:
    return ck.mix(DF_GLASS, DF_VEIN, (0.5 * ck.smoothstep(0.7, 1.0, v))[:, None])  # clear, a darker trailing edge


def build_firefly() -> ck.Mesh:
    mesh = ck.Mesh("insect_firefly")
    # the body: a slim beetle, about 1.4 cm long; the abdomen's last segments (behind FF_LANTERN_Z) are the lantern,
    # pale yellow-green wax, which the firefly material lights from the instance's blink
    zs = [0.0050, 0.0030, 0.0005, -0.0020, -0.0045, -0.0065, -0.0080, FF_TAIL_Z]
    path = np.array([(0.0, 0.0008, z) for z in zs])
    rad = np.array([0.0012, 0.0016, 0.0017, 0.0017, 0.0016, 0.0015, 0.0013, 0.0008])
    P, T = ck.tube(path, rad, 6, squash=0.7, up_hint=(0.0, 1.0, 0.0))
    lantern = ck.smoothstep(FF_LANTERN_Z + 0.0006, FF_LANTERN_Z - 0.0006, P[:, 2])
    col = ck.mix(FF_DARK, FF_LANTERN, lantern[:, None])
    ck.finish(mesh, P, T, FF_SLOT, col, 0, wet=0.3 * lantern, cavity=0.1)
    # the pronotum: a flat shield over the head, faded red with a dark central spot
    sc = np.array([0.0, 0.0018, 0.0062])
    P, T = ck.ellipsoid(sc, (0.0020, 0.0006, 0.0018), 4, 8)
    spot = 1.0 - ck.smoothstep(0.0004, 0.0009, np.linalg.norm((P - sc)[:, [0, 2]], axis=1))
    ck.finish(mesh, P, T, FF_SLOT, ck.mix(FF_SHIELD, FF_DARK, spot[:, None]), 0, cavity=0.1)
    # the head, tucked under the shield, and two thin antennae swept forward
    hc = np.array([0.0, 0.0008, 0.0074])
    P, T = ck.ellipsoid(hc, (0.0009, 0.0008, 0.0008), 4, 6)
    ck.finish(mesh, P, T, FF_SLOT, FF_DARK, 0, cavity=0.2)
    for side in (1.0, -1.0):
        path = ck.bezier([(side * 0.0005, 0.0012, 0.0080), (side * 0.0016, 0.0020, 0.0098),
                          (side * 0.0028, 0.0018, 0.0112)], 3)
        P, T = ck.tube(path, np.array([0.00022, 0.00018, 0.00014]), 3)
        ck.finish(mesh, P, T, FF_SLOT, FF_DARK, 0, cavity=0.2)
    # wings: the dark wing covers held up and out in flight, and the clear hind wings beating beneath them
    for side in (1.0, -1.0):
        _wing(mesh, FF_SLOT, side, FF_WING_ROOT_X, FF_WING_Y + 0.0003, 0.0042,
              le=[(0.0, 0.0040), (0.5, 0.0030), (1.0, 0.0012)], te=[(0.0, -0.0040), (0.5, -0.0048), (1.0, -0.0040)],
              lift=0.0016, nu=4, nv=3, shade=_ff_elytron_colour)
        _wing(mesh, FF_SLOT, side, FF_WING_ROOT_X, FF_WING_Y, 0.0080,
              le=[(0.0, 0.0030), (0.5, 0.0026), (1.0, 0.0006)], te=[(0.0, -0.0010), (0.5, -0.0034), (1.0, -0.0024)],
              lift=0.0004, nu=5, nv=3, shade=_ff_hindwing_colour)
    return mesh


def build_meshes() -> list:
    return [build_moth(), build_dragonfly(), build_firefly()]


def main() -> None:
    out = wk.out_arg()
    info = wk.export_static(build_meshes(), out, extras={"hymn_wildlife": "insect"})
    print(f"insect: {info}")


if __name__ == "__main__":
    main()
