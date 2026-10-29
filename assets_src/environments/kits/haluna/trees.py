"""The Haluna kit's two trees (M2-ENV-07): the hero banyan at the chapel court and the windbreak tree
in the rows behind the houses (haluna.md §1.3, §5.1 H01/H02/H07).

They are grown by the vegetation generators (assets_src/environments/vegetation/banyan.py and
windbreak.py: leaf-level sprays on twigs, painted bark, buttresses, prop and aerial roots) and only
exported here, as kit pieces, so the Haluna dresser places them with no layout or scene change:

  banyan_hero     the hero banyan, 14 m, ~25 m across
  windbreak_tree  the windbreak tree, 8 m, an upright oval crown

The piece names are the scene contract: haluna_layout.json places them, the zone's collision table
and test_haluna_zone.gd name them. Until M3-ENV-750 they were `banyan_placeholder` and
`windbreak_placeholder` (the names of M1's stand-ins), with the same geometry.

Kit pieces carry exactly two LODs (`<piece>`, `<piece>-lod1`); the dresser draws LOD1 beyond
`lod1_from_m` (75 m in Haluna). The vegetation frame (+Z up) is converted to the kit's (Godot's +Y up,
-Z north): Blender (x, y, z) -> Godot (x, z, -y), which kit_common.export_glb turns straight back,
so the exported vertices are exactly the generator's. The wind channels (COLOR, UV2) follow the
vegetation convention, read by the vegetation bark and foliage shaders of the kit materials.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

import kit_common as kc

VEG_SRC = Path(__file__).resolve().parents[2] / "vegetation"
if str(VEG_SRC) not in sys.path:
    sys.path.append(str(VEG_SRC))  # after the kit's own modules, so kit names win

import banyan  # noqa: E402
import windbreak  # noqa: E402

# Generator material slot -> kit material (assets/environments/kits/haluna/materials/<slot>.tres).
SLOTS = {
    "banyan_bark": "kit_banyan_bark",
    "banyan_root": "kit_banyan_root",
    "banyan_leaf": "kit_banyan_leaf",
    "windbreak_bark": "kit_windbreak_bark",
    "windbreak_leaf": "kit_windbreak_leaf",
}

TRI_BUDGET = {
    "banyan_hero": tuple(banyan.TRI_BUDGET),
    "windbreak_tree": tuple(windbreak.TRI_BUDGET),
}


def to_kit(vmb, name: str) -> kc.MeshBuilder:
    """A vegetation MeshBuilder (+Z up) as a kit MeshBuilder (+Y up), slots renamed to kit materials."""
    mb = kc.MeshBuilder(name)
    pos = np.asarray(vmb.pos, dtype=float)
    nrm = np.asarray(vmb.nrm, dtype=float)
    mb.pos = np.column_stack([pos[:, 0], pos[:, 2], -pos[:, 1]]).tolist()
    mb.nrm = np.column_stack([nrm[:, 0], nrm[:, 2], -nrm[:, 1]]).tolist()
    mb.uv = [list(q) for q in vmb.uv]
    mb.uv2 = [list(q) for q in vmb.uv2]
    mb.col = [list(q) for q in vmb.col]
    mb.tris = [tuple(t) for t in vmb.tris]
    mb.tri_mat = list(vmb.tri_mat)
    mb.materials = [SLOTS[m] for m in vmb.materials]
    return mb


def _export(builders: list, piece: str) -> list[kc.MeshBuilder]:
    return [to_kit(b, piece if i == 0 else f"{piece}-lod{i}") for i, b in enumerate(builders)]


def build_banyan(piece: str = "banyan_hero") -> list[kc.MeshBuilder]:
    return _export(banyan.build("hero"), piece)


def build_windbreak(piece: str = "windbreak_tree") -> list[kc.MeshBuilder]:
    return _export(windbreak.build("a"), piece)


TARGETS = {"banyan_hero": build_banyan, "windbreak_tree": build_windbreak}
