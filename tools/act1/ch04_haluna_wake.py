#!/usr/bin/env python3
"""Ch4's wake night (ch04/haluna_wake) on the real Haluna (ADR 0041; M3-C04-1226).

The zone was a greybox stand-in for Haluna's night variant (ADR 0035: HalunaStory is not data-driven). It now
instances Haluna's own dressing (`game/levels/ch02/haluna/haluna_dressing.tscn`: terrain, kit, sea, sky, the night
mood) through GreyboxZone's layout "dressing" row, takes Haluna's runtime walk collision (Ch04Zone, configured from
ch02/haluna's own Collision node), and shows env-art's wake-night story sets (M3-ENV-709: the lamps to the wall, the
feast on the sand, the ink kit, the shells) by flag. The greybox blocks are gone; every story point stands where its
place is in Haluna: Neme's house on the tidewall lane, the child in the lane, the shut inn, Reed at the chapel court,
the dock, the feast at the causeway head and the wake-shell wall, the causeway's first slabs at dawn.

Points are (x, z, yaw_deg) with yaw 0 facing -Z (the layouts' convention); their y is Haluna's floor there, read by
`tools/act1/ch04_haluna_wake_floors.gd` into ch04_haluna_wake_floors.json (re-run it after Haluna's terrain changes):

    godot --headless --path . res://tools/act1/ch04_haluna_wake_floors.tscn
    python3 tools/act1/ch04_haluna_wake.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZONE = ROOT / "game" / "levels" / "ch04" / "haluna_wake"
LAYOUT = ZONE / "haluna_wake_layout.json"
FLOORS = Path(__file__).resolve().parent / "ch04_haluna_wake_floors.json"
HALUNA = "res://game/levels/ch02/haluna/"

# Haluna's places (ch02/haluna's map and layout): Neme's house (house_tile_c at -58, 4.5, its front on the lane), the
# tidewall lane's child, the inn's door, the chapel court, the dock (dock_haluna at -6, 60, 35 deg), the wake-shell wall
# at the causeway head (-14.61, -122.14, -31.1 deg; the shells on its south face) and the causeway's slabs.
DOCK_AT, DOCK_YAW = (-6.0, 60.0), 35.0
WALL_FACE_YAW = 16.0  # facing the wall's shells from the village side
GAP = (-13.9, -119.6)  # where a shell is set, in front of Imra's


def at_wall(back_m: float, along_m: float) -> tuple[float, float, float]:
    """A place facing the wall's gap, back_m behind it (village side) and along_m along the wall."""
    a = math.radians(WALL_FACE_YAW)
    dx, dz = -math.sin(a), -math.cos(a)  # the facing
    tx, tz = -dz, dx  # along the wall
    return (round(GAP[0] - dx * back_m + tx * along_m, 2), round(GAP[1] - dz * back_m + tz * along_m, 2),
            WALL_FACE_YAW)
CAUSEWAY_YAW = 300.0  # walking out along the causeway (north-east)


def dock(s: float) -> tuple[float, float]:
    """The point s m out along the dock's walk (its local +x)."""
    a = math.radians(DOCK_YAW)
    return round(DOCK_AT[0] + s * math.cos(a), 2), round(DOCK_AT[1] - s * math.sin(a), 2)


DOCK_OUT_YAW = 305.0  # facing out to sea along the dock
DOCK_IN_YAW = 125.0  # facing the shore

