#!/usr/bin/env python3
"""M3-BPR-418: writes the greybox Act II boss arenas into game/battle/arenas/, until env-art's kits exist.

Each arena follows its chapter's grade in docs/kb/art/color_script.md and its place in docs/kb/art/creatures/
act2_roster.md. The fighters stand flat at y = 0 (party slots at +x, foes at -x, the battle camera at z +8.4 looking
down -z), so every backdrop sits at -z. Lights set light_volumetric_fog_energy 0 (the Lead's rule). Every arena
keeps a node named Sea (the arena contract, test_battle_arena: the flood rig's water).

    fen_roots_dusk        Ch10, the Mangrove Drowner: a mud bar in tannin water under the prop-root cage, overcast dusk.
    lowlight_engine_hall  Ch11, the Lamp Engine: Lowlight's flooded hall, pillars, conduits in steady bound teal.
    keth_terrace_wall     Ch12, the Avalanche Ram: a snow terrace under the Lit Age terrace wall with its cold seep,
                          the pass-cords' red knots the only warm note.
    night_sea_barge       Ch15, the Wakefin: the drifting wedding barge at night, no lamp struck; the sea-glow only.

Usage: python3 tools/arenas/gen_act2_arenas.py [out_dir]   (default game/battle/arenas). Edit this script, not the
generated scenes.
"""
import math
import sys
from pathlib import Path


def lin(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def col(h: str, a: float = 1.0) -> str:
    r, g, b = lin(h)
    return "Color(%.3f, %.3f, %.3f, %.1f)" % (r, g, b, a)


def euler_basis(rx: float, ry: float, rz: float) -> list:
    """Godot's YXZ euler (degrees) as the basis' three column vectors (x, y, z axes), as .tscn writes them."""
    x, y, z = (math.radians(a) for a in (rx, ry, rz))
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    ry_m = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    rx_m = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    rz_m = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]

    def mul(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

    m = mul(mul(ry_m, rx_m), rz_m)
    return [(m[0][c], m[1][c], m[2][c]) for c in range(3)]


def light_basis(elev: float, azim: float) -> str:
    """A DirectionalLight3D shines along -Z of its basis: a basis whose -Z points down at `elev` from azimuth `azim`."""
    e, a = math.radians(elev), math.radians(azim)
    d = (-math.cos(e) * math.sin(a), -math.sin(e), -math.cos(e) * math.cos(a))
    z = tuple(-c for c in d)
    up = (0.0, 1.0, 0.0)
    x = (up[1] * z[2] - up[2] * z[1], up[2] * z[0] - up[0] * z[2], up[0] * z[1] - up[1] * z[0])
    n = math.sqrt(sum(c * c for c in x))
    x = tuple(c / n for c in x)
    y = (z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0])
    return "Transform3D(%.6f, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f, 0, 9, 0)" % (
        x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2])


