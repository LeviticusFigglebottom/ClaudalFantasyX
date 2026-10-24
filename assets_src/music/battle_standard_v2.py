"""Standard battle theme v2 (M2-AUD-03): the M1 composition re-orchestrated around what synthesis does well.

Original composition for this project (SPEC §2, §9). The notes, form, riff, interlock and timing are v1's
(battle_standard.py, imported, so the two stay the same piece for A/B listening); what changes is the band. The M1
self-assessment named the modelled distorted guitar and the virtual-analog lead as the weakest elements, and the
listening notes offered "metallophone and drums only" as a direction. v2 takes it:

* **No guitar.** Each open or accented guitar chord becomes a struck stab: a low metallophone pair (root and fifth,
  two octaves up, hard mallets, hand-damped at the chord's length) over a kettle-gong click; each palm-muted chug
  becomes a muted plucked string an octave over the bass (a tight, dry "tak").
* **No synth lead.** The theme is a breath flute played hard (strong breath, short tongued attacks, little
  vibrato), doubled an octave up by the metallophone as in v1's E section; the E section's twin lead in thirds is
  two flutes, panned apart. The answer phrase drops an octave so the flute stays in its singing range.
* The rhythm section (frame drums, the big drum, jingles, the fingered bass), the gong cycle and the kotekan are
  v1's events unchanged.

Loop: 3.0 s intro (v1's bars 47-48) + a 72.0 s loop, as v1. Render:
    python3 assets_src/music/battle_standard_v2.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("battle_standard", os.path.join(os.path.dirname(__file__),
                                                                                "battle_standard.py"))
V1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V1)

OUT = os.path.join(ROOT, "assets", "audio", "music", "battle_standard_v2.ogg")
SEED = 20261106
TARGET_LUFS = -16.0
FLUTE_PRE = 0.065
FLUTE_TOP = 86.0   # D6: phrases that climb past it are played an octave down


def _reorchestrate(events: list) -> list:
    """v1's events with the guitar parts replaced (take 0 only: the stab and the pluck are one player)."""
    out = []
    for e in events:
        if e.bus != "gtr":
            out.append(e)
            continue
        a = e.args
        if a.get("take", 0) != 0:
            continue
        if a["mute"] >= 0.85:
            out.append(V1.Ev("tak", "tak", e.t, dict(m=a["root"] + 12, vel=a["vel"], dur=a["dur"]), 0.25, e.bar))
        else:
            for k, off in enumerate((24, 31)):
                out.append(V1.Ev("stab", "stab", e.t + 0.002 * k, dict(m=a["root"] + off, vel=a["vel"], dur=a["dur"]),
                                 -0.3 + 0.6 * k, e.bar))
            out.append(V1.Ev("stab", "click", e.t, dict(m=a["root"] + 36, vel=a["vel"]), 0.0, e.bar))
    return out


def event_job(e) -> tuple:
    a = e.args
    if e.kind == "tak":
        return string_pluck, dict(m=a["m"], dur=min(a["dur"], 0.09), vel=0.55 + 0.4 * a["vel"],
                                  seed=SEED + int(round(e.t * 1000)) * 7, pick_pos=0.12, t60=0.8, mute=0.7,
                                  max_f=5000.0, release=0.02)
    if e.kind == "stab":
        return metallophone_note, dict(m=a["m"], vel=0.35 + 0.45 * a["vel"], seed=SEED + int(round(e.t * 1000)) * 11,
                                       decay=2.2, hardness=0.75, ombak_hz=6.5, damp_at=max(0.08, a["dur"] * 0.9))
    if e.kind == "click":
        return kettle_gong, dict(m=a["m"], vel=0.3 + 0.3 * a["vel"], seed=SEED + int(round(e.t * 1000)) * 13,
                                 t60=0.5, damp_at=0.06)
    return V1.event_job(e)


