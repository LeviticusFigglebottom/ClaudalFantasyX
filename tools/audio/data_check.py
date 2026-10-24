"""Checks for the game's audio tables (M2-AUD-02; docs/kb/tech/audio_runtime.md).

tools/validate_data.py calls `audio_errors()` for game/data/audio/*.json: every file, bus, cue, bed, zone scene,
flag, encounter and VFX effect a table names must exist, and every sound another table names must be a row of
sfx.json. Pure functions over the parsed JSON plus an `exists(res_path)` callback, so the tests feed fixtures.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

MIX = "game/data/audio/mix.json"
MUSIC = "game/data/audio/music.json"
SFX_DIR = "game/data/audio/"
SFX = "game/data/audio/sfx.json"
BATTLE_SFX = "game/data/audio/battle_sfx.json"
SHRINE_SFX = "game/data/audio/shrine_sfx.json"
UI_SFX = "game/data/audio/ui_sfx.json"
AMBIENCE = "game/data/audio/ambience.json"
FOOTSTEPS = "game/data/audio/footsteps.json"
CLASSES = "@classes"  # load_files: {global class name: [its declared signals]} from game/**/*.gd
NODE_SIGNALS = {"ready", "tree_entered", "tree_exiting", "tree_exited", "visibility_changed", "hidden",
                "draw", "resized", "focus_entered", "focus_exited"}
ENCOUNTERS = "game/data/battle/encounters.json"
VFX_EFFECTS = "game/data/vfx/battle/effects.json"
SILENCE = "silence"
AUDIO_EXT = (".ogg", ".wav")


def _num(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _res_file(v: object, exists: Callable[[str], bool], w: str, errs: list[str], exts=AUDIO_EXT) -> None:
    if not isinstance(v, str) or not v.startswith("res://") or not v.endswith(exts):
        errs.append(f"{w}: must be a res:// path ending in {'/'.join(exts)}")
    elif not exists(v):
        errs.append(f"{w}: {v} does not exist")


def mix_errors(mix: object) -> tuple[list[str], set[str]]:
    errs: list[str] = []
    buses = {"Master"}
    if not isinstance(mix, dict):
        return [f"{MIX}: must be an object"], buses
    for i, row in enumerate(mix.get("buses", [])):
        w = f"{MIX} buses[{i}]"
        if not isinstance(row, dict) or not isinstance(row.get("name"), str) or not row["name"]:
            errs.append(f"{w}: needs a name")
            continue
        if row["name"] in buses:
            errs.append(f"{w}: bus {row['name']} is defined twice")
        if row.get("send", "Master") not in buses:
            errs.append(f"{w}: sends to {row.get('send')}, which is not a bus defined before it")
        buses.add(row["name"])
    for reason, row in (mix.get("ducks") or {}).items():
        w = f"{MIX} ducks.{reason}"
        if not isinstance(row, dict) or not _num(row.get("sec")) or row["sec"] < 0:
            errs.append(f"{w}.sec: must be a number >= 0")
            continue
        for bus, db in (row.get("buses") or {}).items():
            if bus not in buses:
                errs.append(f"{w}.buses: unknown bus {bus}")
            if not _num(db) or db > 0:
                errs.append(f"{w}.buses.{bus}: a duck is a number of dB <= 0")
    for k, v in (mix.get("music") or {}).items():
        if not _num(v):
            errs.append(f"{MIX} music.{k}: must be a number")
    return errs, buses


def _cue_errors(cid: str, row: object, w: str, exists, errs: list[str]) -> int:
    """Returns the cue's stem count (1 for a single file, 0 when broken)."""
    if not isinstance(row, dict):
        errs.append(f"{w}: must be an object")
        return 0
    if ("file" in row) == ("stems" in row):
        errs.append(f"{w}: needs exactly one of file or stems")
        return 0
    if "file" in row:
        _res_file(row["file"], exists, f"{w}.file", errs)
        return 1
    stems = row["stems"]
    if not isinstance(stems, list) or len(stems) < 2:
        errs.append(f"{w}.stems: at least two files")
        return 0
    for j, f in enumerate(stems):
        _res_file(f, exists, f"{w}.stems[{j}]", errs)
    for j in row.get("start_stems", [0]):
        if not isinstance(j, int) or not 0 <= j < len(stems):
            errs.append(f"{w}.start_stems: {j} is not a stem index")
    return len(stems)