class Arena:
    def __init__(self, root: str, note: str) -> None:
        self.root, self.note = root, note
        self.subs: list = []
        self.nodes: list = []
        self.extra: list = []
        self._mats: dict = {}
        self._meshes: dict = {}

    def mat(self, hexc: str, rough: float = 0.9, emit: float = 0.0) -> str:
        key = (hexc, rough, emit)
        if key not in self._mats:
            mid = "Mat_%d" % len(self._mats)
            self._mats[key] = mid
            s = '[sub_resource type="StandardMaterial3D" id="%s"]\nalbedo_color = %s\nroughness = %.2f\n' % (
                mid, col(hexc), rough)
            if emit > 0.0:
                s += "emission_enabled = true\nemission = %s\nemission_energy_multiplier = %.2f\n" % (col(hexc), emit)
            self.subs.append(s)
        return self._mats[key]

    def _mesh(self, kind: str, body: str, mat: str) -> str:
        key = (kind, body, mat)
        if key not in self._meshes:
            mid = "%s_%d" % (kind, len(self._meshes))
            self._meshes[key] = mid
            self.subs.append('[sub_resource type="%s" id="%s"]\nmaterial = SubResource("%s")\n%s' % (kind, mid, mat, body))
        return self._meshes[key]

    def box(self, size: tuple, mat: str) -> str:
        return self._mesh("BoxMesh", "size = Vector3(%.3f, %.3f, %.3f)\n" % size, mat)

    def cyl(self, r_top: float, r_bot: float, h: float, mat: str, segments: int = 12) -> str:
        body = "top_radius = %.3f\nbottom_radius = %.3f\nheight = %.3f\nradial_segments = %d\n" % (r_top, r_bot, h, segments)
        return self._mesh("CylinderMesh", body, mat)

    def node(self, name: str, mesh: str, pos: tuple, rot: tuple = (0.0, 0.0, 0.0)) -> None:
        b = euler_basis(*rot)
        t = ", ".join("%.6f" % v for axis in b for v in axis)
        self.nodes.append('[node name="%s" type="MeshInstance3D" parent="."]\ntransform = Transform3D(%s, %.3f, %.3f, %.3f)\n'
                          'mesh = SubResource("%s")\n' % (name, t, pos[0], pos[1], pos[2], mesh))

    def omni(self, name: str, pos: tuple, color: str, energy: float, rng: float) -> None:
        self.extra.append('[node name="%s" type="OmniLight3D" parent="."]\ntransform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, '
                          '%.3f, %.3f, %.3f)\nlight_color = %s\nlight_energy = %.2f\nlight_volumetric_fog_energy = 0.0\n'
                          'omni_range = %.1f\n' % (name, pos[0], pos[1], pos[2], col(color), energy, rng))

    def write(self, out: Path, grade: dict) -> None:
        env = '''[sub_resource type="ProceduralSkyMaterial" id="Sky_mat"]
sky_top_color = %s
sky_horizon_color = %s
sky_curve = 0.12
ground_bottom_color = %s
ground_horizon_color = %s
sun_angle_max = 20.0

[sub_resource type="Sky" id="Sky_main"]
sky_material = SubResource("Sky_mat")

[sub_resource type="Environment" id="Env_main"]
background_mode = 2
sky = SubResource("Sky_main")
ambient_light_source = 3
ambient_light_color = %s
ambient_light_sky_contribution = 0.5
tonemap_mode = 4
tonemap_exposure = %.2f
glow_enabled = true
glow_intensity = 0.35
glow_bloom = 0.04
fog_enabled = true
fog_mode = 1
fog_light_color = %s
fog_density = %.2f
fog_depth_begin = %.1f
fog_depth_end = %.1f
adjustment_enabled = true
adjustment_saturation = %.2f
''' % (col(grade["sky"][0]), col(grade["sky"][1]), col(grade["ground"]), col(grade["sky"][1]), col(grade["fill"][0]),
       grade["exposure"], col(grade["fog"]), grade["fog_density"], grade["fog_range"][0], grade["fog_range"][1],
       grade["saturation"])
        lights = '[node name="%s" type="Node3D"]\n\n[node name="WorldEnvironment" type="WorldEnvironment" parent="."]\n' \
                 'environment = SubResource("Env_main")\n\n' % self.root
        for name, key, shadow in (("Sun", "key", True), ("Fill", "fill", False), ("Rim", "rim", False)):
            hexc, energy, elev, azim = grade[key]
            lights += '[node name="%s" type="DirectionalLight3D" parent="."]\ntransform = %s\nlight_color = %s\n' \
                      'light_energy = %.2f\nlight_volumetric_fog_energy = 0.0\n' % (
                          name, light_basis(elev, azim), col(hexc), energy)
            if shadow:
                lights += "shadow_enabled = true\ndirectional_shadow_max_distance = 30.0\n"
            lights += "\n"
        head = "[gd_scene load_steps=%d format=3]\n\n%s\n; Generated by tools/arenas/gen_act2_arenas.py; edit the script, " \
               "not this file.\n\n" % (len(self.subs) + 4, "\n".join("; " + ln for ln in self.note.splitlines()))
        text = head + env + "\n" + "\n".join(self.subs) + "\n" + lights + "\n".join(self.nodes) + "\n" + "\n".join(self.extra)
        out.write_text(text.rstrip() + "\n")


