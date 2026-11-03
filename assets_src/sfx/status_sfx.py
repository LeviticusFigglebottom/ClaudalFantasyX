"""Status effects you can hear (M3-AUD-866; the human's playtest FAST-TRACK 3, 11-03: "status effects must be
OBVIOUS"; and FAST-TRACK 5's revive). One apply cue per status in statuses.json, so the ear names the status as the
eye does; a cure, a buff wearing off, and the revive.

Original sound design for this project (SPEC §2, §9), synthesized here and in tools/audio/synth/ with
battle_sfx.py's helpers (imported). No samples, no melody: a cue is at most two or three notes of an open interval.

The grammar, so a player learns it once:
* **harmful** statuses sink: their tones glide or step DOWN, dull (low-passed), and each has its own material;
* **beneficial** statuses rise: tones step UP, bright glass and metal;
* the **breaks** share one crack, then their own material falls (armor: iron; mental: glass; power: a dull body;
  magic: sparks guttering out);
* the **cure** lifts (an airy rise to a clear fifth), the **fade** (a buff ending) is a quiet falling glass, and the
  **revive** swells up from a heartbeat to an open fifth on glass and bell.

    poison        wet bubbles and a sickly tritone dyad sliding down
    sleep         two soft, dark glass notes falling a fourth, a breath under them
    silence       a breath-tone cut off by a closing filter, a muffled knock
    darkness      ink: low noise swirling down over a low drone
    petrify       stone grinding, then a hard stone knock
    slow          a pulse decelerating and dropping in pitch (a slowing tape)
    haste         a pulse accelerating and rising, bright ticks
    stop          two clock ticks, then a held, frozen glass shimmer cut dead
    berserk       a low growl and a drum hit
    confuse       two glass tones wobbling against each other
    doom          a low, dark bell toll
    zombie        a hollow breath in over a minor-second drone
    shell         a cool glass bloom rising
    protect       a bright metal ring with a rising swish
    reflect       a high mirror shimmer (a reversed swell into a glass strike)
    regen         root, fifth, octave on soft glass, rising
    armor_break   the crack, an iron clank falling
    mental_break  the crack, glass splintering down
    power_break   the crack, a dull body thump sinking
    magic_break   the crack, sparks guttering out
    provoke       two hard knocks and a short low bark
    status_cure   an airy rise to a clear fifth
    status_fade   a quiet falling glass
    revive        a heartbeat, a swell, an open fifth on glass and bell

assets/audio/sfx/battle/status_<id>.ogg, status_cure.ogg, status_fade.ogg, revive.ogg (mono, q4; plain git, not an
LFS path): -20 LUFS momentary max (the quiet layer under the hit; targets.py `sfx/battle/*.ogg`), the fade -21, the revive -18.

Render:  python3 tools/audio/render_all.py --only status_sfx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import battle_sfx as B  # noqa: E402
from synth.drums import big_drum  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, midi_to_hz, rng, smooth_noise  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.score import n  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "battle")
SEED = 20261866
STATUS_LUFS = -20.0
REVIVE_LUFS = -18.0
CEILING = -2.0
QUALITY = 4.0


def _N(sec: float) -> int:
    return B._n(sec)


def _env_glide(N: int, f0: float, f1: float, curve: float = 1.0) -> np.ndarray:
    return B._sine_glide(N, f0, f1, curve)


def _glass_note(name: str, dur: float, g, t60: float = 1.0, attack: float = 0.006) -> np.ndarray:
    return B._glass(midi_to_hz(n(name)), dur, g, attack=attack, t60=t60)


def _crack(g, N: int) -> np.ndarray:
    """The breaks' shared crack: a short snapped burst, bright then gone."""
    k = _N(0.06)
    x = np.zeros(N)
    burst = filt(B._noise(g, k), [bq_highpass(1200, 0.7), bq_lowpass(7000, 0.7)]) * B._decay(k, 0.012)
    B._place(x, burst, 0.0)
    B._place(x, 0.6 * B._crackle(g, _N(0.12), 300, 0.04, f_band=4200, q=1.1), 0.005)
    return x


# --------------------------------------------------------------------------- harmful: they sink


def poison(g):
    N = _N(1.1)
    t = B._t(N)
    bub = B._bubbles(g, N, 14, 1.2, 2.0, 0.0, 0.75, amp=0.8, grow=2.5)    # later bubbles bigger: lower
    x = 0.8 * filt(bub, [bq_lowpass(2400, 0.7)]) * np.exp(-t / 0.6)
    dyad = _env_glide(N, 520, 260, 0.7) + 0.7 * _env_glide(N, 520 * 2 ** 0.5, 260 * 2 ** 0.5, 0.7)
    x += 0.55 * filt(dyad, [bq_lowpass(1100, 0.7)]) * B._swell(N, 0.12, 1.5, 0.6)
    return x


