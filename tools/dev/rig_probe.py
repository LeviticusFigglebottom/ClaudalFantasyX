#!/usr/bin/env python3
"""Headless rig probe for the heroes (M1-CHR-14): skin the committed GLBs in numpy and measure what breaks.

    python3 tools/dev/rig_probe.py --hero asha --report            # per-check, per-pose table
    python3 tools/dev/rig_probe.py --hero rhen --report --json out.json
    python3 tools/dev/rig_probe.py --hero asha --report --every 1  # every clip frame (slow)

No Blender, no Godot: numpy only. The probe reads `assets/characters/<hero>/<hero>.glb` (every skinned mesh's
POSITION, NORMAL, JOINTS_0 and WEIGHTS_0, the skin's joints and inverseBindMatrices, and the node hierarchy with its
rest TRS), and computes linear-blend-skinned vertex positions for a pose, exactly as Godot's Skeleton3D does:

    v' = sum_i w_i * (G_joint_i * IBM_i) * v,   G = the joint's global transform with its posed local rotation

Poses come from `assets_src/characters/asha/hero_clips.py` (the same functions that write the AnimationLibrary the
game plays, so a pose here is a frame of the shipped clip): the rest pose, every N-th key of every clip of the hero,
and the stage's world-axis test poses (`asha_extreme_pose.tscn`, composed like `AshaStage._apply_world_pose`, then
the helper bones posed as `HeroHelperBones.drive` does, M1-CHR-15). Bones the clips do not key (fingers, eyes, props,
sash tails) stay at their rest local transform and inherit; the helper bones (skirt panels, shoulder correctives) are
keyed by every clip.

Three checks (thresholds in `tools/dev/rig_checks.json`, per-hero overrides under "heroes"):

* **braid**: each woven strand of the braid (a big connected piece of the braid mesh) has a root ring, its open end
  nearer the scalp at rest. The ring must touch the scalp (the hair cap and the head skin) in every pose -- `gap` is
  the ring's closest signed distance to that surface, inside counting as 0 -- and must ride with the head: `drift` is
  how far a ring vertex moves in the head bone's frame from rest (0 when it is skinned to the head).
* **penetration**: (a) garment and prop vertices inside the body skin: signed distance to the skinned body surface
  (negative = inside, along the interpolated skin normal), the deepest candidates confirmed by the skin's winding
  number so a point beside a limb or over a hidden-face hole is not counted; props (staff, spear, shield) may touch
  the hand that holds them; (b) body vertices covered by clothing at rest that end up outside it (skin poking
  through: the closest garment point lies behind the skin).
* **seams**: (a) positions that coincide at rest across meshes and primitives (the neck seam between Head and Body,
  UV-seam duplicates) must stay coincident; (b) the Body's open boundary (the holes where hidden faces were deleted)
  must stay under a garment; (c) every vertex's skin weights sum to 1 and name real joints.
* **prop grip** (M2-CHR-515, from M1-QA-09: the staff and spear floated upright beside open hands): for a hero whose
  hand never lets go of its prop (`game/data/characters/grips.json`), in every pose (a) the prop keeps its rest turn
  in the hand's frame (`turn`, degrees) and its shaft's axis passes through the fist's grip point (`offset`; the
  shaft may slide through the fist, so only the distance across the axis counts), and (b) the shaft does not pass
  through a garment (`through_garment`: rays along the shaft's centre line and four lines on its surface, outside
  `grip_clear_mm` of the fist, against every garment; the staff through the skirt in a kneel). A pose with the prop
  set down (M2-CHR-520, hero_clips.prop_down) skips (a); (b) still holds for the laid prop.

`tools/tests/test_rig_integrity.py` runs all three for every hero; docs/kb/art/characters/pipeline.md ("Rig
integrity guards") explains how to read the numbers.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):  # a shared machine: one core
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CLIPS_DIR = ROOT / "assets_src" / "characters" / "asha"
if str(CLIPS_DIR) not in sys.path:
    sys.path.insert(0, str(CLIPS_DIR))

import asha_glb  # noqa: E402
import hero_clips  # noqa: E402

CONFIG = Path(__file__).resolve().with_name("rig_checks.json")
GRIPS = ROOT / "game" / "data" / "characters" / "grips.json"  # M2-CHR-515: written by hero_clips.write_grip_data
VILLAGERS_DIR = ROOT / "assets_src" / "characters" / "villagers"
# HYMN_RIG_ROOT=<checkout>: read the hero GLBs from another checkout's assets/characters (e.g. a GLB being rebuilt in
# the main checkout while this code runs from a worktree). Everything else comes from this checkout.
ROOT_ENV = "HYMN_RIG_ROOT"
GRID_CELLS = (0.012, 0.025)  # nearest-vertex grids (m), finer first: most queries resolve in the first
BATTLE_LIB_PREFIX = "battle:"  # pose labels sampled from a hero's battle library (hero_clips.BATTLE_STANCE)
CONFIRM_BATCH = 6  # penetration candidates confirmed by winding number per batch, deepest first


# ---------------------------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------------------------
def _merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_config(hero: str, path: Path = CONFIG) -> dict:
    """The defaults with the hero's overrides merged in (dicts merge key by key; anything else replaces)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return _merge(data["defaults"], data.get("heroes", {}).get(hero, {}))


# ---------------------------------------------------------------------------------------------
# math
# ---------------------------------------------------------------------------------------------
def quat_matrix(q) -> np.ndarray:
    x, y, z, w = (float(c) for c in q)
    n = math.sqrt(x * x + y * y + z * z + w * w) or 1.0
    x, y, z, w = x / n, y / n, z / n, w / n
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def trs(t, q, s) -> np.ndarray:
    m = np.eye(4)
    m[:3, :3] = quat_matrix(q) * np.asarray(s, dtype=float)[None, :]
    m[:3, 3] = t
    return m


