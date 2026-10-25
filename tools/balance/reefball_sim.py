#!/usr/bin/env python3
"""Reefball balance simulator front end (M3-RBL-01, SPEC §6.9).

Runs tools/balance/reefball_sim_main.gd in headless Godot for every suite in
tools/balance/reefball_targets.json, checks each policy's win rate against its band (and the
smart policy's draw rate against max_draw_pct), prints a Markdown table and, with --report,
rewrites the block between the balance markers in docs/kb/design/reefball.md.

Usage: python3 tools/balance/reefball_sim.py [--seeds N] [--godot PATH] [--report] [--check]
--check exits 1 if any band is missed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = ROOT / "tools/balance/reefball_targets.json"
DOC = ROOT / "docs/kb/design/reefball.md"
SIM_SCRIPT = "res://tools/balance/reefball_sim_main.gd"
START = "<!-- reefball-balance:start -->"
END = "<!-- reefball-balance:end -->"
DEFAULT_SEEDS = 2000


def load_suites(path: Path = TARGETS) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["suites"]


def run_suite(godot: str, suite: dict, seeds: int) -> list[dict]:
    """Runs one suite in Godot and returns one aggregate per policy (ReefballSim.run)."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "reefball.json"
        cmd = [godot, "--headless", "--path", str(ROOT), "-s", SIM_SCRIPT, "--", f"--match={suite['match']}",
               f"--policies={','.join(suite['bands'].keys())}", f"--seeds={seeds}", f"--out={out}"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        if proc.returncode != 0 or not out.exists():
            sys.stderr.write(proc.stdout + proc.stderr)
            raise RuntimeError(f"reefball sim failed for suite {suite['id']} (exit {proc.returncode})")
        return json.loads(out.read_text(encoding="utf-8"))


def in_band(result: dict, suite: dict) -> bool:
    """A policy passes when its win % is in its band (null: report only), it never stalls, and the
    smart policy draws no more than max_draw_pct."""
    band = suite["bands"].get(result["policy"])
    ok = result.get("stalled", 0) == 0
    if band is not None:
        ok = ok and band[0] <= result["win_pct"] <= band[1]
    if result["policy"] == "smart" and "max_draw_pct" in suite:
        ok = ok and result["draw_pct"] <= suite["max_draw_pct"]
    return ok


def band_text(band: list | None) -> str:
    return "report only" if band is None else f"{band[0]}–{band[1]}%"


def markdown(suite: dict, results: list[dict], seeds: int, today: str) -> str:
    lines = [f"Measured {today}, {seeds} seeds, match `{suite['match']}` "
             f"(`python3 tools/balance/reefball_sim.py --report`).", "",
             "| Policy | Band | Win % | Draw % | Goals for | Goals against | Contacts | Turnovers | In band |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['policy']} | {band_text(suite['bands'].get(r['policy']))} | {r['win_pct']:.1f} | "
                     f"{r['draw_pct']:.1f} | {r['mean_for']:.2f} | {r['mean_against']:.2f} | "
                     f"{r['mean_contacts']:.1f} | {r['mean_turnovers']:.1f} | "
                     f"{'yes' if in_band(r, suite) else 'NO'} |")
    return "\n".join(lines)


def replace_block(text: str, body: str) -> str:
    """Replaces what sits between the START and END markers (appends a marked block if absent)."""
    block = f"{START}\n{body}\n{END}"
    if START in text and END in text:
        head, rest = text.split(START, 1)
        return head + block + rest.split(END, 1)[1]
    return text.rstrip("\n") + "\n\n" + block + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, default=DEFAULT_SEEDS)
    ap.add_argument("--godot", default=os.environ.get("GODOT", "godot"))
    ap.add_argument("--report", action="store_true", help=f"rewrite the balance block in {DOC.name}")
    ap.add_argument("--check", action="store_true", help="exit 1 if a band is missed")
    args = ap.parse_args(argv)
    today = dt.date.today().isoformat()
    misses = 0
    bodies = []
    for suite in load_suites():
        results = run_suite(args.godot, suite, args.seeds)
        misses += sum(0 if in_band(r, suite) else 1 for r in results)
        bodies.append(markdown(suite, results, args.seeds, today))
    body = "\n\n".join(bodies)
    print(body)
    if args.report:
        DOC.write_text(replace_block(DOC.read_text(encoding="utf-8"), body), encoding="utf-8")
    if args.check and misses:
        print(f"reefball_sim: {misses} band(s) missed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