def sleep(g):
    N = _N(1.4)
    x = np.zeros(N)
    B._place(x, 0.7 * _glass_note("E5", 1.2, g, t60=1.4, attack=0.03), 0.0)
    B._place(x, 0.6 * _glass_note("B4", 1.0, g, t60=1.6, attack=0.03), 0.38)
    breath = filt(B._noise(g, N), [bq_bandpass(700, 0.6), bq_lowpass(1500, 0.7)]) * B._swell(N, 0.5, 2.0, 0.4)
    return filt(x, [bq_lowpass(2500, 0.7)]) + 0.25 * breath


def silence(g):
    N = _N(0.8)
    t = B._t(N)
    tone = (np.sin(2 * np.pi * 660 * t) + 0.4 * np.sin(2 * np.pi * 990 * t)) * B._swell(N, 0.08, 1.0, 1.0)
    breath = filt(B._noise(g, N), [bq_bandpass(1400, 0.7)]) * 0.3
    body = (tone + breath) * np.clip(1.0 - (t - 0.22) / 0.06, 0.0, 1.0)     # shut at 0.22 s
    x = B._sweep_band(body, 3000, 300, q=0.8, steps=16)
    x += 0.5 * B._thump(110, 60, 0.06, N, g, click=0.1) * (t >= 0.0)
    return x


def darkness(g):
    N = _N(1.2)
    swirl = B._sweep_band(B._noise(g, N), 1800, 120, q=2.5, steps=20) * B._swell(N, 0.2, 1.5, 0.45)
    drone = filt(_env_glide(N, 98, 82, 1.0), [bq_lowpass(300, 0.7)]) * B._swell(N, 0.25, 1.5, 0.5)
    return 0.8 * swirl + 0.6 * drone


def petrify(g):
    N = _N(1.0)
    t = B._t(N)
    grind = filt(B._noise(g, N), [bq_bandpass(700, 1.2), bq_lowpass(2200, 0.7)])
    grind *= (0.6 + 0.4 * np.abs(smooth_noise(N, 40, g))) * np.clip(t / 0.5, 0, 1) * (t < 0.6)
    x = 0.6 * grind + 0.4 * B._crackle(g, N, 160, 0.0, f_band=2500, q=1.0) * (t < 0.6)
    k = _N(0.25)
    knock = B._thump(240, 120, 0.05, k, g, click=0.9)
    B._place(x, 1.1 * knock, 0.6)
    return x


def _pulse_train(times: list[float], freqs: list[float], N: int, g, dur: float = 0.05) -> np.ndarray:
    x = np.zeros(N)
    for t0, f in zip(times, freqs):
        k = _N(dur)
        tt = B._t(k)
        B._place(x, np.sin(2 * np.pi * f * tt) * np.exp(-tt / (dur / 3)), t0)
    return x


def slow(g):
    N = _N(1.3)
    times, t, gap = [], 0.0, 0.07
    while t < 1.05:
        times.append(t)
        t += gap
        gap *= 1.22
    freqs = [880 * 0.88 ** i for i in range(len(times))]
    x = _pulse_train(times, freqs, N, g, dur=0.08)
    x += 0.35 * filt(_env_glide(N, 440, 180, 0.6), [bq_lowpass(900, 0.7)]) * B._swell(N, 0.05, 1.0, 0.5)
    return x


def haste(g):
    N = _N(0.9)
    times, t, gap = [], 0.0, 0.16
    while t < 0.75:
        times.append(t)
        t += gap
        gap = max(0.03, gap * 0.78)
    freqs = [700 * 1.09 ** i for i in range(len(times))]
    x = _pulse_train(times, freqs, N, g, dur=0.04)
    x += 0.25 * filt(B._noise(g, N), [bq_highpass(5000, 0.7)]) * B._swell(N, 0.7, 2.0, 0.1)
    return x


def stop(g):
    N = _N(1.2)
    x = np.zeros(N)
    for i, t0 in enumerate((0.0, 0.25)):
        k = _N(0.05)
        tick = filt(B._noise(g, k), [bq_bandpass(2600 - 400 * i, 4.0)]) * B._decay(k, 0.006)
        B._place(x, 0.9 * tick, t0)
    t = B._t(N)
    hold = sum(np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) for f in (1760.0, 2637.0, 3520.0))
    hold *= np.clip((t - 0.5) / 0.03, 0, 1) * (t < 1.0)                     # frozen: no decay, cut dead
    return x + 0.12 * hold


