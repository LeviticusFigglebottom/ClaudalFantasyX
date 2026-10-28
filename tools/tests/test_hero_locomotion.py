"""Tests for the heroes' field locomotion (M2-CHR-12, assets_src/characters/asha/hero_clips.py, the "M2-CHR-12" block).

Run: python3 -m unittest tools.tests.test_hero_locomotion   (or discover -s tools/tests)

The clips are in place: the field controller moves the root, and the planted feet travel under the body at exactly
that speed. game/data/characters/locomotion.json carries what the controller needs (stride and speed per cycle, the
root's travel or turn per key for starts, stops and turns, the heel-contact markers), and these tests hold the clips
to it: the planted feet must stay put on the ground once the root's motion is added back.
"""
import json
import math
import re
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "asha"))

import hero_clips  # noqa: E402

HEROES = ("asha", "rhen", "toma")
CYCLES = ("walk", "run")
IDLES = ("idle_breathe", "idle_shift")
STARTS = ("walk_start", "run_start")
STOPS = ("walk_stop", "run_stop")
TURNS = ("turn_in_place_l90", "turn_in_place_r90", "turn_in_place_180")
REQUIRED = CYCLES + IDLES + STARTS + STOPS + TURNS
LOOPING = set(CYCLES) | set(IDLES)
FLAT_MM = 0.3  # a ball of the foot within this of the floor is a planted foot
SLIDE_MM = 3.0  # a planted foot may drift this much on the ground (15 fps keys, solved by IK)
SPEED_TOL = 0.02  # the JSON speed vs the planted feet's measured speed (fraction)
HIPS_LIMIT_M = 0.1  # the hips shift over the feet by centimetres; the root itself never moves


def _subresources(text: str) -> dict:
    out = {}
    for block in text.split("\n\n"):
        m = re.search(r'resource_name = &"([a-z_0-9]+)"', block)
        if block.startswith('[sub_resource type="Animation"') and m:
            out[m.group(1)] = block
    return out


def _tracks(sub: str) -> dict:
    """(kind, path) -> list of key value tuples (strings, as written)."""
    out = {}
    for ti, kind in re.findall(r'tracks/(\d+)/type = "(\w+)"', sub):
        path = re.search(rf'tracks/{ti}/path = NodePath\("([^"]+)"\)', sub).group(1)
        vals = re.search(rf"tracks/{ti}/keys = PackedFloat32Array\(([^)]*)\)", sub).group(1).split(", ")
        width = {"position_3d": 5, "rotation_3d": 6, "scale_3d": 5, "blend_shape": 3}[kind]
        out[(kind, path)] = [tuple(vals[i + 2:i + width]) for i in range(0, len(vals), width)]
    return out


def _markers(sub: str) -> dict:
    return {n: float(t) for n, t in re.findall(r'"name": &"([a-z_0-9]+)", "time": ([0-9.e-]+)\}', sub)}


class TestHeroLocomotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sk = {h: hero_clips.Skeleton(ROOT / "assets" / "characters" / h / f"{h}.glb") for h in HEROES}
        cls.subs = {h: _subresources(hero_clips.out_path(h).read_text(encoding="utf-8")) for h in HEROES}
        cls.data = json.loads(hero_clips.LOCO_DATA.read_text(encoding="utf-8"))
        cls.fk = {}

    def _ankles(self, hero: str, clip: str) -> list:
        """Per key: (t, {side: where the ball of the foot meets the floor, relative to the root}) from the clip's own
        poses (hero_clips.ball_contact: the point a planted foot pivots on as its heel lifts)."""
        key = (hero, clip)
        if key not in self.fk:
            length = hero_clips.clip_length(hero, clip)
            persona = hero_clips.PERSONA[hero]
            rows = []
            for i in range(int(round(length * hero_clips.FPS)) + 1):
                t = i / hero_clips.FPS
                tt = (t % length) if clip in hero_clips.LOOPS else t
                pose = hero_clips.pose_at(clip, tt, length, self.sk[hero], persona)
                rows.append((t, {s: hero_clips.ball_contact(self.sk[hero], hero, pose, s) for s in "LR"}))
            self.fk[key] = rows
        return self.fk[key]

    def _idle_ankle_y(self, hero: str) -> dict:
        persona = hero_clips.PERSONA[hero]
        pose = hero_clips.pose_at("idle", 0.0, hero_clips.LENGTHS["idle"], self.sk[hero], persona)
        _g, pos = hero_clips._loco_fk(self.sk[hero], pose)
        return {s: float(pos[f"DEF-foot.{s}"][1]) for s in "LR"}

    def _ground(self, hero: str, clip: str, i: int, side: str) -> np.ndarray:
        """A key's ankle in ground coordinates: the root's travel or turn (locomotion.json) added back."""
        row = self.data["heroes"][hero][clip]
        t, ank = self._ankles(hero, clip)[i]
        p = np.array(ank[side], dtype=float)
        if "root_yaw_deg" in row:
            p = hero_clips.qrot(hero_clips.qaxis((0.0, 1.0, 0.0), row["root_yaw_deg"][i]), p)
        elif "root_travel_m" in row:
            p = p + np.array([0.0, 0.0, row["root_travel_m"][i]])
        elif "speed_mps" in row:
            p = p + np.array([0.0, 0.0, row["speed_mps"] * t])
        return p

    def _flat_runs(self, hero: str, clip: str, side: str) -> list:
        rows = self._ankles(hero, clip)
        runs, run = [], []
        for i, (_t, ank) in enumerate(rows + [(None, None)]):
            if ank is not None and abs(float(ank[side][1])) * 1000.0 < FLAT_MM:
                run.append(i)
                continue
            if len(run) >= 2:
                runs.append(run)
            run = []
        return runs

    def test_every_clip_for_every_hero(self):
        for hero in HEROES:
            self.assertTrue(set(REQUIRED) <= set(hero_clips.CLIPS[hero]), hero)
            self.assertTrue(set(REQUIRED) <= set(self.subs[hero]), f"{hero}: in the committed library")
            self.assertTrue(set(REQUIRED) <= set(self.data["heroes"][hero]), f"{hero}: in locomotion.json")
            for clip in REQUIRED:
                sub = self.subs[hero][clip]
                loop = int(re.search(r"loop_mode = (\d)", sub).group(1))
                self.assertEqual(loop, 1 if clip in LOOPING else 0, f"{hero} {clip}")
                row = self.data["heroes"][hero][clip]
                self.assertEqual(row["loop"], clip in LOOPING, f"{hero} {clip}")
                self.assertAlmostEqual(row["length_s"], float(re.search(r"length = ([0-9.]+)", sub).group(1)),
                                       places=4, msg=f"{hero} {clip}")

    def test_locomotion_json_regenerates(self):
        self.assertEqual(hero_clips.LOCO_DATA.read_text(encoding="utf-8"),
                         json.dumps(hero_clips.locomotion_data(), indent=1) + "\n")

    def test_loops_close(self):
        for hero in HEROES:
            for clip in LOOPING:
                for track, keys in _tracks(self.subs[hero][clip]).items():
                    self.assertEqual(keys[0], keys[-1], f"{hero} {clip} {track}")

    def test_no_root_translation(self):
        """Only the hips carry a position track (and Rhen's sheathed hooks, which hold still), and only by
        centimetres; cycles never move them forward."""
        for hero in HEROES:
            sk = self.sk[hero]
            rest = sk.rest_t[hero_clips.HIPS]
            for clip in REQUIRED:
                tracks = _tracks(self.subs[hero][clip])
                hooks = {("position_3d", f"{sk.root_name}/Skeleton3D:{hero_clips.HOOK_BONE}{s}") for s in sk.hooks}
                for k in hooks:  # M2-CHR-513: Rhen's reef-hooks stay sheathed (one place) in the field
                    self.assertEqual(len(set(tracks[k])), 1, f"{hero} {clip} {k[1]}")
                if sk.prop:  # M2-CHR-515: the staff or spear slides through the fist to stay on the floor
                    hooks.add(("position_3d", f"{sk.root_name}/Skeleton3D:{sk.prop['bone']}"))
                pos = [k for k in tracks if k[0] == "position_3d" and k not in hooks]
                self.assertEqual(pos, [("position_3d", f"{sk.root_name}/Skeleton3D:{hero_clips.HIPS}")],
                                 f"{hero} {clip}")
                for path in (p for _k, p in tracks):
                    self.assertTrue(path.startswith(f"{sk.root_name}/Skeleton3D:DEF-"), f"{hero} {clip} {path}")
                for v in tracks[pos[0]]:
                    off = np.array([float(x) for x in v]) - rest
                    self.assertLess(abs(off[0]), HIPS_LIMIT_M, f"{hero} {clip}")
                    self.assertLess(abs(off[2]), HIPS_LIMIT_M, f"{hero} {clip}")
                    if clip in CYCLES:
                        self.assertAlmostEqual(off[2], 0.0, places=5, msg=f"{hero} {clip}")

    def test_stride_matches_the_planted_feet(self):
        """Cycles: the planted ball of the foot travels backward at speed_mps (stride_m per loop); starts, stops and turns:
        with the root's travel or turn added back, every planted foot holds still on the ground."""
        for hero in HEROES:
            for clip in CYCLES:
                row = self.data["heroes"][hero][clip]
                self.assertGreater(row["speed_mps"], 0.5, f"{hero} {clip}")
                self.assertAlmostEqual(row["stride_m"], row["speed_mps"] * row["length_s"], delta=0.002)
                slopes = []
                for side in "LR":
                    for run in self._flat_runs(hero, clip, side):
                        rows = self._ankles(hero, clip)
                        ts = np.array([rows[i][0] for i in run])
                        zs = np.array([float(rows[i][1][side][2]) for i in run])
                        slopes.append(-float(np.polyfit(ts, zs, 1)[0]) if len(run) > 2 else
                                      -(zs[-1] - zs[0]) / (ts[-1] - ts[0]))
                self.assertGreaterEqual(len(slopes), 2, f"{hero} {clip}: both feet plant")
                for s in slopes:
                    self.assertAlmostEqual(s / row["speed_mps"], 1.0, delta=SPEED_TOL, msg=f"{hero} {clip}")
            for clip in CYCLES + STARTS + STOPS + TURNS:
                planted = 0
                for side in "LR":
                    for run in self._flat_runs(hero, clip, side):
                        pts = np.array([self._ground(hero, clip, i, side) for i in run])
                        drift = float(np.max(np.linalg.norm(pts - pts[0], axis=1))) * 1000.0
                        self.assertLess(drift, SLIDE_MM, f"{hero} {clip} {side} keys {run[0]}..{run[-1]}")
                        planted += 1
                self.assertGreaterEqual(planted, 2, f"{hero} {clip}")

    def test_transitions_end_on_the_clips_they_join(self):
        for hero in HEROES:
            first = {c: {k: v[0] for k, v in _tracks(self.subs[hero][c]).items()} for c in ("idle",) + CYCLES}
            for clip in REQUIRED:
                tracks = _tracks(self.subs[hero][clip])
                head = {k: v[0] for k, v in tracks.items()}
                tail = {k: v[-1] for k, v in tracks.items()}
                cyc = clip.split("_")[0]
                if clip in STARTS:
                    self.assertEqual(head, first["idle"], f"{hero} {clip} starts on the idle's first frame")
                    self.assertEqual(tail, first[cyc], f"{hero} {clip} ends on the {cyc}'s first frame")
                elif clip in STOPS:
                    self.assertEqual(head, first[cyc], f"{hero} {clip} starts on the {cyc}'s first frame")
                    self.assertEqual(tail, first["idle"], f"{hero} {clip} ends on the idle's first frame")
                elif clip in TURNS:
                    self.assertEqual(head, first["idle"], f"{hero} {clip}")
                    self.assertEqual(tail, first["idle"], f"{hero} {clip}")
                elif clip in IDLES:
                    self.assertEqual(head, first["idle"], f"{hero} {clip}")
            for clip in TURNS:
                row = self.data["heroes"][hero][clip]
                want = {"turn_in_place_l90": 90.0, "turn_in_place_r90": -90.0, "turn_in_place_180": 180.0}[clip]
                self.assertAlmostEqual(row["turn_deg"], want, places=3)
                self.assertEqual(row["root_yaw_deg"][0], 0.0)
                self.assertAlmostEqual(row["root_yaw_deg"][-1], want, places=3)
            for clip in STARTS + STOPS:
                row = self.data["heroes"][hero][clip]
                travel = row["root_travel_m"]
                self.assertEqual(travel[0], 0.0)
                self.assertAlmostEqual(travel[-1], row["distance_m"], places=4)
                self.assertTrue(all(b >= a for a, b in zip(travel, travel[1:])), f"{hero} {clip}: never backward")

    def test_markers(self):
        """Every stepping clip marks its heel contacts; the cycles at 0 (left) and half the length (right); the foot
        is on the floor at its marker."""
        for hero in HEROES:
            y0 = self._idle_ankle_y(hero)
            for clip in CYCLES + STARTS + STOPS + TURNS:
                marks = _markers(self.subs[hero][clip])
                self.assertTrue(marks, f"{hero} {clip}: has footstep markers")
                self.assertTrue(all(re.fullmatch(r"foot_[lr]_down(_\d)?", n) for n in marks), f"{hero} {clip}")
                self.assertEqual(set(marks), set(self.data["heroes"][hero][clip]["markers"]), f"{hero} {clip}")
                for name, t in marks.items():
                    self.assertAlmostEqual(t, self.data["heroes"][hero][clip]["markers"][name], places=4)
                    side = name[5].upper()
                    persona = hero_clips.PERSONA[hero]
                    length = hero_clips.clip_length(hero, clip)
                    _g, pos = hero_clips._loco_fk(self.sk[hero], hero_clips.pose_at(clip, t, length, self.sk[hero],
                                                                                     persona))
                    self.assertLess(float(pos[f"DEF-foot.{side}"][1]) - y0[side], 0.03, f"{hero} {clip} {name}")
            for clip in CYCLES:
                marks = _markers(self.subs[hero][clip])
                self.assertEqual(marks["foot_l_down"], 0.0)
                self.assertAlmostEqual(marks["foot_r_down"], 0.5 * hero_clips.clip_length(hero, clip), places=4)
            for clip in IDLES:
                self.assertEqual(_markers(self.subs[hero][clip]), {}, f"{hero} {clip}")

    def test_idioms(self):
        """Rhen leans further into his walk than Asha; Toma's feet track wider than either; the staff and the spear
        stay within 20 degrees of upright through the cycles."""
        lean = {h: hero_clips.LOCO_GAIT[h]["walk"]["lean"] + hero_clips.PERSONA[h]["lean"] for h in HEROES}
        self.assertGreater(lean["rhen"], lean["asha"])
        width = {}
        for hero in HEROES:
            rows = self._ankles(hero, "walk")
            width[hero] = float(np.mean([abs(r[1]["L"][0] - r[1]["R"][0]) for r in rows]))
        self.assertGreater(width["toma"], max(width["asha"], width["rhen"]))
        up = np.array([0.0, 1.0, 0.0])
        for hero in ("asha", "toma"):
            persona = hero_clips.PERSONA[hero]
            sk = self.sk[hero]
            g0, _t = hero_clips._loco_fk(sk, hero_clips.staff_hold({}, persona))
            rest = hero_clips.qrot(g0["DEF-hand.R"], up)
            for clip in CYCLES + STARTS + STOPS + TURNS:
                length = hero_clips.clip_length(hero, clip)
                for i in range(int(round(length * hero_clips.FPS)) + 1):
                    pose = hero_clips.staff_hold(hero_clips.pose_at(clip, i / hero_clips.FPS, length, sk, persona),
                                                 persona)
                    g, _t = hero_clips._loco_fk(sk, pose)
                    cos = float(np.dot(hero_clips.qrot(g["DEF-hand.R"], up), rest))
                    self.assertGreater(cos, math.cos(math.radians(20.0)), f"{hero} {clip} key {i}")


if __name__ == "__main__":
    unittest.main()
