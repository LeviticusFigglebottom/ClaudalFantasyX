#!/usr/bin/env python3
"""Objective before/after measurements for M1-AUD-02 (nobody on the agent side can listen).

    python3 tools/audio/measure_quality.py              # piano, reverb, cue files (about 2 min)
    python3 tools/audio/measure_quality.py --voicing    # also split-bus voicing of v1 vs v2 (+2 min)
    python3 tools/audio/measure_quality.py --json out.json

Sections
1. Piano notes: old additive `piano` vs new `grand` (through its soundboard).
   Inharmonicity B fitted blindly from measured partials, against the
   register reference table; early/late decay of the fundamental against
   approximate published ranges; whether decay rate rises with partial
   frequency; centroid trajectory; velocity -> brightness and level.
2. Reverb impulse responses: old 8-line FDN vs new modulated 16-line FDN vs
   an ideal exponentially decaying Gaussian noise (the diffuse-field target).
3. Shipped cue files: LUFS, true peak, loudness range (EBU Tech 3342 style),
   crest factor, stereo correlation, and loop seams.
4. (--voicing) melody vs accompaniment loudness in the Hush theme, v1 and v2.

Reference ranges (approximate, wide on purpose; values from the piano
acoustics literature as remembered, not re-checked against data in this
repo): fundamental *early* decay (0.1-1.0 s) A1 3-10, C3 4-12, C4 6-16,
C5 8-25, C6 12-40, C7 20-70 dB/s; B within 2x of the table in `grand.py`.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth import analysis as A  # noqa: E402
from synth.dsp import SR, fft_convolve, midi_to_hz  # noqa: E402
from synth.grand import grand_note, inharmonicity, soundboard_ir_modal  # noqa: E402
from synth.loudness import _block_powers, _to_lufs, integrated_lufs, momentary_max_lufs, true_peak_dbtp  # noqa: E402
from synth.mixer import read_audio  # noqa: E402
from synth.piano import inharmonicity as old_B  # noqa: E402
from synth.piano import piano_note  # noqa: E402
from synth.reverb import FDNReverb, ModFDNReverb  # noqa: E402

EARLY_RANGE = {33: (3, 10), 48: (4, 12), 60: (6, 16), 72: (8, 25), 84: (12, 40), 96: (20, 70)}
NOTES = (33, 48, 60, 72, 84, 96)


def _board(x: np.ndarray) -> np.ndarray:
    sb = soundboard_ir_modal()
    return fft_convolve(x, sb[:, 0])[: len(x)]


def piano_metrics() -> dict:
    out = {}
    for name in ("old", "new"):
        rows = {}
        for m in NOTES:
            if name == "old":
                x = piano_note(m, 0.55, 10.0, seed=3)
            else:
                x = _board(grand_note(m, 0.55, 10.0, seed=3))
            L = len(x) / SR
            f0 = midi_to_hz(m)
            ref_B = inharmonicity(m)
            fr = A.find_partials(x, f0, old_B(m) if name == "old" else ref_B, 12 if m < 80 else 6, t0=0.05,
                                 length=min(1.0, L - 0.1))
            _, B = A.fit_inharmonicity(fr)
            early = A.decay_rate_db_per_s(x, fr[0], 0.1, min(1.0, L - 0.05)) if np.isfinite(fr[0]) else float("nan")
            late = (A.decay_rate_db_per_s(x, fr[0], 2.0, min(6.0, L - 0.2)) if L > 3.0 and np.isfinite(fr[0])
                    else float("nan"))
            dec = [A.decay_rate_db_per_s(x, fr[k], 0.1, min(1.0, L - 0.05)) for k in range(min(8, len(fr)))
                   if np.isfinite(fr[k])]
            fk = [fr[k] for k in range(min(8, len(fr))) if np.isfinite(fr[k])]
            slope = float(np.polyfit(np.array(fk) / 1000.0, dec, 1)[0]) if len(dec) >= 3 else float("nan")
            hop = int(0.01 * SR)
            fr_rms = np.sqrt([np.mean(x[i:i + hop] ** 2) for i in range(0, len(x) - hop, hop)])
            above = np.nonzero(20 * np.log10(fr_rms / fr_rms.max() + 1e-12) > -60)[0]
            audible = (above[-1] + 1) * hop / SR if len(above) else 0.0
            c = A.spectral_centroid_at(x, [0.03, 1.0])
            lo, hi = EARLY_RANGE[m]
            rows[m] = dict(B=B, B_ratio_to_ref=B / ref_B, early_db_s=early, early_in_range=bool(lo <= early <= hi),
                           late_db_s=late, two_stage=bool(np.isfinite(late) and late < 0.6 * early),
                           decay_slope_db_s_per_khz=slope, audible_s=audible, centroid_30ms=c[0], centroid_1s=c[1],
                           crest_db=A.crest_factor_db(x))
        vel = {}
        for v in (0.2, 0.5, 0.8):
            x = piano_note(60, v, 3.0, seed=3) if name == "old" else _board(grand_note(60, v, 3.0, seed=3))
            vel[v] = dict(centroid_30ms=A.spectral_centroid_at(x, [0.03])[0], mmax_lufs=momentary_max_lufs(x))
        rows["velocity_C4"] = vel
        rows["pp_to_ff_level_db"] = vel[0.8]["mmax_lufs"] - vel[0.2]["mmax_lufs"]
        rows["pp_to_ff_brightness_ratio"] = vel[0.8]["centroid_30ms"] / vel[0.2]["centroid_30ms"]
        out[name] = rows
    return out


def reverb_metrics() -> dict:
    imp = np.zeros((SR * 4, 2))
    imp[0] = 1.0
    g = np.random.default_rng(1)
    t = np.arange(SR * 4) / SR
    ideal = g.standard_normal((len(t), 2)) * np.exp(-6.91 * t / 2.6)[:, None]
    cases = {
        "old FDNReverb (8 lines)": (FDNReverb(rt60=2.6, predelay=0.024, damping=0.32, size=1.1, seed=20261022 % 9973),
                                    sum(FDNReverb.BASE_DELAYS) * 1.1),
        "new ModFDNReverb (16 lines)": (ModFDNReverb(rt60=2.6, rt60_high=1.1, predelay=0.024, seed=20261022 % 9973),
                                        sum(ModFDNReverb.BASE_DELAYS)),
    }
    out = {}
    for name, (rv, total_delay) in cases.items():
        ir = rv.process(imp, tail=0.0)
        out[name] = _ir_stats(ir)
        dens = total_delay / SR
        out[name]["modal_density_per_hz"] = dens
        out[name]["modal_overlap_at_rt60"] = dens * 2.2 / 2.6
    out["ideal diffuse noise"] = _ir_stats(ideal)
    return out


def _ir_stats(ir: np.ndarray) -> dict:
    pk = A.tail_spectral_peakiness(ir)
    return dict(mixing_time_s=A.mixing_time(ir), p99_over_median_db=pk["p99_over_median_db"],
                frac_bins_over_10x=pk["frac_over_10x"], periodicity=A.tail_periodicity(ir),
                kurtosis=A.tail_kurtosis(ir), rt60_500=A.rt60_band(ir, 500), rt60_4k=A.rt60_band(ir, 4000),
                lr_correlation=float(np.corrcoef(ir[4410:, 0], ir[4410:, 1])[0, 1]))


def loudness_range(y: np.ndarray) -> float:
    """EBU Tech 3342-style LRA: short-term (3 s) loudness every 0.5 s, gated, 95th - 10th percentile."""
    p = _block_powers(y, SR, 3.0, 0.5)
    lk = _to_lufs(p)
    p = p[lk > -70]
    rel = _to_lufs(p.mean()) - 20
    lk = _to_lufs(p)
    lk = lk[lk > rel]
    return float(np.percentile(lk, 95) - np.percentile(lk, 10))


def file_metrics() -> dict:
    out = {}
    d = os.path.join(ROOT, "assets", "audio", "music")
    for f in ("hush_theme_sketch.ogg", "hush_theme_v2.ogg", "battle_standard.ogg", "temple_trial.ogg"):
        p = os.path.join(d, f)
        if not os.path.isfile(p):
            continue
        y = read_audio(p)
        row = dict(seconds=len(y) / SR, bytes=os.path.getsize(p), integrated_lufs=integrated_lufs(y),
                   true_peak_dbtp=true_peak_dbtp(y), lra_lu=loudness_range(y), crest_db=A.crest_factor_db(y),
                   lr_correlation=float(np.corrcoef(y[:, 0], y[:, 1])[0, 1]))
        side = os.path.splitext(p)[0] + ".loop.json"
        if os.path.isfile(side):
            with open(side, encoding="utf-8") as fh:
                meta = json.load(fh)
            row["loop"] = dict(meta=meta, seam=A.loop_seam_report(y, meta["loop_start_samples"]))
        out[f] = row
    return out


def voicing_metrics() -> dict:
    """Melody vs accompaniment loudness (LU) in Hush v1 and v2, from split buses."""
    import importlib.util

    def load(name):
        spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "assets_src", "music", name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    out = {}
    v2 = load("hush_theme_v2")
    st: dict = {}
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        v2.render(os.path.join(td, "v2.ogg"), verbose=False, stats=st)
    out["v2_melody_minus_accompaniment_lu"] = st["bus_piano_mel_lufs"] - st["bus_piano_acc_lufs"]
    out["v2_sympathetic_vs_board_db"] = st["sym_ratio_db"]
    lo, hi = st["tempo_bpm_range"]
    out["v2_local_tempo_bpm"] = [lo, hi]
    pedal = st["pedal"]
    out["v2_pedal_lifts"] = int(np.sum((pedal.depth[1:] < 0.5) & (pedal.depth[:-1] >= 0.5)))
    mel = [nt for nt in st["notes"] if nt["role"] == "mel"]
    acc = [nt for nt in st["notes"] if nt["role"] != "mel"]
    out["v2_velocity_mel_mean"] = float(np.mean([nt["vel"] for nt in mel]))
    out["v2_velocity_acc_mean"] = float(np.mean([nt["vel"] for nt in acc]))
    # v1: re-render the sketch's piano events on two buses with the old renderer
    v1 = load("hush_theme_sketch")
    sc = v1.build_score()
    tm = v1.tempo()
    end = tm.t(v1.BARS * 3) + 4.0
    buses = {"mel": np.zeros(int(end * SR)), "acc": np.zeros(int(end * SR))}
    for k, ev in enumerate(sorted(sc.events, key=lambda e: (e.beat, e.inst))):
        if ev.inst != "piano":
            continue
        role = "acc" if (ev.opts.get("lh") or ev.beats == 2.5 or isinstance(ev.pitch, list)) else "mel"
        t0 = tm.t(ev.beat)
        dur = tm.t(ev.beat + ev.beats) - t0
        hold = v1.pedal_release(tm, t0 + dur * 0.95) - t0
        for j, p in enumerate(ev.pitch if isinstance(ev.pitch, list) else [ev.pitch]):
            x = piano_note(p, ev.vel, hold, seed=v1.SEED + 7919 * k + j)
            s = int(t0 * SR)
            e = min(len(buses[role]), s + len(x))
            buses[role][s:e] += x[: e - s]
    out["v1_melody_minus_accompaniment_lu"] = integrated_lufs(buses["mel"]) - integrated_lufs(buses["acc"])
    return out


def _fmt(v):
    if isinstance(v, float):
        return "nan" if math.isnan(v) else f"{v:.3g}"
    return str(v)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--voicing", action="store_true")
    ap.add_argument("--json", default="")
    args = ap.parse_args()
    res = {"piano": piano_metrics(), "reverb": reverb_metrics(), "files": file_metrics()}
    if args.voicing:
        res["voicing"] = voicing_metrics()

    print("== Piano notes (vel 0.55)")
    keys = ("B_ratio_to_ref", "early_db_s", "early_in_range", "late_db_s", "two_stage", "decay_slope_db_s_per_khz",
            "audible_s", "centroid_30ms", "centroid_1s", "crest_db")
    print("model note " + " ".join(f"{k:>14}" for k in keys))
    for name, rows in res["piano"].items():
        for m in NOTES:
            print(f"{name:5} {m:4d} " + " ".join(f"{_fmt(rows[m][k]):>14}" for k in keys))
        print(f"{name:5} C4 pp->ff level {rows['pp_to_ff_level_db']:.1f} dB, brightness x"
              f"{rows['pp_to_ff_brightness_ratio']:.2f}")
    print("\n== Reverb IR (RT60 2.6 s)")
    for name, r in res["reverb"].items():
        print(f"{name:30} " + ", ".join(f"{k} {_fmt(v)}" for k, v in r.items()))
    print("\n== Files")
    for f, r in res["files"].items():
        print(f"{f:24} " + ", ".join(f"{k} {_fmt(v)}" for k, v in r.items() if k != "loop"))
        if "loop" in r:
            print(f"{'':24} loop seam {r['loop']['seam']}")
    if args.voicing:
        print("\n== Voicing")
        for k, v in res["voicing"].items():
            print(f"{k}: {v}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=lambda o: o if not isinstance(o, np.generic) else o.item())
    return 0


if __name__ == "__main__":
    sys.exit(main())
