"""Battle choreography data checks (M2-BPR-01/02): game/data/battle/choreo.json.

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
REACTIONS = ("damage", "heal", "miss")


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
    if not _num(c.get("settle_sec")) or c["settle_sec"] < 0:
        errs.append(f"{CHOREO_FILE}: settle_sec must be a number >= 0")
    rm = c.get("reduced_motion")
    if not isinstance(rm, dict) or any(not _num(rm.get(k)) or not 0 <= rm[k] <= 1 for k in
                                       ("travel_scale", "lean_scale", "tilt_scale")):
        errs.append(f"{CHOREO_FILE}: reduced_motion scales must be numbers in [0, 1]")
    sp = c.get("speeds")
    if not isinstance(sp, dict) or not _num(sp.get("min")) or not _num(sp.get("max")) or not 0 < sp["min"] <= sp["max"]:
        errs.append(f"{CHOREO_FILE}: speeds needs 0 < min <= max")
    return errs
