"""Act I's crowd bodies (M3-CRE-659, ADR 0152): the characters' villager pipeline at the crowd tier. Two steps:

    blender --background --factory-startup --python assets_src/crowd/build_crowd.py -- --body B --bake-dir DIR
    python3 assets_src/crowd/build_crowd.py --body B --bake-dir DIR       # maps, materials, actor, clips

Every module here is the characters track's (assets_src/characters/villagers/, pipeline.md section 15), imported
and pointed at the crowd folders from outside; none is edited (ADR 0152):

* mesh (Blender): build_villager.main with its PARAMS_DIR at assets_src/crowd/params. It writes LOD0 and LOD1;
  the crowd tier ships only LOD1, as assets/crowd/<body>/<body>.glb (LOD0 goes to the bake dir and is dropped).
  The params' `_build.shapes` is empty: LOD1 carries no blendshapes, so none are built.
* maps: villager_textures.skin with its PARAMS_DIR, OUT_ROOT and map sizes moved (head 512 albedo and normal,
  256 ORM and skin mask; body 256). The cloth is the villagers' shared atlas, not rebuilt.
* materials: write_materials.tables for the body, its texture paths re-rooted (the skin maps under
  assets/crowd/<body>/textures, Asha's generic atlases and the villagers' cloth atlas where they are), written for
  the material slots the LOD1 GLB has; plus `<body>_actor.tscn` (the GLB turned to face -Z, as the villagers').
* clips (M3-CRE-662): not per body. The crowd bodies share one skeleton (the villager rig, the same bone names), so
  each age group shares one AnimationLibrary, `assets/crowd/clips/crowd_<library>_clips.tres` (ranges.json
  `clip_libraries`: adult, elder, child, child_small). The library's reference body builds it, in its own job, from
  its freshly built GLB: villager_clips.build with its PARAMS_DIR, GLB path and persona moved (the group's mean
  `_persona`), the members' work clips (`_work`) added through its EXTRA_CLIPS hook with crowd_clips.pose_at. Its
  tracks are rooted at ARMATURE, not at the reference's own armature node, and it records the reference's hips rest
  height (`metadata/hips_rest_y`): the crowd import (game/world/npc/crowd_clip_library.gd) names every body's
  armature ARMATURE and scales each body's hips track to its own height (Skeleton3D.motion_scale).

Deterministic (the villager jobs' snaps are on in every crowd params file: `_build.host_snaps`).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VILLAGERS = ROOT / "assets_src" / "characters" / "villagers"
PARAMS_DIR = HERE / "params"
OUT_ROOT = ROOT / "assets" / "crowd"
HEAD_SIZE = (512, 256)  # albedo and normal, ORM and skin mask (the villagers' 1024 / 512)
BODY_SIZE = (256, 256)  # the villagers' 512
RES = "res://assets"
LOD0_DIR = "lod0"
RANGES = HERE / "ranges.json"
LIB_DIR = OUT_ROOT / "clips"
ARMATURE = "crowd_skeleton"  # every crowd body's armature node after import (game/data/import/crowd.json)
HIPS_META = "hips_rest_y"
PERSONA_DIGITS = {"sway": 2, "lean": 2, "arms_down": 1}
ACTOR = """[gd_scene load_steps=2 format=3]

[ext_resource type="PackedScene" path="res://assets/crowd/{body}/{body}.glb" id="glb"]

[node name="{Name}" type="Node3D"]