def closest_on_triangles(p: np.ndarray, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Closest point on each triangle (a, b, c rows) to each point p (rows), with barycentric weights (Ericson 5.1.5).
    All inputs (n, 3); returns (closest (n, 3), bary (n, 3))."""
    ab, ac, ap = b - a, c - a, p - a
    d1, d2 = np.einsum("ij,ij->i", ab, ap), np.einsum("ij,ij->i", ac, ap)
    bp = p - b
    d3, d4 = np.einsum("ij,ij->i", ab, bp), np.einsum("ij,ij->i", ac, bp)
    cp = p - c
    d5, d6 = np.einsum("ij,ij->i", ab, cp), np.einsum("ij,ij->i", ac, cp)
    va = d3 * d6 - d5 * d4
    vb = d5 * d2 - d1 * d6
    vc = d1 * d4 - d3 * d2
    n = len(p)
    bary = np.zeros((n, 3))
    done = np.zeros(n, dtype=bool)

    def put(mask, u, v, w):  # the first region test a point passes decides it
        m = mask & ~done
        bary[m, 0], bary[m, 1], bary[m, 2] = u[m], v[m], w[m]
        done[m] = True

    one, zero = np.ones(n), np.zeros(n)
    put((d1 <= 0) & (d2 <= 0), one, zero, zero)
    put((d3 >= 0) & (d4 <= d3), zero, one, zero)
    with np.errstate(divide="ignore", invalid="ignore"):
        v_ab = np.where(d1 - d3 != 0, d1 / (d1 - d3), 0.0)
        put((vc <= 0) & (d1 >= 0) & (d3 <= 0), 1 - v_ab, v_ab, zero)
        put((d6 >= 0) & (d5 <= d6), zero, zero, one)
        w_ac = np.where(d2 - d6 != 0, d2 / (d2 - d6), 0.0)
        put((vb <= 0) & (d2 >= 0) & (d6 <= 0), 1 - w_ac, zero, w_ac)
        den = (d4 - d3) + (d5 - d6)
        w_bc = np.where(den != 0, (d4 - d3) / den, 0.0)
        put((va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0), zero, 1 - w_bc, w_bc)
        s = va + vb + vc
        s = np.where(s != 0, s, 1.0)
        v_in, w_in = vb / s, vc / s
    put(np.ones(n, dtype=bool), 1 - v_in - w_in, v_in, w_in)
    q = a * bary[:, :1] + b * bary[:, 1:2] + c * bary[:, 2:3]
    return q, bary


def _nearest_brute(p: np.ndarray, q: np.ndarray, k: int, chunk: int = 512) -> np.ndarray:
    centre = q.mean(axis=0)
    qq = (q - centre).astype(np.float32)
    qn = np.einsum("ij,ij->i", qq, qq)
    k = min(k, len(q))
    out = np.empty((len(p), k), dtype=np.int64)
    for s in range(0, len(p), chunk):
        pp = (p[s:s + chunk] - centre).astype(np.float32)
        d = qn[None, :] - 2.0 * (pp @ qq.T)
        if k == 1:
            out[s:s + chunk, 0] = np.argmin(d, axis=1)
        else:
            part = np.argpartition(d, k - 1, axis=1)[:, :k]
            order = np.argsort(np.take_along_axis(d, part, axis=1), axis=1)
            out[s:s + chunk] = np.take_along_axis(part, order, axis=1)
    return out


def nearest_index(p: np.ndarray, q: np.ndarray, k: int = 1, cell: float = 0.03, far_ok: bool = False) -> np.ndarray:
    """Indices (n, k) of the k nearest rows of q to each row of p. Uniform grids (GRID_CELLS, then `cell` metres)
    answer the points whose k-th nearest row lies within the cell size (exactly); the rest fall back to brute force,
    or get -1 with `far_ok`."""
    k = min(k, len(q))
    out = np.full((len(p), k), -1, dtype=np.int64)
    todo = np.arange(len(p))
    for c in sorted({min(x, cell) for x in GRID_CELLS} | {cell}):
        if not len(todo):
            break
        res = _nearest_grid(p[todo], q, k, c)
        done = res[:, 0] >= 0
        out[todo[done]] = res[done]
        todo = todo[~done]
    if len(todo) and not far_ok:
        out[todo] = _nearest_brute(p[todo], q, k)
    return out


def _nearest_grid(p: np.ndarray, q: np.ndarray, k: int, cell: float) -> np.ndarray:
    """k nearest rows of q within one grid cell's distance (else -1), from each point's 3x3x3 block of cells."""
    lo = np.minimum(p.min(axis=0), q.min(axis=0)) - 2 * cell
    cq = np.floor((q - lo) / cell).astype(np.int64)
    cp = np.floor((p - lo) / cell).astype(np.int64)
    dims = np.maximum(cq.max(axis=0), cp.max(axis=0)) + 3
    key_q = (cq[:, 0] * dims[1] + cq[:, 1]) * dims[2] + cq[:, 2]
    order = np.argsort(key_q, kind="stable")
    sk = key_q[order]
    uk, start = np.unique(sk, return_index=True)
    end = np.append(start[1:], len(sk))
    off = np.array([(i, j, m) for i in (-1, 0, 1) for j in (-1, 0, 1) for m in (-1, 0, 1)])
    nb = cp[:, None, :] + off[None]  # (n, 27, 3)
    key = ((nb[..., 0] * dims[1] + nb[..., 1]) * dims[2] + nb[..., 2]).reshape(-1)
    pos = np.searchsorted(uk, key)
    pos = np.minimum(pos, len(uk) - 1)
    hit = uk[pos] == key
    st = np.where(hit, start[pos], 0)
    cnt = np.where(hit, end[pos] - start[pos], 0)
    per_q = cnt.reshape(len(p), 27).sum(axis=1)
    out = np.empty((len(p), k), dtype=np.int64)
    ok = per_q >= k
    if ok.any():
        cnt2 = cnt.reshape(len(p), 27)[ok].reshape(-1)
        st2 = st.reshape(len(p), 27)[ok].reshape(-1)
        qid_ok = np.nonzero(ok)[0]
        seg_q = np.repeat(np.arange(len(qid_ok)), 27)
        total = int(cnt2.sum())
        seg_start = np.cumsum(cnt2) - cnt2
        rep = np.repeat(np.arange(len(cnt2)), cnt2)
        idx = order[st2[rep] + (np.arange(total) - seg_start[rep])]
        owner = seg_q[rep]
        diff = q[idx] - p[qid_ok[owner]]
        d2 = np.einsum("ij,ij->i", diff, diff)
        # owner is non-decreasing: per-point minima by reduceat, k times, masking each pick
        seg = np.searchsorted(owner, np.arange(len(qid_ok)))
        kth = np.zeros(len(qid_ok))
        for c in range(k):
            mn = np.minimum.reduceat(d2, seg)
            pos = np.flatnonzero(d2 == mn[owner])
            _, first = np.unique(owner[pos], return_index=True)
            pick = pos[first]
            out[qid_ok, c] = idx[pick]
            kth = mn
            d2[pick] = np.inf
        # exact only when the k-th nearest lies within one cell
        ok[qid_ok[np.sqrt(kth) > cell]] = False
    out[~ok] = -1
    return out


def weld(p: np.ndarray, tol: float = 1e-5) -> np.ndarray:
    """Weld id per row: rows whose positions round to the same point of a `tol` grid share an id (bit-identical
    duplicates always do; near-misses that straddle a rounding boundary do not)."""
    key = np.round(p / tol).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    return inv.reshape(-1)


# ---------------------------------------------------------------------------------------------
# the rig
# ---------------------------------------------------------------------------------------------
@dataclass
class Prim:
    mesh: str
    material: str
    P: np.ndarray  # (n, 3) bind positions
    N: np.ndarray  # (n, 3) bind normals
    J: np.ndarray  # (n, 4) skin joint indices
    W: np.ndarray  # (n, 4) weights
    F: np.ndarray  # (m, 3) triangles


@dataclass
class Part:
    """Several primitives treated as one surface (indices into the concatenation)."""
    name: str
    prims: list
    P: np.ndarray = field(default=None)
    N: np.ndarray = field(default=None)
    J: np.ndarray = field(default=None)
    W: np.ndarray = field(default=None)
    F: np.ndarray = field(default=None)
    src: np.ndarray = field(default=None)  # (n,) index of the primitive each vertex came from

    def __post_init__(self) -> None:
        off = 0
        P, N, J, W, F, src = [], [], [], [], [], []
        for i, pr in enumerate(self.prims):
            P.append(pr.P)
            N.append(pr.N)
            J.append(pr.J)
            W.append(pr.W)
            F.append(pr.F + off)
            src.append(np.full(len(pr.P), i))
            off += len(pr.P)
        self.P, self.N = np.concatenate(P), np.concatenate(N)
        self.J, self.W = np.concatenate(J), np.concatenate(W)
        self.F, self.src = np.concatenate(F), np.concatenate(src)


def villagers() -> list[str]:
    """M3-CHR-03: villager builds the guards cover (a `"villager": true` entry under "heroes" in rig_checks.json).
    Their GLB is assets/characters/villagers/<npc>/<npc>.glb and their clips are villager_clips.py's."""
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    return sorted(k for k, v in data.get("heroes", {}).items() if isinstance(v, dict) and v.get("villager"))


def is_villager(hero: str) -> bool:
    return hero not in hero_clips.PERSONA and hero in villagers()


def _villager_clips():
    if str(VILLAGERS_DIR) not in sys.path:
        sys.path.insert(0, str(VILLAGERS_DIR))
    import villager_clips

    return villager_clips


def clip_names(hero: str) -> list[str]:
    """The clips the game plays for this character (hero_clips.CLIPS, or villager_clips.clips_for)."""
    return _villager_clips().clips_for(hero) if is_villager(hero) else list(hero_clips.CLIPS[hero])


def hero_glb(hero: str) -> Path:
    base = Path(os.environ.get(ROOT_ENV) or ROOT)
    if is_villager(hero):
        return base / "assets" / "characters" / "villagers" / hero / f"{hero}.glb"
    return base / "assets" / "characters" / hero / f"{hero}.glb"


class Rig:
    def __init__(self, hero: str, glb: Path | None = None) -> None:
        self.hero = hero
        self.glb = Path(glb) if glb else hero_glb(hero)
        js, bin_ = asha_glb.read_glb(self.glb)
        self.js = js
        nodes = js["nodes"]
        self.names = [n.get("name", f"node{i}") for i, n in enumerate(nodes)]
        self.index = {n: i for i, n in enumerate(self.names)}
        self.parent = [-1] * len(nodes)
        for i, n in enumerate(nodes):
            for c in n.get("children", []):
                self.parent[c] = i
        self.rest_t = [np.array(n.get("translation", [0.0, 0.0, 0.0]), dtype=float) for n in nodes]
        self.rest_q = [np.array(n.get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=float) for n in nodes]
        self.rest_s = [np.array(n.get("scale", [1.0, 1.0, 1.0]), dtype=float) for n in nodes]
        for n in nodes:
            if "matrix" in n:
                raise ValueError(f"{self.glb}: node {n.get('name')} uses a matrix; the probe reads TRS only")
        # parents before children
        self.order: list[int] = []
        seen = set()

        def visit(i: int) -> None:
            if i in seen:
                return
            if self.parent[i] >= 0:
                visit(self.parent[i])
            seen.add(i)
            self.order.append(i)

        for i in range(len(nodes)):
            visit(i)
        if len(js.get("skins", [])) != 1:
            raise ValueError(f"{self.glb}: expected one skin")
        skin = js["skins"][0]
        self.joints = list(skin["joints"])
        self.joint_names = [self.names[j] for j in self.joints]
        ibm = asha_glb.accessor(js, bin_, skin["inverseBindMatrices"]).astype(np.float64)
        self.ibm = ibm.reshape(-1, 4, 4).transpose(0, 2, 1)  # glTF matrices are column-major
        self.prims: dict[str, list[Prim]] = {}
        for i, n in enumerate(nodes):
            if "mesh" not in n or "skin" not in n:
                continue
            mesh = js["meshes"][n["mesh"]]
            out = []
            for p in mesh["primitives"]:
                if p.get("mode", 4) != 4:
                    continue
                a = p["attributes"]
                mat = js["materials"][p["material"]]["name"] if "material" in p else ""
                P = asha_glb.accessor(js, bin_, a["POSITION"]).astype(np.float64)
                N = asha_glb.accessor(js, bin_, a["NORMAL"]).astype(np.float64) if "NORMAL" in a else np.zeros_like(P)
                J = asha_glb.accessor(js, bin_, a["JOINTS_0"]).astype(np.int64)
                W = asha_glb.accessor(js, bin_, a["WEIGHTS_0"]).astype(np.float64)
                if js["accessors"][a["WEIGHTS_0"]].get("normalized") and W.max() > 1.0:
                    W = W / (255.0 if W.max() <= 255 else 65535.0)
                F = asha_glb.accessor(js, bin_, p["indices"]).astype(np.int64).reshape(-1, 3)
                out.append(Prim(self.names[i], mat, P, N, J, W, F))
            self.prims[self.names[i]] = out
        self._sk = None

    # -- selection ------------------------------------------------------------------------------
    def part(self, spec, name: str | None = None) -> Part | None:
        """`spec`: "Mesh", "Mesh:material" or a list of those. None when nothing matches."""
        specs = [spec] if isinstance(spec, str) else list(spec)
        prims = []
        for s in specs:
            mesh, _, mat = s.partition(":")
            for pr in self.prims.get(mesh, []):
                if not mat or pr.material == mat:
                    prims.append(pr)
        if not prims:
            return None
        return Part(name or "+".join(specs), prims)

    # -- poses ----------------------------------------------------------------------------------
    @property
    def skeleton(self) -> "hero_clips.Skeleton":
        if self._sk is None:
            self._sk = hero_clips.Skeleton(self.glb)
        return self._sk

    def globals(self, local_q: dict | None = None, hips_t=None) -> list[np.ndarray]:
        """Global 4x4 of every node for local rotations {bone name: quaternion} (+ the hips translation)."""
        local_q = local_q or {}
        scales = local_q.get(hero_clips.SCALE_KEY, {})  # M1-CHR-15: the skirt panels' floor gathers
        moved = local_q.get(hero_clips.POS_KEY, {})  # M2-CHR-513: the reef-hooks, drawn
        g: list[np.ndarray | None] = [None] * len(self.names)
        hips = self.index.get(hero_clips.HIPS)
        for i in self.order:
            q = local_q.get(self.names[i], self.rest_q[i])
            t = hips_t if (i == hips and hips_t is not None) else np.asarray(moved.get(self.names[i], self.rest_t[i]))
            m = trs(t, q, np.asarray(scales.get(self.names[i], self.rest_s[i]), dtype=float))
            g[i] = m if self.parent[i] < 0 else g[self.parent[i]] @ m
        return g

    def skin_matrices(self, local_q: dict | None = None, hips_t=None) -> np.ndarray:
        g = self.globals(local_q, hips_t)
        return np.stack([g[j] for j in self.joints]) @ self.ibm

    @staticmethod
    def skin(part: Part, mats: np.ndarray, normals: bool = False):
        """Linear-blend-skinned positions (and normals, re-normalised) of a part for skin matrices `mats`."""
        M = np.einsum("nk,nkij->nij", part.W, mats[part.J])
        P = np.einsum("nij,nj->ni", M[:, :3, :3], part.P) + M[:, :3, 3]
        if not normals:
            return P
        N = np.einsum("nij,nj->ni", M[:, :3, :3], part.N)
        N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
        return P, N


@dataclass
class Pose:
    label: str
    local_q: dict
    hips_t: object = None
    kind: str = "clip"  # rest | stage | clip
    down: float = 0.0  # M2-CHR-520: how far a held prop is set down (released: the grip check skips the pose)


def parse_world_pose(tscn: Path) -> dict:
    """{bone: (x, y, z) degrees} from a stage scene's `world_pose = {...}` block, in file order."""
    text = Path(tscn).read_text(encoding="utf-8")
    m = re.search(r"world_pose\s*=\s*\{(.*?)\n\}", text, re.S)
    if not m:
        return {}
    out = {}
    for b, x, y, z in re.findall(r'"([^"]+)"\s*:\s*Vector3\(\s*([-\d.e]+)\s*,\s*([-\d.e]+)\s*,\s*([-\d.e]+)\s*\)',
                                 m.group(1)):
        out[b] = (float(x), float(y), float(z))
    return out


def world_pose_local(rig: Rig, world: dict) -> dict:
    """AshaStage._apply_world_pose: each listed bone (in order) turns about the stage axes on top of its current
    global pose, keeping its parent's (the bones' own rest scale is 1, so rotations compose as quaternions)."""
    glob_q = {}
    local = {}

    def gq(i: int) -> np.ndarray:
        name = rig.names[i]
        if name in glob_q:
            return glob_q[name]
        p = rig.parent[i]
        base = np.array([0.0, 0.0, 0.0, 1.0]) if p < 0 else gq(p)
        q = hero_clips.qmul(base, local.get(name, rig.rest_q[i]))
        glob_q[name] = q / np.linalg.norm(q)
        return glob_q[name]

    for bone, deg in world.items():
        i = rig.index[bone]
        glob_q.clear()
        cur = gq(i)
        new = hero_clips.qmul(hero_clips.qeuler(deg), cur)
        p = rig.parent[i]
        pq = np.array([0.0, 0.0, 0.0, 1.0]) if p < 0 else gq(p)
        lq = hero_clips.qmul(hero_clips.qinv(pq), new)
        local[bone] = lq / np.linalg.norm(lq)
    # M1-CHR-15: the stage then poses the helper bones from the rest (HeroHelperBones.drive)
    local.update(hero_clips.helper_locals(rig.skeleton, local))
    return local


def clip_poses(rig: Rig, every: int, clips: list | None = None, max_samples: int | None = None) -> list[Pose]:
    """Every `every`-th key (and always the last) of every clip, as hero_clips.build writes them; with `max_samples`,
    long clips widen the stride so they give at most about that many."""
    if is_villager(rig.hero):
        vc = _villager_clips()
        persona = vc.persona(rig.hero)
        length_of, is_loop, pose_fn = vc.length_of, vc.is_loop, vc.pose_at
    else:
        persona = hero_clips.PERSONA[rig.hero]
        length_of = lambda c: hero_clips.clip_length(rig.hero, c)  # noqa: E731  (M2-CHR-12: per-hero cycles)
        is_loop, pose_fn = hero_clips.LOOPS.__contains__, hero_clips.pose_at
    sk = rig.skeleton
    out = []
    if not clips and not is_villager(rig.hero) and rig.hero in hero_clips.BATTLE_STANCE:
        # the battle actor's own library (hero_clips.build_battle): its idle has the stance, its strikes build on it
        hero_clips._STANCE_ACTIVE.add(rig.hero)
        try:
            names = ["idle"] + [c for c in clip_names(rig.hero) if c in hero_clips.BATTLE_FRAMES or c == "revive"]
            out += [Pose(BATTLE_LIB_PREFIX + p.label, p.local_q, p.hips_t, p.kind, p.down)
                    for p in clip_poses(rig, every, names, max_samples)]
        finally:
            hero_clips._STANCE_ACTIVE.discard(rig.hero)
    for clip in clips or clip_names(rig.hero):
        length = length_of(clip)
        loop = is_loop(clip)
        n = int(round(length * hero_clips.FPS))
        stride = max(1, every)
        if max_samples:
            stride = max(stride, math.ceil(n / max(1, max_samples - 1)))
        frames = sorted(set(range(0, n + 1, stride)) | {n})
        # row 56: a walk or run whose skirt hem carries its momentum is baked frame by frame after a first pass round
        # the cycle (hero_clips.build); probe it the same way, every frame in order, keeping the sampled ones
        trail = loop and clip in getattr(hero_clips, "SKIRT_TRAIL_CLIPS", ()) and bool(getattr(sk, "skirt", None)) \
            and rig.hero in hero_clips.LOCO_GAIT
        sk.skirt_trail = {} if trail else None
        if trail:
            for f in range(n):
                tt = (f / hero_clips.FPS) % length
                p0 = hero_clips.staff_hold(pose_fn(clip, tt, length, sk, persona), persona)
                sk.local_pose({b: hero_clips.qeuler(v) for b, v in p0.items() if b != "hips"}, p0.get("hips"),
                              hero_clips.hook_hold(rig.hero, clip, tt / length))
        keep = set(frames)
        for f in (range(n + 1) if trail else frames):
            t = f / hero_clips.FPS
            tt = (t % length) if loop else t
            pose = hero_clips.staff_hold(pose_fn(clip, tt, length, sk, persona), persona)
            turns = {b: hero_clips.qeuler(v) for b, v in pose.items() if b != "hips"}
            hold = {} if is_villager(rig.hero) else hero_clips.hook_hold(rig.hero, clip, tt / length)
            local = sk.local_pose(turns, pose.get("hips"), hold)
            hips = sk.rest_t[hero_clips.HIPS] + np.asarray(pose.get("hips", (0.0, 0.0, 0.0)), dtype=float)
            if f in keep:
                out.append(Pose(f"{clip}@{f}", local, hips, "clip", float(hold.get("_down", 0.0))))
        sk.skirt_trail = None
    return out


def poses_for(rig: Rig, cfg: dict, every: int | None = None) -> list[Pose]:
    out = [Pose("rest", {}, None, "rest")]
    for label, rel in cfg.get("stage_poses", {}).items():
        out.append(Pose(label, world_pose_local(rig, parse_world_pose(ROOT / rel)), None, "stage"))
    if every:  # an explicit stride samples every clip at it
        out += clip_poses(rig, every)
    else:
        out += clip_poses(rig, int(cfg["every_nth_frame"]), max_samples=cfg.get("max_samples_per_clip"))
    return out


# ---------------------------------------------------------------------------------------------
# surfaces
# ---------------------------------------------------------------------------------------------
class Topology:
    """The pose-independent half of a surface: welded triangles, vertex -> incident triangles, open boundary."""

    def __init__(self, F: np.ndarray, P_rest: np.ndarray, weld_tol: float = 1e-6) -> None:
        self.F = F
        self.n = len(P_rest)
        self.weld_id = weld(P_rest, weld_tol)
        counts = np.bincount(F.reshape(-1), minlength=self.n)
        width = max(1, int(counts.max()))
        self.vt = np.full((self.n, width), -1, dtype=np.int64)
        flat_v = F.reshape(-1)
        flat_t = np.repeat(np.arange(len(F)), 3)
        order = np.argsort(flat_v, kind="stable")
        flat_v, flat_t = flat_v[order], flat_t[order]
        starts = np.searchsorted(flat_v, np.arange(self.n))
        self.vt[flat_v, np.arange(len(flat_v)) - starts[flat_v]] = flat_t
        self.used = np.nonzero(counts > 0)[0]
        wf = self.weld_id[F]
        e = np.concatenate([wf[:, [0, 1]], wf[:, [1, 2]], wf[:, [2, 0]]])
        e.sort(axis=1)
        e = e[e[:, 0] != e[:, 1]]
        uniq, cnt = np.unique(e, axis=0, return_counts=True)
        self.boundary = np.nonzero(np.isin(self.weld_id, np.unique(uniq[cnt == 1].reshape(-1))))[0]


def vertex_normals(P: np.ndarray, topo: Topology) -> np.ndarray:
    """Area-weighted vertex normals, welded by position so UV seams don't split them."""
    F = topo.F
    fn = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
    key = topo.weld_id[F]
    acc = np.zeros((int(topo.weld_id.max()) + 1, 3))
    for k in range(3):
        np.add.at(acc, key[:, k], fn)
    n = acc[topo.weld_id]
    return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)


