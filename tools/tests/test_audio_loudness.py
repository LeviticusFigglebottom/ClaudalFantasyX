"""Every shipped audio file meets its loudness and size target (M2-AUD-06; tools/audio/targets.py, mix.md §2, §5).
Decodes each .ogg under assets/audio/ with ffmpeg and measures it with the repo's BS.1770 meter.
Run: python3 -m unittest discover -s tools/tests"""
import shutil
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))
import targets  # noqa: E402
from synth.loudness import integrated_lufs, momentary_max_lufs, true_peak_dbtp  # noqa: E402
from synth.mixer import read_audio  # noqa: E402

AUDIO = ROOT / "assets" / "audio"


@unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg to decode")
class AudioLoudnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.files = sorted(AUDIO.rglob("*.ogg"))
        cls.decoded = {}

    def _decode(self, p: Path) -> np.ndarray:
        """The decoded file; a mono file (both channels equal) as mono, so it measures as its own target says."""
        if p not in self.decoded:
            # ffmpeg upmixes mono at -3 dB per channel, so a mono file is decoded again as mono.
            y = read_audio(str(p), channels=2)
            self.decoded[p] = read_audio(str(p), channels=1) if np.array_equal(y[:, 0], y[:, 1]) else y
        return self.decoded[p]

    def test_every_file_has_a_target(self) -> None:
        missing = [str(p.relative_to(AUDIO)) for p in self.files if targets.rule_for(str(p.relative_to(AUDIO))) is None]
        self.assertEqual(missing, [], "add a rule to tools/audio/targets.py")

    def test_sizes(self) -> None:
        total = 0
        for p in self.files + sorted(AUDIO.rglob("*.json")):
            size = p.stat().st_size
            total += size
            self.assertLessEqual(size, targets.FILE_LIMIT, f"{p} is over 5 MB")
        self.assertLessEqual(total, targets.TOTAL_BUDGET, f"all audio {total / 1048576:.2f} MiB is over budget")

    def test_loudness_and_peaks(self) -> None:
        bad = []
        stems: dict[str, list] = {}     # one stack per "stem" rule (one boss cue each), in file order: p1, p2, ...
        for p in self.files:
            rel = str(p.relative_to(AUDIO))
            rule = targets.rule_for(rel)
            if rule is None:
                continue
            _, metric, target, tol, ceiling, _ = rule
            y = self._decode(p)
            tp = true_peak_dbtp(y)
            if tp > ceiling + 0.05:
                bad.append(f"{rel}: true peak {tp:.2f} dBTP over {ceiling}")
            if metric == "stem":
                stems.setdefault(rule[0], []).append(y)
                continue
            lv = integrated_lufs(y) if metric == "integrated" else momentary_max_lufs(y)
            if abs(lv - target) > tol:
                bad.append(f"{rel}: {metric} {lv:.2f} LUFS, target {target} +- {tol}")
        for glob, group in stems.items():
            _, _, target, tol, ceiling, _ = targets.rule_for(glob.replace("*", "1"))
            n = min(len(s) for s in group)
            stack = sum(s[:n] for s in group)
            full = integrated_lufs(stack)
            if abs(full - target) > tol:
                bad.append(f"{glob} together: {full:.2f} LUFS, target {target} +- {tol}")
            tp = true_peak_dbtp(stack)
            if tp > ceiling + 0.05:
                bad.append(f"{glob} together: true peak {tp:.2f} dBTP over {ceiling}")
            if integrated_lufs(group[0]) > full:
                bad.append(f"{glob}: stem 1 alone is louder than the stack")
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
