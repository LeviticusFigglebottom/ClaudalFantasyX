"""Foot slip of a creature build's exported clips, measured in numpy (no Blender): the companion of clip_audit.gd for
iterating on a build. python3 tools/creatures/foot_slip.py <creature id> [leg-tip bone ...]

For each clip, the farthest any low vertex slides from where it planted while it stays within PLANT_M of its lowest
point (cm). Uses the build's own export_clips() (grounded and pinned), as the GLB will carry them.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
COMMON = ROOT / "assets_src" / "creatures" / "common"
FLOOR_M = 0.04
PLANT_M = 0.012
CONTACT_REST_M = 0.15


def load_build(cid: str):
    folder = ROOT / "assets_src" / "creatures" / cid
    sys.path[:0] = [str(COMMON), str(folder)]
    spec = importlib.util.spec_from_file_location(f"build_{cid}", folder / f"build_{cid}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def rig_and_mesh(mod):
    """The builds differ: build_mesh() may make the rig itself, or take build_rig()'s extra results after the rig."""
    if not inspect.signature(mod.build_mesh).parameters:
        return mod.build_mesh()
    made = mod.build_rig()
    rig, extra = (made[0], made[1:]) if isinstance(made, tuple) else (made, ())
    return rig, mod.build_mesh(rig, *extra)


def slips(cid: str) -> dict[str, float]:
    mod = load_build(cid)
    import grounding as gr  # noqa: PLC0415 (on the path load_build set)

    rig, mesh = rig_and_mesh(mod)
    clips = mod.export_clips(rig, mesh)
    poser = gr.Poser(rig, mesh)
    rest = poser.vertices(poser.matrices({}))
    mask = rest[:, 1] < CONTACT_REST_M
    out = {}
    for clip in clips:
        frames = np.array([poser.vertices(poser.matrices(gr.pose_at(clip, poser.names, t)), mask)
                           for t in gr.frame_times(clip)])
        low = frames[:, :, 1].min(axis=0)
        best = 0.0
        for v in np.flatnonzero(low < FLOOR_M):
            planted = frames[:, v, 1] <= low[v] + PLANT_M
            start = None
            for k in range(1, len(frames)):
                if planted[k] and planted[k - 1]:
                    if start is None:
                        start = frames[k - 1, v, [0, 2]]
                    best = max(best, float(np.linalg.norm(frames[k, v, [0, 2]] - start)))
                else:
                    start = None
        out[clip.name] = 100.0 * best
    return out


if __name__ == "__main__":
    for name, cm in slips(sys.argv[1]).items():
        print(f"{name:12} {cm:6.1f} cm")
