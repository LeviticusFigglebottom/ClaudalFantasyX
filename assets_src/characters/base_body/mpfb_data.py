"""Readers for the vendored MPFB2 / MakeHuman CC0 data (M1-CHR-03, ADR 0021). Pure Python + numpy.

This is our own code: it parses the plain-text data formats and does not import, copy or
translate anything from MPFB2's GPL program code. The data lives in
`assets_src/third_party/mpfb2/data/` and is reproduced by `tools/fetch_mpfb2.py` from a pinned
commit. Formats read here:

* **Wavefront OBJ** (`3dobjs/base.obj`, the "hm08" base mesh): `v`, `vt`, `g`, `f v/vt` lines.
  Units are decimetres, Y up, the figure faces +Z, +X is the figure's left.
* **Target** (`*.target.gz`): gzip text, one `index dx dy dz` line per moved vertex (same units
  and axes). Lines starting with `#` are comments.
* **Weights** (`rigs/rigify/weights.human_toes.json.gz`): `{"weights": {group: [[vertex, w], ...]}}`.
* **UV-layer face sets** (`uv_layers/*.json.gz`): `{face index: {loop: [u, v]}}`; only the keys
  (which faces form the lips, the face mask, the scalp) are used.

Everything is converted on load to the repo's Blender frame (bb_params): metres, Z up, the
character faces -Y, +X is the character's LEFT. (x, y, z)_mh -> (x, -z, y) * 0.1.
"""
from __future__ import annotations

import gzip
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "assets_src" / "third_party" / "mpfb2" / "data"
UNIT_M = 0.1  # MakeHuman units are decimetres
N_BODY = 13380  # vertices 0..13379 are the skin ("body" group); helpers and joint cubes follow


def to_repo(P: np.ndarray) -> np.ndarray:
    """MakeHuman frame (Y up, faces +Z) -> repo frame (Z up, faces -Y), metres."""
    P = np.asarray(P, dtype=np.float64)
    return np.stack([P[..., 0], -P[..., 2], P[..., 1]], axis=-1) * UNIT_M


@dataclass
class DonorMesh:
    V: np.ndarray  # (n, 3) all vertices, repo frame
    VT: np.ndarray  # (m, 2) texture coordinates
    faces: dict = field(default_factory=dict)  # group -> list of (vertex ids, uv ids)

    def body(self) -> tuple[np.ndarray, np.ndarray]:
        """The skin: quads (k, 4) of vertex ids and (k, 4) of uv ids."""
        F = np.array([f for f, _t in self.faces["body"]], dtype=np.int64)
        T = np.array([t for _f, t in self.faces["body"]], dtype=np.int64)
        return F, T

    def group_vertices(self, group: str) -> np.ndarray:
        return np.unique(np.concatenate([np.array(f) for f, _t in self.faces[group]]))

    def joint(self, name: str) -> np.ndarray:
        """Centre of a `joint-*` cube (MakeHuman's joint markers), repo frame."""
        return self.V[self.group_vertices(f"joint-{name}")].mean(axis=0)


def load_obj(path: Path | None = None) -> DonorMesh:
    path = path or DATA / "3dobjs" / "base.obj"
    V: list[list[float]] = []
    VT: list[list[float]] = []
    faces: dict[str, list] = {}
    group = "default"
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("v "):
                V.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("vt "):
                VT.append([float(x) for x in line.split()[1:3]])
            elif line.startswith("g "):
                group = line.split()[1]
            elif line.startswith("f "):
                vi, ti = [], []
                for tok in line.split()[1:]:
                    parts = tok.split("/")
                    vi.append(int(parts[0]) - 1)
                    ti.append(int(parts[1]) - 1 if len(parts) > 1 and parts[1] else -1)
                faces.setdefault(group, []).append((vi, ti))
    return DonorMesh(to_repo(np.array(V)), np.array(VT), faces)


def load_target(rel: str, n: int = N_BODY) -> np.ndarray:
    """A target as a dense (n, 3) delta in the repo frame (vertices >= n are dropped)."""
    D = np.zeros((n, 3))
    with gzip.open(DATA / "targets" / rel, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            a = line.split()
            i = int(a[0])
            if i < n:
                D[i] = [float(a[1]), float(a[2]), float(a[3])]
    return to_repo(D)


def load_weights(rel: str = "rigs/rigify/weights.human_toes.json.gz", n: int = N_BODY) -> dict[str, np.ndarray]:
    """{group: dense (n,) weights}. Groups include MakeHuman's non-bone masks (mhmask-*)."""
    with gzip.open(DATA / rel, "rt", encoding="utf-8") as fh:
        js = json.load(fh)
    out: dict[str, np.ndarray] = {}
    for name in sorted(js["weights"]):
        w = np.zeros(n)
        for vi, wt in js["weights"][name]:
            if vi < n:
                w[int(vi)] = float(wt)
        out[name] = w
    return out


def load_face_set(name: str) -> np.ndarray:
    """Face indices (into the body quads) of a uv-layer face set, e.g. 'lips_solid'."""
    with gzip.open(DATA / "uv_layers" / f"{name}.json.gz", "rt", encoding="utf-8") as fh:
        js = json.load(fh)
    return np.array(sorted(int(k) for k in js), dtype=np.int64)
