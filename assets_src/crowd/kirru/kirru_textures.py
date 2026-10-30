"""A Kirru crowd body's textures, materials and actor scene (after build_kirru.py, on its bake dir):

    python3 assets_src/crowd/kirru/kirru_textures.py --body kirru_man --bake-dir DIR

Pell's own texture and material writers (assets_src/characters/pell/pell_textures.py, write_materials.py) run on the
body's merged params (kirru_params) into the bake dir; the maps are then scaled by kirru_bodies.json `texture_scale`
(crowd bodies are seen at a distance) and written as assets/crowd/<id>/textures/<id>_*.png, the materials as
assets/crowd/<id>/materials/*.tres pointing at them, and the actor scene <id>_actor.tscn the villager crowd's way (the
model turned to face +z, as assets/crowd/*/<body>_actor.tscn). Deterministic: fixed resampling, no PNG metadata.
"""
from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PELL = ROOT / "assets_src" / "characters" / "pell"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PELL))

import kirru_params  # noqa: E402

PELL_TEX = "res://assets/characters/pell/textures/pell_"
ACTOR = """[gd_scene load_steps=2 format=3]

[ext_resource type="PackedScene" path="res://assets/crowd/{id}/{id}.glb" id="glb"]

[node name="{node}" type="Node3D"]

[node name="Model" parent="." instance=ExtResource("glb")]
transform = Transform3D(-1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0)
"""


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--body", required=True)
    ap.add_argument("--bake-dir", required=True)
    args = ap.parse_args()
    body, bake = args.body, Path(args.bake_dir)
    params = kirru_params.write_params(body, bake)
    out = kirru_params.asset_dir(body)
    scale = float(kirru_params.bodies()["texture_scale"])

    pt = _module("pell_textures", PELL / "pell_textures.py")
    pt.OUT = out / "_raw"  # inside the repo (the atlas writer prints repo-relative paths); removed below
    pt.PARAMS = params
    for name, value in kirru_params.texture_overrides(body).items():
        setattr(pt, name, value)
    pt.OUT.mkdir(parents=True, exist_ok=True)
    argv = sys.argv
    sys.argv = [argv[0], "--bake-dir", str(bake)]
    try:
        rc = pt.main()
    finally:
        sys.argv = argv
    if rc:
        return rc
    tex = out / "textures"
    tex.mkdir(parents=True, exist_ok=True)
    for src in sorted(pt.OUT.glob("pell_*.png")):
        im = Image.open(src)
        im.load()
        size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
        small = im.resize(size, Image.Resampling.LANCZOS) if size != im.size else im
        small = Image.fromarray(np.asarray(small))  # drop any source metadata
        small.save(tex / f"{body}_{src.name[len('pell_'):]}", optimize=False)
    shutil.rmtree(pt.OUT)

    wm = _module("pell_write_materials", PELL / "write_materials.py")
    wm.OUT = out / "materials"
    wm.PARAMS = params
    rc = wm.main()
    if rc:
        return rc
    for tres in sorted(wm.OUT.glob("*.tres")):
        text = tres.read_text(encoding="utf-8")
        tres.write_text(text.replace(PELL_TEX, f"res://assets/crowd/{body}/textures/{body}_"), encoding="utf-8")
    node = "".join(w.capitalize() for w in body.split("_"))
    (out / f"{body}_actor.tscn").write_text(ACTOR.format(id=body, node=node), encoding="utf-8")
    print(f"[kirru] {body}: textures x{scale}, materials and actor in {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
