"""Oruvel rebuilt (M3-ENV-730; oruvel.md §7, act3_ending E7, colour script `post_credits`): the raft-town after the
Ending, the same moorings rebuilt, not the same hulls. Pure numpy; see ov_common.py.

  raft_deck_rebuilt  raft_deck's frame and moorings (9 x 7 m, deck at RAFT_DECK_Y) on three new hulls in other
                     colourways, about a third of its planks new timber (`ov_timber_new`) among the silvered old ones
  lamp_post          the first lamp of a world without glimmer (E7): a new timber post on a raft's corner, an iron
                     bracket and hook, and a diver's oil lantern with its wick hanging from it. Unlit here: the flame
                     is the stager's OmniLight (`ending_grades.json` post_credits `lamp`), at LAMP_AT
"""

from __future__ import annotations

import numpy as np

import ov_common as oc
import ov_hulls as ohl

kc = oc.kc

M_TIMBER_NEW = "ov_timber_new"

TRI_BUDGET = {"raft_deck_rebuilt": (18000, 900), "lamp_post": (1500, 150)}

NEW_SHARE = 0.33  # of the deck's planks
POST_H = 2.6
LAMP_AT = (0.55, POST_H - 0.62, 0.0)  # the lantern's chimney centre, lamp_post's frame


def _components(mb: kc.MeshBuilder) -> list[np.ndarray]:
    """The triangles of each separate closed part (each plank is its own)."""
    t = np.asarray(mb.tris)
    parent = np.arange(len(mb.pos))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a, b, c in t:
        ra, rb, rc = find(a), find(b), find(c)
        parent[rb] = ra
        parent[find(rc)] = ra
    roots = np.array([find(a) for a in t[:, 0]])
    return [np.nonzero(roots == r)[0] for r in np.unique(roots)]


def build_raft_deck_rebuilt(seed: int = 781) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("raft_deck_rebuilt", seed)
        noise = kc.Noise3(rng)
        hulls = [(-3.0, 10.8, 2.3, 1.15, oc.M_PAINT_TEAL), (0.0, 11.2, 2.4, 1.2, oc.M_PAINT_OCHRE),
                 (3.0, 10.8, 2.2, 1.1, oc.M_PAINT)]
        mb = ohl.raft("raft_deck_rebuilt" + (oc.LOD if lod else ""), 9.0, 7.0, ohl.RAFT_DECK_Y, hulls, rng, noise,
                      lod=lod)
        if not lod:  # new planks among the old: the deck boards (long, thin, their tops at the deck line)
            p = np.asarray(mb.pos)
            new = mb.material(M_TIMBER_NEW)
            tm = np.asarray(mb.tri_mat)
            col = np.asarray(mb.col, float)
            t = np.asarray(mb.tris)
            for comp in _components(mb):
                v = np.unique(t[comp])
                y, ext = p[v, 1], np.ptp(p[v][:, [0, 2]], axis=0)
                if y.max() > ohl.RAFT_DECK_Y + 0.03 or y.min() < ohl.RAFT_DECK_Y - 0.08 or ext.max() < 1.5:
                    continue
                if rng.random() < NEW_SHARE:
                    tm[comp] = new
                    col[v, 1] *= 0.3  # little salt yet
                    col[v, 3] *= 0.3  # crisp edges
            mb.tri_mat = tm.tolist()
            mb.col = col.tolist()
        out.append(mb)
    return out


def build_lamp_post(seed: int = 782) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lamp_post", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("lamp_post" + (oc.LOD if lod else ""))
        new, iron, rope = mb.material(M_TIMBER_NEW), mb.material(oc.M_IRON), mb.material(oc.M_ROPE)
        kc.plank(mb, (0.0, 0.0, 0.0), (0.0, POST_H, 0.0), 0.14, 0.14, new, up=(1.0, 0.0, 0.0), noise=noise,
                 variation=float(rng.random()), seg=1 if lod else 3)
        # The bracket: an iron arm out from the post's head, a diagonal brace under it, a hook at its end.
        arm_y = POST_H - 0.12
        kc.tube(mb, np.array([[0.07, arm_y, 0.0], [LAMP_AT[0] + 0.04, arm_y, 0.0]]), 0.018, 4 if lod else 6, iron)
        if not lod:
            kc.tube(mb, np.array([[0.07, arm_y - 0.45, 0.0], [0.4, arm_y - 0.01, 0.0]]), 0.012, 5, iron)
            hook = np.array([[LAMP_AT[0], arm_y, 0.0], [LAMP_AT[0], arm_y - 0.1, 0.0], [LAMP_AT[0] + 0.03, arm_y - 0.14,
                                                                                         0.0]])
            kc.tube(mb, hook, 0.008, 4, iron)
            # The lashing that seats the post on the raft's corner cleat, and a cap board against the rain.
            oc.lashing(mb, (0.0, 0.35, 0.0), (0.0, 1.0, 0.0), 0.1, rope, turns=4)
            kc.rounded_block(mb, (0.0, POST_H + 0.02, 0.0), (0.11, 0.02, 0.11), new, radius=0.01, seg=1)
        oc.lantern(mb, (LAMP_AT[0], arm_y - 0.47, 0.0), rng, scale=1.1, lod=lod)
        if not lod:  # the new wick in the chimney (the flame is the stager's light)
            kc.tube(mb, np.array([[LAMP_AT[0], arm_y - 0.47 + 0.05, 0.0], [LAMP_AT[0], arm_y - 0.47 + 0.09, 0.0]]),
                    0.006, 4, mb.material(oc.M_WICK))
        out.append(mb)
    return out


TARGETS = {"raft_deck_rebuilt": build_raft_deck_rebuilt, "lamp_post": build_lamp_post}