def music_errors(music: object, exists, flags: set[str], encounters: set[str],
                 extra_beds: frozenset = frozenset()) -> tuple[list[str], dict[str, int]]:
    errs: list[str] = []
    if not isinstance(music, dict):
        return [f"{MUSIC}: must be an object"], {}
    cues: dict[str, int] = {}
    for cid, row in (music.get("cues") or {}).items():
        cues[cid] = _cue_errors(cid, row, f"{MUSIC} cues.{cid}", exists, errs)
    beds = set(extra_beds)
    for bid, row in (music.get("ambience") or {}).items():
        _cue_errors(bid, row, f"{MUSIC} ambience.{bid}", exists, errs)
        beds.add(bid)
    seen: set[str] = set()

    def keys(row: dict, w: str) -> None:
        m = row.get("music")
        if m is not None and m != SILENCE and m not in cues:
            errs.append(f"{w}.music: unknown cue {m}")
        for a in row.get("ambience", []):
            if a not in beds:
                errs.append(f"{w}.ambience: unknown bed {a}")

    for i, row in enumerate(music.get("zones", [])):
        w = f"{MUSIC} zones[{i}]"
        scene = row.get("scene") if isinstance(row, dict) else None
        if not isinstance(scene, str) or not scene.startswith("res://") or not scene.endswith(".tscn"):
            errs.append(f"{w}.scene: must be a res://...tscn path")
            continue
        if scene in seen:
            errs.append(f"{w}.scene: {scene} has two rows")
        seen.add(scene)
        if not exists(scene):
            errs.append(f"{w}.scene: {scene} does not exist")
        keys(row, w)
        for j, v in enumerate(row.get("variants", [])):
            if not isinstance(v, dict) or v.get("flag") not in flags:
                errs.append(f"{w}.variants[{j}].flag: {v.get('flag') if isinstance(v, dict) else v} is not declared")
                continue
            keys(v, f"{w}.variants[{j}]")
    battle = music.get("battle") or {}
    if battle.get("default") not in cues:
        errs.append(f"{MUSIC} battle.default: unknown cue {battle.get('default')}")
    for enc, cid in (battle.get("encounters") or {}).items():
        if enc not in encounters:
            errs.append(f"{MUSIC} battle.encounters: unknown encounter {enc}")
        if cid not in cues:
            errs.append(f"{MUSIC} battle.encounters.{enc}: unknown cue {cid}")
    most = max(cues.values(), default=0)
    for ph, row in (battle.get("phases") or {}).items():
        for k in ("stems_on", "stems_off"):
            for j in row.get(k, []):
                if not isinstance(j, int) or not 0 <= j < most:
                    errs.append(f"{MUSIC} battle.phases.{ph}.{k}: {j} is no cue's stem")
    return errs, cues


def sfx_errors(sfx: object, exists, buses: set[str]) -> tuple[list[str], set[str]]:
    errs: list[str] = []
    if not isinstance(sfx, dict):
        return [f"{SFX}: must be an object"], set()
    ids = set()
    for sid in sfx.get("_dupes", []):
        errs.append(f"{SFX}: row {sid} is defined in two sfx files")
    for sid, row in (sfx.get("sfx") or {}).items():
        w = f"{SFX} sfx.{sid}"
        ids.add(sid)
        if not isinstance(row, dict) or not isinstance(row.get("files"), list) or not row["files"]:
            errs.append(f"{w}.files: at least one file")
            continue
        for j, f in enumerate(row["files"]):
            _res_file(f, exists, f"{w}.files[{j}]", errs)
        if row.get("bus", "SFX") not in buses:
            errs.append(f"{w}.bus: unknown bus {row.get('bus')}")
        for k in ("volume_db", "pitch_jitter", "cooldown_ms", "voices", "unit_size_m"):
            if k in row and not _num(row[k]):
                errs.append(f"{w}.{k}: must be a number")
        if not 0 <= row.get("pitch_jitter", 0) < 0.5:
            errs.append(f"{w}.pitch_jitter: 0 <= jitter < 0.5")
    return errs, ids


def _refs(doc: object, path: str, ids: set[str], errs: list[str]) -> None:
    """Every string value under a `sfx`/section key of a hook table must be an sfx.json row."""
    def walk(v: object, w: str) -> None:
        if isinstance(v, dict):
            for k, x in v.items():
                if k == "doc" or k.startswith("_"):
                    continue
                walk(x, f"{w}.{k}")
        elif isinstance(v, list):
            for j, x in enumerate(v):
                walk(x, f"{w}[{j}]")
        elif isinstance(v, str) and v not in ids:
            errs.append(f"{w}: {v} is not an sfx.json row")
    walk(doc, path)


