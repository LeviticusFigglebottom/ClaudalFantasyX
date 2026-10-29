#!/usr/bin/env python3
"""ADR 0041: the Act I placeholder audit. Everything a player meets from the title to the end of Ch9 must be final.

Two halves:
- runtime (tools/placeholder/scan.tscn, run headless): every Act I zone (and each layout variant) and every arena an
  Act I encounter fights on is loaded as the game loads it. Visible capsule stand-ins, flat-coloured primitive or CSG
  meshes (greybox) and visible nodes named placeholder/temp/greybox/proxy are recorded.
- static (here): battle bodies (every Act I foe, spawn, summon and Vowbound has a real actor scene), arenas (an Act I
  encounter with no arena fights on the sandbox's own; an arena still under game/battle/arenas/ is greybox),
  portraits (hero portraits for the Act I party, bestiary portraits for Act I foes), audio (every sound, music and
  ambience cue the Act I scripts name resolves to a file on disk; no temp-named audio), and asset files named like
  placeholders.

Each finding becomes a row: path, what it is, chapter, owning role (ADR 0041's split), severity (how visible it is to
a player: high = on screen in play or battle, medium = heard or seen in a menu or in passing, low = a name only).

Usage:
  python3 tools/placeholder_audit.py                  # run the Godot scan, print the summary
  python3 tools/placeholder_audit.py --write          # ...and write docs/kb/qa/act1_final_inventory.md
  python3 tools/placeholder_audit.py --scan-json F    # use a scan already run (no Godot)
  python3 tools/placeholder_audit.py --static-only    # skip the runtime half
  python3 tools/placeholder_audit.py --check          # exit 1 while any item is left (ADR 0041's "done")
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "kb" / "qa" / "act1_final_inventory.md"
SCAN_SCENE = "res://tools/placeholder/scan.tscn"

LAST_CHAPTER = 9
CHAPTER_RE = re.compile(r"(?:^|[/_])ch(\d\d)(?!\d)")
NAME_RE = re.compile(r"(?i)(placeholder|(?:^|[_\W])temp(?:[_\W]|$)|greybox|graybox|proxy)")
GREYBOX_ARENA_DIR = "res://game/battle/arenas/"
TEST_DIR = "res://game/levels/_tests/"
PARTY = ["rhen", "asha", "toma", "ysolde", "liss", "kerrid"]
# Act I dialogue: the slice's (ch02, ch03), the prologue's and Ch1-Ch9's.
DIALOGUE_DIRS = ["prologue"] + ["ch%02d" % n for n in range(1, LAST_CHAPTER + 1)]
CUE_RE = re.compile(r"@(sfx|music|ambience)\s+([A-Za-z0-9_]+)")
AUDIO_SKIP = {"silence", "stop", "off"}

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

# ADR 0041's split (the Lead, 2026-10-28): owner -> what it takes.
OWNER_ZONES_EARLY = "env-art"  # Prologue-Ch4 zones, the shared kits, and the arenas used there
OWNER_ZONES_LATE = "env-art-b"  # Ch5-Ch9 zones and the arenas used there
OWNER_REGULAR = "creatures"  # regular enemies and wildlife
OWNER_BOSS = "creatures-b"  # bosses and Vowbound
OWNER_PEOPLE = "characters"  # named story NPCs (and the party's models)
OWNER_PARTY = "integration-qa"  # the party's bodies wherever they stand as capsules (the Lead, 2026-10-28)
OWNER_FOLK = "creatures"  # generic villagers and background folk (the VillagerLayer/FieldNpc owner)
# Named story NPCs (the Lead's list): characters builds them. Anyone else on a capsule is background folk.
NAMED_NPCS = {
    "hobb", "fenn", "marra", "tavi", "neme", "ione", "ivo", "osu", "sabe", "garo", "reed", "skipper_sadi",
    "ferrymaster", "elder", "gatekeeper", "poolkeeper", "purser", "scaleman", "stillguard", "kell", "tender",
    "inquisitor", "officer", "clerk", "sefir",
}
PARTY_EXTRA = ["pell"]
OWNER_FLOW = "act1-chapters"  # placement and flow
OWNER_VFX = "battle-presentation"
OWNER_AUDIO = "audio"
OWNER_UI = "ui-menus"
EARLY_LAST_CHAPTER = 4

# Rows the owner rules above route to a role that can't close them (the Lead, 2026-10-29, env-art's LEAD-ASK on
# M3-HER-1140): (path regex, what regex, owner, why). The first match wins; a row that matches none keeps its owner.
ROUTES: list[tuple[str, str, str, str]] = [
    (r"^game/levels/prologue/prologue\.tscn$", r"under City/Vigils", OWNER_PEOPLE,
     "Pell's vigil stand-in: characters' model, slice-polish places him on his mark"),
    (r"^assets/environments/kits/tamsule_bell/(reefball_drop_proxy\.glb|materials/tb_drop_proxy\.tres)$", r"",
     OWNER_ZONES_LATE, "the Tamsule Bell's held drop is rendering's (M3-RND-26, env-art-b)"),
]


@dataclass
class Item:
    path: str
    what: str
    chapter: int | None
    owner: str
    severity: str
    kind: str
    detail: str = ""
    count: int = 1
    examples: list[str] = field(default_factory=list)

    def chapter_label(self) -> str:
        if self.chapter is None:
            return "all"
        return "Prologue" if self.chapter == 0 else "Ch%d" % self.chapter


def _json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def res_to_path(res: str, root: Path = ROOT) -> Path:
    return root / res.removeprefix("res://")


def chapter_of(path: str) -> int | None:
    """The chapter a path or id belongs to: chNN in it, 0 for the prologue, else None."""
    m = CHAPTER_RE.search(path.lower())
    if m:
        return int(m.group(1))
    if "prologue" in path.lower() or "iskarra" in path.lower():
        return 0
    return None


def zone_owner(chapter: int | None) -> str:
    return OWNER_ZONES_LATE if chapter is not None and chapter > EARLY_LAST_CHAPTER else OWNER_ZONES_EARLY


# --- Act I encounters -------------------------------------------------------------------------------------------


def act1_encounters(root: Path = ROOT) -> dict[str, int]:
    """Encounter id -> the chapter that fights it: every encounter id the chapter files, the slice's flow and the
    Act I zone layouts name (an encounter only the sandbox or a test names is not part of the playable game)."""
    ids = {str(e.get("id", "")) for e in _json(root / "game/data/battle/encounters.json").get("encounters", [])}
    found: dict[str, int] = {}

    def walk(v: object, chapter: int) -> None:
        if isinstance(v, dict):
            for x in v.values():
                walk(x, chapter)
        elif isinstance(v, list):
            for x in v:
                walk(x, chapter)
        elif isinstance(v, str) and v in ids:
            found[v] = min(found.get(v, chapter), chapter)

    for p in sorted((root / "game/data/flow/chapters").glob("ch*.json")):
        ch = chapter_of(p.name)
        if ch is not None and ch <= LAST_CHAPTER:
            walk(_json(p), ch)
    fp = _json(root / "game/data/flow/first_playable.json")
    walk(fp, 3)
    for enc in ("ch02_tideline",):
        if enc in ids:
            found[enc] = min(found.get(enc, 2), 2)
    for p in sorted((root / "game/levels").glob("ch0*/**/*_layout.json")):
        ch = chapter_of(str(p.relative_to(root)))
        if ch is not None:
            walk(_json(p), ch)
    # dialogue events (`<<event start_battle drownbell>>`) and scene files name encounters too
    token = re.compile(r"[a-z0-9_]+")
    texts = [p for d in DIALOGUE_DIRS for p in sorted((root / "game/data/dialogue" / d).glob("*.dlg"))]
    texts += [p for p in sorted((root / "game/levels").glob("**/*.tscn")) if "/_tests/" not in str(p)]
    for p in texts:
        ch = chapter_of(str(p.relative_to(root)))
        if ch is None or ch > LAST_CHAPTER:
            continue
        for t in set(token.findall(p.read_text(encoding="utf-8", errors="ignore"))) & ids:
            found[t] = min(found.get(t, ch), ch)
    for p in sorted((root / "game/data/world").glob("**/*.json")):
        ch = chapter_of(str(p.relative_to(root)))
        if ch is not None and ch <= LAST_CHAPTER:
            walk(_json(p), ch)
    return found


def arena_chapters(root: Path = ROOT) -> dict[str, int]:
    """Arena scene -> the earliest Act I chapter whose encounter fights on it."""
    scenes = ((_json(root / "game/data/battle/arenas.json").get("arenas", {})).get("scenes", {})) or {}
    encounters = {str(e.get("id", "")): e for e in _json(root / "game/data/battle/encounters.json").get("encounters", [])}
    out: dict[str, int] = {}
    for enc_id, ch in act1_encounters(root).items():
        scene = str(scenes.get(str(encounters.get(enc_id, {}).get("arena", "")), ""))
        if scene:
            out[scene] = min(out.get(scene, ch), ch)
    return out


def party_hero(actor: str, root: Path = ROOT) -> str:
    """The party member a stage actor plays (hero_motion.json's actor_aliases and actor_prefixes, as
    HeroFieldActor.hero_of reads them), or ""."""
    field = (_json(root / "game/data/hero_motion/hero_motion.json").get("field", {})) or {}
    hero = str((field.get("actor_aliases", {}) or {}).get(actor, actor))
    for prefix in field.get("actor_prefixes", []) or []:
        if hero.startswith(prefix):
            hero = hero[len(prefix) :]
    return hero if hero in PARTY or hero in PARTY_EXTRA else ""


def battle_model(scene: str, root: Path = ROOT) -> str:
    """The model a hero's battle wrapper loads by path (HeroBattleActor.model_path), or "" when it has none."""
    try:
        text = res_to_path(scene, root).read_text(encoding="utf-8")
    except OSError:
        return ""
    m = re.search(r'^model_path = "([^"]+)"', text, re.M)
    return m.group(1) if m else ""


