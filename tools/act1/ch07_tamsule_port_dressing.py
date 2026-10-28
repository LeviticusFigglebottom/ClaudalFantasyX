#!/usr/bin/env python3
"""Ch7 Tamsule's port (ch07/tamsule) dressed from env-art's kits where it stands (ADR 0041: no greybox on the played
path; env-art's own 'Tamsule stilt' kit, M3-C07-04, may replace these pieces).

The port keeps its greybox frame and collision (flat decks at y 0 joined by bridges, the river's floor 1 m down), and
every block gets kit dressing:
  - the decks and bridges: Haluna's timber decking on piles (the Bell kit's mooring posts), the river a WaterSurface
    (the scene's Water, the galleries' water) over a sand bed;
  - the floating market: Haluna's stalls with goods, Oruvel's boats moored along its edges;
  - the stilt lane: Haluna's stilt houses behind the lane's frontage and the Bell kit's gilded signboard;
  - the market boats: Oruvel's cookboats and outriggers at their deck; the harbour: Corrow's trader at her berth;
  - the Bell on its gantry beyond the north edge (the Bell kit as its preview places it, turned so no leg crosses the
    gantry foot), the Bell's moorings; the weeping column stays a block until rendering's effect (M3-RND-27);
  - the river's banks: rows of the Bell kit's shophouses on stilts, with box colliders.

    python3 tools/act1/ch07_tamsule_port_dressing.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZONE = ROOT / "game" / "levels" / "ch07" / "tamsule"
LAYOUT = ZONE / "tamsule_layout.json"
KIT = "res://assets/environments/kits/tamsule_bell/"
HALUNA = "res://assets/environments/kits/haluna/"
ORUVEL = "res://assets/environments/kits/oruvel/"
CORROW = "res://assets/environments/kits/corrow/"
RES_GALLERIES = "res://game/levels/ch07/tamsule_bell_galleries/"
DECKS = ("Quay", "QuayBridge", "Market", "LaneBridge", "StiltLane", "GantryBridge", "GantryFoot", "BoatBridge",
         "MarketBoats", "HarbourBridge", "Harbour")
DECK = ("timber_deck_2m", 2.09, 1.88)  # Haluna's decking: x, z (its top at the origin)
DECK_STAGGER_M = 0.004  # neighbouring tiles' tops differ by this, so their overlaps never z-fight
PILE = {"piece": "mooring_post", "top": 1.5, "above_deck_m": 0.25, "step_m": 4.0}
BELL_AT = (0.0, 0.0, -40.0)
BELL_TURN_DEG = 30.0  # the gantry's six legs at 30 + 60k deg: none crosses the gantry foot's deck
BANKS = {"south": (44.0, (-44.0, 56.0)), "west": (-58.0, (-44.0, 36.0)), "east": (66.0, (-44.0, 36.0))}
BANK_STEP_M = 11.5
STALL_GOODS = (("basket_set", 1.9, 0.6, 20.0), ("cargo_sacks", -1.9, 0.8, -15.0), ("crate_stack", 0.0, -1.6, 0.0))
MARKET_BOATS = (("outrigger_7m", HALUNA, -13.5, 9.5, 90.0), ("cookboat", ORUVEL, 13.6, 9.0, 0.0),
                ("hull_outrigger", ORUVEL, -6.0, 13.2, 10.0))
TAVI_BOATS = (("cookboat", ORUVEL, 20.8, -14.0, 0.0), ("hull_outrigger", ORUVEL, 20.6, -8.8, 5.0))
TRADER = {"scale": 0.75, "y": -0.9}


def r3(v: float) -> float:
    return round(v, 3)


def deck_tiles(b: dict) -> list[dict]:
    """Decking over a deck block's top, row by row, tiles staggered so their overlaps never z-fight."""
    (cx, cy, cz), (w, h, d) = b["pos"], b["size"]
    top = cy + h * 0.5
    nx, nz = max(1, math.ceil(w / (DECK[1] - 0.05))), max(1, math.ceil(d / (DECK[2] - 0.05)))
    s = max(w / nx / DECK[1], d / nz / DECK[2], 1.0)
    out = []
    for i in range(nx):
        for j in range(nz):
            x = cx - w * 0.5 + (i + 0.5) * w / nx
            z = cz - d * 0.5 + (j + 0.5) * d / nz
            out.append({"piece": DECK[0], "kit_dir": HALUNA, "at": [r3(x), r3(z)],
                        "y": r3(top + DECK_STAGGER_M * ((i + j) % 2)), "yaw_deg": 0.0, "scale": r3(s)})
    return out


def piles(b: dict) -> list[dict]:
    """The Bell kit's mooring posts round a deck's edge, every PILE step_m, standing just proud of the deck."""
    (cx, cy, cz), (w, h, d) = b["pos"], b["size"]
    top = cy + h * 0.5
    y = top + PILE["above_deck_m"] - PILE["top"]
    pts = []
    for zs in (-1.0, 1.0):
        n = max(1, round(w / PILE["step_m"]))
        pts += [(cx - w * 0.5 + k * w / n, cz + zs * d * 0.5) for k in range(n + 1)]
    for xs in (-1.0, 1.0):
        n = max(1, round(d / PILE["step_m"]))
        pts += [(cx + xs * w * 0.5, cz - d * 0.5 + k * d / n) for k in range(1, n)]
    return [{"piece": PILE["piece"], "at": [r3(x), r3(z)], "y": r3(y), "yaw_deg": 0.0} for x, z in pts]


