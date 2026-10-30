#!/usr/bin/env python3
"""Act I audio audit (ADR 0041: Act I at final quality; M3-AUD-861). Lists every silent, temp or reused-placeholder
sound a player can meet from the title through Ch9, from the data the runtime reads (no Godot run):

  zones       every Act I level scene: a music.json zone row and an ambience.json bed (beds that exist for a scene
              but are not wired are flagged)
  enemies     every enemies.json id: creature_voices.json's five events, each row's files on disk, and rows that
              borrow another creature's files (variant_of, or the same file in two creatures' rows)
  battles     every boss fight (an encounter with a phased foe): its own cue, and a row for each phase of a stem cue
  abilities   every Act I skill's battle effect: its own sound, not a borrowed generic hit/heal/status row
  intros      every Act I boss intro (choreo.json boss_intro): its own sting in battle_stings.json by_arg
  skills      every skills.json skill: what BattleVfx plays for it (a skill row, its element, heal, status), and
              so what BattleAudio hears; a skill that does none of those is silent
  cutscenes   every Act I .dlg `@music` / `@sfx` id: a music.json cue, a real file, or a sequencer music_stand_ins
              row (temp), or nothing (silent)
  actions     every Act I .dlg `@anim` clip: a cutscene_foley.json row (or '' for a silent gesture), or an `@sfx`
              beside it; doors opened in cutscenes are heard here or through `@sfx`
  battle      every battle-wide sound: element hits, heal, status landing and ticks, KO, openings, outcomes, Rim
              break, each Act I Vowbound's call sting, the items, the Swell finishers and choreo styles
  footsteps   every Act I level names its ground; every surface has walk, run, stop and turn rows
  ui          ui_sfx.json hooks still `pending` (their target class has not landed, so they are silent)
  ui core     the cursor, confirm, cancel and error rows, and every hook's signal rows, on disk
  notes       audio data rows whose own note says stand-in, temp, placeholder, sketch or "no scene yet"

Run: python3 tools/audio/act1_audio_audit.py [--md] [--act 2]   (exit 1 while any Act I item is open:
tools/tests/test_act1_audio_audit.py gates on it, M3-AUD-864. `--act 2` audits Ch10-Ch16 the same way as a report,
exit 0: the Act II audio inventory for ADR 0203's gate.)"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACT1_DIRS = ["prologue"] + [f"ch0{i}" for i in range(1, 10)]
# The act under audit (set_act): its level and dialogue folders, its encounter, flag and dialogue-path patterns, and
# the later acts a data note may name without being a temp note. Act I's are the defaults; `--act 2` (ADR 0203
# preparation, report-only) audits Ch10-Ch16 the same way.
ACT = 1
IN_ACT_ENC = re.compile(r"(?!ch(1[0-9]|2[0-9])_)")   # Act I: every encounter id but Ch10+'s
ACT_FLAG = re.compile(r"ch0[1-9]_")
ACT_DLG = re.compile(r"(prologue|ch0[1-9]|slice|act1|vertical)")
LATER_NOTE = re.compile(r"act[23]|Act I{2,3}\b|Ch1[0-9]|Ch2[0-9]")


def set_act(n: int) -> None:
    """Point every section at act `n` (1 or 2)."""
    global ACT, ACT1_DIRS, IN_ACT_ENC, ACT_FLAG, ACT_DLG, LATER_NOTE
    ACT = n
    if n == 1:
        ACT1_DIRS = ["prologue"] + [f"ch0{i}" for i in range(1, 10)]
        IN_ACT_ENC = re.compile(r"(?!ch(1[0-9]|2[0-9])_)")
        ACT_FLAG = re.compile(r"ch0[1-9]_")
        ACT_DLG = re.compile(r"(prologue|ch0[1-9]|slice|act1|vertical)")
        LATER_NOTE = re.compile(r"act[23]|Act I{2,3}\b|Ch1[0-9]|Ch2[0-9]")
    elif n == 2:
        ACT1_DIRS = [f"ch1{i}" for i in range(0, 7)]
        IN_ACT_ENC = re.compile(r"ch1[0-6]_")
        ACT_FLAG = re.compile(r"ch1[0-6]_")
        ACT_DLG = re.compile(r"/ch1[0-6]/|act2")
        LATER_NOTE = re.compile(r"act3|Act III\b|Ch1[7-9]|Ch2[0-9]")
    else:
        raise ValueError(f"no act {n}")


def _later(enc_id: str) -> bool:
    """An encounter outside the act under audit."""
    return not IN_ACT_ENC.match(enc_id)
DATA = ROOT / "game" / "data"
AUDIO = DATA / "audio"
# Reported cases that are right as they are, each with its reason (printed under "By design", never counted)
BY_DESIGN = {
    "game/levels/ch03/first_verse/first_verse.tscn: no music":
        "Cutscene B's own @music (shell_shrine_interior, hush_first_verse) scores it; a zone cue would fight it",
    "game/levels/ch07/tidecup_match/tidecup_match.tscn: no ambience bed":
        "ReefballAudio plays the crowd beds (reefball_hooks.json murmur/excited) with the match's state",
    "ui class `BattlePause` (game/ui/menus/battle_pause/battle_pause.gd) takes input and has no hook on it or a base class":
        "the pause controller (a Node); what the player sees and moves is BattlePauseMenu, which has its hook",
    "ui class `DialogueAssist` (game/ui/dialogue_assist/dialogue_assist.gd) takes input and has no hook on it or a base class":
        "the dialogue assist overlay; its Backlog page is a FieldSubmenu (hooked), and its lines are VoiceAudio's",
    "ui class `DialogueBox` (game/ui/dialogue/dialogue_box.gd) takes input and has no hook on it or a base class":
        "VoiceAudio voices every DialogueBox (the speaker's blips and recorded lines; audio_director.gd)",
    "ui class `MenuPage` (game/ui/battle/menu_page.gd) takes input and has no hook on it or a base class":
        "a page inside CommandMenu, LatticeMenu and the rest: their hooks watch its cursor",
    "ui class `SaveSlotRow` (game/ui/save/save_slot_row.gd) takes input and has no hook on it or a base class":
        "a row of SaveMenu, whose hook plays the slot sounds",
    "ui class `SwellRingView` (game/ui/battle/swell_ring_view.gd) takes input and has no hook on it or a base class":
        "a display inside CommandMenu (the Swell ring); the Swell's sounds are battle and choreo rows",
    "ui class `LatticeBoardView` (game/ui/menus/lattice/lattice_board_view.gd) takes input and has no hook on it or a base class":
        "the board inside LatticeMenu, whose hook plays its node, unlock and step sounds",
    "ui class `KiteChart` (game/ui/kite/kite_chart.gd) takes input and has no hook on it or a base class":
        "Act III's Kite (Ch18): later-act UI, paused by ADR 0041",
    "ui class `ControlsModel` (game/ui/settings/controls_model.gd) takes input and has no hook on it or a base class":
        "a model (SettingsPageModel), not a node: ControlsMenu, a SettingsPage, is what is hooked",
    "ui class `TownMenu` (game/ui/shop/town_menu.gd) takes input and has no hook on it or a base class":
        "a base class only: ShopMenu and InnMenu extend it, and each has its own hook",
}
TEMP_WORDS = re.compile(r"\b(stand-in|stand in|temp|temporary|placeholder|sketch|no scene yet|no zone yet)\b", re.I)


def _json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _res(path: str) -> Path:
    return ROOT / path.removeprefix("res://")


def act1_scenes() -> list[str]:
    out = []
    for d in ACT1_DIRS:
        for p in sorted((ROOT / "game" / "levels" / d).rglob("*.tscn")):
            if p.stem.endswith("_dressing") or p.stem != p.parent.name:
                continue                # a level is <level>/<level>.tscn; other scenes there are parts it instances
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


def _act1_enemies() -> list[str]:
    """Act I's foes: every enemy an Act I encounter fields (Ch10+ encounters are paused, ADR 0041), plus any that no
    encounter names (summons and set-piece entries)."""
    enemies = _json(DATA / "battle" / "enemies.json")["enemies"]
    ids = list(enemies) if isinstance(enemies, dict) else [r["id"] for r in enemies]
    fielded: dict[str, set] = {}
    for e in _json(DATA / "battle" / "encounters.json")["encounters"]:
        later = _later(e["id"])
        for f in e.get("enemies", []):
            fielded.setdefault(f, set()).add(later)
    return [i for i in ids if i not in fielded or False in fielded[i]]


def audit_enemies() -> list[str]:
    ids = _act1_enemies()
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
    # a skill only later-act foes use is paused with them (ADR 0041)
    later = {e for enc in _json(DATA / "battle" / "encounters.json")["encounters"]
             if _later(enc["id"]) for e in enc.get("enemies", [])}
    act1_foes = set(_act1_enemies())
    users: dict[str, set] = {}
    for f in _json(DATA / "battle" / "enemies.json")["enemies"]:
        for sid in re.findall(r'"([a-z0-9_]+)"', json.dumps(f)):
            users.setdefault(sid, set()).add(f["id"])
    out = []
    for r in rows:
        sid = r["id"]
        if sid in users and not (users[sid] & act1_foes) and users[sid] <= later:
            continue
        if sid in vmap.get("skills", {}) or sid in bsfx.get("skills", {}) or f'"{sid}"' in named:
            continue  # its own row, or a boss telegraph / choreography row names it
        does = (r.get("power", 0) or 0) > 0 or r.get("heal") or r.get("statuses") or r.get("status") \
            or r.get("kind") in ("heal", "revive", "status", "buff", "debuff", "attack", "magic", "physical")
        if not does:
            out.append(f"skill `{sid}` (kind {r.get('kind')}, power {r.get('power')}): no hit, heal or status, "
                       "so nothing but the choreography's accents")
    return out


def audit_battles() -> list[str]:
    """Every boss fight (an encounter with a phased foe) has its own cue, and every phase of a stem cue has a row."""
    enc = _json(DATA / "battle" / "encounters.json")["encounters"]
    foes = {r["id"]: r for r in _json(DATA / "battle" / "enemies.json")["enemies"]}
    music = _json(AUDIO / "music.json")
    cues, battle = music["cues"], music["battle"]
    out = []
    for e in enc:
        phased = [f for f in e.get("enemies", []) if foes.get(f, {}).get("phases")]
        if not phased:
            continue
        cue = battle["encounters"].get(e["id"])
        if cue is None:
            out.append(f"boss encounter `{e['id']}` ({', '.join(phased)}) plays the default battle music")
            continue
        if cues.get(cue, {}).get("stems"):
            for f in phased:
                for ph in foes[f]["phases"]:
                    if ph.get("id") not in battle.get("phases", {}):
                        out.append(f"`{e['id']}`: {f}'s phase `{ph.get('id')}` has no music row (its stems never change)")
    return out


GENERIC_VFX = {"hit_none", "hit_fire", "hit_ice", "hit_lightning", "hit_water", "hit_holy", "heal", "status_apply",
               "ko_release"}


def audit_abilities() -> list[str]:
    """Every ability effect BattleVfx plays for an Act I skill (effects.json map.skills) has its own sound, not one of
    the generic hit / heal / status rows it borrowed when battle-presentation gave it a VFX (M3-BPR-421)."""
    vmap = _json(DATA / "vfx" / "battle" / "effects.json")["map"].get("skills", {})
    rows = _json(AUDIO / "battle_sfx.json")["vfx"]
    later = {e for enc in _json(DATA / "battle" / "encounters.json")["encounters"]
             if _later(enc["id"]) for e in enc.get("enemies", [])}
    act1_foes = set(_act1_enemies())
    users: dict[str, set] = {}
    for f in _json(DATA / "battle" / "enemies.json")["enemies"]:
        for sid in re.findall(r'"([a-z0-9_]+)"', json.dumps(f)):
            users.setdefault(sid, set()).add(f["id"])
    out = []
    for sid, effect in sorted(vmap.items()):
        if sid in users and not (users[sid] & act1_foes) and users[sid] <= later:
            continue  # a later-act foe's skill
        row = rows.get(effect)
        if effect not in GENERIC_VFX and row in GENERIC_VFX:
            out.append(f"ability `{sid}` (effect `{effect}`) borrows `{row}`")
    return out


def audit_intros() -> list[str]:
    """Every Act I boss intro (choreo.json boss_intro rows) plays its own sting, not the shared one."""
    intro = _json(DATA / "battle" / "choreo.json")["choreo"]["boss_intro"]
    stings = _json(AUDIO / "battle_stings.json")["events"]["boss_intro"]
    by = stings.get("by_arg", {})
    out = []
    for enc, row in intro.get("rows", {}).items():
        if _later(enc):
            continue
        if enc not in by:
            out.append(f"boss intro `{enc}` ({row.get('enemy')}) plays the shared `{stings.get('sfx')}` sting")
    return out


def _dlg_files() -> list[Path]:
    out = []
    for d in ["game/data/dialogue", "game/cutscene", "game/levels"]:
        out += sorted((ROOT / d).rglob("*.dlg"))
    act1 = []
    for p in out:
        rel = p.relative_to(ROOT).as_posix()
        m = ACT_DLG.search(rel)
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
                # CutsceneSound.music (M2-AUD-07): a music.json cue plays on Audio's deck, stems and all; only an id
                # that is not a cue falls back to the sequencer's own stream (<music_dir><id>.ogg, then the stand-in)
                if cid in cues:
                    continue
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


def _ui_classes() -> dict[str, tuple[str, str, bool]]:
    """class_name -> (file, the class it extends, whether it takes input) for every game/ui script."""
    out = {}
    for p in sorted((ROOT / "game" / "ui").rglob("*.gd")):
        t = p.read_text(encoding="utf-8")
        m = re.search(r"^class_name\s+(\w+)", t, re.M)
        e = re.search(r"^extends\s+(\w+)", t, re.M)
        if m:
            takes = bool(re.search(r"Button|pressed|ui_accept|_gui_input|_unhandled_input|handle_input", t))
            out[m.group(1)] = (p.relative_to(ROOT).as_posix(), e.group(1) if e else "", takes)
    return out


def audit_ui() -> list[str]:
    ui = _json(AUDIO / "ui_sfx.json")
    hooked = {h.get("class") for h in ui.get("hooks") or []}
    classes = _ui_classes()
    out = []
    for cls, (path, _, takes) in classes.items():
        if not takes or cls.endswith("Shot"):
            continue  # display-only, or a screenshot harness
        c, seen = cls, set()
        while c in classes and c not in hooked and c not in seen:  # UiAudio.hook_for walks the base scripts
            seen.add(c)
            c = classes[c][1]
        if c not in hooked and classes[cls][1] not in ("RefCounted", "Resource", "Object"):
            out.append(f"ui class `{cls}` ({path}) takes input and has no hook on it or a base class")
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
                            and not LATER_NOTE.search(v):
                        out.append(f"{p.name}:{path}: {v[:140]}")
                    else:
                        walk(v, f"{path}.{k}" if path else k)
            elif isinstance(o, list):
                for j, v in enumerate(o):
                    walk(v, f"{path}[{j}]")
        walk(_json(p), "")
    return out


def _sfx_rows() -> dict:
    rows = {}
    for p in [AUDIO / "sfx.json"] + sorted(AUDIO.glob("sfx_*.json")):
        for k, v in _json(p).get("sfx", {}).items():
            rows.setdefault(k, v)  # AudioData.sfx_rows: the first file's row wins
    return rows


def _row_problem(rows: dict, rid: str) -> str:
    """'' when sfx row `rid` exists and every file it names is on disk, else what is wrong with it."""
    row = rows.get(rid)
    if row is None:
        return f"`{rid}` is no sfx row"
    files = row.get("files") or ([row["file"]] if row.get("file") else [])
    if not files:
        return f"`{rid}` names no file"
    gone = [f for f in files if not _res(f).is_file()]
    return f"`{rid}` is missing {gone[0]}" if gone else ""


def audit_cutscene_actions() -> list[str]:
    """Every Act I `@anim` clip is heard or silent on purpose: cutscene_foley.json `anim` maps it (exactly, else
    by glob) to a row, or to '' for a gesture that makes no sound; or an `@sfx` within two lines plays for it."""
    import fnmatch
    anim = _json(AUDIO / "cutscene_foley.json")["anim"]
    rows = _sfx_rows()
    out, seen = [], set()
    for p in _dlg_files():
        rel = p.relative_to(ROOT).as_posix()
        lines = p.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            m = re.match(r"\s*@anim\s+\S+\s+(\S+)", line)
            if not m or m.group(1) in seen:
                continue
            clip = m.group(1)
            key = clip if clip in anim else next((k for k in anim if "*" in k and fnmatch.fnmatch(clip, k)), None)
            if key is None:
                if any(lines[j].lstrip().startswith("@sfx") for j in range(max(0, i - 2), min(len(lines), i + 3))):
                    continue
                seen.add(clip)
                out.append(f"{rel}:{i + 1} @anim clip `{clip}`: no foley row and no @sfx beside it (silent)")
                continue
            seen.add(clip)
            if anim[key] and _row_problem(rows, anim[key]):
                out.append(f"{rel}:{i + 1} @anim clip `{clip}`: {_row_problem(rows, anim[key])}")
    return out


def audit_battle_events() -> list[str]:
    """What every battle plays whatever the skill: each element hit, the heal, a status landing, each status tick,
    a KO, the openings, the outcomes, a Rim break, a Vowbound's call, dismissal and fall, the items, and each
    Swell style's contact. Each must reach an sfx row whose files are on disk."""
    vmap = _json(DATA / "vfx" / "battle" / "effects.json")["map"]
    bsfx = _json(AUDIO / "battle_sfx.json")
    choreo = _json(AUDIO / "choreo_sfx.json")
    rows = _sfx_rows()
    out = []
    for sec in ("elements", "events", "ticks", "items", "swell_by_hero", "ko_overrides"):
        for k, effect in vmap.get(sec, {}).items():
            rid = bsfx["vfx"].get(effect)
            if rid is None:
                out.append(f"battle {sec} `{k}` (effect `{effect}`): no battle_sfx vfx row (silent)")
            elif rid and _row_problem(rows, rid):
                out.append(f"battle {sec} `{k}`: {_row_problem(rows, rid)}")
    for sec in ("events", "outcomes", "openings"):
        for k, rid in bsfx.get(sec, {}).items():
            if rid and _row_problem(rows, rid):
                out.append(f"battle_sfx {sec} `{k}`: {_row_problem(rows, rid)}")
    stings = bsfx.get("vowbound_stings", {})
    for v in _json(DATA / "battle" / "vowbound.json")["vowbound"]:
        flag = str(v.get("bound_flag", ""))
        if not ACT_FLAG.match(flag):
            continue  # bound in another act
        if v["id"] not in stings:
            out.append(f"Vowbound `{v['id']}` (bound by {flag}): no call sting in battle_sfx vowbound_stings")
        elif _row_problem(rows, stings[v["id"]]):
            out.append(f"Vowbound `{v['id']}`: {_row_problem(rows, stings[v['id']])}")
    accents = choreo.get("accents", {})
    for style, row in choreo.get("styles", {}).items():
        for part in ("strike", "contact"):
            rid = row.get(part)
            if rid == "@weapon":  # the actor's weapon accent (ChoreoAudio WEAPON), checked below
                continue
            if rid and _row_problem(rows, rid):
                out.append(f"choreo style `{style}` {part}: {_row_problem(rows, rid)}")
        for by in ("strike_by_weapon", "contact_by_weapon"):
            for w, rid in (row.get(by) or {}).items():
                if rid and _row_problem(rows, rid):
                    out.append(f"choreo style `{style}` {by} `{w}`: {_row_problem(rows, rid)}")
    for kind in set(choreo.get("weapons", {}).values()) | {choreo.get("weapon_default", "")}:
        rid = accents.get(kind)
        if rid is None:
            out.append(f"weapon kind `{kind}`: no accent row in choreo_sfx.json (its blows land silent)")
        elif rid and _row_problem(rows, rid):
            out.append(f"weapon kind `{kind}` accent: {_row_problem(rows, rid)}")
    return out