# --- the static checks ------------------------------------------------------------------------------------------


def check_battle(root: Path = ROOT) -> list[Item]:
    """Every Act I foe, spawn, summon and Vowbound has a real body; every Act I encounter has a final arena."""
    out: list[Item] = []
    encounters = {str(e.get("id", "")): e for e in _json(root / "game/data/battle/encounters.json").get("encounters", [])}
    enemies = {str(e.get("id", "")): e for e in _json(root / "game/data/battle/enemies.json").get("enemies", [])}
    arenas = ((_json(root / "game/data/battle/arenas.json").get("arenas", {})).get("scenes", {})) or {}
    sandbox = _find_key(_json(root / "game/data/ui/battle_sandbox.json"), "stand_ins") or {}
    used = act1_encounters(root)
    foes: dict[str, int] = {}
    greybox_arenas: dict[tuple[str, str], list[tuple[int, str]]] = {}
    for enc_id, ch in sorted(used.items()):
        enc = encounters.get(enc_id, {})
        for fid in enc.get("enemies", []):
            fid = str(fid).split("#")[0]
            foes[fid] = min(foes.get(fid, ch), ch)
        arena = str(enc.get("arena", ""))
        scene = str(arenas.get(arena, ""))
        if arena == "":
            out.append(
                Item(
                    "game/data/battle/encounters.json#%s" % enc_id,
                    "encounter %s has no arena: it fights on the sandbox's own set" % enc_id,
                    ch,
                    OWNER_FLOW,
                    "high",
                    "arena",
                )
            )
        elif scene.startswith(GREYBOX_ARENA_DIR):
            greybox_arenas.setdefault((arena, scene), []).append((ch, enc_id))
        elif scene and not res_to_path(scene, root).exists():
            out.append(Item(scene.removeprefix("res://"), "arena %s scene is missing" % arena, ch, zone_owner(ch), "high", "arena"))
    for (arena, scene), uses in sorted(greybox_arenas.items()):
        ch = min(c for c, _ in uses)
        what = "arena %s is still the greybox scene (encounters %s)" % (arena, ", ".join(sorted(e for _, e in uses)))
        out.append(Item(scene.removeprefix("res://"), what, ch, zone_owner(ch), "high", "arena"))
    # spawns and summons the Act I foes call in
    skills = _json(root / "game/data/battle/skills.json")
    for fid in list(foes):
        for sp in enemies.get(fid, {}).get("spawn", []) or []:
            foes.setdefault(str(sp), foes[fid])
    for sid in _collect_key(skills, "summon"):
        if sid in enemies:
            foes.setdefault(sid, min(foes.values()) if foes else None)
    vowbound = [str(v.get("id", "")) for v in _json(root / "game/data/battle/vowbound.json").get("vowbound", [])]
    for fid, ch in sorted(foes.items(), key=lambda kv: kv[0]):
        e = enemies.get(fid, {})
        model = str(e.get("model") or (sandbox.get(fid, {}) or {}).get("scene", ""))
        boss = "phases" in e
        owner = OWNER_BOSS if boss else OWNER_REGULAR
        if model == "":
            out.append(Item("game/data/battle/enemies.json#%s" % fid, "foe %s fights as a primitive stand-in (no model)" % fid, ch, owner, "high", "battle_body"))
        elif not res_to_path(model, root).exists():
            out.append(Item(model.removeprefix("res://"), "foe %s's model scene is missing" % fid, ch, owner, "high", "battle_body"))
    creature_rows = _json(root / "game/data/creatures/creatures.json").get("creatures", {}) or {}
    for vid in vowbound:
        scene = str((sandbox.get(vid, {}) or {}).get("scene", ""))
        own = creature_rows.get(vid, {}) or {}
        if scene == "" and own.get("vowbound"):  # the game's own rule: CreatureModels.vowbound_creature (M3-CRE-638)
            scene = str(own.get("scene", ""))
        if scene == "" or not res_to_path(scene, root).exists():
            out.append(Item("game/data/battle/vowbound.json#%s" % vid, "Vowbound %s is drawn as a primitive (no actor scene)" % vid, None, OWNER_BOSS, "high", "battle_body"))
    for hero in PARTY:
        scene = str((sandbox.get(hero, {}) or {}).get("scene", ""))
        model = battle_model(scene, root) if scene else ""
        if scene == "" or not res_to_path(scene, root).exists():
            out.append(Item("game/data/ui/battle_sandbox.json#%s" % hero, "party member %s has no battle actor (a capsule in battle)" % hero, None, OWNER_PARTY, "high", "battle_body"))
        elif model and not res_to_path(model, root).exists():
            out.append(Item(model.removeprefix("res://"), "party member %s's battle actor waits for its model (a capsule in battle until it lands)" % hero, None, OWNER_PEOPLE, "high", "battle_body"))
    return out


