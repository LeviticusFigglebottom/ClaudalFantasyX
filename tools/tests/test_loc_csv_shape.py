"""Every loc csv row has exactly the header's columns (keys, en). An unquoted comma in the text splits a row: Godot keeps
only the text before it, and the player reads half a sentence ("It is kept" for "It is kept, not used."). Run:
python3 -m unittest tools.tests.test_loc_csv_shape"""
import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class LocCsvShapeTest(unittest.TestCase):
    def test_every_row_has_the_headers_columns(self) -> None:
        bad = []
        for path in sorted((ROOT / "game/data/loc").glob("*.csv")):
            with path.open(encoding="utf-8", newline="") as f:
                rows = csv.reader(f)
                header = next(rows)
                for n, row in enumerate(rows, 2):
                    if len(row) != len(header):
                        bad.append(f"{path.relative_to(ROOT)}:{n} {row[0]} has {len(row)} columns, not {len(header)}")
        self.assertEqual(bad, [], "quote the text: a comma inside it splits the row")


if __name__ == "__main__":
    unittest.main()