def audit_footsteps() -> list[str]:
    """Every Act I level a hero walks names its ground (footsteps.json `scenes`) rather than falling to the default,
    and every surface has its walk, run, stop and turn rows with files on disk."""
    fs = _json(AUDIO / "footsteps.json")
    rows = _sfx_rows()
    out = []
    for name, srf in fs["surfaces"].items():
        for gait in ("walk", "run", "stop", "turn"):
            rid = srf.get(gait)
            if not rid:
                out.append(f"footstep surface `{name}`: no `{gait}` row")
            elif _row_problem(rows, rid):
                out.append(f"footstep surface `{name}` {gait}: {_row_problem(rows, rid)}")
    for s in act1_scenes():
        sid = fs["scenes"].get(s)
        if sid is None:
            out.append(f"{s.removeprefix('res://')}: no footsteps.json scene row (falls to `{fs['default']}`)")
        elif sid not in fs["surfaces"]:
            out.append(f"{s.removeprefix('res://')}: footstep surface `{sid}` does not exist")
    for rule in fs.get("mesh_surfaces", {}).get("rules", []):
        if rule.get("surface") not in fs["surfaces"]:
            out.append(f"footsteps mesh rule {rule.get('match')}: surface `{rule.get('surface')}` does not exist")
    return out


def audit_ui_core() -> list[str]:
    """The sounds every menu leans on: the cursor, confirm, cancel and error rows, and each hook's rows on disk."""
    rows = _sfx_rows()
    out = [f"core ui sound: {_row_problem(rows, r)}" for r in ("ui_cursor", "ui_confirm", "ui_cancel", "ui_error")
           if _row_problem(rows, r)]
    for hook in _json(AUDIO / "ui_sfx.json").get("hooks") or []:
        for sig, rid in (hook.get("signals") or {}).items():
            if isinstance(rid, str) and rid and _row_problem(rows, rid):
                out.append(f"ui hook `{hook.get('class')}`.{sig}: {_row_problem(rows, rid)}")
    return out