def berserk(g):
    N = _N(0.9)
    t = B._t(N)
    growl = filt(B._noise(g, N), [bq_bandpass(260, 2.0), bq_bandpass(520, 1.0)])
    growl *= (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t)) * B._swell(N, 0.2, 1.5, 0.3)
    x = 1.4 * growl
    B._place(x, 0.8 * big_drum(0.8, variant=3, seed=SEED + 40)[: N], 0.18)
    return x


def confuse(g):
    N = _N(1.2)
    t = B._t(N)
    a = np.sin(2 * np.pi * np.cumsum(880 * 2 ** (40 * np.sin(2 * np.pi * 5.0 * t) / 1200)) / SR)
    b = np.sin(2 * np.pi * np.cumsum(932 * 2 ** (-40 * np.sin(2 * np.pi * 4.3 * t) / 1200)) / SR)
    return 0.5 * (a + b) * B._swell(N, 0.1, 1.0, 0.5)


def doom(g):
    x = B._bell_partials(midi_to_hz(n("D2")), 2.0, g, t60=3.0, bright=0.4)
    return filt(x, [bq_lowpass(1500, 0.7)])


def zombie(g):
    N = _N(1.2)
    t = B._t(N)
    breath = filt(B._noise(g, N), [bq_bandpass(500, 1.5), bq_bandpass(1100, 2.0)]) * B._swell(N, 0.6, 2.0, 0.2)
    drone = (np.sin(2 * np.pi * 147 * t) + np.sin(2 * np.pi * 156 * t)) * B._swell(N, 0.4, 1.5, 0.5)
    return 0.9 * breath + 0.35 * filt(drone, [bq_lowpass(600, 0.7)])


# --------------------------------------------------------------------------- beneficial: they rise


def shell(g):
    N = _N(1.1)
    x = np.zeros(N)
    for i, nm in enumerate(("D6", "A6", "D7")):
        B._place(x, (0.6 - 0.1 * i) * _glass_note(nm, 0.9, g, t60=1.6, attack=0.12), 0.09 * i)
    return x * B._swell(N, 0.25, 1.2, 0.6)


def protect(g):
    N = _N(1.1)
    x = 0.6 * B._bell_partials(midi_to_hz(n("E5")), 1.1, g, t60=1.2, bright=1.4)
    swish = B._sweep_band(B._noise(g, N), 600, 5000, q=1.5, steps=16) * B._swell(N, 0.12, 2.0, 0.08)
    return x + 0.4 * swish


def reflect(g):
    N = _N(1.0)
    x = np.zeros(N)
    sw = _glass_note("B6", 0.3, g, t60=0.8)[::-1]                          # the reversed swell into the strike
    B._place(x, 0.5 * sw, 0.0)
    B._place(x, 0.7 * _glass_note("B6", 0.7, g, t60=0.9), 0.3)
    B._place(x, 0.4 * _glass_note("F#7", 0.6, g, t60=0.7), 0.31)
    return x


def regen(g):
    N = _N(1.2)
    x = np.zeros(N)
    for i, nm in enumerate(("G5", "D6", "G6")):
        B._place(x, (0.6 - 0.1 * i) * _glass_note(nm, 0.8, g, t60=1.2, attack=0.02), 0.14 * i)
    return x


# --------------------------------------------------------------------------- the breaks


def armor_break(g):
    N = _N(1.0)
    x = _crack(g, N)
    B._place(x, 0.5 * filt(B._bell_partials(midi_to_hz(n("C4")), 0.9, g, t60=0.8, bright=1.2,
                                            glide_cents=-200), [bq_lowpass(4000, 0.7)]), 0.03)
    return x


def mental_break(g):
    N = _N(1.0)
    x = _crack(g, N)
    for i, nm in enumerate(("E6", "B5", "F5")):
        B._place(x, 0.4 * _glass_note(nm, 0.5, g, t60=0.5), 0.04 + 0.09 * i)
    return x


def power_break(g):
    N = _N(1.0)
    x = _crack(g, N)
    B._place(x, 1.0 * B._thump(160, 50, 0.18, _N(0.7), g, click=0.4), 0.03)
    return x


