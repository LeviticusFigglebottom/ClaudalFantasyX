"""Act I mix pass: the loudness step at every music change the player hears, cutscene -> field -> battle and back
(the Lead's 10-30 item on 7dc3ab41; M3-AUD-864's transitions, measured as levels).

For each Act I chapter it pairs the cues that hand over to each other:
* a cutscene's `@music` cues in script order, and its last cue -> the zone loop its `location:` resumes on release;
* every Act I zone loop -> the regular battle cue (music.json battle.default) and back;
* a chapter's zone loops -> each of its boss cues (battle.encounters), and back.

Each cue's level is its integrated loudness as the deck plays it (its file, or the stack of its `start_stems`), plus
the row's `volume_db`. A step over STEP_LU between two cues that hand over is reported; the deck crossfades on the beat
(M3-AUD-864), so a step is heard as one cue being louder than the other, not as a click. Report only.

Act II (M4-A2P-1950, the Lead's 10-30 18:04 item): `--act 2` audits Ch10-Ch16's scenes and bosses, and `--chapters
ch10,ch11` keeps the chapters named. Every act also gets the victory hand-over: the victory sting (sfx/battle/
victory.ogg, at its momentary max: a sting's own rule) -> each zone loop the field resumes under it (AudioDirector's battle return).

Run:  python3 tools/audio/act1_mix_pass.py [--md docs/kb/audio/act1_mix_pass.md] [--act 2 --chapters ch10,ch11]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))

import numpy as np  # noqa: E402

import act1_audio_audit as A  # noqa: E402
from synth.loudness import integrated_lufs, momentary_max_lufs  # noqa: E402
from synth.mixer import read_audio  # noqa: E402

AUDIO = ROOT / "game" / "data" / "audio"
STEP_LU = 3.0          # a step past this between two cues that hand over is reported
SILENT = {"silence", "stop", "none"}
VICTORY = "sfx:victory"   # the victory sting (a SfxBank row, not a cue): level() reads its file


def _json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _res(r: str) -> Path:
    return ROOT / r.removeprefix("res://")


def cue_files(cid: str) -> tuple[list[Path], float] | None:
    """The files the deck plays for a cue at its start, and the row's volume_db."""
    if cid == VICTORY:
        return [ROOT / "assets/audio/sfx/battle/victory.ogg"], 0.0
    cues = _json(AUDIO / "music.json")["cues"]
    row = cues.get(cid)
    if row is None:
        seq = _json(ROOT / "game" / "data" / "cutscene" / "sequencer.json")
        stand = seq.get("music_stand_ins", {}).get(cid)
        if stand and stand in cues:
            return cue_files(stand)
        p = _res(str(seq.get("music_dir", "res://assets/audio/music/"))) / f"{cid}.ogg"
        return ([p], 0.0) if p.is_file() else None
    if "stems" in row:
        on = row.get("start_stems", [0])
        return [_res(row["stems"][i]) for i in on], float(row.get("volume_db", 0.0))
    return [_res(row["file"])], float(row.get("volume_db", 0.0))


@lru_cache(maxsize=None)
def level(cid: str) -> float | None:
    if cid == VICTORY:  # a sting is held to its momentary max (targets.py), not to the integral of its decay
        return momentary_max_lufs(read_audio(str(ROOT / "assets/audio/sfx/battle/victory.ogg"), channels=2))
    got = cue_files(cid)
    if not got or not all(p.is_file() for p in got[0]):
        return None
    ys = [read_audio(str(p), channels=2) for p in got[0]]
    n = min(len(y) for y in ys)
    return integrated_lufs(np.sum([y[:n] for y in ys], axis=0)) + got[1]


def zone_cues() -> dict[str, str]:
    """Act I level scene -> its zone cue."""
    rows = {r["scene"]: r.get("music", "") for r in _json(AUDIO / "music.json")["zones"]}
    return {s: rows[s] for s in A.act1_scenes() if rows.get(s)}


def chapter_of(path: str) -> str:
    m = re.search(r"/(prologue|ch[01][0-9])/", path)
    return m.group(1) if m else "?"


