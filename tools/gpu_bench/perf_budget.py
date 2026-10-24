"""Perf regression sweep against SPEC §4.2 (the PC GPU queue's perf sweep).

Usage: python tools/gpu_bench/perf_budget.py <out_baseline.csv> <in.csv> [<in.csv> ...]
Merges gpu_bench CSVs (scene, camera, preset, res, GPU median and p99, ...) into one baseline CSV, and
prints a markdown report projecting each row from the measuring card (RX 9070 XT) to the SPEC tiers:
* recommended (RTX 3060 class): High at 1440p must hold 60 fps, so GPU <= 16.7 ms; factor 2.3-2.8x;
* minimum (GTX 1060 class): Low at 1080p must hold 30 fps (33.3 ms), 60 where it can (16.7 ms); 4.2-5.0x.
A row is flagged OVER when even the low factor misses the budget, AT RISK when only the high factor does.
The factors are estimates (docs/kb/qa/gpu/2026-10-23-gpu-report.md), so treat the flags as triage.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

TIERS = [
    # (label, preset, res_h, budget_ms, factor_lo, factor_hi)
    ("recommended: High 1440p, 60 fps", "high", "1440", 16.7, 2.3, 2.8),
    ("minimum: Low 1080p, 30 fps", "low", "1080", 33.3, 4.2, 5.0),
    ("minimum: Low 1080p, 60 fps", "low", "1080", 16.7, 4.2, 5.0),
]
FIELDS = ["scene", "camera", "preset", "res_w", "res_h", "internal_w", "internal_h", "gpu_median_ms", "gpu_p99_ms",
          "cpu_median_ms", "frame_median_ms", "frame_p99_ms", "adapter", "driver"]
# Optional columns of the slice sweep (tools/gpu_bench/slice_sweep.tscn): empty on gpu_bench rows.
FIELDS += ["gpu_mean_ms", "frame_max_ms", "hidden_max_ms", "hidden_total_ms", "visible_max_ms"]


def load(paths: list[str]) -> list[dict]:
    rows = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            rows.extend(csv.DictReader(f))
    return rows


def verdict(ms: float, budget: float, lo: float, hi: float) -> str:
    if ms * lo > budget:
        return "**OVER**"
    if ms * hi > budget:
        return "at risk"
    return "ok"


def main() -> int:
    out, ins = sys.argv[1], sys.argv[2:]
    rows = load(ins)
    rows.sort(key=lambda r: (r["scene"], r["camera"], r["res_h"], ["low", "medium", "high", "ultra"].index(r["preset"])))
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    for label, preset, res_h, budget, lo, hi in TIERS:
        print(f"\n### {label} (budget {budget} ms; RX 9070 XT x {lo}-{hi})\n")
        print("| Scene / camera | 9070 XT median (p99) ms | Projected ms | Verdict |")
        print("|---|---:|---:|---|")
        for r in rows:
            if r["preset"] != preset or r["res_h"] != res_h:
                continue
            ms = float(r["gpu_median_ms"])
            p99 = float(r["gpu_p99_ms"])
            print(f"| {r['scene']} {r['camera']} | {ms:.2f} ({p99:.2f}) | {ms * lo:.1f}-{ms * hi:.1f} | "
                  f"{verdict(ms, budget, lo, hi)} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
