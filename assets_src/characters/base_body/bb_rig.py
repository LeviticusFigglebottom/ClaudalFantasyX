"""Rig stage for the base body (M1-CHR-01). Runs inside Blender (bpy).

1. Add Rigify's human metarig, delete its face bones (faces use the shared blendshape API in
   asha.md §6.2), add `eye.L` / `eye.R` (basic.super_copy) under the head.
2. Fit every bone to the landmarks from bb_params, keeping each bone's original roll axis.
3. `rigify_generate` the control rig (kept in the optional .blend for animators).
4. Build a clean, deform-only game skeleton from the generated `DEF-*` bones, each parented to
   its nearest deforming ancestor, and skin the body to it with Blender's automatic (bone-heat)
   weights. That skeleton is what the .glb carries.
"""
from __future__ import annotations

import addon_utils
import bpy
import numpy as np
from mathutils import Vector

from bb_params import Landmarks, unit, v3

KEEP_PREFIX = (
    "spine", "shoulder.", "upper_arm.", "forearm.", "hand.", "palm.", "f_index.", "f_middle.", "f_ring.",
    "f_pinky.", "thumb.", "breast.", "pelvis.", "thigh.", "shin.", "foot.", "toe.", "heel.02.",
)


def _targets(lm: Landmarks) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    S = lm.S
    P = lm.P
    t: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    z_hp = P("hip")[2]
    z_notch = P("notch")[2]
    sp0 = v3(0, 0.025 * S, z_hp + 0.01 * S)
    sp1 = v3(0, 0.02 * S, z_hp + 0.14 * S)
    sp2 = v3(0, 0.012 * S, P("waist")[2] + 0.06 * S)
    sp3 = v3(0, 0.01 * S, P("nipple")[2] + 0.01 * S)
    sp4 = v3(0, 0.012 * S, z_notch - 0.012 * S)
    nb, sb = P("neck_base"), P("skull_base")
    sp5 = nb + (sb - nb) * 0.5 + v3(0, 0.012 * S, 0)
    sp6 = sb + v3(0, 0.004 * S, 0)
    crown = v3(0, sb[1], P("crown")[2])
    chain = [sp0, sp1, sp2, sp3, sp4, sp5, sp6, crown]
    names = ["spine"] + [f"spine.{i:03d}" for i in range(1, 7)]
    for i, n in enumerate(names):
        t[n] = (chain[i], chain[i + 1])
    for side in ("L", "R"):
        sp = lm.side_pt
        sh, el, wr = sp("shoulder", side), sp("elbow", side), sp("wrist", side)
        a_up = unit(el - sh)
        t[f"shoulder.{side}"] = (sp("clavicle_in", side) + v3(0, 0.012 * S, 0.006 * S),
                                 sh - a_up * 0.022 * S + v3(0, 0.004 * S, 0.018 * S))
        t[f"upper_arm.{side}"] = (sh, el)
        t[f"forearm.{side}"] = (el, wr)
        hand = lm.hands[side]
        palm_len = float(np.linalg.norm(hand.knuckle - hand.wrist))
        t[f"hand.{side}"] = (wr, wr + hand.axis * palm_len * 0.42)
        fingers = {fg.name: fg for fg in hand.fingers}
        for i, nm in enumerate(("f_index", "f_middle", "f_ring", "f_pinky")):
            fg = fingers[nm]
            base = wr + hand.axis * palm_len * 0.2 + (fg.joints[0] - hand.knuckle) * 0.55
            t[f"palm.{i + 1:02d}.{side}"] = (base, fg.joints[0])
            for k in range(3):
                t[f"{nm}.{k + 1:02d}.{side}"] = (fg.joints[k], fg.joints[k + 1])
        th = fingers["thumb"]
        for k in range(3):
            t[f"thumb.{k + 1:02d}.{side}"] = (th.joints[k], th.joints[k + 1])
        nip = sp("nipple", side)
        t[f"breast.{side}"] = (nip + v3(0, 0.11 * S, 0), nip + v3(0, -0.01 * S, 0))
        hp = sp("hip", side)
        t[f"pelvis.{side}"] = (sp0, hp + v3(0.02 * S * (1 if side == "L" else -1), -0.07 * S, 0.09 * S))
        kn, an = sp("knee", side), sp("ankle", side)
        ball, tt = sp("ball", side), sp("toe_tip", side)
        t[f"thigh.{side}"] = (hp, kn)
        t[f"shin.{side}"] = (kn, an)
        t[f"foot.{side}"] = (an, ball + v3(0, 0, 0.012 * S))
        t[f"toe.{side}"] = (ball + v3(0, 0, 0.012 * S), tt + v3(0, 0, 0.008 * S))
        hb = sp("heel_back", side)
        sgn = 1 if side == "L" else -1
        t[f"heel.02.{side}"] = (v3(hb[0] - 0.035 * S * sgn, hb[1] - 0.01 * S, 0.0),
                                v3(hb[0] + 0.035 * S * sgn, hb[1] - 0.01 * S, 0.0))
        e = sp("eye", side)
        t[f"eye.{side}"] = (e, e + v3(0, -0.025 * S, 0))
    return t


