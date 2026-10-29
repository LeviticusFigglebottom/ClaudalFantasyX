"""Battle choreography data checks (M2-BPR-01/02/03/04): game/data/battle/choreo.json.

validate_data.py calls choreo_errors(); tools/tests/test_choreo_validate.py tests it.
Docs: docs/kb/tech/battle_presentation.md.
"""

from __future__ import annotations

CHOREO_FILE = "game/data/battle/choreo.json"
SKILLS_FILE = "game/data/battle/skills.json"
## The clip contract (game/battle/scene/battle_clips.gd BattleClips.ALL).
CLIPS = {"idle", "ready", "attack", "cast", "item", "read", "defend", "finisher", "hit", "dodge", "ko", "victory"}
TRAVELS = {"target", "step", "none"}
STYLE_TIMES = ("approach_sec", "recover_sec", "return_sec")
STYLE_SHAPES = ("lunge_m", "lift_m", "crouch_m", "lean_deg")
REACTIONS = ("damage", "heal", "miss", "push", "immune")
## M2-BPR-03: the battle camera director (game/battle/scene/battle_camera_director.gd).
CAMERA_SHOTS = ("default", "actor", "target", "cast", "finisher")
CAMERA_ANCHORS = {"actor", "strike", "target", "default"}
CAMERA_TIMES = ("blend_in_sec", "to_contact_sec", "hold_contact_sec", "blend_out_sec")
CAMERA_PLACED = ("back_m", "side_m", "up_m")
SAFE_SIDES = ("left", "right", "top", "bottom")
FOV_RANGE = (10, 90)

## M2-BPR-04 optional style shapes: name -> the least value allowed (None: any number).
STYLE_EXTRAS = {"arc_m": 0, "windup_m": None, "trace_m": None, "stagger_sec": 0, "wave_m_s": 0, "react_scale": 0}
## Accent fields (BattleChoreo.accent), every one a number; clip optional.
ACCENT_NUMS = ("lift_m", "crouch_m", "recoil_m", "tilt_deg", "sway_deg", "sways")
## Vowbound exits (BattleChoreo.leave) and entrances (BattleChoreo.enter): number fields.
EXIT_NUMS = ("delay_sec", "sec", "back_m", "depth_m", "tilt_deg")
ENTRY_NUMS = ("delay_sec", "sec", "back_m", "depth_m", "lean_deg")


