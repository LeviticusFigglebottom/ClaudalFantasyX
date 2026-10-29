#!/usr/bin/env python3
"""Act I scene-change sweep (ADR 0042 §4, ADR 0111).

Runs the scene-swap probe (game/core/debug/scene_swap_probe.tscn) once per Act I target, in its own headless
Godot, with ResidentLoads on as the game has it (--resident-loads) and the resident hero bodies already loaded
(--warm-resident: the title loads them while it shows), on the real clock. Prints one row per target:
whether the swap and its hidden frames were under the opaque fade (`covered`), the worst hidden frame, the
entry time and the worst visible frame (the fade lifting and the 60 frames after it). Exit 1 when any target
was not covered or printed no stats; frame times over budget are reported but do not fail the run, because a
headless box is not the PC (its numbers are the PC-QUEUE measurement).

Targets: every zone in game/data/ui/scene_loads.json, perf_budgets.json's scene_swap targets (the title and the
battle sandbox), and every Act I encounter in game/data/battle/encounters.json as a field battle
(`battle:<id>`, the probe's --encounter).

Usage: python3 tools/loading/act1_swap_sweep.py [--godot godot] [--only <substring>] [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCENE_LOADS = ROOT / "game/data/ui/scene_loads.json"
BUDGETS = ROOT / "game/data/debug/perf_budgets.json"
ENCOUNTERS = ROOT / "game/data/battle/encounters.json"
ACT1_PREFIXES = ("prologue", "ch01_", "ch02_", "ch03_", "ch04_", "ch05_", "ch06_", "ch07_", "ch08_", "ch09_")
BATTLE_PREFIX = "battle:"
PROBE_TAG = "SCENE_SWAP_PROBE "
HIDDEN_BUDGET_MS = 1000.0
TIMEOUT_S = 600


def targets() -> list[str]:
    zones = list(json.loads(SCENE_LOADS.read_text())["scene_loads"]["scenes"])
    swap = json.loads(BUDGETS.read_text())["scene_swap"]
    rows = json.loads(ENCOUNTERS.read_text())
    rows = rows.get("encounters", []) if isinstance(rows, dict) else rows
    battles = sorted(BATTLE_PREFIX + r["id"] for r in rows if str(r.get("id", "")).startswith(ACT1_PREFIXES))
    return sorted(zones) + [t for t in swap["targets"] if t not in zones] + battles


def probe_scene() -> str:
    return json.loads(BUDGETS.read_text())["scene_swap"]["probe_scene"]


def parse_stats(output: str) -> dict | None:
    for line in output.splitlines():
        if line.startswith(PROBE_TAG):
            try:
                parsed = json.loads(line[len(PROBE_TAG):])
            except json.JSONDecodeError:
                return None
            return parsed if isinstance(parsed, dict) else None
    return None


def row(target: str, stats: dict | None) -> dict:
    if stats is None:
        return {
            "target": target,
            "ok": False,
            "covered": False,
            "max_frame_ms": None,
            "entry_ms": None,
            "max_visible_frame_ms": None,
        }
    covered = bool(stats.get("covered", False))
    return {
        "target": target,
        "ok": covered,
        "covered": covered,
        "cover_alpha_min": stats.get("cover_alpha_min"),
        "max_frame_ms": stats.get("max_frame_ms"),
        "entry_ms": stats.get("entry_ms"),
        "max_visible_frame_ms": stats.get("max_visible_frame_ms"),
        "over_budget": bool(stats.get("over_budget", False)),
        "prewarm_wait_frames": stats.get("prewarm_wait_frames"),
    }


def run(godot: str, target: str) -> dict:
    where = "--encounter=" + target[len(BATTLE_PREFIX):] if target.startswith(BATTLE_PREFIX) else "--to=" + target
    args = [godot, "--headless", "--path", str(ROOT), probe_scene(), "--", where]
    args += ["--resident-loads", "--warm-resident"]
    try:
        done = subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT_S, check=False)
        return row(target, parse_stats(done.stdout + done.stderr))
    except subprocess.TimeoutExpired:
        return row(target, None)


def fmt(r: dict) -> str:
    ms = r["max_frame_ms"]
    entry = r["entry_ms"]
    vis = r["max_visible_frame_ms"]
    worst = "-" if ms is None else "%.0f ms%s" % (ms, " OVER" if ms > HIDDEN_BUDGET_MS else "")
    return "%-9s %-13s %-10s %-12s %s" % (
        "covered" if r["covered"] else "UNCOVERED",
        worst,
        "-" if entry is None else "%.0f ms" % entry,
        "-" if vis is None else "%.1f ms" % vis,
        r["target"],
    )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--only", default="")
    ap.add_argument("--json", default="")
    a = ap.parse_args(argv)
    rows = []
    print("%-9s %-13s %-10s %-12s %s" % ("cover", "worst hidden", "entry", "worst shown", "target"))
    for t in targets():
        if a.only and a.only not in t:
            continue
        r = run(a.godot, t)
        rows.append(r)
        print(fmt(r), flush=True)
    if a.json:
        Path(a.json).write_text(json.dumps(rows, indent=1) + "\n")
    bad = [r["target"] for r in rows if not r["ok"]]
    if bad:
        print("not covered or no stats: %s" % ", ".join(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
