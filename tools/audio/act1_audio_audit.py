#!/usr/bin/env python3
"""Act I audio audit (ADR 0041: Act I at final quality; M3-AUD-861). Lists every silent, temp or reused-placeholder
sound a player can meet from the title through Ch9, from the data the runtime reads (no Godot run):

  zones       every Act I level scene: a music.json zone row and an ambience.json bed (beds that exist for a scene
              but are not wired are flagged)
  enemies     every enemies.json id: creature_voices.json's five events, each row's files on disk, and rows that
              borrow another creature's files (variant_of, or the same file in two creatures' rows)
  skills      every skills.json skill: what BattleVfx plays for it (a skill row, its element, heal, status), and
              so what BattleAudio hears; a skill that does none of those is silent
  cutscenes   every Act I .dlg `@music` / `@sfx` id: a music.json cue, a real file, or a sequencer music_stand_ins
              row (temp), or nothing (silent)
  ui          ui_sfx.json hooks still `pending` (their target class has not landed, so they are silent)
  notes       audio data rows whose own note says stand-in, temp, placeholder, sketch or "no scene yet"

Run: python3 tools/audio/act1_audio_audit.py [--md]   (exit 0; it is a report, not a gate)"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACT1_DIRS = ["prologue"] + [f"ch0{i}" for i in range(1, 10)]
DATA = ROOT / "game" / "data"
AUDIO = DATA / "audio"
TEMP_WORDS = re.compile(r"\b(stand-in|stand in|temp|temporary|placeholder|sketch|no scene yet|no zone yet)\b", re.I)


def _json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _res(path: str) -> Path:
    return ROOT / path.removeprefix("res://")


def act1_scenes() -> list[str]:
    out = []
    for d in ACT1_DIRS:
        for p in sorted((ROOT / "game" / "levels" / d).rglob("*.tscn")):
            if p.stem.endswith("_dressing"):
                continue
            out.append("res://" + p.relative_to(ROOT).as_posix())
    return out


def audit_zones() -> list[str]:
    music = {r["scene"]: r for r in _json(AUDIO / "music.json")["zones"]}
    amb = _json(AUDIO / "ambience.json")
    beds = amb["ambience"]
    zones = amb["zones"]
    out = []
    for s in act1_scenes():
        rel = s.removeprefix("res://")
        miss = [w for w, ok in (("music", s in music and music[s].get("music")), ("ambience bed", s in zones)) if not ok]
        if miss:
            out.append(f"{rel}: no {' and no '.join(miss)}")
    for bid, row in beds.items():
        note = row.get("_note", "")
        if re.search(r"no (zone|scene)", note, re.I) and not any(bid in (z.get("day", []) + z.get("night", []))
                                                                 for z in zones.values()):
            out.append(f"ambience bed `{bid}` is unwired: {note[:110]}")
    return out


def audit_enemies() -> list[str]:
    enemies = _json(DATA / "battle" / "enemies.json")["enemies"]
    ids = list(enemies) if isinstance(enemies, dict) else [r["id"] for r in enemies]
    voices = _json(AUDIO / "creature_voices.json")["creatures"]
    rows = {}
    for p in [AUDIO / "sfx.json"] + sorted(AUDIO.glob("sfx_*.json")):
        rows.update(_json(p).get("sfx", {}))
    owner: dict[str, set] = {}
    out = []
    for cid in ids:
        v = voices.get(cid)
        if v is None:
            out.append(f"{cid}: no creature_voices row (silent in battle)")
            continue
        if not isinstance(v, dict):
            out.append(f"{cid}: creature_voices says `{v}` (no voice, hit or death sound)")
            continue
        if v.get("variant_of"):
            out.append(f"{cid}: borrows {v['variant_of']}'s voice, pitched x{v.get('pitch', 1.0)} (reused)")
            continue
        ev = v.get("events", {})
        for e in ("idle", "attack", "hurt", "death", "move"):
            rid = ev.get(e)
            if not rid:
                out.append(f"{cid}: no `{e}` sound")
                continue
            files = rows.get(rid, {}).get("files", [])
            if not files:
                out.append(f"{cid}.{e}: row `{rid}` has no files")
            for f in files:
                if not _res(f).is_file():
                    out.append(f"{cid}.{e}: {f} is missing")
                owner.setdefault(f, set()).add(cid)
    for f, who in sorted(owner.items()):
        if len(who) > 1:
            out.append(f"{f} is shared by {', '.join(sorted(who))} (reused)")
    return out


def audit_skills() -> list[str]:
    skills = _json(DATA / "battle" / "skills.json")["skills"]
    rows = skills if isinstance(skills, list) else [dict(id=k, **v) for k, v in skills.items()]
    vmap = _json(DATA / "vfx" / "battle" / "effects.json")["map"]
    bsfx = _json(AUDIO / "battle_sfx.json")
    named = "".join(p.read_text(encoding="utf-8") for p in sorted(AUDIO.glob("*.json")))
    named += (DATA / "vfx" / "battle" / "boss_vfx.json").read_text(encoding="utf-8")
    out = []
    for r in rows:
        sid = r["id"]
        if sid in vmap.get("skills", {}) or sid in bsfx.get("skills", {}) or f'"{sid}"' in named:
            continue  # its own row, or a boss telegraph / choreography row names it
        does = (r.get("power", 0) or 0) > 0 or r.get("heal") or r.get("statuses") or r.get("status") \
            or r.get("kind") in ("heal", "revive", "status", "buff", "debuff", "attack", "magic", "physical")
        if not does:
            out.append(f"skill `{sid}` (kind {r.get('kind')}, power {r.get('power')}): no hit, heal or status, "
                       "so nothing but the choreography's accents")
    return out


def _dlg_files() -> list[Path]:
    out = []
    for d in ["game/data/dialogue", "game/cutscene", "game/levels"]:
        out += sorted((ROOT / d).rglob("*.dlg"))
    act1 = []
    for p in out:
        rel = p.relative_to(ROOT).as_posix()
        m = re.search(r"(prologue|ch0[1-9]|slice|act1|vertical)", rel)
        if m:
            act1.append(p)
    return act1


def audit_cutscenes() -> list[str]:
    cues = _json(AUDIO / "music.json")["cues"]
    seq = _json(DATA / "cutscene" / "sequencer.json")
    stand = seq.get("music_stand_ins", {})
    music_dir = str(seq.get("music_dir", "res://assets/audio/music/"))
    rows = {}
    for p in [AUDIO / "sfx.json"] + sorted(AUDIO.glob("sfx_*.json")):
        rows.update(_json(p).get("sfx", {}))
    out, seen = [], set()
    for p in _dlg_files():
        rel = p.relative_to(ROOT).as_posix()
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            m = re.match(r"\s*@(music|sfx)\s+([A-Za-z0-9_]+)", line)
            if not m:
                continue
            kind, cid = m.groups()
            if cid == "silence" or (kind, cid) in seen:
                continue
            seen.add((kind, cid))
            if kind == "music":
                # CutsceneSequencer._music_stream: <music_dir><id>.ogg first, then the stand-in's file
                if _res(music_dir + cid + ".ogg").is_file():
                    continue
                if cid not in stand:
                    out.append(f"{rel}:{i} @music {cid}: no file and no stand-in (silent)")
                    continue
                row = cues.get(cid, {})
                same = row.get("file") == f"{music_dir}{stand[cid]}.ogg"
                if row.get("stems"):
                    out.append(f"{rel}:{i} @music {cid}: a stem cue, so the cutscene plays only `{stand[cid]}` "
                               f"of {len(row['stems'])} stems (partial)")
                elif not same:
                    out.append(f"{rel}:{i} @music {cid} plays `{stand[cid]}`, another piece (temp)")
            else:
                if cid not in rows and not _res(f"res://assets/audio/sfx/{cid}.ogg").is_file() \
                        and not list((ROOT / "assets/audio/sfx").rglob(f"{cid}.ogg")):
                    out.append(f"{rel}:{i} @sfx {cid}: no row and no file (silent)")
    return out


def audit_ui() -> list[str]:
    ui = _json(AUDIO / "ui_sfx.json")
    out = []
    for row in ui.get("hooks") or []:
        if row.get("pending"):
            out.append(f"ui hook `{row.get('class')}` is pending (its class has not landed: silent until it does)")
    return out


def audit_notes() -> list[str]:
    out = []
    for p in sorted(AUDIO.glob("*.json")):
        def walk(o, path):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in ("_note", "note") and isinstance(v, str) and TEMP_WORDS.search(v) \
                            and not re.search(r"act[23]|Act I{2,3}\b|Ch1[0-9]|Ch2[0-9]", v):
                        out.append(f"{p.name}:{path}: {v[:140]}")
                    else:
                        walk(v, f"{path}.{k}" if path else k)
            elif isinstance(o, list):
                for j, v in enumerate(o):
                    walk(v, f"{path}[{j}]")
        walk(_json(p), "")
    return out


SECTIONS = [("Zones", audit_zones), ("Enemies", audit_enemies), ("Skills", audit_skills),
            ("Cutscenes", audit_cutscenes), ("UI", audit_ui), ("Notes that say temp", audit_notes)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--md", action="store_true", help="print as a markdown list")
    args = ap.parse_args()
    total = 0
    for name, fn in SECTIONS:
        items = fn()
        total += len(items)
        print(f"\n## {name} ({len(items)})" if args.md else f"\n{name}: {len(items)}")
        for it in items:
            print(f"- {it}" if args.md else f"  {it}")
    print(f"\n{total} item(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