def flute_line(notes: list, seed: int, breath: float = 0.5) -> list[tuple[float, np.ndarray]]:
    """[(start, mono)] for a lead line [(t, dur, midi, vel)]: tongued, hard-blown flute notes."""
    g = rng(seed)
    shift = -12.0 if max(m for _, _, m, _ in notes) > FLUTE_TOP else 0.0
    out = []
    for i, (t, d, m, v) in enumerate(notes):
        long = d >= 0.5
        x = breath_flute(m + shift, d * 0.92 + 0.02, 0.45 + 0.5 * v, seed=seed + 5 * i, breath=breath,
                         scoop_cents=30.0 if long else 8.0, vib_cents=9.0 if d >= 0.9 else 0.0, vib_rate=5.6,
                         swell=0.15 if d >= 1.4 else 0.0, attack=0.025, release=0.08 if not long else 0.16,
                         beta=0.62)
        out.append((t - FLUTE_PRE + float(g.normal(0, 0.003)), x))
    return out


def lead_bus(x: np.ndarray) -> np.ndarray:
    """Presence and v1's ping-pong 3/16 delay (taken from v1's lead bus, without its drive)."""
    y = filt(x, [bq_highpass(220, 0.7), bq_peak(2200, 2.5, 1.0), bq_lowpass(9500, 0.7)])
    return V1.lead_bus(y * 0.8) / 0.8


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    events, phrases = V1.build_events()
    events = _reorchestrate(events)
    mx = LoopMixer(intro_s=2 * V1.BAR, loop_s=V1.LOOP_BARS * V1.BAR, intro_tail_s=6.0)
    # Bus gains from measured bus loudness, relative to the lead: drums -4 LU, twin lead -4, kotekan and its
    # doubling -8, stabs -7, tak -11, bass -6, jingles -12, gong -14, kettle -16 (see render(stats=...)["bus_lufs"]).
    mx.bus("drums", -5.2, send=0.12, process=V1.drum_bus)
    mx.bus("jingle", 3.0, send=0.10)
    mx.bus("gong", -17.2, send=0.30)
    mx.bus("kettle", -9.9, send=0.20)
    mx.bus("bass", -3.8, send=0.0, process=V1.bass_bus)
    mx.bus("stab", -8.3, send=0.25)
    mx.bus("tak", 4.7, send=0.08, process=lambda x: filt(x, [bq_highpass(140, 0.7), bq_lowpass(4500, 0.7)]))
    mx.bus("metal", -4.5, send=0.28)
    mx.bus("metal_lead", -2.6, send=0.30)
    mx.bus("lead", -0.7, send=0.22, process=lead_bus)
    mx.bus("lead2", -3.6, send=0.22, process=lead_bus)

    rendered = render_jobs([event_job(e) for e in events], workers=1)
    intro_offset = -(V1.INTRO_BARS[0] - 1) * V1.BAR
    for e, x in zip(events, rendered):
        mx.add(e.bus, x, e.t, pan=e.pan)
        if e.bar in V1.INTRO_BARS:
            mx.add(e.bus, x, e.t + intro_offset, pan=e.pan, part="intro")
    for k, (bus, notes) in enumerate(phrases):
        for t, x in flute_line(notes, SEED + 977 * k, breath=0.5 if bus == "lead" else 0.42):
            mx.add(bus, x, t, pan=-0.15 if bus == "lead" else 0.3)

    room = ModFDNReverb(rt60=1.7, rt60_high=0.7, predelay=0.018, size=0.85, mod_depth=8.0, mod_rate=0.6,
                        early_level=0.35, seed=SEED % 9973)
    intro, loop = mx.render(reverb=room, reverb_return_db=-3.0)
    rep: dict = {}
    intro, loop = master_loop(intro, loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    y = np.concatenate([intro, loop])
    S, L = len(intro), len(loop)
    write_ogg(out_path, y, quality=3.5, tags={"LOOPSTART": str(S), "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, S, L, V1.BPM, 4,
                       extra={"intro_bars": 2, "loop_bars": V1.LOOP_BARS})
    m = measure(y)
    if stats is not None:
        stats["splice_residual_db"] = mx.splice_residual_db
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"battle_standard_v2: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  loop {S}+{L}  splice {mx.splice_residual_db:.1f} dB  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
