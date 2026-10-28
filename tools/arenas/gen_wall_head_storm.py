#!/usr/bin/env python3
"""M3-BPR-406: writes the greybox Ch8 battle arena game/battle/arenas/wall_head_storm.tscn (the Corrow wall-head in
the storm, the Ch8 grade of docs/kb/art/color_script.md). Usage: gen_wall_head_storm.py <out.tscn>."""
import math, sys

def lin(h):  # sRGB hex -> Godot Color (sRGB values, as the other arenas write them)
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def col(h, a=1.0):
    r, g, b = lin(h); return "Color(%.3f, %.3f, %.3f, %.1f)" % (r, g, b, a)

def basis_dir(elev, azim):
    # A DirectionalLight3D shines along -Z of its basis; build a basis whose -Z points down at `elev` from azimuth `azim`.
    e, a = math.radians(elev), math.radians(azim)
    d = (-math.cos(e) * math.sin(a), -math.sin(e), -math.cos(e) * math.cos(a))  # light travel direction
    z = tuple(-c for c in d)
    up = (0.0, 1.0, 0.0)
    x = (up[1]*z[2]-up[2]*z[1], up[2]*z[0]-up[0]*z[2], up[0]*z[1]-up[1]*z[0])
    n = math.sqrt(sum(c*c for c in x)); x = tuple(c/n for c in x)
    y = (z[1]*x[2]-z[2]*x[1], z[2]*x[0]-z[0]*x[2], z[0]*x[1]-z[1]*x[0])
    return "Transform3D(%.6f, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f, 0, 9, 0)" % (
        x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2])

subs, nodes = [], []
mats = {
    "Mat_laterite": ("#8A5A3C", 0.85), "Mat_laterite_dark": ("#6A4430", 0.9), "Mat_stone": ("#5A5650", 0.9),
    "Mat_stone_dark": ("#3E3C3A", 0.95), "Mat_sea": ("#1E3E44", 0.3), "Mat_storm": ("#2A323C", 1.0),
    "Mat_storm_far": ("#3A424C", 1.0), "Mat_rope": ("#7A6A4E", 1.0), "Mat_iron": ("#2A2826", 0.6),
}
for mid, (c, rough) in mats.items():
    subs.append('[sub_resource type="StandardMaterial3D" id="%s"]\nalbedo_color = %s\nroughness = %.2f\n' % (mid, col(c), rough))
subs.append('[sub_resource type="StandardMaterial3D" id="Mat_lamp"]\nalbedo_color = %s\nemission_enabled = true\nemission = %s\nemission_energy_multiplier = 1.4\n' % (col("#FFB070"), col("#FFB070")))

meshes = {}
def box(name, size, mat):
    key = (size, mat)
    if key not in meshes:
        mid = "Box_%d" % len(meshes)
        meshes[key] = mid
        subs.append('[sub_resource type="BoxMesh" id="%s"]\nmaterial = SubResource("%s")\nsize = Vector3(%.3f, %.3f, %.3f)\n' % (mid, mat, *size))
    return meshes[key]

cyls = {}
def cyl(r_top, r_bot, h, mat):
    key = (r_top, r_bot, h, mat)
    if key not in cyls:
        mid = "Cyl_%d" % len(cyls)
        cyls[key] = mid
        subs.append('[sub_resource type="CylinderMesh" id="%s"]\nmaterial = SubResource("%s")\ntop_radius = %.3f\nbottom_radius = %.3f\nheight = %.3f\nradial_segments = 16\n' % (mid, mat, r_top, r_bot, h))
    return cyls[key]

def node(name, mesh, pos, rot_y=0.0, extra=""):
    c, s = math.cos(math.radians(rot_y)), math.sin(math.radians(rot_y))
    nodes.append('[node name="%s" type="MeshInstance3D" parent="."]\ntransform = Transform3D(%.6f, 0, %.6f, 0, 1, 0, %.6f, 0, %.6f, %.3f, %.3f, %.3f)\nmesh = SubResource("%s")\n%s' % (name, c, -s, s, c, pos[0], pos[1], pos[2], mesh, extra))

# The wall-walk: warm laterite slab, flat at y = 0 where the fighters stand.
node("Walk", box("walk", (60.0, 0.6, 9.0), "Mat_laterite"), (0.0, -0.3, 0.0))
for i, x in enumerate([-24.0, -16.0, -8.0, -4.0, 0.0, 4.0, 8.0, 16.0, 24.0]):  # joints between the wall-walk's courses
    node("Joint%d" % i, box("joint", (0.06, 0.02, 9.0), "Mat_laterite_dark"), (x, 0.005, 0.0))
# The parapet behind everyone (seaward), with crenels: the Reach comes over it.
node("Parapet", box("parapet", (60.0, 1.1, 0.7), "Mat_stone"), (0.0, 0.55, -4.6))
for i in range(30):
    node("Merlon%d" % i, box("merlon", (1.0, 0.6, 0.7), "Mat_stone"), (-29.0 + i * 2.0, 1.4, -4.6))
# The wall's sea face falling away below the parapet.
node("SeaFace", box("seaface", (60.0, 8.0, 0.8), "Mat_stone_dark"), (0.0, -4.3, -5.3))
# The wall's landward face down to the low town, and the town's ground far below (seen when the camera pulls back).
node("LandFace", box("landface", (60.0, 12.0, 0.8), "Mat_stone_dark"), (0.0, -6.3, 4.9))
node("LowTown", box("lowtown", (200.0, 0.4, 120.0), "Mat_laterite_dark"), (0.0, -12.3, 65.0))
# The Fisher Stair, going down landward at the party's side (screen right); EntryMarker_ward at its head.
node("StairHead", box("stairhead", (2.2, 0.6, 2.4), "Mat_laterite"), (5.6, -0.3, -1.4))
for i in range(7):
    node("Step%d" % i, box("step", (0.5, 0.3, 2.2), "Mat_laterite_dark"), (6.95 + i * 0.5, -0.45 - i * 0.3, -1.4))