def check_vfx(root: Path = ROOT) -> list[Item]:
    """Every Act I boss has its set-piece VFX (boss_vfx.json `bosses`, BattleBossVfx); a boss with none fights with
    only the generic hit effects."""
    out: list[Item] = []
    rows = (_json(root / "game/data/vfx/battle/boss_vfx.json").get("bosses", {})) or {}
    encounters = {str(e.get("id", "")): e for e in _json(root / "game/data/battle/encounters.json").get("encounters", [])}
    enemies = {str(e.get("id", "")): e for e in _json(root / "game/data/battle/enemies.json").get("enemies", [])}
    seen: set[str] = set()
    for enc_id, ch in sorted(act1_encounters(root).items(), key=lambda kv: kv[1]):
        for fid in encounters.get(enc_id, {}).get("enemies", []):
            fid = str(fid)
            if fid in seen or "phases" not in enemies.get(fid, {}):
                continue
            seen.add(fid)
            if fid not in rows:
                out.append(
                    Item(
                        "game/data/vfx/battle/boss_vfx.json#%s" % fid,
                        "boss %s has no set-piece VFX (generic hit effects only)" % fid,
                        ch,
                        OWNER_VFX,
                        "medium",
                        "vfx",
                    )
                )
    return out


def check_portraits(root: Path = ROOT) -> list[Item]:
    out: list[Item] = []
    heroes = (_json(root / "game/data/ui/hero_portraits.json").get("hero_portraits", {})) or {}
    hdir = str(heroes.get("dir", "res://assets/ui/portraits/heroes/"))
    fb = str(heroes.get("fallback_emotion", "neutral"))
    for hero in PARTY:
        f = hdir + "%s_%s.png" % (hero, fb)
        if not res_to_path(f, root).exists():
            out.append(Item(f.removeprefix("res://"), "no menu portrait for %s (the page shows an initial)" % hero, None, OWNER_UI, "medium", "portrait"))
    creatures = (_json(root / "game/data/ui/creature_portraits.json").get("creature_portraits", {})) or {}
    cdir = str(creatures.get("dir", "res://assets/ui/portraits/creatures/"))
    fmt = str(creatures.get("file_fmt", "{creature}.png"))
    enemies = {str(e.get("id", "")): e for e in _json(root / "game/data/battle/enemies.json").get("enemies", [])}
    encounters = {str(e.get("id", "")): e for e in _json(root / "game/data/battle/encounters.json").get("encounters", [])}
    seen: set[str] = set()
    for enc_id, ch in sorted(act1_encounters(root).items(), key=lambda kv: kv[1]):
        for fid in encounters.get(enc_id, {}).get("enemies", []):
            model = str(enemies.get(str(fid), {}).get("model") or "")
            if not model:
                continue
            creature = Path(model.removeprefix("res://")).parent.name
            if creature in seen:
                continue
            seen.add(creature)
            f = cdir + fmt.format(creature=creature)
            if not res_to_path(f, root).exists():
                out.append(Item(f.removeprefix("res://"), "no bestiary portrait for %s" % creature, ch, OWNER_UI, "medium", "portrait"))
    return out


