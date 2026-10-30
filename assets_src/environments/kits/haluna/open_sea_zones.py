"""Ch15's open sea (M4-A2P-045; open_sea_ch15.md), built from act1-chapters' greybox
(game/levels/ch15/open_sea/open_sea_layout.json), read here so the barge follows the greybox if it moves. Pure numpy.

  open_sea_barge  Merel's bridal barge (bridal_barge.py's builders) at the greybox's size: its deck the Deck block
                  (4 x 10 m, level at y 0), its rail on the Rail blocks, Tobin's bier under the bridal cloth and the
                  canopy over it on the Bier block, the bow (-Z) to the dawn. The arena's barge (bridal_barge, 16 x 7.5)
                  is the Wakefin's battle floor and stays as it is. Its local X runs along the zone's Z: the dressing
                  sets it at yaw -90.
"""

from __future__ import annotations

import json
from pathlib import Path

import bridal_barge as bb
import kit_common as kc

ROOT = Path(__file__).resolve().parents[4]
LAYOUT = ROOT / "game" / "levels" / "ch15" / "open_sea" / "open_sea_layout.json"
TRI_BUDGET = {"open_sea_barge": (16000, 1200)}
RAIL_INSET = 0.08  # bridal_barge sets its rail this far in from the half-beam
CANOPY_PAD = 0.5  # the canopy's posts this far beyond the bier's ends


def blocks() -> dict:
    return {b["id"]: b for b in json.loads(LAYOUT.read_text(encoding="utf-8"))["blocks"]}


def fitted() -> dict:
    """The barge's dimensions from the greybox (in the barge's frame: X along the zone's Z, bow at -X)."""
    bl = blocks()
    d, rail, bier = bl["Deck"], bl["RailE"], bl["Bier"]
    half_len = d["size"][2] / 2
    half_beam = abs(rail["pos"][0]) + RAIL_INSET
    bx, bl_half = bier["pos"][2] - d["pos"][2], bier["size"][2] / 2
    return {"bow_x": -half_len, "stern_x": half_len, "half_beam_m": half_beam, "bier_at": (bx, 0.0),
            "canopy": ((bx - bl_half - CANOPY_PAD, half_beam - 0.5), (bx + bl_half + CANOPY_PAD, half_beam - 0.7))}


def build_barge(seed: int = 1870) -> list[kc.MeshBuilder]:
    return bb.build_fitted("open_sea_barge", seed, **fitted())


TARGETS = {"open_sea_barge": build_barge}