node("StairWallN", box("stairwall", (4.0, 0.9, 0.3), "Mat_stone"), (8.2, -0.6, -2.65))
node("StairWallS", box("stairwall", (4.0, 0.9, 0.3), "Mat_stone"), (8.2, -0.6, -0.15))
# Liss's hoist at the stair head: plain rope and iron (ADR 0017 (c): nothing bound).
node("HoistPost", box("hoistpost", (0.18, 2.6, 0.18), "Mat_iron"), (6.4, 1.3, -2.5))
node("HoistArm", box("hoistarm", (1.6, 0.14, 0.14), "Mat_iron"), (7.1, 2.55, -2.5))
node("HoistRope", box("hoistrope", (0.04, 2.2, 0.04), "Mat_rope"), (7.8, 1.4, -2.5))
# Two steady watch lamps on the parapet (warm laterite against a slate sky); steady, no flicker.
for i, x in enumerate([-6.0, 3.0]):
    node("LampPost%d" % i, box("lamppost", (0.12, 1.2, 0.12), "Mat_iron"), (x, 1.7, -4.2))
    node("Lamp%d" % i, box("lamp", (0.26, 0.3, 0.26), "Mat_lamp"), (x, 2.4, -4.2))
# The storm sea below and beyond; the storm wall's dark columns on the horizon.
node("Sea", box("sea", (600.0, 0.2, 400.0), "Mat_sea"), (0.0, -7.5, -205.0))
# The storm wall: low, wide banks far out over the sea (the fog takes their edges); no near columns.
for i, (x, z, w, h) in enumerate([(-120, -170, 140, 34), (10, -190, 160, 42), (140, -175, 130, 30)]):
    node("StormBank%d" % i, box("stormbank%d" % i, (w, h, 14.0), "Mat_storm_far"), (x, h * 0.5 - 7.5, z))

env = '''[sub_resource type="ProceduralSkyMaterial" id="Sky_mat"]
sky_top_color = %s
sky_horizon_color = %s
sky_curve = 0.1
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
tonemap_exposure = 0.8
glow_enabled = true
glow_intensity = 0.35
glow_bloom = 0.04
fog_enabled = true
fog_mode = 1
fog_light_color = %s
fog_density = 0.6
fog_depth_begin = 16.0
fog_depth_end = 140.0
adjustment_enabled = true
adjustment_saturation = 0.95
''' % (col("#3E4A57"), col("#8A8070"), col("#1E2A30"), col("#8A8070"), col("#5E6E80"), col("#5E6670"))

head = '''[gd_scene load_steps=%d format=3]

; M3-BPR-406: the wall-head of the Corrow seawall in the storm (Ch8 B13-B16: ch08_stair_hold_1..3, undertows_reach),
; greybox until env-art's arena lands (request M3-BPR-407). The Ch8 grade (color_script.md "Ch8 The Seawall"): sun 30
; deg az 250, key #FFE4CE 2.0, fill #5E6E80 0.5, rim #CFE8FF 1.2, sky #3E4A57 / #8A8070, fog #5E6670, exposure 0.80,
; saturation x0.95. Warm laterite wall-walk flat at y = 0, the parapet and the storm sea behind, the Fisher Stair going
; down landward at the party's side with EntryMarker_ward at its head (where the Climb "is"), Liss's hoist of plain
; rope and iron. Two steady watch lamps; every light light_volumetric_fog_energy 0. No glow at the stair foot (Kerrid).
; Generated by tools/arenas/gen_wall_head_storm.py (python3 tools/arenas/gen_wall_head_storm.py game/battle/arenas/wall_head_storm.tscn); edit the script, not this file.

'''
lights = '''[node name="WallHeadStorm" type="Node3D"]

[node name="WorldEnvironment" type="WorldEnvironment" parent="."]
environment = SubResource("Env_main")

[node name="Sun" type="DirectionalLight3D" parent="."]
transform = %s
light_color = %s
light_energy = 2.0
light_volumetric_fog_energy = 0.0
shadow_enabled = true
directional_shadow_max_distance = 30.0

[node name="Fill" type="DirectionalLight3D" parent="."]
transform = %s
light_color = %s
light_energy = 0.5
light_volumetric_fog_energy = 0.0

[node name="Rim" type="DirectionalLight3D" parent="."]
transform = %s
light_color = %s
light_energy = 1.2
light_volumetric_fog_energy = 0.0

[node name="EntryMarker_ward" type="Marker3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 5.2, 0, -1.4)

''' % (basis_dir(30, 250), col("#FFE4CE"), basis_dir(40, 70), col("#5E6E80"), basis_dir(18, 160), col("#CFE8FF"))
lamps = ""
for i, x in enumerate([-6.0, 3.0]):
    lamps += '''[node name="LampLight%d" type="OmniLight3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, %.3f, 2.4, -3.9)
light_color = %s
light_energy = 1.2
light_volumetric_fog_energy = 0.0
omni_range = 5.0

''' % (i, x, col("#FFB070"))
out = head % (len(subs) + 4) + env + "\n" + "\n".join(subs) + "\n" + lights + "\n".join(nodes) + "\n" + lamps
open(sys.argv[1], "w").write(out.rstrip() + "\n")