def audio_ids(root: Path = ROOT) -> tuple[dict[str, set[str]], list[str]]:
    """{"sfx"|"music"|"ambience": ids} from every game/data/audio json, and every audio file they name."""
    ids: dict[str, set[str]] = {"sfx": set(), "music": set(), "ambience": set()}
    files: list[str] = []
    for p in sorted((root / "game/data/audio").glob("*.json")):
        d = _json(p)
        for key, bucket in (("sfx", "sfx"), ("cues", "music"), ("ambience", "ambience")):
            v = d.get(key)
            if isinstance(v, dict):
                ids[bucket].update(k for k in v if k not in ("doc", "_doc"))
        for f in _strings(d):
            if f.startswith("res://assets/audio/"):
                files.append(f)
    return ids, sorted(set(files))


def check_audio(root: Path = ROOT) -> list[Item]:
    """Every @sfx and @music cue the Act I scripts name plays a real file, resolved as CutsceneSequencer does: a
    music.json cue on Audio's deck (CutsceneSound.music), else sfx_dir/<name>.ogg, music_dir/<name>.ogg (else its
    music_stand_ins track: a stand-in, still a placeholder).
    Plus the audio files the audio tables name: missing, or named as temp."""
    out: list[Item] = []
    cfg = _json(root / "game/data/cutscene/sequencer.json")
    dirs = {"sfx": str(cfg.get("sfx_dir", "")), "music": str(cfg.get("music_dir", ""))}
    stand_ins = cfg.get("music_stand_ins", {}) or {}
    music_cues = {
        k: str(v.get("file", "")).removeprefix("res://")
        for k, v in (_json(root / "game/data/audio/music.json").get("cues", {}) or {}).items()
        if isinstance(v, dict)
    }
    found: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for d in DIALOGUE_DIRS:
        for p in sorted((root / "game/data/dialogue" / d).glob("*.dlg")):
            for kind, name in CUE_RE.findall(p.read_text(encoding="utf-8", errors="ignore")):
                if kind in dirs and name not in AUDIO_SKIP:
                    found[(kind, name)].append(p.stem)
    # CutsceneSound.music (M2-AUD-07): a music.json cue plays on Audio's deck, stems and LFS files included, before
    # the sequencer's own music_dir/<id>.ogg and its stand-in are tried (M3-AUD-861)
    cue_files: dict[str, list[str]] = {}
    for k, v in (_json(root / "game/data/audio/music.json").get("cues", {}) or {}).items():
        if isinstance(v, dict):
            cue_files[k] = [str(v["file"])] if v.get("file") else [str(f) for f in v.get("stems", []) or []]
    for (kind, name), scenes in sorted(found.items()):
        if kind == "music" and cue_files.get(name) and all(res_to_path(f, root).exists() for f in cue_files[name]):
            continue
        if res_to_path("%s%s.ogg" % (dirs[kind], name), root).exists():
            continue
        ch = min((c for c in (chapter_of(s) for s in scenes) if c is not None), default=None)
        stand = str(stand_ins.get(name, "")) if kind == "music" else ""
        if stand and res_to_path("%s%s.ogg" % (dirs[kind], stand), root).exists():
            what = "@music %s plays the stand-in %s" % (name, stand)
        else:
            what = "@%s %s is silent (no %s%s.ogg)" % (kind, name, dirs[kind].removeprefix("res://"), name)
        if kind == "music" and name in music_cues:
            what += (
                "; music.json has a `%s` cue row (%s), but CutsceneSequencer only reads music_dir/<id>.ogg"
                " and music_stand_ins: a seam between audio's table and the sequencer" % (name, music_cues[name])
            )
        item = Item("%s%s.ogg" % (dirs[kind].removeprefix("res://"), name), what, ch, OWNER_AUDIO, "medium", "audio")
        item.examples = sorted(set(scenes))
        item.count = len(scenes)
        out.append(item)
    _, files = audio_ids(root)
    for f in files:
        rel = f.removeprefix("res://")
        if "{" in rel:  # a template (vo/{speaker}/{line_id}.ogg), not a file
            continue
        if not (root / rel).exists():
            out.append(Item(rel, "audio file a table names is missing (the cue is silent)", chapter_of(rel), OWNER_AUDIO, "medium", "audio"))
        elif NAME_RE.search(Path(rel).stem):
            out.append(Item(rel, "audio file is named as a temp/placeholder", chapter_of(rel), OWNER_AUDIO, "medium", "audio"))
    return out


