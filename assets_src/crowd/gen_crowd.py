#!/usr/bin/env python3
"""Act I's crowd generator (M3-CRE-659, ADR 0152). Pure Python + numpy, deterministic and seeded.

    python3 assets_src/crowd/gen_crowd.py           # writes params/<body>.json and fills crowd.json
    python3 assets_src/crowd/gen_crowd.py --check   # exit 1 if either would change

Inputs: the roster `game/data/world/npc/crowd.json` (each person's zone, stage actor, role, community, age band, sex
and build, plus the `bodies` plan) and the range tables `assets_src/crowd/ranges.json` (per community: skin, hair
and cloth; per role: kits, work clip and cloth; per age band, sex and build: body and face slider ranges; per kit:
the villager_costume pieces). Outputs:

* `assets_src/crowd/params/<body>.json`, one per planned body, in the characters' villager schema
  (assets_src/characters/villagers/params: the bb_params block plus `_skin`, `_hair`, `_eyes`, `_costume`,
  `_tints`, `_build`, `_persona`; plus `_work`, the work clips its wearers play), which build_crowd.py feeds to the characters' modules unchanged. Each face is
  rejection-sampled away from every Haluna villager's (M3-CHR-100: crowd bodies are new people) and from the other
  crowd faces of its age band.
* In crowd.json, each person's `island` (from the community), `body` (assign), `tints` (cloth_a/b/c and hair) and
  `work`. A body must match the person's age band and sex, come from a community theirs accepts and be unused in
  the zone so far (so no body repeats within a zone); tints are two-swatch palette mixes, redrawn until they stand
  apart from every other person wearing the same body.
"""
from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import validate_npc as vn  # noqa: E402  (skin_delta_e: the one metric the generator and the validator share)

RANGES = HERE / "ranges.json"
ROSTER = ROOT / "game" / "data" / "world" / "npc" / "crowd.json"
PARAMS_DIR = HERE / "params"
PALETTE = ROOT / "docs" / "kb" / "art" / "palette.json"
HALUNA_PARAMS = ROOT / "assets_src" / "characters" / "villagers" / "params"
TINT_SLOTS = ("cloth_a", "cloth_b", "cloth_c")
CLOTH_KEYS = {"cloth_a": "a", "cloth_b": "b", "cloth_c": "c"}
ORDER_KIT = "robe"
ORDER_COMMUNITY = "order"
LEATHER = "#FFFFFF"  # the villagers' untinted leather (write_materials: a white col_albedo)
PERSON_KEYS = ("id", "zone", "stage_actor", "role", "island", "community", "age_band", "sex", "build", "body", "tints",
               "work", "about")
DIGITS = 4
FINE_DIGITS = 5  # metres of mouth_corner_lift and canthus_offset_m


def seed_of(*parts: object) -> int:
    return zlib.crc32("/".join(str(p) for p in parts).encode("utf-8"))


def rng_for(*parts: object) -> np.random.Generator:
    return np.random.default_rng(seed_of(*parts))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(data: object) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------------------------
# colour
# ---------------------------------------------------------------------------------------------
class Palette:
    def __init__(self, path: Path = PALETTE) -> None:
        self.hex = {k: v["hex"] for k, v in load_json(path)["swatches"].items()}

    def rgb(self, name: str) -> np.ndarray:
        h = name if name.startswith("#") else self.hex[name]
        return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)

    def mix(self, a: str, b: str, t: float) -> str:
        return to_hex(self.rgb(a) + (self.rgb(b) - self.rgb(a)) * t)


def to_hex(c: np.ndarray) -> str:
    c = np.clip(np.round(c), 0, 255).astype(int)
    return "#{:02X}{:02X}{:02X}".format(*c)


def rgb_of(h: str) -> np.ndarray:
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)


def tint_distance(a: dict, b: dict) -> float:
    """How far apart two people's dress reads: the largest RGB distance over the cloth slots."""
    return max(float(np.linalg.norm(rgb_of(a[s]) - rgb_of(b[s]))) for s in TINT_SLOTS)


def draw_mix(pal: Palette, specs: list, rng: np.random.Generator) -> tuple[str, list]:
    a, b, lo, hi = specs[int(rng.integers(len(specs)))]
    t = float(rng.uniform(lo, hi))
    return pal.mix(a, b, t), [a, b, t]


