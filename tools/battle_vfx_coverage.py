#!/usr/bin/env python3
"""Battle VFX coverage (M3-BPR-411): every skill and battle item that would play no effect.

BattleVfx.effects_for (game/vfx/battle/battle_vfx.gd) plays, per hit:
  - the map's `skills`/`items` entry (a special) when there is one;
  - `elements[element]` for damage (amount > 0), the `heal` event for a heal (amount < 0);
  - the `status` event when statuses are added; the `ko` event (or a ko_override) when the target falls.
A skill or item that deals no damage, heals nothing, adds no status and has no special (a guard, a cover, a cleanse,
an MP restore, a delay push, a summon, a field clear, a withdrawal) plays nothing: the action has no visible effect.
An element missing from `elements` falls back to `none`, which is listed too.

Usage: python3 tools/battle_vfx_coverage.py [--json]   (exit 0; it reports, the rendering track decides)
The proposal maps each gap to an effect that already exists in effects.json (library effects, palette colours only).
A revive is reported but not proposed: its hit likely carries the restored HP as a heal already (verify first).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EFFECTS = ROOT / "game/data/vfx/battle/effects.json"
SKILLS = ROOT / "game/data/battle/skills.json"
ITEMS = ROOT / "game/data/items/items.json"

# The library effect each gap category borrows (all exist in effects.json; palette colours only).
PROPOSAL = {
    "cleanse": "heal",          # a cure or a cleanse: the warm rising heal motes
    "mp": "heal",               # an MP restore: the same rise
    "delay": "status_apply",    # a pushed turn reads as a status landing
    "stance": "status_apply",   # a guard, a cover, a counter stance, a ward on the user
    "telegraph": "status_apply",  # a charge gathering (the timeline shows its intent; a boss may add its own)
    "summon": "status_apply",   # a summon (the summoned foe's own entrance plays on stage)
    "withdraw": "hit_lightning",  # Storm-Call drives foes off: the storm's own strike
    "field": "flash_toll",      # a field clear: a capped flash (safety-capped, fainter under reduced motion)
    "other": "status_apply",
}

# M3-BPR-411 fill on stage: what the choreography already plays for each gap category (the particle is still
# rendering's to add). Every gap must have one; tools/tests/test_battle_vfx_coverage.py checks it.
STAGED = {
    "telegraph": "BattleTelegraph's gather (or the boss row's own gather)",
    "summon": "the summoned foe's entrance (BattleChoreo entries)",
    "withdraw": "BattleStage's withdrawal",
    "delay": "choreo.json reaction.push (the target staggers back)",
    "cleanse": "the skill's style (support, or reaction.push when it also pushes)",
    "stance": "the guard style (the defend clip)",
    "mp": "the item style",
    "revive": "the item style",
    "field": "the skill's style",
    "other": "the skill's style",
}


def _load(p: Path) -> dict:
    return json.loads(p.read_text())


def _skill_gap(s: dict, mapped: set[str], elements: set[str]) -> str:
    """'' when the skill plays something, else its gap category."""
    if s["id"] in mapped:
        return ""
    if s.get("statuses"):
        return ""
    kind = s.get("kind", "")
    power = float(s.get("power", 0) or 0)
    if kind in ("heal",) and power > 0:
        return ""
    if kind in ("physical", "magical") and power > 0:
        return "" if s.get("element", "none") in elements else "element"
    if s.get("charge"):
        return "telegraph"
    if s.get("cleanses"):
        return "cleanse"
    if s.get("withdraws"):
        return "withdraw"
    if s.get("clears_field"):
        return "field"
    if s.get("summon"):
        return "summon"
    if s.get("delay_ranks") or s.get("pushes_ward"):
        return "delay"
    if s.get("covers") or s.get("counter") or s.get("target") == "self":
        return "stance"
    return "other"


# Gaps kept on purpose (M3-BPR-411 closed by M3-BPR-420's Act I effects): skill id -> why it plays no effect of its own.
INTENDED = {
    "toll_gather": "the Drownbell's gather plays through its own rig (BattleBossVfx on charge_started)",
    "unravel": "Act II (Ch12's cord moth), paused by ADR 0041; its effect comes with Act II",
    "voice_glimmer": "Kesh's Glimmer voice (M4-A2P-025): her six voices' effects are M3-BPR-442's",
    "cord_lift": "Hesk's cleanse (M4-A2P-024): Nhoa's, Hesk's and Ethren's effects are M3-BPR-443's",
    "nhoa_echo": "Nhoa's echo plays the copied action's effect; her own double (M4-A2P-024) is M3-BPR-443's",
}


def _item_gap(i: dict, mapped: set[str], elements: set[str]) -> str:
    if i["id"] in mapped:
        return ""
    effects = (i.get("battle") or {}).get("effects", [])
    gaps = []
    for e in effects:
        t = e.get("type", "")
        if t in ("heal_hp", "add_status"):
            return ""
        if t == "damage":
            return "" if e.get("element", "none") in elements else "element"
        gaps.append({"restore_mp": "mp", "cure": "cleanse", "revive": "revive", "delay": "delay"}.get(t, "other"))
    return gaps[0] if gaps else ""


def coverage() -> dict:
    fx = _load(EFFECTS)
    m = fx["map"]
    elements = set(m.get("elements", {}))
    skills = [s for s in _load(SKILLS)["skills"] if isinstance(s, dict)]
    items_raw = _load(ITEMS)["items"]
    items = items_raw if isinstance(items_raw, list) else [dict(id=k, **v) for k, v in items_raw.items()]
    battle_items = [i for i in items if i.get("battle")]
    out = {"skills": {}, "items": {}, "effects": sorted(fx["effects"])}
    for s in skills:
        g = _skill_gap(s, set(m.get("skills", {})), elements)
        if g:
            out["skills"][s["id"]] = g
    for i in battle_items:
        g = _item_gap(i, set(m.get("items", {})), elements)
        if g:
            out["items"][i["id"]] = g
    out["intended"] = {k: INTENDED[k] for k in out["skills"] if k in INTENDED}
    out["unexplained"] = sorted(k for k in out["skills"] if k not in INTENDED) + sorted(out["items"])
    out["proposal"] = {
        "skills": {k: PROPOSAL.get(v, PROPOSAL["other"]) for k, v in out["skills"].items() if v != "element"},
        "items": {k: PROPOSAL[v] for k, v in out["items"].items() if v in PROPOSAL},
    }
    out["staged"] = {
        "skills": {k: STAGED.get(v, "") for k, v in out["skills"].items() if v != "element"},
        "items": {k: STAGED.get(v, "") for k, v in out["items"].items()},
    }
    missing = [e for e in set(PROPOSAL.values()) if e not in fx["effects"]]
    out["proposal_missing_effects"] = sorted(missing)
    return out


def main() -> int:
    c = coverage()
    if "--json" in sys.argv:
        print(json.dumps(c, indent=2, sort_keys=True))
        return 0
    print(f"skills with no effect: {len(c['skills'])}")
    for k, v in sorted(c["skills"].items()):
        print(f"  {k}: {v} (staged: {c['staged']['skills'].get(k, '-')})")
    print(f"battle items with no effect: {len(c['items'])}")
    for k, v in sorted(c["items"].items()):
        print(f"  {k}: {v} (staged: {c['staged']['items'].get(k, '-')})")
    print(f"unexplained gaps: {len(c['unexplained'])} ({len(c['intended'])} kept on purpose, INTENDED)")
    for k in c["unexplained"]:
        print(f"  UNEXPLAINED {k}")
    if c["proposal_missing_effects"]:
        print("PROPOSAL names effects that do not exist:", c["proposal_missing_effects"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
