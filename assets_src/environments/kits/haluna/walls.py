"""Haluna coral walls (haluna.md §1.2). Pure numpy; see kit_common.py.

  tidewall_straight   a 2.0 m segment of dry-stacked coral blocks (0.25-0.5 m), 1.6 m tall, 0.7 m at
                      the base with a 6 deg batter on both faces, under a lime-mortared cap (the white
                      line that reads from the sea in H01)
  tidewall_windgap    the same with a 0.15 m wind slot between 0.6 and 1.2 m (every 3rd segment)
  tidewall_gate       a 2.0 m segment with a 1.3 m opening (lanes reach the beach through these)
  wakeshell_wall      the Pilgrim's Wake shrine wall at the causeway head: a 7 m arc, 2.2 m tall,
                      ~500 carved wake-shells (6-14 cm) set in lime mortar, each with a name glyph,
                      and the single clean empty gap at shoulder height waiting for Asha (Ch2)
  wake_shell_set      one named wake-shell the gap's size, no stand, to set in the wall (M3-ENV-743; origin at
                      its centre, face +Z)

Segments are built along +X, centred on x = 0, the sea face on +Z. Curved runs (R = 12 / 24 m) are
laid by the zone dresser as rotated straight segments; the cap overlaps 3 cm at each end so the
joints close on curves down to R = 12 m. Parameters: `height`, `seed`, `weather`, block size range.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_STONE = "kit_coral_stone"
M_MORTAR = "kit_mortar_white"
M_SHELL = "kit_wake_shell"

SEG_LEN_M = 2.0
BASE_THICK_M = 0.7
BATTER_DEG = 6.0
BLOCK_MIN_M, BLOCK_MAX_M = 0.25, 0.5
WINDGAP_M = (0.15, 0.6, 1.2)  # width, bottom, top
GATE_W_M = 1.3
# Broken-coral faces (M2 final pass): a tight edge radius and a broad, shallow displacement read as
# flat-faced quarried chunks; the old 3.5 cm radius at 6 cm / 17 cm displacement read as pillows.
BLOCK_EDGE_R_M, BLOCK_DISP_M, BLOCK_DISP_PERIOD_M = 0.018, 0.04, 0.26

TRI_BUDGET = {
    "tidewall": (5600, 500),
    "wakeshell_wall": (28000, 1500),
    "wake_shell_set": (300, 60),
}
BUDGET_KEY = {"tidewall_straight": "tidewall", "tidewall_windgap": "tidewall", "tidewall_gate": "tidewall"}


def _thickness_at(y: float, height: float) -> float:
    return BASE_THICK_M - 2.0 * y * math.tan(math.radians(BATTER_DEG)) * (BASE_THICK_M / 0.7)


def tidewall(name: str, seed: int, *, height: float = 1.6, gap: str = "none",
             weather: kc.Weathering = kc.VILLAGE, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
    mat = mb.material(M_STONE)
    cap_h = 0.12
    body_h = height - cap_h
    hl = SEG_LEN_M * 0.5
    if lod:
        t0, t1 = _thickness_at(0.0, height), _thickness_at(body_h, height)
        kc.rounded_block(mb, (0, body_h * 0.5, 0), (hl, body_h * 0.5, (t0 + t1) * 0.25), mat, seg=1, radius=0.05)
        kc.rounded_block(mb, (0, body_h + cap_h * 0.5, 0), (hl + 0.03, cap_h * 0.5, t1 * 0.5 + 0.04),
                         mb.material(M_MORTAR), seg=1, radius=0.04)
        return mb
    y = 0.0
    course = 0
    while y < body_h - 0.05:
        ch = min(rng.uniform(0.17, 0.34), body_h - y)
        if body_h - (y + ch) < 0.12:
            ch = body_h - y
        x = -hl - rng.uniform(0.0, BLOCK_MAX_M * 0.6) if course % 2 else -hl
        while x < hl - 0.01:
            bl = rng.uniform(BLOCK_MIN_M, BLOCK_MAX_M)
            x0, x1 = max(x, -hl), min(x + bl, hl)
            x = x + bl
            if x1 - x0 < 0.08:
                continue
            yc = y + ch * 0.5
            slot = (gap == "windgap" and WINDGAP_M[1] - 0.05 < yc < WINDGAP_M[2] + 0.05) or (gap == "gate")
            half_gap = (WINDGAP_M[0] if gap == "windgap" else GATE_W_M) * 0.5
            if slot and x1 > -half_gap and x0 < half_gap:
                # Split the block around the opening.
                pieces = [(x0, -half_gap), (half_gap, x1)]
            else:
                pieces = [(x0, x1)]
            for a, b in pieces:
                if b - a < 0.06:
                    continue
                # Irregular dry-stacked coral: each block a little proud or sunk, tilted, and
                # its own height, so the courses never read as a ruled line.
                thick = _thickness_at(yc, height) * rng.uniform(0.9, 1.04)
                sink = rng.uniform(-0.02, 0.025)
                bh = ch * rng.uniform(0.82, 1.0)
                kc.rounded_block(mb, ((a + b) * 0.5, yc - sink, rng.uniform(-0.035, 0.035)),
                                 ((b - a) * 0.5 - 0.015, bh * 0.5 - 0.008, thick * 0.5), mat,
                                 rot=kc.rot_z(rng.normal(0, 0.05)) @ kc.rot_y(rng.normal(0, 0.04))
                                 @ kc.rot_x(rng.normal(0, 0.03)), radius=BLOCK_EDGE_R_M, seg=3, noise=noise,
                                 disp_m=BLOCK_DISP_M, disp_period_m=BLOCK_DISP_PERIOD_M, weather=weather,
                                 variation=float(rng.random()))
        y += ch
        course += 1
    # Lime-mortared cap (rounded), stepped down over the gate opening.
    t_top = _thickness_at(body_h, height)
    cap_mat = mb.material(M_MORTAR)
    cap_spans = [(-hl - 0.03, hl + 0.03)] if gap != "gate" else [(-hl - 0.03, -GATE_W_M * 0.5),
                                                                  (GATE_W_M * 0.5, hl + 0.03)]
    for a, b in cap_spans:
        kc.rounded_block(mb, ((a + b) * 0.5, body_h + cap_h * 0.5, 0.0), ((b - a) * 0.5, cap_h * 0.5,
                         t_top * 0.5 + 0.04), cap_mat, radius=0.05, seg=4, noise=noise, disp_m=0.012,
                         disp_period_m=0.5, weather=kc.Weathering(moss=0.3, salt=0.3, wet=0.0, erosion=0.35),
                         variation=float(rng.random()))
    if gap == "gate":
        # A worn threshold stone in the opening.
        kc.rounded_block(mb, (0.0, 0.05, 0.0), (GATE_W_M * 0.5, 0.06, BASE_THICK_M * 0.5), mat, radius=0.04, seg=3,
                         noise=noise, disp_m=0.015, weather=kc.Weathering(moss=0.1, salt=0.4, wet=0.0, erosion=0.9),
                         variation=float(rng.random()))
    return mb


def build_tidewall(name: str, seed: int, gap: str) -> list[kc.MeshBuilder]:
    return [tidewall(name, seed, gap=gap), tidewall(name, seed, gap=gap, lod=True)]


# ---------------------------------------------------------------------------------------------
# Wake-shell wall
# ---------------------------------------------------------------------------------------------
WAKE_ARC_M = 7.0
WAKE_RADIUS_M = 6.0
WAKE_HEIGHT_M = 2.2
WAKE_SHELLS = 520
WAKE_GAP = (0.0, 1.45, 0.11)  # arc position (m from centre), height (m), radius (m)
GLYPH_CELLS = 4  # kit_textures.build_shell_glyph atlas


def _shell(mb: kc.MeshBuilder, center, normal, up, size: float, glyph: int, age: float, rng, mat: int) -> None:
    """One scallop-like wake-shell: a ribbed fan (hinge down) bulging out of the mortar."""
    normal = kc.normalize(np.asarray(normal, float))
    up = kc.normalize(np.asarray(up, float) - normal * np.dot(up, normal))
    right = np.cross(up, normal)
    roll = rng.normal(0.0, 0.25)
    up, right = up * math.cos(roll) + right * math.sin(roll), right * math.cos(roll) - up * math.sin(roll)
    nr, na = 3, 7
    span = math.radians(130.0)
    grid = np.zeros((nr + 1, na + 1, 3))
    uv = np.zeros((nr + 1, na + 1, 2))
    gx, gy = glyph % GLYPH_CELLS, glyph // GLYPH_CELLS
    hinge = np.asarray(center, float) - up * size * 0.45
    for i in range(nr + 1):
        r = size * (0.08 + 0.92 * i / nr)
        for j in range(na + 1):
            a = -span * 0.5 + span * j / na
            rib = 0.06 * size * (0.5 + 0.5 * math.cos(a * 18.0)) * (i / nr)
            bulge = size * 0.22 * math.sin(math.pi * min(1.0, i / nr * 0.95 + 0.05)) * math.cos(a * 0.8)
            grid[i, j] = hinge + up * (math.cos(a) * r) + right * (math.sin(a) * r) + normal * (bulge + rib)
            lu = 0.5 + math.sin(a) * (r / size) * 0.5
            lv = 1.0 - math.cos(a) * (r / size) * 0.9 - 0.05
            uv[i, j] = ((gx + np.clip(lu, 0, 1)) / GLYPH_CELLS, (gy + np.clip(lv, 0, 1)) / GLYPH_CELLS)
    col = np.array([0.0, 0.3 * age, 0.0, 0.3 + 0.6 * age])
    uv2 = np.array([0.9, age])
    flip = np.dot(np.cross(grid[1, 4] - grid[1, 2], grid[2, 3] - grid[0, 3]), normal) < 0
    kc.quad_strip(mb, grid, mat, uv=uv, col=col, uv2=uv2, flip=bool(flip))


def build_wakeshell_wall(seed: int = 51, *, shells: int = WAKE_SHELLS,
                         weather: kc.Weathering = kc.VILLAGE) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("wakeshell_wall", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("wakeshell_wall")
    stone = mb.material(M_STONE)
    mortar = mb.material(M_MORTAR)
    shell_mat = mb.material(M_SHELL)
    half_angle = WAKE_ARC_M / WAKE_RADIUS_M * 0.5
    # The arc's concave (inner) face looks towards +Z; centre of curvature at z = +R.
    def on_arc(s: float, inset: float = 0.0):
        a = s / WAKE_RADIUS_M
        r = WAKE_RADIUS_M - inset
        p = np.array([math.sin(a) * r, 0.0, WAKE_RADIUS_M - math.cos(a) * r])
        n = kc.normalize(np.array([-math.sin(a), 0.0, math.cos(a)]))
        return p, n, a
    n_blocks = 16
    thick = 0.6
    for k in range(n_blocks):
        s0 = -WAKE_ARC_M * 0.5 + WAKE_ARC_M * k / n_blocks
        s1 = s0 + WAKE_ARC_M / n_blocks
        p, n, a = on_arc((s0 + s1) * 0.5, -thick * 0.5)
        bl = (s1 - s0) * 0.5 + 0.015
        # Mortared shell face (plaster), on coral block masonry.
        kc.rounded_block(mb, p + np.array([0.0, WAKE_HEIGHT_M * 0.5, 0.0]), (bl, WAKE_HEIGHT_M * 0.5, thick * 0.5),
                         mortar, rot=kc.rot_y(-a), radius=0.03, seg=3, noise=noise, disp_m=0.015, disp_period_m=0.4,
                         weather=weather, variation=float(rng.random()))
        # Coral coping and plinth.
        for y, hh, extra in ((WAKE_HEIGHT_M + 0.09, 0.09, 0.08), (0.12, 0.12, 0.06)):
            kc.rounded_block(mb, p + np.array([0.0, y, 0.0]), (bl + 0.01, hh, thick * 0.5 + extra), stone,
                             rot=kc.rot_y(-a), radius=0.05, seg=3, noise=noise, disp_m=0.03, disp_period_m=0.3,
                             weather=weather, variation=float(rng.random()))
    # End piers.
    for sgn in (-1.0, 1.0):
        p, n, a = on_arc(sgn * (WAKE_ARC_M * 0.5 + 0.15), -thick * 0.5)
        kc.rounded_block(mb, p + np.array([0.0, (WAKE_HEIGHT_M + 0.35) * 0.5, 0.0]),
                         (0.22, (WAKE_HEIGHT_M + 0.35) * 0.5, thick * 0.5 + 0.08), stone, rot=kc.rot_y(-a), radius=0.06,
                         seg=3, noise=noise, disp_m=0.035, weather=weather, variation=float(rng.random()))
    # Shells: jittered rows between 0.35 and 2.05 m, densest at hand height, oldest lowest.
    placed = 0
    rows = np.linspace(0.38, 2.02, 15)
    per_row = int(math.ceil(shells / len(rows)))
    for ri, y in enumerate(rows):
        for ci in range(per_row):
            if placed >= shells:
                break
            s = -WAKE_ARC_M * 0.5 + 0.12 + (WAKE_ARC_M - 0.24) * (ci + 0.5 * (ri % 2) + rng.uniform(-0.2, 0.2)) / per_row
            yy = y + rng.uniform(-0.035, 0.035)
            gs, gy, gr = WAKE_GAP
            if math.hypot(s - gs, yy - gy) < gr + 0.06:
                continue
            p, n, _a = on_arc(s, 0.0)
            size = rng.uniform(0.06, 0.14)
            age = float(np.clip(1.0 - (yy - 0.35) / 1.8 + rng.normal(0, 0.2), 0, 1))
            _shell(mb, p + np.array([0.0, yy, 0.0]) + n * 0.005, n, np.array([0.0, 1.0, 0.0]), size,
                   int(rng.integers(0, GLYPH_CELLS * GLYPH_CELLS)), age, rng, shell_mat)
            placed += 1
    lod = kc.MeshBuilder("wakeshell_wall-lod1")
    for k in range(8):
        s = -WAKE_ARC_M * 0.5 + WAKE_ARC_M * (k + 0.5) / 8
        p, n, a = on_arc(s, -thick * 0.5)
        kc.rounded_block(lod, p + np.array([0.0, WAKE_HEIGHT_M * 0.5 + 0.05, 0.0]),
                         (WAKE_ARC_M / 16 + 0.02, WAKE_HEIGHT_M * 0.5 + 0.05, thick * 0.5), lod.material(M_MORTAR),
                         rot=kc.rot_y(-a), seg=1, radius=0.03)
    return [mb, lod]


def build_wake_shell_set(seed: int = 717) -> list[kc.MeshBuilder]:
    """M3-ENV-743: one named wake-shell set in the wall (no stand), the gap's size (WAKE_GAP): its centre at the
    origin, its face out along +Z, the glyph state by material override (`kit_wake_shell_inked`, `_faded`)."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("wake_shell_set", seed)
        mb = kc.MeshBuilder("wake_shell_set" + ("-lod1" if lod else ""))
        _shell(mb, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0), WAKE_GAP[2] * 1.05, 5, 0.0, rng,
               mb.material(M_SHELL))
        out.append(mb)
    return out


TARGETS = {
    "tidewall_straight": lambda: build_tidewall("tidewall_straight", 61, "none"),
    "tidewall_windgap": lambda: build_tidewall("tidewall_windgap", 62, "windgap"),
    "tidewall_gate": lambda: build_tidewall("tidewall_gate", 63, "gate"),
    "wakeshell_wall": build_wakeshell_wall,
    "wake_shell_set": build_wake_shell_set,
}
