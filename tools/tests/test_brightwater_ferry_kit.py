"""Tests for the Brightwater ferry procedural kit (M3-ENV-08). Run: python3 -m unittest discover -s tools/tests

* Geometry (no Blender needed): every target is inside its budget with an authored LOD1 chain, the generators are
  deterministic, the weathering channels are in [0, 1], and every slot is a `bf_*` slot.
* The ship is walkable: the main deck's planks lie flat at y 0 and the poop's at y 0.9; the gangways are open;
  the hatches are where the deck has no planks; the rig's shrouds come down on the hull's chain-plates.
* Kin: the ferry and the drowned hulls are one hull generator, with M3-ENV-06's `arena_derelict_deck` plank,
  seam and plank-thickness proportions; the drowned carry no light.
* The grade: lut_ch04_crossing keeps the sea's teal where ch04_wake greys it, and is ch04_wake elsewhere.
* Committed assets: one .glb per target inside its budget, every file under 5 MB with a PROVENANCE row, the kit's
  post-import on every .glb, a material for every slot, the manifest, the Blender job (4 threads), and the preview
  layout names only kit pieces, with a lantern piece at every lamp.
* The Seventh Terrace (M3-ENV-08B): the ferry's hull generator, a flat walkable deck and poop, the open main hatch over
  the hold, the name-board a separate piece on its brackets, the three sail states, only the membrane's seams glow,
  nothing ties the ferry to the derelict, and the Ch4 insert (D06) frames the board from Ch1's O07 point.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import re
import struct
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "brightwater_ferry"
ASSETS = ROOT / "assets" / "environments" / "kits" / "brightwater_ferry"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "brightwater_ferry_kit"
LAYOUT = PREVIEW / "brightwater_ferry_layout.json"
ORUVEL_PREVIEW = ROOT / "game" / "levels" / "_tests" / "oruvel_kit"
MAX_BYTES = 5 * 1024 * 1024

sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"brightwater_ferry_kit_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")
import bf_common as bf  # noqa: E402
import bf_deckhouse  # noqa: E402
import bf_drowned  # noqa: E402
import bf_hull  # noqa: E402
import bf_props  # noqa: E402
import bf_rig  # noqa: E402
import bf_terrace as bt  # noqa: E402
import bf_terrace_rig as btr  # noqa: E402

TARGETS = BUILD.targets()
_CACHE: dict[str, list] = {}


def built(name: str) -> list:
    if name not in _CACHE:
        _CACHE[name] = BUILD.build_target(TARGETS[name][2])
    return _CACHE[name]


def read_glb(path: Path) -> dict:
    data = path.read_bytes()
    magic, _v, _len = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a glb"
    jlen = struct.unpack("<I", data[12:16])[0]
    return json.loads(data[20:20 + jlen])


def tris_of(mb, slot: str) -> np.ndarray:
    """(n, 3, 3) triangles of one slot."""
    if slot not in mb.materials:
        return np.zeros((0, 3, 3))
    k = mb.materials.index(slot)
    pos = np.asarray(mb.pos)
    idx = np.asarray([t for t, m in zip(mb.tris, mb.tri_mat) if m == k])
    return pos[idx]


class KitGeometryTests(unittest.TestCase):
    def test_every_target_is_inside_its_budget_with_a_lod_chain(self) -> None:
        self.assertEqual(len(TARGETS), 28)  # + the landing and boarding gear (M3-ENV-746)
        for name, (key, module, _fn) in TARGETS.items():
            with self.subTest(target=name):
                builders = built(name)
                self.assertEqual([], BUILD.check_budget(module, key, builders))
                self.assertEqual([name, name + "-lod1"], [b.name for b in builders])
                self.assertLess(builders[1].triangle_count, builders[0].triangle_count)

    def test_generators_are_deterministic(self) -> None:
        for name in ("ferry_hull", "ferry_rig", "derelict_hulk_a", "passenger_bundles", "terrace_hull",
                     "terrace_name_board", "terrace_sails_lowered"):
            with self.subTest(target=name):
                a, b = built(name), BUILD.build_target(TARGETS[name][2])
                for x, y in zip(a, b):
                    self.assertEqual(x.tris, y.tris)
                    self.assertEqual(x.materials, y.materials)
                    np.testing.assert_array_equal(np.asarray(x.pos), np.asarray(y.pos))
                    np.testing.assert_array_equal(np.asarray(x.col), np.asarray(y.col))

    def test_channels_in_range_and_slots_are_the_kits(self) -> None:
        for name in TARGETS:
            for mb in built(name):
                with self.subTest(mesh=mb.name):
                    col = np.asarray(mb.col)
                    self.assertTrue((col >= 0.0).all() and (col <= 1.0).all())
                    uv2 = np.asarray(mb.uv2)
                    self.assertTrue((uv2[:, 0] >= 0.0).all() and (uv2[:, 0] <= 1.0).all())
                    self.assertTrue(all(m.startswith("bf_") for m in mb.materials), mb.materials)
                    self.assertEqual(sorted(set(mb.tri_mat)), list(range(len(mb.materials))), "no unused slots")
                    self.assertFalse(np.isnan(np.asarray(mb.nrm)).any(), "normals are finite")
                    self.assertFalse(np.isnan(np.asarray(mb.pos)).any(), "positions are finite")


def _winding_agreement(mb) -> tuple[float, float]:
    """(fraction of faces, fraction of face area) whose geometric winding (b - a) x (c - a) agrees with the sum of
    their vertex normals. Back-face culling keys on the winding, so a face wound against its normals vanishes from
    the side it is lit for."""
    pos, nrm, t = np.asarray(mb.pos), np.asarray(mb.nrm), np.asarray(mb.tris)
    g = np.cross(pos[t[:, 1]] - pos[t[:, 0]], pos[t[:, 2]] - pos[t[:, 0]])
    area = np.linalg.norm(g, axis=1)
    keep = area > 1e-12
    agree = ((g * nrm[t].sum(axis=1)).sum(axis=1) > 0.0)[keep]
    return float(agree.mean()), float(area[keep][agree].sum() / area[keep].sum())


class WindingTests(unittest.TestCase):
    """M3-ENV-700: bf_common.transom was wound inward, so the ferry's and the drowned hulls' transoms vanished from
    astern."""

    def test_the_transom_faces_astern_with_its_normals(self) -> None:
        for form in (bf.FERRY, bf_drowned.FORM_A, bf_drowned.FORM_B):
            for lod in (False, True):
                with self.subTest(form=form.transom_z, lod=lod):
                    mb = bf.kc.MeshBuilder("transom")
                    bf.transom(mb, form, bf.M_BLUE, lod=lod)
                    self.assertEqual((1.0, 1.0), _winding_agreement(mb))

    def test_every_piece_is_wound_with_its_normals(self) -> None:
        for name in TARGETS:
            for mb in built(name):
                with self.subTest(mesh=mb.name):
                    by_count, by_area = _winding_agreement(mb)
                    self.assertGreater(by_count, 0.85)
                    self.assertGreater(by_area, 0.8)


class WalkableShipTests(unittest.TestCase):
    def test_main_deck_and_poop_are_flat(self) -> None:
        mb = built("ferry_hull")[0]
        deck = tris_of(mb, bf.M_DECK).reshape(-1, 3)
        up = deck[np.abs(deck[:, 1]) < 0.05]  # the main deck's plank tops
        main = deck[(deck[:, 2] < bf.POOP_Z - 0.8) & (deck[:, 1] > -0.02)]  # forward of the poop ladders
        self.assertGreater(len(up), 1000)
        self.assertLess(float(np.abs(main[:, 1]).max()), 0.02, "the main deck's planks top out at y 0 (no hump)")
        poop = deck[(deck[:, 2] > bf.POOP_Z + 0.2) & (deck[:, 1] > bf.POOP_Y - 0.02)]
        self.assertLess(float(np.abs(poop[:, 1] - bf.POOP_Y).max()), 0.02, "the poop deck is flat at 0.9")

    def test_gangways_are_open(self) -> None:
        f = bf.FERRY
        z0, z1 = bf.GANGWAY_Z
        self.assertTrue(f.in_gangway(0.5 * (z0 + z1)))
        mb = built("ferry_hull")[0]
        timber = tris_of(mb, bf.M_TIMBER).reshape(-1, 3)
        rail = timber[(timber[:, 2] > z0 + 0.1) & (timber[:, 2] < z1 - 0.1) & (np.abs(timber[:, 0]) > 3.2)
                      & (timber[:, 1] > 0.3)]
        self.assertEqual(len(rail), 0, "nothing stands in the gangways above the sill")

    def test_hatches_have_no_planks_over_them(self) -> None:
        mb = built("ferry_hull")[0]
        deck = tris_of(mb, bf.M_DECK).reshape(-1, 3)
        for hx, hz, ax, az, _h in (bf.MAIN_HATCH, bf.FORE_HATCH):
            inside = (np.abs(deck[:, 0] - hx) < ax - 0.05) & (np.abs(deck[:, 2] - hz) < az - 0.05) & (deck[:, 1] < 0.05)
            self.assertFalse(inside.any(), f"no deck planks inside the hatch at z {hz}")

    def test_shrouds_land_on_the_chain_plates(self) -> None:
        rig = built("ferry_rig")[0]
        rope = tris_of(rig, bf.M_ROPE).reshape(-1, 3)
        for mz in (bf.FOREMAST_Z, bf.MAINMAST_Z):
            for side in (-1.0, 1.0):
                for p in bf.chain_points(bf.FERRY, mz, side):
                    d = np.linalg.norm(rope - (p + np.array([0.0, 0.08, 0.0])), axis=1)
                    self.assertLess(float(d.min()), 0.06, f"a shroud ends at the deadeye {p.round(2)}")

    def test_deckhouse_door_is_clear_of_the_fife_rail(self) -> None:
        self.assertLess(bf.MAINMAST_Z + bf_hull.FIFE_DZ[bf.MAINMAST_Z], bf.MAINMAST_Z, "the main's fife rail is forward")
        self.assertGreater(bf_deckhouse.Z0 - bf.MAINMAST_Z, 0.8, "a passage between the mast and the door")

    def test_sails_belly_to_lee(self) -> None:
        for lug in (bf_rig.FORE, bf_rig.MAIN):
            flat = bf_rig.sail_surface(dataclasses.replace(lug, belly=0.0), np.array(0.4), np.array(0.5))
            full = bf_rig.sail_surface(lug, np.array(0.4), np.array(0.5))
            self.assertLess(float(full[0] - flat[0]), -0.2, "the wind from the starboard beam fills the sail to port")


class KinAndLightTests(unittest.TestCase):
    def test_plank_proportions_match_the_derelict_arena(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "bs_derelict_ro", ROOT / "assets_src" / "environments" / "kits" / "brine_shoals" / "bs_derelict.py")
        bsd = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bsd)
        self.assertEqual(bf.PLANK_W_M, bsd.PLANK_W_M)
        self.assertEqual(bf.PLANK_GAP_M, bsd.PLANK_GAP_M)
        self.assertEqual(bf.PLANK_T_M, bsd.PLANK_T_M)

    def test_the_drowned_are_the_ferrys_hull_and_carry_no_light(self) -> None:
        self.assertIsInstance(bf_drowned.FORM_A, bf.HullForm)
        self.assertIsInstance(bf_drowned.FORM_B, bf.HullForm)
        for name in bf_drowned.TARGETS:
            for mb in built(name):
                with self.subTest(mesh=mb.name):
                    self.assertFalse(set(mb.materials) & set(bf.EMISSIVE), "no lamp on a drowned hull")
        lo, hi = built("derelict_hulk_a")[0].bounds()
        self.assertLess(float(lo[1]), -1.5, "grounded: her hull runs down into the sea")
        self.assertLess(float(hi[1]), 5.0, "dismasted")

    def test_only_the_lantern_and_the_windows_glow(self) -> None:
        for name in TARGETS:
            for mb in built(name):
                glowing = set(mb.materials) & set(bf.EMISSIVE)
                if name == "ferry_lantern":
                    self.assertEqual(glowing, {bf.M_GLASS}, mb.name)
                elif name == "ferry_deckhouse":
                    self.assertEqual(glowing, {bf.M_WINDOW}, mb.name)
                elif name == "terrace_membrane" and not mb.name.endswith(bf.LOD):
                    self.assertEqual(glowing, {btr.M_WOUND}, mb.name)
                else:
                    self.assertEqual(glowing, set(), mb.name)

    def test_lantern_flame_is_inside_its_glass(self) -> None:
        mb = built("ferry_lantern")[0]
        glass = tris_of(mb, bf.M_GLASS).reshape(-1, 3)
        fy = bf_props.LANTERN_FLAME[1]
        self.assertLess(float(glass[:, 1].min()), fy)
        self.assertGreater(float(glass[:, 1].max()), fy)


def _hull_tris(name: str, slot: str) -> np.ndarray:
    return tris_of(built(name)[0], slot).reshape(-1, 3)


class SeventhTerraceTests(unittest.TestCase):
    def test_one_hull_generator_and_its_proportions(self) -> None:
        self.assertIsInstance(bt.FORM, bf.HullForm)
        self.assertIn(bt.M_COPPER, built("terrace_hull")[0].materials, "copper sheathing")
        copper = _hull_tris("terrace_hull", bt.M_COPPER)
        sides = copper[copper[:, 2] < bt.FORM.transom_z - 0.01]  # the rudder's blade is sheathed too
        self.assertLess(float(sides[:, 1].max()), bt.COPPER_Y + 0.02, "the copper stops at its line")
        self.assertGreater(bt.COPPER_Y, bt.WATERLINE_Y + 0.2, "the copper boot-top shows above the waterline")
        lacquer = _hull_tris("terrace_hull", bt.M_LACQUER)
        self.assertGreater(len(lacquer), 1000, "black lacquer topsides")

    def test_main_deck_and_poop_are_flat_and_the_hatch_is_open(self) -> None:
        deck = _hull_tris("terrace_hull", bf.M_DECK)
        main = deck[(deck[:, 2] < bt.POOP_Z - 0.8) & (deck[:, 1] > -0.02)]
        self.assertLess(float(np.abs(main[:, 1]).max()), 0.02, "the main deck tops out at y 0")
        poop = deck[(deck[:, 2] > bt.POOP_Z + 0.2) & (deck[:, 1] > bt.POOP_Y - 0.02)]
        self.assertLess(float(np.abs(poop[:, 1] - bt.POOP_Y).max()), 0.02, "the poop is flat")
        hx, hz, ax, az, _h = bt.MAIN_HATCH
        for slot in (bf.M_DECK, bf.M_TAR):
            t = _hull_tris("terrace_hull", slot)
            inside = (np.abs(t[:, 0] - hx) < ax - 0.05) & (np.abs(t[:, 2] - hz) < az - 0.05) & (np.abs(t[:, 1]) < 0.1)
            self.assertFalse(inside.any(), f"nothing in {slot} closes the hatch over the hold")
        self.assertLess(bt.HOLD_Z[0], hz - az)
        self.assertGreater(bt.HOLD_Z[1], hz + az, "the hold runs past both ends of the hatch")
        floor = tris_of(built("terrace_hold")[0], bf.M_TIMBER).reshape(-1, 3)
        self.assertLess(abs(float(np.median(floor[floor[:, 1] < bt.HOLD_FLOOR_Y + 0.1][:, 1])) - bt.HOLD_FLOOR_Y), 0.05)

    def test_gangways_open_and_shrouds_on_the_chain_plates(self) -> None:
        self.assertTrue(bt.FORM.in_gangway(0.5 * sum(bt.GANGWAY_Z)))
        rig = tris_of(built("terrace_rig")[0], bf.M_ROPE).reshape(-1, 3)
        for lug in btr.LUGS:
            for side in (-1.0, 1.0):
                for p in bf.chain_points(bt.FORM, lug.mast_z, side):
                    d = np.linalg.norm(rig - (p + np.array([0.0, 0.08, 0.0])), axis=1)
                    self.assertLess(float(d.min()), 0.06)

    def test_the_name_board_is_its_own_piece_on_its_brackets(self) -> None:
        board = built("terrace_name_board")[0]
        lo, hi = board.bounds()
        hx, hy = bt.NAME_BOARD_HALF
        self.assertGreaterEqual(float(lo[2]), -0.002, "its back face at its origin")
        self.assertLess(float(hi[0]), hx + 0.01)
        self.assertLess(float(hi[1]), hy + 0.01)
        self.assertEqual(set(board.materials), {bt.M_LACQUER, bf.M_RED, bt.M_COPPER_BRIGHT}, "red on black, copper band")
        hull = built("terrace_hull")[0]
        brackets = tris_of(hull, bt.M_COPPER_BRIGHT).reshape(-1, 3)
        near = brackets[(brackets[:, 2] > bt.FORM.transom_z) & (np.abs(brackets[:, 1] - bt.NAME_BOARD_AT[1]) < hy + 0.06)]
        self.assertGreater(len(near), 20, "the hull carries the board's brackets on the transom")
        self.assertLess(bt.FORM.transom_z, bt.NAME_BOARD_AT[2], "the board hangs outside the transom")
        self.assertEqual(len(bt.name_glyph_cells()), sum(len(w) for w in bt.NAME_WORDS))

    def test_nothing_crosses_the_name_board(self) -> None:
        bx, by, bz = bt.NAME_BOARD_AT
        hx, hy = bt.NAME_BOARD_HALF
        for name in ("terrace_hull", "terrace_rig", "terrace_sails_set", "terrace_moored"):
            p = np.asarray(built(name)[0].pos)
            behind = (p[:, 2] > bz + bt.NAME_BOARD_T + 0.03) & (p[:, 2] < bz + 3.0) & (np.abs(p[:, 0] - bx) < hx) & (np.abs(p[:, 1] - by) < hy)
            self.assertFalse(behind.any(), f"{name} stands in front of the name-board")

    def test_the_galley_sets_four_places(self) -> None:
        self.assertEqual(len(bt.BOWLS), 4)
        clay = tris_of(built("terrace_galley")[0], bf.M_CLAY).reshape(-1, 3)
        th = bt.TABLE[4]
        for x, z in bt.BOWLS:
            d = np.hypot(clay[:, 0] - x, clay[:, 2] - z)
            self.assertTrue(((d < 0.09) & (np.abs(clay[:, 1] - th - 0.04) < 0.05)).any(), f"a bowl at ({x}, {z})")
        rice = tris_of(built("terrace_galley")[0], bt.M_RICE).reshape(-1, 3)
        self.assertGreater(len(rice), 0, "the meal half-eaten")

    def test_the_hold_holds_ingots_and_the_dead_lamp_housing(self) -> None:
        hold = built("terrace_hold")[0]
        self.assertIn(bt.M_COPPER_BRIGHT, hold.materials, "copper ingots")
        ceramic = tris_of(hold, bt.M_CERAMIC).reshape(-1, 3)
        self.assertGreater(len(ceramic), 0, "the lamp-housing")
        self.assertFalse(set(hold.materials) & set(bf.EMISSIVE), "dead: no light in the housing")

    def test_three_sail_states(self) -> None:
        tack_y = max(btr.FORE.tack[1], btr.MAIN.tack[1])
        set_hi = built("terrace_sails_set")[0].bounds()[1]
        self.assertGreater(float(set_hi[1]), btr.MAIN.peak[1] - 0.2, "set: the yards hoisted")
        for name in ("terrace_sails_furled", "terrace_sails_lowered"):
            canvas = tris_of(built(name)[0], btr.M_CANVAS).reshape(-1, 3)
            self.assertLess(float(canvas[:, 1].max()), tack_y + 1.6, f"{name}: the cloth is down on the booms")
        furled = tris_of(built("terrace_sails_furled")[0], btr.M_CANVAS).reshape(-1, 3)
        lowered = tris_of(built("terrace_sails_lowered")[0], btr.M_CANVAS).reshape(-1, 3)
        self.assertGreater(float(np.abs(furled[:, 0]).max()), 0.0)
        self.assertLess(float(np.abs(furled[:, 0]).max()), 0.8, "furled: tidy on the booms amidships")
        self.assertLess(float(lowered[:, 0].min()), -(bt.FORM.half_beam + 0.2), "lowered: a bight over the port rail")
        flat = btr.sail_surface(dataclasses.replace(btr.MAIN, belly=0.0), np.array(0.4), np.array(0.5))
        full = btr.sail_surface(btr.MAIN, np.array(0.4), np.array(0.5))
        self.assertLess(float(full[0] - flat[0]), -0.2, "set: filled to port")

    def test_the_membrane_webs_the_shrouds(self) -> None:
        mem = tris_of(built("terrace_membrane")[0], btr.M_MEMBRANE).reshape(-1, 3)
        self.assertGreater(len(mem), 200)
        lo, hi = mem.min(axis=0), mem.max(axis=0)
        self.assertGreater(float(hi[0]), 1.5)
        self.assertLess(float(lo[0]), -1.5, "on both sides of the main")

    def test_nothing_ties_the_ferry_to_the_derelict(self) -> None:
        """Sea-law: fenders and boathooks only. No rope reaches across the gap."""
        gear = built("alongside_gear")[0]
        rope = tris_of(gear, bf.M_ROPE).reshape(-1, 3)
        ferry_out = -(bf.FERRY.half_beam + bf.FERRY.bulwark_t + 0.5)
        self.assertGreater(float(rope[:, 0].min()), ferry_out, "every line stays on the ferry's side")
        hooks = tris_of(gear, bf.M_TIMBER).reshape(-1, 3)
        her_rail = bt.DERELICT_IN_FERRY[0] + bt.FORM.half_beam
        self.assertLess(float(hooks[:, 0].min()), her_rail + 0.3, "the boathooks reach her cap rail")
        gap = -(bf.FERRY.half_beam + bf.FERRY.bulwark_t) - (bt.DERELICT_IN_FERRY[0] + bt.FORM.half_beam + bt.FORM.bulwark_t)
        self.assertAlmostEqual(gap, bt.GAP_M, places=6, msg="an oar's length off")

    def test_derelict_preview_layouts_and_the_matching_inserts(self) -> None:
        main = json.loads((PREVIEW / "brightwater_derelict_layout.json").read_text())
        names = set()
        for f in ("brightwater_derelict_layout.json", "brightwater_derelict_sails_set_layout.json",
                  "brightwater_derelict_sails_lowered_layout.json", "brightwater_derelict_name_board_layout.json"):
            layout = json.loads((PREVIEW / f).read_text())
            self.assertEqual(layout["kit_dir"], "res://assets/environments/kits/brightwater_ferry/")
            for spec in layout["pieces"]:
                self.assertIn(spec["piece"], TARGETS, spec)
                names.add(spec["piece"])
        self.assertFalse(names & {"terrace_sails_furled", "terrace_moored"}, "Ch4: no Ch1 state")
        self.assertNotIn("ferry_lantern", names, "by day the ferry's lanterns are out (their glass glows)")
        scene = (PREVIEW / "brightwater_derelict_preview.tscn").read_text()
        m = re.search(r'id = &"D06"\nposition = Vector3\(([^)]*)\)', scene)
        eye = np.array([float(v) for v in m.group(1).split(",")])
        board_d = np.array(main["anchors"]["name_board"])
        oruvel = json.loads((ORUVEL_PREVIEW / "oruvel_layout.json").read_text())
        terrace = json.loads((ORUVEL_PREVIEW / "oruvel_seventh_terrace_layout.json").read_text())
        b = next(p for p in terrace["pieces"] if p["piece"] == "terrace_name_board")
        board_o = np.array([b["at"][0], b["y"], b["at"][1]])
        np.testing.assert_allclose(eye - board_d, np.array(oruvel["shots"]["O07"]["eye"]) - board_o, atol=2e-3,
                                   err_msg="D06 frames the board from O07's point")
        self.assertIn('[node name="SailsLowered" type="Node3D" parent="." node_paths=PackedStringArray("tide")]\nvisible = false',
                      scene, "the lowered state is hidden until a shot shows it")


class GradeTests(unittest.TestCase):
    def test_the_crossing_grade_keeps_the_sea_teal(self) -> None:
        lut = _load("bf_zone_lut")
        zl = lut.zl
        teal = np.array([[0.02, 0.24, 0.28]])  # the glowing night sea, display-encoded
        navy = np.array([[0.05, 0.08, 0.16]])  # the night sky
        warm = np.array([[0.8, 0.5, 0.25]])  # a lamp pool
        wake = zl.GRADES["ch04_wake"]

        def sat(c):
            return float((c.max() - c.min()) / max(c.max(), 1e-6))

        self.assertGreater(sat(lut.grade(teal)), sat(zl.grade(teal, wake)) + 0.05, "teal spared the cool cut")
        np.testing.assert_allclose(lut.grade(navy), zl.grade(navy, wake), atol=0.02, err_msg="the sky is ch04_wake's")
        np.testing.assert_allclose(lut.grade(warm), zl.grade(warm, wake), atol=1e-9, err_msg="the pools are ch04_wake's")


class CommittedAssetTests(unittest.TestCase):
    def test_one_glb_per_target_inside_its_budget(self) -> None:
        glbs = sorted(ASSETS.glob("*.glb"))
        self.assertEqual(sorted(p.stem for p in glbs), sorted(TARGETS))
        for p in glbs:
            key, module, _fn = TARGETS[p.stem]
            gltf = read_glb(p)
            for mesh in gltf["meshes"]:
                tris = 0
                for prim in mesh["primitives"]:
                    tris += gltf["accessors"][prim["indices"]]["count"] // 3
                    self.assertIn("COLOR_0", prim["attributes"])
                    self.assertIn("TEXCOORD_1", prim["attributes"])
                lod = 1 if mesh["name"].endswith("-lod1") else 0
                self.assertLessEqual(tris, module.TRI_BUDGET[key][lod], f"{p.name} {mesh['name']}")

    def test_every_file_is_small_and_has_provenance(self) -> None:
        prov = (ROOT / "assets" / "PROVENANCE.md").read_text(encoding="utf-8")
        for p in ASSETS.rglob("*"):
            if p.is_file() and p.suffix != ".import":
                rel = p.relative_to(ROOT).as_posix()
                self.assertLess(p.stat().st_size, MAX_BYTES, rel)
                self.assertIn(f"| {rel} |", prov)

    def test_glb_imports_use_the_kit_post_import(self) -> None:
        for p in sorted(ASSETS.glob("*.glb")):
            imp = p.with_name(p.name + ".import")
            self.assertTrue(imp.is_file(), imp.name)
            self.assertIn('import_script/path="res://game/core/import/brightwater_ferry_kit_post_import.gd"',
                          imp.read_text())

    def test_the_lut_imports_as_a_3d_texture(self) -> None:
        imp = (ASSETS / "lut_ch04_crossing.png.import").read_text()
        self.assertIn('importer="3d_texture"', imp)
        self.assertIn("slices/horizontal=32", imp)

    def test_every_slot_has_a_material(self) -> None:
        for p in sorted(ASSETS.glob("*.glb")):
            for m in read_glb(p).get("materials", []):
                self.assertTrue((ASSETS / "materials" / f"{m['name']}.tres").is_file(), f"{p.name}: {m['name']}")

    def test_manifest_matches_targets(self) -> None:
        manifest = json.loads((ASSETS / "kit_manifest.json").read_text())
        self.assertEqual(manifest["kit"], "brightwater_ferry")
        self.assertEqual(sorted(manifest["pieces"]), sorted(TARGETS))

    def test_blender_job_is_pinned_and_covers_the_kit(self) -> None:
        jobs = json.loads((ROOT / "tools" / "dev" / "blender_builds.json").read_text())["jobs"]
        job = next(j for j in jobs if j["id"] == "brightwater_ferry_kit")
        self.assertEqual(job["threads"], 4)
        self.assertIn("assets/environments/kits/brightwater_ferry/*.glb", job["outputs"])
        self.assertIn("assets/environments/kits/brightwater_ferry/lut_ch04_crossing.png", job["outputs"])
        self.assertIn("assets_src/environments/kits/brightwater_ferry/*.py", job["sources"])

    def test_preview_layout_names_only_kit_pieces_and_lights_every_lantern(self) -> None:
        layout = json.loads(LAYOUT.read_text())
        self.assertEqual(layout["kit_dir"], "res://assets/environments/kits/brightwater_ferry/")
        for spec in layout["pieces"]:
            self.assertIn(spec["piece"], TARGETS, spec)
            self.assertIn("y", spec, "no terrain in the preview: every piece carries its height")
        lanterns = [s for s in layout["pieces"] if s["piece"] == "ferry_lantern"]
        self.assertEqual(len(lanterns), len(layout["lamps"]))
        fy = bf_props.LANTERN_FLAME[1]
        for spec, lamp in zip(lanterns, layout["lamps"]):
            self.assertAlmostEqual(spec["at"][0], lamp[0], places=2)
            self.assertAlmostEqual(spec["at"][1], lamp[2], places=2)
            self.assertAlmostEqual(spec["y"] + fy, lamp[1], places=2)
        self.assertEqual(layout["lamp_color"], "#FFB16E", "oil_lamp")
        ship = [s for s in layout["pieces"] if s["piece"].startswith("ferry_") and s["piece"] != "ferry_lantern"]
        self.assertTrue(all(s["at"] == [0.0, 0.0] and s["yaw_deg"] == 0.0 for s in ship), "one ship origin")


if __name__ == "__main__":
    unittest.main()
