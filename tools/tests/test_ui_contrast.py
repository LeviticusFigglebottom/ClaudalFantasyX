"""The UI text colours against the panels they sit on (the Lead's as-played Act I UI pass, 2026-10-30).

Every text role in game/data/ui/theme.json (resolved through docs/kb/art/palette.json, alpha composited) is checked
with the WCAG 2 contrast ratio, in the standard palette and the colorblind one (game/data/ui/accessibility.json):
  - body text on the page panels (panel_deep and panel_low over the night backdrop): at least 4.5 (AA);
  - a menu row's bold labels on the raised cursor fill (panel_raised over panel_deep): at least 3.0 (AA large text:
    RankLabel and MenuLabel are bold 24 px and over, past the 18.66 px bold line).
text_disabled is exempt (WCAG excludes inactive controls); it must still read as dimmer than text_dim.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THEME = ROOT / "game/data/ui/theme.json"
PALETTE = ROOT / "docs/kb/art/palette.json"
ACCESSIBILITY = ROOT / "game/data/ui/accessibility.json"
BODY_ROLES = ["text", "text_dim", "focus_gold", "danger", "hp", "mp", "swell", "heal"]
BODY_MIN = 4.5
LARGE_MIN = 3.0


def _hex(h: str) -> list[float]:
    return [int(h[i : i + 2], 16) / 255.0 for i in (1, 3, 5)]


def _swatches() -> dict[str, str]:
    doc = json.loads(PALETTE.read_text())
    out: dict[str, str] = {}

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, dict) and isinstance(v.get("hex"), str):
                    out[k] = v["hex"]
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(doc)
    return out


def _colors(palette: str) -> dict[str, list[float]]:
    roles = dict(json.loads(THEME.read_text())["theme"]["colors"])
    roles.update(json.loads(ACCESSIBILITY.read_text())["accessibility"]["palettes"][palette])
    sw = _swatches()
    out = {}
    for role, (src, alpha) in roles.items():
        rgb = _hex(src) if str(src).startswith("#") else _hex(sw[src])
        out[role] = rgb + [float(alpha)]
    return out


def _over(fg: list[float], bg: list[float]) -> list[float]:
    a = fg[3]
    return [fg[i] * a + bg[i] * (1.0 - a) for i in range(3)] + [1.0]


def _lum(c: list[float]) -> float:
    lin = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c[:3]]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(fg: list[float], bg: list[float]) -> float:
    a, b = _lum(_over(fg, bg)), _lum(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


class UiContrastTest(unittest.TestCase):
    def _backgrounds(self, c: dict[str, list[float]]) -> dict[str, list[float]]:
        night = _over(c["outline"], [0.0, 0.0, 0.0, 1.0])
        deep = _over(c["panel_deep"], night)
        return {"panel_deep": deep, "panel_low": _over(c["panel_low"], night), "raised": _over(c["panel_raised"], deep)}

    def test_text_roles_meet_aa_on_the_panels_in_both_palettes(self) -> None:
        sections = json.loads(ACCESSIBILITY.read_text())["accessibility"]["palettes"]
        for palette in sections:
            c = _colors(palette)
            bg = self._backgrounds(c)
            for role in BODY_ROLES:
                for name in ("panel_deep", "panel_low"):
                    r = ratio(c[role], bg[name])
                    self.assertGreaterEqual(r, BODY_MIN, f"{palette}: {role} on {name} is {r:.2f}")
                r = ratio(c[role], bg["raised"])
                self.assertGreaterEqual(r, LARGE_MIN, f"{palette}: {role} on the cursor row is {r:.2f}")

    def test_disabled_text_reads_dimmer_than_dim_text(self) -> None:
        c = _colors("standard")
        deep = self._backgrounds(c)["panel_deep"]
        self.assertLess(ratio(c["text_disabled"], deep), ratio(c["text_dim"], deep))


if __name__ == "__main__":
    unittest.main()