SPAWNS = {
    "NemeDoor": (-58.0, -3.6, 0.0),  # off house_tile_c's porch (its front at z -2.25)
    "FeastEdge": (-4.0, -100.0, 0.0),
    "DockEnd": dock(36.0) + (DOCK_OUT_YAW,),
    "DockShore": dock(4.0) + (DOCK_IN_YAW,),
    "WallDawn": (-12.5, -118.0, WALL_FACE_YAW),
    "InkLamp": (-12.2, -118.6, 45.0),  # C4-07: Rhen beside H15, just behind its lens, turned to Ysolde at the gap
    "Shrine": (-67.0, 44.3, 180.0),  # the dressing's SaveShrine (haluna_shrine) respawns here, as on ch02/haluna
}
MARKS = {
    "table_lane": (-0.5, -102.5, 0.0),
    "lane_toma": (-52.5, -4.5, 270.0),  # C4-01: Toma out along the lane with the table's heavy end (the flow then seats him)
    "neme_table": (4.0, -111.5, 315.0),
    "wall_gap": GAP + (WALL_FACE_YAW,),
    # C4-04: the village gathered at the wall when it calls (the flow stands them here before the shell is set)
    "wall_osu": at_wall(1.4, 0.0),
    "wall_neme": at_wall(3.0, -1.6),
    "wall_toma": at_wall(3.0, 0.8),
    "wall_vendor": at_wall(3.6, -3.2),
    "wall_fisher": at_wall(3.8, 4.8),
    "feast_edge": (10.5, -108.0, 90.0),
    "dock_end": dock(35.5) + (DOCK_OUT_YAW,),
    "dock_shore": dock(3.0) + (DOCK_IN_YAW,),
    # C4-06: Asha and Toma come down to the dock after the shell (the flow stands them here before the scene)
    "dock_asha_from": dock(27.5) + (DOCK_OUT_YAW,),  # C4-06: 8 m short of the end, so she reaches Rhen in H13
    "dock_toma_from": dock(-2.5) + (DOCK_OUT_YAW,),
    "wall_away": (-8.5, -123.0, 90.0),
    "dawn_neme": (-15.4, -117.6, -37.0),  # C4-08: beside Asha at her shell, out of H08's line, watching her
    # C4-05: Rhen, then Asha and Toma, walk a few metres from the wall toward the feast before the fade (the dock
    # scene places them after; a walk to the feast's edge ran on 45 s in black).
    "leave_rhen": (-7.07, -116.25, -115.0),
    "leave_asha": (-6.92, -114.56, -111.0),
    "leave_toma": (-9.51, -115.81, -111.0),
    "causeway_toma": (12.55, -130.0, CAUSEWAY_YAW),
    "causeway_asha": (10.4, -128.5, CAUSEWAY_YAW),
    "causeway_rhen": (8.6, -127.2, CAUSEWAY_YAW),
    "way_feast_s": (8.0, -110.0, 90.0),
    "way_lane_n": (-6.0, -95.0, 0.0),
    "way_wall_east": (-9.5, -121.5, 270.0),
    "way_rail_gap": (4.0, -120.0, 0.0),
    "way_flats": (7.0, -126.0, CAUSEWAY_YAW),
}
ACTORS = {  # id: ((x, z, yaw), extra); the feast's villagers face the wall's gap, where Osu walks to set the shell
    "asha": ((-10.2, -115.8, 196.0), {"color": "#d9c3a0"}),
    "toma": ((-56.4, -3.4, 0.0), {"color": "#6f7f8f", "radius": 0.36, "height": 1.9}),
    "neme": ((-59.6, -3.3, 0.0), {"cast": "neme", "color": "#8f6f5f"}),
    "osu": ((6.0, -103.3, 51.0), {"cast": "osu", "color": "#9a8a7a"}),
    "vendor": ((3.4, -104.6, 47.0), {"cast": "vendor", "color": "#7a8a5a"}),
    "fisher": ((8.3, -107.6, 62.0), {"cast": "fisher", "color": "#5a7a8a"}),
    "child": ((-70.0, -9.5, 90.0), {"cast": "child", "color": "#d4b07a", "radius": 0.2, "height": 1.1}),
    "netmender": ((-5.2, 56.4, 0.0), {"cast": "netmender", "color": "#8a9a7a"}),  # on the sand by the dock's foot
    "reed": ((-116.3, 33.6, 270.0), {"cast": "reed", "color": "#b8b2a8"}),
    "ysolde_edge": ((10.5, -108.0, 90.0), {"color": "#2a2440", "radius": 0.26, "height": 1.85}),
    "ysolde": ((-13.6, -119.2, 196.0), {"color": "#2a2440", "radius": 0.26, "height": 1.0, "hidden": True}),
}
TRIGGERS = [  # (id, (x, z), size, yaw, rest)
    ("npc_child", ACTORS["child"][0][:2], [2, 0, 2], 0.0,
     {"activation": "interact", "prompt_key": "FIELD_PROMPT_LISTEN", "requires_flag": "ch04_started",
      "blocked_by_flag": "ch04_shell_set", "payload": {"dialogue": "ch04_bark_lane_rhyme"}}),
    ("npc_netmender", ACTORS["netmender"][0][:2], [2, 0, 2], 0.0,
     {"activation": "interact", "prompt_key": "FIELD_PROMPT_LISTEN", "requires_flag": "ch04_started",
      "blocked_by_flag": "ch04_shell_set", "payload": {"dialogue": "ch04_bark_dock_netmender"}}),
    ("npc_reed", ACTORS["reed"][0][:2], [2, 0, 2], 0.0,
     {"activation": "interact", "prompt_key": "FIELD_PROMPT_LISTEN", "requires_flag": "ch04_started",
      "blocked_by_flag": "ch04_shell_set", "payload": {"dialogue": "ch04_bark_chapel_reed"}}),
    ("inn_door", (-30.0, 57.5), [1.5, 0, 2], 0.0,
     {"activation": "interact", "prompt_key": "FIELD_PROMPT_LOOK", "payload": {"dialogue": "ch04_bark_inn_closed"}}),
    ("feast", (-2.5, -101.5), [24, 0, 1.5], 0.0,
     {"requires_flag": "ch04_started", "blocked_by_flag": "ch04_shell_set", "once": True,
      "payload": {"beat": "the_wake"}}),
    ("table_vendor", (2.5, -106.5), [2.4, 0, 2.4], 0.0,
     {"activation": "interact", "prompt_key": "FIELD_PROMPT_LISTEN", "blocked_by_flag": "ch04_shell_set",
      "payload": {"dialogue": "ch04_wake_vendor"}}),
    ("table_osu", (6.0, -104.5), [2.4, 0, 2.4], 0.0,
     {"activation": "interact", "prompt_key": "FIELD_PROMPT_LISTEN", "blocked_by_flag": "ch04_shell_set",
      "payload": {"dialogue": "ch04_wake_osu"}}),
    ("table_fisher", (7.3, -108.5), [2.4, 0, 2.4], 0.0,
     {"activation": "interact", "prompt_key": "FIELD_PROMPT_LISTEN", "blocked_by_flag": "ch04_shell_set",
      "payload": {"dialogue": "ch04_wake_fisher"}}),
    ("table_neme", (5.0, -112.5), [2.4, 0, 2.4], 0.0,
     {"activation": "interact", "prompt_key": "FIELD_PROMPT_LISTEN", "blocked_by_flag": "ch04_shell_set",
      "payload": {"beat": "neme_table"}}),
    ("wall", (-12.5, -118.8), [9, 0, 2.5], -31.1,
     {"requires_flag": "ch04_feast_neme", "blocked_by_flag": "ch04_shell_set", "payload": {"beat": "shell_set"}}),
    ("the_ink", (-13.4, -119.4), [2, 0, 1.5], -31.1,
     {"activation": "interact", "prompt_key": "FIELD_PROMPT_LOOK", "requires_flag": "ch04_dock_comforted",
      "blocked_by_flag": "ch04_saw_ysolde_ink", "payload": {"beat": "the_ink"}}),
    ("neme_door", (-58.0, -2.8), [2, 0, 1.2], 0.0,
     {"activation": "interact", "prompt_key": "FIELD_PROMPT_SLEEP", "requires_flag": "ch04_dock_comforted",
      "payload": {"beat": "dawn"}}),
]
SHOTS = {  # id: (pos, look_at, fov[, "abs"]); heights over Haluna's ground (props ignored), or absolute (the dock)
    "H02": ((-47.0, 1.9, -1.5), (-64.0, 1.4, -7.5), 46),  # down the tidewall lane, west
    "H04": ((-34.0, 3.0, 6.0), (-41.0, 1.0, 0.0), 46),
    "H07": ((-108.0, 2.2, 36.0), (-117.0, 1.6, 32.0), 40),
    "H09": ((-3.5, 2.6, 60.5), (14.0, 0.8, 47.0), 46),
    "H08": ((-13.2, 1.5, -117.2), (-14.4, 1.3, -120.6), 28),  # 2.5 m back from the gap: the hands and the shells
    "H12": ((16.0, 3.0, -98.0), (-6.0, 1.0, -114.0), 62),  # from east of the feast: the mats, the lamps, the wall
    "H13": ((26.9, 0.9, 44.2), (23.1, 2.1, 39.6), 54, "abs"),  # low, off the dock end's side, over the sea
    "H14": ((19.4, 3.0, 42.2), (23.1, 2.9, 39.6), 16, "abs"),  # down the dock's middle at eye height
    "H15": ((-12.6, 1.0, -118.8), (-13.9, 1.2, -120.2), 18),
    "H16": ((-15.05, 1.55, -117.82), (-14.61, 1.55, -116.28), 22),  # Neme at the wall, close, from the wall's side
    "H17": ((-9.7, 1.55, -114.1), (-10.2, 1.55, -115.8), 24),  # Asha at the wall, close (C4-04's smile)
    "C01": ((-12.0, 5.5, -113.0), (8.0, 0.5, -127.0), 45, "abs"),  # behind the three: the path leading away
    "C02": ((6.0, 6.5, -112.0), (14.0, 0.5, -136.0), 50, "abs"),  # nearer: the causeway's first slabs, the islet
}
# Field camera volumes over Haluna's own (Ch04Zone copies ch02/haluna's CameraVolumes): where those leave only the
# hub orbit and the orbit's default side is a roof. Absolute coordinates.
CAMERA_VOLUMES = [
    # Neme's door, deep in the tidewall lane's roofs: from the lane's north-west end, over the gate.
    {"id": "NemeDoor", "mode": "pan_follow", "at": [-58.0, 3.0, -3.6], "size": [10.0, 6.0, 10.0],
     "pos": [-64.0, 5.5, -11.0], "look_at": [-58.0, 2.4, -3.6], "fov": 46.4, "priority": 1},
]
STATES = [
    {"flag": "ch03_rhen_sworn_guardian", "show_sets": ["ch04_wake", "ch04_shell_imra_faded"]},
    {"flag": "ch04_shell_set", "show_sets": ["ch04_shell_asha"], "hide": ["ysolde_edge"]},
    {"flag": "ch04_dock_comforted", "hide": ["vendor", "fisher", "osu", "child", "netmender", "reed"],
     "show": ["ysolde"]},
    {"flag": "ch04_saw_ysolde_ink", "hide": ["ysolde"], "hide_sets": ["ch04_shell_imra_faded"],
     "show_sets": ["ch04_shell_imra_inked"]},
]