@dataclass
class Hit:
    sd: np.ndarray  # signed distance along the surface normal (positive = the side the normals face: outside)
    closest: np.ndarray  # closest surface point
    normal: np.ndarray  # interpolated unit normal there
    facing: np.ndarray  # |cos| between (query - closest) and that normal: low = off past an open boundary
    vertex: np.ndarray  # nearest surface vertex
    tri: np.ndarray = None  # triangle of the closest point (-1 = far)
    bary: np.ndarray = None  # its barycentric weights


class Surface:
    """A posed triangle surface, for closest-point and signed-distance queries."""

    def __init__(self, topo: Topology, P: np.ndarray) -> None:
        self.topo, self.P = topo, P
        self.N = vertex_normals(P, topo)

    def query(self, q: np.ndarray, k: int = 3, reach: float | None = None) -> Hit:
        """Closest surface point of each query point: exact over the triangles around its k nearest vertices. With
        `reach` (metres), points with fewer than k surface vertices that near come back far (sd = +inf, facing 0)."""
        topo = self.topo
        if reach is None:
            near = topo.used[nearest_index(q, self.P[topo.used], k=k)]  # (n, k)
        else:
            ni = nearest_index(q, self.P[topo.used], k=k, cell=reach, far_ok=True)
            near = np.where(ni >= 0, topo.used[np.maximum(ni, 0)], -1)
        tris = np.where(near[:, :, None] >= 0, topo.vt[np.maximum(near, 0)], -1).reshape(len(q), -1)
        best_d = np.full(len(q), np.inf)
        best_c = np.zeros((len(q), 3))
        best_n = np.zeros((len(q), 3))
        best_t = np.full(len(q), -1, dtype=np.int64)
        best_b = np.zeros((len(q), 3))
        for col in range(tris.shape[1]):
            t = tris[:, col]
            ok = np.nonzero(t >= 0)[0]
            if not len(ok):
                continue
            f = topo.F[t[ok]]
            c, bary = closest_on_triangles(q[ok], self.P[f[:, 0]], self.P[f[:, 1]], self.P[f[:, 2]])
            d = np.linalg.norm(q[ok] - c, axis=1)
            better = d < best_d[ok]
            sel = ok[better]
            nrm = self.N[f[better, 0]] * bary[better, :1] + self.N[f[better, 1]] * bary[better, 1:2] + \
                self.N[f[better, 2]] * bary[better, 2:3]
            best_d[sel], best_c[sel], best_n[sel] = d[better], c[better], nrm
            best_t[sel], best_b[sel] = t[ok][better], bary[better]
        nn = np.maximum(np.linalg.norm(best_n, axis=1), 1e-12)
        best_n = best_n / nn[:, None]
        dot = np.einsum("ij,ij->i", q - best_c, best_n)
        sign = np.where(dot < 0, -1.0, 1.0)
        far = ~np.isfinite(best_d)
        dot[far] = 0.0
        facing = np.where(far, 0.0, np.where(best_d > 1e-9, np.abs(dot) / np.maximum(best_d, 1e-12), 1.0))
        return Hit(np.where(far, np.inf, sign * best_d), best_c, best_n, facing, np.maximum(near[:, 0], 0), best_t,
                   best_b)


