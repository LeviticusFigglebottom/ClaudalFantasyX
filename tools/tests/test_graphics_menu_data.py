"""M1-UI-10: every value the Graphics page can show has a loc row (validate_data does not scan
game/data/settings/ or the menu's value_keys table)."""
import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRESETS = ROOT / "game/data/settings/graphics_presets.json"
MENU = ROOT / "game/data/ui/graphics_menu.json"
STRINGS = ROOT / "game/data/loc/strings.csv"


def _loc_keys() -> set[str]:
    with STRINGS.open(encoding="utf-8") as f:
        return {row[0] for row in csv.reader(f) if row}


class GraphicsMenuDataTest(unittest.TestCase):
    def setUp(self) -> None:
        self.presets = json.loads(PRESETS.read_text(encoding="utf-8"))
        self.menu = json.loads(MENU.read_text(encoding="utf-8"))["graphics_menu"]
        self.loc = _loc_keys()

    def test_every_string_option_has_a_value_key(self) -> None:
        value_keys = self.menu["value_keys"]
        for key, row in self.presets["settings"].items():
            for option in row["options"]:
                if isinstance(option, str):
                    self.assertIn(option, value_keys, f"{key}: option '{option}' has no value_keys row")

    def test_every_key_the_page_shows_is_translated(self) -> None:
        keys = list(self.menu["value_keys"].values())
        keys += [self.menu["on_key"], self.menu["off_key"], self.menu["custom_key"]]
        keys += [row["label_key"] for row in self.presets["settings"].values()]
        keys += [p["name_key"] for p in self.presets["presets"]]
        keys += ["GFX_MENU_TITLE", "GFX_MENU_PRESET", "GFX_MENU_HELP_PRESET", "GFX_MENU_HELP_SETTING"]
        self.assertEqual([k for k in keys if k not in self.loc], [])

    def test_formatted_settings_exist(self) -> None:
        for key in self.menu["percent_settings"] + self.menu["multiplier_settings"]:
            self.assertIn(key, self.presets["settings"])


if __name__ == "__main__":
    unittest.main()
