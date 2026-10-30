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
FOOTSTEP_KINDS = ("walk", "run", "stop", "turn")  # M3-AUD-802: a surface's rows
VOICES = "game/data/audio/voices.json"  # M3-AUD-07
REEFBALL_HOOKS = "game/data/audio/reefball_hooks.json"  # M3-AUD-17
CHOREO_SFX = "game/data/audio/choreo_sfx.json"  # M3-AUD-13
BATTLE_STINGS = "game/data/audio/battle_stings.json"  # M3-AUD-18
LIFE = "game/data/audio/life.json"  # M3-AUD-814
IMPACT = "game/data/audio/impact_audio.json"  # M3-AUD-816
CUTSCENE_FOLEY = "game/data/audio/cutscene_foley.json"  # M3-AUD-817
ASHCROWN_SFX = "game/data/audio/ashcrown_sfx.json"  # M3-AUD-825
CHOREO = "game/data/battle/choreo.json"  # the battle-presentation track's styles (once merged)
SPEAKERS = "game/data/dialogue/speakers.json"
CREATURE_VOICES = "game/data/audio/creature_voices.json"  # M3-AUD-14
ENEMIES = "game/data/battle/enemies.json"
CLASSES = "@classes"  # load_files: {global class name: [its declared signals]} from game/**/*.gd
NODE_SIGNALS = {"ready", "tree_entered", "tree_exiting", "tree_exited", "visibility_changed", "hidden",
                "draw", "resized", "focus_entered", "focus_exited"}
ENCOUNTERS = "game/data/battle/encounters.json"
ACCESSIBILITY = "game/data/ui/accessibility.json"
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
    for k, v in (mix.get("volume_settings") or {}).items():
        if not isinstance(v, list) or not v or any(b not in buses for b in v):
            errs.append(f"{MIX} volume_settings.{k}: a non-empty list of buses ({v})")
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
    pending = set(battle.get("pending_encounters") or [])
    for enc in sorted(pending & set(encounters)):
        errs.append(f"{MUSIC} battle.pending_encounters: {enc} exists now, take it off the list")
    for enc, cid in (battle.get("encounters") or {}).items():
        if enc not in encounters and enc not in pending:  # pending: a planned fight combat has not written yet
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
    if name == ASHCROWN_SFX:
        body.pop("at", None)  # node paths under the zone, not sfx rows
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