def ray_hits(O: np.ndarray, D: np.ndarray, P: np.ndarray, F: np.ndarray, t_max: float,
             chunk: int = 16, detail: bool = False):
    """Nearest hit distance along each ray (inf = no triangle within t_max), Moller-Trumbore, both faces. With
    `detail`, also the hit triangle (-1 = none) and its (u, v) barycentrics."""
    a, b, c = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]
    e1, e2 = b - a, c - a
    out = np.full(len(O), np.inf)
    tri = np.full(len(O), -1, dtype=np.int64)
    uv = np.zeros((len(O), 2))
    lo = np.minimum(np.minimum(a, b), c)
    hi = np.maximum(np.maximum(a, b), c)
    for s in range(0, len(O), chunk):
        o, d = O[s:s + chunk], D[s:s + chunk]
        # only the triangles whose box meets the chunk's reach
        reach_lo = np.minimum(o, o + d * t_max).min(axis=0)
        reach_hi = np.maximum(o, o + d * t_max).max(axis=0)
        keep = np.nonzero(np.all(hi >= reach_lo, axis=1) & np.all(lo <= reach_hi, axis=1))[0]
        if not len(keep):
            continue
        E1, E2, A = e1[keep][None], e2[keep][None], a[keep][None]
        dd = np.broadcast_to(d[:, None, :], (len(o), len(keep), 3))
        pvec = np.cross(dd, E2)
        det = np.einsum("rtk,rtk->rt", np.broadcast_to(E1, pvec.shape), pvec)
        with np.errstate(divide="ignore", invalid="ignore"):
            inv = 1.0 / det
            tvec = o[:, None, :] - A
            u = np.einsum("rtk,rtk->rt", tvec, pvec) * inv
            qvec = np.cross(tvec, E1)
            v = np.einsum("rtk,rtk->rt", dd, qvec) * inv
            t = np.einsum("rtk,rtk->rt", np.broadcast_to(E2, qvec.shape), qvec) * inv
            ok = (np.abs(det) > 1e-14) & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0) & (t <= t_max)
        t = np.where(ok, t, np.inf)
        j = np.argmin(t, axis=1)
        r = np.arange(len(o))
        out[s:s + chunk] = t[r, j]
        tri[s:s + chunk] = np.where(np.isfinite(t[r, j]), keep[j], -1)
        uv[s:s + chunk] = np.stack([u[r, j], v[r, j]], axis=1)
    return (out, tri, uv) if detail else out


