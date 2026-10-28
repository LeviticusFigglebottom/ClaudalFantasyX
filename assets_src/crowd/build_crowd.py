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
* clips: villager_clips.build with its PARAMS_DIR and GLB path moved, and the body's work clips (`_work` in its
  params, from the roster) added through its EXTRA_CLIPS hook with crowd_clips.pose_at: idle, talk, walk + work.

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


def build_clips(body: str) -> int:
    sys.path.insert(0, str(VILLAGERS))
    sys.path.insert(0, str(HERE))
    import crowd_clips as cc
    import villager_clips as vc

    extra = json.loads((PARAMS_DIR / f"{body}.json").read_text(encoding="utf-8"))
    work = [c for c in extra.get("_work", []) if c]
    unknown = sorted(set(work) - set(cc.CLIPS))
    if unknown:
        raise SystemExit(f"build_crowd: {body} names unknown work clips {unknown}")
    vc.PARAMS_DIR = PARAMS_DIR
    vc.glb_path = glb_path
    vc.EXTRA_CLIPS[body] = work
    vc.EXTRA_LENGTHS.update(cc.LENGTHS)
    vc.EXTRA_LOOPS.update(cc.CLIPS)
    villager_pose = vc.pose_at

    def pose_at(clip: str, t: float, length: float, sk, pers: dict) -> dict:
        if clip in cc.POSES:
            return cc.pose_at(clip, t, length, sk, pers)
        return villager_pose(clip, t, length, sk, pers)

    vc.pose_at = pose_at
    try:
        text = vc.build(body)
    finally:
        vc.pose_at = villager_pose
    p = OUT_ROOT / body / "anim" / f"{body}_clips.tres"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    log(f"{body}: {len(vc.clips_for(body))} clips ({len(text) / 1e6:.2f} MB)")
    return len(vc.clips_for(body))


def finish(args: argparse.Namespace) -> int:
    bake = Path(args.bake_dir).resolve()
    build_maps(args.body, bake)
    mats = build_materials(args.body)
    log(f"{args.body}: {len(mats)} materials and the actor scene")
    build_clips(args.body)
    return 0


def main() -> int:
    if importlib.util.find_spec("bpy") is not None:  # under Blender: the mesh step
        return build_mesh(parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []))
    return finish(parse_args(sys.argv[1:]))


if __name__ == "__main__":
    sys.exit(main())