def check_named_files(root: Path = ROOT) -> list[Item]:
    """Asset files named like placeholders (the runtime scan catches the visible nodes; this catches the files)."""
    out: list[Item] = []
    for base in ("assets/environments", "assets/characters", "assets/creatures", "assets/props", "game/creatures"):
        for p in sorted((root / base).rglob("*")):
            if p.suffix.lower() not in (".glb", ".tscn", ".tres", ".png", ".gltf") or not NAME_RE.search(p.stem):
                continue
            rel = str(p.relative_to(root))
            ch = chapter_of(rel)
            if ch is not None and ch > LAST_CHAPTER:
                continue
            out.append(Item(rel, "asset file named as a placeholder", ch, zone_owner(ch) if base.startswith("assets/environments") else OWNER_PEOPLE if "characters" in base else OWNER_REGULAR, "low", "named_file"))
    return out


# --- the runtime half -------------------------------------------------------------------------------------------


def find_godot() -> str | None:
    return shutil.which("godot") or shutil.which("godot4")


def run_scan(godot: str, root: Path = ROOT) -> dict:
    with tempfile.TemporaryDirectory(prefix="placeholder_scan_") as tmp:
        out = Path(tmp) / "scan.json"
        env = dict(os.environ, XDG_DATA_HOME=str(Path(tmp) / "xdg"))
        subprocess.run(
            [godot, "--headless", "--path", str(root), SCAN_SCENE, "--", "--out=%s" % out],
            env=env,
            check=False,
            capture_output=True,
            timeout=3600,
        )
        if not out.exists():
            raise RuntimeError("the Godot scan wrote nothing (run `godot --headless --path . --import` first?)")
        return json.loads(out.read_text(encoding="utf-8"))