[node name="Model" parent="." instance=ExtResource("glb")]
transform = Transform3D(-1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0)
"""
# material slots never in a crowd GLB's LOD1 (asha's LOD1_DROP_MATS and the excluded eye pieces), and the dialogue
# variant (no talking close-ups at the crowd tier)
UNUSED = {"skin_head_dialogue"}


def log(msg: str) -> None:
    print(f"[crowd] {msg}", flush=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="build_crowd.py")
    ap.add_argument("--body", required=True)
    ap.add_argument("--bake-dir", required=True)
    ap.add_argument("--report")
    return ap.parse_args(argv)


def glb_path(body: str) -> Path:
    return OUT_ROOT / body / f"{body}.glb"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------------------------
# mesh (Blender)
# ---------------------------------------------------------------------------------------------
def build_mesh(args: argparse.Namespace) -> int:
    sys.path.insert(0, str(VILLAGERS))
    import build_villager as bv

    bv.PARAMS_DIR = PARAMS_DIR
    bake = Path(args.bake_dir).resolve()
    lod0 = bake / LOD0_DIR / f"{args.body}.glb"
    lod0.parent.mkdir(parents=True, exist_ok=True)
    argv = ["build_villager.py", "--", "--npc", args.body, "--out", str(lod0), "--bake-dir", str(bake)]
    if args.report:
        argv += ["--report", args.report]
    saved = sys.argv
    sys.argv = argv
    try:
        rc = bv.main()
    finally:
        sys.argv = saved
    if rc:
        return rc
    out = glb_path(args.body)
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(lod0.with_name(f"{args.body}_lod1.glb")), out)
    log(f"{args.body}: shipped LOD1 as {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.2f} MB)")
    return 0


# ---------------------------------------------------------------------------------------------
# maps, materials, actor, clips (python3)
# ---------------------------------------------------------------------------------------------
def build_maps(body: str, bake: Path) -> None:
    sys.path.insert(0, str(VILLAGERS))
    import villager_textures as vt

    vt.PARAMS_DIR = PARAMS_DIR
    vt.OUT_ROOT = OUT_ROOT
    vt.HEAD_SIZE = HEAD_SIZE
    vt.BODY_SIZE = BODY_SIZE
    vt.skin(body, bake)


def glb_materials(path: Path) -> set[str]:
    data = path.read_bytes()
    n = struct.unpack_from("<I", data, 12)[0]
    js = json.loads(data[20:20 + n])
    return {m["name"] for m in js.get("materials", [])}


def retarget(fname: str, body: str) -> str:
    """A villager material's texture path (relative to res://assets/characters) for the crowd layout."""
    own = f"villagers/{body}/textures/"
    if fname.startswith(own):
        return f"crowd/{body}/textures/" + fname[len(own):]
    return "characters/" + fname


def build_materials(body: str) -> list[str]:
    wmv = load_module("villager_write_materials", VILLAGERS / "write_materials.py")
    wmv.PARAMS_DIR = PARAMS_DIR
    extra = json.loads((PARAMS_DIR / f"{body}.json").read_text(encoding="utf-8"))
    out = OUT_ROOT / body / "materials"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    wmv.wm.OUT = out
    wmv.wm.TEX = RES
    shader, standard, std_tex = wmv.tables(body, extra)
    slots = glb_materials(glb_path(body))
    written = []
    for name, (sh, prio, params, textures) in shader.items():
        if name in UNUSED or name not in slots:
            continue
        wmv.wm.write_shader_material(name, sh, prio, params, {k: retarget(v, body) for k, v in textures.items()})
        written.append(name)
    for name, mat in standard.items():
        if name in slots:
            wmv.wm.write_standard_material(name, mat, {k: retarget(v, body) for k, v in std_tex.get(name, {}).items()})
            written.append(name)
    missing = sorted(slots - set(written))
    if missing:
        raise SystemExit(f"build_crowd: {body}.glb slots without a material: {missing}")
    actor = OUT_ROOT / body / f"{body}_actor.tscn"
    actor.write_text(ACTOR.format(body=body, Name="".join(w.capitalize() for w in body.split("_"))), encoding="utf-8")
    return sorted(written)


def libraries() -> dict[str, dict]:
    """ranges.json `clip_libraries`: library -> {"ref": body, "bodies": [body, ...]}."""
    data = json.loads(RANGES.read_text(encoding="utf-8"))["clip_libraries"]
    return {k: v for k, v in data.items() if not k.startswith("_")}


