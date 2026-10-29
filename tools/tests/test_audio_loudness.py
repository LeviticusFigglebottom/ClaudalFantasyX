"""Every shipped audio file meets its loudness and size target (M2-AUD-06; tools/audio/targets.py, mix.md §2, §5).
Decodes each .ogg under assets/audio/ with ffmpeg and measures it with the repo's BS.1770 meter.
Run: python3 -m unittest discover -s tools/tests

Speed (M2-NIT-06). Nearly all the time is true_peak_dbtp's FFTs on the long music files, whose sample counts
are not FFT-friendly. The measurements are unchanged, but:
* each file (and each boss cue's stack of stems) is measured in its own worker process, longest first. The
  worker count is HYMN_TEST_JOBS, else the CPU count (at most 4).
* each measurement is cached under HYMN_TEST_CACHE (default ~/.cache/hymn-undertow/audio_loudness). The key
  is the SHA-256 of the decoded files' bytes, of every tools/audio/synth/*.py module, of this file, of the numpy
  version and of the ffmpeg version line, so a hit is the value this code computes for these bytes. Only the
  measured numbers are cached; the comparison against targets.py runs fresh every time. HYMN_TEST_CACHE=off
  measures everything again."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))
import targets  # noqa: E402
from synth.loudness import integrated_lufs, momentary_max_lufs, true_peak_dbtp  # noqa: E402
from synth.mixer import read_audio  # noqa: E402

AUDIO = ROOT / "assets" / "audio"
LFS_MUSIC = re.compile(r"^(music/act[0-9]+|sfx/act3)/")  # Git LFS paths, as validate_data.LFS_MUSIC_RE and .gitattributes
LFS_AUDIO = ROOT / "assets" / "lfs" / "audio"  # ADR 0173: new Act I audio, the same layout and rules as AUDIO


def rel(p: Path) -> str:
    """A file's path for targets.rule_for: relative to assets/audio/ or to assets/lfs/audio/ (ADR 0173)."""
    return (p.relative_to(LFS_AUDIO) if p.is_relative_to(LFS_AUDIO) else p.relative_to(AUDIO)).as_posix()


def in_lfs(p: Path) -> bool:
    return p.is_relative_to(LFS_AUDIO) or bool(LFS_MUSIC.match(rel(p)))
MAX_DEFAULT_JOBS = 4  # each worker can hold ~1 GB while it oversamples a long music bed


def _decode(p: Path) -> np.ndarray:
    """The decoded file; a mono file (both channels equal) as mono, so it measures as its own target says."""
    # ffmpeg upmixes mono at -3 dB per channel, so a mono file is decoded again as mono.
    y = read_audio(str(p), channels=2)
    return read_audio(str(p), channels=1) if np.array_equal(y[:, 0], y[:, 1]) else y


def measure_file(path: str, metric: str) -> dict:
    """True peak, and the rule's loudness metric unless the file is a stem (measured with its stack)."""
    y = _decode(Path(path))
    out = {"tp": true_peak_dbtp(y)}
    if metric != "stem":
        out["lv"] = integrated_lufs(y) if metric == "integrated" else momentary_max_lufs(y)
    return out


def measure_stack(paths: list[str]) -> dict:
    """One boss cue: the stack's loudness and true peak, and stem 1 alone (each stem's own peak is a file job)."""
    group = [_decode(Path(p)) for p in paths]
    n = min(len(s) for s in group)
    stack = sum(s[:n] for s in group)
    return {"full": integrated_lufs(stack), "tp": true_peak_dbtp(stack), "first": integrated_lufs(group[0])}


def _jobs() -> int:
    env = os.environ.get("HYMN_TEST_JOBS", "")
    return max(1, int(env)) if env.isdigit() else max(1, min(MAX_DEFAULT_JOBS, os.cpu_count() or 1))