def winding_number(q: np.ndarray, P: np.ndarray, F: np.ndarray, chunk: int = 4096) -> np.ndarray:
    """Generalised winding number of each point w.r.t. the triangles (Van Oosterom-Strackee solid angles / 4 pi):
    ~1 inside a closed outward-wound surface, ~0 outside, in between near holes."""
    w = np.zeros(len(q))
    for s in range(0, len(F), chunk):
        f = F[s:s + chunk]
        a = P[f[:, 0]][None] - q[:, None]
        b = P[f[:, 1]][None] - q[:, None]
        c = P[f[:, 2]][None] - q[:, None]
        la, lb, lc = (np.linalg.norm(x, axis=2) for x in (a, b, c))
        num = np.einsum("ntk,ntk->nt", a, np.cross(b, c))
        den = la * lb * lc + np.einsum("ntk,ntk->nt", a, b) * lc + np.einsum("ntk,ntk->nt", b, c) * la + \
            np.einsum("ntk,ntk->nt", c, a) * lb
        w += 2.0 * np.arctan2(num, den).sum(axis=1)
    return w / (4.0 * math.pi)


def components(F: np.ndarray, weld_id: np.ndarray, n: int) -> np.ndarray:
    """Connected-component label per vertex (over the welded triangles), labels 0..k-1 (min-label propagation with
    pointer jumping)."""
    lab = np.arange(int(weld_id.max()) + 1)
    wf = weld_id[F]
    e = np.concatenate([wf[:, [0, 1]], wf[:, [1, 2]], wf[:, [2, 0]]])
    while True:
        m = np.minimum(lab[e[:, 0]], lab[e[:, 1]])
        new = lab.copy()
        np.minimum.at(new, e[:, 0], m)
        np.minimum.at(new, e[:, 1], m)
        new = new[new]  # pointer jumping
        if np.array_equal(new, lab):
            break
        lab = new
    _, out = np.unique(lab[weld_id[:n]], return_inverse=True)
    return out.reshape(-1)


def dominant_bone(rig: Rig, part: Part, i: int) -> str:
    k = int(np.argmax(part.W[i]))
    return rig.joint_names[int(part.J[i, k])]


# ---------------------------------------------------------------------------------------------
# the checks
# ---------------------------------------------------------------------------------------------
def _mm(x: float) -> float:
    return round(float(x) * 1000.0, 2)


def _xyz(p) -> list:
    return [round(float(c), 3) for c in p]


