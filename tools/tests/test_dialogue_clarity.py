"""Dialogue stays clear over the field (the Lead's 10-30 18:24 polish pass): in every zone, the ambience beds that
play there (ambience.json zones, day and night, the wind at its loudest; or music.json's own list), ducked by mix.json
ducks.dialogue's Ambience, sit at least MARGIN_LU under a line's blip stream (the per-speaker blips at their stream
level, mix.md §6: -23.3 LUFS). Levels are each bed file's integrated loudness plus its row's volume_db."""
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))
AUDIO = ROOT / "game/data/audio"
BLIP_STREAM = -23.3   # mix.md §6: the blip stream with voices.json mix_db (+6) and the box's blip_volume_db (-8)
MARGIN_LU = 2.5


def _json(name: str) -> dict:
    return json.loads((AUDIO / name).read_text(encoding="utf-8"))


def zone_bed_levels() -> dict[str, float]:
    """'<scene> <day|night>' -> the summed level of its beds under dialogue (LUFS)."""
    from synth.loudness import integrated_lufs
    from synth.mixer import read_audio

    amb, mus = _json("ambience.json"), _json("music.json")
    rows = dict(amb["ambience"])
    rows.update(mus.get("ambience", {}))
    duck = float(_json("mix.json")["ducks"]["dialogue"]["buses"].get("Ambience", 0.0))
    wind = amb.get("wind", {})
    zrows = {z["scene"]: z for z in mus["zones"]}
    cache: dict[str, float] = {}

    def level(bed: str) -> float:
        if bed not in cache:
            r = rows[bed]
            y = read_audio(str(ROOT / r["file"].removeprefix("res://")), channels=2)
            cache[bed] = integrated_lufs(y) + float(r.get("volume_db", 0.0))
        return cache[bed]

    out = {}
    for scene in sorted(set(amb["zones"]) | set(zrows)):
        z, zr = amb["zones"].get(scene, {}), zrows.get(scene, {})
        for key in ("day", "night") if "night" in z else ("day",):
            beds = [(b, 0.0) for b in (zr.get("ambience") or z.get(key, []))]
            if z.get("wind") and wind.get("bed") not in [b for b, _ in beds]:
                beds.append((wind["bed"], float(wind.get("max_db", 0.0))))
            beds = [(b, extra) for b, extra in beds if b in rows and (ROOT / rows[b]["file"].removeprefix("res://")).is_file()]
            if beds:
                total = sum(10 ** ((level(b) + extra) / 10) for b, extra in beds)
                out[f"{scene} {key}"] = 10 * math.log10(total) + duck
    return out


class DialogueClarityTest(unittest.TestCase):
    def test_every_zones_beds_sit_under_a_lines_blips(self) -> None:
        loud = {k: round(v, 1) for k, v in zone_bed_levels().items() if BLIP_STREAM - v < MARGIN_LU}
        self.assertEqual(loud, {}, f"beds under dialogue within {MARGIN_LU} LU of the blips ({BLIP_STREAM})")


if __name__ == "__main__":
    unittest.main()