def hook_errors(name: str, doc: object, ids: set[str], vfx_effects: set[str]) -> list[str]:
    errs: list[str] = []
    if not isinstance(doc, dict):
        return [f"{name}: must be an object"]
    body = {k: v for k, v in doc.items() if k not in ("doc", "version") and not k.startswith("_")}
    numbers = {k: v for k, v in body.items() if _num(v)}
    for k in numbers:
        body.pop(k)
    _refs(body, name, ids, errs)
    if name == BATTLE_SFX:
        for eid in (doc.get("vfx") or {}):
            if eid not in vfx_effects:
                errs.append(f"{name} vfx.{eid}: not a BattleVfx effect")
        for eid in vfx_effects:
            if eid not in (doc.get("vfx") or {}):
                errs.append(f"{name} vfx: effect {eid} has no sound")
        for sid in (doc.get("reduced") or {}):
            if sid not in ids:
                errs.append(f"{name} reduced.{sid}: {sid} is not an sfx.json row")
    return errs


def ambience_errors(doc: object, exists, flags: set[str], buses: set[str], music_beds: set[str]) -> list[str]:
    """ambience.json (M2-AUD-05): its beds, the zones' bed lists, night flags, and the wind mapping."""
    if not isinstance(doc, dict):
        return [f"{AMBIENCE}: must be an object"]
    errs: list[str] = []
    beds = set(music_beds)
    for bid, row in (doc.get("ambience") or {}).items():
        w = f"{AMBIENCE} ambience.{bid}"
        _cue_errors(bid, row, w, exists, errs)
        beds.add(bid)
        if isinstance(row, dict) and row.get("bus", "Ambience") not in buses:
            errs.append(f"{w}.bus: unknown bus {row.get('bus')}")
        if isinstance(row, dict) and not _num(row.get("volume_db", 0)):
            errs.append(f"{w}.volume_db: must be a number")
    wind = doc.get("wind") or {}
    if wind:
        if wind.get("bed") not in beds:
            errs.append(f"{AMBIENCE} wind.bed: unknown bed {wind.get('bed')}")
        if not all(_num(wind.get(k)) for k in ("min_m_s", "max_m_s", "min_db", "max_db")):
            errs.append(f"{AMBIENCE} wind: min_m_s, max_m_s, min_db and max_db must be numbers")
        elif wind["min_m_s"] >= wind["max_m_s"]:
            errs.append(f"{AMBIENCE} wind: min_m_s must be below max_m_s")
    for scene, row in (doc.get("zones") or {}).items():
        w = f"{AMBIENCE} zones.{scene}"
        if not scene.startswith("res://") or not scene.endswith(".tscn"):
            errs.append(f"{w}: the key must be a res://...tscn path")
        elif not exists(scene):
            errs.append(f"{w}: {scene} does not exist")
        if not isinstance(row, dict):
            errs.append(f"{w}: must be an object")
            continue
        for k in ("day", "night"):
            for b in row.get(k, []):
                if b not in beds:
                    errs.append(f"{w}.{k}: unknown bed {b}")
        if "night" in row and row.get("night_flag") not in flags:
            errs.append(f"{w}.night_flag: {row.get('night_flag')} is not declared")
        if row.get("wind") and not wind:
            errs.append(f"{w}.wind: the table has no wind row")
    return errs


def footstep_errors(doc: object, exists, ids: set[str]) -> list[str]:
    """footsteps.json (M2-AUD-05): surfaces name sfx rows, scenes exist and name surfaces, strides are positive."""
    if not isinstance(doc, dict):
        return [f"{FOOTSTEPS}: must be an object"]
    errs: list[str] = []
    surfaces = doc.get("surfaces") or {}
    for surf, sid in surfaces.items():
        if sid not in ids:
            errs.append(f"{FOOTSTEPS} surfaces.{surf}: {sid} is not an sfx.json row")
    if doc.get("default") not in surfaces:
        errs.append(f"{FOOTSTEPS} default: {doc.get('default')} is not a surface")
    for scene, surf in (doc.get("scenes") or {}).items():
        if not exists(scene):
            errs.append(f"{FOOTSTEPS} scenes: {scene} does not exist")
        if surf not in surfaces:
            errs.append(f"{FOOTSTEPS} scenes.{scene}: {surf} is not a surface")
    for k in ("walk_step_m", "run_step_m"):
        if not _num(doc.get(k)) or doc[k] <= 0:
            errs.append(f"{FOOTSTEPS} {k}: a stride is a number > 0")
    return errs