def skin_d(clear: dict, cloth: str, skin: str) -> float:
    return vn.skin_delta_e(cloth, skin, float(clear["k_l"]), float(clear["k_h"]))


def draw_cloth(pal: Palette, sets: dict, key: str, rng: np.random.Generator, skin: str, clear: dict,
               who: str) -> str:
    """A cloth mix for set `key` at least clear["floor"] (skin_delta_e, ranges.json skin_clearance) from the
    wearer's skin, so cloth never reads as bare skin. Widening, in order, never keeping a miss: `tries` draws from
    the slot's own mixes; as many from each of the community's other sets; each of the slot's swatches mixed toward
    the dark or the light swatch (away from the skin's lightness first) by each widening step. None: an error
    naming `who`."""
    floor = float(clear["floor"])
    tries = int(clear["tries"])
    for k in [key] + sorted(s for s in sets if s != key):
        for _ in range(tries):
            c = draw_mix(pal, sets[k], rng)[0]
            if skin_d(clear, c, skin) >= floor:
                return c
    w = clear["widen"]
    skin_l = vn.srgb_to_lab(skin)[0]
    swatches = list(dict.fromkeys(s for spec in sets[key] for s in spec[:2]))
    for step in w["steps"]:
        for s in swatches:
            lighter = vn.srgb_to_lab(to_hex(pal.rgb(s)))[0] >= skin_l
            tones = (w["light"], w["dark"]) if lighter else (w["dark"], w["light"])
            for tone in tones:
                c = pal.mix(s, tone, float(step))
                if skin_d(clear, c, skin) >= floor:
                    return c
    raise SystemExit(f"gen_crowd: no cloth for {who} ({key}) clears skin_delta_e {floor} from skin {skin}")


# ---------------------------------------------------------------------------------------------
# draws
# ---------------------------------------------------------------------------------------------
def draw(v: object, rng: np.random.Generator, digits: int = DIGITS) -> object:
    """[lo, hi] numbers -> a draw (ints stay ints); a list of strings -> a choice; [[lo, hi], ...] -> each drawn;
    anything else as is."""
    if isinstance(v, list) and v and all(isinstance(x, list) for x in v):
        return [draw(x, rng, digits) for x in v]
    if isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v):
        lo, hi = v
        if isinstance(lo, int) and isinstance(hi, int):
            return int(rng.integers(lo, hi + 1))
        return round(float(rng.uniform(lo, hi)), digits)
    if isinstance(v, list) and v and all(isinstance(x, str) for x in v):
        return v[int(rng.integers(len(v)))]
    return v


def lerp_table(a: dict, b: dict, u: float) -> dict:
    return {k: a[k] + (b[k] - a[k]) * u for k in a}


# ---------------------------------------------------------------------------------------------
# bodies
# ---------------------------------------------------------------------------------------------
FACE_KEYS = ("eye_tilt_deg", "jaw_width", "cheekbone_height", "cheekbone_width", "chin_size", "nose_bridge_width",
             "nose_tip_projection", "lip_fullness", "lip_lower_fullness", "mouth_corner_lift", "brow_ridge",
             "canthus_offset_m", "donor_mix_african", "donor_mix_asian", "donor_mix_caucasian")
BODY_ORDER = ("height_m", "heads_tall", "shoulder_width_heads", "chest_width_heads", "chest_depth_heads",
              "waist_width_heads", "hip_width_heads", "crotch_height_heads", "arm_span_ratio", "hand_length_heads",
              "foot_length_ratio", "neck_length_heads", "neck_width_ratio", "head_width_ratio", "femininity", "muscle",
              "mass", "breast", "eye_scale", "ipd_m", "arm_abduction_deg")
FACE_ORDER = ("eye_tilt_deg", "canthus_offset_m", "jaw_width", "cheekbone_height", "cheekbone_width", "chin_size",
              "nose_bridge_width", "nose_tip_projection", "lip_fullness", "lip_close", "lip_seal", "lip_lower_fullness",
              "mouth_corner_lift", "brow_ridge", "donor_mix_african", "donor_mix_asian", "donor_mix_caucasian")
