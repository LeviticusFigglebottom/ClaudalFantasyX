"""Integration QA (M3-HER-1121): no beat waits on a flag nothing sets (a softlock you can't see in any one file).

Every `when: {"set": [...]}` in the chapter files, every Interactable's `requires_flag` in the zone layouts and every
objective's `requires` names flags that must be raised before that beat, prompt or objective can come up.
This collects every place the game raises a flag:
- chapter and flow steps `{"set": "<flag>"}`;
- any data key `sets_flag`, `flag`, or ending in `_flag`, with a string value;
- `sets_flag = &"<flag>"` on Interactables in scenes;
- `<<set $<flag> ...>>` in dialogue;
- `Game.set_flag(&"<flag>")` in code;
- the flags Game.set_chapter raises (`chNN_started`).
It fails on any required flag no setter names. Flags already handed to their owner are listed in
tests/integration/qa_known.json "unset_flags" (flag -> task).
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHAPTERS = ROOT / "game" / "data" / "flow" / "chapters"
KNOWN = ROOT / "tests" / "integration" / "qa_known.json"

SET_DLG = re.compile(r"<<set \$([a-z0-9_]+)")
SET_TSCN = re.compile(r'sets_flag = &?"([a-z0-9_]+)"')
SET_GD = re.compile(r'Game\.set_flag\(&?"([a-z0-9_]+)"')
CHAPTER_STARTED = re.compile(r"^ch\d\d_started$")


def _walk_setters(v: object, out: set[str]) -> None:
    if isinstance(v, dict):
        for k, x in v.items():
            if isinstance(x, str) and (k == "set" or k == "sets_flag" or k == "flag" or k.endswith("_flag")):
                out.add(x)
            else:
                _walk_setters(x, out)
    elif isinstance(v, list):
        for x in v:
            _walk_setters(x, out)


def _walk_required(v: object, out: dict[str, str], where: str) -> None:
    if isinstance(v, dict):
        when = v.get("when")
        if isinstance(when, dict):
            for f in when.get("set", []) or []:
                out.setdefault(str(f), where)
        if isinstance(v.get("requires_flag"), str) and v["requires_flag"]:  # an Interactable that waits on a flag
            out.setdefault(v["requires_flag"], where)
        if isinstance(v.get("requires"), list):  # an objective that waits on flags
            for f in v["requires"]:
                if isinstance(f, str):
                    out.setdefault(f, where)
        for k, x in v.items():
            _walk_required(x, out, f"{where}.{k}")
    elif isinstance(v, list):
        for i, x in enumerate(v):
            _walk_required(x, out, f"{where}[{i}]")


def setters() -> set[str]:
    out: set[str] = set()
    for p in (ROOT / "game").rglob("*.json"):  # data tables and zone layouts (their Interactables set flags)
        try:
            _walk_setters(json.loads(p.read_text(encoding="utf-8")), out)
        except (ValueError, UnicodeDecodeError):
            continue
    for p in (ROOT / "game" / "data" / "dialogue").rglob("*.dlg"):
        out.update(SET_DLG.findall(p.read_text(encoding="utf-8")))
    for p in (ROOT / "game").rglob("*.tscn"):
        out.update(SET_TSCN.findall(p.read_text(encoding="utf-8", errors="ignore")))
    for p in (ROOT / "game").rglob("*.gd"):
        out.update(SET_GD.findall(p.read_text(encoding="utf-8", errors="ignore")))
    return out


def required() -> dict[str, str]:
    out: dict[str, str] = {}
    sources = sorted(CHAPTERS.glob("*.json")) + [ROOT / "game" / "data" / "flow" / "objectives.json"]
    sources += sorted((ROOT / "game" / "levels").rglob("*_layout.json"))
    for p in sources:
        if p.exists():
            _walk_required(json.loads(p.read_text(encoding="utf-8")), out, str(p.relative_to(ROOT)))
    return out


class FlagReachTests(unittest.TestCase):
    def test_every_required_flag_has_a_setter(self) -> None:
        known = json.loads(KNOWN.read_text(encoding="utf-8")).get("unset_flags", {}) if KNOWN.exists() else {}
        have = setters()
        missing = {
            f: where
            for f, where in required().items()
            if f not in have and not CHAPTER_STARTED.match(f) and f not in known
        }
        self.assertEqual(
            missing, {}, "beats wait on flags that nothing sets (a softlock): " + json.dumps(missing, indent=1)
        )

    def test_the_collector_sees_each_kind_of_setter(self) -> None:
        have = setters()
        self.assertTrue(any(f.startswith("ch0") for f in have), "chapter steps and dialogue set chapter flags")
        self.assertIn("prologue_seen", have, "a Game.set_flag call in code is seen")

    def test_the_requirements_come_from_every_source(self) -> None:
        req = required()
        self.assertGreater(len(req), 20, "chapter whens, layout prompts and objectives are all read")
        self.assertTrue(any("_layout.json" in w for w in req.values()), "an Interactable's requires_flag is read")
        self.assertTrue(any("objectives.json" in w for w in req.values()), "an objective's requires is read")


if __name__ == "__main__":
    unittest.main()