def ui_hook_errors(doc: object, ids: set[str], classes: dict[str, list[str]] | None) -> list[str]:
    """ui_sfx.json (M2-AUD-05): hooks by class name. Class and signal names are checked against the game's scripts
    (unless the hook is `pending`), and only the sound fields are sfx rows."""
    if not isinstance(doc, dict):
        return [f"{UI_SFX}: must be an object"]
    errs: list[str] = []

    def row(v: object, w: str) -> None:
        if v not in ids:
            errs.append(f"{w}: {v} is not an sfx.json row")

    for j, sid in enumerate(doc.get("priority", [])):
        row(sid, f"{UI_SFX} priority[{j}]")
    seen: set[str] = set()
    for i, h in enumerate(doc.get("hooks", [])):
        w = f"{UI_SFX} hooks[{i}]"
        if not isinstance(h, dict) or not isinstance(h.get("class"), str) or not h["class"]:
            errs.append(f"{w}.class: needs a class name")
            continue
        cls = h["class"]
        if cls in seen:
            errs.append(f"{w}.class: {cls} has two hooks")
        seen.add(cls)
        known = classes is not None and not h.get("pending", False)
        if known and cls not in classes:
            errs.append(f"{w}.class: no script declares class_name {cls} (mark the hook pending until it lands)")
            known = False
        for sig, sid in (h.get("signals") or {}).items():
            row(sid, f"{w}.signals.{sig}")
            if known and sig not in classes[cls] and sig not in NODE_SIGNALS:
                errs.append(f"{w}.signals.{sig}: {cls} declares no such signal")
        for k in ("on_enter", "on_exit"):
            if k in h:
                row(h[k], f"{w}.{k}")
        for j, x in enumerate(h.get("watch", [])):
            ww = f"{w}.watch[{j}]"
            if not isinstance(x, dict) or not isinstance(x.get("expr"), str) or not x["expr"]:
                errs.append(f"{ww}.expr: needs an expression")
                continue
            sounds = [x[k] for k in ("sfx", "rise", "fall") if k in x] + list((x.get("values") or {}).values())
            if not sounds:
                errs.append(f"{ww}: plays nothing (needs sfx, rise, fall or values)")
            for sid in sounds:
                row(sid, ww)
    return errs


def audio_errors(files: dict[str, object], exists: Callable[[str], bool], flags: set[str]) -> list[str]:
    errs, buses = mix_errors(files.get(MIX))
    enc_doc = files.get(ENCOUNTERS) or {}
    encounters = {e.get("id") for e in enc_doc.get("encounters", []) if isinstance(e, dict)}
    amb = files.get(AMBIENCE) or {}
    amb_beds = frozenset((amb.get("ambience") or {}).keys()) if isinstance(amb, dict) else frozenset()
    e2, _ = music_errors(files.get(MUSIC), exists, flags, encounters, amb_beds)
    e3, ids = sfx_errors(merged_sfx(files), exists, buses)
    errs += e2 + e3
    if AMBIENCE in files:
        music_beds = set(((files.get(MUSIC) or {}).get("ambience") or {}).keys())
        errs += ambience_errors(files[AMBIENCE], exists, flags, buses, music_beds)
    if FOOTSTEPS in files:
        errs += footstep_errors(files[FOOTSTEPS], exists, ids)
    vfx_effects = set(((files.get(VFX_EFFECTS) or {}).get("effects") or {}).keys())
    for name in (BATTLE_SFX, SHRINE_SFX):
        if name in files:
            errs += hook_errors(name, files[name], ids, vfx_effects)
    if UI_SFX in files:
        errs += ui_hook_errors(files[UI_SFX], ids, files.get(CLASSES))
    return errs


def merged_sfx(files: dict[str, object]) -> dict:
    """sfx.json plus every sfx_<domain>.json (the runtime's AudioData.sfx_rows). A row in two files is an error."""
    rows: dict = {}
    dupes: list[str] = []
    for rel in [SFX] + sorted(k for k in files if k.startswith(SFX_DIR + "sfx_")):
        for sid, row in ((files.get(rel) or {}).get("sfx") or {}).items():
            if sid in rows:
                dupes.append(sid)
            rows[sid] = row
    out: dict = {"sfx": rows}
    if dupes:
        out["_dupes"] = dupes
    return out


def load_files(root: Path) -> dict[str, object]:
    out = {}
    extra = [str(p.relative_to(root)) for p in sorted((root / SFX_DIR).glob("sfx_*.json"))]
    for rel in [MIX, MUSIC, SFX, BATTLE_SFX, SHRINE_SFX, UI_SFX, AMBIENCE, FOOTSTEPS, ENCOUNTERS, VFX_EFFECTS] + extra:
        p = root / rel
        if p.is_file():
            out[rel] = json.loads(p.read_text(encoding="utf-8"))
    out[CLASSES] = script_classes(root)
    return out


def script_classes(root: Path) -> dict[str, list[str]]:
    """{class_name: [declared signals]} for every script under game/ (ui_sfx.json hooks name classes and signals)."""
    import re

    out: dict[str, list[str]] = {}
    for p in sorted((root / "game").rglob("*.gd")):
        text = p.read_text(encoding="utf-8")
        m = re.search(r"(?m)^class_name\s+(\w+)", text)
        if m:
            out[m.group(1)] = re.findall(r"(?m)^signal\s+(\w+)", text)
    return out
