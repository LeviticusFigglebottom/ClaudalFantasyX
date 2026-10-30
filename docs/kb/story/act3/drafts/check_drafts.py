"""Check the Act III draft scripts (planning only) with the Act II checks, without wiring them into the game.

Usage: python3 docs/kb/story/act3/drafts/check_drafts.py

1. dlgc: copies game/data to a temporary root, adds the drafts under game/data/dialogue/act3_drafts/, and compiles the
   whole project with tools/dlgc.py. Every dlgc error or warning in a draft is reported: syntax, cues and their
   arguments, events, speakers, emotions, line ids (unique across the game), choices, conditions, words per line.
2. The Act II runtime rules (tests/integration/test_act2_dialogue.gd), checked statically:
   - the letterbox is off again wherever a node ends with `===` and no jump;
   - glimmer light: glimmer_lift needs motion=spiral_up and may appear only in LIFT_ALLOWED (Act III README rule 1);
     glimmer_held never rises; glimmer_bound is still.
3. The Act III rules (act3/README.md, act3_ending §0): no line in Dace's voice in Ch17 (the ledger is read);
   "revenant" not before Ch19; no Eighth Verse sung before H07; light rises only in a lifting, a release, or after H09,
   and nothing is held or bound after H09; every flag read or set is declared in game/data/flags.tres or in README.md's
   "Flags to declare" table; a #lamptongue line uses only docs/kb/audio/lamptongue.md §1's roots, and verse 8 is sung
   only in H07. Speakers the game doesn't have yet come from README.md's "Speakers to add" table and are
   added to the temporary copy only.
Banned terms are covered by tools/validate_data.py, which already scans docs/kb/story/ and every .dlg file.
Exit code 1 on any error.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import dlgc  # noqa: E402

from act3_rules import (  # noqa: E402
    DECLARED,
    act3_errors,
    letterbox_errors,
    light_errors,
)

README_SPEAKER = re.compile(r"^\| `([a-z0-9_]+)` \| ([^|]+?) \| speaker \|", re.M)
README_FLAG = re.compile(r"^\| `([a-z0-9_]+)` \|", re.M)


def drafts() -> list[Path]:
    return sorted(p for d in ("ch17", "ch18", "ch19", "ch20", "ending") for p in HERE.glob(f"{d}/*.dlg"))


def run_dlgc(files: list[Path]) -> tuple[list[str], list[str]]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shutil.copytree(ROOT / "game" / "data", root / "game" / "data")
        add_draft_speakers(root)
        for f in files:
            dest = root / "game" / "data" / "dialogue" / "act3_drafts" / f.parent.name / f.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(f, dest)
        result = dlgc.compile_project(root)
        mine = lambda msg: "act3_drafts" in str(msg)  # noqa: E731
        return [str(e) for e in result.errors if mine(e)], [str(w) for w in result.warnings if mine(w)]


def add_draft_speakers(root: Path) -> None:
    """The speakers the drafts need that the game doesn't have yet (README's table), in the temporary copy only."""
    rows = README_SPEAKER.findall((HERE / "README.md").read_text(encoding="utf-8"))
    sp = root / "game" / "data" / "dialogue" / "speakers.json"
    data = json.loads(sp.read_text(encoding="utf-8"))
    known = {r["id"] for r in data["speakers"]}
    csv_rows = ["keys,en"]
    for sid, name in rows:
        if sid not in known:
            data["speakers"].append({"id": sid, "name_key": f"CHAR_{sid.upper()}"})
            csv_rows.append(f"CHAR_{sid.upper()},{name.strip()}")
    sp.write_text(json.dumps(data, indent=1), encoding="utf-8")
    (root / "game" / "data" / "loc" / "zz_act3_drafts.csv").write_text("\n".join(csv_rows) + "\n", encoding="utf-8")


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
