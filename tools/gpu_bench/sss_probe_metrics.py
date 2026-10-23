"""Deep-water SSS patch metrics for a water_look_probe pair (M1-RND-18, the M1-ART-05 method).

Usage: python tools/gpu_bench/sss_probe_metrics.py <sss_on.png> <sss_off.png> [--probe-json on.json]
Both images come from game/levels/_tests/swatches/water_look_probe.tscn with --camera=survey: one with the
look's SSS, one with col_sss #000000. Deep water = rows y < 290 (above the reef lip), foam (OkL > 0.85
in either image) excluded. Prints the share of deep pixels where SSS adds dE_ok > 0.03 / > 0.05, the
max added, the OkL p90 - p10 spread of the SSS-on image, and (with --probe-json) the > 15 m band median
and its dE_ok to deep_teal_shadow "+1" (#106776).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "screenshots"))
import palette_check as pc  # noqa: E402
import pngio  # noqa: E402

DEEP_ROWS = 290
FOAM_L = 0.85
DEEP_SWATCH = "#106776"


def metrics(on: np.ndarray, off: np.ndarray) -> dict:
    la = pc.image_oklab(on[:DEEP_ROWS, :, :3])
    lb = pc.image_oklab(off[:DEEP_ROWS, :, :3])
    deep = (la[..., 0] <= FOAM_L) & (lb[..., 0] <= FOAM_L)
    de = np.linalg.norm(la - lb, axis=-1)[deep]
    lum = la[..., 0][deep]
    return {
        "deep_pixels": int(deep.sum()),
        "share_over_0.03": float(np.mean(de > 0.03)),
        "share_over_0.05": float(np.mean(de > 0.05)),
        "max_added": float(de.max()),
        "okl_p90_p10": float(np.percentile(lum, 90) - np.percentile(lum, 10)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("on")
    ap.add_argument("off")
    ap.add_argument("--probe-json")
    a = ap.parse_args()
    out = metrics(pngio.read(a.on), pngio.read(a.off))
    if a.probe_json:
        bands = json.loads(Path(a.probe_json).read_text(encoding="utf-8")).get("bands", {})
        print(json.dumps(bands, indent=1)[:600], file=sys.stderr)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