def library_path(lib: str) -> Path:
    return LIB_DIR / f"crowd_{lib}_clips.tres"


def group_persona(params: list[dict]) -> dict:
    """The library's persona: its members' `_persona` averaged (sway, lean, arms_down)."""
    return {k: round(sum(float(p["_persona"][k]) for p in params) / len(params), d) for k, d in PERSONA_DIGITS.items()}


def library_spec(lib: str) -> tuple[str, dict, list[str]]:
    """(reference body, persona, work clips) of a library: the work clips any member's wearers play, in
    crowd_clips order."""
    sys.path.insert(0, str(HERE))
    import crowd_clips as cc

    spec = libraries()[lib]
    params = [json.loads((PARAMS_DIR / f"{b}.json").read_text(encoding="utf-8")) for b in spec["bodies"]]
    want = {c for p in params for c in p.get("_work", []) if c}
    unknown = sorted(want - set(cc.CLIPS))
    if unknown:
        raise SystemExit(f"build_crowd: library {lib} names unknown work clips {unknown}")
    return spec["ref"], group_persona(params), [c for c in cc.CLIPS if c in want]


def build_library(lib: str) -> str:
    """The library's AnimationLibrary text: villager_clips.build on the reference body's skeleton with the group's
    persona and work clips, its tracks rooted at ARMATURE, plus the reference's hips rest height."""
    sys.path.insert(0, str(VILLAGERS))
    sys.path.insert(0, str(HERE))
    import crowd_clips as cc
    import villager_clips as vc

    ref, pers, work = library_spec(lib)
    vc.PARAMS_DIR = PARAMS_DIR
    vc.glb_path = glb_path
    vc.EXTRA_CLIPS[ref] = work
    vc.EXTRA_LENGTHS.update(cc.LENGTHS)
    vc.EXTRA_LOOPS.update(cc.CLIPS)
    villager_pose, villager_persona = vc.pose_at, vc.persona

    def pose_at(clip: str, t: float, length: float, sk, p: dict) -> dict:
        if clip in cc.POSES:
            return cc.pose_at(clip, t, length, sk, p)
        return villager_pose(clip, t, length, sk, p)

    vc.pose_at = pose_at
    vc.persona = lambda _npc: {**vc.DEFAULT_PERSONA, **pers, "staff": False}
    try:
        text = vc.build(ref)
    finally:
        vc.pose_at, vc.persona = villager_pose, villager_persona
    sk = vc.hc.Skeleton(glb_path(ref))
    text = text.replace(f'NodePath("{sk.root_name}/', f'NodePath("{ARMATURE}/')
    return text + f"metadata/{HIPS_META} = {vc.hc.fmt(float(sk.rest_t[vc.hc.HIPS][1]))}\n"


def build_clips(body: str) -> list[str]:
    """The libraries `body` is the reference of (each written to assets/crowd/clips/)."""
    out = []
    for lib, spec in libraries().items():
        if spec["ref"] != body:
            continue
        text = build_library(lib)
        p = library_path(lib)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        log(f"{body}: library {lib} for {len(spec['bodies'])} bodies ({len(text) / 1e6:.2f} MB)")
        out.append(lib)
    return out


def finish(args: argparse.Namespace) -> int:
    bake = Path(args.bake_dir).resolve()
    build_maps(args.body, bake)
    mats = build_materials(args.body)
    log(f"{args.body}: {len(mats)} materials and the actor scene")
    stale = OUT_ROOT / args.body / "anim"  # M3-CRE-659's per-body clips, now shared (build_clips)
    if stale.exists():
        shutil.rmtree(stale)
    build_clips(args.body)
    return 0


def main() -> int:
    if importlib.util.find_spec("bpy") is not None:  # under Blender: the mesh step
        return build_mesh(parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []))
    return finish(parse_args(sys.argv[1:]))


if __name__ == "__main__":
    sys.exit(main())