def fen_roots_dusk() -> tuple:
    a = Arena("FenRootsDusk", "M3-BPR-418: Ch10, the Mangrove Drowner's roots in Ossa Fen (act2_roster.md), greybox until\n"
              "env-art's fen kit. The Ch10 grade (color_script.md): overcast dusk, sun 2 deg az 275, key #FFFEFA 0.9,\n"
              "fill #6F7E8E 0.5, rim #FFE9B8 0.6, sky #4A5868 / #9A9488, fog #5A6A62, exposure 0.90, saturation x0.85.\n"
              "A mud bar in brown-black tannin water; the prop-root cage the Drowner grows through behind the foes.")
    mud, mud_dark = a.mat("#3E3426", 0.95), a.mat("#2E271C", 1.0)
    water = a.mat("#3A2A18", 0.12)
    root, root_dark = a.mat("#4A4034", 0.95), a.mat("#3A3229", 1.0)
    tree_far, reed = a.mat("#4A5A50", 1.0), a.mat("#6A6A4E", 1.0)
    a.node("MudBar", a.box((40.0, 0.6, 14.0), mud), (0.0, -0.3, 0.0))
    for i, (x, z, w) in enumerate([(-9.0, 4.0, 6.0), (6.0, -4.5, 7.0), (-2.0, 5.6, 5.0)]):
        a.node("MudDark%d" % i, a.box((w, 0.02, 2.4), mud_dark), (x, 0.005, z))
    a.node("Sea", a.box((400.0, 0.1, 300.0), water), (0.0, -0.35, -100.0))  # the arena contract's Sea
    # The prop-root cage: a trunk and roots leaning out to the mud, behind the foes' side (screen left).
    a.node("Trunk", a.cyl(0.55, 0.8, 7.0, root_dark), (-4.5, 3.5, -6.0))
    for i, (x, z, lean, turn) in enumerate([(-6.8, -4.2, 28, 0), (-2.4, -4.4, -26, 0), (-5.6, -3.4, 20, 40),
                                            (-3.2, -3.6, -18, -35), (-7.6, -5.8, 32, 70), (-1.6, -6.2, -30, -60)]):
        a.node("Root%d" % i, a.cyl(0.12, 0.2, 4.6, root), (x, 1.8, z), (0.0, turn, lean))
    for i, (x, z, h) in enumerate([(-30, -42, 10), (-14, -48, 13), (2, -45, 9), (18, -50, 12), (34, -44, 10)]):
        a.node("TreeLine%d" % i, a.box((16.0, h, 4.0), tree_far), (x, h * 0.5 - 0.3, z))
    for i, x in enumerate([5.0, 6.2, 7.1, 9.4, -11.0, -12.3]):
        a.node("Reed%d" % i, a.box((0.06, 1.3, 0.06), reed), (x, 0.65, -6.6 + (i % 3) * 0.4))
    grade = {"sky": ("#4A5868", "#9A9488"), "ground": "#2E271C", "fog": "#5A6A62", "fog_density": 0.55,
             "fog_range": (14.0, 120.0), "exposure": 0.90, "saturation": 0.85,
             "key": ("#FFFEFA", 0.9, 8.0, 275.0), "fill": ("#6F7E8E", 0.5, 40.0, 95.0), "rim": ("#FFE9B8", 0.6, 12.0, 180.0)}
    return a, grade


def lowlight_engine_hall() -> tuple:
    a = Arena("LowlightEngineHall", "M3-BPR-418: Ch11, the Lamp Engine's hall in Lowlight (act2_roster.md), greybox until env-art's\n"
              "kit. The Ch11 grade (color_script.md): overcast midday, sun 65 deg az 200 through the open roof, key #F3F2FF\n"
              "1.4, fill #7FA3A8 0.7, rim #BFE6E0 0.6, sky #7A8896 / #A8B4B8, fog #8A9A98, exposure 0.75, saturation x0.85.\n"
              "Silent and dead: pale stone, a shallow channel, pillars, and Lit Age conduits in steady bound teal (never\n"
              "flicker, never gold); the engine's recess behind the foes.")
    floor, floor_dark = a.mat("#8A9A98", 0.8), a.mat("#6A7A78", 0.85)
    wall, pillar = a.mat("#6A7472", 0.9), a.mat("#7A8684", 0.85)
    channel = a.mat("#0E4A55", 0.1)
    conduit = a.mat("#4FB3B0", 0.4, 1.0)
    brass = a.mat("#B08D57", 0.45)
    a.node("Floor", a.box((32.0, 0.6, 16.0), floor), (0.0, -0.3, 0.0))
    for i, x in enumerate([-12.0, -8.0, -4.0, 0.0, 4.0, 8.0, 12.0]):
        a.node("Joint%d" % i, a.box((0.05, 0.02, 16.0), floor_dark), (x, 0.005, 0.0))
    a.node("Sea", a.box((32.0, 0.04, 1.4), channel), (0.0, 0.01, -4.6))  # the channel: the arena contract's Sea
    a.node("BackWall", a.box((32.0, 11.0, 0.8), wall), (0.0, 5.2, -7.4))
    a.node("SideWallW", a.box((0.8, 11.0, 16.0), wall), (-15.6, 5.2, 0.0))
    a.node("RoofW", a.box((13.0, 0.6, 16.0), wall), (-9.5, 10.6, 0.0))
    a.node("RoofE", a.box((13.0, 0.6, 16.0), wall), (9.5, 10.6, 0.0))
    for i, x in enumerate([-10.0, -6.0, 6.0, 10.0]):
        a.node("Pillar%d" % i, a.cyl(0.5, 0.55, 10.0, pillar, 16), (x, 5.0, -5.8))
    for i, y in enumerate([1.1, 2.6, 4.4]):
        a.node("Conduit%d" % i, a.box((30.0, 0.08, 0.08), conduit), (0.0, y, -6.95))
    # The engine's recess behind the foes (screen left): a brass-framed arch in the back wall.
    a.node("RecessBack", a.box((5.0, 6.0, 0.4), floor_dark), (-3.0, 3.0, -6.9))
    a.node("RecessFrameL", a.box((0.3, 6.2, 0.5), brass), (-5.6, 3.1, -6.7))
    a.node("RecessFrameR", a.box((0.3, 6.2, 0.5), brass), (-0.4, 3.1, -6.7))
    a.node("RecessFrameTop", a.box((5.5, 0.3, 0.5), brass), (-3.0, 6.2, -6.7))
    grade = {"sky": ("#7A8896", "#A8B4B8"), "ground": "#6A7A78", "fog": "#8A9A98", "fog_density": 0.35,
             "fog_range": (12.0, 80.0), "exposure": 0.75, "saturation": 0.85,
             "key": ("#F3F2FF", 1.4, 65.0, 200.0), "fill": ("#7FA3A8", 0.7, 35.0, 20.0), "rim": ("#BFE6E0", 0.6, 15.0, 120.0)}
    return a, grade


