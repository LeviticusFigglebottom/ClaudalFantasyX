"""Cutscene timing against audio's cues (the Lead's timing pass, 2026-10-28).

The first verse's sung lines land on hush_first_verse's phrases. Each line is
#timed (the sequencer shows it and goes on), so its moment is the sum of the script's waits after the `@music` cue.
This checks those moments against the phrase starts audio's own source computes (verse_notes), so a re-render that
moves the song, or a script edit that moves a wait, fails here instead of drifting out of sync."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPILED = ROOT / "game" / "data" / "dialogue" / "compiled" / "ch03_the_first_verse.json"
CUE = "hush_first_verse"
TOLERANCE_S = 0.05


def _ops(node) -> list:
    """Every op of the compiled scene, in file order."""
    out = []
    if isinstance(node, dict):
        if "op" in node:
            out.append(node)
        for v in node.values():
            out += _ops(v)
    elif isinstance(node, list):
        for v in node:
            out += _ops(v)
    return out


def _phrase_starts() -> list[float]:
    sys.path.insert(0, str(ROOT / "assets_src" / "music"))
    import hush_first_verse as verse  # noqa: E402 (audio's source; builds nothing on import)

    notes, _mir = verse.verse_notes()
    starts, k = [], 0
    for line in verse.VERSE:
        starts.append(notes[k][0])
        k += len(line)
    return starts


class FirstVerseSyncTest(unittest.TestCase):
    def test_each_sung_line_shows_on_its_phrase(self):
        ops = _ops(json.loads(COMPILED.read_text(encoding="utf-8")))
        t, started, shown = 0.0, False, []
        for op in ops:
            if op.get("op") == "cue" and op.get("cue") == "music" and op.get("args") == [CUE]:
                started = True
                continue
            if not started:
                continue
            if op.get("op") == "cue" and op.get("cue") == "wait":
                t += float(op["args"][0])
            elif op.get("op") == "line":
                if "timed" not in op.get("tags", []):
                    break
                shown.append((op["id"], t))
        starts = _phrase_starts()
        self.assertEqual(len(shown), len(starts), f"one timed line per phrase: {shown}")
        for (line_id, at), want in zip(shown, starts):
            msg = f"{line_id} shows at {at:.2f} s, its phrase {want:.2f} s"
            self.assertAlmostEqual(at, want, delta=TOLERANCE_S, msg=msg)


class CurrentShaftCrossfadeTest(unittest.TestCase):
    """Ch1 C1-06: the script crossfades rhen_current_hum to oruvel_raft in the breath after the hum's first pass, as
    audio wrote it (rhen_current_hum.py: the second pass sinks under the town's music), never across the first."""

    def test_the_crossfade_starts_in_the_breath(self):
        sys.path.insert(0, str(ROOT / "tools" / "audio"))
        sys.path.insert(0, str(ROOT / "assets_src" / "music"))
        import rhen_current_hum as hum  # noqa: E402

        first = hum.phrase_notes(hum.T0, 1.0)
        breath_from = first[-1][0] + first[-1][1]
        breath_to = breath_from + hum.GAP_S
        compiled = ROOT / "game" / "data" / "dialogue" / "compiled" / "ch01_current_shaft.json"
        t, started, at = 0.0, False, None
        for op in _ops(json.loads(compiled.read_text(encoding="utf-8"))):
            if op.get("op") != "cue":
                continue
            if op.get("cue") == "music" and op.get("args") == ["rhen_current_hum"]:
                started = True
            elif started and op.get("cue") == "wait":
                t += float(op["args"][0])
            elif started and op.get("cue") == "music":
                at = t
                break
        self.assertIsNotNone(at, "the scene crossfades to the town's music")
        msg = f"crossfade at {at:.2f} s, breath {breath_from:.2f}-{breath_to:.2f} s"
        self.assertTrue(breath_from <= at <= breath_to, msg)


if __name__ == "__main__":
    unittest.main()
