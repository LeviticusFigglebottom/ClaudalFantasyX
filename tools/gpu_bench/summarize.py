"""Summarize a gpu_bench CSV into the markdown tables of docs/kb/qa/gpu/<date>-gpu-report.md.

Usage: python tools/gpu_bench/summarize.py <bench.csv>

Budget verdicts project the measured GPU median onto the SPEC 4.2 reference cards with a
relative-performance factor (RANGES below). Those factors are estimates from public raster
benchmarks, not measurements: a verdict is PASS only if it holds at the pessimistic end,
FAIL only if it fails at the optimistic end, and MARGINAL otherwise.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict

# How many times slower the reference card is than the measuring card (RX 9070 XT), low..high.
RANGES = {"rtx3060": (2.3, 2.8), "gtx1060": (4.2, 5.0)}
BUDGET_60 = 1000.0 / 60.0
BUDGET_30 = 1000.0 / 30.0
# SPEC 4.2: High at 1440p60 on the recommended tier; Low at 1080p 30-60 fps on the minimum tier.
CHECKS = [
    ("High 1440p on RTX 3060 (60 fps)", "high", 2560, "rtx3060", BUDGET_60),
    ("Low 1080p on GTX 1060 (30 fps floor)", "low", 1920, "gtx1060", BUDGET_30),
]


def verdict(ms: float, card: str, budget: float) -> str:
    lo, hi = RANGES[card]
    if ms * hi <= budget:
        return "PASS"
    if ms * lo > budget:
        return "FAIL"
    return "MARGINAL"


def load(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main(path: str) -> None:
    rows = [r for r in load(path) if float(r["gpu_median_ms"]) > 0.0]
    scenes = [r for r in rows if r["variant"] == "scene"]

    print("## Scene x preset x resolution (GPU / CPU ms, median and p99)\n")
    print("| Scene | Camera | Preset | Res | Internal | GPU med | GPU p99 | CPU med | CPU p99 |")
    print("|---|---|---|---|---|---:|---:|---:|---:|")
    for r in scenes:
        print(
            f"| {r['scene']} | {r['camera']} | {r['preset']} | {r['res_w']}x{r['res_h']} | "
            f"{r['internal_w']}x{r['internal_h']} | {float(r['gpu_median_ms']):.2f} | "
            f"{float(r['gpu_p99_ms']):.2f} | {float(r['cpu_median_ms']):.2f} | {float(r['cpu_p99_ms']):.2f} |"
        )

    print("\n## Budget verdicts (projected; see method)\n")
    head = " | ".join(f"{name}: 9070 XT ms -> projected ms -> verdict" for name, *_ in CHECKS)
    print(f"| Scene | Camera | {head} |")
    print("|---|---|" + "---|" * len(CHECKS))
    by_key: dict[tuple, dict] = {(r["scene"], r["camera"], r["preset"], int(r["res_w"])): r for r in scenes}
    for scene, camera in dict.fromkeys((r["scene"], r["camera"]) for r in scenes):
        cells = []
        for _, preset, width, card, budget in CHECKS:
            r = by_key.get((scene, camera, preset, width))
            if r is None:
                cells.append("n/a")
                continue
            ms = float(r["gpu_median_ms"])
            lo, hi = RANGES[card]
            cells.append(f"{ms:.2f} -> {ms * lo:.1f}-{ms * hi:.1f} -> **{verdict(ms, card, budget)}**")
        print(f"| {scene} | {camera} | " + " | ".join(cells) + " |")

    breakdown = [r for r in rows if r["variant"] != "scene"]
    if breakdown:
        print("\n## Feature breakdowns (GPU median ms; delta vs. the feature-off row)\n")
        groups: dict[tuple, list[dict]] = defaultdict(list)
        for r in breakdown:
            groups[(r["scene"], r["camera"], r["preset"], r["res_w"], r["res_h"])].append(r)
        for (scene, camera, preset, w, h), rs in groups.items():
            base = float(rs[0]["gpu_median_ms"])
            print(f"\n**{scene} {camera}, preset {preset}, {w}x{h}** (base row: {rs[0]['variant']})\n")
            print("| Variant | GPU med | GPU p99 | Delta vs base |")
            print("|---|---:|---:|---:|")
            for r in rs:
                ms = float(r["gpu_median_ms"])
                print(f"| {r['variant']} | {ms:.2f} | {float(r['gpu_p99_ms']):.2f} | {ms - base:+.2f} |")


if __name__ == "__main__":
    main(sys.argv[1])
