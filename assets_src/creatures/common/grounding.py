"""Keep a creature's clips off the floor (M3-CRE-631): docs/kb/art/creatures/pipeline.md.

Pure numpy, no Blender. It poses the rig and the mesh at every baked frame of a clip exactly as creature_kit's export
does (keys sampled at f / FPS, rotations about the rest axes at each bone's head, offsets in the armature frame), so a
build can measure its clips and correct them before export.

`grounded(rig, mesh, clips, limbs)` returns the clips (with the kit's `hit_b` and `idle_b` derived first, from the
authored clips, so the correction is never mirrored or scaled) with each limb re-keyed at every frame: where a limb's
lowest vertex would go under the floor, the limb is turned (or lifted) by the least amount that sets it on the floor.
A foot planted at rest then stays planted while the body bobs over it, instead of sinking through the ground. Frames
where the limb is clear keep their authored pose, so a clip that never dips is unchanged.
"""

from __future__ import annotations

import numpy as np

import creature_kit as ck


def _local(head, rot, loc) -> np.ndarray:
    """A bone's pose relative to its parent, as creature_kit's export builds it: T(head + loc) @ R(rot) @ T(-head)."""
    h = np.asarray(head, dtype=np.float64)
    M = np.eye(4)
    M[:3, :3] = ck.euler(*rot)
    M[:3, 3] = h + np.asarray(loc, dtype=np.float64) - M[:3, :3] @ h
    return M


class Poser:
    """Skinning matrices of a rig in a pose, and the mesh posed by them (Godot axes, metres)."""

    def __init__(self, rig: ck.Rig, mesh: ck.Mesh) -> None:
        self.rig = rig
        self.names = [b.name for b in rig.bones]
        self.parent = [rig.index(b.parent) if b.parent else -1 for b in rig.bones]
        self.heads = [np.asarray(b.head, dtype=np.float64) for b in rig.bones]
        a = mesh.arrays()
        self.P = np.c_[a["pos"], np.ones(len(a["pos"]))]
        self.J, self.W = a["joints"], a["weights"]
        self.children: dict[int, list[int]] = {i: [] for i in range(len(self.names))}
        for i, p in enumerate(self.parent):
            if p >= 0:
                self.children[p].append(i)

    def subtree(self, name: str) -> list[int]:
        out, todo = [], [self.rig.index(name)]
        while todo:
            i = todo.pop(0)
            out.append(i)
            todo.extend(self.children[i])
        return out

    def matrices(self, pose: dict) -> list[np.ndarray]:
        """`pose`: {bone: (rot degrees, loc metres)}; bones not in it stay at rest. Parents precede children."""
        mats: list[np.ndarray] = []
        for i, name in enumerate(self.names):
            rot, loc = pose.get(name, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
            M = _local(self.heads[i], rot, loc)
            mats.append(M if self.parent[i] < 0 else mats[self.parent[i]] @ M)
        return mats

    def resolve(self, mats: list[np.ndarray], pose: dict, bones: list[int]) -> None:
        """Recomputes `mats` for `bones` (a subtree, parents first) after their keys in `pose` changed."""
        for i in bones:
            rot, loc = pose.get(self.names[i], ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
            mats[i] = mats[self.parent[i]] @ _local(self.heads[i], rot, loc)

    def vertices(self, mats: list[np.ndarray], mask: np.ndarray | None = None) -> np.ndarray:
        S = np.asarray(mats)
        P, J, W = (self.P, self.J, self.W) if mask is None else (self.P[mask], self.J[mask], self.W[mask])
        out = np.zeros((len(P), 3))
        for k in range(J.shape[1]):
            out += W[:, k:k + 1] * np.einsum("nij,nj->ni", S[J[:, k]], P)[:, :3]
        return out


def frame_times(clip: ck.Clip) -> list[float]:
    frames = max(int(round(clip.length * ck.FPS)), 1)
    return [min(f / ck.FPS, clip.length) for f in range(frames + 1)]


def pose_at(clip: ck.Clip, bones: list[str], t: float) -> dict:
    out = {}
    for b in bones:
        rot, loc = clip.sample(b, t)
        if b == "root" and clip.name in ck.IN_PLACE_CLIPS:
            loc = np.array([0.0, loc[1], 0.0])
        out[b] = (tuple(float(v) for v in rot), tuple(float(v) for v in loc))
    return out


def lowest(poser: Poser, clip: ck.Clip) -> list[float]:
    """The lowest vertex y at every baked frame of `clip`."""
    return [float(poser.vertices(poser.matrices(pose_at(clip, poser.names, t)))[:, 1].min()) for t in frame_times(clip)]


def _correct(poser: Poser, mats, pose, bone: str, sub: list[int], mask, axis: int, sign: float, limit: float,
             floor: float) -> float:
    """The least turn (degrees about the rest `axis`, or a lift in metres when axis is "lift") of `bone` that puts
    its subtree's vertices at or above `floor`."""
    rot0, loc0 = pose.get(bone, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))

    def low(c: float) -> float:
        rot, loc = list(rot0), list(loc0)
        if axis == 3:
            loc[1] += c
        else:
            rot[axis] += sign * c
        pose[bone] = (tuple(rot), tuple(loc))
        poser.resolve(mats, pose, sub)
        return float(poser.vertices(mats, mask)[:, 1].min())

    if low(0.0) >= floor:
        return 0.0
    # the first of STEPS steps that clears the floor, then bisect down to the least; when none does (the limb can't
    # reach), the step that comes closest, so a limb is never flung to its limit for nothing
    best, best_low, hi = 0.0, low(0.0), None
    for k in range(1, STEPS + 1):
        c = limit * k / STEPS
        y = low(c)
        if y >= floor:
            hi = c
            break
        if y > best_low + 1e-9:
            best, best_low = c, y
    if hi is None:
        low(best)
        return best
    lo = hi - limit / STEPS
    for _ in range(32):
        mid = 0.5 * (lo + hi)
        if low(mid) >= floor:
            hi = mid
        else:
            lo = mid
    low(hi)
    return hi


LIFT = 3  # a limb spec's axis: lift the limb along its parent's up (metres) instead of turning it
STEPS = 16  # the search's coarse steps over a limb's range


def grounded(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip], limbs: list[tuple], floor: float = 0.0) -> list[ck.Clip]:
    """`limbs`: (bone, axis 0/1/2 or LIFT, sign, limit) per limb, in order; the turn is `sign` × degrees about the
    bone's rest axis (up to `limit`), or a lift up to `limit` metres. Returns the clips (plus hit_b and idle_b) with
    those bones keyed at every frame."""
    poser = Poser(rig, mesh)
    subs = {b: poser.subtree(b) for b, *_ in limbs}
    masks = {b: (np.isin(poser.J, subs[b]) & (poser.W > 1e-6)).any(axis=1) for b in subs}
    out = []
    for clip in ck.with_variety(clips):
        fixed = ck.Clip(clip.name, clip.length, loop=clip.loop)
        for b, ks in clip.keys.items():
            if b not in subs:
                fixed.keys[b] = list(ks)
        for t in frame_times(clip):
            pose = pose_at(clip, poser.names, t)
            mats = poser.matrices(pose)
            for b, axis, sign, limit in limbs:
                _correct(poser, mats, pose, b, subs[b], masks[b], axis, sign, limit, floor)
                fixed.key(b, t, pose[b][0], pose[b][1])
        out.append(fixed)
    return out
