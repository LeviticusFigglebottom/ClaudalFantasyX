"""Reefball data checks in tools/validate_data.py and the pure helpers of tools/balance/reefball_sim.py
(M3-RBL-01). Run: python3 -m unittest discover -s tools/tests"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "balance"))
import reefball_sim as rs  # noqa: E402
import validate_data as vd  # noqa: E402


def _shipped() -> list[dict]:
    return [json.loads((ROOT / p).read_text(encoding="utf-8"))
            for p in (vd.REEFBALL_RULES, vd.REEFBALL_SIDES, vd.REEFBALL_MATCHES)]


class ReefballValidateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rules, self.sides, self.matches = _shipped()

    def errs(self) -> list[str]:
        return vd.reefball_errors(self.rules, self.sides, self.matches)

    def test_shipped_data_passes(self) -> None:
        self.assertEqual(self.errs(), [])

    def test_shipped_keys_are_collected(self) -> None:
        files = {vd.REEFBALL_RULES: self.rules, vd.REEFBALL_SIDES: self.sides, vd.REEFBALL_MATCHES: self.matches}
        keys = vd.check_reefball(files, vd.Report())
        self.assertIn("RBL_ACTION_LOFT", keys)
        self.assertIn("CHAR_RHEN", keys)

    def test_missing_file(self) -> None:
        rep = vd.Report()
        self.assertEqual(vd.check_reefball({vd.REEFBALL_RULES: self.rules}, rep), [])
        self.assertEqual(len(rep.errors), 2)

    def test_actions_must_cost_a_stroke(self) -> None:
        self.rules["rules"]["actions"]["pass"]["strokes"] = 0
        self.assertTrue(any("actions.pass.strokes" in e for e in self.errs()))
        del self.rules["rules"]["actions"]["dive"]
        self.assertTrue(any("actions must be exactly" in e for e in self.errs()))

    def test_odds_and_ranges(self) -> None:
        r = self.rules["rules"]
        r["odds_max"] = 1.5
        r["fetch_depth"] = 9
        r["loft"]["max_depth"] = 0
        r["rise"]["edge_k"] = "big"
        r["breath"]["rested_pct"] = 120
        text = "\n".join(self.errs())
        for want in ("odds_min and odds_max", "fetch_depth", "loft.max_depth", "rise.edge_k", "rested_pct"):
            self.assertIn(want, text)

    def test_role_specs(self) -> None:
        role = self.rules["rules"]["roles"][0]
        role["attack"] = {"band": 1, "rel": 0}
        role["defend"] = {"band": 7}
        role["kickoff"]["attack"] = -1
        text = "\n".join(self.errs())
        self.assertIn(".attack: must be", text)
        self.assertIn(".defend.band", text)
        self.assertIn("kickoff.attack", text)

    def test_ai_profile_numbers(self) -> None:
        p = self.rules["rules"]["ai_profiles"][0]
        p["whim_pct"] = 150
        del p["score_value"]
        text = "\n".join(self.errs())
        self.assertIn("whim_pct must be in 0..100", text)
        self.assertIn("score_value must be a number", text)

    def test_sides(self) -> None:
        s = self.sides["sides"]
        s[0]["captain"] = "nobody"
        s[0]["divers"][0]["role"] = "keeper"
        s[0]["divers"][1]["stats"]["loft"] = 99
        del s[0]["divers"][2]["stats"]["ward"]
        s[1]["divers"][0]["id"] = s[0]["divers"][3]["id"]
        text = "\n".join(self.errs())
        for want in ("captain 'nobody'", "unknown role 'keeper'", "stat loft", "stats must be exactly",
                     "diver id used by another side"):
            self.assertIn(want, text)

    def test_matches(self) -> None:
        m = self.matches["matches"][0]
        m["sides"] = ["oruvel", "oruvel"]
        m["player_side"] = 2
        m["ai_profile"] = "nope"
        text = "\n".join(self.errs())
        for want in ("two different sides", "player_side", "unknown ai_profile"):
            self.assertIn(want, text)
        m["sides"] = ["oruvel", "nowhere"]
        self.assertTrue(any("unknown side 'nowhere'" in e for e in self.errs()))

    def test_stakes_key(self) -> None:
        # M3-RBL-201: optional, but a present stakes_key is a non-empty loc key, collected for the loc check.
        files = {vd.REEFBALL_RULES: self.rules, vd.REEFBALL_SIDES: self.sides, vd.REEFBALL_MATCHES: self.matches}
        self.assertIn("RBL_HUD_STAKES_TIDECUP_OPENING", vd.check_reefball(files, vd.Report()))
        m = self.matches["matches"][0]
        m["stakes_key"] = ""
        self.assertTrue(any("stakes_key" in e for e in self.errs()))
        del m["stakes_key"]
        self.assertEqual(self.errs(), [])

    def test_bad_top_level(self) -> None:
        self.assertTrue(vd.reefball_errors({}, {}, {}))
        self.rules["rules"]["bands"] = [{"id": "ring", "name_key": "K"}]
        self.assertTrue(any("bands must list" in e for e in self.errs()))


class ReefballSimHelpersTest(unittest.TestCase):
    SUITE = {"id": "s", "match": "m", "bands": {"naive": [10, 30], "smart": [55, 80], "other": None},
             "max_draw_pct": 15}

    def _r(self, policy: str, win: float, draw: float = 0.0, stalled: int = 0) -> dict:
        return {"policy": policy, "win_pct": win, "draw_pct": draw, "stalled": stalled, "mean_for": 1.0,
                "mean_against": 1.0, "mean_contacts": 30.0, "mean_turnovers": 9.0}

    def test_in_band(self) -> None:
        self.assertTrue(rs.in_band(self._r("naive", 20), self.SUITE))
        self.assertFalse(rs.in_band(self._r("naive", 31), self.SUITE))
        self.assertFalse(rs.in_band(self._r("smart", 70, draw=16), self.SUITE))
        self.assertTrue(rs.in_band(self._r("other", 99), self.SUITE))
        self.assertFalse(rs.in_band(self._r("other", 99, stalled=1), self.SUITE))

    def test_markdown_and_block(self) -> None:
        body = rs.markdown(self.SUITE, [self._r("naive", 20), self._r("smart", 90)], 100, "2026-10-24")
        self.assertIn("| naive | 10–30% | 20.0 |", body)
        self.assertIn("| NO |", body)
        doc = f"# T\n\n{rs.START}\nold\n{rs.END}\n\nafter\n"
        out = rs.replace_block(doc, body)
        self.assertNotIn("old", out)
        self.assertTrue(out.endswith("\n\nafter\n"))
        self.assertIn(rs.START, rs.replace_block("# T\n", "x"))

    def test_targets_file_is_well_formed(self) -> None:
        suites = rs.load_suites()
        self.assertTrue(suites)
        for s in suites:
            for band in s["bands"].values():
                self.assertTrue(band is None or (len(band) == 2 and band[0] <= band[1]))


if __name__ == "__main__":
    unittest.main()