class Probe:
    """Everything pose-independent for one hero, then `run(poses)` -> per-check, per-pose rows."""

    def __init__(self, hero: str, cfg: dict | None = None, glb: Path | None = None) -> None:
        self.hero = hero
        self.cfg = cfg or load_config(hero)
        self.rig = rig = Rig(hero, glb)
        pen, seams = self.cfg["penetration"], self.cfg["seams"]
        self.weld_tol = float(seams["weld_tol_mm"]) / 1000.0
        # the body skin (body + head skin): what clothes and props must stay outside of
        body = rig.part(self.cfg["body"])
        self.skin = rig.part([self.cfg["body"]] + list(self.cfg["skin_extra"]), "skin")
        self.skin_topo = Topology(self.skin.F, self.skin.P)
        nb = len(body.P)  # the body's vertices come first in `skin`
        self.garments = [p for p in (rig.part(s, s) for s in self.cfg["garments"]) if p is not None]
        self.props = [p for p in (rig.part(s, s) for s in self.cfg["props"]) if p is not None]
        self.groups = [(p, False) for p in self.garments] + [(p, True) for p in self.props]
        # props a scene hides in some clips: {mesh: "battle"} (the battle clip contract, e.g. Kerrid's back cleaver,
        # which his battle actor hides for the instance in his hand) or a list of clip names
        battle = set(hero_clips.BATTLE_CLIPS) | {"revive"}
        self.hidden = {m: (battle if v == "battle" else set(v)) for m, v in self.cfg.get("hidden_props", {}).items()}
        self.hidden_in_battle = {m for m, v in self.cfg.get("hidden_props", {}).items() if v == "battle"}
        grip = re.compile(pen["grip_bones"])
        self.grip_vertex = np.array([bool(grip.search(dominant_bone(rig, self.skin, i)))
                                     for i in range(len(self.skin.P))])
        self.cloth = rig.part(self.cfg["garments"], "garments") if self.garments else None
        self.covered = np.zeros(0, dtype=np.int64)
        if self.cloth is not None:
            self.cloth_topo = Topology(self.cloth.F, self.cloth.P)
            # body skin with clothing over it at rest: a ray along the skin normal meets a garment within cover_mm.
            # The cloth point it meets (triangle + barycentrics) is tracked through every pose, and skin that passes
            # that same cloth point pokes through. Relative to rest by construction (at rest the cloth is in front),
            # so a garment edge beside the skin, or a layer passing inside the body (garment_in_body's job), can't
            # fire it.
            body_N = vertex_normals(self.skin.P, self.skin_topo)[:nb]
            _, tri, uv = ray_hits(body.P, body_N, self.cloth.P, self.cloth.F, float(pen["cover_mm"]) / 1000.0,
                                  detail=True)
            self.covered = np.nonzero(tri >= 0)[0]
            self.cover_tri, self.cover_uv = tri[self.covered], uv[self.covered]
        # seams: positions that coincide at rest inside each group
        self.seam_groups = []
        for spec in seams["groups"]:
            part = rig.part(spec, "+".join(spec) if isinstance(spec, list) else spec)
            if part is None:
                continue
            wid = weld(part.P, self.weld_tol)
            cnt = np.bincount(wid)
            dup = np.nonzero(cnt[wid] > 1)[0]
            first = np.full(len(cnt), len(wid))
            np.minimum.at(first, wid[dup], dup)  # the lowest index of each coincident set
            keep = dup[first[wid[dup]] != dup]
            self.seam_groups.append((part, keep, first[wid[keep]]))
        # the body's open boundary, less the welded seam to the head (checked as a coincident seam)
        sb = self.skin_topo.boundary[self.skin_topo.boundary < nb]
        wid = weld(self.skin.P, self.weld_tol)
        other = np.zeros(int(wid.max()) + 1, dtype=int)
        np.add.at(other, wid[nb:], 1)
        bb = sb[other[wid[sb]] == 0]
        cells = np.floor(self.skin.P[bb] / 0.05).astype(np.int64)  # spatially compact ray chunks
        self.body_boundary = bb[np.lexsort((cells[:, 2], cells[:, 0], cells[:, 1]))]
        self.braid = self._braid_setup(self.cfg.get("braid"))
        self.grip = self._grip_setup(self.cfg.get("prop_grip"))

    # -- prop grip (M2-CHR-515) ------------------------------------------------------------------
    def _grip_setup(self, gc: dict | None):
        entry = None
        if gc and GRIPS.exists():
            entry = json.loads(GRIPS.read_text(encoding="utf-8"))["skeletons"].get(f"{self.hero}_skeleton")
        if not entry or not self.props:
            return None
        rig = self.rig
        b, h = rig.index[entry["bone"]], rig.index[entry["hand"]]
        g = rig.globals()
        G_b, G_h = g[b], g[h]
        rel0 = np.linalg.inv(G_h) @ G_b
        bind = rel0.copy()  # the prop as the GLB binds it: no clip or stage solve has placed it (the bind pose)
        # M2-CHR-544: the grip moves the prop's bone (in the hand's frame) so its shaft runs through the closed fist
        rel0[:3, 3] += np.asarray(entry.get("offset", (0.0, 0.0, 0.0)), dtype=float)
        # the shaft: the prop vertices skinned to its bone, in the bone's frame (its local y runs up the shaft)
        loc = []
        for part in self.props:
            own = part.J[np.arange(len(part.P)), np.argmax(part.W, axis=1)] == rig.joints.index(b)
            if own.any():
                loc.append((np.linalg.inv(G_b) @ np.c_[part.P[own], np.ones(int(own.sum()))].T).T[:, :3])
        if not loc:
            raise ValueError(f"{self.hero}: no prop vertex skinned to {entry['bone']}")
        loc = np.concatenate(loc)
        radial = np.hypot(loc[:, 0], loc[:, 2])
        return {"bone": b, "hand": h, "rel0": rel0, "bind": bind, "y": (float(loc[:, 1].min()), float(loc[:, 1].max())),
                "r": float(np.median(radial)) * float(gc["surface_lines_at"]),
                "clear": float(gc["grip_clear_mm"]) / 1000.0, "name": entry["bone"]}

    def _grip_rows(self, pose: Pose, cloth_P) -> list[dict]:
        gr, rig = self.grip, self.rig
        g = rig.globals(pose.local_q, pose.hips_t)
        G_b, G_h = g[gr["bone"]], g[gr["hand"]]
        rel = np.linalg.inv(G_h) @ G_b
        R = gr["rel0"][:3, :3].T @ rel[:3, :3]
        turn = math.degrees(math.acos(float(np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0))))
        # the fist's grip point (the prop bone's head at rest, carried by the hand) against the posed shaft axis
        grip = (G_h @ gr["rel0"][:, 3])[:3]
        o, d = G_b[:3, 3], G_b[:3, 1] / np.linalg.norm(G_b[:3, 1])
        v = grip - o
        offset = float(np.linalg.norm(v - (v @ d) * d))
        unposed = np.allclose(rel, gr["bind"], atol=1e-6)  # the bind pose: nothing places the prop there
        rows = [] if pose.down > 0.0 or unposed else [{"pose": pose.label, "kind": "grip", "group": gr["name"],
                                              "turn_deg": round(turn, 3), "offset_mm": _mm(offset)}]
        if self.cloth is not None:
            if cloth_P is None:
                cloth_P = rig.skin(self.cloth, mats=rig.skin_matrices(pose.local_q, pose.hips_t))
            ax, az = G_b[:3, 0], G_b[:3, 2]
            ax, az = ax / np.linalg.norm(ax), az / np.linalg.norm(az)
            lines = [np.zeros(3)] + [gr["r"] * c for c in (ax, -ax, az, -az)]
            lo, hi = gr["y"]
            hits, where = 0, "-"
            for a, z in ((lo, -gr["clear"]), (gr["clear"], hi)):  # below the fist, then above it
                if z <= a:
                    continue
                O = np.array([o + d * a + c for c in lines])
                t, tri, _ = ray_hits(O, np.tile(d, (len(O), 1)), cloth_P, self.cloth.F, z - a, detail=True)
                hit = np.isfinite(t)
                hits += int(hit.sum())
                if hit.any() and where == "-":
                    k = int(np.nonzero(hit)[0][0])
                    pr = self.cloth.prims[int(self.cloth.src[int(self.cloth.F[tri[k], 0])])]
                    where = f"{pr.mesh}:{pr.material} on {dominant_bone(rig, self.cloth, int(self.cloth.F[tri[k], 0]))}"
            rows.append({"pose": pose.label, "kind": "through_garment", "group": gr["name"], "count": hits,
                         "where": where})
        return rows

    # -- braid ----------------------------------------------------------------------------------
    def _braid_setup(self, bc: dict | None):
        if not bc:
            return None
        rig = self.rig
        part = rig.part(bc["mesh"], bc["mesh"])
        scalp = rig.part(bc["scalp"], "scalp")
        topo = Topology(scalp.F, scalp.P)
        btopo = Topology(part.F, part.P)
        lab = components(part.F, btopo.weld_id, len(part.P))
        sizes = np.bincount(lab)
        strands = np.nonzero(sizes >= int(bc["min_strand_verts"]))[0]
        if not len(strands):
            raise ValueError(f"{self.hero}: no braid strand of {bc['min_strand_verts']}+ vertices in {bc['mesh']}")
        rest_sd = Surface(topo, scalp.P).query(part.P).sd
        ring_r = float(bc["root_ring_mm"]) / 1000.0
        rings = []
        for s in strands:
            idx = np.nonzero(lab == s)[0]
            ends = np.intersect1d(idx, btopo.boundary)  # a tube's open ends; the root is the one nearer the scalp
            cand = ends if len(ends) else idx
            r0 = cand[np.argmin(rest_sd[cand])]
            rings.append(cand[np.linalg.norm(part.P[cand] - part.P[r0], axis=1) <= ring_r])
        return {"part": part, "scalp": scalp, "topo": topo, "rings": rings,
                "head": rig.joint_names.index(bc["head_bone"])}

    def _braid_row(self, pose: Pose, mats: np.ndarray, mats_rest: np.ndarray) -> dict:
        b = self.braid
        rig = self.rig
        Pb = rig.skin(b["part"], mats)
        surf = Surface(b["topo"], rig.skin(b["scalp"], mats))
        allr = np.concatenate(b["rings"])
        sd = surf.query(Pb[allr]).sd
        gaps = []
        o = 0
        for ring in b["rings"]:
            v = sd[o:o + len(ring)]
            o += len(ring)
            gaps.append((max(float(v.min()), 0.0), float(np.clip(v, 0, None).mean()), float(v.max())))
        worst = max(range(len(gaps)), key=lambda k: gaps[k][0])
        g, mean, mx = gaps[worst]
        # drift: how far the root moves in the head bone's frame (0 when it is skinned rigidly to the head)
        h = b["head"]
        G_pose = mats[h] @ np.linalg.inv(rig.ibm[h])
        G_rest = mats_rest[h] @ np.linalg.inv(rig.ibm[h])
        Pr = rig.skin(b["part"], mats_rest)[allr]
        loc_pose = (np.linalg.inv(G_pose) @ np.c_[Pb[allr], np.ones(len(allr))].T).T[:, :3]
        loc_rest = (np.linalg.inv(G_rest) @ np.c_[Pr, np.ones(len(allr))].T).T[:, :3]
        drift = float(np.linalg.norm(loc_pose - loc_rest, axis=1).max())
        part = b["part"]
        bones = sorted({rig.joint_names[int(j)] for i in allr for j, w in zip(part.J[i], part.W[i]) if w > 0.01})
        return {"pose": pose.label, "gap_mm": _mm(g), "ring_mean_mm": _mm(mean), "ring_max_mm": _mm(mx),
                "drift_mm": _mm(drift), "strand": worst, "strands": len(b["rings"]),
                "root_rest": _xyz(part.P[b["rings"][worst]].mean(axis=0)), "root_bones": bones}

    # -- penetration ----------------------------------------------------------------------------
    def _penetration_rows(self, pose: Pose, mats: np.ndarray, skin_surf: Surface):
        rig, pen = self.rig, self.cfg["penetration"]
        fmin, max_depth = float(pen["facing_min"]), float(pen["max_depth_mm"]) / 1000.0
        k = int(pen["neighbours"])
        lim = float(pen["max_mm"]) / 1000.0
        reach = max_depth + float(pen["reach_margin_mm"]) / 1000.0
        confirm, wmin = int(pen["confirm_deepest"]), float(pen["winding_min"])
        rows = []
        clip = pose.label.split("@")[0]
        in_battle_lib = clip.startswith(BATTLE_LIB_PREFIX)  # the battle actor's own library: its scene hides these
        clip = clip[len(BATTLE_LIB_PREFIX):] if in_battle_lib else clip
        for part, is_prop in self.groups:
            hidden = clip in self.hidden.get(part.name, ()) or (in_battle_lib and part.name in self.hidden_in_battle)
            if is_prop and hidden:  # hidden in this clip (a battle actor's back prop)
                continue
            P = rig.skin(part, mats)
            h = skin_surf.query(P, k, reach)
            valid = (h.facing >= fmin) & (h.sd >= -max_depth)
            if is_prop:
                valid &= ~self.grip_vertex[h.vertex]
            depth = np.where(valid, np.maximum(-h.sd, 0.0), 0.0)
            # confirm the deepest candidates with the skin's winding number (inside = mostly enclosed by skin);
            # a point the normals call "inside" that the skin does not enclose is beside a limb or a hole
            # (in batches from the deepest down, until one is confirmed; the count is of confirmed ones)
            cand = np.nonzero(depth > lim)[0]
            cand = cand[np.argsort(-depth[cand])][:confirm]
            checked = np.zeros(len(depth), dtype=bool)
            for s in range(0, len(cand), CONFIRM_BATCH):
                batch = cand[s:s + CONFIRM_BATCH]
                wn = winding_number(P[batch], skin_surf.P, self.skin_topo.F)
                depth[batch[wn < wmin]] = 0.0
                checked[batch] = True
                if (wn >= wmin).any():
                    break
            depth[~checked] = np.where(depth[~checked] > lim, 0.0, depth[~checked])  # unconfirmed: not counted
            i = int(np.argmax(depth))
            pr = part.prims[int(part.src[i])]
            rows.append({"pose": pose.label, "kind": "prop_in_body" if is_prop else "garment_in_body",
                         "group": part.name, "depth_mm": _mm(depth[i]), "count": int((depth > lim).sum()),
                         "where": f"{pr.mesh}:{pr.material}", "bone": dominant_bone(rig, part, i),
                         "skin_bone": dominant_bone(rig, self.skin, int(h.vertex[i])), "rest": _xyz(part.P[i])})
        cloth_P = None
        if self.cloth is not None and len(self.covered):
            cloth_P = rig.skin(self.cloth, mats)
            f = self.cloth.F[self.cover_tri]
            u, v = self.cover_uv[:, :1], self.cover_uv[:, 1:]
            over = cloth_P[f[:, 0]] * (1 - u - v) + cloth_P[f[:, 1]] * u + cloth_P[f[:, 2]] * v
            Ps = skin_surf.P[self.covered]
            # how far the skin has passed the cloth point that was over it, along the posed skin normal
            rel = Ps - over
            past = np.einsum("ij,ij->i", rel, skin_surf.N[self.covered])
            # only while that cloth point is still over the skin (slid sideways less than max_depth): farther off,
            # the skin has left that cloth, not passed through it
            lateral = np.linalg.norm(rel - past[:, None] * skin_surf.N[self.covered], axis=1)
            depth = np.where(lateral <= max_depth, np.maximum(past, 0.0), 0.0)
            i = int(np.argmax(depth))
            vi = int(self.covered[i])
            pr = self.cloth.prims[int(self.cloth.src[int(f[i, 0])])]
            rows.append({"pose": pose.label, "kind": "skin_through_garment", "group": "Body",
                         "depth_mm": _mm(depth[i]), "count": int((depth > lim).sum()),
                         "where": f"Body through {pr.mesh}:{pr.material}", "bone": dominant_bone(rig, self.skin, vi),
                         "skin_bone": dominant_bone(rig, self.cloth, int(f[i, 0])), "rest": _xyz(self.skin.P[vi])})
        return rows, cloth_P

    # -- seams ----------------------------------------------------------------------------------
    def _seam_rows(self, pose: Pose, mats: np.ndarray, skin_surf: Surface, cloth_P) -> list[dict]:
        rig, seams = self.rig, self.cfg["seams"]
        rows = []
        for part, dup, rep in self.seam_groups:
            if not len(dup):
                continue
            P = rig.skin(part, mats)
            gap = np.linalg.norm(P[dup] - P[rep], axis=1)
            i = int(np.argmax(gap))
            a, b = int(dup[i]), int(rep[i])
            pa, pb = part.prims[int(part.src[a])], part.prims[int(part.src[b])]
            rows.append({"pose": pose.label, "kind": "coincident", "group": part.name, "open_mm": _mm(gap[i]),
                         "count": int((gap > float(seams["max_open_mm"]) / 1000.0).sum()),
                         "where": f"{pa.mesh}:{pa.material} / {pb.mesh}:{pb.material}",
                         "bone": f"{dominant_bone(rig, part, a)} / {dominant_bone(rig, part, b)}",
                         "rest": _xyz(part.P[a])})
        if self.cloth is not None and len(self.body_boundary):
            if cloth_P is None:
                cloth_P = rig.skin(self.cloth, mats)
            O = skin_surf.P[self.body_boundary]
            D = skin_surf.N[self.body_boundary]
            t = ray_hits(O, D, cloth_P, self.cloth.F, float(seams["cover_reach_mm"]) / 1000.0)
            exposed = ~np.isfinite(t)
            near = np.zeros(len(O))
            if exposed.any():
                h = Surface(self.cloth_topo, cloth_P).query(O[exposed])
                near[exposed] = np.linalg.norm(O[exposed] - h.closest, axis=1)
            i = int(np.argmax(near))
            vi = int(self.body_boundary[i])
            rows.append({"pose": pose.label, "kind": "boundary_exposed", "group": "Body boundary",
                         "open_mm": _mm(near[i]), "count": int(exposed.sum()), "of": int(len(O)),
                         "where": "Body", "bone": dominant_bone(rig, self.skin, vi), "rest": _xyz(self.skin.P[vi])})
        return rows

    def weights_report(self) -> dict:
        """Static skin-data sanity: weights sum to 1, joint indices exist, no negative weights."""
        tol = float(self.cfg["seams"]["weight_sum_tol"])
        worst = {"sum_err": 0.0, "where": "-", "bad_joint": 0, "negative": 0}
        for mesh, prims in self.rig.prims.items():
            for pr in prims:
                err = float(np.abs(pr.W.sum(axis=1) - 1.0).max())
                if err > worst["sum_err"]:
                    worst["sum_err"], worst["where"] = err, f"{mesh}:{pr.material}"
                worst["bad_joint"] += int((pr.J >= len(self.rig.joints)).sum())
                worst["negative"] += int((pr.W < 0).sum())
        worst["ok"] = worst["sum_err"] <= tol and worst["bad_joint"] == 0 and worst["negative"] == 0
        return worst

    # -- driver ---------------------------------------------------------------------------------
    def run(self, poses: list[Pose]) -> dict:
        rig = self.rig
        mats_rest = rig.skin_matrices()
        out = {"hero": self.hero, "poses": [p.label for p in poses], "braid": [], "penetration": [], "seams": [],
               "grip": [], "weights": self.weights_report()}
        for pose in poses:
            mats = rig.skin_matrices(pose.local_q, pose.hips_t)
            skin_surf = Surface(self.skin_topo, rig.skin(self.skin, mats))
            if self.braid:
                out["braid"].append(self._braid_row(pose, mats, mats_rest))
            rows, cloth_P = self._penetration_rows(pose, mats, skin_surf)
            out["penetration"] += rows
            out["seams"] += self._seam_rows(pose, mats, skin_surf, cloth_P)
            if self.grip:
                out["grip"] += self._grip_rows(pose, cloth_P)
        return out