def from_scan(scan: list[dict], root: Path = ROOT) -> list[Item]:
    """Groups the runtime scan's items into rows: one per capsule actor, one per zone and greybox group, one per
    placeholder-named mesh."""
    out: list[Item] = []
    creature_ids = {Path(str(e.get("model") or "")).parent.name for e in _json(root / "game/data/battle/enemies.json").get("enemies", [])}
    creature_ids |= {"hound", "matron", "spar_wraith", "inquisitor"}
    bosses = {"matron", "spar_wraith", "drownbell", "hullgnaw", "undertows_reach", "cinder_matron"}
    arena_ch = arena_chapters(root)
    groups: dict[tuple[str, str, str], list[dict]] = collections.defaultdict(list)
    for it in scan:
        key_group = it.get("group", "")
        if it["kind"] == "named":
            key_group = re.sub(r"[-_]lod\d+$", "", Path(it.get("node", "")).name)
        elif it["kind"] == "greybox":
            key_group = ""  # one row per zone or arena; its groups are listed in the row
        groups[(it["scene"], it["kind"], key_group)].append(it)
    for (scene, kind, group), its in sorted(groups.items()):
        rel = scene.removeprefix("res://")
        ch = arena_ch.get(scene, chapter_of(rel))
        arena = "/arenas/" in rel
        nodes = sorted({i.get("node", "") for i in its})
        variants = sorted({i.get("detail", "").split(";")[0] for i in its if i.get("detail", "").startswith("variant")})
        if kind == "capsule":
            who = group.lower()
            base = re.sub(r"(_\d+|_[a-d])$", "", who)
            if base in creature_ids or who in creature_ids:
                owner = OWNER_BOSS if base in bosses or who in bosses else OWNER_REGULAR
            elif party_hero(who, root) != "":
                owner = OWNER_PARTY
            elif base in NAMED_NPCS or who in NAMED_NPCS:
                owner = OWNER_PEOPLE
            else:
                owner = OWNER_FOLK
            what = "%s is a capsule stand-in" % who + (" (%s)" % ", ".join(variants) if variants else "")
            out.append(Item(rel, what, ch, owner, "high", "capsule", examples=nodes[:3]))
        elif kind == "greybox":
            meshes = collections.Counter(i.get("detail", "").split("; ")[-1] for i in its)
            mesh_txt = ", ".join("%d %s" % (n, m) for m, n in meshes.most_common())
            tops = collections.Counter(
                re.sub(r"\d+$", "*", "/".join(i.get("node", "").split("/")[:2])) or "root" for i in its
            )
            top_txt = ", ".join("%s %d" % (g or "root", n) for g, n in tops.most_common(8))
            where = "battle arena" if arena else "zone"
            what = "%s greybox: %d visible primitive/CSG meshes (%s), under %s" % (where, len(its), mesh_txt, top_txt)
            out.append(Item(rel, what, ch, zone_owner(ch), "high", "greybox", count=len(its), examples=nodes[:4]))
        elif kind == "named":
            what = "visible mesh named as a placeholder: %s (%d node(s))" % (group, len(its))
            out.append(Item(rel, what, ch, zone_owner(ch), "medium", "named", count=len(its), examples=nodes[:3]))
        elif kind == "missing":
            out.append(Item(rel, "scene file is missing", ch, zone_owner(ch), "high", "missing"))
    return out


