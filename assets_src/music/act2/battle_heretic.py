"""`battle_heretic`: the regular battle theme once the party are heretics, Ch14 on (M4-A2P-091; ADR 0204 §9; the cue
sheet §2): a variant of Act I's `battle_standard_v2`, not a new theme.

Original composition for this project (SPEC §2, §9). The notes, form, riff, timing, intro and loop are v1's
(battle_standard.py) and the band is v2's (battle_standard_v2.py), both imported, so the two cues stay the same piece
and can swap mid-act. The only borrowed line is our own: ORDER_HUM (motifs.py). All its notes (G A B E D) lie in the
theme's E Phrygian, so its opening cell sits under the riff, hummed low. Nothing is taken from any existing music.

The brief (the cue sheet): the same fight, with the Order now hunting them. Harder, its warmth gone. So the band is
v2's, darkened:
* the flute lead plays an octave lower, behind a darker filter, so it is a voice in the fight and no longer bright
  over it; the twin lead the same;
* the metallophone doubling of the lead and the kotekan come down 6 dB and lose their top;
* the jingles are gone;
* the gong cycle and the kettle come up: the Stillguard's bronze;
* the Order hums ORDER_HUM's first six notes, low and close, twice a loop (bars 9 and 33), in long notes under the
  riff.
E Phrygian at 160 BPM, a 3.0 s intro and a 72.0 s loop, exactly as v2, so music.json can swap the two. Vorbis q3.5,
-16 LUFS integrated. Plain git (ADR 0175).

Render:  python3 tools/audio/render_all.py --only battle_heretic
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)

import numpy as np  # noqa: E402

from motifs import ORDER_HUM  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V2 = _mod("battle_standard_v2", os.path.join(MUSIC, "battle_standard_v2.py"))
V1 = V2.V1

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "battle_heretic.ogg")
SEED = 20261980
TARGET_LUFS = -16.0
HUM_BARS = (9, 33)
HUM_NOTES = 6
HUM_STRETCH = 2.0          # ORDER_HUM's beats doubled: long notes under the riff


def dark_lead(x: np.ndarray) -> np.ndarray:
    return V2.lead_bus(filt(x, [bq_lowpass(3200, 0.7)]))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    events, phrases = V1.build_events()
    events = [e for e in V2._reorchestrate(events) if e.bus != "jingle"]
    mx = LoopMixer(intro_s=2 * V1.BAR, loop_s=V1.LOOP_BARS * V1.BAR, intro_tail_s=6.0)
    # v2's bus gains, then the heretic changes: the metal 6 dB down and darker, the bronze up, no jingles
    mx.bus("drums", -5.2, send=0.12, process=V1.drum_bus)
    mx.bus("jingle", -60.0, send=0.0)
    mx.bus("gong", -11.2, send=0.35)
    mx.bus("kettle", -6.9, send=0.22)
    mx.bus("bass", -3.8, send=0.0, process=V1.bass_bus)
    mx.bus("stab", -8.3, send=0.25)
    mx.bus("tak", 4.7, send=0.08, process=lambda x: filt(x, [bq_highpass(140, 0.7), bq_lowpass(4500, 0.7)]))
    mx.bus("metal", -10.5, send=0.28, process=lambda x: filt(x, [bq_lowpass(4000, 0.7)]))
    mx.bus("metal_lead", -8.6, send=0.30, process=lambda x: filt(x, [bq_lowpass(4000, 0.7)]))
    mx.bus("lead", -0.7, send=0.22, process=dark_lead)
    mx.bus("lead2", -3.6, send=0.22, process=dark_lead)
    mx.bus("hum", -4.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))

    rendered = render_jobs([V2.event_job(e) for e in events], workers=1)
    intro_offset = -(V1.INTRO_BARS[0] - 1) * V1.BAR
    for e, x in zip(events, rendered):
        mx.add(e.bus, x, e.t, pan=e.pan)
        if e.bar in V1.INTRO_BARS:
            mx.add(e.bus, x, e.t + intro_offset, pan=e.pan, part="intro")
    for k, (bus, notes) in enumerate(phrases):
        low = [(t, d, m - 12, v) for t, d, m, v in notes]                   # the lead an octave down
        for t, x in V2.flute_line(low, V2.SEED + 977 * k, breath=0.5 if bus == "lead" else 0.42):
            mx.add(bus, x, t, pan=-0.15 if bus == "lead" else 0.3)
    line = [(float(m), b * V1.BEAT * HUM_STRETCH) for m, b in ORDER_HUM[:HUM_NOTES]]
    for k, bar in enumerate(HUM_BARS):
        x = hum_ensemble(line, voices=14, seed=SEED + 10 + k, register="low", spread=0.7)
        mx.add("hum", x, (bar - 1) * V1.BAR - 0.1, pan=-0.2 + 0.4 * k)

    room = ModFDNReverb(rt60=1.7, rt60_high=0.7, predelay=0.018, size=0.85, mod_depth=8.0, mod_rate=0.6,
                        early_level=0.35, seed=SEED % 9973)
    intro, loop = mx.render(reverb=room, reverb_return_db=-3.0)
    rep: dict = {}
    intro, loop = master_loop(intro, loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    y = np.concatenate([intro, loop])
    S, L = len(intro), len(loop)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, y, quality=3.5, tags={"LOOPSTART": str(S), "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, S, L, V1.BPM, 4,
                       extra={"intro_bars": 2, "loop_bars": V1.LOOP_BARS})
    m = measure(y)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"battle_heretic: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  loop {S}+{L}  limiter {rep}")
    return m


if __name__ == "__main__":
    render()
