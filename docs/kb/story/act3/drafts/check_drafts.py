"""Check the Act III draft scripts (planning only) with the Act II checks, without wiring them into the game.

Usage: python3 docs/kb/story/act3/drafts/check_drafts.py

1. dlgc: copies game/data to a temporary root, adds the drafts under game/data/dialogue/act3_drafts/, and compiles the
   whole project with tools/dlgc.py. Every dlgc error or warning in a draft is reported: syntax, cues and their
   arguments, events, speakers, emotions, line ids (unique across the game), choices, conditions, words per line.
2. The Act II runtime rules (tests/integration/test_act2_dialogue.gd), checked statically:
   - the letterbox is off again wherever a node ends with `===` and no jump;
   - glimmer light: glimmer_lift needs motion=spiral_up and may appear only in LIFT_ALLOWED (Act III README rule 1);
     glimmer_held never rises; glimmer_bound is still.
3. The Act III rules (act3/README.md): no speaker or narration in Dace's voice; "revenant" not before Ch19; no
   Eighth Verse sung; every flag read or set is declared in game/data/flags.tres or in README.md's "Flags to declare"
   table.
Banned terms are covered by tools/validate_data.py, which already scans docs/kb/story/ and every .dlg file.
Exit code 1 on any error.
"""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import dlgc  # noqa: E402

LIFT_ALLOWED = {"ch18_backs_to_the_water.dlg"}
FLAG_USE = re.compile(r"\$([a-z0-9_]+)")
README_FLAG = re.compile(r"^\| `([a-z0-9_]+)` \|", re.M)
DECLARED = re.compile(r'^"([a-z0-9_]+)":', re.M)


def drafts() -> list[Path]:
    return sorted(HERE.glob("ch*/*.dlg"))


def run_dlgc(files: list[Path]) -> tuple[list[str], list[str]]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shutil.copytree(ROOT / "game" / "data", root / "game" / "data")
        for f in files:
            dest = root / "game" / "data" / "dialogue" / "act3_drafts" / f.parent.name / f.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(f, dest)
        result = dlgc.compile_project(root)
        mine = lambda msg: "act3_drafts" in str(msg)  # noqa: E731
        return [str(e) for e in result.errors if mine(e)], [str(w) for w in result.warnings if mine(w)]


def letterbox_errors(path: Path) -> list[str]:
    out, on, jumped = [], False, False
    for no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        t = raw.strip()
        if t.startswith("title:"):
            jumped = False
        elif t.startswith("@letterbox on"):
            on = True
        elif t.startswith("@letterbox off"):
            on = False
        elif t.startswith("<<jump") or t.startswith("<<event start_battle"):
            jumped = True
        elif t == "===":
            if on and not jumped:
                out.append(f"{path.name}:{no}: the node ends with the letterbox still on")
            if not jumped:
                on = False
    return out


def light_errors(path: Path) -> list[str]:
    out = []
    for no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        t = raw.strip()
        if t.startswith("@vfx glimmer_lift"):
            if "motion=spiral_up" not in t:
                out.append(f"{path.name}:{no}: released light must rise (motion=spiral_up)")
            if path.name not in LIFT_ALLOWED:
                out.append(f"{path.name}:{no}: nothing rises in Act III before H09 except a Kirru-way lifting")
        elif t.startswith("@vfx glimmer_held") and "motion=" in t:
            out.append(f"{path.name}:{no}: held light never rises")
        elif t.startswith("@vfx glimmer_bound") and ("motion=" in t or "drift=" in t):
            out.append(f"{path.name}:{no}: bound light is still")
    return out


def act3_errors(path: Path, flags: set[str]) -> list[str]:
    out = []
    for no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        t = raw.strip()
        if t.startswith("//"):
            continue
        if re.match(r"^(Dace|Narrator\(dace\))\b", t):
            out.append(f"{path.name}:{no}: the ledger is read, never voiced: no line in Dace's voice")
        if re.search(r"\brevenants?\b", t, re.I):
            out.append(f"{path.name}:{no}: 'revenant' is not said before Ch19")
        if re.search(r"\bsings?\b.*\bEighth Verse\b", t):
            out.append(f"{path.name}:{no}: the Eighth Verse is never sung before H07")
        if t.startswith("<<"):
            for f in FLAG_USE.findall(t):
                if f not in flags:
                    out.append(f"{path.name}:{no}: flag '{f}' is neither in flags.tres nor in README's 'Flags to declare'")
    return out


def main() -> int:
    files = drafts()
    flags = set(DECLARED.findall((ROOT / "game" / "data" / "flags.tres").read_text(encoding="utf-8")))
    flags |= set(README_FLAG.findall((HERE / "README.md").read_text(encoding="utf-8")))
    errors, warnings = run_dlgc(files)
    for f in files:
        errors += letterbox_errors(f) + light_errors(f) + act3_errors(f, flags)
    for w in warnings:
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    print(f"check_drafts: {len(files)} file(s), {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
