"""`cinder_matron`: the Cinder Matron boss (M3-AUD-09; act_outline Ch5): two synchronized stems, a 67.2 s loop.

Original composition for this project (SPEC §2, §9). The copper-chime theme, the fire counter-line, the anvil
ostinato and the 2+2+3 bass below were written for this fight and are not derived from any existing melody. The
brief: Ashcrown, a stair-mountain of dark volcanic stone with copper veins and an ash plume; its temple guardian, a
magma-crusted construct, fought in two phases. The fight introduces Kerrid's armour-breaking: in phase 1 the
Matron is all crust (stone, copper, a limping mechanical gait); in phase 2 the crust is broken and the fire inside
shows.

D Phrygian dominant (D Eb F# G A Bb C: the flat second of the Drownbell's Phrygian, but with a major third, so it
reads as heat rather than water), 7/8 grouped 2+2+3 at 300 eighths a minute (a bar is 1.4 s), 48 bars. The uneven
bar is the construct's gait: two short steps and a long one.

**Stem 1** (`cinder_matron_p1.ogg`, the Crust; plays from the start):
* the theme on a copper chime: tuned kettle gongs (synth.gongs) struck as a melody, doubled an octave up by a
  hard metallophone (A: bars 9-16, B: 17-24, A: 33-40, B': 41-48);
* the anvil: a hard, hand-damped high bar on each group of the 2+2+3, the heaviest on the long group;
* a fingered bass in the same 2+2+3; frame drums and a big drum on the groups;
* the temple: a low men's hum on D and A (the fifth) in the intro and the breakdown; a large gong at bars 1, 25.

**Stem 2** (`cinder_matron_p2.ogg`, the Fire; the game fades it in when the crust breaks):
* a hard-blown breath flute, high, with a sustained counter-line over the theme (A, B, A, B');
* the core: a low rumbling noise band that swells in each bar, and magma crackle (short noise pops, denser in the
  loud sections); a sub-bass surge into every section;
* jingles on every eighth, frame-drum slaps filling the short groups, a second big drum on the long group;
* low strings (the saw-ensemble pad, root and fifth, kept low).

Form: 1-8 the forge wakes (anvil, drums, bass; the hum from bar 5) | 9-16 A | 17-24 B | 25-32 breakdown (anvil,
gong, hum; the drums come back from 29) | 33-40 A | 41-48 B', a drum fill in bar 48; its Eb falls to bar 1's D.

Mastering (as the Drownbell): both stems share one gain (the full stack at -16 LUFS) and one limiter gain curve
computed on the full stack (synth.mixer.limit_gain), so stem 1 + stem 2 is exactly the limited mix. Stem 2 is
trimmed so the stack sits about +2 LU over stem 1 alone. Loop: LOOPSTART = 0 on both; equal lengths. The files start a sixteenth before bar 1's downbeat (the sidecars'
`downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/cinder_matron.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum, jingle  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, rng  # noqa: E402
from synth.electric import bass_note  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "music")
OUT = os.path.join(OUT_DIR, "cinder_matron_p1.ogg")
OUT2 = os.path.join(OUT_DIR, "cinder_matron_p2.ogg")
SEED = 20261241
TARGET_LUFS = -16.0
EIGHTHS_PER_MIN = 300.0
E8 = 60.0 / EIGHTHS_PER_MIN          # one eighth note, 0.2 s
BAR_E = 7                            # 7/8
BAR = BAR_E * E8
BARS = 48
LOOP_S = BARS * BAR
GROUPS = (1, 3, 5)                   # the 2+2+3 group starts (eighths, 1-based)
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## the file starts a sixteenth (half an eighth) before bar 1's downbeat, so the wrap seam falls in a quiet sixteenth
## rather than on the loop's heaviest attack (big drum, gong, anvil and bass at once); see render()
LEAD_IN_E = 0.5
## Stem 2's trim at mastering: the Fire lifts the stack about 2 LU over stem 1 alone (measured: render prints both).
STEM2_GAIN_DB = 0.0

CHORDS = (["D", "D", "Eb", "D", "D", "D", "C", "Eb"]
          + ["D", "Eb", "D", "C", "Bb", "C", "Eb", "D"]
          + ["G", "A", "Bb", "A", "G", "Eb", "C", "D"]
          + ["D", "D", "Eb", "Eb", "D", "D", "C", "Eb"]
          + ["D", "Eb", "D", "C", "Bb", "C", "Eb", "D"]
          + ["G", "A", "Bb", "A", "G", "Eb", "C", "Eb"])
SECTION = ["I"] * 8 + ["A"] * 8 + ["B"] * 8 + ["D"] * 8 + ["A2"] * 8 + ["B2"] * 8
ROOT_MIDI = {"D": "D2", "Eb": "Eb2", "C": "C2", "Bb": "Bb1", "G": "G1", "A": "A1"}
FIFTH = {"D": 7, "Eb": 7, "C": 7, "Bb": 7, "G": 7, "A": 6}   # A's fifth in the mode is Eb (a diminished fifth)

## the theme (pitch, eighths); each bar is 7 eighths
THEME_A = [
    [("D5", 2), ("Eb5", 2), ("F#5", 3)],
    [("G5", 2), ("F#5", 2), ("Eb5", 3)],
    [("D5", 2), ("C5", 2), ("D5", 3)],
    [("G4", 4), (None, 3)],
    [("Bb4", 2), ("C5", 2), ("D5", 3)],
    [("Eb5", 2), ("D5", 2), ("C5", 3)],
    [("Bb4", 2), ("A4", 2), ("Bb4", 3)],
    [("D5", 5), (None, 2)],
]
THEME_B = [
    [("G5", 3), ("A5", 2), ("Bb5", 2)],
    [("C6", 2), ("Bb5", 2), ("A5", 3)],
    [("D6", 4), ("C6", 3)],
    [("Bb5", 2), ("A5", 2), ("G5", 3)],
    [("G5", 2), ("A5", 2), ("Bb5", 3)],
    [("Eb6", 4), ("D6", 3)],
    [("C6", 2), ("Bb5", 2), ("A5", 3)],
    [("F#5", 5), (None, 2)],
]
THEME_B2 = THEME_B[:7] + [[("G5", 2), ("F#5", 2), ("Eb5", 3)]]
## stem 2: the fire's counter-line over A and over B
COUNTER_A = [
    [("A5", 7)], [("Bb5", 4), ("A5", 3)], [("F#5", 7)], [("G5", 7)],
    [("F#5", 4), ("G5", 3)], [("A5", 7)], [("Bb5", 4), ("C6", 3)], [("D6", 5), (None, 2)],
]
COUNTER_B = [
    [("D6", 7)], [("C6", 4), ("D6", 3)], [("Bb5", 7)], [("C6", 4), ("A5", 3)],
    [("Bb5", 7)], [("G5", 4), ("Bb5", 3)], [("A5", 7)], [("F#5", 5), (None, 2)],
]


def t_of(bar: int, e: float = 1.0) -> float:
    """Seconds from the loop start to eighth `e` (1-based) of `bar`."""
    return (bar - 1) * BAR + (e - 1) * E8


def add_chime(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
    """The theme on tuned kettle gongs, doubled an octave up by a hard metallophone."""
    g = rng(seed)
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, ee in bar:
            d = ee * E8
            if p is not None:
                v = vel * g.uniform(0.94, 1.04) * (1.06 if ee >= 3 else 1.0)
                x = kettle_gong(n(p), v, seed=seed + int(round(pos * 1000)), t60=1.0 + 0.35 * ee,
                                damp_at=d + 0.12 if ee < 4 else None)
                mx.add("chime", x, pos + float(g.normal(0, 0.003)), pan=-0.1)
                y = metallophone_note(n(p) + 12, 0.45 * v, seed=seed + 7 + int(round(pos * 1000)), decay=2.0,
                                      hardness=0.75, ombak_hz=6.5, damp_at=min(d, 0.45))
                mx.add("chime_metal", y, pos, pan=0.2)
            pos += d


def add_flute(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float, pan: float) -> None:
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, ee in bar:
            d = ee * E8
            if p is None:
                pos += d
                first = True
                continue
            x = breath_flute(n(p), d * 0.95 + 0.02, vel * g.uniform(0.95, 1.04), seed=seed + int(round(pos * 1000)),
                             breath=0.55, scoop_cents=45.0 if first else 15.0, vib_cents=12.0 if ee >= 4 else 4.0,
                             vib_rate=5.8, swell=0.3 if ee >= 7 else 0.0, attack=0.03, release=0.16, beta=0.65)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.003)), pan=pan)
            pos += d
            first = False


def build_p1(mx: LoopMixer) -> None:
    g = rng(SEED)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT_MIDI[ch])
        brk = sec == "D" and bar < 29
        # the anvil: a hard, damped high bar on each group (root, root, fifth), heaviest on the long group
        for k, e in enumerate(GROUPS):
            m = root + 36 + (FIFTH[ch] if k == 2 else 0)
            v = (0.62 if k == 2 else 0.48) * g.uniform(0.93, 1.05)
            x = metallophone_note(m, v, seed=SEED + 100 * bar + e, decay=1.4, hardness=1.0, ombak_hz=7.0,
                                  damp_at=0.09 if k < 2 else 0.22)
            mx.add("anvil", x, t_of(bar, e) + float(g.normal(0, 0.002)), pan=0.35 if k == 1 else -0.25)
        # the bass in 2+2+3 (in the breakdown it holds the root over two bars)
        if not brk:
            for e, dur_e, off, v in ((1, 1.8, 0, 0.85), (3, 1.8, 0, 0.62), (5, 1.2, 12, 0.7), (7, 0.9, 7, 0.5)):
                o = FIFTH[ch] if off == 7 else off
                x = bass_note(root + o, dur_e * E8, v * g.uniform(0.93, 1.05), seed=SEED + 6000 + 10 * bar + e,
                              mute=0.35)
                mx.add("bass", x, t_of(bar, e) + 0.003)
        elif bar % 2 == 1:
            mx.add("bass", bass_note(root, 2 * BAR - 0.1, 0.8, seed=SEED + 6900 + bar, mute=0.0), t_of(bar))
        # drums
        if not brk:
            for e in range(1, BAR_E + 1):
                if e in GROUPS:
                    st, v = "dum", (0.9 if e == 1 else 0.72)
                elif e == 6:
                    st, v = "slap", 0.62
                else:
                    st, v = ("tek" if e % 2 == 0 else "ghost"), 0.4
                mx.add("drums", frame_drum(st, v * g.uniform(0.9, 1.06), variant=bar * 8 + e, seed=SEED + 3),
                       t_of(bar, e) + float(g.normal(0, 0.003)), pan=0.05 if st == "dum" else -0.15)
            mx.add("drums", big_drum(0.9, variant=bar, seed=SEED + 4), t_of(bar, 1))
            if sec in ("A", "B", "A2", "B2") or bar >= 29:
                mx.add("drums", big_drum(0.62, variant=bar + 1, seed=SEED + 4), t_of(bar, 5))
        else:
            mx.add("drums", big_drum(0.7, variant=bar, seed=SEED + 4), t_of(bar, 1))
        if bar == BARS:
            for k, e in enumerate((3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7)):
                mx.add("drums", frame_drum("slap" if k % 2 else "dum", 0.5 + 0.06 * k, variant=k, seed=SEED + 6),
                       t_of(bar, e), pan=0.05)
    # the temple: a low hum on D and its fifth
    for start, line in ((5, [("D3", 4 * BAR - 0.4)]),
                        (25, [("D3", 2 * BAR), ("A2", 2 * BAR), ("D3", 2 * BAR), ("Eb3", 2 * BAR - 0.4)])):
        x = hum_ensemble([(n(p), d) for p, d in line], voices=12, seed=SEED + 70 + start, register="low", spread=0.8)
        env = np.ones(len(x))
        k = int(1.2 * SR)
        env[:k] = np.linspace(0, 1, k) ** 2
        env[-k:] *= np.linspace(1, 0, k) ** 2
        mx.add("hum", x * env[:, None], t_of(start) - 0.1)
    for bar in (1, 25):
        mx.add("gong", large_gong(n("D2"), 0.6, seed=SEED + 80 + bar, t60=8.0), t_of(bar), pan=0.0)
    add_chime(mx, THEME_A, 9, SEED + 100, 0.8)
    add_chime(mx, THEME_B, 17, SEED + 200, 0.85)
    add_chime(mx, THEME_A, 33, SEED + 300, 0.85)
    add_chime(mx, THEME_B2, 41, SEED + 400, 0.9)


def core_rumble(g, sr: int = SR) -> np.ndarray:
    """One bar of the molten core: a low noise band (70-260 Hz) swelling to the long group and falling back."""
    N = int((BAR + 0.4) * sr)
    t = np.arange(N) / sr
    x = filt(g.standard_normal(N), [bq_bandpass(140.0, 0.6, sr), bq_lowpass(300.0, 0.7, sr)], sr=sr)
    x /= np.std(x) + 1e-9
    peak = t_of(1, 5)
    env = np.where(t < peak, (t / peak) ** 1.5, np.exp(-(t - peak) / 0.5))
    env *= np.minimum(1.0, (N - np.arange(N)) / (0.1 * sr))
    return x * env


def crackle(seconds: float, density: float, g, sr: int = SR) -> np.ndarray:
    """Magma crackle: short band-limited pops at `density` per second, scattered."""
    N = int(seconds * sr)
    out = np.zeros(N)
    tt = float(g.exponential(1.0 / density))
    while tt < seconds - 0.05:
        k = int(g.uniform(0.002, 0.008) * sr)
        pop = filt(g.standard_normal(k + 64), [bq_bandpass(g.uniform(1500, 5000), 1.2, sr)], sr=sr)[:k]
        pop *= np.exp(-np.arange(k) / (0.25 * k)) * g.uniform(0.2, 1.0)
        s = int(tt * sr)
        out[s: s + k] += pop[: N - s]
        tt += float(g.exponential(1.0 / density))
    return out


def build_p2(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    for bar in range(1, BARS + 1, 2):
        ch = CHORDS[bar - 1]
        root = n(ROOT_MIDI[ch]) + 12
        x = pad_chord([root, root + FIFTH[ch], root + 12], 2 * BAR - 0.05, 0.85, seed=SEED + 2000 + bar, voices=5,
                      spread_cents=12.0, attack=0.3, release=0.5, width=0.7)
        mx.add("strings", x, t_of(bar) - 0.03)
    for bar, sec in enumerate(SECTION, start=1):
        loud = sec in ("A", "B", "A2", "B2")
        mx.add("core", core_rumble(rng(SEED + 3000 + bar)), t_of(bar), pan=0.0)
        mx.add("crackle", crackle(BAR, 22.0 if loud else 9.0, rng(SEED + 3500 + bar)), t_of(bar), pan=0.0)
        mx.add("crackle", crackle(BAR, 14.0 if loud else 6.0, rng(SEED + 3700 + bar)), t_of(bar), pan=0.6)
        mx.add("crackle", crackle(BAR, 14.0 if loud else 6.0, rng(SEED + 3900 + bar)), t_of(bar), pan=-0.6)
        if sec == "D" and bar < 29:
            continue
        for e in range(1, BAR_E + 1):
            mx.add("jingle", jingle(0.45 if e in GROUPS else 0.3, variant=bar + e, seed=SEED + 5), t_of(bar, e),
                   pan=0.3)
        for e in (2, 4, 6.5):
            mx.add("drums2", frame_drum("slap", 0.55 * g.uniform(0.9, 1.06), variant=bar * 3 + int(e), seed=SEED + 8),
                   t_of(bar, e), pan=0.2)
        mx.add("drums2", big_drum(0.6, variant=bar + 2, seed=SEED + 7), t_of(bar, 6))
        mx.add("drums2", big_drum(0.7, variant=bar + 3, seed=SEED + 7), t_of(bar, 7))
    for start in (1, 9, 17, 25, 33, 41):
        sub_t = np.arange(int(1.4 * SR)) / SR
        sub = np.sin(2 * np.pi * (38.0 + 16.0 * np.exp(-sub_t / 0.35)) * sub_t) * np.exp(-sub_t / 0.6)
        sub *= np.minimum(1.0, sub_t / 0.01)
        mx.add("sub", sub, t_of(start), pan=0.0)
    add_flute(mx, COUNTER_A, 9, SEED + 500, 0.9, 0.12)
    add_flute(mx, COUNTER_B, 17, SEED + 600, 0.92, 0.12)
    add_flute(mx, COUNTER_A, 33, SEED + 700, 0.92, 0.12)
    add_flute(mx, COUNTER_B, 41, SEED + 800, 0.95, 0.12)


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]) for the planned levels below.
GAINS = {
    "chime": 0.0, "chime_metal": 4.2, "anvil": 3.5, "bass": 0.2, "drums": -1.5, "hum": 3.4, "gong": -9.9,
    "flute": 0.8, "strings": 2.3, "core": -20.9, "crackle": -7.0, "jingle": 9.7, "drums2": 0.1, "sub": -11.5,
}
## The plan (LU relative to the stem-1 lead, the copper chime, by each bus's integrated loudness over the loop).
PLAN = {
    "chime": 0.0, "chime_metal": -7.0, "anvil": -8.0, "bass": -6.0, "drums": -4.0, "hum": -9.0, "gong": -12.0,
    "flute": -1.0, "strings": -10.0, "core": -11.0, "crackle": -16.0, "jingle": -13.0, "drums2": -7.0, "sub": -11.0,
}


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 1:
        mx.bus("chime", G["chime"], send=0.3, process=lambda x: filt(x, [bq_highpass(160, 0.7), bq_peak(1800, 2.0, 1.0)]))
        mx.bus("chime_metal", G["chime_metal"], send=0.3)
        mx.bus("anvil", G["anvil"], send=0.2, process=lambda x: filt(x, [bq_highpass(300, 0.7)]))
        mx.bus("bass", G["bass"], send=0.0, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_peak(100, 2.0, 0.9),
                                                                        bq_lowpass(3000, 0.7)]))
        mx.bus("drums", G["drums"], send=0.12, process=lambda x: filt(x, [bq_highpass(32, 0.7),
                                                                           bq_peak(3500, 1.5, 0.8)]))
        mx.bus("hum", G["hum"], send=0.6)
        mx.bus("gong", G["gong"], send=0.4)
    else:
        mx.bus("flute", G["flute"], send=0.22, process=lambda x: filt(x, [bq_highpass(250, 0.7),
                                                                           bq_peak(2600, 2.0, 1.0)]))
        mx.bus("strings", G["strings"], send=0.3, process=lambda x: string_body(x, cutoff=1400.0))
        mx.bus("core", G["core"], send=0.1, process=lambda x: filt(x, [bq_highpass(55, 0.7)]))
        mx.bus("crackle", G["crackle"], send=0.15, process=lambda x: filt(x, [bq_highpass(900, 0.7)]))
        mx.bus("jingle", G["jingle"], send=0.1)
        mx.bus("drums2", G["drums2"], send=0.12)
        mx.bus("sub", G["sub"], send=0.0, process=lambda x: filt(x, [bq_lowpass(120, 0.7)]))


# Levels (LU relative to the copper chime, the stem-1 lead; PLAN above): the chime's metallophone doubling -7, the
# anvil -8, bass -6, drums -4, the hum -9 (over the whole loop; it sounds in the intro and the breakdown), the gong
# -12; in stem 2 the fire flute -1, strings -10, the core rumble -11, crackle -16, jingles -13, the second drums -7,
# sub -11. GAINS were set from a render's measured bus loudness to land these, and confirmed by a second render.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    loops = []
    bus_lufs = {}
    for stem, build in ((1, build_p1), (2, build_p2)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
        _bus_setup(mx, stem)
        build(mx)
        hall = ModFDNReverb(rt60=2.2, rt60_high=0.9, predelay=0.02, size=1.0, mod_depth=8.0, mod_rate=0.5,
                            early_level=0.32, lowcut=110.0, seed=SEED % 9973)
        _, loop = mx.render(reverb=hall, reverb_return_db=-3.0)
        loops.append(loop)
        bus_lufs.update(mx.bus_lufs)
    loops[1] = loops[1] * db_to_lin(STEM2_GAIN_DB)
    # The loop is periodic, so the file may start anywhere; LEAD_IN_E > 0 starts it before bar 1's downbeat.
    lead_in = int(round(LEAD_IN_E * E8 * SR))
    loops = [np.roll(x, lead_in, axis=0) for x in loops]
    full = loops[0] + loops[1]
    gain = db_to_lin(TARGET_LUFS - integrated_lufs(full))
    ctx = int(0.05 * SR)
    L = len(full)
    # one limiter gain curve for both stems, from the full stack (wrap-aware), iterated to the target
    for _ in range(4):
        f = full * gain
        lg = limit_gain(np.concatenate([f[-ctx:], f, f[:ctx]]), -2.0)[ctx: ctx + L]
        cur = integrated_lufs(f * lg[:, None])
        if abs(cur - TARGET_LUFS) < 0.1:
            break
        gain *= db_to_lin(TARGET_LUFS - cur)
    stems = [s * gain * lg[:, None] for s in loops]
    paths = [out_path, os.path.join(os.path.dirname(out_path), os.path.basename(OUT2))]
    extra = {"stems_of": "cinder_matron", "loop_bars": BARS, "meter": "7/8 (bpm counts eighths)"}
    if lead_in:
        extra["downbeat_offset_s"] = lead_in / SR
    for x, p in zip(stems, paths):
        write_ogg(p, x, quality=3.5, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
        write_loop_sidecar(os.path.splitext(p)[0] + ".loop.json", SR, 0, L, EIGHTHS_PER_MIN, BAR_E, extra=extra)
    m = measure(stems[0] + stems[1])
    m1 = measure(stems[0])
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
        stats["stem1_lufs"] = m1["integrated_lufs"]
        stats["limited_fraction"] = float((lg < 0.999).mean())
    if verbose:
        print(f"cinder_matron: {m['seconds']:.2f}s  full {m['integrated_lufs']:.2f} LUFS TP {m['true_peak_dbtp']:.2f} "
              f"dBTP; stem 1 alone {m1['integrated_lufs']:.2f} LUFS; limited {(lg < 0.999).mean() * 100:.2f} %, "
              f"max {-20 * np.log10(max(lg.min(), 1e-9)):.2f} dB")
        lead = bus_lufs["chime"]
        print("  buses (LU vs the chime)", {k: round(v - lead, 1) for k, v in bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
