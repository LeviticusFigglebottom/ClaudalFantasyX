"""M2-QA-01: tools/screenshots/capture.sh kills a shot's process that never exits, names it, and goes on.

The stub renderer (HYMN_GODOT_RENDER) hangs when its --shots argument holds an id in STUB_HANG: like the
real wrapper it starts a background child (the wrapper's Xvfb) and then blocks in a foreground child (Godot
deadlocked). With HYMN_SHOT_TIMEOUT=2 the shot must be killed within seconds, child processes included,
logged as `CAPTURE PROCESS EXIT 124 (hung: killed after 2 s): <id>`, and fail the run, while the shots
after it still render (docs/kb/qa/screenshots.md, "Engine deadlock").
"""

import os
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / "tools" / "screenshots" / "capture.sh"
TIMEOUT_RC = 124  # timeout(1)'s exit code for a command it had to stop
LIMIT_S = 2

STUB = """#!/usr/bin/env bash
# Stub renderer: prints a capture line for its shots; hangs (a background child plus a blocking
# foreground child, both PIDs written to $STUB_PIDS) when one of them is in STUB_HANG.
shots=""
for a in "$@"; do case "$a" in --shots=*) shots="${a#--shots=}" ;; esac; done
echo "Capture: wrote $shots"
IFS=',' read -ra ids <<< "$shots"
for id in "${ids[@]}"; do
  case ",$STUB_HANG," in
    *",$id,"*)
      sleep 1000 &
      echo $! >> "$STUB_PIDS"
      sleep 1001 &
      fg=$!
      echo $fg >> "$STUB_PIDS"
      wait $fg
      ;;
  esac
done
exit 0
"""


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


class CaptureHangGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.stub = self.dir / "godot-render-stub"
        self.stub.write_text(STUB)
        self.stub.chmod(self.stub.stat().st_mode | stat.S_IXUSR)
        self.log = self.dir / "hymn_capture.log"
        self.pids = self.dir / "pids"

    def tearDown(self) -> None:
        if self.pids.exists():
            for line in self.pids.read_text().split():
                if alive(int(line)):
                    os.kill(int(line), 9)  # only the stub's own children, by the PIDs it wrote
        self.tmp.cleanup()

    def run_capture(self, shots: str, hang: str, shared: bool = False) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env.update(
            {
                "HYMN_GODOT_RENDER": str(self.stub),
                "TMPDIR": str(self.dir),
                "STUB_HANG": hang,
                "STUB_PIDS": str(self.pids),
                "HYMN_SHOT_TIMEOUT": str(LIMIT_S),
                "HYMN_CAPTURE_SHARED": "1" if shared else "0",
            }
        )
        return subprocess.run(
            ["bash", str(CAPTURE), "--shots", shots], env=env, capture_output=True, text=True, timeout=120
        )

    def test_a_hung_shot_is_killed_named_and_fails_the_run(self) -> None:
        t0 = time.monotonic()
        r = self.run_capture("a,b,c", "b")
        self.assertLess(time.monotonic() - t0, 30, "the guard, not the stub's 1000 s sleep, ended shot b")
        self.assertEqual(r.returncode, TIMEOUT_RC, r.stdout + r.stderr)
        log = self.log.read_text()
        self.assertIn(f"CAPTURE PROCESS EXIT {TIMEOUT_RC} (hung: killed after {LIMIT_S} s): b\n", log)
        self.assertIn("Capture: wrote c", log, "the shots after the hung one still run")
        self.assertNotIn("CAPTURE PROCESS EXIT 124", log.split("Capture: wrote b")[0], "shot a was fine")
        self.assertIn(f"exited non-zero: b (exit {TIMEOUT_RC} (hung: killed after {LIMIT_S} s))", r.stdout)

    def test_the_hung_shots_children_die_with_it(self) -> None:
        self.run_capture("b", "b")
        pids = [int(p) for p in self.pids.read_text().split()]
        self.assertEqual(len(pids), 2)
        deadline = time.monotonic() + 5
        while any(alive(p) for p in pids) and time.monotonic() < deadline:
            time.sleep(0.1)
        self.assertFalse([p for p in pids if alive(p)], "Godot and the wrapper's Xvfb stand-ins were killed")

    def test_shared_mode_scales_the_limit_by_the_shot_count(self) -> None:
        r = self.run_capture("a,b", "b", shared=True)
        self.assertEqual(r.returncode, TIMEOUT_RC, r.stdout + r.stderr)
        line = f"CAPTURE PROCESS EXIT {TIMEOUT_RC} (hung: killed after {2 * LIMIT_S} s): a,b\n"
        self.assertIn(line, self.log.read_text())

    def test_a_shot_that_exits_in_time_is_not_flagged(self) -> None:
        r = self.run_capture("a,b", "")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("CAPTURE PROCESS EXIT", self.log.read_text())


if __name__ == "__main__":
    unittest.main()