# ---------------------------------------------------------------------------------------------
# verdicts and the report
# ---------------------------------------------------------------------------------------------
def verdicts(result: dict, cfg: dict) -> list[dict]:
    """One line per check and group: the worst pose, its value, the limit and pass/fail."""
    pen, seams, bc = cfg["penetration"], cfg["seams"], cfg.get("braid") or {}
    out = []
    if result["braid"]:
        for key, lim in (("gap_mm", bc["max_gap_mm"]), ("drift_mm", bc["max_drift_mm"])):
            w = max(result["braid"], key=lambda r: r[key])
            out.append({"check": f"braid {key[:-3]}", "value_mm": w[key], "limit_mm": lim, "ok": w[key] <= lim,
                        "pose": w["pose"], "where": f"strand {w['strand']} of {w['strands']}, root at rest "
                        f"{w['root_rest']}, root bones {', '.join(w['root_bones'])}"})
    for kind, group in sorted({(r["kind"], r["group"]) for r in result["penetration"]}):
        w = max((r for r in result["penetration"] if r["kind"] == kind and r["group"] == group),
                key=lambda r: r["depth_mm"])
        lim = float(pen.get("limits_mm", {}).get(group, pen["max_mm"]))
        # a group with a documented allowance (limits_mm) may also cap how many vertices pass max_mm in any pose
        n_lim = pen.get("limits_count", {}).get(group)
        n_worst = max(r["count"] for r in result["penetration"] if r["kind"] == kind and r["group"] == group)
        ok = w["depth_mm"] <= lim and (n_lim is None or n_worst <= int(n_lim))
        out.append({"check": f"penetration {kind} {group}", "value_mm": w["depth_mm"], "limit_mm": lim,
                    "count": n_worst, "count_limit": n_lim, "ok": ok, "pose": w["pose"],
                    "where": f"{w['where']} on {w['bone']} vs {w['skin_bone']}, rest {w['rest']} "
                    f"({w['count']} verts past {pen['max_mm']} mm)"})
    for kind, group in sorted({(r["kind"], r["group"]) for r in result["seams"]}):
        rows = [r for r in result["seams"] if r["kind"] == kind and r["group"] == group]
        if kind == "boundary_exposed":
            w = max(rows, key=lambda r: (r["count"], r["open_mm"]))
            lim = int(seams["max_exposed"])
            out.append({"check": "seam boundary_exposed", "value_mm": w["open_mm"], "count": w["count"],
                        "limit": lim, "ok": w["count"] <= lim, "pose": w["pose"],
                        "where": f"{w['count']} of {w['of']} open body-boundary verts with no garment over them "
                        f"(farthest {w['open_mm']} mm from cloth, on {w['bone']}, rest {w['rest']})"})
        else:
            w = max(rows, key=lambda r: r["open_mm"])
            lim = float(seams["max_open_mm"])
            out.append({"check": f"seam coincident {group}", "value_mm": w["open_mm"], "limit_mm": lim,
                        "ok": w["open_mm"] <= lim, "pose": w["pose"],
                        "where": f"{w['where']} ({w['bone']}), rest {w['rest']} ({w['count']} verts past {lim} mm)"})
    gc = cfg.get("prop_grip") or {}
    grows = result.get("grip", [])
    for key, lim, kind in (("turn_deg", "max_turn_deg", "grip"), ("offset_mm", "max_offset_mm", "grip")):
        rows = [r for r in grows if r["kind"] == kind]
        if rows:
            w = max(rows, key=lambda r: r[key])
            out.append({"check": f"prop grip {key[:-3] if key.endswith('_mm') else key[:-4]}", "value": w[key],
                        "limit": gc[lim], "ok": w[key] <= float(gc[lim]), "pose": w["pose"],
                        "where": f"{w['group']} in its hand ({key})"})
    allow = set(gc.get("allow_clips", []))  # documented per hero (a follow-up task each), never a default
    rows = [r for r in grows if r["kind"] == "through_garment"]
    if rows:
        kept = [r for r in rows if r["pose"].split("@")[0] not in allow] or [dict(rows[0], count=0)]
        n_allowed = sum(1 for r in rows if r["pose"].split("@")[0] in allow and r["count"] > 0)
        w = max(kept, key=lambda r: r["count"])
        out.append({"check": "prop through_garment", "value": w["count"], "limit": 0, "ok": w["count"] == 0,
                    "pose": w["pose"], "where": f"{w['group']} shaft lines crossing {w['where']}"
                    f" ({n_allowed} poses in the {len(allow)} allowed clips)"})
    wr = result["weights"]
    out.append({"check": "skin weights", "value": round(wr["sum_err"], 6), "limit": seams["weight_sum_tol"],
                "ok": wr["ok"], "pose": "-",
                "where": f"max |sum-1| on {wr['where']}; bad joints {wr['bad_joint']}, negative {wr['negative']}"})
    return out