BB_DEFAULT_FACE = {"canthus_offset_m": 0.0}


def face_scale(ranges: dict) -> dict:
    adult = ranges["face"]["adult"]
    return {k: float(adult[k][1] - adult[k][0]) for k in FACE_KEYS}


def face_distance(a: dict, b: dict, scale: dict) -> float:
    """Root mean square difference over the face sliders, each in units of its adult range."""
    d = [((float(a.get(k, BB_DEFAULT_FACE.get(k, 0.0))) - float(b.get(k, BB_DEFAULT_FACE.get(k, 0.0)))) / scale[k]) ** 2
         for k in FACE_KEYS]
    return float(np.sqrt(np.mean(d)))


def haluna_faces() -> dict[str, dict]:
    return {p.stem: load_json(p) for p in sorted(HALUNA_PARAMS.glob("*.json"))}


def body_sliders(ranges: dict, plan: dict, rng: np.random.Generator) -> dict:
    band, sex, build = plan["age_band"], plan["sex"], plan["build"]
    tb = ranges["body"]
    out: dict = {}
    if band == "child":
        t = tb["child"]
        u = float(rng.uniform(*plan["growth"]))
        out = lerp_table(t["young"], t["old"], u)
        for k, j in t["jitter"].items():
            out[k] += float(rng.uniform(-j, j))
        out["femininity"] = float(rng.uniform(*t["femininity"][sex]))
        out["breast"] = out["breast"] * u * float(t["breast_scale"][sex])
    else:
        rows = {**tb["adult"]["shared"], **tb["adult"][sex][build]}
        out = {k: float(rng.uniform(*v)) for k, v in rows.items()}
        if band == "elder":
            out["height_m"] *= float(rng.uniform(*tb["elder"]["height_scale"]))
            out["neck_length_heads"] = float(rng.uniform(*tb["elder"]["neck_length_heads"]))
    out["arm_abduction_deg"] = float(ranges["face"]["fixed"]["arm_abduction_deg"])
    return {k: round(float(out[k]), DIGITS) for k in BODY_ORDER}


def face_sliders(ranges: dict, plan: dict, rng: np.random.Generator) -> dict:
    tf = ranges["face"]
    band, sex = plan["age_band"], plan["sex"]
    rows = dict(tf["adult"] if band != "child" else tf["child"])
    rows.pop("female", None)
    if band != "child" and sex == "female":
        rows.update(tf["adult"]["female"])
    if band == "elder":
        rows.update(tf["elder"])
    out = {}
    for k in FACE_KEYS:
        lo, hi = rows[k]
        fine = k in ("mouth_corner_lift", "canthus_offset_m")
        out[k] = round(float(rng.uniform(lo, hi)), FINE_DIGITS if fine else DIGITS)
    out.update({k: v for k, v in tf["fixed"].items() if k != "arm_abduction_deg"})
    return {k: out[k] for k in FACE_ORDER}


def pick_face(ranges: dict, bid: str, plan: dict, taken: list[dict], haluna: dict, scale: dict) -> dict:
    """The first draw (of up to 64) at least face_min_distance from every Haluna face and every crowd face of the
    band so far; else the farthest draw."""
    need = float(ranges["face"]["face_min_distance"])
    best, best_d = None, -1.0
    for attempt in range(64):
        f = face_sliders(ranges, plan, rng_for(bid, "face", attempt))
        d = min([face_distance(f, h, scale) for h in haluna.values()] + [face_distance(f, o, scale) for o in taken])
        if d >= need:
            return f
        if d > best_d:
            best, best_d = f, d
    return best


def lip_of(ranges: dict, skin_hex: str) -> str:
    return to_hex(rgb_of(skin_hex) * np.array(ranges["lip_scale"]))