def points() -> dict[str, tuple[float, float]]:
    """Every point whose floor the probe reads (name -> x, z)."""
    out = {f"spawn:{k}": v[:2] for k, v in SPAWNS.items()}
    out.update({f"mark:{k}": v[:2] for k, v in MARKS.items()})
    out.update({f"actor:{k}": v[0][:2] for k, v in ACTORS.items()})
    out.update({f"trigger:{t[0]}": t[1] for t in TRIGGERS})
    for k, (pos, look, *_rest) in SHOTS.items():
        out[f"shot:{k}"] = (pos[0], pos[2])
        out[f"look:{k}"] = (look[0], look[2])
    return out


def floor(floors: dict, key: str) -> float:
    return round(float(floors.get(key, 0.0)), 3)


def layout() -> dict:
    floors = json.loads(FLOORS.read_text(encoding="utf-8")) if FLOORS.exists() else {}

    def p4(key: str, v: tuple) -> list:
        return [v[0], floor(floors, key), v[1], v[2]]

    actors = {}
    for k, (v, extra) in ACTORS.items():
        actors[k] = dict(extra, at=p4(f"actor:{k}", v))
        if "cast" in extra:  # the cast first, as the other Act I layouts write it
            actors[k] = dict({"cast": extra["cast"]}, **actors[k])
    triggers = []
    for tid, (x, z), size, yaw, rest in TRIGGERS:
        row = {"id": tid}
        row.update({k: v for k, v in rest.items() if k == "activation"})
        row.update({"at": [x, floor(floors, f"trigger:{tid}"), z], "size": size})
        row.update({k: v for k, v in rest.items() if k != "activation"})
        row["yaw"] = yaw
        triggers.append(row)
    shots = {}
    for k, (pos, look, fov, *mode) in SHOTS.items():
        base, at = (0.0, 0.0) if mode == ["abs"] else (floor(floors, f"shot:{k}"), floor(floors, f"look:{k}"))
        shots[k] = {"pos": [pos[0], round(base + pos[1], 3), pos[2]],
                    "look_at": [look[0], round(at + look[1], 3), look[2]], "fov": fov}
    return {
        "doc": "M3-C04-1226 (tools/act1/ch04_haluna_wake.py; do not edit by hand): ch04/haluna_wake, Haluna on the "
        "Pilgrim's Wake night (act1_ch04.md C4-01 to C4-08), on the real Haluna (ADR 0041): Haluna's dressing at its "
        "night mood, its walk collision, and env-art's wake-night story sets (M3-ENV-709) shown by flag. Neme's house "
        "on the tidewall lane, the lane's child, the shut inn, Reed at the chapel court, the dark dock, the feast on the "
        "sand at the causeway head and the wake-shell wall with Imra's shell, the causeway's first slabs at dawn. "
        "states (Ch04Zone): the lamps, feast and Imra's faded shell from the start; Asha's shell from ch04_shell_set; "
        "the village gone home and the stranger at the wall from ch04_dock_comforted; gone again, Imra's shell "
        "re-inked, from ch04_saw_ysolde_ink.",
        "dressing": {"scene": HALUNA + "haluna_dressing.tscn", "adopt": HALUNA + "haluna_zone_dresser.gd"},
        "dressing_mood": "night",
        "blocks": [],
        "spawns": {k: p4(f"spawn:{k}", v) for k, v in SPAWNS.items()},
        "marks": {k: p4(f"mark:{k}", v) for k, v in MARKS.items()},
        "actors": actors,
        "shots": shots,
        "triggers": triggers,
        "camera_volumes": CAMERA_VOLUMES,
        "states": STATES,
    }


def main() -> None:
    LAYOUT.write_text(json.dumps(layout(), indent=1) + "\n", encoding="utf-8")
    (Path(__file__).resolve().parent / "ch04_haluna_wake_points.json").write_text(
        json.dumps({k: list(v) for k, v in points().items()}, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
