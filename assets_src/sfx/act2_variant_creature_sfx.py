"""Act II's variant creatures, each with its own voice (M4-AUD-1001; ADR 0204 §2; plain git, ADR 0175).

The Act II audit (tools/audio/act1_audio_audit.py --act 2, "Enemies") found four foes borrowing their parent's set at
another pitch (M3-AUD-849): their models reuse the parent's rig, so the sounds did too. Each now has its own set,
built from its parent family's synthesis in creature_sfx.py (imported: the same building blocks, so the families stay
families) at its own size and pitch, with a layer of its own material on every event:

    root_crab      Ch10: a bark-and-root reef crab, heavier. The crab's shell and gait, lower, with wet bark creaking
                   on each move and a drip of tannin water off it.
    fen_leech      Ch10: a longer, ribbon-flat sail leech. The leech's flap and bite, slower and lower, through brown
                   fen water (a slosh under the flap).
    scree_crawler  Ch12: a scree shell. The tortoise's plod and grind, a little higher, with loose snow crunch and grit
                   on each step and hit. ADR 0204 §2: no frost and no ice from Ch12 to Ch15, so snow and grit only.
    rim_crawler    Ch16: a bleached, chalky tide crawler. The crawler's shell and spawn voice, drier: chalk ticks on its
                   legs and a dusty scrape.

Synthesized here and in tools/audio/synth/ (SPEC §2, §9). Files are assets/audio/act2/sfx/creatures/<id>_<event>_<n>.ogg
(mono, q4), at creature_sfx.py's targets: voices -18 LUFS momentary max, idles -20, movement -21. Regular counts:
idle 1, attack 2, hurt 2, death 1, move 2.

Render:  python3 tools/audio/render_all.py --only act2_variant_creature_sfx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import creature_sfx as C  # noqa: E402
from field_ambience import modal, stick_slip  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.water import drip  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "act2", "sfx", "creatures")
SEED = 20262100
VARIANTS: dict[str, dict] = {
    "root_crab": dict(family="crab", size=1.2, pitch=0.82, legs=3),
    "fen_leech": dict(family="leech", size=1.3, pitch=0.86, spawn=True),
    "scree_crawler": dict(family="tortoise", size=1.3, pitch=1.1),
    "rim_crawler": dict(family="crab", size=1.1, pitch=0.95, legs=4, spawn=True),
}
TP_MAX = -1.8                     # true peak margin under the -1 dBTP rule, Vorbis overshoot included
COUNTS = {"idle": 1, "attack": 2, "hurt": 2, "death": 1, "move": 2}


def _len(x: np.ndarray, sec: float) -> np.ndarray:
    return np.concatenate([x, np.zeros(max(0, int(sec * SR) - len(x)))])


def bark(g) -> np.ndarray:
    """Wet bark creaking on a root."""
    return stick_slip(g, float(g.uniform(0.12, 0.22)), 60.0, 200.0, [(420.0, 1.0), (980.0, 0.5)], q=6.0)


def tannin(g) -> np.ndarray:
    """Brown fen water moved: a low slosh."""
    n = int(0.4 * SR)
    t = np.arange(n) / n
    return filt(g.standard_normal(n), [bq_bandpass(380, 0.8)]) * np.sin(np.pi * t) ** 1.5


def snow_grit(g) -> np.ndarray:
    """Loose snow crunching with grit in it."""
    n = int(0.25 * SR)
    y = np.zeros(n)
    for _ in range(int(g.integers(30, 60))):
        s = int(g.uniform(0, n - 60))
        y[s: s + 40] += filt(g.standard_normal(40), [bq_bandpass(float(g.uniform(1500, 5000)), 1.2)]) * float(g.uniform(0.2, 1.0))
    return filt(y * np.linspace(1, 0.3, n), [bq_lowpass(4500, 0.7)])    # crunch, not clicks: keeps the peaks down


def chalk(g) -> np.ndarray:
    """Chalky, bleached shell ticking: dry, short, dusty."""
    f = float(g.uniform(2600, 3800))
    x = modal([f, f * 1.9], [0.006, 0.004], [1.0, 0.4], 0.05, g, click=0.6)
    n = int(0.12 * SR)
    dust = filt(g.standard_normal(n), [bq_bandpass(4500, 0.8)]) * np.linspace(1, 0, n) ** 2 * 0.3
    return _len(x, 0.12) + dust


MATERIAL = {"root_crab": bark, "fen_leech": tannin, "scree_crawler": snow_grit, "rim_crawler": chalk}


def event_fn(cid: str, event: str, v: int, seed: int):
    p = VARIANTS[cid]
    fam = C.FAMILIES[p["family"]]

    def fn() -> np.ndarray:
        g = rng(seed)
        x = getattr(fam, event)(p, v, g)
        layer = MATERIAL[cid](g)
        at = 0.0 if event in ("move", "idle") else float(g.uniform(0.05, 0.15))
        if cid == "root_crab" and event in ("move", "idle"):
            d = drip(0.4, 2.2, seed=seed + 3)
            layer = layer + 0.4 * np.concatenate([d, np.zeros(max(0, len(layer) - len(d)))])[: len(layer)]
        out = np.zeros(max(len(x), int(at * SR) + len(layer)))
        out[: len(x)] += x
        s = int(at * SR)
        out[s: s + len(layer)] += 0.45 * layer
        if cid == "fen_leech":
            out = filt(out, [bq_lowpass(5000, 0.7)])                     # through brown water
        return C.room(out, seed + 7, mix=0.1, tail=0.3, rt60=0.7)
    return fn


def build() -> dict:
    out: dict = {}
    for ci, cid in enumerate(VARIANTS):
        word_of = C.MOVE_WORD[VARIANTS[cid]["family"]]
        for ei, (event, count) in enumerate(COUNTS.items()):
            word = word_of if event == "move" else event
            for v in range(count):
                out[f"{cid}_{word}_{v + 1}"] = (event_fn(cid, event, v, SEED + 1000 * ci + 100 * ei + v), C.target(event))
    return out


SFX = build()
FILES = [name + ".ogg" for name in SFX]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, (fn, tgt) in SFX.items():
        x = C.finish(fn(), tgt)
        if measure(x)["true_peak_dbtp"] > TP_MAX:          # an inter-sample overshoot: limit lower, keep the loudness
            for _ in range(4):
                x = normalize_momentary(x, tgt, ceiling_db=C.CEILING - 1.5)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=C.QUALITY)
        res[name] = measure(x)
        if verbose:
            print(f"{name}: {res[name]['seconds']:.2f}s  Mmax {res[name]['momentary_max_lufs']:.2f}", flush=True)
    return res


if __name__ == "__main__":
    render()
