"""Loudness and size targets for every shipped audio file (M2-AUD-06; docs/kb/audio/mix.md §2 and §5).

The first rule whose glob matches a file's path (relative to assets/audio/) applies. Each rule names the metric
(integrated loudness for beds and cues, the 400 ms momentary max for short sounds), its target and tolerance (LU),
and the decoded true-peak ceiling (dBTP). tools/tests/test_audio_loudness.py decodes every file and checks it.
"""
from __future__ import annotations

import fnmatch

# (glob, metric, target LUFS, tolerance LU, true-peak ceiling dBTP, why)
RULES = [
    ("music/drownbell_p*.ogg", "stem", -16.0, 0.5, -1.0, "boss stems: the full stack at -16, each alone quieter"),
    ("music/*.ogg", "integrated", -16.0, 0.5, -1.0, "music beds, themes and cutscene cues"),
    ("ambience/*.ogg", "integrated", -26.0, 0.5, -5.0, "ambience beds (mix.md: -26, peaks well down)"),
    ("sfx/ilun_summon.ogg", "integrated", -16.0, 0.5, -1.0, "a music sting (Music bus)"),
    ("sfx/battle/stinger_*_soft.ogg", "momentary", -17.0, 1.0, -1.0, "reduced-audio stingers"),
    ("sfx/battle/stinger_*.ogg", "momentary", -16.0, 1.0, -1.0, "opening stingers"),
    ("sfx/battle/drownbell_toll_soft.ogg", "momentary", -17.0, 1.0, -1.0, "the reduced-audio toll"),
    ("sfx/battle/drownbell_toll.ogg", "momentary", -16.0, 1.0, -1.0, "the boss's toll"),
    ("sfx/battle/bell_release.ogg", "momentary", -16.0, 1.0, -1.0, "the boss's death"),
    ("sfx/battle/victory.ogg", "momentary", -16.0, 1.0, -1.0, "the victory sting"),
    ("sfx/battle/flood_soft.ogg", "momentary", -20.0, 1.0, -1.0, "the reduced-audio Flood"),
    ("sfx/battle/*.ogg", "momentary", -19.0, 2.5, -1.0, "combat SFX (-18 nominal; quieter layers to -21.5)"),
    ("sfx/shrine/shrine_pool_fill.ogg", "integrated", -24.0, 0.5, -6.0, "the shrine pool's fill bed"),
    ("sfx/shrine/*.ogg", "momentary", -18.0, 0.5, -1.0, "the trial's world SFX"),
    ("sfx/step_*.ogg", "momentary", -18.5, 1.5, -1.0, "footsteps"),
    ("sfx/drownbell_toll.ogg", "momentary", -18.0, 1.0, -1.0, "the cutscene's far toll"),
    ("sfx/text_blip.ogg", "momentary", -27.0, 1.0, -3.0, "one dialogue blip"),
    ("sfx/ui_*.ogg", "momentary", -20.0, 1.0, -2.5, "UI SFX"),
    ("sfx/voice/blip_*.ogg", "momentary", -27.0, 1.0, -3.0, "per-speaker dialogue blips (M3-AUD-07)"),
]
FILE_LIMIT = 5 * 1024 * 1024        # CLAUDE.md §8: no file over 5 MB
TOTAL_BUDGET = 24 * 1024 * 1024     # every shipped audio file (mix.md §5: the slice; about 1 MB per minute of music)


def rule_for(rel: str):
    for r in RULES:
        if fnmatch.fnmatch(rel, r[0]):
            return r
    return None