def enc_chapter(enc: str) -> str:
    """The chapter an encounter id belongs to (the Prologue's Drownbell and Ch8's Reach are named, not numbered)."""
    named = {"drownbell": "prologue", "undertows_reach": "ch08"}
    m = re.match(r"(ch[01][0-9])_", enc)
    return named.get(enc, m.group(1) if m else "?")


def pairs() -> list[tuple[str, str, str, str]]:
    """(chapter, kind, from cue, to cue) for every hand-over."""
    out: list[tuple[str, str, str, str]] = []
    zones = zone_cues()
    by_loc = {re.sub(r"^res://game/levels/|/[^/]+\.tscn$", "", s): c for s, c in zones.items()}
    for p in A._dlg_files():
        rel = p.relative_to(ROOT).as_posix()
        text = p.read_text(encoding="utf-8")
        loc = re.search(r"(?m)^location:\s*(\S+)", text)
        seq = [m.group(1) for m in re.finditer(r"(?m)^\s*@music\s+([A-Za-z0-9_]+)", text)]
        seq = [c for c in seq if c not in SILENT]
        for a, b in zip(seq, seq[1:]):
            if a != b:
                out.append((chapter_of(rel), f"cutscene ({p.stem})", a, b))
        if seq and loc and by_loc.get(loc.group(1)) and by_loc[loc.group(1)] != seq[-1]:
            out.append((chapter_of(rel), f"cutscene -> field ({p.stem})", seq[-1], by_loc[loc.group(1)]))
    battle = _json(AUDIO / "music.json")["battle"]
    default = battle["default"]
    for s, c in sorted(zones.items()):
        out.append((chapter_of(s), "field <-> battle", c, default))
    for enc, cue in battle.get("encounters", {}).items():
        if A._later(enc):
            continue
        ch = enc_chapter(enc)
        for s, c in sorted(zones.items()):
            if chapter_of(s) == ch:
                out.append((ch, f"field <-> boss ({enc})", c, cue))
    for s, c in sorted(zones.items()):
        out.append((chapter_of(s), "victory -> field", VICTORY, c))
    seen, uniq = set(), []
    for row in out:
        key = (row[1].split(" (")[0], row[2], row[3])
        if key not in seen:
            seen.add(key)
            uniq.append(row)
    return uniq


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", help="write the report as Markdown to this path")
    ap.add_argument("--act", type=int, default=1)
    ap.add_argument("--chapters", default="", help="comma-separated chapters to keep (ch10,ch11)")
    args = ap.parse_args()
    A.set_act(args.act)
    keep = {c.strip() for c in args.chapters.split(",") if c.strip()}
    rows = []
    for ch, kind, a, b in pairs():
        if keep and ch not in keep:
            continue
        la, lb = level(a), level(b)
        d = None if la is None or lb is None else lb - la
        rows.append((ch, kind, a, la, b, lb, d))
    flagged = [r for r in rows if r[6] is not None and abs(r[6]) > STEP_LU]
    missing = sorted({c for r in rows for c, lv in ((r[2], r[3]), (r[4], r[5])) if lv is None})
    lines = ["| Chapter | Hand-over | From | LUFS | To | LUFS | Step (LU) |", "|---|---|---|---|---|---|---|"]
    for ch, kind, a, la, b, lb, d in sorted(rows, key=lambda r: (r[0], r[1], r[2], r[4])):
        f = lambda v: "n/a" if v is None else f"{v:.1f}"  # noqa: E731
        mark = " **over**" if d is not None and abs(d) > STEP_LU else ""
        lines.append(f"| {ch} | {kind} | `{a}` | {f(la)} | `{b}` | {f(lb)} | {f(d)}{mark} |")
    summary = (f"{len(rows)} hand-overs, {len(flagged)} with a step over {STEP_LU:.0f} LU"
               + (f"; no level for: {', '.join(missing)}" if missing else ""))
    if args.md:
        Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    for r in flagged:
        print(f"{r[0]:9} {r[1]:40} {r[2]:26} {r[3]:6.1f} -> {r[4]:26} {r[5]:6.1f}  step {r[6]:+.1f}")
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