def hair_block(ranges: dict, pal: Palette, bid: str, plan: dict, comm: dict, rng: np.random.Generator) -> tuple:
    kind = plan["hair"]
    spec = ranges["hair"][kind]
    hp: dict = {"kind": kind}
    if kind in ("short", "cropped"):
        hp["hairline"] = "female" if plan["sex"] == "female" else "male"
    elif plan["sex"] == "male":
        hp["hairline"] = "male"
    hp["seed"] = seed_of(bid, "hair") % 1000
    for k, v in spec.items():
        hp[k] = draw(v, rng)
    if kind == "cropped" and plan["sex"] == "female":
        hp["recede"] = 0.0
    elder = plan["age_band"] == "elder"
    mixes = ranges["hair_greys"] if elder else comm["hair"]
    a, b, lo, hi = mixes[int(rng.integers(len(mixes)))]
    t = float(rng.uniform(lo, hi))
    colour = pal.mix(a, b, t)
    hp["colour"] = colour
    if elder:
        hp["grey"] = pal.mix(a, b, min(1.0, t + 0.18))
        hp["grey_share"] = round(float(rng.uniform(0.35, 0.65)), 2)
        hp["brow"] = pal.mix(a, b, max(0.0, t - 0.15))
    elif plan["age_band"] == "adult" and rng.random() < 0.3:
        hp["grey"] = pal.mix("hair_black", "gauze_white", 0.55)
        hp["grey_share"] = round(float(rng.uniform(0.04, 0.12)), 2)
    hp["underpaint"] = to_hex(rgb_of(colour) * 0.85)
    return hp, [a, b, t]


def costume(ranges: dict, plan: dict, rng: np.random.Generator) -> dict:
    kit = ranges["kits"][plan["kit"]]
    out: dict = {}
    for name, spec in kit.items():
        if name.startswith("_"):
            continue
        optional = name.startswith("?")
        key = name.lstrip("?")
        if optional and rng.random() < 0.5:
            continue
        if isinstance(spec, dict):
            piece = {k: draw(v, rng) for k, v in spec.items()}
            if key in ("skirt", "apron", "headwrap"):
                piece["seed"] = int(rng.integers(1, 100))
            out[key] = piece
        else:
            out[key] = spec
    return out


def body_params(ranges: dict, pal: Palette, bid: str, plan: dict, face: dict) -> tuple[dict, list]:
    """The body's params file and its hair mix [swatch_a, swatch_b, t] (people's hair tints move along it)."""
    rng = rng_for(bid, "body")
    comm = ranges["communities"][plan["community"]]
    band, sex = plan["age_band"], plan["sex"]
    sliders = body_sliders(ranges, plan, rng)
    skin_t = float(rng.uniform(0.0, 1.0))
    skin_hex = pal.mix(comm["skin"][0], comm["skin"][1], skin_t)
    sk_r = ranges["skin"]
    skin: dict = {"hex": skin_hex, "age": round(float(rng.uniform(*sk_r["age"][band])), 2), "freckles": 0}
    bands = comm["reach_bands"].get(band, [0, 0]) if band != "child" else [0, 0]
    left = int(rng.integers(bands[0], bands[1] + 1))
    skin["reach_bands"] = {"L": left, "R": max(0, left - int(rng.integers(0, 2)))}
    if left:
        skin["ink_opacity"] = round(float(rng.uniform(*sk_r["ink_opacity"])) - (0.12 if band == "elder" else 0.0), 2)
    if band != "child" and sex == "male":
        stub = float(rng.uniform(*sk_r["stubble"][sex]))
        if stub > sk_r["stubble_share"] * sk_r["stubble"][sex][1]:
            skin["stubble"] = round(stub, 2)
            if band == "elder":
                skin["stubble_grey"] = 0.6
    if band == "elder" and sex == "male":
        skin["scalp_density"] = round(float(rng.uniform(*sk_r["elder_scalp_density"])), 2)
    skin["lip"] = lip_of(ranges, skin_hex)
    skin["seed"] = seed_of(bid, "skin") % 1000
    hair, hair_mix = hair_block(ranges, pal, bid, plan, comm, rng)
    iris_a, iris_b = ranges["iris"][0]
    trng = rng_for(bid, "tints")  # its own stream: the default tints never move the body draws
    tints = {s: draw_cloth(pal, comm["cloth"], CLOTH_KEYS[s], trng, skin_hex, ranges["skin_clearance"],
                           f"body {bid}") for s in TINT_SLOTS}
    tints["leather"] = LEATHER
    pr = ranges["persona"][band]
    persona = {"sway": round(float(rng.uniform(*pr["sway"])), 2), "lean": round(float(rng.uniform(*pr["lean"])), 2),
               "arms_down": round(float(rng.uniform(*pr["arms_down"])), 1)}
    cos = costume(ranges, plan, rng)
    about = (f"Crowd body {bid} (M3-CRE-659, ADR 0152): a{'n' if band[0] in 'ae' else ''} {band} {sex} "
             f"({plan['build']} build) of {plan['community']}'s look, in the `{plan['kit']}` kit with `{plan['hair']}` "
             f"hair. Generated by assets_src/crowd/gen_crowd.py from ranges.json (seed {plan['seed']}); do not edit by "
             f"hand. A new person, not a Haluna villager's face (M3-CHR-100). Keys starting with '_' are read by the "
             f"villager_* modules, not by bb_params.")
    out: dict = {"_about": about, "name": bid}
    out.update(sliders)
    out["skin_hex"] = skin_hex
    out.update(face)
    out["_skin"] = skin
    out["_hair"] = hair
    out["_eyes"] = {"iris": pal.mix(iris_a, iris_b, float(rng.uniform(0.0, 1.0)))}
    out["_costume"] = cos
    out["_tints"] = tints
    out["_build"] = {"shapes": [], "host_snaps": True, "garment_fit": True}
    out["_persona"] = persona
    return out, hair_mix


