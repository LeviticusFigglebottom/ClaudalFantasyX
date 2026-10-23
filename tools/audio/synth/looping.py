"""Seamless loop rendering: an optional one-shot intro plus a steady-state loop body.

A loop sounds seamless only if the samples after the loop end are exactly
what the loop start contains: the start must already carry the tails
(ringing notes, reverb) of the loop's own last bars. Rendering "intro + body
+ body" and cutting out the second body works, but costs two extra passes.
`LoopMixer` gets the same steady state directly:

* **Circular placement.** Every loop event is added modulo the loop length,
  so a note that rings past the loop end lands on the loop start.
* **Steady-state bus processing.** Bus processors (filters, convolutions,
  amps) and the reverb run on the loop with its own last seconds prepended
  (wrap-around pre-roll); after the pre-roll the output is the steady state
  (valid when every memory is shorter than the pre-roll). The modulated
  reverb snaps its LFOs to whole cycles per loop, so even its time-varying
  tail is periodic.
* **Intro.** Intro events are rendered linearly. The intro should be the
  loop's own last bars, so that at the splice its tails match what the loop
  start carries; the reverb is phase-aligned to the loop end for the same
  reason. `splice_residual_db` measures what is left: the loop start minus
  a render of the intro followed by an un-wrapped ("cold") loop start.
* **Master.** One gain for both parts (LUFS-normalized over intro + one
  loop), and the limiter runs with wrap-around context on the loop.

The output file is intro + loop; LOOPSTART = len(intro) and LOOPLENGTH =
len(loop) samples, so a player that jumps from the last sample back to
LOOPSTART plays the steady state forever.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import numpy as np

from .dsp import SR, bq_highpass, db_to_lin, filt, pan_mono
from .loudness import integrated_lufs
from .mixer import limit
from .reverb import ModFDNReverb


@dataclass
class LoopBus:
    name: str
    gain_db: float = 0.0
    send: float = 0.0
    process: object = None
    loop: np.ndarray = field(default=None, repr=False)
    intro: np.ndarray = field(default=None, repr=False)


class LoopMixer:
    def __init__(self, intro_s: float, loop_s: float, sr: int = SR, intro_tail_s: float = 6.0,
                 preroll_s: float = 8.0, cold_s: float = 4.0):
        """preroll_s: wrap-around context fed to bus processors and the reverb before the
        steady-state copy (must exceed every processor's memory, e.g. the reverb's RT60).
        cold_s: length of an un-wrapped render of the loop start, used to measure the
        intro-to-loop splice."""
        self.sr = sr
        self.S = int(round(intro_s * sr))
        self.L = int(round(loop_s * sr))
        self.tail = int(intro_tail_s * sr)
        self.pre = min(self.L, int(preroll_s * sr))
        self.C = min(self.L, int(cold_s * sr))
        self.lead = min(self.S, int(0.05 * sr))     # cold buffer starts 50 ms before the loop start
        self.buses: dict[str, LoopBus] = {}
        self.cold: dict[str, np.ndarray] = {}

    def bus(self, name: str, gain_db: float = 0.0, send: float = 0.0, process=None) -> LoopBus:
        b = LoopBus(name, gain_db, send, process, np.zeros((self.L, 2)), np.zeros((self.S + self.tail, 2)))
        self.buses[name] = b
        self.cold[name] = np.zeros((self.C + self.lead, 2))
        return b

    def add(self, bus: str, sig: np.ndarray, start: float, pan: float = 0.0, gain: float = 1.0,
            part: str = "loop") -> None:
        """start: seconds from the loop start (part='loop', wrapped) or from the file start (part='intro')."""
        b = self.buses[bus]
        st = gain * (pan_mono(sig, pan) if sig.ndim == 1 else sig)
        s = int(round(start * self.sr))
        if part == "intro":
            self._add_linear(b.intro, st, s)
            return
        if self.S > 0 and -self.lead <= s < self.C:
            self._add_linear(self.cold[bus], st, s + self.lead)
        s %= self.L
        pos = 0
        while pos < len(st):
            room = self.L - s
            take = min(room, len(st) - pos)
            b.loop[s: s + take] += st[pos: pos + take]
            pos += take
            s = 0

    @staticmethod
    def _add_linear(buf: np.ndarray, st: np.ndarray, s: int) -> None:
        if s < 0:                       # humanized slightly before t = 0
            st, s = st[-s:], 0
        if s >= len(buf):
            return
        e = min(len(buf), s + len(st))
        buf[s:e] += st[: e - s]

    def _steady(self, x: np.ndarray, fn) -> np.ndarray:
        """Steady-state output of a processor with memory < preroll on the periodic signal x."""
        y = fn(np.concatenate([x[self.L - self.pre:], x]))
        return y[self.pre: self.pre + self.L]

    def render(self, reverb: ModFDNReverb | None = None, reverb_return_db: float = 0.0,
               hp_hz: float = 28.0) -> tuple[np.ndarray, np.ndarray]:
        sr = self.sr
        S, C = self.S, self.C
        loop = np.zeros((self.L, 2))
        intro = np.zeros((S + self.tail, 2))
        send_l, send_i = np.zeros_like(loop), np.zeros_like(intro)
        self.bus_lufs = {}
        for b in self.buses.values():
            g = db_to_lin(b.gain_db)
            xl = self._steady(b.loop, b.process) if b.process else b.loop
            # the intro buffer also gets the un-wrapped loop start after S, so the
            # first-play splice is rendered exactly as a player would hear it
            ib = b.intro.copy()
            a0 = S - self.lead
            ib[a0: a0 + C + self.lead] += self.cold[b.name][: len(ib) - a0]
            xi = b.process(ib) if (b.process and S > 0) else ib
            loop += g * xl
            intro += g * xi
            self.bus_lufs[b.name] = integrated_lufs(g * xl, sr) if np.any(xl) else float("-inf")
            if b.send > 0:
                send_l += b.send * g * xl
                send_i += b.send * g * xi
        if reverb is not None:
            ret = db_to_lin(reverb_return_db)
            reverb.loop_period = self.L / sr
            reverb.t_offset = -self.pre / sr
            loop += ret * self._steady(send_l, lambda v: reverb.process(v, tail=0.0)[: len(v)])
            if S > 0:
                reverb.t_offset = (self.L - S) / sr      # intro = the loop's last bars
                intro += ret * reverb.process(send_i, tail=0.0)[: len(intro)]
            reverb.t_offset = 0.0
        hp = [bq_highpass(hp_hz, 0.6, sr)]
        loop = self._steady(loop, lambda v: filt(v, hp, sr=sr))
        intro = filt(intro, hp, sr=sr)
        # splice residual: the loop start versus what really follows the intro
        n = min(int(0.25 * sr), C, self.tail)
        if S > 0 and n > 0:
            d = loop[:n] - intro[S: S + n]
            self.splice_residual_db = float(10 * np.log10((d ** 2).mean() / max((loop[:n] ** 2).mean(), 1e-30)))
        else:
            self.splice_residual_db = float("-inf")
        return intro[:S], loop


def master_loop(intro: np.ndarray, loop: np.ndarray, target_lufs: float, ceiling_db: float = -2.0,
                sr: int = SR, iters: int = 5, report: dict | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Common gain to the LUFS target (measured on intro + one loop) and wrap-aware limiting.

    `report` (optional) receives the limiter's work: max gain reduction (dB)
    and the fraction of samples it touched, measured on the final pass."""
    S, L = len(intro), len(loop)
    ctx = min(L, int(0.05 * sr))
    for _ in range(iters):
        cur = integrated_lufs(np.concatenate([intro, loop]) if S else loop, sr)
        gain = db_to_lin(target_lufs - cur)
        a, b = intro * gain, loop * gain
        lp = limit(np.concatenate([b[-ctx:], b, b[:ctx]]), ceiling_db, sr=sr)[ctx: ctx + L]
        it = limit(np.concatenate([a, b[:ctx]]), ceiling_db, sr=sr)[:S] if S else a
        if report is not None:
            pre = np.concatenate([a, b])
            post = np.concatenate([it, lp])
            ratio = np.abs(post).max(axis=1) / np.maximum(np.abs(pre).max(axis=1), 1e-12)
            touched = ratio < 0.999
            report["max_gain_reduction_db"] = float(-20 * np.log10(max(ratio.min(), 1e-12)))
            report["fraction_limited"] = float(touched.mean())
        intro, loop = it, lp
        if abs(integrated_lufs(np.concatenate([intro, loop]) if S else loop, sr) - target_lufs) < 0.1:
            break
    return intro, loop


def write_loop_sidecar(path_json: str, sr: int, loop_start: int, loop_length: int, bpm: float | None,
                       beats_per_bar: int | None, extra: dict | None = None) -> dict:
    total = loop_start + loop_length
    meta = {
        "sample_rate": sr,
        "loop_start_samples": loop_start,
        "loop_length_samples": loop_length,
        "total_samples": total,
        "loop_offset_seconds": loop_start / sr,
        "loop_length_seconds": loop_length / sr,
        "bpm": bpm or 0,
        "bar_beats": beats_per_bar or 4,
        "beat_count": int(round(loop_length / sr * bpm / 60)) if bpm else 0,
    }
    if extra:
        meta.update(extra)
    os.makedirs(os.path.dirname(path_json), exist_ok=True)
    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, sort_keys=True)
        f.write("\n")
    return meta
