#!/usr/bin/env python3
"""Act I's music by ear's proxy: harshness, mud and monotony (M3-AUD-864, ADR 0041/0042).

ADR 0042 keeps the self-synthesized score and enforces its bar with checks. The loudness, seam, determinism and
transition checks say a cue is technically clean. This report looks at how it sounds over time, from the shipped
file (git lfs pull first), for every music cue an Act I player can hear (zones, battles, cutscene `@music`):

  balance     the share of the cue's energy in six bands: sub <60 Hz, low 60-250, low-mid 250-800 (where mud
              lives), mid 800-2.5k, presence 2.5-6k (where harshness lives) and air >6k
  harsh       presence + air energy against mid, and the loudest 2% of short windows' presence share: a bright
              cue that stings (a hot 3 kHz) shows as both high
  mud         the low-mid share against mid + presence: a thick, unclear middle
  monotony    over the cue's own length, how little it moves: the spread (std) of short-term loudness (3 s) and of
              the spectral centroid (in octaves), and the share of 3 s windows that are near-copies of the one
              before. A long cue that barely moves on all three is flagged
  peaks       true peak (dBTP) and integrated loudness, for the record

The band shares are unweighted power, so a quiet broadband texture (rain, a fire) still claims most of the top bands:
read a harsh flag against the cue's brief, and look at the spectrogram sheet before changing a source. Each figure
is compared with the whole Act I set: a flag means the cue stands out from its own score by the rule's
margin, not that it breaks an absolute law. The weakest cues are revised in their synth sources.

Run: python3 tools/audio/act1_listening_report.py [--md] [--sheets DIR]   (exit 0: a report)"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))

from synth.loudness import integrated_lufs, true_peak_dbtp  # noqa: E402

DATA = ROOT / "game" / "data"
SR = 44100
BANDS = [("sub", 0, 60), ("low", 60, 250), ("lowmid", 250, 800), ("mid", 800, 2500), ("presence", 2500, 6000),
         ("air", 6000, 22050)]
WIN_S = 3.0
# A cue is flagged when it passes the set's median by these margins
HARSH_DB = 4.0        # presence+air over mid, dB above the set's median
MUD_DB = 4.0          # low-mid over mid+presence, dB above the set's median
MONO_SEC = 45.0       # monotony is judged only on cues at least this long
MONO_LOUD_LU = 1.0    # short-term loudness spread under this
MONO_CENT_OCT = 0.12  # centroid spread under this (octaves)
MONO_SAME = 0.6       # share of windows that are near-copies of the one before, over this


def _json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def act1_cues() -> list[str]:
    """Every music cue an Act I player can hear: Act I zones (and their variants), Act I battles, Act I `@music`."""
    music = _json(DATA / "audio" / "music.json")
    out: list[str] = []

    def add(c):
        if c and c != "silence" and c not in out:
            out.append(c)

    for z in music["zones"]:
        if re.search(r"levels/(prologue|ch0[1-9])/", z["scene"]):
            for row in [z] + z.get("variants", []):
                add(row.get("music"))
    add(music["battle"]["default"])
    for enc, c in music["battle"]["encounters"].items():
        if not re.match(r"ch(1[0-9]|2[0-9])_", enc):
            add(c)
    for d in ["prologue"] + [f"ch0{i}" for i in range(1, 10)]:
        for p in sorted((DATA / "dialogue" / d).glob("*.dlg")):
            for m in re.finditer(r"@music\s+([A-Za-z0-9_]+)", p.read_text(encoding="utf-8")):
                add(m.group(1))
    return out


def cue_file(cid: str) -> Path | None:
    row = _json(DATA / "audio" / "music.json")["cues"].get(cid, {})
    files = row.get("stems") or ([row["file"]] if row.get("file") else [])
    return ROOT / files[0].removeprefix("res://") if files else None


def decode(path: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def _spectra(m: np.ndarray, n_fft: int = 4096, hop: int = 2048) -> tuple[np.ndarray, np.ndarray]:
    """Power spectra of `m` (frames x bins) and the bin frequencies."""
    w = np.hanning(n_fft)
    frames = [m[i:i + n_fft] * w for i in range(0, max(1, len(m) - n_fft), hop)]
    spec = np.abs(np.fft.rfft(np.array(frames), axis=1)) ** 2
    return spec, np.fft.rfftfreq(n_fft, 1.0 / SR)


def analyse(x: np.ndarray) -> dict:
    m = x.mean(axis=1)
    spec, f = _spectra(m)
    loud = spec.sum(axis=1) > 1e-9 * spec.sum(axis=1).max()  # skip the silent frames
    spec = spec[loud]
    total = spec.sum()
    band = {name: float(spec[:, (f >= lo) & (f < hi)].sum() / total) for name, lo, hi in BANDS}

    def db(a, b):
        return 10.0 * np.log10(max(a, 1e-12) / max(b, 1e-12))

    pres_frames = spec[:, (f >= 2500) & (f < 6000)].sum(axis=1) / spec.sum(axis=1)
    hop_s = 2048 / SR
    per_win = max(1, int(WIN_S / hop_s))
    st_loud, cent = [], []
    centroid = (spec * f).sum(axis=1) / spec.sum(axis=1)
    shape = spec[:, (f >= 60) & (f < 8000)]
    shape = np.log10(shape + 1e-12)
    wins = []
    for i in range(0, len(spec) - per_win + 1, per_win):
        p = spec[i:i + per_win].sum(axis=1).mean()
        st_loud.append(10 * np.log10(p + 1e-20))
        cent.append(np.log2(np.median(centroid[i:i + per_win]) + 1.0))
        wins.append(shape[i:i + per_win].mean(axis=0))
    same = 0
    for a, b in zip(wins, wins[1:]):
        same += float(np.abs(a - b).mean() < 0.12)  # under ~1.2 dB mean difference across the band: a near-copy
    return {
        "seconds": len(m) / SR,
        "lufs": integrated_lufs(x),
        "tp": true_peak_dbtp(x),
        "band": band,
        "harsh_db": db(band["presence"] + band["air"], band["mid"]),
        "sting": float(np.percentile(pres_frames, 98)),
        "mud_db": db(band["lowmid"], band["mid"] + band["presence"]),
        "loud_std": float(np.std(st_loud)) if st_loud else 0.0,
        "cent_std": float(np.std(cent)) if cent else 0.0,
        "same": same / max(1, len(wins) - 1),
    }


def flags(r: dict, med: dict) -> list[str]:
    out = []
    if r["harsh_db"] > med["harsh_db"] + HARSH_DB:
        out.append(f"harsh (presence+air {r['harsh_db']:+.1f} dB over mid; set median {med['harsh_db']:+.1f})")
    if r["mud_db"] > med["mud_db"] + MUD_DB:
        out.append(f"muddy (low-mid {r['mud_db']:+.1f} dB over mid+presence; set median {med['mud_db']:+.1f})")
    if r["seconds"] >= MONO_SEC and r["loud_std"] < MONO_LOUD_LU and r["cent_std"] < MONO_CENT_OCT \
            and r["same"] > MONO_SAME:
        out.append(f"monotonous (loudness spread {r['loud_std']:.2f} LU, centroid spread {r['cent_std']:.2f} oct, "
                   f"{100 * r['same']:.0f}% of 3 s windows near-copies)")
    if r["tp"] > -1.0:
        out.append(f"true peak {r['tp']:+.2f} dBTP (over -1)")
    return out


def sheet(rows: list[tuple[str, np.ndarray]], out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cols = 3
    n = len(rows)
    fig, axs = plt.subplots((n + cols - 1) // cols, cols, figsize=(cols * 5, ((n + cols - 1) // cols) * 2.4),
                            squeeze=False)
    for ax, (name, x) in zip(axs.flat, rows):
        m = x.mean(axis=1)
        ax.specgram(m, NFFT=2048, Fs=SR, noverlap=1024, cmap="magma", vmin=-140, vmax=-30)
        ax.set_yscale("symlog", linthresh=500)
        ax.set_ylim(30, 16000)
        ax.set_title(name, fontsize=8)
        ax.tick_params(labelsize=6)
        tw = ax.twinx()
        hop = SR // 2
        t = np.arange(0, len(m), hop) / SR
        lv = [10 * np.log10(np.mean(m[i:i + 3 * SR] ** 2) + 1e-12) for i in range(0, len(m), hop)]
        tw.plot(t, lv, color="cyan", lw=0.7)
        tw.set_ylim(-60, 0)
        tw.tick_params(labelsize=6)
    for ax in list(axs.flat)[n:]:
        ax.axis("off")
    plt.tight_layout()
    plt.savefig(out, dpi=60)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--md", action="store_true", help="print a markdown table")
    ap.add_argument("--sheets", help="write spectrogram contact sheets (PNG) into this folder")
    ap.add_argument("--only", nargs="*", help="only these cues")
    args = ap.parse_args()
    res, audio = {}, []
    for cid in args.only or act1_cues():
        p = cue_file(cid)
        if p is None or not p.is_file() or p.stat().st_size < 1024:
            print(f"{cid}: no decodable file ({p})", file=sys.stderr)
            continue
        x = decode(p)
        res[cid] = analyse(x)
        if args.sheets:
            audio.append((cid, x[:: 1] if len(x) < 200 * SR else x[: 200 * SR]))
    med = {k: float(np.median([r[k] for r in res.values()])) for k in ("harsh_db", "mud_db")}
    if args.md:
        print("| cue | s | LUFS | dBTP | sub | low | low-mid | mid | pres | air | harsh dB | mud dB | loud std | "
              "cent std | same | flags |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for cid, r in res.items():
        b = r["band"]
        fl = flags(r, med)
        if args.md:
            print(f"| {cid} | {r['seconds']:.0f} | {r['lufs']:.1f} | {r['tp']:.1f} | "
                  + " | ".join(f"{100 * b[n]:.0f}" for n, *_ in BANDS)
                  + f" | {r['harsh_db']:+.1f} | {r['mud_db']:+.1f} | {r['loud_std']:.2f} | {r['cent_std']:.2f} | "
                  f"{100 * r['same']:.0f}% | {'; '.join(fl)} |")
        else:
            print(f"{cid:28s} {r['seconds']:6.1f}s {r['lufs']:6.1f} LUFS {r['tp']:5.1f} dBTP  harsh {r['harsh_db']:+5.1f} "
                  f"mud {r['mud_db']:+5.1f}  loud_std {r['loud_std']:.2f} cent_std {r['cent_std']:.2f} "
                  f"same {100 * r['same']:3.0f}%  {'; '.join(fl)}")
    if args.sheets:
        out = Path(args.sheets)
        out.mkdir(parents=True, exist_ok=True)
        for i in range(0, len(audio), 12):
            sheet(audio[i:i + 12], out / f"act1_music_{i // 12 + 1}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
