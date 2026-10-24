"""Tests for the Undertow quality-tier check in tools/validate_data.py (M1-RND-11).
Run: python3 -m unittest discover -s tools/tests
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("validate_data", ROOT / "tools" / "validate_data.py")
vd = importlib.util.module_from_spec(spec)
sys.modules["validate_data"] = vd
spec.loader.exec_module(vd)

DOC = json.loads((ROOT / vd.UNDERTOW_FILE).read_text(encoding="utf-8"))


def errors(mutate) -> list[str]:
    doc = copy.deepcopy(DOC)
    mutate(doc)
    return vd.undertow_quality_errors(ROOT, doc)


class TestUndertowQuality(unittest.TestCase):
    def test_committed_data_is_valid(self) -> None:
        self.assertEqual(vd.undertow_quality_errors(ROOT, DOC), [])

    def test_step_cap_comes_from_the_variant_shader(self) -> None:
        self.assertTrue(any("UNDERTOW_MAX_STEPS" in e for e in errors(lambda d: d["quality"]["high"].update(march_steps=49))))
        self.assertTrue(any("march_steps" in e for e in errors(lambda d: d["quality"]["high"].update(march_steps=0))))
        self.assertTrue(any("shell body" in e for e in errors(lambda d: d["quality"]["low"].update(march_steps=8))))

    def test_curl_reuse_and_jitter_types(self) -> None:
        self.assertTrue(any("curl_reuse" in e for e in errors(lambda d: d["quality"]["high"].update(curl_reuse=20))))
        self.assertTrue(any("curl_reuse" in e for e in errors(lambda d: d["quality"]["high"].update(curl_reuse=1.5))))
        self.assertTrue(any("temporal_jitter" in e for e in errors(lambda d: d["quality"]["high"].update(temporal_jitter=1))))

    def test_tiers_bodies_and_noise(self) -> None:
        self.assertTrue(errors(lambda d: d["quality"].pop("ultra")))
        self.assertTrue(errors(lambda d: d["quality"]["medium"].update(body="volume")))
        self.assertTrue(any("noise.texture" in e for e in errors(lambda d: d["noise"].update(texture="res://nope.png"))))
        self.assertTrue(any("slice count" in e for e in errors(lambda d: d["noise"].update(texels=32))))

    def test_step_floor_and_default_cap_are_parsed_from_the_include(self) -> None:
        # M1-RND-15: the floor is the uniform's hint_range minimum (4), not 1; the default cap is the
        # include's #ifndef value, not a copy in the validator.
        inc = (ROOT / vd.UNDERTOW_BODY_INC).read_text(encoding="utf-8")
        uniforms = (ROOT / vd.UNDERTOW_BODY_UNIFORMS_INC).read_text(encoding="utf-8")
        floor, cap = vd.undertow_step_limits(ROOT)
        self.assertIn(f"march_steps : hint_range({floor},", uniforms)
        self.assertIn(f"#define UNDERTOW_MAX_STEPS {cap}", inc)
        self.assertFalse(hasattr(vd, "UNDERTOW_DEFAULT_STEP_CAP"), "no copied constant")
        self.assertTrue(any(f"outside {floor}.." in e for e in errors(lambda d: d["quality"]["high"].update(march_steps=floor - 1))))
        self.assertEqual(errors(lambda d: d["quality"]["high"].update(march_steps=floor)), [])

    def test_malformed_tiers_are_reported_not_raised(self) -> None:
        self.assertTrue(any("must be an object" in e for e in errors(lambda d: d["quality"].update(high=7))))
        self.assertTrue(any("must be objects" in e for e in errors(lambda d: d.update(quality=[]))))
        self.assertTrue(any("noise must be an object" in e for e in errors(lambda d: d.update(noise="x"))))

    def test_missing_file_is_an_error(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            rep = vd.Report()
            vd.check_undertow(Path(tmp), {}, rep)
            self.assertTrue(any("missing" in e for e in rep.errors))
            rep = vd.Report()
            vd.check_undertow(ROOT, {vd.UNDERTOW_FILE: DOC}, rep)
            self.assertEqual(rep.errors, [])


if __name__ == "__main__":
    unittest.main()
