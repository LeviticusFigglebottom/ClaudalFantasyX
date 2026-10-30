"""ADR 0202 (SPEC v1.6 §6.8): the statuses are named in our own words. No player-facing loc value may name a status
by its old name. Shell, Protect, Reflect and Doom are ordinary words in lower case ("a crab's shell"), so only their
capitalized forms count; Regen and Zombie count in any case; the four Breaks are on tools/banned_terms.txt too.
Proper nouns that only contain an old word are allowed (ALLOWED)."""
import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOC_DIR = ROOT / "game/data/loc"
# Old name -> its ADR 0202 replacement (for the failure message).
CAPITALIZED = {"Shell": "Tide Ward", "Protect": "Bulwark", "Reflect": "Mirrorwater", "Doom": "Last Tide"}
ANY_CASE = {"regen": "Mending", "zombie": "Hollowed", "armor break": "Sundered", "mental break": "Unmoored",
            "power break": "Weakened", "magic break": "Dimmed"}
# Proper nouns with an old word in them: places, skills and gear.
ALLOWED = ("Shell Shrine", "Shell Breaker", "Shell Ram", "Shell Wall", "Bell-Shell")


def old_names_in(text: str) -> list[str]:
    for noun in ALLOWED:
        text = text.replace(noun, "")
    found = [w for w in CAPITALIZED if re.search(r"\b" + w + r"\b", text)]
    found += [w for w in ANY_CASE if re.search(r"\b" + w + r"\b", text, re.IGNORECASE)]
    return found


class StatusNamesTest(unittest.TestCase):
    def test_no_loc_value_names_a_status_by_its_old_name(self) -> None:
        rows = 0
        for path in sorted(LOC_DIR.glob("*.csv")):
            with open(path, newline="", encoding="utf-8") as f:
                for row in csv.reader(f):
                    if len(row) < 2 or row[0] == "keys":
                        continue
                    rows += 1
                    for old in old_names_in(row[1]):
                        new = CAPITALIZED.get(old, ANY_CASE.get(old, ""))
                        self.fail(f"{path.name} {row[0]}: '{old}' is an old status name (ADR 0202: {new}): {row[1]}")
        self.assertGreater(rows, 1000, "the loc tables were read")

    def test_the_check_tells_a_status_from_a_word(self) -> None:
        self.assertEqual(old_names_in("Shell for the whole battle."), ["Shell"])
        self.assertEqual(old_names_in("{name} is a Zombie"), ["zombie"])
        self.assertEqual(old_names_in("Kerrid's Armor Break"), ["armor break"])
        self.assertEqual(old_names_in("A crab's shell. The Shell Shrine. Shell Breaker."), [])
        self.assertEqual(old_names_in("Every vista looks doomed; protect them."), [])


if __name__ == "__main__":
    unittest.main()
