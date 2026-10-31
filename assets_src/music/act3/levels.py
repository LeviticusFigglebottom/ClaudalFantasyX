"""Bus levels for a through-composed cue (synth.mixer.Mixer has no bus_lufs, LoopMixer has): each bus's integrated
loudness after its process and gain, the way Mixer.render sums it. The Act III cues balance their GAINS from these."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools", "audio"))

from synth.dsp import db_to_lin  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402


def bus_levels(mx) -> dict[str, float]:
    out = {}
    for name, b in mx.buses.items():
        x = (b.process(b.buf) if b.process else b.buf) * db_to_lin(b.gain_db)
        out[name] = round(float(integrated_lufs(x)), 1)
    return out