def _arena_ids() -> set[str] | None:
    """The battle arena ids (game/data/battle/arenas.json scenes), or None when the file can't be read."""
    try:
        with open(Path(__file__).resolve().parents[2] / "game/data/battle/arenas.json", encoding="utf-8") as f:
            return set(json.load(f)["arenas"]["scenes"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _encounter_ids() -> set[str] | None:
    """The encounters.json ids, or None when the file can't be read."""
    try:
        with open(Path(__file__).resolve().parents[2] / "game/data/battle/encounters.json", encoding="utf-8") as f:
            doc = json.load(f)
        rows = doc.get("encounters", doc) if isinstance(doc, dict) else doc
        return {str(r["id"]) for r in rows}
    except (OSError, ValueError, KeyError, TypeError):
        return None


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
    arenas = _arena_ids()
    for arena, ids in (doc.get("arenas") or {}).items():
        w = f"{AMBIENCE} arenas.{arena}"
        if arenas is not None and arena not in arenas:
            errs.append(f"{w}: not an arenas.json arena")
        if not isinstance(ids, list) or not ids:
            errs.append(f"{w}: must be a non-empty list of beds")
            continue
        for b in ids:
            if b not in beds:
                errs.append(f"{w}: unknown bed {b}")
    encs = _encounter_ids()
    pending = set(doc.get("pending_encounters") or [])
    for enc, ids in (doc.get("encounters") or {}).items():
        w = f"{AMBIENCE} encounters.{enc}"
        if encs is not None and enc not in encs and enc not in pending:
            # pending_encounters: a set piece planned in its chapter doc that combat has not written yet
            errs.append(f"{w}: not an encounters.json encounter (or listed in pending_encounters)")
        if not isinstance(ids, list) or not ids:
            errs.append(f"{w}: must be a non-empty list of beds")
            continue
        for b in ids:
            if b not in beds:
                errs.append(f"{w}: unknown bed {b}")
    if "arena_fade_sec" in doc and not (_num(doc["arena_fade_sec"]) and doc["arena_fade_sec"] >= 0):
        errs.append(f"{AMBIENCE} arena_fade_sec: must be a number at or above 0")
    for scene, row in (doc.get("zones") or {}).items():
        w = f"{AMBIENCE} zones.{scene}"
        if not scene.startswith("res://") or not scene.endswith(".tscn"):
            errs.append(f"{w}: the key must be a res://...tscn path")
        elif not exists(scene) and not (isinstance(row, dict) and row.get("pending")):
            # "pending": true marks a zone whose scene is on another track's branch (M3-AUD-16): its beds go live
            # when the scene merges; everything else in the row is still checked.
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
        if isinstance(sid, dict):  # M3-AUD-802: {walk, run, stop, turn}; walk and run are required
            for kind in ("walk", "run"):
                if kind not in sid:
                    errs.append(f"{FOOTSTEPS} surfaces.{surf}: no {kind} row")
            for kind, rid in sid.items():
                if kind not in FOOTSTEP_KINDS:
                    errs.append(f"{FOOTSTEPS} surfaces.{surf}.{kind}: not one of {', '.join(FOOTSTEP_KINDS)}")
                elif rid not in ids:
                    errs.append(f"{FOOTSTEPS} surfaces.{surf}.{kind}: {rid} is not an sfx.json row")
        elif sid not in ids:
            errs.append(f"{FOOTSTEPS} surfaces.{surf}: {sid} is not an sfx.json row")
    foley = doc.get("foley") or {}
    for key in ("cloth", "gear"):
        for k, rid in (foley.get(key) or {}).items():
            if rid not in ids:
                errs.append(f"{FOOTSTEPS} foley.{key}.{k}: {rid} is not an sfx.json row")
    if foley and (not isinstance(foley.get("gear_every", 1), int) or foley.get("gear_every", 1) < 1):
        errs.append(f"{FOOTSTEPS} foley.gear_every: a whole number >= 1")
    contacts = doc.get("contacts") or {}
    if contacts and not all(isinstance(m, str) and m for m in contacts.get("markers", [])):
        errs.append(f"{FOOTSTEPS} contacts.markers: marker names are non-empty strings")
    for k in ("min_interval_sec", "stall_m", "retry_sec", "min_weight"):
        if k in contacts and (not _num(contacts[k]) or contacts[k] < 0):
            errs.append(f"{FOOTSTEPS} contacts.{k}: a number >= 0")
    areas = doc.get("surface_areas") or {}
    if areas and not (areas.get("group") or areas.get("group_prefix")):
        errs.append(f"{FOOTSTEPS} surface_areas: needs group or group_prefix")
    meshes = doc.get("mesh_surfaces") or {}  # M3-AUD-812
    for j, rule in enumerate(meshes.get("rules", [])):
        w = f"{FOOTSTEPS} mesh_surfaces.rules[{j}]"
        if rule.get("surface") not in surfaces:
            errs.append(f"{w}: {rule.get('surface')} is not a surface")
        pats = rule.get("match")
        if not isinstance(pats, list) or not pats or not all(isinstance(p, str) and p for p in pats):
            errs.append(f"{w}.match: a non-empty list of name patterns")
        for k in ("up_m", "down_m"):
            if k in rule and (not _num(rule[k]) or rule[k] < 0):
                errs.append(f"{w}.{k}: a number >= 0")
    water = doc.get("water_level") or {}
    if water:
        if water.get("surface") not in surfaces:
            errs.append(f"{FOOTSTEPS} water_level.surface: {water.get('surface')} is not a surface")
        if not water.get("group"):
            errs.append(f"{FOOTSTEPS} water_level: needs group")
        for k in ("wade_m", "above_m"):
            if not _num(water.get(k)) or water[k] < 0:
                errs.append(f"{FOOTSTEPS} water_level.{k}: a number >= 0")
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
    mo = doc.get("motion")
    if mo is not None:  # M3-AUD-832: the menu motion whooshes
        if not isinstance(mo, dict) or not isinstance(mo.get("accessor"), str) or not mo["accessor"]:
            errs.append(f"{UI_SFX} motion: an object with an accessor (the method returning a node's MenuMotion)")
        else:
            for k in ("in", "out"):
                row(mo.get(k), f"{UI_SFX} motion.{k}")
    return errs


LIFE_KINDS = ("villager", "wildlife")


def life_errors(doc: object, ids: set[str], classes: dict[str, list[str]] | None) -> list[str]:
    """life.json (M3-AUD-814): hooks name a kind and a real class (unless pending); every row it plays is an sfx row;
    every [min, max] interval is positive."""
    if not isinstance(doc, dict):
        return [f"{LIFE}: must be an object"]
    errs: list[str] = []
    for j, h in enumerate(doc.get("hooks", [])):
        w = f"{LIFE} hooks[{j}]"
        if not isinstance(h, dict) or not isinstance(h.get("class"), str) or not h["class"]:
            errs.append(f"{w}.class: needs a class name")
            continue
        if h.get("kind") not in LIFE_KINDS:
            errs.append(f"{w}.kind: one of {', '.join(LIFE_KINDS)}")
        if classes is not None and not h.get("pending", False) and h["class"] not in classes:
            errs.append(f"{w}.class: no script declares class_name {h['class']} (mark the hook pending until it lands)")

    def row(v: object, w: str) -> None:
        if v not in ids:
            errs.append(f"{w}: {v} is not an sfx row")

    def interval(v: object, w: str) -> None:
        if not (isinstance(v, list) and len(v) == 2 and all(_num(x) and x > 0 for x in v) and v[0] <= v[1]):
            errs.append(f"{w}: a [min, max] pair of seconds > 0")

    vil = doc.get("villager") or {}
    for k, rid in (vil.get("murmur") or {}).items():
        row(rid, f"{LIFE} villager.murmur.{k}")
    for npc, voice in (vil.get("voices") or {}).items():
        if voice not in (vil.get("murmur") or {}):
            errs.append(f"{LIFE} villager.voices.{npc}: {voice} is not a murmur voice")
    work = vil.get("work") or {}
    for npc, rid in (work.get("rows") or {}).items():
        row(rid, f"{LIFE} villager.work.rows.{npc}")
    if work:
        interval(work.get("every_sec"), f"{LIFE} villager.work.every_sec")
    wild = doc.get("wildlife") or {}
    for kind, keys in (("gull", ("call", "takeoff")), ("crab", ("scuttle",)), ("fish", ("dart",))):
        cfg = wild.get(kind) or {}
        for k in keys:
            if k in cfg:
                row(cfg[k], f"{LIFE} wildlife.{kind}.{k}")
    if "call_every_sec" in (wild.get("gull") or {}):
        interval(wild["gull"]["call_every_sec"], f"{LIFE} wildlife.gull.call_every_sec")
    return errs


def cutscene_foley_errors(doc: object, ids: set[str]) -> list[str]:
    """cutscene_foley.json (M3-AUD-817): every anim, light and vfx row is an sfx row ('' silences an anim clip), and a
    light row names on and off."""
    if not isinstance(doc, dict):
        return [f"{CUTSCENE_FOLEY}: must be an object"]
    errs: list[str] = []
    for kind in ("anim", "vfx"):
        for k, rid in (doc.get(kind) or {}).items():
            if not (rid == "" and kind == "anim") and rid not in ids:
                errs.append(f"{CUTSCENE_FOLEY} {kind}.{k}: {rid} is not an sfx row")
    for k, row in (doc.get("light") or {}).items():
        if not isinstance(row, dict) or set(row) != {"on", "off"}:
            errs.append(f"{CUTSCENE_FOLEY} light.{k}: needs on and off")
            continue
        for state, rid in row.items():
            if rid not in ids:
                errs.append(f"{CUTSCENE_FOLEY} light.{k}.{state}: {rid} is not an sfx row")
    lamps = doc.get("lamps")  # M3-AUD-847: lit lamps crackle at the lamp
    if lamps is not None:
        if not isinstance(lamps, dict) or lamps.get("row") not in ids or not lamps.get("match"):
            errs.append(f"{CUTSCENE_FOLEY} lamps: needs match (light names) and row (an sfx row)")
        gap = lamps.get("every_sec") if isinstance(lamps, dict) else None
        if not (isinstance(gap, list) and len(gap) == 2 and all(_num(v) and v > 0 for v in gap) and gap[0] <= gap[1]):
            errs.append(f"{CUTSCENE_FOLEY} lamps.every_sec: [min, max] seconds > 0")
    return errs


def impact_errors(doc: object, ids: set[str], classes: dict[str, list[str]] | None, mix: object) -> list[str]:
    """impact_audio.json (M3-AUD-816): a real hook class (unless pending), sfx rows for every tier and the slow-mo,
    tiers in rising order, and ducks that mix.json defines."""
    if not isinstance(doc, dict):
        return [f"{IMPACT}: must be an object"]
    errs: list[str] = []
    for j, h in enumerate(doc.get("hooks", [])):
        w = f"{IMPACT} hooks[{j}]"
        if not isinstance(h, dict) or not isinstance(h.get("class"), str) or not h["class"]:
            errs.append(f"{w}.class: needs a class name")
            continue
        if classes is not None and not h.get("pending", False):
            if h["class"] not in classes:
                errs.append(f"{w}.class: no script declares class_name {h['class']} (mark the hook pending until it lands)")
            else:
                for role, sig in (h.get("signals") or {}).items():
                    if sig not in classes[h["class"]]:
                        errs.append(f"{w}.signals.{role}: {h['class']} declares no signal {sig}")
    last = -1.0
    for j, tier in enumerate(doc.get("tiers", [])):
        w = f"{IMPACT} tiers[{j}]"
        lo = tier.get("min_strength") if isinstance(tier, dict) else None
        if not _num(lo) or not 0 < lo <= 1 or lo <= last:
            errs.append(f"{w}.min_strength: rising, in (0, 1]")
        else:
            last = lo
        if not isinstance(tier, dict) or tier.get("sfx") not in ids:
            errs.append(f"{w}.sfx: not an sfx row")
    ducks = (mix or {}).get("ducks") or {} if isinstance(mix, dict) else {}
    for key in ("hitstop", "slowmo"):
        cfg = doc.get(key) or {}
        if "sfx" in cfg and cfg["sfx"] not in ids:
            errs.append(f"{IMPACT} {key}.sfx: {cfg['sfx']} is not an sfx row")
        if cfg.get("duck") and cfg["duck"] not in ducks:
            errs.append(f"{IMPACT} {key}.duck: {cfg['duck']} is not a mix.json duck")
    for rid in doc.get("reduced_skip", []):
        if rid not in ids:
            errs.append(f"{IMPACT} reduced_skip: {rid} is not an sfx row")
    return errs


def audio_errors(files: dict[str, object], exists: Callable[[str], bool], flags: set[str]) -> list[str]:
    errs, buses = mix_errors(files.get(MIX))
    acc = ((files.get(ACCESSIBILITY) or {}).get("accessibility") or {}).get("settings", [])
    acc_ids = {r.get("id") for r in acc if isinstance(r, dict)}
    for k in ((files.get(MIX) or {}).get("volume_settings") or {}):
        if ACCESSIBILITY in files and k not in acc_ids:
            errs.append(f"{MIX} volume_settings.{k}: not a setting in {ACCESSIBILITY}")
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
    for name in (BATTLE_SFX, SHRINE_SFX, ASHCROWN_SFX):
        if name in files:
            errs += hook_errors(name, files[name], ids, vfx_effects)
    if UI_SFX in files:
        errs += ui_hook_errors(files[UI_SFX], ids, files.get(CLASSES))
    errs += reverb_errors(files.get(MIX), files.get(MUSIC), buses)
    if VOICES in files:
        rows = merged_sfx(files).get("sfx") or {}
        errs += voice_errors(files[VOICES], files.get(SPEAKERS), rows)
    if CHOREO_SFX in files:
        errs += choreo_errors(files[CHOREO_SFX], merged_sfx(files).get("sfx") or {}, files.get(CLASSES),
                              files.get(CHOREO))
    if LIFE in files:
        errs += life_errors(files[LIFE], ids, files.get(CLASSES))
    if CUTSCENE_FOLEY in files:
        errs += cutscene_foley_errors(files[CUTSCENE_FOLEY], ids)
    if IMPACT in files:
        errs += impact_errors(files[IMPACT], ids, files.get(CLASSES), files.get(MIX))
    if REEFBALL_HOOKS in files:
        all_beds = set(amb_beds) | set(((files.get(MUSIC) or {}).get("ambience") or {}).keys())
        errs += reefball_hook_errors(files[REEFBALL_HOOKS], ids, all_beds, files.get(CLASSES))
    errs += muffle_errors(files.get(MIX), files.get(REEFBALL_HOOKS), buses)
    if BATTLE_STINGS in files:
        errs += sting_errors(files[BATTLE_STINGS], ids, set(((files.get(MIX) or {}).get("ducks") or {}).keys()))
    if CREATURE_VOICES in files:
        errs += creature_voice_errors(files[CREATURE_VOICES], files.get(ENEMIES), merged_sfx(files).get("sfx") or {})
    return errs


def muffle_errors(mix: object, reefball: object, buses: set[str]) -> list[str]:
    """mix.json muffle (M3-AUD-22): real buses (never Music), cutoff below open, a ramp >= 0; reefball_hooks.json
    muffle names a reason and where the ear is."""
    errs: list[str] = []
    cfg = (mix or {}).get("muffle") if isinstance(mix, dict) else None
    if cfg is not None:
        for b in cfg.get("buses", []):
            if b not in buses:
                errs.append(f"{MIX} muffle.buses: {b} is not a bus")
            if b == "Music":
                errs.append(f"{MIX} muffle.buses: the score is not in the water (leave Music out)")
        if not (_num(cfg.get("cutoff_hz")) and _num(cfg.get("open_hz")) and 20 <= cfg["cutoff_hz"] < cfg["open_hz"]):
            errs.append(f"{MIX} muffle: 20 <= cutoff_hz < open_hz")
        if not _num(cfg.get("ramp_sec", 0)) or cfg.get("ramp_sec", 0) < 0:
            errs.append(f"{MIX} muffle.ramp_sec: seconds >= 0")
    m = (reefball or {}).get("muffle") if isinstance(reefball, dict) else None
    if m is not None:
        if not isinstance(m.get("reason"), str) or not m["reason"]:
            errs.append(f"{REEFBALL_HOOKS} muffle.reason: a reason name")
        if not m.get("use_camera") and not m.get("ear_groups"):
            errs.append(f"{REEFBALL_HOOKS} muffle: use_camera or ear_groups names the ear")
        if cfg is None:
            errs.append(f"{REEFBALL_HOOKS} muffle: needs mix.json muffle")
    return errs


def sting_errors(doc: object, ids: set[str], ducks: set[str]) -> list[str]:
    """battle_stings.json (M3-AUD-18): every row an sfx row, every duck a mix.json duck held for a time > 0."""
    w0 = BATTLE_STINGS
    if not isinstance(doc, dict):
        return [f"{w0}: must be an object"]
    errs: list[str] = []
    for ev, row in (doc.get("events") or {}).items():
        w = f"{w0} events.{ev}"
        if not isinstance(row, dict):
            errs.append(f"{w}: must be an object")
            continue
        for sid in [row.get("sfx")] + list((row.get("by_arg") or {}).values()):
            if sid not in ids:
                errs.append(f"{w}: {sid} is not an sfx row")
        if "duck" in row:
            if row["duck"] not in ducks:
                errs.append(f"{w}.duck: {row['duck']} is not a mix.json duck")
            if not _num(row.get("duck_sec")) or row["duck_sec"] <= 0:
                errs.append(f"{w}.duck_sec: a duck needs a time > 0")
    for k, v in (doc.get("reduced") or {}).items():
        for sid in (k, v):
            if sid not in ids:
                errs.append(f"{w0} reduced: {sid} is not an sfx row")
    return errs


CROWD_STATES = {"murmur", "excited", "silence"}


def reefball_hook_errors(doc: object, ids: set[str], beds: set[str], classes: dict[str, list[str]] | None) -> list[str]:
    """reefball_hooks.json (M3-AUD-17): every sound an sfx row, the crowd's beds ambience beds, each action's crowd
    state known, the swim numbers positive, and class and signal names real unless the hook is `pending`."""
    w0 = REEFBALL_HOOKS
    if not isinstance(doc, dict):
        return [f"{w0}: must be an object"]
    errs: list[str] = []

    def row(v: object, w: str) -> None:
        if v not in ids:
            errs.append(f"{w}: {v} is not an sfx.json row")

    def action(a: object, w: str) -> None:
        if not isinstance(a, dict):
            errs.append(f"{w}: an action is an object")
            return
        for k in ("sfx", "sfx_at"):
            v = a.get(k)
            for sid in (v if isinstance(v, list) else [v] if v is not None else []):
                row(sid, f"{w}.{k}")
        for k in ("crowd", "restore"):
            if k in a and a[k] not in CROWD_STATES:
                errs.append(f"{w}.{k}: {a[k]} is not murmur, excited or silence")
        if "restore" in a and (not _num(a.get("restore_after_sec")) or a["restore_after_sec"] <= 0):
            errs.append(f"{w}.restore_after_sec: a restore needs a time > 0")
        picks = a.get("by")  # M3-AUD-824: sub-actions picked from a signal argument
        picks = picks if isinstance(picks, list) else [picks] if picks is not None else []
        for j, p in enumerate(picks):
            if not isinstance(p, dict) or not isinstance(p.get("arg", 0), int) or not isinstance(p.get("values"), dict):
                errs.append(f"{w}.by[{j}]: needs an int arg and a values object")
                continue
            for val, sub in p["values"].items():
                action(sub, f"{w}.by[{j}].values.{val}")
        if not any(k in a for k in ("sfx", "sfx_at", "crowd")) and not picks:
            errs.append(f"{w}: does nothing (needs sfx, sfx_at, crowd or by)")

    crowd = doc.get("crowd") or {}
    for k in ("murmur", "excited"):
        if crowd.get(k) not in beds:
            errs.append(f"{w0} crowd.{k}: {crowd.get(k)} is not an ambience bed")
    for k in ("fade_sec", "rite_fade_sec"):
        if k in crowd and (not _num(crowd[k]) or crowd[k] < 0):
            errs.append(f"{w0} crowd.{k}: a fade is a number >= 0")
    swim = doc.get("swim") or {}
    for k in ("enter", "exit", "stroke"):
        row(swim.get(k), f"{w0} swim.{k}")
    for k in ("stroke_m", "teleport_m"):
        if not _num(swim.get(k)) or swim[k] <= 0:
            errs.append(f"{w0} swim.{k}: a distance > 0")
    if not _num(swim.get("edge_m")) or swim["edge_m"] < 0:
        errs.append(f"{w0} swim.edge_m: a distance >= 0")
    if not isinstance(swim.get("groups"), list) or not swim["groups"]:
        errs.append(f"{w0} swim.groups: needs at least one group")
    seen: set[str] = set()
    for i, h in enumerate(doc.get("hooks", [])):
        w = f"{w0} hooks[{i}]"
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
        for sig, a in (h.get("signals") or {}).items():
            action(a, f"{w}.signals.{sig}")
            if known and sig not in classes[cls] and sig not in NODE_SIGNALS:
                errs.append(f"{w}.signals.{sig}: {cls} declares no such signal")
        for k in ("on_enter", "on_exit"):
            if k in h:
                action(h[k], f"{w}.{k}")
        sp = h.get("sphere")
        if sp is not None and (not isinstance(sp, dict) or not (sp.get("radius_method") or _num(sp.get("radius_m")))):
            errs.append(f"{w}.sphere: needs radius_method or radius_m")
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
    extra = [p.relative_to(root).as_posix() for p in sorted((root / SFX_DIR).glob("sfx_*.json"))]
    for rel in [MIX, MUSIC, SFX, BATTLE_SFX, SHRINE_SFX, UI_SFX, AMBIENCE, FOOTSTEPS, ENCOUNTERS, VFX_EFFECTS,
                ACCESSIBILITY, VOICES, SPEAKERS, REEFBALL_HOOKS, CHOREO_SFX, CHOREO, BATTLE_STINGS, CREATURE_VOICES, ENEMIES, LIFE, IMPACT, CUTSCENE_FOLEY, ASHCROWN_SFX] + extra:
        p = root / rel
        if p.is_file():
            out[rel] = json.loads(p.read_text(encoding="utf-8"))
    out[CLASSES] = script_classes(root)
    return out


def script_classes(root: Path) -> dict[str, list[str]]:
    """{class_name: [declared signals]} for every script under game/ (ui_sfx.json hooks name classes and signals).
    A class also has the signals of the game classes it extends (GraphicsMenu extends SettingsPage, whose
    `closed` it emits)."""
    import re

    own: dict[str, list[str]] = {}
    base: dict[str, str] = {}
    for p in sorted((root / "game").rglob("*.gd")):
        text = p.read_text(encoding="utf-8")
        m = re.search(r"(?m)^class_name\s+(\w+)", text)
        if m:
            own[m.group(1)] = re.findall(r"(?m)^signal\s+(\w+)", text)
            e = re.search(r"(?m)^extends\s+(\w+)", text)
            if e:
                base[m.group(1)] = e.group(1)
    return {cls: _with_inherited(cls, own, base) for cls in own}


def _with_inherited(cls: str, own: dict[str, list[str]], base: dict[str, str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    while cls in own and cls not in seen:
        seen.add(cls)
        out += [s for s in own[cls] if s not in out]
        cls = base.get(cls, "")
    return out


# AudioEffectReverb's ranges (M2-AUD-10)
REVERB_RANGES = {"room_size": (0.0, 1.0), "damping": (0.0, 1.0), "spread": (0.0, 1.0), "hipass": (0.0, 1.0),
                 "dry": (0.0, 1.0), "wet": (0.0, 1.0), "predelay_msec": (20.0, 500.0),
                 "predelay_feedback": (0.0, 0.98)}


def reverb_errors(mix: object, music: object, buses: set[str]) -> list[str]:
    """mix.json `reverb` / `reverb_presets` and the zone rows' `reverb` keys (M2-AUD-10)."""
    errs: list[str] = []
    if not isinstance(mix, dict):
        return errs
    cfg = mix.get("reverb")
    presets = mix.get("reverb_presets") or {}
    if cfg is not None:
        if not isinstance(cfg, dict):
            return [f"{MIX} reverb: must be an object"]
        for b in cfg.get("buses", []):
            if b not in buses:
                errs.append(f"{MIX} reverb.buses: unknown bus {b}")
        if cfg.get("default") not in presets:
            errs.append(f"{MIX} reverb.default: unknown preset {cfg.get('default')}")
        if not _num(cfg.get("ramp_sec", 0)) or cfg.get("ramp_sec", 0) < 0:
            errs.append(f"{MIX} reverb.ramp_sec: a number >= 0")
    for pid, row in presets.items():
        w = f"{MIX} reverb_presets.{pid}"
        if not isinstance(row, dict):
            errs.append(f"{w}: must be an object")
            continue
        for k, (lo, hi) in REVERB_RANGES.items():
            if k not in row:
                errs.append(f"{w}.{k}: missing")
            elif not _num(row[k]) or not lo <= row[k] <= hi:
                errs.append(f"{w}.{k}: a number in {lo}..{hi}")
    zones = (music.get("zones") if isinstance(music, dict) else None) or []
    for i, z in enumerate(zones):
        if not isinstance(z, dict):
            continue
        for w, row in [(f"{MUSIC} zones[{i}]", z)] + [(f"{MUSIC} zones[{i}].variants[{j}]", v)
                                                     for j, v in enumerate(z.get("variants", []))
                                                     if isinstance(v, dict)]:
            if "reverb" in row and row["reverb"] not in presets:
                errs.append(f"{w}.reverb: unknown preset {row['reverb']} (mix.json reverb_presets)")
    return errs


def voice_errors(doc: object, speakers: object, rows: dict) -> list[str]:
    """voices.json (M3-AUD-07): a voice for every speakers.json id, blip sets of real Voice-bus rows, sane numbers,
    and a VO pattern with {line_id}."""
    errs: list[str] = []
    if not isinstance(doc, dict):
        return [f"{VOICES}: must be an object"]
    if doc.get("pace", "syllable") not in ("syllable", "letter"):
        errs.append(f"{VOICES} pace: syllable or letter (M3-AUD-21)")
    if not _num(doc.get("mix_db", 0.0)) or not -12.0 <= doc.get("mix_db", 0.0) <= 12.0:
        errs.append(f"{VOICES} mix_db: a number in -12..12 dB (M3-AUD-23)")

    def voice(row: object, w: str, full: bool) -> None:
        if not isinstance(row, dict):
            errs.append(f"{w}: must be an object")
            return
        blips = row.get("blips")
        if full or blips is not None:
            if not isinstance(blips, list) or not blips:
                errs.append(f"{w}.blips: a non-empty list of sfx rows")
                blips = []
            for b in blips:
                if b not in rows:
                    errs.append(f"{w}.blips: unknown sfx row {b}")
                elif (rows[b] or {}).get("bus") != "Voice":
                    errs.append(f"{w}.blips: row {b} must play on the Voice bus")
        checks = {"pitch": (0.25, 4.0), "rate_ms": (0, 1000), "jitter": (0.0, 0.3), "volume_db": (-40.0, 12.0)}
        for k, (lo, hi) in checks.items():
            if k in row and (not _num(row[k]) or not lo <= row[k] <= hi):
                errs.append(f"{w}.{k}: a number in {lo}..{hi}")
            elif full and k not in row:
                errs.append(f"{w}.{k}: missing")

    voice(doc.get("default"), f"{VOICES} default", True)
    table = doc.get("speakers") or {}
    if not isinstance(table, dict):
        errs.append(f"{VOICES} speakers: must be an object")
        table = {}
    known = {r.get("id") for r in ((speakers or {}).get("speakers") or []) if isinstance(r, dict)}
    for sid, row in table.items():
        if speakers is not None and sid not in known and not (isinstance(row, dict) and row.get("pending")):
            errs.append(f"{VOICES} speakers.{sid}: not a speaker in {SPEAKERS}")
        voice(row, f"{VOICES} speakers.{sid}", False)
    for sid in sorted(k for k in known if isinstance(k, str)):
        if sid not in table:
            errs.append(f"{VOICES} speakers: {sid} ({SPEAKERS}) has no voice")
    vo = doc.get("vo") or {}
    pattern = vo.get("pattern", "")
    if not isinstance(pattern, str) or not pattern.startswith("res://") or "{line_id}" not in pattern:
        errs.append(f"{VOICES} vo.pattern: a res:// path with {{line_id}} (and usually {{speaker}})")
    if "bus" in vo and vo["bus"] != "Voice":
        errs.append(f"{VOICES} vo.bus: recorded lines play on the Voice bus")
    return errs


CHOREO_ROLES = {"beat": 2, "contact": 1}  # choreo_audio.gd's roles and the arguments each needs
CHOREO_SKIPS = {"contact", "steps"}


def choreo_errors(doc: object, rows: dict, classes: dict[str, list[str]] | None, choreo: object) -> list[str]:
    """choreo_sfx.json (M3-AUD-13): hooks by class and signal name (checked once the class exists; until then the
    hook must say pending), every sound a Combat-bus sfx row, weapons with accents, whooshes with a crest time, and
    style ids that choreo.json knows (when the battle-presentation track's table is present)."""
    if not isinstance(doc, dict):
        return [f"{CHOREO_SFX}: must be an object"]
    errs: list[str] = []
    w0 = CHOREO_SFX

    def row(v: object, w: str, blank: bool = True) -> None:
        if blank and v == "":
            return
        if v not in rows:
            errs.append(f"{w}: {v} is not an sfx.json row")
        elif (rows[v] or {}).get("bus") != "Combat":
            errs.append(f"{w}: row {v} must play on the Combat bus")

    def count(v: object, w: str) -> None:
        if not isinstance(v, int) or isinstance(v, bool) or v < 0:
            errs.append(f"{w}: a whole number >= 0")

    hooks = doc.get("hooks") or []
    if not hooks:
        errs.append(f"{w0} hooks: at least one hook")
    for i, h in enumerate(hooks):
        w = f"{w0} hooks[{i}]"
        if not isinstance(h, dict) or not isinstance(h.get("class"), str) or not h["class"]:
            errs.append(f"{w}.class: needs a class name")
            continue
        known = classes is not None and h["class"] in classes
        if classes is not None and not known and not h.get("pending", False):
            errs.append(f"{w}.class: no script declares class_name {h['class']} (mark the hook pending)")
        for role, sig in (h.get("signals") or {}).items():
            if role not in CHOREO_ROLES:
                errs.append(f"{w}.signals.{role}: not a role ({', '.join(sorted(CHOREO_ROLES))})")
            if known and sig not in classes[h["class"]]:
                errs.append(f"{w}.signals.{role}: {h['class']} declares no signal {sig}")
    accents = doc.get("accents") or {}
    for kind, sid in accents.items():
        row(sid, f"{w0} accents.{kind}")
    for who, kind in (doc.get("weapons") or {}).items():
        if kind not in accents:
            errs.append(f"{w0} weapons.{who}: {kind} has no accent")
    if doc.get("weapon_default") not in accents:
        errs.append(f"{w0} weapon_default: {doc.get('weapon_default')} has no accent")
    peaks = doc.get("peaks") or {}
    for sid, sec in peaks.items():
        row(sid, f"{w0} peaks.{sid}", blank=False)
        if not _num(sec) or sec < 0:
            errs.append(f"{w0} peaks.{sid}: seconds >= 0")
    known_styles = None
    if isinstance(choreo, dict):
        known_styles = set(((choreo.get("choreo") or {}).get("styles") or {}).keys())
    for sid, st in (doc.get("styles") or {}).items():
        w = f"{w0} styles.{sid}"
        pending = isinstance(st, dict) and st.get("pending", False)  # M3-AUD-838: a row made ahead of its style
        if known_styles is not None and sid not in known_styles and not pending:
            errs.append(f"{w}: not a style in {CHOREO}")
        if not isinstance(st, dict):
            errs.append(f"{w}: must be an object")
            continue
        for k in ("approach", "return"):
            row(st.get(k, ""), f"{w}.{k}")
            count(st.get(f"{k}_steps", 0), f"{w}.{k}_steps")
        strikes = [st.get("strike", "")] + list((st.get("strike_by_weapon") or {}).values())
        for j, v in enumerate(strikes):
            row(v, f"{w}.strike" if j == 0 else f"{w}.strike_by_weapon")
            if v and v not in peaks:
                errs.append(f"{w}: whoosh {v} has no crest time in peaks")
        if st.get("contact", "") != "@weapon":
            row(st.get("contact", ""), f"{w}.contact")
        for v in (st.get("contact_by_weapon") or {}).values():
            row(v, f"{w}.contact_by_weapon")
        for k in ("strike_by_weapon", "contact_by_weapon"):
            for kind in (st.get(k) or {}):
                if kind not in accents:
                    errs.append(f"{w}.{k}: {kind} is not a weapon kind (accents)")
        if "needs_hit" in st and not isinstance(st["needs_hit"], bool):
            errs.append(f"{w}.needs_hit: true or false")
    for skill, sid in (doc.get("skills") or {}).items():
        row(sid, f"{w0} skills.{skill}")
    row(doc.get("ko"), f"{w0} ko", blank=False)
    for k in ("enter", "step_off"):
        r = doc.get(k) or {}
        row(r.get("sfx"), f"{w0} {k}.sfx", blank=False)
        count(r.get("steps", 0), f"{w0} {k}.steps")
    vb = doc.get("vowbound") or {}
    for k in ("call", "rise", "rise_long", "sink", "fall"):
        row(vb.get(k), f"{w0} vowbound.{k}", blank=False)
    for vid, lay in (vb.get("layers") or {}).items():  # M3-AUD-846: a Vowbound's own sound over each moment
        for k, sid in (lay or {}).items():
            if k.startswith("_"):
                continue
            if k not in ("call", "rise", "sink", "fall"):
                errs.append(f"{w0} vowbound.layers.{vid}.{k}: one of call, rise, sink, fall")
            row(sid, f"{w0} vowbound.layers.{vid}.{k}")
    if not _num(vb.get("long_sec")) or vb["long_sec"] <= 0:
        errs.append(f"{w0} vowbound.long_sec: seconds > 0")
    flood = doc.get("flood") or {}
    row(flood.get("sfx"), f"{w0} flood.sfx", blank=False)
    # M3-AUD-800: the phase and stagger are the choreography's own (choreo.json bosses.<boss>.flood); this table's
    # are only a fallback, so one of the two must give them.
    floods = [flood]
    if isinstance(choreo, dict):
        for b in ((choreo.get("choreo") or {}).get("bosses") or {}).values():
            if isinstance(b, dict) and isinstance(b.get("flood"), dict):
                floods.append(b["flood"])
    if "phase" in flood and not isinstance(flood["phase"], str):
        errs.append(f"{w0} flood.phase: a phase id")
    if "stagger_sec" in flood and (not _num(flood["stagger_sec"]) or flood["stagger_sec"] < 0):
        errs.append(f"{w0} flood.stagger_sec: seconds >= 0")
    if not any(isinstance(f.get("phase"), str) and _num(f.get("stagger_sec")) for f in floods):
        errs.append(f"{w0} flood: no phase id and stagger_sec here or in {CHOREO} bosses.*.flood")
    for k in doc.get("reduced_skip", []):
        if k not in CHOREO_SKIPS:
            errs.append(f"{w0} reduced_skip: {k} is not one of {sorted(CHOREO_SKIPS)}")
    return errs


CREATURE_EVENTS = ("idle", "attack", "hurt", "death", "move")
SILENT_CREATURE = "silent"


def creature_voice_errors(doc: object, enemies: object, rows: dict) -> list[str]:
    """creature_voices.json (M3-AUD-14): every enemies.json enemy has a voice row or "silent"; each event is a known
    event naming a real sfx row; pitch, delays and levels are sane; clips map to known events."""
    errs: list[str] = []
    if not isinstance(doc, dict):
        return [f"{CREATURE_VOICES}: must be an object"]
    table = doc.get("creatures")
    if not isinstance(table, dict):
        return [f"{CREATURE_VOICES} creatures: must be an object"]
    for cid, row in table.items():
        w = f"{CREATURE_VOICES} creatures.{cid}"
        if row == SILENT_CREATURE:
            continue
        if not isinstance(row, dict) or not isinstance(row.get("events"), dict) or not row["events"]:
            errs.append(f"{w}: an object with events, or \"{SILENT_CREATURE}\"")
            continue
        for ev, sid in row["events"].items():
            if ev not in CREATURE_EVENTS:
                errs.append(f"{w}.events.{ev}: not an event ({', '.join(CREATURE_EVENTS)})")
            if sid not in rows:
                errs.append(f"{w}.events.{ev}: {sid} is not an sfx.json row")
        if "pitch" in row and (not _num(row["pitch"]) or not 0.5 <= row["pitch"] <= 2.0):
            errs.append(f"{w}.pitch: a number in 0.5..2.0")
    for ev, ms in (doc.get("delays_ms") or {}).items():
        if ev not in CREATURE_EVENTS or not _num(ms) or not 0 <= ms <= 2000:
            errs.append(f"{CREATURE_VOICES} delays_ms.{ev}: an event and 0..2000 ms")
    for clip, ev in (doc.get("clips") or {}).items():
        if ev not in CREATURE_EVENTS:
            errs.append(f"{CREATURE_VOICES} clips.{clip}: {ev} is not an event")
    for ev in doc.get("reduced_skip", []):
        if ev not in CREATURE_EVENTS:
            errs.append(f"{CREATURE_VOICES} reduced_skip: {ev} is not an event")
    for k in ("under_db", "idle_cooldown_ms"):
        if k in doc and not _num(doc[k]):
            errs.append(f"{CREATURE_VOICES} {k}: must be a number")
    if _num(doc.get("under_db", 0)) and doc.get("under_db", 0) > 0:
        errs.append(f"{CREATURE_VOICES} under_db: voices sit under the hit sounds (<= 0 dB)")
    for cls, prop in (doc.get("model_classes") or {}).items():
        if not isinstance(prop, str) or not prop:
            errs.append(f"{CREATURE_VOICES} model_classes.{cls}: the property naming the model's creature id")
    for e in ((enemies or {}).get("enemies") or []):
        eid = e.get("id") if isinstance(e, dict) else None
        if isinstance(eid, str) and eid not in table:
            errs.append(f"{CREATURE_VOICES} creatures: enemy {eid} ({ENEMIES}) has no voice row and is not \"silent\"")
    return errs