def build_metarig(lm: Landmarks) -> bpy.types.Object:
    addon_utils.enable("rigify", default_set=True)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.armature_human_metarig_add()
    meta = bpy.context.active_object
    meta.name = "metarig"
    targets = _targets(lm)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = meta.data.edit_bones
    for b in list(eb):
        if not b.name.startswith(KEEP_PREFIX):
            eb.remove(b)
    head = eb["spine.006"]
    for side in ("L", "R"):
        e = eb.new(f"eye.{side}")
        e.parent = head
        e.use_deform = True
    old_z = {b.name: b.z_axis.copy() for b in eb}
    old_z["eye.L"] = Vector((0, 0, 1))
    old_z["eye.R"] = Vector((0, 0, 1))
    # move every bone with connections off, then restore the metarig's own connect flags
    # (Rigify decides chain extents from them, e.g. the neck must stay unconnected to the chest)
    was_connected = {b.name: b.use_connect for b in eb}
    was_connected["eye.L"] = was_connected["eye.R"] = False
    for b in eb:
        b.use_connect = False
    for name, (h, tl) in targets.items():
        b = eb[name]
        b.head = Vector(h.tolist())
        b.tail = Vector(tl.tolist())
        b.align_roll(old_z[name])
    for b in eb:
        if was_connected[b.name]:
            b.use_connect = True
    bpy.ops.object.mode_set(mode="OBJECT")
    for side in ("L", "R"):
        pb = meta.pose.bones[f"eye.{side}"]
        pb.rigify_type = "basic.super_copy"
    return meta


def generate_rig(meta: bpy.types.Object) -> bpy.types.Object:
    before = set(bpy.data.objects.keys())
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = meta
    meta.select_set(True)
    bpy.ops.pose.rigify_generate()
    new = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]
    rigs = [o for o in new if o.type == "ARMATURE"]
    if not rigs:  # regenerated in place
        rigs = [o for o in bpy.data.objects if o.type == "ARMATURE" and o.name != meta.name]
    rig = rigs[0]
    rig.name = "rig"
    return rig


def _def_parent(rig: bpy.types.Object, name: str) -> str | None:
    bones = rig.data.bones
    b = bones[name].parent
    while b is not None:
        if b.name.startswith("DEF-"):
            return b.name
        if b.name.startswith("ORG-"):
            cand = "DEF-" + b.name[4:]
            if cand in bones and cand != name:
                return cand
        b = b.parent
    return None


def build_game_skeleton(rig: bpy.types.Object, name: str) -> bpy.types.Object:
    """A deform-only armature: every DEF-* bone, re-parented to its nearest deforming ancestor."""
    defs = [b.name for b in rig.data.bones if b.use_deform and b.name.startswith("DEF-")]
    parents = {n: _def_parent(rig, n) for n in defs}
    rest = {}
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for n in defs:
        e = rig.data.edit_bones[n]
        rest[n] = (e.head.copy(), e.tail.copy(), e.roll)
    bpy.ops.object.mode_set(mode="OBJECT")
    arm = bpy.data.armatures.new(name)
    ob = bpy.data.objects.new(name, arm)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for n in defs:
        e = arm.edit_bones.new(n)
        e.head, e.tail, e.roll = rest[n]
        e.use_deform = True
    for n in defs:
        if parents[n]:
            arm.edit_bones[n].parent = arm.edit_bones[parents[n]]
    bpy.ops.object.mode_set(mode="OBJECT")
    return ob


def skin(body_ob: bpy.types.Object, rig: bpy.types.Object, skel: bpy.types.Object) -> dict:
    """Bone-heat weights against the generated rig's DEF bones, then retarget to the skeleton."""
    bpy.ops.object.select_all(action="DESELECT")
    body_ob.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    # verts the heat solver left unweighted get the nearest bone (logged, should be 0)
    me = body_ob.data
    groups = {g.index: g.name for g in body_ob.vertex_groups}
    unweighted = [v.index for v in me.vertices if sum(g.weight for g in v.groups) < 1e-4]
    if unweighted:
        heads = {n: (rig.data.bones[n].head_local + rig.data.bones[n].tail_local) / 2 for n in groups.values()}
        for vi in unweighted:
            co = me.vertices[vi].co
            best = min(heads, key=lambda n: (heads[n] - co).length)
            body_ob.vertex_groups[best].add([vi], 1.0, "REPLACE")
    # move the mesh onto the clean skeleton
    mod = next(m for m in body_ob.modifiers if m.type == "ARMATURE")
    mod.object = skel
    body_ob.parent = skel
    return {"unweighted_fixed": len(unweighted), "groups": len(groups)}


def attach_rigid(ob: bpy.types.Object, skel: bpy.types.Object, bone: str) -> None:
    vg = ob.vertex_groups.new(name=bone)
    vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = skel
    ob.parent = skel
