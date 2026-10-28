"""UI SFX for the UI track's new screens (M3-AUD-832): menu motion, the title's reveal, the save slots, the shrine travel
list and the Reefball HUD.

All synthesized here and in tools/audio/synth/ (SPEC §2, §9: no samples, no recordings, no generated audio), from
menu_sfx.py's helpers and palette (metallophone bars on D-A-E, small glass, soft air, a small room), so these sit in
one set with the menus around them. Mono, 44.1 kHz, Ogg Vorbis q4 (mix.md §5). Rendered at the UI rule's -20 LUFS
momentary max with sample peaks <= -3 dBFS (tools/audio/targets.py "sfx/ui_*.ogg"); the quiet ones are brought down
by their row's volume_db (sfx_ui_screens.json), as ui_map_pan is.

    ui_whoosh_in        a menu page rising into place (MenuMotion's open, 0.18 s): soft air, its band gliding up,
                        no pitch; it sits under the page's own open sound
    ui_whoosh_out       a page sinking away (MenuMotion's close, 0.12 s): shorter, its band gliding down
    ui_title_reveal     the title's opening reveal (TitleReveal, 0.75 s): a low glass bloom as the logo fades in, then
                        a faint shimmer of three bars (D-A-E, rising) as the choices rise, under the title's swell
    ui_save_slot        a save written into its slot: a stylus's short scratch on salt-glass and a bar with a glint
                        an octave up, settled (a mark made, not a fanfare)
    ui_load_slot        a save taken up: air drawn in and down, then two bars falling a fourth (A5 to E5) into a soft
                        low glass hum, the way the tide draws back
    ui_shrine_travel    the party leaving by the shrine network (ShrineTravelMenu): a slow glass arpeggio up D-A-E-A,
                        bound light's chime, over a rising wash of water that thins as the router's fade takes it
    ui_reefball_choices the Reefball choices rising at the player's contact: three small bubbles rising and a soft bar
    ui_reefball_glint   the preview shows a scoring choice under the cursor: one bright small glint, very short
    ui_count_run        the battle result's numbers counting up (BattleResultPanel, count_sec 0.6): a quick run of tiny
                        bar ticks climbing the D-A-E palette and speeding up, like coins told out (M3-AUD-848)
    ui_count_done       the count settled: two soft bars a fifth apart (A5 over D5), let ring
    ui_prompt_in        the field's interact prompt appearing over something you can use: one tiny glass tick (M3-AUD-854)
    ui_interact         using it: a soft touch (a cloth-muffled tap and a faint bar), under whatever it opens

Render:  python3 assets_src/sfx/screen_sfx.py   (or tools/audio/render_all.py --only screen_sfx)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from menu_page_sfx import _bubble, _glass  # noqa: E402
from menu_sfx import _air, _crackle, _env, _place, _room, _sweep_noise, _tail_fade  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.score import n  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
SEED = 83200
UI_TARGET = -20.0
UI_CEILING = -3.0


def _whoosh(g, sec: float, f_from: float, f_to: float, peak_at: float) -> np.ndarray:
    """Air moved by a sliding panel: noise through a gliding band, swelling to peak_at (0..1) and gone by the end."""
    k = int(sec * SR)
    u = np.arange(k) / k
    env = np.where(u < peak_at, (u / peak_at) ** 1.5, ((1 - u) / (1 - peak_at)) ** 2)
    y = _sweep_noise(g, sec, f_from, f_to, 0.9, 12) * env
    return filt(y, [bq_highpass(350, 0.7), bq_lowpass(6000, 0.7)])


def ui_whoosh_in() -> np.ndarray:
    g = rng(SEED + 101)
    return _tail_fade(_whoosh(g, 0.26, 700.0, 2300.0, 0.55), 0.02)


def ui_whoosh_out() -> np.ndarray:
    g = rng(SEED + 201)
    return _tail_fade(_whoosh(g, 0.2, 2000.0, 650.0, 0.35), 0.02)


def ui_title_reveal() -> np.ndarray:
    g = rng(SEED + 301)
    buf = np.zeros(int(1.6 * SR))
    bloom = _glass(midi_to_hz(n("D5")), 1.2, 0.5, g) * _env(int(1.2 * SR), 0.3, 0.45)
    _place(buf, 0.35 * bloom, 0.0)
    _place(buf, 0.006 * _sweep_noise(g, 0.6, 500.0, 1600.0, 0.8, 16) * _env(int(0.6 * SR), 0.35, 0.15), 0.0)
    for i, (note, at) in enumerate((("D6", 0.25), ("A6", 0.36), ("E7", 0.47))):
        _place(buf, (0.18 - 0.03 * i) * metallophone_note(n(note), 0.22, seed=SEED + 302 + i, decay=0.6,
                                                          hardness=0.2, ombak_hz=5.0), at)
    buf = filt(buf, [bq_highpass(200, 0.7), bq_peak(4800, -2.0, 1.0), bq_lowpass(9000, 0.7)])
    return _tail_fade(_room(buf, 0.8, 0.25, SEED + 305), 0.2)


def ui_save_slot() -> np.ndarray:
    g = rng(SEED + 401)
    buf = np.zeros(int(0.9 * SR))
    k = int(0.09 * SR)
    scratch = _crackle(g, 0.09, 30, 360.0, 2500.0, 8000.0) * _env(k, 0.01, 0.04)
    _place(buf, 0.3 * scratch, 0.0)
    _place(buf, metallophone_note(n("A5"), 0.4, seed=SEED + 402, decay=0.55, hardness=0.35, ombak_hz=5.0), 0.07)
    _place(buf, metallophone_note(n("A6"), 0.14, seed=SEED + 403, decay=0.3, hardness=0.3, pair=False), 0.075)
    _place(buf, 0.25 * _glass(midi_to_hz(n("E7")), 0.4, 0.09, g), 0.08)
    buf = filt(buf, [bq_highpass(280, 0.7), bq_lowpass(9000, 0.7)])
    return _tail_fade(_room(buf, 0.5, 0.18, SEED + 404), 0.12)


def ui_load_slot() -> np.ndarray:
    g = rng(SEED + 501)
    buf = np.zeros(int(1.25 * SR))
    _place(buf, 0.03 * _whoosh(g, 0.4, 2400.0, 600.0, 0.4), 0.0)
    _place(buf, metallophone_note(n("A5"), 0.36, seed=SEED + 502, decay=0.5, hardness=0.3, ombak_hz=5.0), 0.2)
    _place(buf, metallophone_note(n("E5"), 0.36, seed=SEED + 503, decay=0.7, hardness=0.3, ombak_hz=5.0), 0.34)
    hum = _glass(midi_to_hz(n("E4")), 0.8, 0.35, g) * _env(int(0.8 * SR), 0.12, 0.3)
    _place(buf, 0.3 * hum, 0.34)
    buf = filt(buf, [bq_highpass(160, 0.7), bq_lowpass(8000, 0.7)])
    return _tail_fade(_room(buf, 0.7, 0.22, SEED + 504), 0.15)


def ui_shrine_travel() -> np.ndarray:
    g = rng(SEED + 601)
    sec = 2.2
    buf = np.zeros(int(sec * SR))
    for i, (note, at) in enumerate((("D5", 0.0), ("A5", 0.14), ("E6", 0.28), ("A6", 0.42))):
        _place(buf, 0.32 * _glass(midi_to_hz(n(note)), 1.2, 0.45, g), at)
        _place(buf, metallophone_note(n(note), 0.18, seed=SEED + 602 + i, decay=0.8, hardness=0.2, ombak_hz=4.5), at)
    k = int(1.6 * SR)
    rise = np.clip(np.arange(k) / (1.1 * SR), 0, 1) ** 2 * _env(k, 1.1, 0.25)
    wash = _sweep_noise(g, 1.6, 300.0, 2600.0, 0.7, 20) * rise
    _place(buf, 0.05 * filt(wash, [bq_lowpass(4000, 0.7)]), 0.2)
    _place(buf, 0.006 * _air(g, 1.0, 0.6, 0.3, 3400.0), 0.5)
    buf = filt(buf, [bq_highpass(180, 0.7), bq_peak(5000, -2.0, 1.0), bq_lowpass(9500, 0.7)])
    return _tail_fade(_room(buf, 1.1, 0.3, SEED + 606), 0.3)


def ui_reefball_choices() -> np.ndarray:
    g = rng(SEED + 701)
    buf = np.zeros(int(0.5 * SR))
    for i, (f, at) in enumerate(((1500.0, 0.0), (1850.0, 0.045), (2300.0, 0.085))):
        _place(buf, (0.2 - 0.03 * i) * _bubble(f, 0.035, g), at)
    _place(buf, metallophone_note(n("D6"), 0.26, seed=SEED + 702, decay=0.35, hardness=0.3, ombak_hz=5.0), 0.1)
    buf = filt(buf, [bq_highpass(350, 0.7), bq_lowpass(8500, 0.7)])
    return _tail_fade(_room(buf, 0.35, 0.12, SEED + 703), 0.06)


def ui_reefball_glint() -> np.ndarray:
    g = rng(SEED + 801)
    buf = np.zeros(int(0.45 * SR))
    _place(buf, 0.5 * _glass(midi_to_hz(n("E7")), 0.4, 0.07, g), 0.0)
    _place(buf, metallophone_note(n("B6"), 0.12, seed=SEED + 802, decay=0.25, hardness=0.4, pair=False), 0.01)
    buf = filt(buf, [bq_highpass(800, 0.7), bq_lowpass(10000, 0.7)])
    return _tail_fade(_room(buf, 0.3, 0.1, SEED + 803), 0.05)


def ui_count_run() -> np.ndarray:
    g = rng(SEED + 901)
    sec = 0.62
    buf = np.zeros(int((sec + 0.25) * SR))
    notes = ["D6", "E6", "A6", "D7", "E7"]
    t, i = 0.0, 0
    while t < sec:
        gap = 0.075 * (1.0 - 0.55 * t / sec)  # the ticks speed up toward the end, as the count eases out
        _place(buf, metallophone_note(n(notes[min(i // 3, len(notes) - 1)]), 0.12, seed=SEED + 902 + i, decay=0.12,
                                      hardness=0.55, pair=False), t)
        t += gap
        i += 1
    buf = filt(buf, [bq_highpass(900, 0.7), bq_lowpass(9500, 0.7)])
    return _tail_fade(_room(buf, 0.3, 0.1, SEED + 903), 0.05)


def ui_count_done() -> np.ndarray:
    g = rng(SEED + 951)
    buf = np.zeros(int(0.9 * SR))
    _place(buf, metallophone_note(n("D5"), 0.32, seed=SEED + 952, decay=0.6, hardness=0.3, ombak_hz=5.0), 0.0)
    _place(buf, metallophone_note(n("A5"), 0.3, seed=SEED + 953, decay=0.6, hardness=0.3, ombak_hz=5.0), 0.02)
    _place(buf, 0.15 * _glass(midi_to_hz(n("A6")), 0.5, 0.12, g), 0.03)
    buf = filt(buf, [bq_highpass(220, 0.7), bq_lowpass(8500, 0.7)])
    return _tail_fade(_room(buf, 0.5, 0.18, SEED + 954), 0.12)


def ui_prompt_in() -> np.ndarray:
    g = rng(SEED + 1001)
    buf = np.zeros(int(0.35 * SR))
    _place(buf, 0.6 * _glass(midi_to_hz(n("E7")), 0.25, 0.04, g), 0.0)
    buf = filt(buf, [bq_highpass(1500, 0.7), bq_lowpass(10000, 0.7)])
    return _tail_fade(_room(buf, 0.25, 0.08, SEED + 1002), 0.04)


def ui_interact() -> np.ndarray:
    g = rng(SEED + 1101)
    buf = np.zeros(int(0.45 * SR))
    tap = _env(int(0.05 * SR), 0.001, 0.012) * filt(g.standard_normal(int(0.05 * SR)), [bq_lowpass(1400, 0.7),
                                                                                          bq_highpass(200, 0.7)])
    _place(buf, 0.06 * tap, 0.0)
    _place(buf, metallophone_note(n("A5"), 0.3, seed=SEED + 1102, decay=0.3, hardness=0.25, pair=False), 0.01)
    buf = filt(buf, [bq_highpass(180, 0.7), bq_lowpass(8000, 0.7)])
    return _tail_fade(_room(buf, 0.3, 0.1, SEED + 1103), 0.05)


UI = {
    "ui_whoosh_in": ui_whoosh_in,
    "ui_whoosh_out": ui_whoosh_out,
    "ui_title_reveal": ui_title_reveal,
    "ui_save_slot": ui_save_slot,
    "ui_load_slot": ui_load_slot,
    "ui_shrine_travel": ui_shrine_travel,
    "ui_reefball_choices": ui_reefball_choices,
    "ui_reefball_glint": ui_reefball_glint,
    "ui_count_run": ui_count_run,
    "ui_count_done": ui_count_done,
    "ui_prompt_in": ui_prompt_in,
    "ui_interact": ui_interact,
}
FILES = [f"{u}.ogg" for u in UI]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    res = {}
    for name, fn in UI.items():
        x = normalize_momentary(fn(), UI_TARGET, ceiling_db=UI_CEILING)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.3f}s  momentary max {m['momentary_max_lufs']:.2f} LUFS  "
                  f"peak {m['sample_peak_dbfs']:.2f} dBFS  true peak {m['true_peak_dbtp']:.2f} dBTP")
    return res


if __name__ == "__main__":
    render()