def _num(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _style_errors(sid: str, st: object) -> list[str]:
    w = f"{CHOREO_FILE}: styles.{sid}"
    if not isinstance(st, dict):
        return [f"{w}: must be an object"]
    errs: list[str] = []
    for k in STYLE_TIMES:
        if not _num(st.get(k)) or st[k] < 0:
            errs.append(f"{w}.{k}: must be a number >= 0")
    if not _num(st.get("strike_sec")) or st["strike_sec"] <= 0:
        errs.append(f"{w}.strike_sec: must be a number > 0")
    if not _num(st.get("contact_at")) or not 0 < st["contact_at"] <= 1:
        errs.append(f"{w}.contact_at: must be in (0, 1]")
    for k in STYLE_SHAPES:
        if not _num(st.get(k)):
            errs.append(f"{w}.{k}: must be a number")
    travel = st.get("travel")
    if travel not in TRAVELS:
        errs.append(f"{w}.travel: must be one of {sorted(TRAVELS)}")
    elif travel == "target" and (not _num(st.get("stop_short_m")) or st["stop_short_m"] < 0):
        errs.append(f"{w}.stop_short_m: a 'target' style needs a number >= 0")
    elif travel == "step" and not _num(st.get("step_m")):
        errs.append(f"{w}.step_m: a 'step' style needs a number")
    if st.get("clip") not in CLIPS:
        errs.append(f"{w}.clip: '{st.get('clip')}' is not in the clip contract")
    for k, least in STYLE_EXTRAS.items():
        if k in st and (not _num(st[k]) or (least is not None and st[k] < least)):
            errs.append(f"{w}.{k}: must be a number" + (f" >= {least}" if least is not None else ""))
    if _num(st.get("arc_m")) and st["arc_m"] > 0 and not (_num(st.get("approach_sec")) and st["approach_sec"] > 0):
        errs.append(f"{w}.arc_m: a leap needs an approach_sec > 0 to rise in")
    if "windup_at" in st and (not _num(st["windup_at"]) or not 0 < st["windup_at"] < 1):
        errs.append(f"{w}.windup_at: must be in (0, 1)")
    strokes = st.get("trace_strokes", 1)
    if not isinstance(strokes, int) or isinstance(strokes, bool) or strokes < 1:
        errs.append(f"{w}.trace_strokes: must be a whole number >= 1 (the glyph ends on the contact)")
    if "shot" in st and not (isinstance(st["shot"], str) and st["shot"]):
        errs.append(f"{w}.shot: must be a non-empty camera framing name")
    return errs


def _accent_errors(where: str, a: object) -> list[str]:
    if not isinstance(a, dict) or not _num(a.get("sec")) or a["sec"] <= 0:
        return [f"{where}: an accent needs sec > 0"]
    errs = [f"{where}.{k}: must be a number" for k in ACCENT_NUMS if k in a and not _num(a[k])]
    if "clip" in a and a["clip"] not in CLIPS:
        errs.append(f"{where}.clip: '{a['clip']}' is not in the clip contract")
    return errs


def _move_errors(where: str, m: object, nums: tuple[str, ...]) -> list[str]:
    if not isinstance(m, dict):
        return [f"{where}: must be an object"]
    errs = [f"{where}.{k}: must be a number >= 0" for k in nums if k != "lean_deg" and k != "tilt_deg"
            and (not _num(m.get(k)) or m[k] < 0)]
    errs += [f"{where}.{k}: must be a number" for k in ("lean_deg", "tilt_deg") if k in nums and not _num(m.get(k))]
    if _num(m.get("sec")) and m["sec"] <= 0:
        errs.append(f"{where}.sec: must be > 0")
    if m.get("clip") not in CLIPS:
        errs.append(f"{where}.clip: must be a contract clip")
    if "clip_own" in m and not (isinstance(m["clip_own"], str) and m["clip_own"]):  # M3-CRE-639: a model's own clip
        errs.append(f"{where}.clip_own: must be a clip name")
    return errs


def _boss_errors(bosses: object, skill_ids: set[str]) -> list[str]:
    w = f"{CHOREO_FILE}: bosses"
    if not isinstance(bosses, dict):
        return [f"{w}: must be an object"]
    errs: list[str] = []
    for bid, b in bosses.items():
        if bid == "doc":
            continue
        if not isinstance(b, dict):
            errs.append(f"{w}.{bid}: must be an object")
            continue
        charge = b.get("charge_skill")
        if charge is not None and charge != "*" and charge not in skill_ids:  # "*": any charge (M3-BPR-408)
            errs.append(f"{w}.{bid}.charge_skill: '{charge}' is not a skill (or '*')")
        if charge is not None and "gather" not in b:
            errs.append(f"{w}.{bid}.gather: a boss with a charge_skill needs its gather accent")
        for key in ("gather", "break"):
            if key in b:
                errs += _accent_errors(f"{w}.{bid}.{key}", b.get(key))
        phases = b.get("phases", {})
        if not isinstance(phases, dict):
            errs.append(f"{w}.{bid}.phases: must be an object of phase id -> moment")
            phases = {}
        for pid, m in phases.items():
            if not isinstance(m, dict) or not ("boss" in m or "party" in m):
                errs.append(f"{w}.{bid}.phases.{pid}: needs a boss or a party accent")
                continue
            for who in ("boss", "party"):
                if who in m:
                    errs += _accent_errors(f"{w}.{bid}.phases.{pid}.{who}", m[who])
            for k in ("party_delay_sec", "stagger_sec"):
                if k in m and (not _num(m[k]) or m[k] < 0):
                    errs.append(f"{w}.{bid}.phases.{pid}.{k}: must be a number >= 0")
        f = b.get("flood")
        if f is not None:
            if not isinstance(f, dict) or not isinstance(f.get("phase"), str):
                errs.append(f"{w}.{bid}.flood: needs a phase id")
            else:
                if not _num(f.get("stagger_sec")) or f["stagger_sec"] < 0:
                    errs.append(f"{w}.{bid}.flood.stagger_sec: must be a number >= 0")
                errs += _accent_errors(f"{w}.{bid}.flood.accent", f.get("accent"))
    return errs


def _vowbound_errors(v: object) -> list[str]:
    w = f"{CHOREO_FILE}: vowbound"
    if not isinstance(v, dict):
        return [f"{w}: must be an object"]
    errs = _accent_errors(f"{w}.call", v.get("call"))
    errs += _move_errors(f"{w}.step_off", v.get("step_off"), EXIT_NUMS)
    so = v.get("step_off")
    if isinstance(so, dict) and (not _num(so.get("stagger_sec")) or so["stagger_sec"] < 0):
        errs.append(f"{w}.step_off.stagger_sec: must be a number >= 0")
    errs += _move_errors(f"{w}.entry", v.get("entry"), ENTRY_NUMS)
    for key in ("dismiss", "fall"):
        errs += _move_errors(f"{w}.{key}", v.get(key), EXIT_NUMS)
    r = v.get("return")
    if not isinstance(r, dict) or not _num(r.get("share")) or not 0 <= r["share"] <= 1:
        errs.append(f"{w}.return.share: must be in [0, 1]")
    elif not _num(r.get("stagger_sec")) or r["stagger_sec"] < 0:
        errs.append(f"{w}.return.stagger_sec: must be a number >= 0")
    return errs


def _shot_errors(sid: str, shot: object) -> list[str]:
    w = f"{CHOREO_FILE}: camera.shots.{sid}"
    if not isinstance(shot, dict):
        return [f"{w}: must be an object"]
    errs: list[str] = []
    anchor = shot.get("anchor")
    if anchor not in CAMERA_ANCHORS:
        errs.append(f"{w}.anchor: must be one of {sorted(CAMERA_ANCHORS)}")
    keys = ("push", "look_at") if anchor == "default" else CAMERA_PLACED + ("look_at",)
    for k in keys + ("look_up_m",):
        if not _num(shot.get(k)):
            errs.append(f"{w}.{k}: must be a number")
    for k in ("push", "look_at"):
        if _num(shot.get(k)) and not 0 <= shot[k] <= 1:
            errs.append(f"{w}.{k}: must be in [0, 1]")
    if anchor != "default" and _num(shot.get("side_m")) and shot["side_m"] < 0:
        errs.append(f"{w}.side_m: must be >= 0 (the viewer's side: the line is never crossed)")
    if "fov" in shot and (not _num(shot["fov"]) or not FOV_RANGE[0] <= shot["fov"] <= FOV_RANGE[1]):
        errs.append(f"{w}.fov: must be a number in {list(FOV_RANGE)}")
    return errs


def camera_errors(cam: object, styles: dict) -> list[str]:
    """Problems in choreo.json's "camera" section (M2-BPR-03)."""
    w = f"{CHOREO_FILE}: camera"
    if not isinstance(cam, dict):
        return [f"{w}: must be an object"]
    errs: list[str] = []
    for k in CAMERA_TIMES:
        if not _num(cam.get(k)) or cam[k] < 0:
            errs.append(f"{w}.{k}: must be a number >= 0")
    for k in ("default_look_m", "near_m"):
        if not _num(cam.get(k)) or cam[k] <= 0:
            errs.append(f"{w}.{k}: must be a number > 0")
    safe = cam.get("safe_frame")
    if not isinstance(safe, dict) or any(not _num(safe.get(k)) or not 0 <= safe[k] < 0.5 for k in SAFE_SIDES):
        errs.append(f"{w}.safe_frame: needs {', '.join(SAFE_SIDES)} in [0, 0.5)")
    shots = cam.get("shots")
    if not isinstance(shots, dict):
        return errs + [f"{w}.shots: must be an object"]
    for sid in CAMERA_SHOTS:
        if sid not in shots:
            errs.append(f"{w}.shots: the '{sid}' shot is missing")
    for sid, shot in shots.items():
        errs += _shot_errors(sid, shot)
    by_style = cam.get("by_style") if isinstance(cam.get("by_style"), dict) else {}
    for sid in sorted(set(styles) - set(by_style)):
        errs.append(f"{w}.by_style: style '{sid}' has no shots")
    for sid in sorted(set(by_style) - set(styles)):
        errs.append(f"{w}.by_style: '{sid}' is not a style")
    pairs = [(f"by_style.{k}", v) for k, v in by_style.items()] + [("enemy", cam.get("enemy"))]
    enemy_by_actor = cam.get("enemy_by_actor", {}) if isinstance(cam.get("enemy_by_actor", {}), dict) else {}
    for eid, pair in enemy_by_actor.items():
        if eid != "doc":
            pairs.append((f"enemy_by_actor.{eid}", pair))
    enemy_by_skill = cam.get("enemy_by_skill", {}) if isinstance(cam.get("enemy_by_skill", {}), dict) else {}
    for sid, pair in enemy_by_skill.items():  # M3-BPR-420: a boss's big moves
        if sid != "doc":
            pairs.append((f"enemy_by_skill.{sid}", pair))
    for where, pair in pairs:
        if not isinstance(pair, dict):
            errs.append(f"{w}.{where}: must be an object with lead and contact")
            continue
        for slot in ("lead", "contact"):
            shot = pair.get(slot)
            if not isinstance(shot, str) or (shot != "" and shot not in shots):
                errs.append(f"{w}.{where}.{slot}: must name a shot or be ''")
    return errs


def choreo_errors(doc: object, skills: object) -> list[str]:
    """Problems in choreo.json; `skills` is skills.json (for skill ids and kinds)."""
    if not isinstance(doc, dict) or not isinstance(doc.get("choreo"), dict):
        return [f"{CHOREO_FILE}: needs a 'choreo' object"]
    c = doc["choreo"]
    errs: list[str] = []
    styles = c.get("styles")
    if not isinstance(styles, dict) or "melee" not in styles:
        return [f"{CHOREO_FILE}: styles must be an object with the 'melee' fallback"]
    for sid, st in styles.items():
        errs += _style_errors(sid, st)
    rows = skills.get("skills", []) if isinstance(skills, dict) else []
    skill_ids = {str(r.get("id")) for r in rows if isinstance(r, dict)}
    kinds = {str(r.get("kind")) for r in rows if isinstance(r, dict)}
    for section in ("style_by_kind", "style_by_target", "style_by_skill"):
        table = c.get(section)
        if not isinstance(table, dict):
            errs.append(f"{CHOREO_FILE}: {section} must be an object")
            continue
        for key, sid in table.items():
            if sid not in styles:
                errs.append(f"{CHOREO_FILE}: {section}.{key} names an unknown style '{sid}'")
            if section == "style_by_skill" and key not in skill_ids:
                errs.append(f"{CHOREO_FILE}: style_by_skill names an unknown skill '{key}'")
    by_actor = c.get("style_by_actor", {})
    for actor, table in (by_actor.items() if isinstance(by_actor, dict) else []):
        if actor == "doc":
            continue
        for kind, sid in (table.items() if isinstance(table, dict) else []):
            if sid not in styles:
                errs.append(f"{CHOREO_FILE}: style_by_actor.{actor}.{kind} names an unknown style '{sid}'")
    swells = c.get("swell_style_by_hero", {})
    for hero, sid in (swells.items() if isinstance(swells, dict) else []):  # M3-BPR-422
        if hero != "doc" and sid not in styles:
            errs.append(f"{CHOREO_FILE}: swell_style_by_hero.{hero} names an unknown style '{sid}'")
    by_kind = c.get("style_by_kind") if isinstance(c.get("style_by_kind"), dict) else {}
    for kind in sorted(kinds - set(by_kind)):
        errs.append(f"{CHOREO_FILE}: style_by_kind has no style for skill kind '{kind}'")
    if c.get("item_style") not in styles:
        errs.append(f"{CHOREO_FILE}: item_style must name a style")
    reaction = c.get("reaction") if isinstance(c.get("reaction"), dict) else {}
    for kind in REACTIONS:
        r = reaction.get(kind)
        if not isinstance(r, dict) or not _num(r.get("sec")) or r["sec"] < 0 or r.get("clip") not in CLIPS:
            errs.append(f"{CHOREO_FILE}: reaction.{kind} needs sec >= 0 and a contract clip")
    for block, keys in (("ko", ("delay_sec", "collapse_sec", "tilt_deg", "drop_m")), ("enter", ("back_m", "sec"))):
        b = c.get(block)
        if not isinstance(b, dict) or any(not _num(b.get(k)) or b[k] < 0 for k in keys):
            errs.append(f"{CHOREO_FILE}: {block} needs numbers >= 0 for {', '.join(keys)}")
        elif b.get("clip") not in CLIPS:
            errs.append(f"{CHOREO_FILE}: {block}.clip must be a contract clip")
    if "bosses" in c:
        errs += _boss_errors(c["bosses"], skill_ids)
    if "telegraph" in c:  # M3-BPR-413
        t = c["telegraph"]
        errs += _accent_errors(f"{CHOREO_FILE}: telegraph.gather", t.get("gather") if isinstance(t, dict) else None)
    if "vowbound" in c:
        errs += _vowbound_errors(c["vowbound"])
    if not _num(c.get("settle_sec")) or c["settle_sec"] < 0:
        errs.append(f"{CHOREO_FILE}: settle_sec must be a number >= 0")
    rm = c.get("reduced_motion")
    if not isinstance(rm, dict) or any(not _num(rm.get(k)) or not 0 <= rm[k] <= 1 for k in
                                       ("travel_scale", "lean_scale", "tilt_scale")):
        errs.append(f"{CHOREO_FILE}: reduced_motion scales must be numbers in [0, 1]")
    outro = c.get("outro")
    if not isinstance(outro, dict) or not _num(outro.get("settle_sec")) or outro["settle_sec"] < 0:
        errs.append(f"{CHOREO_FILE}: outro needs settle_sec >= 0")
    else:
        for kind, extra in (("victory", ("hops", "hop_m")), ("escape", ("back_m",))):
            o = outro.get(kind)
            keys = ("delay_sec", "sec", "stagger_sec") + extra
            if not isinstance(o, dict) or any(not _num(o.get(k)) or o[k] < 0 for k in keys) or o.get("clip") not in CLIPS:
                errs.append(f"{CHOREO_FILE}: outro.{kind} needs numbers >= 0 for {', '.join(keys)} and a contract clip")
    sp = c.get("speeds")
    if not isinstance(sp, dict) or not _num(sp.get("min")) or not _num(sp.get("max")) or not 0 < sp["min"] <= sp["max"]:
        errs.append(f"{CHOREO_FILE}: speeds needs 0 < min <= max")
    errs += camera_errors(c.get("camera"), styles)
    if "placeholder_clips" in c:
        errs += placeholder_errors(c["placeholder_clips"])
    if "impact" in c:
        errs += impact_errors(c["impact"])
    sp_ = c.get("spacing")
    if sp_ is not None and (not isinstance(sp_, dict) or not _num(sp_.get("clearance_m")) or sp_["clearance_m"] < 0
                            or not _num(sp_.get("footprint_k", 1.0)) or sp_.get("footprint_k", 1.0) <= 0):
        errs.append(f"{CHOREO_FILE}: spacing needs clearance_m >= 0 and footprint_k > 0")
    return errs


def _pair(v: object, lo: float = 0.0) -> bool:
    return isinstance(v, list) and len(v) == 2 and all(_num(x) and x >= lo for x in v) and v[0] <= v[1]


def impact_errors(imp: object) -> list[str]:
    """M3-BPR-401 BattleImpact: strengths in (0, 1], hit-stop 0-6 frames, a capped flash, reduced-motion scales."""
    w = f"{CHOREO_FILE}: impact"
    if not isinstance(imp, dict):
        return [f"{w} must be an object"]
    errs: list[str] = []
    for k in ("full_frac", "stop_fps"):
        if not _num(imp.get(k)) or imp[k] <= 0:
            errs.append(f"{w}.{k} must be a number > 0")
    for k in ("crit_bonus", "heavy_strength", "shake_min_strength"):
        if not _num(imp.get(k)) or not 0 <= imp[k] <= 1:
            errs.append(f"{w}.{k} must be a number in [0, 1]")
    frames = imp.get("hit_stop_frames")
    if not _pair(frames) or frames[1] > 6:
        errs.append(f"{w}.hit_stop_frames must be [lo, hi] frames with 0 <= lo <= hi <= 6")
    for k in ("shake_scale", "recoil_scale"):
        if not _pair(imp.get(k)):
            errs.append(f"{w}.{k} must be [lo, hi] with 0 <= lo <= hi")
    fl = imp.get("flash")
    if not isinstance(fl, dict) or not _pair(fl.get("energy")) or not _num(fl.get("energy_cap")) \
            or fl["energy"][1] > fl["energy_cap"] or any(not _num(fl.get(k)) or fl[k] <= 0 for k in
                                                         ("range_m", "height_frac", "sec")):
        errs.append(f"{w}.flash needs energy [lo, hi] <= energy_cap, and range_m, height_frac, sec > 0")
    elif not isinstance(fl.get("color"), str) or not fl["color"].startswith("#"):
        errs.append(f"{w}.flash.color must be a #hex color")
    sm = imp.get("ko_slowmo")
    if not isinstance(sm, dict) or not _num(sm.get("factor")) or not 0 < sm["factor"] <= 1 \
            or any(not _num(sm.get(k)) or sm[k] < 0 for k in ("lead_sec", "sec")):
        errs.append(f"{w}.ko_slowmo needs factor in (0, 1] and lead_sec, sec >= 0")
    rm = imp.get("reduced_motion")
    if not isinstance(rm, dict) or any(not _num(rm.get(k)) or not 0 <= rm[k] <= 1 for k in
                                       ("shake_scale", "flash_scale", "slowmo_factor")) or rm.get("slowmo_factor") == 0:
        errs.append(f"{w}.reduced_motion needs shake_scale, flash_scale in [0, 1] and slowmo_factor in (0, 1]")
    return errs


# --- M2-BPR-10: placeholder hero clips (choreo.json placeholder_clips; BattlePlaceholderClips) -------------


def _euler(v: object) -> bool:
    return isinstance(v, list) and len(v) == 3 and all(_num(x) for x in v)


def _pose_errors(w: str, pose: object, roles: set[str]) -> list[str]:
    if not isinstance(pose, dict):
        return [f"{w}: must be an object of role -> [x, y, z] degrees"]
    errs: list[str] = []
    for role, v in pose.items():
        if role not in roles:
            errs.append(f"{w}.{role}: not a role in placeholder_clips.bones")
        elif not _euler(v):
            errs.append(f"{w}.{role}: must be [x, y, z] degrees")
    return errs


def placeholder_errors(pc: object) -> list[str]:
    """Problems in placeholder_clips: every contract clip has a row, roles have bone names, lengths are positive,
    key times lie within the clip, poses name known roles as [x, y, z]."""
    w = f"{CHOREO_FILE}: placeholder_clips"
    if not isinstance(pc, dict):
        return [f"{w}: must be an object"]
    errs: list[str] = []
    bones = pc.get("bones")
    if not isinstance(bones, dict) or not bones:
        return [f"{w}.bones: needs role -> [bone names]"]
    for role, names in bones.items():
        if not isinstance(names, list) or not names or not all(isinstance(n, str) and n for n in names):
            errs.append(f"{w}.bones.{role}: needs a non-empty list of bone names")
    roles = set(bones)
    mr = pc.get("min_roles")
    if not isinstance(mr, int) or isinstance(mr, bool) or not 1 <= mr <= len(roles):
        errs.append(f"{w}.min_roles: must be an integer in [1, {len(roles)}]")
    errs += _pose_errors(f"{w}.base", pc.get("base", {}), roles)
    clips = pc.get("clips")
    if not isinstance(clips, dict):
        return errs + [f"{w}.clips: must be an object"]
    for name in sorted(CLIPS - set(clips)):
        errs.append(f"{w}.clips: no placeholder for contract clip '{name}'")
    for name, clip in clips.items():
        cw = f"{w}.clips.{name}"
        if name not in CLIPS:
            errs.append(f"{cw}: not a contract clip")
        if not isinstance(clip, dict):
            errs.append(f"{cw}: must be an object")
            continue
        length = clip.get("length_sec")
        if not _num(length) or length <= 0:
            errs.append(f"{cw}.length_sec: must be a number > 0")
            length = None
        if not isinstance(clip.get("loop"), bool):
            errs.append(f"{cw}.loop: must be true or false")
        keys = clip.get("keys")
        if not isinstance(keys, list) or not keys:
            errs.append(f"{cw}.keys: needs at least one key")
            continue
        for i, key in enumerate(keys):
            kw = f"{cw}.keys[{i}]"
            if not isinstance(key, dict):
                errs.append(f"{kw}: must be an object")
                continue
            t = key.get("t")
            if not _num(t) or t < 0 or (length is not None and t > length):
                errs.append(f"{kw}.t: must be a time within [0, length_sec]")
            if "pose" in key:
                errs += _pose_errors(f"{kw}.pose", key["pose"], roles)
            if "hips_m" in key and not _euler(key["hips_m"]):
                errs.append(f"{kw}.hips_m: must be [x, y, z] metres")
    return errs


# --- M2-BPR-07: per-encounter arenas (game/data/battle/arenas.json) ----------------------------

ARENAS_FILE = "game/data/battle/arenas.json"
ENCOUNTERS_FILE = "game/data/battle/encounters.json"


def arena_errors(doc: object, encounters: object, scene_exists) -> list[str]:
    """Problems in arenas.json and the encounters' `arena` fields; `scene_exists(res_path)` says whether a scene is there."""
    if not isinstance(doc, dict) or not isinstance(doc.get("arenas"), dict):
        return [f"{ARENAS_FILE}: needs an 'arenas' object"]
    scenes = doc["arenas"].get("scenes")
    if not isinstance(scenes, dict):
        return [f"{ARENAS_FILE}: needs a 'scenes' object"]
    errs: list[str] = []
    for sid, path in scenes.items():
        if not isinstance(path, str) or not path.endswith(".tscn") or not scene_exists(path):
            errs.append(f"{ARENAS_FILE}: scenes.{sid} names a missing scene '{path}'")
    staging = doc["arenas"].get("staging", {})
    for aid, st in (staging.items() if isinstance(staging, dict) else []):
        if aid == "doc":
            continue
        if aid not in scenes:
            errs.append(f"{ARENAS_FILE}: staging names an unknown arena '{aid}'")
        elif not isinstance(st, dict) or any(not _num(st.get(k, 1.0)) or st.get(k, 1.0) <= 0 for k in ("travel_scale", "tempo")):
            errs.append(f"{ARENAS_FILE}: staging.{aid} needs travel_scale and tempo > 0")
    rows = encounters.get("encounters", []) if isinstance(encounters, dict) else []
    for r in rows:
        if isinstance(r, dict) and "arena" in r and r["arena"] not in scenes:
            errs.append(f"{ENCOUNTERS_FILE}: {r.get('id')}.arena names an unknown arena '{r['arena']}'")
    return errs


# --- M2-BPR-08: C10, the first-call cinematic (choreo.json summon_cinematic) ---------------------

FLAGS_FILE = "game/data/flags.tres"


def declared_flags(text: str) -> set[str]:
    """Flag names declared in flags.tres (its `flags = { "name": "doc", ... }` dictionary)."""
    import re

    return set(re.findall(r'^"([a-z0-9_]+)":', text, re.M))


def summon_errors(doc: object, flags: set[str]) -> list[str]:
    """Problems in choreo.json summon_cinematic: its seen-flags declared, its numbers, its entry."""
    c = doc.get("choreo", {}) if isinstance(doc, dict) else {}
    s = c.get("summon_cinematic")
    w = f"{CHOREO_FILE}: summon_cinematic"
    if not isinstance(s, dict):
        return [f"{w}: missing"]
    errs: list[str] = []
    fl = s.get("first_call_flags")
    if not isinstance(fl, dict) or not fl:
        errs.append(f"{w}.first_call_flags: needs at least one Vowbound -> flag")
    else:
        errs += [f"{w}.first_call_flags.{v}: flag '{f}' is not declared in {FLAGS_FILE}" for v, f in fl.items() if f not in flags]
    for k in ("hold_sec", "light_energy", "light_at_sec", "light_in_sec", "light_range_m", "light_height_m",
              "camera_in_sec", "camera_out_sec"):
        if not _num(s.get(k)) or s[k] < 0:
            errs.append(f"{w}.{k}: must be a number >= 0")
    for key in ("entry", "off_entry"):
        e = s.get(key)
        if not isinstance(e, dict) or any(not _num(e.get(k)) or e[k] < 0 for k in ENTRY_NUMS) or e.get("clip") not in CLIPS:
            errs.append(f"{w}.{key}: needs numbers >= 0 for {', '.join(ENTRY_NUMS)} and a contract clip")
    if "summon" not in (c.get("camera", {}).get("shots", {}) if isinstance(c.get("camera"), dict) else {}):
        errs.append(f"{CHOREO_FILE}: camera.shots needs the 'summon' shot")
    return errs


# --- M3-BPR-02: boss intros (choreo.json boss_intro) ------------------------------------------------

BOSS_INTRO_TIMES = ("camera_in_sec", "camera_out_sec", "card_at_sec", "card_in_sec", "card_out_sec", "rise_px",
                    "reveal_wait_max_sec")
BOSS_INTRO_CARD_NUMS = ("title_height", "rule_y", "rule_length", "rule_px", "band_alpha", "band_fade")
BOSS_INTRO_ROW_KEYS = ("title_key", "epithet_key")


def boss_intro_errors(doc: object, encounters: object, loc_keys: set[str]) -> list[str]:
    """Problems in choreo.json boss_intro: its times, the card, and per encounter a real encounter listing the row's
    enemy, a camera shot that exists, hold_sec > 0 (the card fits in it), loc keys that exist, a boolean on_retry."""
    c = doc.get("choreo", {}) if isinstance(doc, dict) else {}
    b = c.get("boss_intro")
    w = f"{CHOREO_FILE}: boss_intro"
    if b is None:
        return []
    if not isinstance(b, dict):
        return [f"{w}: must be an object"]
    errs = [f"{w}.{k}: must be a number >= 0" for k in BOSS_INTRO_TIMES if not _num(b.get(k)) or b[k] < 0]
    card = b.get("card")
    if not isinstance(card, dict):
        errs.append(f"{w}.card: must be an object")
    else:
        rect = card.get("rect")
        if not isinstance(rect, list) or len(rect) != 4 or not all(_num(v) and v >= 0 for v in rect):
            errs.append(f"{w}.card.rect: needs [x, y, w, h], numbers >= 0")
        if not isinstance(card.get("layer"), int) or isinstance(card.get("layer"), bool):
            errs.append(f"{w}.card.layer: must be a whole number")
        for k in ("title_variation", "epithet_variation"):
            if not isinstance(card.get(k), str) or not card[k]:
                errs.append(f"{w}.card.{k}: must name a theme label variation")
        errs += [f"{w}.card.{k}: must be a number >= 0" for k in BOSS_INTRO_CARD_NUMS
                 if not _num(card.get(k)) or card[k] < 0]
        if _num(card.get("band_alpha")) and card["band_alpha"] > 1:
            errs.append(f"{w}.card.band_alpha: must be in [0, 1]")
    rows = b.get("rows")
    if not isinstance(rows, dict) or not rows:
        return errs + [f"{w}.rows: needs at least one encounter"]
    cam = c.get("camera") if isinstance(c.get("camera"), dict) else {}
    shots = cam.get("shots") if isinstance(cam.get("shots"), dict) else {}
    enc_rows = encounters.get("encounters", []) if isinstance(encounters, dict) else []
    enc = {str(r.get("id")): r for r in enc_rows if isinstance(r, dict)}
    card_sec = sum(b[k] for k in ("card_at_sec", "card_in_sec", "card_out_sec") if _num(b.get(k)))
    for eid, row in rows.items():
        where = f"{w}.rows.{eid}"
        if not isinstance(row, dict):
            errs.append(f"{where}: must be an object")
            continue
        if eid not in enc:
            errs.append(f"{where}: '{eid}' is not an encounter")
        elif row.get("enemy") not in enc[eid].get("enemies", []):
            errs.append(f"{where}.enemy: '{row.get('enemy')}' is not in the encounter")
        if row.get("shot") not in shots:
            errs.append(f"{where}.shot: '{row.get('shot')}' is not a camera shot")
        hold = row.get("hold_sec")
        if not _num(hold) or hold <= 0:
            errs.append(f"{where}.hold_sec: must be a number > 0")
        elif _num(b.get("camera_in_sec")) and b["camera_in_sec"] + hold < card_sec:
            errs.append(f"{where}.hold_sec: the card's fade in and out must fit before the camera turns home")
        for k in BOSS_INTRO_ROW_KEYS:
            if not isinstance(row.get(k), str) or row[k] not in loc_keys:
                errs.append(f"{where}.{k}: '{row.get(k)}' has no localization entry")
        if "on_retry" in row and not isinstance(row["on_retry"], bool):
            errs.append(f"{where}.on_retry: must be true or false")
    return errs