SECTIONS = [("Zones", audit_zones), ("Enemies", audit_enemies), ("Battles", audit_battles), ("Intros", audit_intros),
            ("Abilities", audit_abilities),
            ("Skills", audit_skills),
            ("Cutscenes", audit_cutscenes), ("Cutscene actions", audit_cutscene_actions),
            ("Battle events", audit_battle_events), ("Footsteps", audit_footsteps), ("UI", audit_ui),
            ("UI core", audit_ui_core), ("Notes that say temp", audit_notes)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--md", action="store_true", help="print as a markdown list")
    ap.add_argument("--act", type=int, default=1, help="1 (the gate) or 2 (ADR 0203 preparation: a report, exit 0)")
    args = ap.parse_args()
    set_act(args.act)
    total = 0
    held = []
    for name, fn in SECTIONS:
        items = [i for i in fn() if i not in BY_DESIGN]
        held += [i for i in fn() if i in BY_DESIGN]
        total += len(items)
        print(f"\n## {name} ({len(items)})" if args.md else f"\n{name}: {len(items)}")
        for it in items:
            print(f"- {it}" if args.md else f"  {it}")
    print("\n## By design" if args.md else "\nBy design:")
    for it in held:
        print(f"- {it}: {BY_DESIGN[it]}" if args.md else f"  {it}: {BY_DESIGN[it]}")
    print(f"\n{total} item(s)")
    return 1 if total and ACT == 1 else 0


if __name__ == "__main__":
    sys.exit(main())
