"""M2-UI-15: player-facing text goes through loc keys.

Scans every GDScript under game/ for string literals that reach the screen: an assignment to
`.text`, the help, hint, header, note or banner setters, `tr(...)`, `pop_info(...)` and the
`"label"` and `"right"` row fields. A literal there must be a loc key (UPPER_SNAKE), an id or
format (lowercase, digits and punctuation only), or be on ALLOW. StringName (&"...") and NodePath
(^"...") literals are never text. Anything else fails, naming the file and line, so a hard-coded
English string cannot slip into the UI.
"""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SINK = re.compile(
    r'(\.text\s*=|\.tooltip_text\s*=|set_help\(|set_hint\(|set_header\(|set_note\(|show_banner\('
    r'|pop_info\(|\btr\(|"label"\s*:|"right"\s*:)'
)
KEY = re.compile(r"^[A-Z][A-Z0-9_]*$")
ID_OR_FORMAT = re.compile(r"^[a-z0-9_./#%:{}()\[\] ,+×·-]*$")
# path:line -> why it is allowed (keep it short and rare).
ALLOW: dict[str, str] = {}


def literals(code: str) -> list[tuple[int, str, str]]:
    """(start, prefix, text) for each "..." literal in a line of code; prefix is & ^ or ''."""
    out = []
    i = 0
    while i < len(code):
        c = code[i]
        if c == "#":
            break
        if c == '"':
            prefix = code[i - 1] if i > 0 and code[i - 1] in "&^" else ""
            j = i + 1
            buf = []
            while j < len(code) and code[j] != '"':
                if code[j] == "\\" and j + 1 < len(code):
                    buf.append(code[j : j + 2])
                    j += 2
                    continue
                buf.append(code[j])
                j += 1
            out.append((i, prefix, "".join(buf)))
            i = j + 1
            continue
        i += 1
    return out


def offenders(root: Path = ROOT) -> list[str]:
    found = []
    for path in sorted((root / "game").rglob("*.gd")):
        rel = path.relative_to(root).as_posix()
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            sink = SINK.search(line)
            if not sink:
                continue
            for start, prefix, text in literals(line):
                if start < sink.start() or prefix:
                    continue
                after = line[start + len(text) + 2 :].lstrip()
                if after.startswith((":", "]")):
                    continue  # a dictionary key or an index
                if KEY.match(text) or ID_OR_FORMAT.match(text) or not re.search(r"[A-Za-z]{2,}", text):
                    continue
                where = f"{rel}:{n}"
                if where not in ALLOW:
                    found.append(f"{where}: {text!r}")
    return found


class LocLiteralTest(unittest.TestCase):
    def test_no_player_facing_literal_bypasses_the_loc_keys(self) -> None:
        bad = offenders()
        self.assertEqual(bad, [], "hard-coded player-facing strings (use a loc key):\n" + "\n".join(bad))

    def test_the_scanner_catches_a_literal_and_skips_keys_ids_and_string_names(self) -> None:
        self.assertEqual([t for _, _, t in literals('x.text = "Hello there"')], ["Hello there"])
        self.assertEqual([p for _, p, _ in literals('a(&"id", ^"Path", "X")')], ["&", "^", ""])
        self.assertEqual([t for _, _, t in literals('tr(k) if k != &"" else ""')], ["", ""])
        self.assertTrue(KEY.match("HUD_HELP_FMT"))
        self.assertTrue(ID_OR_FORMAT.match("%d/%d"))
        self.assertFalse(ID_OR_FORMAT.match("Not enough lume"))

    def test_a_hard_coded_label_is_reported_with_its_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp) / "game"
            game.mkdir()
            (game / "menu.gd").write_text(
                'func _ready() -> void:\n\t_title.text = tr("MENU_TITLE")\n\t_help.text = "Press A to go"\n'
                '\trows.append({"id": &"x", "label": "Bestiary"})\n',
                encoding="utf-8",
            )
            self.assertEqual(
                offenders(Path(tmp)), ["game/menu.gd:3: 'Press A to go'", "game/menu.gd:4: 'Bestiary'"]
            )


if __name__ == "__main__":
    unittest.main()