def probe(hero: str, every: int | None = None, cfg: dict | None = None,
          glb: Path | None = None) -> tuple[dict, list[dict]]:
    cfg = cfg or load_config(hero)
    p = Probe(hero, cfg, glb)
    result = p.run(poses_for(p.rig, cfg, every))
    result["glb"] = str(p.rig.glb)
    return result, verdicts(result, cfg)


def format_report(result: dict, verdict: list[dict], per_pose: bool = True) -> str:
    lines = [f"# rig probe: {result['hero']} ({len(result['poses'])} poses) -- {result.get('glb', '')}", "",
             "## verdicts"]
    for v in verdict:
        val = v.get("value_mm", v.get("value"))
        lim = v.get("limit_mm", v.get("limit", "-"))
        cnt = f" count={v['count']}" if "count" in v else ""
        if v.get("count_limit") is not None:
            cnt += f" (limit {v['count_limit']})"
        lines.append(f"{'ok  ' if v['ok'] else 'FAIL'} {v['check']:<48} {val!s:>8} (limit {lim}){cnt} @ {v['pose']}"
                     f"  -- {v['where']}")
    if per_pose:
        if result["braid"]:
            lines += ["", "## braid (per pose, mm)",
                      f"{'pose':<24}{'gap':>8}{'ring_mean':>11}{'ring_max':>10}{'drift':>8}"]
            for r in result["braid"]:
                lines.append(f"{r['pose']:<24}{r['gap_mm']:>8}{r['ring_mean_mm']:>11}{r['ring_max_mm']:>10}"
                             f"{r['drift_mm']:>8}")
        lines += ["", "## penetration (per pose, worst per group, mm; zero rows omitted)"]
        for r in result["penetration"]:
            if r["depth_mm"] > 0:
                lines.append(f"{r['pose']:<24}{r['kind']:<22}{r['group']:<12}{r['depth_mm']:>8}  n={r['count']:<5}"
                             f"{r['where']} on {r['bone']} vs {r['skin_bone']}, rest {r['rest']}")
        lines += ["", "## seams (per pose, mm; zero rows omitted)"]
        for r in result["seams"]:
            if r["open_mm"] > 0 or r.get("count"):
                lines.append(f"{r['pose']:<24}{r['kind']:<18}{r['group']:<26}{r['open_mm']:>8}  n={r['count']:<5}"
                             f"{r['where']} ({r['bone']}), rest {r['rest']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Headless rig probe for the heroes (M1-CHR-14).")
    ap.add_argument("--hero", choices=sorted(hero_clips.PERSONA) + villagers(), action="append",
                    help="default: every hero (the villagers in rig_checks.json only when named)")
    ap.add_argument("--report", action="store_true", help="print the verdicts and the per-pose tables")
    ap.add_argument("--every", type=int, help="clip key stride (default: every_nth_frame in rig_checks.json)")
    ap.add_argument("--json", type=Path, help="write the full result (rows and verdicts) here")
    ap.add_argument("--glb", type=Path, help="probe this GLB instead (one --hero only)")
    ap.add_argument("--root", type=Path, help=f"read assets/characters/<hero>/<hero>.glb under this checkout "
                    f"(same as {ROOT_ENV})")
    args = ap.parse_args(argv)
    if args.root:
        os.environ[ROOT_ENV] = str(args.root)
    if args.glb and len(args.hero or []) != 1:
        ap.error("--glb needs exactly one --hero")
    dump = {}
    failed = False
    for hero in args.hero or sorted(hero_clips.PERSONA):
        result, verdict = probe(hero, args.every, glb=args.glb)
        dump[hero] = {"result": result, "verdicts": verdict}
        failed |= not all(v["ok"] for v in verdict)
        print(format_report(result, verdict, per_pose=args.report))
        print()
    if args.json:
        args.json.write_text(json.dumps(dump, indent=1), encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