def bell_set() -> list[dict]:
    """The Bell, its head, its six legs, its catch-pool and pennants as the kit's preview places them about the Bell's
    axis (tools/act1/ch07_tamsule_bell_dressing.py's zone), at BELL_AT and turned BELL_TURN_DEG."""
    x, y, z = BELL_AT
    rows = [("tamsule_bell", 0.0), ("gantry_head", 0.0), ("catch_pool", 0.0)]
    rows += [("gantry_leg", -60.0 * k) for k in range(6)]
    rows += [("pennant_line", a) for a in (-60.0, -120.0, -240.0, -300.0)]
    return [{"piece": p, "at": [x, z], "y": y, "yaw_deg": r3(a + BELL_TURN_DEG), "block": "Bell"} for p, a in rows]


def market(blocks: dict) -> list[dict]:
    out = []
    for sid in ("MarketStallA", "MarketStallB"):
        (sx, sy, sz), size = blocks[sid]["pos"], blocks[sid]["size"]
        base = sy - size[1] * 0.5
        out.append({"piece": "market_stall", "kit_dir": HALUNA, "at": [sx, sz], "y": base, "yaw_deg": 0.0,
                    "block": sid})
        for piece, dx, dz, yaw in STALL_GOODS:
            out.append({"piece": piece, "kit_dir": HALUNA, "at": [r3(sx + dx), r3(sz + dz)], "y": base,
                        "yaw_deg": yaw})
    (mx, _my, mz) = blocks["Market"]["pos"]
    for piece, kit, dx, dz, yaw in MARKET_BOATS:
        out.append({"piece": piece, "kit_dir": kit, "at": [r3(mx + dx), r3(mz + dz)], "y": -0.5, "yaw_deg": yaw})
    for piece, kit, x, z, yaw in TAVI_BOATS:
        out.append({"piece": piece, "kit_dir": kit, "at": [x, z], "y": -0.5, "yaw_deg": yaw})
    return out


def lane(blocks: dict) -> list[dict]:
    (hx, hy, hz), hs = blocks["StiltHouse"]["pos"], blocks["StiltHouse"]["size"]
    front = hz - hs[2] * 0.5
    out = [{"piece": "stilt_house", "kit_dir": HALUNA, "at": [r3(hx + dx), r3(front + 3.0 + 0.4)], "y": 0.0,
            "yaw_deg": 180.0, "block": "StiltHouse"} for dx in (-2.8, 3.6)]
    (gx, gy, gz), gs = blocks["Signboard"]["pos"], blocks["Signboard"]["size"]
    out.append({"piece": "signboard_gilded", "at": [gx, r3(gz - 0.3)], "y": 0.0, "yaw_deg": 0.0, "block": "Signboard"})
    return out


def harbour(blocks: dict) -> list[dict]:
    (tx, _ty, tz) = blocks["Trader"]["pos"]
    out = [{"piece": "trader_boat", "kit_dir": CORROW, "at": [r3(tx + 0.6), tz], "y": TRADER["y"], "yaw_deg": 0.0,
            "scale": TRADER["scale"], "block": "Trader"}]
    (bx, by, bz), bs = blocks["BellMoorings"]["pos"], blocks["BellMoorings"]["size"]
    out.append({"piece": "oruvel_moorings", "at": [bx, bz], "y": 0.0, "yaw_deg": 0.0, "scale": 0.5,
                "block": "BellMoorings"})
    return out


def banks() -> list[dict]:
    """Shophouses on stilts along the river's three far banks, facing the water, with box colliders (the river's floor
    reaches them)."""
    out = []
    k = 0
    for side, (line, (a, b)) in BANKS.items():
        n = int((b - a) // BANK_STEP_M) + 1
        for i in range(n):
            u = a + i * BANK_STEP_M
            x, z, yaw = (u, line, 180.0) if side == "south" else (line, u, 90.0 if side == "west" else 270.0)
            out.append({"piece": ("shophouse_a", "shophouse_b")[k % 2], "at": [r3(x), r3(z)], "y": 0.0,
                        "yaw_deg": yaw, "collide": True})
            k += 1
    return out


def dressing() -> dict:
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    blocks = {b["id"]: b for b in layout["blocks"]}
    pieces = []
    for did in DECKS:
        pieces += deck_tiles(blocks[did])
        if not did.endswith("Bridge"):
            pieces += piles(blocks[did])
    pieces += market(blocks) + lane(blocks) + harbour(blocks) + bell_set() + banks()
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act1/ch07_tamsule_port_dressing.py from env-art's Tamsule Bell, Haluna, Oruvel "
        "and Corrow kits on the port's own frame (ADR 0041); do not edit by hand.",
        "seed": 70,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "environment": RES_GALLERIES + "tamsule_noon_environment.tres",
        "time_of_day_h": 12.25,
        "greybox": {"hide_all": True, "keep": ["BellColumn"]},
        "pieces": pieces,
    }


def main() -> None:
    (ZONE / "tamsule_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
