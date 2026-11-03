#!/usr/bin/env python3
"""The battle status icons (FAST-TRACK 11-03, the human's playtest: statuses must be obvious on the character).

One SVG per status in game/data/battle/statuses.json, written to assets/vfx/battle/status_icons/<id>.svg from the
vector glyphs below (no reference images, no generated art). BattleStatusLooks shows them over a fighter's head
while the status lasts; ui-menus uses the same set in the Read and status help (a request task).

Colour-blind safe by SHAPE first (docs/kb/tech/battle_status_looks.md):
  - the badge says the side: a beneficial status sits in a CIRCLE, a harmful one in a ROUNDED SQUARE;
  - the glyph says which status: 21 distinct silhouettes (a drop, a crescent, a cairn, an hourglass, a bell...);
  - a "break" (a stat lowered) adds a down-arrow tab to the glyph of the stat it breaks (shield, rings, blade, star),
    so Protect and Armor Break share a shield, Shell and Mental Break share the rings, one up and one down.
The glyph colour is the status's palette swatch (game/data/vfx/battle/status_looks.json), outlined in ui_panel_low.

    python3 tools/vfx/status_icons.py            # write the icons
    python3 tools/vfx/status_icons.py --check    # exit 1 if a committed icon differs from the generator
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUSES = ROOT / "game/data/battle/statuses.json"
LOOKS = ROOT / "game/data/vfx/battle/status_looks.json"
PALETTE = ROOT / "docs/kb/art/palette.json"
OUT = ROOT / "assets/vfx/battle/status_icons"

SIZE_PX = 128
OUTLINE = "ui_panel_low"
BADGE_FILL = "ui_panel_deep"
RIM = {"beneficial": "ui_focus", "harmful": "ui_danger"}
STROKE_W = 2.2


def _star(cx: float, cy: float, points: int, r_out: float, r_in: float, rot_deg: float = -90.0) -> str:
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot_deg + i * 180.0 / points)
        pts.append(f"{cx + r * math.cos(a):.2f},{cy + r * math.sin(a):.2f}")
    return "M" + " L".join(pts) + " Z"


def _spiral(cx: float, cy: float, turns: float, r_max: float) -> str:
    pts = []
    steps = int(turns * 32)
    for i in range(steps + 1):
        t = i / steps
        a = t * turns * 2 * math.pi
        r = 1.5 + t * (r_max - 1.5)
        pts.append(f"{cx + r * math.cos(a):.2f},{cy + r * math.sin(a):.2f}")
    return "M" + " L".join(pts)


SHIELD = "M32 13 L47 18 L46 33 C45 42 39 47 32 51 C25 47 19 42 18 33 L17 18 Z"
RINGS = [(32, 32, 16), (32, 32, 10.5), (32, 32, 5)]
BLADE = "M30 12 L34 12 L34 40 L30 40 Z M24 40 L40 40 L40 44 L24 44 Z M30.5 44 L33.5 44 L33.5 52 L30.5 52 Z"
STAR4 = _star(32, 31, 4, 18, 6)


def _glyph(sid: str) -> list[tuple[str, str, bool]]:
    """[(kind, data, filled)]: kind "path" (d) or "circle" ("cx cy r"); filled False draws a thick stroke."""
    g: dict[str, list[tuple[str, str, bool]]] = {
        "poison": [("path", "M32 11 C27 20 18 29 18 38 C18 46 24 52 32 52 C40 52 46 46 46 38 C46 29 37 20 32 11 Z", True)],
        "sleep": [("path", "M36 13 C24 13 15 22 15 33 C15 44 24 52 35 52 C42 52 47 49 50 44 C38 46 28 38 28 27 C28 21 31 16 36 13 Z", True)],
        "silence": [
            ("path", "M14 18 L50 18 L50 40 L30 40 L21 49 L22 40 L14 40 Z", True),
            ("path", "M12 52 L52 12", False),
        ],
        "darkness": [
            ("path", "M10 32 C18 20 46 20 54 32 C46 44 18 44 10 32 Z", True),
            ("circle", "32 32 6", True),
            ("path", "M14 52 L50 12", False),
        ],
        "petrify": [
            ("path", "M20 42 C20 38 26 37 32 37 C38 37 46 38 46 42 C46 47 40 50 32 50 C24 50 20 47 20 42 Z", True),
            ("path", "M23 30 C23 26 28 25 33 25 C38 25 42 26 42 30 C42 34 38 35 33 35 C28 35 23 34 23 30 Z", True),
            ("path", "M27 19 C27 16 30 14 33 14 C36 14 38 16 38 19 C38 22 36 23 33 23 C30 23 27 22 27 19 Z", True),
        ],
        "slow": [("path", "M19 12 L45 12 L45 15 L34 30 L34 34 L45 49 L45 52 L19 52 L19 49 L30 34 L30 30 L19 15 Z", True)],
        "haste": [
            ("path", "M12 16 L28 32 L12 48 L12 40 L20 32 L12 24 Z", True),
            ("path", "M30 16 L46 32 L30 48 L30 40 L38 32 L30 24 Z", True),
            ("path", "M46 22 L52 22 L52 42 L46 42 Z", True),
        ],
        "stop": [("path", "M18 14 L28 14 L28 50 L18 50 Z", True), ("path", "M36 14 L46 14 L46 50 L36 50 Z", True)],
        "berserk": [("path", _star(32, 32, 9, 21, 10), True)],
        "confuse": [("path", _spiral(32, 32, 2.6, 19), False)],
        "doom": [
            ("path", "M32 11 C24 11 20 18 20 27 L20 38 L14 45 L50 45 L44 38 L44 27 C44 18 40 11 32 11 Z", True),
            ("circle", "32 50 4", True),
        ],
        "zombie": [
            ("path", "M32 50 L13 31 C8 25 11 15 19 14 C25 13 29 17 32 21 C35 17 39 13 45 14 C53 15 56 25 51 31 Z", True),
            ("path", "M32 21 L28 29 L35 34 L29 42", False),
        ],
        "shell": [("circle", f"{x} {y} {r}", False) for x, y, r in RINGS],
        "protect": [("path", SHIELD, True)],
        "reflect": [
            ("path", "M40 10 L46 10 L46 54 L40 54 Z", True),
            ("path", "M10 18 L37 32 L10 46", False),
        ],
        "regen": [("path", "M27 12 L37 12 L37 27 L52 27 L52 37 L37 37 L37 52 L27 52 L27 37 L12 37 L12 27 L27 27 Z", True)],
        "armor_break": [("path", SHIELD, True), ("path", "M33 16 L28 27 L36 33 L30 47", False)],
        "mental_break": [("circle", f"{x} {y} {r}", False) for x, y, r in RINGS] + [("path", "M33 14 L28 26 L36 33 L30 48", False)],
        "power_break": [("path", BLADE, True), ("path", "M27 22 L37 28 L27 34", False)],
        "magic_break": [("path", STAR4, True), ("path", "M33 16 L29 27 L36 33 L31 45", False)],
        "provoke": [
            ("circle", "32 32 15", False),
            ("circle", "32 32 4", True),
            ("path", "M32 9 L32 21 M32 43 L32 55 M9 32 L21 32 M43 32 L55 32", False),
        ],
    }
    return g[sid]


BREAKS = {"armor_break", "mental_break", "power_break", "magic_break"}
CRACKS = {"armor_break", "mental_break", "magic_break", "zombie"}


def _hex(palette: dict, swatch: str) -> str:
    return str(palette["swatches"][swatch]["hex"]).upper()


def svg_for(sid: str, category: str, swatch: str, palette: dict) -> str:
    color = _hex(palette, swatch)
    outline = _hex(palette, OUTLINE)
    rim = _hex(palette, RIM[category])
    fill = _hex(palette, BADGE_FILL)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE_PX}" height="{SIZE_PX}" viewBox="0 0 64 64">',
        f"<!-- {sid}: generated by tools/vfx/status_icons.py; do not edit -->",
    ]
    if category == "beneficial":
        out.append(f'<circle cx="32" cy="32" r="29" fill="{fill}" fill-opacity="0.9" stroke="{rim}" stroke-width="3"/>')
    else:
        out.append(
            f'<rect x="3.5" y="3.5" width="57" height="57" rx="9" fill="{fill}" fill-opacity="0.9" '
            f'stroke="{rim}" stroke-width="3"/>'
        )
    for kind, data, filled in _glyph(sid):
        crack = not filled and (sid in CRACKS and kind == "path")
        stroke_col = outline if crack else color
        if kind == "circle":
            cx, cy, r = data.split()
            shape = f'<circle cx="{cx}" cy="{cy}" r="{r}"'
        else:
            shape = f'<path d="{data}"'
        if filled:
            out.append(f'{shape} fill="{color}" stroke="{outline}" stroke-width="{STROKE_W}" stroke-linejoin="round"/>')
        else:
            # A stroked glyph: a dark under-stroke, then the colour (reads on any backdrop).
            w = 5.0 if not crack else 3.0
            if not crack:
                out.append(
                    f'{shape} fill="none" stroke="{outline}" stroke-width="{w + 2.4}" stroke-linecap="round" '
                    'stroke-linejoin="round"/>'
                )
            out.append(
                f'{shape} fill="none" stroke="{stroke_col}" stroke-width="{w}" stroke-linecap="round" '
                'stroke-linejoin="round"/>'
            )
    if sid in BREAKS:
        # The "lowered" tab: a down arrow in the bottom-right corner, white on the rim colour.
        out.append(f'<circle cx="50" cy="50" r="10" fill="{rim}" stroke="{outline}" stroke-width="{STROKE_W}"/>')
        out.append(
            f'<path d="M46 44 L54 44 L54 48 L57 48 L50 56 L43 48 L46 48 Z" fill="{_hex(palette, "ui_line_white")}" '
            f'stroke="{outline}" stroke-width="1.2" stroke-linejoin="round"/>'
        )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def build() -> dict[str, str]:
    statuses = json.loads(STATUSES.read_text())["statuses"]
    looks = json.loads(LOOKS.read_text())["looks"]
    palette = json.loads(PALETTE.read_text())
    files: dict[str, str] = {}
    for row in statuses:
        sid = row["id"]
        files[f"{sid}.svg"] = svg_for(sid, row["category"], looks[sid]["icon_swatch"], palette)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    files = build()
    if args.check:
        bad = [n for n, t in files.items() if not (OUT / n).exists() or (OUT / n).read_text() != t]
        for n in bad:
            print(f"status_icons: {n} differs from the generator", file=sys.stderr)
        return 1 if bad else 0
    OUT.mkdir(parents=True, exist_ok=True)
    for n, t in files.items():
        (OUT / n).write_text(t)
    print(f"status_icons: wrote {len(files)} icons to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
