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

    def __init__(self, rig: ck.Rig, mesh: ck.Mesh | list[ck.Mesh]) -> None:
        """`mesh`: one mesh, or several in the same rig (M3-CRE-632: a body and its extra meshes, e.g. a rim)."""
        self.rig = rig
        self.names = [b.name for b in rig.bones]
        self.parent = [rig.index(b.parent) if b.parent else -1 for b in rig.bones]
        self.heads = [np.asarray(b.head, dtype=np.float64) for b in rig.bones]
        arrays = [m.arrays() for m in (mesh if isinstance(mesh, (list, tuple)) else [mesh])]
        pos = np.concatenate([a["pos"] for a in arrays])
        self.P = np.c_[pos, np.ones(len(pos))]
        self.J = np.concatenate([a["joints"] for a in arrays])
        self.W = np.concatenate([a["weights"] for a in arrays])
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
            M = _local(self.heads[i], rot, loc)
            mats[i] = M if self.parent[i] < 0 else mats[self.parent[i]] @ M  # M3-CRE-632: the root may be a limb

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
    its subtree's vertices at or above `floor`. `axis` may also be (wx, wy, wz): the turn adds `sign` × c × w to the
    bone's Euler degrees (M3-CRE-632: a leg splayed round a body turns about its own outward axis)."""
    rot0, loc0 = pose.get(bone, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))

    def low(c: float) -> float:
        rot, loc = list(rot0), list(loc0)
        if isinstance(axis, tuple):
            rot = [r + sign * c * w for r, w in zip(rot, axis)]
        elif axis == LIFT:
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


def grounded(rig: ck.Rig, mesh: ck.Mesh | list[ck.Mesh], clips: list[ck.Clip], limbs: list[tuple],
             floor: float = 0.0) -> list[ck.Clip]:
    """`limbs`: (bone, axis 0/1/2, (wx, wy, wz) or LIFT, sign, limit) per limb, in order; the turn is `sign` × degrees
    about the bone's rest axis (up to `limit`), or a lift up to `limit` metres. An optional fifth item, a tuple of clip
    names, corrects the limb in those clips only (M3-CRE-632; it keeps its authored pose in the others). The root may
    be a limb (a lift of the whole body), and `mesh` may be a list (a body and its extra meshes). Returns the clips
    (plus hit_b and idle_b) with those bones keyed at every frame."""
    return reground(rig, mesh, ck.with_variety(clips), limbs, floor)


def reground(rig: ck.Rig, mesh: ck.Mesh | list[ck.Mesh], clips: list[ck.Clip], limbs: list[tuple],
             floor: float = 0.0) -> list[ck.Clip]:
    """grounded() on clips that already carry their hit_b and idle_b: a second pass after pinned(), whose held feet
    can tip a toe or a pad under the floor."""
    poser = Poser(rig, mesh)
    subs = {b: poser.subtree(b) for b, *_ in limbs}
    masks = {b: (np.isin(poser.J, subs[b]) & (poser.W > 1e-6)).any(axis=1) for b in subs}
    out = []
    for clip in clips:
        fixed = ck.Clip(clip.name, clip.length, loop=clip.loop)
        for b, ks in clip.keys.items():
            if b not in subs:
                fixed.keys[b] = list(ks)
        for t in frame_times(clip):
            pose = pose_at(clip, poser.names, t)
            mats = poser.matrices(pose)
            for b, axis, sign, limit, *only in limbs:
                if not only or clip.name in only[0]:
                    _correct(poser, mats, pose, b, subs[b], masks[b], axis, sign, limit, floor)
                fixed.key(b, t, pose[b][0], pose[b][1])
        out.append(fixed)
    return out


