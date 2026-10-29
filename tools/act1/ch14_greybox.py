#!/usr/bin/env python3
"""Ch14 "The Peace Wedding" greybox (M4-C14-02): ch13/ansedra_lacquer_court, before the beat sheet (M4-C14-01). From
act_outline.md (Ch14) and the colour script's `ch14` (dusk 18:30, overcast breaking to a thin red band, red lacquer and
still water, the highest contrast of Act II).

  ch13/ansedra_lacquer_court  the wedding court on the still water: the court's stone floor under a red-lacquered
                              colonnade, the wedding dais at the north (`vows`: Sefir officiates), the guests' galleries
                              east and west, the Conclave's gallery north-west (where the trap is sprung), the water-steps
                              down at the south (a ramp: `kerrid_steps`, he holds them and is the last aboard) to the
                              bridal barge's mooring (`barge_deck`), and the court's water-gate across the canal beyond
                              (`merel_gate`: she drops it behind them and stays). The escape goes out across the water.

x is east, north is -Z. Shares Ch10's and Ch11's builders.

    python3 tools/act1/ch14_greybox.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch10_greybox import box, water  # noqa: E402
from ch11_greybox import floor, walls  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ZONE = ROOT / "game" / "levels" / "ch13" / "ansedra_lacquer_court"
COL_STONE = "#bab4a8"
COL_LACQUER = "#9a2a20"
COL_GOLD = "#b8a070"
COL_LAGOON = "#2e3448"
COL_BARGE = "#b03a2a"
SUN = {"pitch_deg": -4.0, "yaw_deg": -90.0, "energy": 1.2, "color": "#ffb48a"}  # 1 deg up in the west, a red band
ENV = {"background": "#b85a3a", "ambient_color": "#2e3448", "ambient_energy": 0.5}
COURT = (0.0, -12.0, 15.0, 12.0)  # centre x, z, half sizes; floor y 0
DECK_Y = -0.6  # the barge's deck, at the foot of the water-steps


def lacquer_court() -> dict:
    cx, cz, hx, hz = COURT
    blocks = water(-60.0, 60.0, -60.0, 40.0, color=COL_LAGOON)
    blocks.append(floor("Court", cx, cz, hx, hz, 0.0, COL_STONE))
    blocks += walls("Court", cx, cz, hx, hz, 0.0, 1.0, {"s": (-3.2, 3.2), "e": (8.0, 11.0)})
    for k in range(7):  # the red-lacquered colonnade round three sides
        x = cx - hx + 1.0 + k * (2 * hx - 2.0) / 6
        blocks.append(box(f"ColumnN{k}", x, 3.0, cz - hz + 1.0, 0.6, 6.0, 0.6, color=COL_LACQUER, solid=False))
    for side in (-1.0, 1.0):
        for k in range(5):
            z = cz - hz + 3.0 + k * (2 * hz - 6.0) / 4
            blocks.append(box(f"Column{'WE'[side > 0]}{k}", cx + side * (hx - 1.0), 3.0, z, 0.6, 6.0, 0.6,
                              color=COL_LACQUER, solid=False))
        blocks.append(box(f"Gallery{'WE'[side > 0]}", cx + side * (hx - 3.0), 0.3, cz, 3.0, 0.6, 2 * hz - 8.0,
                          color=COL_LACQUER))
    blocks.append(box("Dais", cx, 0.4, cz - hz + 3.0, 8.0, 0.8, 3.0, color=COL_GOLD))
    blocks.append(box("ConclaveGallery", cx - hx + 3.0, 1.0, cz - hz + 2.5, 5.0, 2.0, 3.0, color=COL_LACQUER))
    ramps = [{"id": "WaterSteps", "from": [cx, 0.0, cz + hz], "to": [cx, DECK_Y, cz + hz + 4.0], "width": 6.0,
              "color": COL_STONE}]
    for side in (-1.0, 1.0):
        blocks.append(box(f"WaterStepsWall{'WE'[side > 0]}", cx + side * 3.25, 0.5, cz + hz + 2.0, 0.5, 2.0, 4.0,
                          color=COL_STONE))
    blocks.append(box("Barge", cx, DECK_Y - 0.25, cz + hz + 9.0, 4.0, 0.5, 10.0, color=COL_BARGE))
    for side in (-1.0, 1.0):
        blocks.append(box(f"BargeRail{'WE'[side > 0]}", cx + side * 2.1, DECK_Y + 0.3, cz + hz + 9.0, 0.2, 0.6, 10.0,
                          color=COL_GOLD))
    blocks.append(box("BargeStern", cx, DECK_Y + 0.3, cz + hz + 14.1, 4.2, 0.6, 0.2, color=COL_GOLD))
    blocks.append(box("WaterGate", cx, 2.0, cz + hz + 18.0, 10.0, 5.0, 0.8, color=COL_LACQUER, solid=False))
    blocks.append(box("EntryStep", cx + hx + 1.5, -0.25, cz + 9.5, 3.0, 0.5, 3.0, color=COL_STONE))
    blocks.append(box("EntryBound", cx + hx + 3.25, 1.0, cz + 9.5, 0.5, 2.0, 3.0, color=COL_STONE))
    return {
        "doc": "M4-C14-02 greybox (tools/act1/ch14_greybox.py; do not edit by hand): the Lacquer Court at dusk "
        "(colour script ch14). The court's floor under a red-lacquered colonnade, the wedding dais (vows: Sefir "
        "officiates), the guests' galleries, the Conclave's gallery (north-west), the water-steps down (a ramp; "
        "kerrid_steps: he holds them) to the bridal barge (barge_deck; the barge trigger runs the escape out across the "
        "water) and the water-gate beyond (merel_gate). Entered from the city at the east (CourtEntry). The story waits "
        "on the beat sheet (M4-C14-01).",
        "sun": SUN,
        "environment": ENV,
        "block_color": COL_STONE,
        "blocks": blocks,
        "ramps": ramps,
        "spawns": {"CourtEntry": [cx + hx - 2.0, 0.0, cz + 9.5, 90.0], "Barge": [cx, DECK_Y, cz + hz + 7.0, 180.0]},
        "marks": {"vows": [cx, 0.0, cz - hz + 5.5, 0.0], "tobin_falls": [cx + 1.5, 0.0, cz - hz + 6.0, 0.0],
                  "kerrid_steps": [cx, 0.0, cz + hz - 0.8, 0.0], "barge_deck": [cx, DECK_Y, cz + hz + 10.0, 180.0],
                  "merel_gate": [cx + 4.0, DECK_Y, cz + hz + 14.6, 180.0]},
        "actors": {},
        "shots": {"W01": {"pos": [cx, 2.4, cz + hz - 2.0], "look_at": [cx, 1.4, cz - hz + 3.0], "fov": 45}},
        "triggers": [{"id": "barge", "activation": "touch", "at": [cx, DECK_Y, cz + hz + 12.0], "size": [3.0, 0, 3.0],
                      "payload": {"beat": "escape"}, "yaw": 0.0}],
    }


def main() -> None:
    out = ZONE / "ansedra_lacquer_court_layout.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(lacquer_court(), indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
