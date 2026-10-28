#!/usr/bin/env python3
"""The playthrough stills' plan (ADR 0041; tools/act1/cutscene_stills.tscn renders it): each zone visit of the Act I
chapter flows from Ch4 on, in chapter order, with its arrive rows and beats in flow order. The harness plays each visit
on one zone instance and runs the flow's own steps (set, zone calls, place, party, play), so the actors stand where the
story left them when each scene starts.

    python3 tools/act1/cutscene_stills_plan.py OUT.json [chNN ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHAPTERS = ROOT / "game" / "data" / "flow" / "chapters"
STEP_KEYS = ("set", "zone", "place", "party", "play")


def visits(chapter: str) -> list[dict]:
    locs = {r["id"]: r["scene"] for r in json.loads((ROOT / "game/data/world/locations.json").read_text())["locations"]}
    flow = json.loads((CHAPTERS / f"{chapter}.json").read_text())
    out = []
    for loc, zone in flow.get("zones", {}).items():
        groups = []
        for g in list(zone.get("arrive", [])) + list(zone.get("beats", {}).values()):
            steps = [s for s in g.get("steps", []) if any(k in s for k in STEP_KEYS)]
            if any("play" in s for s in steps):
                groups.append({"flags": list(g.get("when", {}).get("set", [])), "steps": steps})
        if groups and locs.get(loc):
            out.append({"zone": locs[loc], "location": loc, "party": zone.get("party", {}), "groups": groups})
    return out


def main() -> None:
    chapters = sys.argv[2:] or [f"ch0{n}" for n in range(4, 10)]
    plan = [v for c in chapters for v in visits(c)]
    Path(sys.argv[1]).write_text(json.dumps(plan, indent=1) + "\n", encoding="utf-8")
    print(f"{len(plan)} visits, {sum(1 for v in plan for g in v['groups'] for s in g['steps'] if 'play' in s)} scenes")


if __name__ == "__main__":
    main()