def keth_terrace_wall() -> tuple:
    a = Arena("KethTerraceWall", "M3-BPR-418: Ch12, the Avalanche Ram's terrace wall on Keth Pass (act2_roster.md), greybox until\n"
              "env-art's kit. The Ch12 grade (color_script.md): morning, sun 30 deg az 140, key #FAF6FF 2.8, fill #7FA6DC\n"
              "0.8, rim #FFFFFF 0.6, sky #1E5BB8 / #C8D8E8, fog #D0DCE8, exposure 0.65, saturation x0.9. Snow on rock under\n"
              "the Lit Age terrace wall and its seep of drowned light (glimmer_held, dim and cold); the pass-cords' red\n"
              "knots the only warm note.")
    snow, rock, rock_dark = a.mat("#D8DCE0", 0.9), a.mat("#6A6E72", 0.95), a.mat("#4E5256", 1.0)
    wall, ice = a.mat("#8A8E92", 0.9), a.mat("#C8D8E8", 0.3)
    seep = a.mat("#7FC6D9", 0.3, 0.6)
    peak, cap = a.mat("#9AA8B8", 1.0), a.mat("#E8EEF4", 0.9)
    cord, knot, post = a.mat("#7A6A52", 1.0), a.mat("#9A2E26", 0.9), a.mat("#4E4438", 1.0)
    a.node("Terrace", a.box((40.0, 0.6, 14.0), snow), (0.0, -0.3, 0.0))
    for i, (x, z, w, d) in enumerate([(-8.0, 3.6, 3.0, 1.6), (7.5, -3.0, 2.4, 1.2), (12.0, 4.4, 3.4, 1.8)]):
        a.node("Rock%d" % i, a.box((w, 0.5, d), rock), (x, 0.0, z))
    a.node("TerraceWall", a.box((28.0, 7.0, 1.2), wall), (-6.0, 3.5, -6.4))
    for i, x in enumerate([-14.0, -8.0, -2.0, 4.0]):
        a.node("Course%d" % i, a.box((0.06, 7.0, 0.04), rock_dark), (x, 3.5, -5.78))
    a.node("Seep", a.box((0.5, 4.8, 0.06), seep), (-4.0, 3.0, -5.76))
    for i, (x, h) in enumerate([(-4.6, 3.2), (-3.4, 2.4), (-5.2, 1.6)]):
        a.node("Ice%d" % i, a.box((0.3, h, 0.12), ice), (x, h * 0.5, -5.7))
    a.node("Drop", a.box((40.0, 30.0, 0.8), rock_dark), (0.0, -15.6, 7.4))
    a.node("Sea", a.box((160.0, 0.1, 90.0), ice), (0.0, -30.0, 60.0))  # a frozen tarn below the drop (the contract's Sea)
    for i, (x, z, r, h) in enumerate([(-80, -160, 40, 70), (-10, -190, 50, 95), (70, -170, 45, 80)]):
        a.node("Peak%d" % i, a.cyl(0.0, r, h, peak, 6), (x, h * 0.5 - 20.0, z))
        a.node("Cap%d" % i, a.cyl(0.0, r * 0.32, h * 0.32, cap, 6), (x, h - 20.0 - h * 0.16, z))
    # The pass-cord along the party's side (screen right): posts, the cord and its red knots.
    for i, x in enumerate([3.0, 7.0, 11.0]):
        a.node("CordPost%d" % i, a.box((0.12, 1.4, 0.12), post), (x, 0.7, -4.6))
    a.node("Cord", a.box((8.2, 0.03, 0.03), cord), (7.0, 1.3, -4.6))
    for i, x in enumerate([3.8, 4.9, 6.1, 7.6, 8.8, 10.2]):
        a.node("Knot%d" % i, a.box((0.08, 0.12, 0.08), knot), (x, 1.22, -4.6))
    grade = {"sky": ("#1E5BB8", "#C8D8E8"), "ground": "#4E5256", "fog": "#D0DCE8", "fog_density": 0.2,
             "fog_range": (30.0, 260.0), "exposure": 0.65, "saturation": 0.90,
             "key": ("#FAF6FF", 2.8, 30.0, 140.0), "fill": ("#7FA6DC", 0.8, 40.0, 320.0), "rim": ("#FFFFFF", 0.6, 15.0, 230.0)}
    return a, grade


