"""Act I as-played music pass (M3-AUD-864; the Lead's 10-30 item on 0347aa74): each Act I cutscene's timeline, run
against the cues' real lengths, for the things a player hears as faults:

* **a gap inside a scene:** a one-shot cue runs out while the scene still has lines or waits to play, and no `@music`
  follows for more than GAP_SEC. A scene that silences on purpose says `@music silence`, and that is not a gap;
* **a cut:** an `@music` fade under mix.json min_fade_sec (the deck holds it to the floor anyway; listed here so the
  script can say what it means);
* **a double start:** `@music X` while X is already the scene's cue (the deck leaves it be, so it is only noise).

The scene's time is its `@wait`s plus each spoken line at a reading pace (LINE_BASE_S + chars / CPS), so a gap is a
fair estimate, not a frame count. What happens after a scene (the field, a battle, victory, the next scene) is
AudioDirector's: the zone returns on release (zone_return_sec, test_zone_return.gd), battles start their own cue
(battle_in_sec) and stop it on victory (battle_out_sec), and act1_mix_pass.py measures the loudness of every hand-over.

Run:  python3 tools/audio/act1_playthrough.py [--md docs/kb/audio/act1_playthrough.md]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))

import act1_audio_audit as A  # noqa: E402
import act1_mix_pass as MP  # noqa: E402
from synth.mixer import read_audio  # noqa: E402

GAP_SEC = 3.0
LINE_BASE_S, CPS = 0.8, 14.0
MUSIC = re.compile(r"^\s*@music\s+(\S+)(.*)$")
WAIT = re.compile(r"^\s*@wait\s+([0-9.]+)")
LINE = re.compile(r"^\s*[A-Z][A-Za-z_ ]*(?:\s+as\s+\"[^\"]*\")?\s*(?:\[[^\]]*\])?:\s*(.+?)\s*(?:#line:.*)?$")


def _json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def cue_info(cid: str) -> tuple[bool, float] | None:
    """(loops, seconds) for a cue as the deck plays it; None if it has no file."""
    got = MP.cue_files(cid)
    if not got or not all(p.is_file() for p in got[0]):
        return None
    p = got[0][0]
    imp = Path(str(p) + ".import")
    loops = "stems" in (_json(ROOT / "game/data/audio/music.json")["cues"].get(cid) or {}) or (
        imp.is_file() and "loop=true" in imp.read_text(encoding="utf-8")) or Path(str(p)[:-4] + ".loop.json").is_file()
    return loops, len(read_audio(str(p), channels=1)) / 44100.0


def scan(path: Path, min_fade: float) -> list[str]:
    out: list[str] = []
    t = 0.0
    cur, cur_at, cur_end = "", 0.0, None
    rel = path.relative_to(ROOT).as_posix()
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = MUSIC.match(raw)
        if m:
            cid, rest = m.group(1), m.group(2)
            fm = re.search(r"fade=([0-9.]+)", rest)
            if fm and float(fm.group(1)) < min_fade:
                out.append(f"{rel}:{i} `@music {cid} fade={fm.group(1)}`: under min_fade_sec {min_fade} (the deck "
                           f"plays it as a {min_fade} s fade)")
            if cur_end is not None and t - cur_end > GAP_SEC:
                out.append(f"{rel}:{i} gap: `{cur}` ran out about {t - cur_end:.0f} s before this `@music` "
                           f"(from ~{cur_end:.0f} s to ~{t:.0f} s into the scene)")
            if cid == cur and cid != "silence" and "stem=" not in rest:  # a stem change is meant
                out.append(f"{rel}:{i} `@music {cid}` again: it is already the scene's cue (the deck leaves it be)")
            info = None if cid == "silence" else cue_info(cid)
            cur, cur_at = cid, t
            cur_end = (t + info[1]) if info is not None and not info[0] else None
            continue
        w = WAIT.match(raw)
        if w:
            t += float(w.group(1))
            continue
        ln = LINE.match(raw)
        if ln and not raw.lstrip().startswith(("@", "<<", "//", "title:", "location:", "---", "===")):
            t += LINE_BASE_S + len(ln.group(1)) / CPS
    if cur_end is not None and t - cur_end > GAP_SEC:
        out.append(f"{rel}: end: `{cur}` ran out about {t - cur_end:.0f} s before the scene ends (~{t:.0f} s); "
                   f"the zone returns on release (zone_return_sec)")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md")
    ap.add_argument("--act", type=int, default=1)
    args = ap.parse_args()
    A.set_act(args.act)
    mix = _json(ROOT / "game/data/audio/mix.json")["music"]
    rows: list[str] = []
    for p in A._dlg_files():
        if "@music" in p.read_text(encoding="utf-8"):
            rows += scan(p, float(mix.get("min_fade_sec", 0.2)))
    for r in rows:
        print(r)
    print(f"{len(rows)} item(s)")
    if args.md:
        Path(args.md).write_text("\n".join(f"- {r}" for r in rows) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.exit(main())
