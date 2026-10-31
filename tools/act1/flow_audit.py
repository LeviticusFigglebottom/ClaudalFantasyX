#!/usr/bin/env python3
"""Act I flow audit (act1-chapters; the Lead's flow and pacing pass, 2026-10-29): dead ends, soft-locks and flag
hygiene over the chapter flows (game/data/flow/chapters/ch01..ch09), their zone layouts and the dialogue.

What it reports:
  never_set     flags Act I reads as "must be set" (a flow `when.set`, a trigger's `requires_flag`, a layout state or
                variant, a dialogue `<<if $flag>>`) that nothing sets anywhere: data, dialogue or code.
  unreachable   flow groups (arrive rows, beats) and triggers that never become enabled. A monotone fixed point from a
                new game: every flag the code sets (a `set_flag` literal in game/, or a data key that names a flag the
                code sets, such as a trial's `landed_flag`) counts as available; a group runs when its `when.set` flags
                are; it adds its `set` steps, battle victory flags, its scenes' <<set>>s (through <<jump>>s) and the
                zones it goes to. `unset` conditions are ignored (they make beats one-shot, never reachable).
  zones         Act I zones that no reachable step goes to (the chapter's start zone aside).
  orphans       Ch1–Ch9 dialogue scenes that no flow, trigger, jump or code names.

    python3 tools/act1/flow_audit.py [--root DIR] [--json]
Exit status 1 when never_set or unreachable has a row.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ACT1_CHAPTERS = [f"ch0{n}" for n in range(1, 10)]
READ_KEYS = {"requires_flag", "blocked_by_flag", "flag", "flags", "unlock_flag", "night_flag", "storm_flag",
             "until_flag", "objective_flag"}
SET_FLAG_CODE = re.compile(r'(?:set_flag\(\s*|sets?_flag\s*:?=\s*)&?"([a-z0-9_]+)"')  # a call, or an Interactable's
GET_FLAG_CODE = re.compile(r'get_flag\(\s*&?"([a-z0-9_]+)"')
DLG_SET = re.compile(r"<<set \$(\w+) = true>>")
DLG_IF = re.compile(r"<<(?:else)?if ([^>]*)>>")
DLG_FLAG = re.compile(r"\$(\w+)")
DLG_TITLE = re.compile(r"^title:\s*(\S+)", re.MULTILINE)
DLG_JUMP = re.compile(r"<<jump (\S+)>>")


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


class Audit:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.scenes: dict[str, tuple[set[str], list[str], set[str], str]] = {}  # title -> sets, jumps, ifs, file
        for f in sorted((root / "game/data/dialogue").glob("**/*.dlg")):
            for body in re.split(r"^===\s*$", f.read_text(encoding="utf-8"), flags=re.MULTILINE):
                m = DLG_TITLE.search(body)
                if m:
                    ifs = {x for cond in DLG_IF.findall(body) for x in DLG_FLAG.findall(cond)}
                    self.scenes[m.group(1)] = (set(DLG_SET.findall(body)), DLG_JUMP.findall(body), ifs,
                                               str(f.relative_to(root)))
        self.code_sets: set[str] = set()
        self.code_text = ""
        for f in (root / "game").glob("**/*.gd"):
            text = f.read_text(encoding="utf-8")
            self.code_sets |= set(SET_FLAG_CODE.findall(text))
            self.code_text += text
        self.data_sets: set[str] = set()
        self.code_beats: set[str] = set()
        for f in list((root / "game/data").glob("**/*.json")) + list((root / "game/levels").glob("**/*_layout.json")):
            try:
                self._data_setters(load(f))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
        self.chapters = {c: load(root / f"game/data/flow/chapters/{c}.json") for c in ACT1_CHAPTERS
                         if (root / f"game/data/flow/chapters/{c}.json").exists()}
        # M5-A3P-1004: the later chapters' flows (Act III's revisits to Act I zones wait on their flags, e.g.
        # ch18_world_open); what they set counts as available, since the story reaches them after Act I
        self.later_chapters = [load(f) for f in sorted((root / "game/data/flow/chapters").glob("ch*.json"))
                               if f.stem not in ACT1_CHAPTERS]
        self.layouts: dict[str, dict] = {}
        for data in self.chapters.values():
            for zid in data.get("zones", {}):
                p = root / f"game/levels/{zid}/{zid.split('/')[-1]}_layout.json"
                if p.exists():
                    self.layouts[zid] = load(p)

    def _data_setters(self, o: object) -> None:
        if isinstance(o, dict):
            for k, v in o.items():
                if k.endswith("flag") and k not in READ_KEYS and isinstance(v, str) and v:
                    self.data_sets.add(v)
                if k.endswith("_beat") and isinstance(v, str) and v:
                    self.code_beats.add(v)  # a beat a zone's code runs (Coilspire's trial: seized_beat)
                self._data_setters(v)
        elif isinstance(o, list):
            for v in o:
                self._data_setters(v)

    def scene_sets(self, title: str, seen: set[str] | None = None) -> set[str]:
        seen = set() if seen is None else seen
        if title in seen or title not in self.scenes:
            return set()
        seen.add(title)
        sets, jumps, _ifs, _f = self.scenes[title]
        out = set(sets)
        for j in jumps:
            out |= self.scene_sets(j, seen)
        return out

    def step_effects(self, steps: list[dict]) -> tuple[set[str], set[str], set[str], set[str]]:
        """(flags set, zones gone to, scenes played, beats run) by a list of flow steps."""
        flags, zones, scenes, beats = set(), set(), set(), set()
        for s in steps:
            if "set" in s:
                flags.add(s["set"])
            if "play" in s:
                scenes.add(s["play"])
                flags |= self.scene_sets(s["play"])
            if "battle" in s:
                flags |= {s[k] for k in ("victory_flag",) if s.get(k)}
                if s.get("return_spawn"):
                    pass
            if "go" in s:
                zones.add(str(s["go"].get("location", "")))
            if "beat" in s:
                beats.add(s["beat"])
            if "if_event" in s:
                f, z, sc, b = self.step_effects(s.get("steps", []))  # the steps run when the scene raises the event
                flags, zones, scenes, beats = flags | f, zones | z, scenes | sc, beats | b
        return flags, zones, scenes, beats

    def run(self) -> dict:
        have = set(self.code_sets) | set(self.data_sets)
        for data in self.later_chapters:
            for z in data.get("zones", {}).values():
                for g in z.get("arrive", []) + list(z.get("beats", {}).values()):
                    have |= self.step_effects(g["steps"])[0]
        zones = {next(iter(self.chapters[c]["zones"])) for c in self.chapters if self.chapters[c].get("zones")}
        played: set[str] = set()
        groups = []  # (label, zone, when.set, steps, kind)
        triggers = []  # (label, zone, requires, payload, sets_flag)
        for c, data in self.chapters.items():
            for zid, z in data.get("zones", {}).items():
                for i, g in enumerate(z.get("arrive", [])):
                    groups.append((f"{zid} arrive[{i}]", zid, set(g.get("when", {}).get("set", [])), g["steps"],
                                   "arrive"))
                for bid, g in z.get("beats", {}).items():
                    groups.append((f"{zid} beat:{bid}", zid, set(g.get("when", {}).get("set", [])), g["steps"],
                                   "beat"))
                for t in self.layouts.get(zid, {}).get("triggers", []):
                    req = t.get("requires_flag")
                    triggers.append((f"{zid} trigger:{t['id']}", zid, {req} if req else set(), t.get("payload", {}),
                                     t.get("sets_flag")))
        done_g: set[str] = set()
        done_t: set[str] = set()
        beats_live: set[tuple[str, str]] = {(g[1], g[0].split("beat:")[1]) for g in groups
                                            if g[4] == "beat" and g[0].split("beat:")[1] in self.code_beats}
        changed = True
        while changed:
            changed = False
            for label, zid, req, payload, sets_flag in triggers:
                if label in done_t or zid not in zones or not req <= have:
                    continue
                done_t.add(label)
                changed = True
                if sets_flag:
                    have.add(sets_flag)
                if "beat" in payload:
                    beats_live.add((zid, payload["beat"]))
                if "dialogue" in payload:
                    played.add(payload["dialogue"])
                    have |= self.scene_sets(payload["dialogue"])
            for label, zid, req, steps, kind in groups:
                if label in done_g or zid not in zones or not req <= have:
                    continue
                if kind == "beat" and (zid, label.split("beat:")[1]) not in beats_live:
                    continue
                done_g.add(label)
                changed = True
                f, zs, sc, bs = self.step_effects(steps)
                have |= f
                zones |= zs
                played |= sc
                beats_live |= {(zid, b) for b in bs}
        # flags Act I reads as "must be set"
        reads: dict[str, list[str]] = {}

        def read(flag: str, where: str) -> None:
            reads.setdefault(flag, []).append(where)

        for label, zid, req, _steps, _k in groups:
            for f in req:
                read(f, label)
        for label, _zid, req, _p, _s in triggers:
            for f in req:
                read(f, label)
        for zid, lay in self.layouts.items():
            for s in lay.get("states", []):
                if s.get("flag"):
                    read(s["flag"], f"{zid} state")
            for v in lay.get("variants", []):
                for f in v.get("when", {}).get("set", []):
                    read(f, f"{zid} variant")
        for title, (_sets, _jumps, ifs, f) in self.scenes.items():
            if any(f"/{c}/" in f for c in ACT1_CHAPTERS):
                for flag in ifs:
                    read(flag, f"{title} <<if>>")
        all_sets = have | self.code_sets | self.data_sets | {x for s in self.scenes.values() for x in s[0]}
        for data in self.chapters.values():
            for z in data.get("zones", {}).values():
                for g in z.get("arrive", []) + list(z.get("beats", {}).values()):
                    all_sets |= self.step_effects(g["steps"])[0]
        for lay in self.layouts.values():
            all_sets |= {t["sets_flag"] for t in lay.get("triggers", []) if t.get("sets_flag")}
        never_set = {f: w for f, w in sorted(reads.items()) if f not in all_sets}
        unreachable = sorted({g[0] for g in groups} - done_g) + sorted({t[0] for t in triggers} - done_t)
        act1_zones = set(self.layouts)
        orphans = []
        named = played | {j for s in self.scenes.values() for j in s[1]}
        refs = self.code_text + "".join(
            f.read_text(encoding="utf-8") for ext in ("json", "tscn") for f in (self.root / "game").glob(f"**/*.{ext}")
            if "/dialogue/compiled/" not in str(f))
        for title, (_s, _j, _i, f) in sorted(self.scenes.items()):
            if any(f"/{c}/" in f for c in ACT1_CHAPTERS) and title not in named and title not in refs:
                orphans.append(f"{title} ({f})")
        # A flag read in chapter N whose data and dialogue setters are all in later chapters (code setters unknown).
        set_in: dict[str, set[int]] = {}
        for c, data in self.chapters.items():
            n = int(c[2:])
            for zid, z in data.get("zones", {}).items():
                for g in z.get("arrive", []) + list(z.get("beats", {}).values()):
                    for f in self.step_effects(g["steps"])[0]:
                        set_in.setdefault(f, set()).add(n)
                for tr in self.layouts.get(zid, {}).get("triggers", []):
                    p = tr.get("payload", {})
                    for f in ({tr["sets_flag"]} if tr.get("sets_flag") else set()) | (
                            self.scene_sets(p["dialogue"]) if "dialogue" in p else set()):
                        set_in.setdefault(f, set()).add(n)
        late = []
        for f, wheres in sorted(reads.items()):
            if f in self.code_sets or f in self.data_sets or f not in set_in:
                continue
            for w in wheres:
                m = re.match(r"(ch0\d)", w)
                if m and min(set_in[f]) > int(m.group(1)[2:]):
                    late.append(f"{f}: read by {w}, first set in ch0{min(set_in[f])}")
        return {"never_set": never_set, "unreachable": unreachable, "late": late,
                "zones": sorted(act1_zones - zones), "orphans": orphans}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    out = Audit(Path(a.root)).run()
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        for k, v in out.items():
            print(f"== {k} ({len(v)})")
            for row in (v.items() if isinstance(v, dict) else v):
                print("  ", row if isinstance(row, str) else f"{row[0]}: read by {', '.join(row[1][:4])}")
    return 1 if out["never_set"] or out["unreachable"] or out["late"] else 0


if __name__ == "__main__":
    sys.exit(main())
