"""M5-A3P-1981 (Act III, the open-world unlock; SPEC §6.6, act_outline Ch18): flying back to a place must not
replay its chapter. Once the Kite flies, every zone in game/data/world/kite.json can be revisited with the whole
story so far set. This check approximates that state as every flag the game can set: chapter `set` steps,
victory and objective flags, trigger `sets_flag`, `.dlg` `<<set $flag = true>>` lines, GDScript
`set_flag(&"flag")` calls, and the Kite's open_flag. Under it, no `arrive` row of a destination's zone story may
hold. Such a row would replay that chapter's arrival (its `chapter` step rolls the chapter back, its `battle`
refights). The approximation is the most-advanced state; an optional flag a player skipped can still let an
after-scene play on a revisit, by design. `revisit_errors` is pure; `check(root)` reads the repo.
Run: python3 tools/act3/kite_revisit_check.py"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

KITE_FILE = "game/data/world/kite.json"
CHAPTERS_GLOB = "game/data/flow/chapters/*.json"
SKIP_PARTS = ("compiled", "chapter_select")
FLAG_KEYS = {"victory_flag", "objective_flag", "sets_flag"}
DLG_SET_RE = re.compile(r"<<set \$(\w+)\s*=\s*true")
GD_SET_RE = re.compile(r'set_flag\(&?"(\w+)"')


def settable_flags(docs: list[object], dialogue: list[str], scripts: list[str]) -> set[str]:
    """Every flag a step, a battle, a trigger, a dialogue or a script can set (a `when` names, never sets)."""
    out: set[str] = set()

    def walk(o: object) -> None:
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "when":
                    continue
                if k == "set":
                    out.update(x for x in ([v] if isinstance(v, str) else v if isinstance(v, list) else [])
                               if isinstance(x, str))
                elif k in FLAG_KEYS and isinstance(v, str):
                    out.add(v)
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    for d in docs:
        walk(d)
    for text in dialogue:
        out.update(DLG_SET_RE.findall(text))
    for text in scripts:
        out.update(GD_SET_RE.findall(text))
    return out


def holds(when: dict, state: set[str]) -> bool:
    return all(f in state for f in when.get("set", [])) and not any(f in state for f in when.get("unset", []))


def revisit_errors(kite: dict, chapters: dict[str, dict], state: set[str]) -> list[str]:
    """`chapters` maps a chapter file name to its document. One error per arrive row that would replay."""
    state = state | {str(kite.get("open_flag", ""))}
    errors = []
    for key in ("destinations", "secrets"):
        for row in kite.get(key, []):
            loc = str(row.get("location_id", ""))
            for name, doc in sorted(chapters.items()):
                zone = (doc.get("zones", {}) if isinstance(doc, dict) else {}).get(loc)
                if not isinstance(zone, dict):
                    continue
                for i, arrive in enumerate(zone.get("arrive", [])):
                    if holds(arrive.get("when", {}), state):
                        steps = [next(iter(s), "?") for s in arrive.get("steps", [])]
                        errors.append(f"{name} {loc} arrive[{i}] replays when the Kite lands at {row.get('id')}: "
                                      f"its when {arrive.get('when', {})} holds with the story done (steps {steps})")
    return errors


def check(root: Path) -> list[str]:
    def readable(p: Path) -> bool:
        return not any(s in str(p) for s in SKIP_PARTS)

    docs = []
    for p in sorted(root.glob("game/**/*.json")):
        if readable(p):
            try:
                docs.append(json.loads(p.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
    dialogue = [p.read_text(encoding="utf-8") for p in sorted(root.glob("game/data/dialogue/**/*.dlg"))]
    scripts = [p.read_text(encoding="utf-8") for p in sorted(root.glob("game/**/*.gd"))]
    state = settable_flags(docs, dialogue, scripts)
    kite = json.loads((root / KITE_FILE).read_text(encoding="utf-8")).get("kite", {})
    chapters = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.glob(CHAPTERS_GLOB))}
    return revisit_errors(kite, chapters, state)


def main() -> int:
    errors = check(Path(__file__).resolve().parents[2])
    for e in errors:
        print(e)
    print(f"kite revisits: {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
