#!/usr/bin/env python3
"""Battle tells, told apart (the Lead's 10-30 21:25 accessibility item).

A telegraphed skill (skills.json `charge`) warns the party a turn or more ahead; its wind-up sound is the tell for a
player who isn't watching the timeline. It has to differ from the same enemy's ordinary attack (or the warning reads
as "it hit again") and from every other tell in the act (or a player can't tell which threat is gathering). For each
pair this compares:
  - timbre: the level difference (dB, RMS over 24 log-spaced bands, each sound's own mean removed) of the long-term
    spectrum of the sounding frames: how differently the two are coloured;
  - brightness: the spectral centroid ratio;
  - shape: the sounding length ratio and the attack time (10 % to 90 % of the envelope peak).
A pair is distinct when any one cue clears its bar (TIMBRE_DB, CENTROID_RATIO, LENGTH_RATIO). The bars are the sizes
people reliably hear across a room through game music: a ~4 dB colour change, a third of an octave in brightness, half
again as long. A tell and its enemy's attack, and two tells of one chapter (they can meet in one fight), must be
distinct; a look-alike pair from different chapters never shares a fight and is reported, not failed.

    python3 tools/audio/tell_check.py [--md report.md]
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from synth.dsp import SR  # noqa: E402
from synth.mixer import read_audio  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
TIMBRE_DB = 4.0
CENTROID_RATIO = 1.26  # a third of an octave
LENGTH_RATIO = 1.5
FLOOR_DB = 30.0  # frames this far under the loudest are not "sounding"
BANDS = np.geomspace(60.0, 16000.0, 25)

# Act I's tells (enemies.json users of a `charge` skill, Ch1-Ch9) and whose attack each must not be mistaken for.
ACT1_TELLS = {
    "gnaw_coil": ("hullgnaw", "Ch1, Hullgnaw"),
    "toll_gather": ("drownbell", "Ch2, the Drownbell"),
    "lines_taut": ("spar_wraith", "Ch4, the Spar Wraith"),
    "recrust_gather": ("cinder_matron", "Ch5, the Cinder Matron"),
    "reach_for_stair": ("tide_crawler", "Ch8, the tide crawlers"),
    "close_the_hand": ("undertows_reach", "Ch8, Undertow's Reach (the Grip)"),
    "breach_gather": ("undertows_reach", "Ch8, Undertow's Reach (the Breach)"),
}


def _sfx_rows() -> dict:
    rows: dict = {}
    d = os.path.join(ROOT, "game", "data", "audio")
    for f in sorted(os.listdir(d)):
        if f.startswith("sfx") and f.endswith(".json"):
            rows.update(json.load(open(os.path.join(d, f))).get("sfx", {}))
    return rows


def _file(rows: dict, sfx_id: str) -> str:
    row = rows.get(sfx_id) or {}
    files = row.get("files") or [row.get("file")]
    return os.path.join(ROOT, str(files[0]).replace("res://", ""))


def features(path: str) -> dict:
    x = read_audio(path, channels=1)
    x = x[:, 0] if x.ndim == 2 else x
    n, hop = 2048, 512
    win = np.hanning(n)
    frames = [x[i : i + n] * win for i in range(0, max(1, len(x) - n), hop)]
    spec = np.abs(np.fft.rfft(np.array(frames), axis=1)) ** 2
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    energy = spec.sum(axis=1)
    db = 10 * np.log10(energy + 1e-20)
    sounding = db >= db.max() - FLOOR_DB
    s = spec[sounding].mean(axis=0)
    bands = np.array([s[(freqs >= lo) & (freqs < hi)].sum() for lo, hi in zip(BANDS[:-1], BANDS[1:])])
    shape = 10 * np.log10(bands + 1e-20)
    env = np.sqrt(energy / energy.max())
    peak = int(np.argmax(env))
    a10 = int(np.argmax(env >= 0.1))
    a90 = int(np.argmax(env >= 0.9))
    return {
        "shape": shape - shape.mean(),
        "centroid": float((s * freqs).sum() / (s.sum() + 1e-20)),
        "length_s": float(sounding.sum() * hop / SR),
        "attack_s": float(max(0, a90 - a10) * hop / SR) if a90 >= a10 else float(peak * hop / SR),
    }


def compare(a: dict, b: dict) -> dict:
    timbre = float(np.sqrt(np.mean((a["shape"] - b["shape"]) ** 2)))
    bright = max(a["centroid"], b["centroid"]) / max(1.0, min(a["centroid"], b["centroid"]))
    length = max(a["length_s"], b["length_s"]) / max(0.01, min(a["length_s"], b["length_s"]))
    cues = []
    if timbre >= TIMBRE_DB:
        cues.append(f"colour {timbre:.1f} dB")
    if bright >= CENTROID_RATIO:
        cues.append(f"brightness x{bright:.2f}")
    if length >= LENGTH_RATIO:
        cues.append(f"length x{length:.2f}")
    return {"timbre_db": timbre, "bright": bright, "length": length, "cues": cues}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--md", default="")
    a = ap.parse_args(argv)
    rows = _sfx_rows()
    battle = json.load(open(os.path.join(ROOT, "game", "data", "audio", "battle_sfx.json")))
    voices = json.load(open(os.path.join(ROOT, "game", "data", "audio", "creature_voices.json")))["creatures"]
    feats: dict = {}
    out: list[str] = []
    bad = 0
    for skill, (enemy, who) in ACT1_TELLS.items():
        tell_id = battle["vfx"].get(skill) or battle["skills"].get(skill)
        feats[skill] = features(_file(rows, tell_id))
        f = feats[skill]
        line = f"{skill} ({who}; `{tell_id}`, {f['length_s']:.1f} s, centroid {f['centroid']:.0f} Hz)"
        attack_id = ((voices.get(enemy) or {}).get("events") or {}).get("attack")
        if attack_id:
            c = compare(f, features(_file(rows, attack_id)))
            ok = bool(c["cues"])
            bad += 0 if ok else 1
            line += f": against its attack `{attack_id}`: {', '.join(c['cues']) or 'NOT DISTINCT'}"
        out.append(("  " if attack_id and ok else "  FAIL ") + line)
    pairs = []
    for p, q in itertools.combinations(ACT1_TELLS, 2):
        c = compare(feats[p], feats[q])
        pairs.append((p, q, c))
        if c["cues"]:
            continue
        same_fight = ACT1_TELLS[p][1].split(",")[0] == ACT1_TELLS[q][1].split(",")[0]
        bad += 1 if same_fight else 0
        out.append(
            f"  {'FAIL' if same_fight else 'alike (never in one fight)'} {p} and {q}: "
            f"colour {c['timbre_db']:.1f} dB, brightness x{c['bright']:.2f}, length x{c['length']:.2f}"
        )
    closest = min(pairs, key=lambda t: t[2]["timbre_db"])
    head = (
        f"{len(ACT1_TELLS)} Act I tells; each against its enemy's attack and the {len(pairs)} pairs of tells: "
        f"{bad} not distinct where it matters. Closest pair by colour: {closest[0]} / {closest[1]} "
        f"({', '.join(closest[2]['cues']) or 'none'})."
    )
    print(head + "\n" + "\n".join(out))
    if a.md:
        with open(a.md, "w") as fh:
            fh.write("# Act I battle tells\n\n" + head + "\n\n" + "\n".join(f"- {x.strip()}" for x in out) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