def magic_break(g):
    N = _N(1.1)
    t = B._t(N)
    x = _crack(g, N)
    sparks = B._crackle(g, N, 900, 0.0, f_band=5000, q=0.9) * np.exp(-t / 0.35)
    fizz = B._sweep_band(B._noise(g, N), 6000, 900, q=2.0, steps=16) * B._swell(N, 0.04, 1.0, 0.4)
    return x + 0.8 * sparks + 0.3 * fizz


def provoke(g):
    N = _N(0.9)
    x = np.zeros(N)
    for i, t0 in enumerate((0.0, 0.14)):
        B._place(x, 0.9 * B._thump(300 - 60 * i, 140, 0.03, _N(0.15), g, click=1.0), t0)
    t = B._t(_N(0.4))
    bark = sum((k ** -0.9) * np.sin(2 * np.pi * 110 * k * t) for k in range(1, 18))
    bark = filt(bark, [bq_bandpass(600, 0.9)]) * B._swell(len(t), 0.05, 1.0, 0.12)
    B._place(x, 0.5 * bark, 0.3)
    return x


# --------------------------------------------------------------------------- cure, fade, revive


def status_cure(g):
    N = _N(1.1)
    air = B._sweep_band(B._noise(g, N), 400, 6000, q=1.2, steps=20) * B._swell(N, 0.35, 2.0, 0.2)
    x = 0.4 * air
    B._place(x, 0.6 * _glass_note("D6", 0.8, g, t60=1.2), 0.28)
    B._place(x, 0.5 * _glass_note("A6", 0.7, g, t60=1.1), 0.36)
    return x


def status_fade(g):
    N = _N(0.9)
    x = np.zeros(N)
    B._place(x, 0.5 * _glass_note("A5", 0.7, g, t60=0.9, attack=0.02), 0.0)
    B._place(x, 0.4 * _glass_note("D5", 0.7, g, t60=0.9, attack=0.02), 0.14)
    return filt(x, [bq_lowpass(4000, 0.7)])


def revive(g):
    N = _N(2.0)
    x = np.zeros(N)
    for i, t0 in enumerate((0.0, 0.32)):                                   # the heartbeat
        B._place(x, (0.9 - 0.3 * i) * B._thump(70, 45, 0.09, _N(0.3), g, click=0.1), t0)
    swell = B._sweep_band(B._noise(g, _N(1.0)), 300, 4000, q=1.0, steps=20) * B._swell(_N(1.0), 0.9, 2.5, 0.08)
    B._place(x, 0.5 * swell, 0.3)
    for nm, a in (("A5", 0.6), ("E6", 0.5)):
        B._place(x, a * _glass_note(nm, 1.0, g, t60=1.6), 1.2)
    B._place(x, 0.35 * B._bell_partials(midi_to_hz(n("A4")), 0.8, g, t60=1.4, bright=1.0), 1.2)
    return x


APPLY = {
    "poison": poison, "sleep": sleep, "silence": silence, "darkness": darkness, "petrify": petrify, "slow": slow,
    "haste": haste, "stop": stop, "berserk": berserk, "confuse": confuse, "doom": doom, "zombie": zombie,
    "shell": shell, "protect": protect, "reflect": reflect, "regen": regen, "armor_break": armor_break,
    "mental_break": mental_break, "power_break": power_break, "magic_break": magic_break, "provoke": provoke,
}
SFX: dict = {f"status_{k}": (fn, STATUS_LUFS) for k, fn in APPLY.items()}
SFX.update({"status_cure": (status_cure, STATUS_LUFS), "status_fade": (status_fade, STATUS_LUFS - 1.0),
            "revive": (revive, REVIVE_LUFS)})
FILES = [name + ".ogg" for name in SFX]


def finish(x: np.ndarray, target: float, seed: int) -> np.ndarray:
    x = filt(x, [bq_highpass(35, 0.7)])
    x = B._tail_fade(B._room(x, 0.9, 0.18, seed, predelay=0.012, size=0.6, high=6000, tail=0.4), 0.06)
    for _ in range(4):  # a peaky transient loses level in the limiter: go again until the target holds
        x = normalize_momentary(x, target, ceiling_db=CEILING)
    return x


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for i, (name, (fn, tgt)) in enumerate(SFX.items()):
        x = finish(fn(rng(SEED + 100 * i)), tgt, SEED + 100 * i + 1)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=QUALITY)
        res[name] = measure(x)
        if verbose:
            m = res[name]
            print(f"{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  peak {m['sample_peak_dbfs']:.2f}")
    return res


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT_DIR)