# --- the inventory ----------------------------------------------------------------------------------------------


def route(item: Item) -> Item:
    """ROUTES' owner for an item one of its rows matches, else the item as it is."""
    for path_re, what_re, owner, _why in ROUTES:
        if re.search(path_re, item.path) and re.search(what_re, item.what):
            item.owner = owner
            break
    return item


def audit(scan: list[dict] | None, root: Path = ROOT) -> list[Item]:
    items = (from_scan(scan, root) if scan is not None else []) + check_battle(root) + check_portraits(root)
    items += check_vfx(root)
    items += check_audio(root) + check_named_files(root)
    items = [route(i) for i in items if i.chapter is None or i.chapter <= LAST_CHAPTER]
    items.sort(key=lambda i: (i.owner, SEVERITY_ORDER[i.severity], i.chapter if i.chapter is not None else 99, i.path))
    return items


def render(items: list[Item], source: str, scanned: list[str] | None = None) -> str:
    by_owner: dict[str, list[Item]] = collections.defaultdict(list)
    for i in items:
        by_owner[i.owner].append(i)
    sev = collections.Counter(i.severity for i in items)
    lines = [
        "# Act I final-quality inventory (ADR 0041)",
        "",
        "Generated by `python3 tools/placeholder_audit.py --write` (integration-qa owns it). Don't hand-edit the "
        "tables: fix the item and re-run. Act I is done when this lists nothing and a full headless playthrough "
        "passes (ADR 0041 §4).",
        "",
        "- **Scope:** everything a player meets from the title to the end of Ch9. The runtime scan loads every Act I "
        "zone (each layout variant too) and every arena an Act I encounter uses. The static checks cover battle "
        "bodies, arenas, portraits, audio cues and files, and placeholder-named assets.",
        "- **Severity:** high = on screen in play or battle; medium = heard, or seen in a menu or in passing; low = "
        "a name only.",
        "- **Covered elsewhere:** item, equipment and skill icons and the battle HUD's faces are UI's "
        "`test_menu_glyphs` and `test_battle_portraits` (M3-UI-211; `docs/kb/qa/ui_act1_menu_audit.md`); sounds are "
        "`tools/audio/act1_audio_audit.py` (audio's, M3-AUD-861).",
        "- **Not audited yet, with the reason:** battle VFX beyond the bosses' set pieces (every hit falls back to "
        "its element's effect, so whether a skill needs a signature effect is battle-presentation's call).",
        "- **Source:** %s." % source,
    ]
    if scanned:
        lines += [
            "- **Scenes the runtime scan loaded (%d):** %s." % (len(scanned), ", ".join("`%s`" % Path(s).stem for s in scanned)),
            "",
        ]
    lines += [
        "## Summary: %d items (%d high, %d medium, %d low)" % (len(items), sev["high"], sev["medium"], sev["low"]),
        "",
        "| Owner | High | Medium | Low | Task |",
        "|---|---|---|---|---|",
    ]
    for owner in sorted(by_owner):
        c = collections.Counter(i.severity for i in by_owner[owner])
        lines.append("| %s | %d | %d | %d | %s |" % (owner, c["high"], c["medium"], c["low"], TASKS.get(owner, "")))
    for owner in sorted(by_owner):
        lines += ["", "## %s (%s)" % (owner, TASKS.get(owner, "")), "", "| Severity | Chapter | Path | What |", "|---|---|---|---|"]
        for i in by_owner[owner]:
            what = i.what + (": " + ", ".join(i.examples) if i.examples and i.kind in ("audio",) else "")
            lines.append("| %s | %s | `%s` | %s |" % (i.severity, i.chapter_label(), i.path, what.replace("|", "/")))
    return "\n".join(lines) + "\n"


