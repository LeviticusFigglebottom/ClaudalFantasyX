#!/usr/bin/env python3
"""The playthrough stills' plan (ADR 0041; tools/act1/cutscene_stills.tscn renders it): each zone visit of the Act I
chapter flows from Ch4 on, in chapter order, with its arrive rows and beats in flow order. The harness plays each visit
on one zone instance and runs the flow's own steps (set, zone calls, place, party, play), so the actors stand where the
story left them when each scene starts.

    python3 tools/act1/cutscene_stills_plan.py OUT.json [chNN ...]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHAPTERS = ROOT / "game" / "data" / "flow" / "chapters"
# The flow steps the harness runs; the plan adds "stand" ([x, y, z]: the player on a beat's trigger) and "reload".
STEP_KEYS = ("set", "zone", "place", "party", "play")


def beat_triggers(scene: str) -> dict[str, dict]:
    """{beat: its trigger} from the zone layout's triggers whose payload names a flow beat."""
    path = ROOT / scene.replace("res://", "").replace(".tscn", "_layout.json")
    if not scene or not path.exists():
        return {}
    layout = json.loads(path.read_text(encoding="utf-8"))
    return {t["payload"]["beat"]: t for t in layout.get("triggers", []) if "beat" in t.get("payload", {})}


def scene_sets() -> dict[str, tuple[set, list]]:
    """{scene title: ({flags its <<set>>s raise}, [titles it jumps to])} over every chapter's dialogue."""
    out = {}
    for f in sorted((ROOT / "game/data/dialogue").glob("ch*/*.dlg")):
        for body in re.split(r"^===\s*$", f.read_text(encoding="utf-8"), flags=re.M):
            m = re.search(r"^title:\s*(\S+)", body, re.M)
            if m:
                raised = set(re.findall(r"<<set \$(\w+) = true>>", body))
                out[m.group(1)] = (raised, re.findall(r"<<jump (\S+)>>", body))
    return out


def provides(steps: list[dict], sets: dict) -> set:
    """The flags a group's steps raise: set steps, battle victories and the <<set>>s of the scenes it plays."""
    out, todo, seen = set(), [], set()
    for s in steps:
        out |= {s["set"]} if "set" in s else set()
        out |= {s["victory_flag"]} if "victory_flag" in s else set()
        todo += [s["play"]] if "play" in s else []
    while todo:
        t = todo.pop()
        if t not in seen and t in sets:
            seen.add(t)
            out |= sets[t][0]
            todo += sets[t][1]
    return out


def story_order(groups: list[dict], elsewhere: set) -> list[dict]:
    """The zone's groups as the story meets them (the flow lists arrive rows latest first): a group comes after the
    groups that raise the flags it needs, and before any that raises a flag it needs unset. A flag the chapter's other
    zones raise counts once nothing here is ready without it (the party has been there); a flag nothing in the
    chapter raises is set already (an earlier chapter)."""
    here = set().union(*(g["provides"] for g in groups)) if groups else set()
    done, away, left, out = set(), False, list(groups), []
    while left:
        known = here | (set() if away else elsewhere)
        ready = [g for g in left if set(g["flags"]) & known <= done and not set(g["unset"]) & done]
        if not ready and not away:
            away, done = True, done | elsewhere
            continue
        g = ready[0] if ready else left[0]  # a cycle: keep the flow's order
        left.remove(g)
        out.append(g)
        done |= g["provides"]
    return out


def visits(chapter: str) -> list[dict]:
    locs = {r["id"]: r["scene"] for r in json.loads((ROOT / "game/data/world/locations.json").read_text())["locations"]}
    flow = json.loads((CHAPTERS / f"{chapter}.json").read_text())
    sets = scene_sets()
    out = []
    for loc, zone in flow.get("zones", {}).items():
        groups = []
        stands = beat_triggers(locs.get(loc, ""))
        beats = zone.get("beats", {})
        inline = {s["beat"] for g in zone.get("arrive", []) for s in g.get("steps", []) if "beat" in s}
        rows = [(None, g) for g in zone.get("arrive", [])] + [(b, g) for b, g in beats.items() if b not in inline]
        for beat, g in rows:
            # an arrive row's {"beat": id} step runs that beat's steps there, in the arrival's state
            flat = []
            for s in g.get("steps", []):
                flat += beats.get(s["beat"], {}).get("steps", []) if "beat" in s else [s]
            raises = provides(flat, sets)
            # a go to this same location reloads it (a variant may apply: Ch9's dawn): "reload" with its spawn
            flat = [{"reload": s["go"].get("spawn", "")} if s.get("go", {}).get("location") == loc else s for s in flat]
            steps = [s for s in flat if any(k in s for k in STEP_KEYS + ("reload",))]
            when = g.get("when", {})
            need, avoid = list(when.get("set", [])), list(when.get("unset", []))
            if beat in stands:  # the player walked into the beat's trigger: stand them on it, as in play
                trig = stands[beat]
                steps = [{"stand": trig["at"][:3]}] + steps
                need += [trig["requires_flag"]] if trig.get("requires_flag") else []
                avoid += [trig["blocked_by_flag"]] if trig.get("blocked_by_flag") else []
            # rows with no scene (a fight) order the story too; they are dropped after story_order
            groups.append({"flags": need, "unset": avoid, "arrive": beat is None, "provides": raises, "steps": steps})
        if groups and locs.get(loc):
            out.append({"zone": locs[loc], "location": loc, "party": zone.get("party", {}), "groups": groups})
    for v in out:
        elsewhere = set().union(*(g["provides"] for w in out if w is not v for g in w["groups"]))
        v["groups"] = story_order(v["groups"], elsewhere - set().union(*(g["provides"] for g in v["groups"])))
        v["groups"] = [g for g in v["groups"] if any("play" in s for s in g["steps"])]
        for g in v["groups"]:
            g["provides"] = sorted(g["provides"])
    return [v for v in out if v["groups"]]


def main() -> None:
    chapters = sys.argv[2:] or [f"ch0{n}" for n in range(4, 10)]
    plan = [v for c in chapters for v in visits(c)]
    Path(sys.argv[1]).write_text(json.dumps(plan, indent=1) + "\n", encoding="utf-8")
    print(f"{len(plan)} visits, {sum(1 for v in plan for g in v['groups'] for s in g['steps'] if 'play' in s)} scenes")


if __name__ == "__main__":
    main()
