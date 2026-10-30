"""env-art-b's battle arenas (M3-ENV-1303..1314) are reproducible from their writers. Each wrapper writes env-art's
arena table (`assets_src/environments/kits/haluna/arena_scenes.py`, read-only) through the same `write_arena`, with
its own additions (Lanternfall's votives and terrace, the camp's fires, the Ch6 arenas' smoke columns, the wall-head's Undertow, the headland's
scrub, the Ch14–15 arenas' zone looks), or writes its own table (the Ashcrown arenas, the Lacquer Court's steps). test_arenas.py skips the ids in WRAPPERS; this test reproduces
them instead."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KITS = ROOT / "assets_src" / "environments" / "kits"
WRAPPERS = {
    "pemakar/b_lanternfall.py": ("ash_terrace_lanternfall",),
    "brine_shoals/b_camp_arena.py": ("salvage_camp_burning",),
    "brine_shoals/b_shoals_arena.py": ("brine_shoals_afternoon",),
    "corrow/b_seawall_storm.py": ("seawall_stairhead_storm", "seawall_stairhead_hoist", "seawall_stairhead_surge"),
    "coilspire/b_headland_arena.py": ("coilspire_headland_path", "coilspire_tier_landing"),
    "ashcrown/b_arenas.py": ("ashcrown_forecourt_day", "ashcrown_anvil_court"),
    "haluna/ansedra_arenas.py": ("lacquer_court_steps", "ansedra_lagoon_escape", "bridal_barge_night"),
}
WRAPPED = {aid for ids in WRAPPERS.values() for aid in ids}


def _load(rel: str):
    path = KITS / rel
    spec = importlib.util.spec_from_file_location("b_arena_" + path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class WrappedArenaTests(unittest.TestCase):
    def test_wrapped_arenas_are_reproducible(self) -> None:
        for rel, ids in WRAPPERS.items():
            with tempfile.TemporaryDirectory() as tmp:
                _load(rel).main(out_dir=Path(tmp))
                for aid in ids:
                    with self.subTest(arena=aid):
                        committed = ROOT / "assets" / "environments" / "arenas" / aid / f"{aid}.tscn"
                        out = Path(tmp) / aid / f"{aid}.tscn"
                        self.assertEqual(committed.read_text(encoding="utf-8"), out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
