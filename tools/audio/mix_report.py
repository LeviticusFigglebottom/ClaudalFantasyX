"""The mix as it plays, bus by bus (M3-AUD-23; docs/kb/audio/mix.md section 8).

targets.py checks each file on its own. This report adds what the runtime does on top: each sfx row's volume_db, each
music cue's and ambience bed's volume_db. It lists the effective level of every set (a set = the files that share a
directory and a name stem, e.g. sfx/creatures/*_attack_*) per bus, so the sets can be compared with each other.
It also measures a dialogue line's blip stream at both paces (voices.json `pace`), since one blip's level only means
something at the rate the blips come.

Run:  python3 tools/audio/mix_report.py [--out docs/kb/audio/mix_report.md]
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))
import data_check  # noqa: E402
import targets  # noqa: E402
from synth.dsp import SR  # noqa: E402
from synth.loudness import _block_powers, _to_lufs, integrated_lufs, momentary_max_lufs  # noqa: E402
from synth.mixer import read_audio  # noqa: E402

AUDIO = ROOT / "assets" / "audio"
LINE = "That's a very big spear for a very small conversation."


def short_term_max_lufs(x: np.ndarray) -> float:
    """Max 3 s short-term loudness (BS.1770 / EBU R128), 100 ms hop."""
    return float(_to_lufs(_block_powers(x, SR, 3.0, 0.1)).max())


def _decode(p: Path) -> np.ndarray:
    y = read_audio(str(p), channels=2)
    return read_audio(str(p), channels=1) if np.array_equal(y[:, 0], y[:, 1]) else y


def _rel(res: str) -> str:
    return res.removeprefix("res://assets/audio/")


def _set_name(rel: str) -> str:
    """The set a file belongs to: its directory and its name with trailing variant numbers and a final word dropped
    for numbered families (creatures/reef_crab_attack_2 -> creatures/*_attack)."""
    d, _, name = rel.rpartition("/")
    stem = re.sub(r"(_\d+)?\.ogg$", "", name)
    if d.endswith("creatures"):
        parts = stem.split("_")
        return f"{d}/*_{parts[-1]}" if len(parts) > 1 else f"{d}/{stem}"
    return f"{d}/{re.sub(r'_(soft|far)$', '', stem)}"


def measure_rows() -> list[dict]:
    files = data_check.load_files(ROOT)
    rows = data_check.merged_sfx(files)["sfx"]
    out = []
    seen: set[str] = set()
    for sid, row in sorted(rows.items()):
        for res in row.get("files", []):
            rel = _rel(res)
            p = AUDIO / rel
            if not p.is_file() or not rel.endswith(".ogg"):
                continue
            seen.add(rel)
            rule = targets.rule_for(rel)
            y = _decode(p)
            metric = rule[1] if rule else "momentary"
            lv = integrated_lufs(y) if metric == "integrated" else momentary_max_lufs(y)
            vol = float(row.get("volume_db", 0.0))
            out.append({"kind": "sfx", "id": sid, "rel": rel, "bus": row.get("bus", "SFX"), "metric": metric,
                        "file": lv, "vol": vol, "eff": lv + vol, "target": rule[2] if rule else None})
    music = files.get(data_check.MUSIC) or {}
    for kind, table, bus in (("cue", music.get("cues") or {}, "Music"), ("bed", music.get("ambience") or {}, "Ambience")):
        for cid, row in sorted(table.items()):
            res = [row["file"]] if "file" in row else list(row.get("stems", []))
            for r in res:
                rel = _rel(r)
                p = AUDIO / rel
                if not p.is_file() or rel in seen:
                    continue
                seen.add(rel)
                lv = integrated_lufs(_decode(p))
                vol = float(row.get("volume_db", 0.0))
                out.append({"kind": kind, "id": cid, "rel": rel, "bus": row.get("bus", bus), "metric": "integrated",
                            "file": lv, "vol": vol, "eff": lv + vol, "target": (targets.rule_for(rel) or [0, 0, None])[2]})
    amb = files.get(data_check.AMBIENCE) or {}
    for cid, row in sorted((amb.get("ambience") or {}).items()):
        rel = _rel(row.get("file", ""))
        p = AUDIO / rel
        if not p.is_file() or rel in seen:
            continue
        seen.add(rel)
        lv = integrated_lufs(_decode(p))
        vol = float(row.get("volume_db", 0.0))
        out.append({"kind": "bed", "id": cid, "rel": rel, "bus": row.get("bus", "Ambience"), "metric": "integrated",
                    "file": lv, "vol": vol, "eff": lv + vol, "target": (targets.rule_for(rel) or [0, 0, None])[2]})
    return out


def blip_stream(pace: str) -> dict:
    """A line's blips as the box and VoiceAudio would play them at the default reveal speed, without pauses: the
    default voice's first blip, at each blip time, mixed, then measured (short-term max, 3 s)."""
    box = json.loads((ROOT / "game/data/dialogue/text_box.json").read_text())["text_box"]
    voices = json.loads((ROOT / "game/data/audio/voices.json").read_text())
    rows = data_check.merged_sfx(data_check.load_files(ROOT))["sfx"]
    dflt = voices["default"]
    blip = _decode(AUDIO / _rel(rows[dflt["blips"][0]]["files"][0]))
    if blip.ndim > 1:
        blip = blip.mean(axis=1)
    cps = float(box["chars_per_sec"])
    vowels = box["flap_vowels"]
    every = int(box["blip_every_n_chars"])
    rate = float(dflt.get("rate_ms", 0)) / 1000.0
    times = []
    n = 0
    inside = False
    for i, ch in enumerate(LINE):
        t = i / cps
        if pace == "letter":
            if ch.strip():
                n += 1
                if n % every == 0:
                    times.append(t)
        else:
            v = ch in vowels
            if v and not inside:
                times.append(t)
            inside = v
    kept = []
    for t in times:
        if not kept or t - kept[-1] >= rate:
            kept.append(t)
    lines = 4  # the line said four times over: long enough for a 3 s window
    dur = len(LINE) / cps
    y = np.zeros(int((dur * lines + 1.0) * SR))
    gain = 10 ** ((float(box["blip_volume_db"]) + float(dflt.get("volume_db", 0.0))
                   + float(voices.get("mix_db", 0.0))) / 20)
    for k in range(lines):
        for t in kept:
            s = int((t + k * dur) * SR)
            e = min(len(y), s + len(blip))
            y[s:e] += gain * blip[: e - s]
    return {"pace": pace, "per_sec": len(kept) / dur, "short_term_max": short_term_max_lufs(y),
            "one_blip": momentary_max_lufs(gain * blip)}


def report() -> str:
    rows = measure_rows()
    by: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        by.setdefault((r["bus"], _set_name(r["rel"])), []).append(r)
    lines = ["# Mix report (generated)", "",
             "Generated by `python3 tools/audio/mix_report.py --out docs/kb/audio/mix_report.md` (M3-AUD-23). Effective level =",
             "the decoded file's loudness (integrated for cues and beds, momentary max for SFX) + its data row's `volume_db`.",
             "Bus faders, ducks and the player's volume settings come on top at runtime and are the same for a whole bus.", ""]
    for bus in sorted({b for b, _ in by}):
        lines += [f"## {bus}", "", "| Set | Files | Metric | Effective median | Min | Max | Row volume_db |",
                  "|---|---|---|---|---|---|---|"]
        for (b, name), group in sorted(by.items()):
            if b != bus:
                continue
            eff = [g["eff"] for g in group]
            vols = sorted({g["vol"] for g in group})
            lines.append(f"| `{name}` | {len(group)} | {group[0]['metric']} | {statistics.median(eff):.1f} | "
                         f"{min(eff):.1f} | {max(eff):.1f} | {', '.join(f'{v:+.1f}' for v in vols)} |")
        lines.append("")
    lines += ["## Blip streams", "", "A dialogue line's blips at the default reveal (40 chars/s, no pauses), the default voice:", "",
              "| Pace | Blips per second | One blip | Stream (short-term max) |", "|---|---|---|---|"]
    for pace in ("letter", "syllable"):
        b = blip_stream(pace)
        lines.append(f"| {pace} | {b['per_sec']:.1f} | {b['one_blip']:.1f} | {b['short_term_max']:.1f} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    text = report()
    if args.out:
        (ROOT / args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