# ---------------------------------------------------------------------------------------------------------------------
# Planted feet (the Act I final-quality audit, 2026-10-29): grounded() keeps a foot on the floor but lets it slide
# along it while the body skitters, rears or recoils over it (tools/creatures/clip_audit.gd measured up to 37 cm).
# pinned() holds a planted foot where it touched down: while a leg's tip stays on the floor, a small solve turns the
# hip (about the vertical, and about the leg's bend axis) and the knee so the tip keeps its spot, then eases the
# correction out over RELEASE_FRAMES once the foot lifts.
# ---------------------------------------------------------------------------------------------------------------------
PIN_CLIPS = ("idle", "idle_b", "ready", "attack", "cast", "hit", "hit_b")  # a KO collapses: its feet go where it falls
PLANT_M = 0.03  # a tip within this of the floor is planted (a skitter lifts a dragged foot ~2 cm; a step or a tap, 8)
RELEASE_FRAMES = 4
PIN_ITERS = 10
PIN_FLOOR_PASSES = 10  # re-solves that lift a held foot whose toes went under the floor
PIN_DAMP = 1e-6  # Levenberg-Marquardt damping (m^2 per deg^2)
PIN_MAX_STEP_DEG = 8.0  # the most one iteration turns a joint
PIN_STEP_DEG = 0.5  # the solve's finite-difference step
PIN_LIMIT_DEG = 50.0  # the most the pin turns any joint
PIN_ROUND = 5  # decimals the solved turns keep, so a build is byte-identical on every numpy SIMD path


def _turn(rot, spec, sign: float, c: float) -> tuple:
    """`rot` turned by c degrees: about a rest axis (0/1/2) or along a weighted axis (wx, wy, wz)."""
    r = list(rot)
    if isinstance(spec, tuple):
        return tuple(v + sign * c * w for v, w in zip(r, spec))
    r[spec] += sign * c
    return tuple(r)


