"""The Act III dialogue rules (docs/kb/story/act3/README.md, act3_ending.md §0), shared by the draft checker
(docs/kb/story/act3/drafts/check_drafts.py) and the production check (tools/tests/test_act3_rules.py, M5-A3P-1000).

Each function takes one .dlg path and returns error strings; the chapter comes from the file's folder (ch17, ch18, ...).
- letterbox_errors: the letterbox is off again wherever a node ends with `===` and no jump.
- light_errors: released light rises, and only in a Kirru-way lifting, a release, or from H09 on; held light never
  rises; bound light is still; nothing is held or bound after H09.
- act3_errors: no line in Dace's voice in Ch17 (the ledger is read); "revenant" not before Ch19; no Eighth Verse sung
  before H07; #lamptongue lines use only docs/kb/audio/lamptongue.md §1's roots, and verse 8 is sung only in H07;
  every flag a condition or <<set>> names is in `flags`.
"""

from __future__ import annotations

import re
from pathlib import Path

# Where light may rise before H09 (Act III README rule 1): a Kirru-way lifting, each Vowbound's release, Kesh's release,
# and Sefir's (H08). From H09 on everything rises (act3_ending §0 rules 3, 4, 7) and nothing may be held or bound.
LIFT_ALLOWED = {"ch18_backs_to_the_water.dlg", "ch21_kesh_release.dlg", "ch21_the_letting.dlg", "ch21_sefir_lets_go.dlg"}
LIFT_ALLOWED_SUFFIX = "_release.dlg"
AFTER_H09 = ("ch21_great_unbinding.dlg", "ending_")
# docs/kb/audio/lamptongue.md §1: the glossary's nine roots and Audio's eight. New Lamptongue is built from these only.
LAMPTONGUE_ROOTS = {"vey", "ish", "karra", "hal", "ennu", "mir", "tash", "re", "oan",
                    "arre", "seli", "aun", "thel", "sen", "sev", "kor", "una"}
LETTING = "ch21_the_letting.dlg"
FLAG_USE = re.compile(r"\$([a-z0-9_]+)")
DECLARED = re.compile(r'^"([a-z0-9_]+)":', re.M)


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


def after_h09(path: Path) -> bool:
    return path.name.startswith(AFTER_H09[1]) or path.name == AFTER_H09[0]


def light_errors(path: Path) -> list[str]:
    out = []
    for no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        t = raw.strip()
        if t.startswith("@vfx glimmer_lift"):
            if "motion=spiral_up" not in t:
                out.append(f"{path.name}:{no}: released light must rise (motion=spiral_up)")
            if not (path.name in LIFT_ALLOWED or path.name.endswith(LIFT_ALLOWED_SUFFIX) or after_h09(path)):
                out.append(f"{path.name}:{no}: nothing rises in Act III before H09 except a Kirru-way lifting")
        elif t.startswith(("@vfx glimmer_held", "@vfx glimmer_bound")) and after_h09(path):
            out.append(f"{path.name}:{no}: nothing is held or bound after H09; every mote rises (act3_ending §0 rule 7)")
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
        if path.parent.name == "ch17" and re.match(r"^(Dace|Narrator\(dace\))\b", t):
            out.append(f"{path.name}:{no}: the ledger is read, never voiced: no line in Dace's voice")
        if path.parent.name in ("ch17", "ch18") and re.search(r"\brevenants?\b", t, re.I):
            out.append(f"{path.name}:{no}: 'revenant' is not said before Ch19")
        if re.search(r"\bsings?\b.*\bEighth Verse\b", t):
            out.append(f"{path.name}:{no}: the Eighth Verse is never sung before H07")
        if "#lamptongue" in t:
            text = re.sub(r"^[A-Z][A-Za-z_]*(?: as \"[^\"]+\")? \[[a-z_]+\]: ", "", t.split(" #line:")[0])
            for word in re.findall(r"[a-z]+", text.lower()):
                if word not in LAMPTONGUE_ROOTS:
                    out.append(f"{path.name}:{no}: '{word}' is not a Lamptongue root (docs/kb/audio/lamptongue.md §1)")
            if "#sung" in t and "tash" in text.lower() and path.name != LETTING:
                out.append(f"{path.name}:{no}: verse 8 (the Letting) is sung only in H07, {LETTING}")
        if t.startswith("<<"):
            for f in FLAG_USE.findall(t):
                if f not in flags:
                    out.append(f"{path.name}:{no}: flag '{f}' is not declared (flags.tres, or the drafts README's 'Flags to declare')")
    return out


def declared_flags(root: Path) -> set[str]:
    return set(DECLARED.findall((root / "game" / "data" / "flags.tres").read_text(encoding="utf-8")))