def night_sea_barge() -> tuple:
    a = Arena("NightSeaBarge", "M3-BPR-418: Ch15, the Wakefin on the open sea at night (act2_roster.md), greybox until env-art's\n"
              "kit. The Ch15 grade (color_script.md): moon key #D2DFFF 0.25, fill #0B1630 0.15, rim #9DB4D9 0.4, sky #050A14\n"
              "/ #0B1630, fog #1C3A4A, exposure 1.10, saturation x0.85. The party on the drifting wedding barge; the foes in\n"
              "the water. No lamp is struck (no warm source): the only light is the moon and the sea-glow (#1C6B78, 0.12).")
    deck, deck_dark = a.mat("#4A3E32", 0.9), a.mat("#33291F", 0.95)
    rail, cloth = a.mat("#3A3026", 0.95), a.mat("#B8B0A0", 1.0)
    sea = a.mat("#1C6B78", 0.08, 0.12)
    a.node("Sea", a.box((400.0, 0.1, 300.0), sea), (0.0, -0.08, -100.0))
    a.node("Deck", a.box((9.0, 0.5, 8.0), deck), (4.6, -0.25, 0.4))
    for i, z in enumerate([-2.4, -0.8, 0.8, 2.4]):
        a.node("Plank%d" % i, a.box((9.0, 0.02, 0.04), deck_dark), (4.6, 0.005, z))
    a.node("Hull", a.box((9.2, 1.0, 8.2), deck_dark), (4.6, -0.9, 0.4))
    a.node("RailW", a.box((0.12, 0.5, 8.0), rail), (0.15, 0.25, 0.4))
    a.node("RailN", a.box((9.0, 0.5, 0.12), rail), (4.6, 0.25, -3.55))
    # The wedding canopy's bare frame at the stern, its cloth furled (no one sits under it tonight).
    for i, (x, z) in enumerate([(7.2, -2.6), (8.8, -2.6), (7.2, -1.0), (8.8, -1.0)]):
        a.node("CanopyPole%d" % i, a.box((0.1, 2.2, 0.1), rail), (x, 1.1, z))
    a.node("CanopyFurl", a.cyl(0.14, 0.14, 1.6, cloth), (8.0, 2.2, -2.6), (0.0, 0.0, 90.0))
    grade = {"sky": ("#050A14", "#0B1630"), "ground": "#061A2B", "fog": "#1C3A4A", "fog_density": 0.3,
             "fog_range": (20.0, 160.0), "exposure": 1.10, "saturation": 0.85,
             "key": ("#D2DFFF", 0.25, 35.0, 200.0), "fill": ("#0B1630", 0.15, 40.0, 20.0), "rim": ("#9DB4D9", 0.4, 15.0, 120.0)}
    return a, grade


ARENAS = {"fen_roots_dusk": fen_roots_dusk, "lowlight_engine_hall": lowlight_engine_hall,
          "keth_terrace_wall": keth_terrace_wall, "night_sea_barge": night_sea_barge}


def main() -> int:
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "game/battle/arenas")
    for aid, build in ARENAS.items():
        arena, grade = build()
        arena.write(out_dir / ("%s.tscn" % aid), grade)
        print("wrote", out_dir / ("%s.tscn" % aid))
    return 0


if __name__ == "__main__":
    sys.exit(main())