def all_bodies(ranges: dict, roster: dict, pal: Palette) -> dict[str, tuple[dict, list]]:
    haluna = haluna_faces()
    scale = face_scale(ranges)
    taken: dict[str, list] = {}
    out = {}
    for bid, plan in roster["bodies"].items():
        band = plan["age_band"]
        face = pick_face(ranges, bid, plan, taken.setdefault(band, []), haluna, scale)
        taken[band].append(face)
        out[bid] = body_params(ranges, pal, bid, plan, face)
    return out


# ---------------------------------------------------------------------------------------------
# people
# ---------------------------------------------------------------------------------------------
def feasible(ranges: dict, person: dict, bodies: dict, used_in_zone: set) -> list[str]:
    accepts = ranges["communities"][person["community"]]["accepts"]
    order_role = person["community"] == ORDER_COMMUNITY
    out = []
    for bid, b in bodies.items():
        if bid in used_in_zone or b["age_band"] != person["age_band"] or b["sex"] != person["sex"]:
            continue
        if (b["kit"] == ORDER_KIT) != order_role or b["community"] not in accepts:
            continue
        out.append(bid)
    return out


def assign(ranges: dict, roster: dict) -> dict[str, str]:
    """person id -> body. Zones with the most people go first; within a zone, the person with the fewest choices."""
    w = ranges["assign"]
    bodies = roster["bodies"]
    people = roster["people"]
    zones: dict[str, list[int]] = {}
    for i, p in enumerate(people):
        zones.setdefault(p["zone"], []).append(i)
    uses = {bid: 0 for bid in bodies}
    out: dict[str, str] = {}
    for zone in sorted(zones, key=lambda z: (-len(zones[z]), z)):
        used: set = set()
        left = list(zones[zone])
        while left:
            left.sort(key=lambda i: (len(feasible(ranges, people[i], bodies, used)), i))
            p = people[left.pop(0)]
            cands = feasible(ranges, p, bodies, used)
            if not cands:
                raise SystemExit(f"gen_crowd: no body for {p['id']} in {zone} (plan more bodies)")
            accepts = ranges["communities"][p["community"]]["accepts"]
            kits = ranges["roles"][p["role"]]["kits"]

            def score(bid: str) -> float:
                b = bodies[bid]
                s = w["build"] * (b["build"] == p["build"]) + w["home"] * (b["community"] == p["community"])
                s += w["accepted_rank"] * (len(accepts) - accepts.index(b["community"])) / len(accepts)
                s += w["kit"] * (b["kit"] in kits) - w["per_use"] * uses[bid]
                return s + (seed_of(p["id"], bid) % 1000) * 1e-6

            best = max(cands, key=score)
            out[p["id"]] = best
            used.add(best)
            uses[best] += 1
    return out


