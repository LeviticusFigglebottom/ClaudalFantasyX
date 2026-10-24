"""M2-NIT-04: tools/screenshots/capture.sh names a Godot process that exits non-zero, in both modes.

capture.sh runs against a stub renderer (HYMN_GODOT_RENDER) that writes a fake capture line and exits with a
chosen code when its --shots argument holds a failing id. Per-shot mode (the default) and
HYMN_CAPTURE_SHARED=1 must both write `CAPTURE PROCESS EXIT <rc>: <shots>` to the log, list the run in the
closing "exited non-zero" line, and return the process's exit code (docs/kb/qa/screenshots.md, "Engine race").
"""

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / "tools" / "screenshots" / "capture.sh"
ABORT_RC = 134  # SIGABRT, what the lavapipe pipeline abort at exit returns (M1-QA-10)

STUB = """#!/usr/bin/env bash
# Stub renderer: prints a capture line for its shots, exits STUB_RC when one of them is in STUB_FAIL.
shots=""
for a in "$@"; do case "$a" in --shots=*) shots="${a#--shots=}" ;; esac; done
echo "Capture: wrote $shots"
IFS=',' read -ra ids <<< "$shots"
for id in "${ids[@]}"; do
  case ",$STUB_FAIL," in *",$id,"*) exit "$STUB_RC" ;; esac
done
exit 0
"""


class CaptureExitLineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.stub = self.dir / "godot-render-stub"
        self.stub.write_text(STUB)
        self.stub.chmod(self.stub.stat().st_mode | stat.S_IXUSR)
        self.log = self.dir / "hymn_capture.log"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_capture(self, shots: str, fail: str, shared: bool) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env.update(
            {
                "HYMN_GODOT_RENDER": str(self.stub),
                "TMPDIR": str(self.dir),
                "STUB_FAIL": fail,
                "STUB_RC": str(ABORT_RC),
                "HYMN_CAPTURE_SHARED": "1" if shared else "0",
            }
        )
        return subprocess.run(
            ["bash", str(CAPTURE), "--shots", shots], env=env, capture_output=True, text=True, timeout=60
        )

    def test_per_shot_mode_names_the_failing_shot(self) -> None:
        r = self.run_capture("a,b,c", "b", shared=False)
        self.assertEqual(r.returncode, ABORT_RC)
        log = self.log.read_text()
        self.assertIn(f"CAPTURE PROCESS EXIT {ABORT_RC}: b\n", log)
        self.assertNotIn("CAPTURE PROCESS EXIT %d: a" % ABORT_RC, log)
        self.assertIn(f"capture process(es) exited non-zero: b (exit {ABORT_RC})", r.stdout)
        self.assertIn(f"CAPTURE PROCESS EXIT {ABORT_RC}: b", r.stdout, "the gate's grep echoes it")

    def test_shared_mode_names_the_failing_run_too(self) -> None:
        r = self.run_capture("a,b,c", "b", shared=True)
        self.assertEqual(r.returncode, ABORT_RC)
        log = self.log.read_text()
        self.assertIn(f"CAPTURE PROCESS EXIT {ABORT_RC}: a,b,c\n", log, "the same signature, with the shot list")
        self.assertEqual(log.count("Capture: wrote"), 1, "one shared process")
        self.assertIn(f"capture process(es) exited non-zero: a,b,c (exit {ABORT_RC})", r.stdout)
        self.assertIn(f"CAPTURE PROCESS EXIT {ABORT_RC}: a,b,c", r.stdout)

    def test_a_clean_run_writes_no_exit_line_in_either_mode(self) -> None:
        for shared in (False, True):
            with self.subTest(shared=shared):
                r = self.run_capture("a,b", "", shared=shared)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertNotIn("CAPTURE PROCESS EXIT", self.log.read_text())
                self.assertNotIn("exited non-zero", r.stdout)


if __name__ == "__main__":
    unittest.main()