# Owner -> the task file that carries its rows (docs/kb/tasks/M3/).
TASKS = {
    OWNER_ZONES_EARLY: "M3-HER-1140",
    OWNER_ZONES_LATE: "M3-HER-1141",
    OWNER_REGULAR: "M3-HER-1142",
    OWNER_BOSS: "M3-HER-1143",
    OWNER_PEOPLE: "M3-HER-1144",
    OWNER_PARTY: "M3-HER-1149",
    OWNER_FLOW: "M3-HER-1145",
    OWNER_AUDIO: "M3-HER-1146",
    OWNER_UI: "M3-HER-1147",
    OWNER_VFX: "M3-HER-1148",
}


def _find_key(v: object, key: str) -> object:
    if isinstance(v, dict):
        if key in v:
            return v[key]
        for x in v.values():
            r = _find_key(x, key)
            if r is not None:
                return r
    return None


def _collect_key(v: object, key: str) -> list[str]:
    out: list[str] = []
    if isinstance(v, dict):
        for k, x in v.items():
            if k == key and isinstance(x, str):
                out.append(x)
            else:
                out += _collect_key(x, key)
    elif isinstance(v, list):
        for x in v:
            out += _collect_key(x, key)
    return out


def _strings(v: object) -> list[str]:
    if isinstance(v, dict):
        return [s for x in v.values() for s in _strings(x)]
    if isinstance(v, list):
        return [s for x in v for s in _strings(x)]
    return [v] if isinstance(v, str) else []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scan-json", help="a scan.json already written by tools/placeholder/scan.tscn")
    ap.add_argument("--static-only", action="store_true", help="skip the runtime scan")
    ap.add_argument("--write", action="store_true", help="write docs/kb/qa/act1_final_inventory.md")
    ap.add_argument("--check", action="store_true", help="exit 1 while any item is left")
    ap.add_argument("--source-note", default="", help="appended to the inventory's Source line (e.g. a trial merge)")
    args = ap.parse_args(argv)
    raw: dict | None = None
    source = "static checks only"
    if args.scan_json:
        raw = json.loads(Path(args.scan_json).read_text(encoding="utf-8"))
        source = "the runtime scan and the static checks"
    elif not args.static_only:
        godot = find_godot()
        if godot is None:
            print("no godot on PATH: static checks only (python3 tools/dev/fetch_godot.py)", file=sys.stderr)
        else:
            raw = run_scan(godot)
            source = "the runtime scan and the static checks"
    if args.source_note:
        source += "; " + args.source_note
    scan = raw.get("items", []) if raw is not None else None
    scanned = raw.get("scanned", []) if raw is not None else []
    items = audit(scan)
    sev = collections.Counter(i.severity for i in items)
    owners = collections.Counter(i.owner for i in items)
    print("placeholder audit: %d items (%d high, %d medium, %d low)" % (len(items), sev["high"], sev["medium"], sev["low"]))
    for o, n in sorted(owners.items()):
        print("  %-20s %d" % (o, n))
    if args.write:
        INVENTORY.write_text(render(items, source, scanned), encoding="utf-8")
        print("wrote %s" % INVENTORY.relative_to(ROOT))
    return 1 if args.check and items else 0


if __name__ == "__main__":
    sys.exit(main())