def cloth_sets(ranges: dict, person: dict) -> dict:
    role = ranges["roles"][person["role"]]
    comm = ranges["communities"][person["community"]]
    sets = dict(comm["cloth"])
    if person["role"] == "diver" and person["community"] in ranges["side_cloth"]:
        sets.update({k: v for k, v in ranges["side_cloth"][person["community"]].items() if not k.startswith("_")})
    sets.update(role.get("cloth", {}))
    return sets


def hair_tint(ranges: dict, pal: Palette, body: dict, rng: np.random.Generator) -> str:
    """The body's own hair mix moved along its segment by up to hair_shift: the scalp underpaint the skin maps baked
    stays under a near colour."""
    a, b, t = body["_hair_mix"]
    lo, hi = ranges["hair_shift"]
    d = float(rng.uniform(lo, hi)) * (1.0 if rng.random() < 0.5 else -1.0)
    return pal.mix(a, b, min(1.0, max(0.0, t + d)))


def person_tints(ranges: dict, pal: Palette, person: dict, body: dict, others: list[dict]) -> dict:
    sets = cloth_sets(ranges, person)
    need = float(ranges["assign"]["tint_min_distance"])
    best, best_d = None, -1.0
    for attempt in range(int(ranges["assign"]["tint_tries"])):
        rng = rng_for(person["id"], "tints", attempt)
        t = {s: draw_cloth(pal, sets, CLOTH_KEYS[s], rng, body["skin"], ranges["skin_clearance"], person["id"])
             for s in TINT_SLOTS}
        t["hair"] = hair_tint(ranges, pal, body, rng)
        d = min([tint_distance(t, o) for o in others], default=1e9)
        if d >= need:
            return t
        if d > best_d:
            best, best_d = t, d
    return best


def people(ranges: dict, roster: dict, pal: Palette, bodies: dict[str, dict]) -> list[dict]:
    """`bodies`: per body, its hair mix (`_hair_mix`) and skin (`skin`)."""
    assigned = assign(ranges, roster)
    worn: dict[str, list[dict]] = {}
    out = []
    for p in roster["people"]:
        q = dict(p)
        bid = assigned[p["id"]]
        q["island"] = ranges["communities"][p["community"]]["island"]
        q["body"] = bid
        q["tints"] = person_tints(ranges, pal, p, bodies[bid], worn.setdefault(bid, []))
        worn[bid].append(q["tints"])
        q["work"] = ranges["roles"][p["role"]]["work"]
        out.append({k: q[k] for k in PERSON_KEYS if k in q})
    return out


# ---------------------------------------------------------------------------------------------
def generate() -> tuple[dict[str, str], str]:
    ranges = load_json(RANGES)
    roster = load_json(ROSTER)
    pal = Palette()
    bodies = all_bodies(ranges, roster, pal)
    roster["people"] = people(ranges, roster, pal, {bid: {"_hair_mix": m, "skin": p["skin_hex"]}
                                                     for bid, (p, m) in bodies.items()})
    files = {}
    for bid, (params, _m) in bodies.items():
        # the work clips its wearers play (crowd_clips.py), so the build needs nothing outside assets_src
        params["_work"] = sorted({p["work"] for p in roster["people"] if p["body"] == bid and p["work"]})
        files[f"{bid}.json"] = dump(params)
    return files, dump(roster)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if a params file or crowd.json would change")
    args = ap.parse_args(argv)
    files, roster_text = generate()
    stale = []
    for name, text in files.items():
        path = PARAMS_DIR / name
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            stale.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
    extra = sorted(p.name for p in PARAMS_DIR.glob("*.json") if p.name not in files) if PARAMS_DIR.is_dir() else []
    stale += [f"{PARAMS_DIR.relative_to(ROOT)}/{n} (not planned)" for n in extra]
    if ROSTER.read_text(encoding="utf-8") != roster_text:
        stale.append(str(ROSTER.relative_to(ROOT)))
        if not args.check:
            ROSTER.write_text(roster_text, encoding="utf-8")
    if args.check:
        for s in stale:
            print(f"stale: {s}")
        return 1 if stale else 0
    print(f"gen_crowd: {len(files)} bodies, {len(json.loads(roster_text)['people'])} people "
          f"({len(stale)} file(s) written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