def pinned(rig: ck.Rig, mesh: ck.Mesh | list[ck.Mesh], clips: list[ck.Clip], legs: list[tuple],
           floor: float = 0.0, only: tuple = PIN_CLIPS) -> list[ck.Clip]:
    """`legs`: (upper bone, lower bone or None, bend axis 0/1/2 or (wx, wy, wz), sign) per leg; the upper bone's yaw
    is its Euler y. A leg of one bone (a fin planted on the floor) is held by its yaw and bend alone. Run after grounded() (it adds no hit_b or idle_b of its own). Clips not in `only` are returned as they
    are; in the others the legs' two bones are keyed at every frame."""
    poser = Poser(rig, mesh)
    legs_i = []
    for up, low, axis, sign in legs:
        sub = poser.subtree(up)
        lower = poser.subtree(low if low is not None else up)
        mask = (np.isin(poser.J, lower) & (poser.W > 0.5)).any(axis=1)
        rest = poser.vertices(poser.matrices({}), mask)
        tip = int(np.flatnonzero(mask)[int(np.argmin(rest[:, 1]))])
        whole = (np.isin(poser.J, sub) & (poser.W > 1e-6)).any(axis=1)  # every vertex the leg moves (paw, toes)
        legs_i.append((up, low, axis, sign, sub, tip, whole))
    out = []
    for clip in clips:
        if clip.name not in only:
            out.append(clip)
            continue
        fixed = ck.Clip(clip.name, clip.length, loop=clip.loop)
        moved = {b for leg in legs_i for b in leg[:2] if b is not None}  # (up, low, ...)
        for b, ks in clip.keys.items():
            if b not in moved:
                fixed.keys[b] = list(ks)
        times = frame_times(clip)
        poses = [pose_at(clip, poser.names, t) for t in times]
        for up, low, axis, sign, sub, tip, whole in legs_i:
            anchor = None
            hold = np.zeros(3)
            fade = 0
            for k, t in enumerate(times):
                pose = poses[k]
                mats = poser.matrices(pose)
                p = poser.vertices(mats, np.eye(1, len(poser.P), tip, dtype=bool)[0])[0]
                planted = p[1] <= floor + PLANT_M
                if planted:
                    if anchor is None:
                        anchor = np.array([p[0], floor, p[2]])
                    c = _solve(poser, mats, pose, up, low, axis, sign, sub, tip, anchor, hold)
                    # held at its spot, the leg may tip a toe or a pad under the floor: raise the target by that much
                    for _ in range(PIN_FLOOR_PASSES):
                        under = floor - _leg_low(poser, mats, pose, up, low, axis, sign, sub, whole, c)
                        if under <= 1e-4:
                            break
                        c = _solve(poser, mats, pose, up, low, axis, sign, sub, tip, anchor + [0.0, under, 0.0], c)
                    hold, fade = c, RELEASE_FRAMES
                else:
                    anchor = None
                    if fade > 0:  # ease the last correction out rather than snap the leg back
                        fade -= 1
                        hold = hold * (fade / RELEASE_FRAMES)
                        # the fading turn must not push the lifting foot through the floor (the authored pose, which
                        # grounded() set on it, never does): shrink it until the leg clears
                        for _ in range(PIN_FLOOR_PASSES + 1):
                            if _leg_low(poser, mats, pose, up, low, axis, sign, sub, whole, hold) >= floor - 1e-4:
                                break
                            hold = hold * 0.5
                        else:
                            hold = np.zeros(3)
                    else:
                        hold = np.zeros(3)
                    c = hold
                c = np.round(c, PIN_ROUND)
                rot_up, loc_up = pose.get(up, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
                r_up = _turn(_turn(rot_up, 1, 1.0, float(c[0])), axis, sign, float(c[1]))
                fixed.key(up, t, r_up, loc_up)
                if low is not None:
                    rot_low, loc_low = pose.get(low, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
                    fixed.key(low, t, _turn(rot_low, axis, sign, float(c[2])), loc_low)
        out.append(fixed)
    return out


def _leg_low(poser: Poser, mats, pose: dict, up: str, low: str | None, axis, sign: float, sub: list[int],
             whole: np.ndarray, c: np.ndarray) -> float:
    """The leg's lowest vertex y with the turns `c` applied (the pose and `mats` are left as they were)."""
    keep = {b: pose[b] for b in (up, low) if b is not None and b in pose}
    rot_up, loc_up = pose.get(up, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
    pose[up] = (_turn(_turn(rot_up, 1, 1.0, float(c[0])), axis, sign, float(c[1])), loc_up)
    if low is not None:
        rot_low, loc_low = pose.get(low, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
        pose[low] = (_turn(rot_low, axis, sign, float(c[2])), loc_low)
    poser.resolve(mats, pose, sub)
    y = float(poser.vertices(mats, whole)[:, 1].min())
    for b in (up, low):
        if b is None:
            continue
        if b in keep:
            pose[b] = keep[b]
        else:
            pose.pop(b, None)
    poser.resolve(mats, pose, sub)
    return y


def _solve(poser: Poser, mats, pose: dict, up: str, low: str, axis, sign: float, sub: list[int], tip: int,
           target: np.ndarray, start: np.ndarray) -> np.ndarray:
    """Turns (hip yaw, hip bend, knee bend) in degrees that bring the tip to `target` (damped least squares)."""
    rot_up, loc_up = pose.get(up, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
    rot_low, loc_low = pose.get(low, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))) if low is not None else ((), ())
    one = np.eye(1, len(poser.P), tip, dtype=bool)[0]
    n = 3 if low is not None else 2

    def tip_at(c: np.ndarray) -> np.ndarray:
        pose[up] = (_turn(_turn(rot_up, 1, 1.0, float(c[0])), axis, sign, float(c[1])), loc_up)
        if low is not None:
            pose[low] = (_turn(rot_low, axis, sign, float(c[2])), loc_low)
        poser.resolve(mats, pose, sub)
        return poser.vertices(mats, one)[0]

    c = np.array(start, dtype=np.float64)
    for _ in range(PIN_ITERS):
        r = tip_at(c) - target
        if float(np.linalg.norm(r)) < 1e-4:
            break
        J = np.zeros((3, 3))
        for j in range(n):
            d = np.zeros(3)
            d[j] = PIN_STEP_DEG
            J[:, j] = (tip_at(c + d) - tip_at(c)) / PIN_STEP_DEG  # tip_at(c) recomputed: resolve() leaves mats posed
        # damped (Levenberg-Marquardt) and clamped, so a far target never flings a joint to another solution
        A = J.T @ J + PIN_DAMP * np.eye(3)
        step = np.linalg.solve(A, -J.T @ r)
        step = np.clip(step, -PIN_MAX_STEP_DEG, PIN_MAX_STEP_DEG)
        c = np.clip(c + step, -PIN_LIMIT_DEG, PIN_LIMIT_DEG)
    tip_at(np.zeros(3))  # leave the pose as it was: the caller keys the result
    pose[up] = (rot_up, loc_up)
    if low is not None:
        pose[low] = (rot_low, loc_low)
    return c