class _Cache:
    def __init__(self) -> None:
        env = os.environ.get("HYMN_TEST_CACHE", "")
        self.dir = None if env == "off" else Path(env or Path.home() / ".cache" / "hymn-undertow") / "audio_loudness"
        h = hashlib.sha256()
        for src in sorted((ROOT / "tools" / "audio" / "synth").glob("*.py")) + [Path(__file__).resolve()]:
            h.update(src.name.encode() + b"\0" + src.read_bytes())
        ffmpeg = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.splitlines()[:1]
        h.update(f"numpy {np.__version__}\0{ffmpeg}".encode())
        self.code = h.hexdigest()

    def key(self, kind: str, metric: str, paths: list[Path]) -> str:
        h = hashlib.sha256(f"{self.code}\0{kind}\0{metric}".encode())
        for p in paths:
            h.update(b"\0" + hashlib.sha256(p.read_bytes()).digest())
        return h.hexdigest()

    def get(self, key: str) -> dict | None:
        if self.dir is None:
            return None
        try:
            return json.loads((self.dir / f"{key}.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def put(self, key: str, value: dict) -> None:
        if self.dir is None:
            return
        try:
            self.dir.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=self.dir, suffix=".tmp")  # unique per writer; renamed into place
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(value, f)
            os.replace(tmp, self.dir / f"{key}.json")
        except OSError:
            pass  # a cache that cannot be written only costs time


def measure_all(jobs: list[tuple]) -> list[dict]:
    """Run (fn, args, paths, kind, metric) jobs through the cache and a process pool; results in job order."""
    cache = _Cache()
    keys = [cache.key(kind, metric, paths) for _, _, paths, kind, metric in jobs]
    results: list = [cache.get(k) for k in keys]
    todo = sorted((i for i, r in enumerate(results) if r is None),
                  key=lambda i: -sum(p.stat().st_size for p in jobs[i][2]))
    if todo:
        with ProcessPoolExecutor(max_workers=min(_jobs(), len(todo))) as pool:
            futures = {i: pool.submit(jobs[i][0], *jobs[i][1]) for i in todo}
            for i, fut in futures.items():
                results[i] = fut.result()
                cache.put(keys[i], results[i])
    return results


@unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg to decode")
class AudioLoudnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.files = sorted(AUDIO.rglob("*.ogg")) + sorted(LFS_AUDIO.rglob("*.ogg"))

    def test_every_file_has_a_target(self) -> None:
        missing = [rel(p) for p in self.files if targets.rule_for(rel(p)) is None]
        self.assertEqual(missing, [], "add a rule to tools/audio/targets.py")

    def test_sizes(self) -> None:
        total = 0
        for p in self.files + sorted(AUDIO.rglob("*.json")):
            if in_lfs(p):
                continue  # Git LFS (ADR 0039): outside the plain-git budget and the 5 MB limit
            size = p.stat().st_size
            total += size
            self.assertLessEqual(size, targets.FILE_LIMIT, f"{p} is over 5 MB")
        self.assertLessEqual(total, targets.TOTAL_BUDGET, f"all audio {total / 1048576:.2f} MiB is over budget")

    def test_loudness_and_peaks(self) -> None:
        ruled = []                       # (rel, rule) in file order, as before M2-NIT-06
        stems: dict[str, list[Path]] = {}  # one stack per "stem" rule (one boss cue each), in file order: p1, p2, ...
        for p in self.files:
            rel_path = rel(p)
            rule = targets.rule_for(rel_path)
            if rule is None:
                continue
            ruled.append((p, rel_path, rule))
            if rule[1] == "stem":
                stems.setdefault(rule[0], []).append(p)
        file_jobs = [(measure_file, (str(p), rule[1]), [p], "file", rule[1]) for p, _, rule in ruled]
        stack_jobs = [(measure_stack, ([str(p) for p in group],), group, "stack", "stem") for group in stems.values()]
        results = measure_all(file_jobs + stack_jobs)
        per_file = dict(zip((j[1][0] for j in file_jobs), results[:len(file_jobs)]))
        per_stack = dict(zip(stems, results[len(file_jobs):]))

        bad = []
        for p, rel_path, rule in ruled:
            _, metric, target, tol, ceiling, _ = rule
            tp = per_file[str(p)]["tp"]
            if tp > ceiling + 0.05:
                bad.append(f"{rel_path}: true peak {tp:.2f} dBTP over {ceiling}")
            if metric == "stem":
                continue
            lv = per_file[str(p)]["lv"]
            if abs(lv - target) > tol:
                bad.append(f"{rel_path}: {metric} {lv:.2f} LUFS, target {target} +- {tol}")
        for glob, r in per_stack.items():
            _, _, target, tol, ceiling, _ = targets.rule_for(glob.replace("*", "1"))
            if abs(r["full"] - target) > tol:
                bad.append(f"{glob} together: {r['full']:.2f} LUFS, target {target} +- {tol}")
            if r["tp"] > ceiling + 0.05:
                bad.append(f"{glob} together: true peak {r['tp']:.2f} dBTP over {ceiling}")
            if r["first"] > r["full"]:
                bad.append(f"{glob}: stem 1 alone is louder than the stack")
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
